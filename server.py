#!/usr/bin/env python2.7
#coding=utf-8

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy import exc
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, flash
from time import sleep
tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "wl2681"
DB_PASSWORD = "22g7a22h"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
engine.execute("""DROP TABLE IF EXISTS test;""")
engine.execute("""CREATE TABLE IF NOT EXISTS test (
  ID INT,
  DID INT NOT NULL,
  Name TEXT NOT NULL,
  Duration INT,
  Color TEXT,
  Content_Rating TEXT,
  Year INT,
  Language TEXT,
  Country TEXT,
  Budget INT,
  Gross INT,
  Score REAL,
  IMDB_Link TEXT,
  Genre TEXT NOT NULL
);""")
engine.execute("""INSERT INTO test VALUES(E'0',E'0',E'Avatar ',E'178',E'COLOR',E'PG-13',E'2009',E'English',E'USA',E'237000000',E'760505847',E'7.9',E'Empty.',E'Sci-Fi');""")



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
def home():
      return index()

@app.route('/index')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  
  session['refer'] = None
  

  #
  # example of a database query
  #
  cursor = g.conn.execute("SELECT name FROM test")
  names = []
  for result in cursor:
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #

  
  return render_template("index.html")

@app.route('/search', methods=['GET'])
def search():
  name = request.values.get("name")
  #name = request.form['name']

  #cmd = 'INSERT INTO test(name) VALUES (:name1), (:name2)';
  #g.conn.execute(text(cmd), name1 = name, name2 = name);

  pattern = "%%%s%%" % name.lower()
  columns = ['id', 'name', 'year']
  cmd = 'SELECT ' + ', '.join(columns) + ' FROM movie WHERE LOWER(name) LIKE (:pattern)'
  cursor = g.conn.execute(text(cmd), pattern=pattern)
  context = [dict(list(zip(cursor.keys(), result))) for result in cursor]

  return render_template('index.html', sresult=context, len_result=len(context))

@app.route('/movie', methods=['GET'])
def movie():

  mid = int(request.values.get("id"))
  session['refer'] = str(mid)

  # Get movie
  cmd = 'SELECT * FROM movie WHERE id = :mid'
  cursor = engine.execute(text(cmd), mid=mid)
  context = dict(list(zip(cursor.keys(), [unicode(item) for item in cursor.fetchone()])))
  did = int(context['did'])
  context['director_id'] = did

  # Get director name
  cmd = 'SELECT name FROM people WHERE id = :did'
  cursor = engine.execute(text(cmd), did=did)
  context['director'] = cursor.fetchone()[0]

  # Get cast
  cmd = 'SELECT people.id, people.name FROM people, stars WHERE people.id = stars.id AND stars.mid = :mid'
  cursor = engine.execute(text(cmd), mid=mid)
  context['stars_id'], context['stars'] = cursor.fetchone()

  if session.has_key('logged_in') and session['logged_in']:
    # Update context['iflike']
    cmd = """
      SELECT COUNT(*) FROM users, likes
      WHERE users.username = :username AND users.id = likes.uid AND likes.mid = :mid
    """
    cursor = engine.execute(text(cmd), username=session['username'], mid=mid)
    if cursor.fetchone()[0] > 0:
        context['iflike'] = 1
    else:
        context['iflike'] = 0

    # Update context['iffavor']
    cmd = """
      SELECT COUNT(*) FROM users, favorites
      WHERE users.username = :username AND users.id = favorites.uid AND favorites.mid = :mid
    """
    cursor = engine.execute(text(cmd), username=session['username'], mid=mid)
    if cursor.fetchone()[0] > 0:
        context['iffavor'] = 1
    else:
        context['iffavor'] = 0

  if request.values.get('like'):
    context['iflike'] = 1

    # Insert into 'likes' table
    cmd = 'SELECT id FROM users where username = :username'
    cursor = engine.execute(text(cmd), username=session['username'])
    uid = cursor.fetchone()[0]
    cmd = 'INSERT INTO likes VALUES (:uid, :mid)'

    # Request form will get resubmitted when going back
    try:
        engine.execute(text(cmd), uid=uid, mid=mid)
    except exc.IntegrityError:
        pass

  if request.values.get('cancellike'):
    context['iflike'] = 0

    # Delete from 'likes' table
    cmd = 'SELECT id FROM users where username = :username'
    cursor = engine.execute(text(cmd), username=session['username'])
    uid = cursor.fetchone()[0]
    cmd = 'DELETE FROM likes WHERE uid = :uid AND mid= :mid'

    # Request form will get resubmitted when going back
    try:
        engine.execute(text(cmd), uid=uid, mid=mid)
    except exc.IntegrityError:
        pass

  if request.values.get('favor'):
    context['iffavor'] = 1

    # Insert into 'favorites' table
    cmd = 'SELECT id FROM users where username = :username'
    cursor = engine.execute(text(cmd), username=session['username'])
    uid = cursor.fetchone()[0]
    cmd = 'INSERT INTO favorites VALUES (:uid, :mid)'
    engine.execute(text(cmd), uid=uid, mid=mid)

  if request.values.get('cancelfavor'):
    context['iffavor'] = 0

    # Delete from 'favorites' table
    cmd = 'SELECT id FROM users where username = :username'
    cursor = engine.execute(text(cmd), username=session['username'])
    uid = cursor.fetchone()[0]
    cmd = 'DELETE FROM favorites WHERE uid = :uid AND mid= :mid'
    engine.execute(text(cmd), uid=uid, mid=mid)

  # Get num_like
  cmd = 'SELECT COUNT(*) FROM likes WHERE mid = :mid'
  cursor = engine.execute(text(cmd), mid=mid)
  context['num_like'] = cursor.fetchone()[0]

  # Get num_favor
  cmd = 'SELECT COUNT(*) FROM favorites WHERE mid = :mid'
  cursor = engine.execute(text(cmd), mid=mid)
  context['num_favor'] = cursor.fetchone()[0]

  cmd = 'SELECT username, timestamp, content FROM comments, users WHERE mid = :mid AND uid = users.id'
  cursor = engine.execute(text(cmd), mid=mid)
  columns = ['user_name', 'time', 'content']
  comments = [dict(list(zip(columns, result))) for result in cursor]
  return render_template("movie.html", data=context, comments=comments)


@app.route('/people', methods=['GET'])
def people():
  pid = int(request.values.get("id"))
  cmd = 'SELECT * FROM people WHERE id = :pid'
  cursor = engine.execute(text(cmd), pid=pid)
  context = dict(list(zip(cursor.keys(), cursor.fetchone())))
  
  return render_template("people.html", data=context)


@app.route('/tologin')
def do_admin_login():
    if session.has_key('sign_up'):
      del session['sign_up']
    return render_template("login.html")

@app.route('/seefavor')
def seefavor():
    cmd = 'SELECT id FROM users WHERE username = :username'
    cursor = engine.execute(text(cmd), username=session['username'])
    uid = cursor.fetchone()[0]

    cmd = 'SELECT m.id, m.name, m.year FROM movie AS m, favorites AS f WHERE f.uid = :uid AND m.id = f.mid'
    cursor = engine.execute(text(cmd), uid=uid)
    data = [dict(list(zip(cursor.keys(), result))) for result in cursor]

    return render_template("seefavor.html", data=data, username=session['username'])

@app.route('/login', methods=['POST'])
def login():
    cmd = 'SELECT COUNT(*) FROM users WHERE username = :username AND password = :password'
    cursor = engine.execute(text(cmd), username=request.form['username'], password=request.form['password'])
    if cursor.fetchone()[0] > 0:
        session['logged_in'] = True
        session['username'] = request.form['username']
        if session['refer'] is not None:
          return redirect('/movie?id=%s'%(session['refer']))
        else:
          return redirect('/')
    else:
      flash('Wrong password!')
      return redirect('/tologin')


@app.route('/comment', methods=['POST'])
def comment():
    cmd = 'SELECT MAX(id) FROM comments'
    cursor = engine.execute(cmd)
    cid = cursor.fetchone()[0] + 1

    cmd = 'SELECT id FROM users WHERE username = :username'
    cursor = engine.execute(text(cmd), username=session['username'])
    uid = cursor.fetchone()[0]

    cmd = 'INSERT INTO comments VALUES (:cid, :timestamp, :mid, :uid, :content)'
    engine.execute(text(cmd),
                   cid=cid, timestamp=request.form['timestamp'],
                   mid=request.form['mid'], uid=uid, content=request.form['new_comment'])

    return redirect('/movie?id=%s'%(request.form['mid']))
    

@app.route('/tosignup')
def do_sign_up():
    if session.has_key('sign_up'):
      sleep(1)
      del session['sign_up']
      return redirect('/')
    else:
      return render_template("signup.html")


@app.route('/signup', methods=['POST','GET'])
def signup():
    cmd = 'SELECT COUNT(*) FROM users WHERE username = :username'
    cursor = engine.execute(text(cmd), username=request.form['username'])
    if cursor.fetchone()[0] == 0:
      cmd = 'SELECT MAX(id) FROM users'
      cursor = engine.execute(cmd)
      uid = cursor.fetchone()[0] + 1

      cmd = 'INSERT INTO users VALUES (:uid, :username, :password, :email)'
      engine.execute(text(cmd), uid=uid,
                     username=request.form['username'],
                     password=request.form['password'],
                     email=request.form['email'])

      flash('sign up success!')
      session['sign_up'] = True
      sleep(1)
      return redirect('/tologin')
    else:
      flash('username already taken!')
      return redirect('/tosignup')


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect('/')


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.secret_key = os.urandom(12)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)


  run()