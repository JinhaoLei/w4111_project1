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

  #TODO: The key words that users want to search will be recorded by name variable above.
  #      You should return all movies whose names match with the key words.
  #Returns: A list with some dicts. Each dict records id, name, and year of a matched movie. 
  #         Below is a hard-coded example.        

  context = [{'id':'0', 'name':'Avatar','year':'2009'}]
  return render_template('index.html', sresult=context, len_result=len(context))

@app.route('/movie', methods=['GET'])
def movie():

  id = int(request.values.get("id"))
  session['refer'] = str(id)


  #TODO: This route needs to get the detailed information for a single movie and display it.
  #      Given the movie id above, you should return all attributes of this movie plus four extra fields.
  #      The four extra fields are 'iflike', 'iffavor', 'num_like', 'num_favor'. 'iflike' and 'iffavor'
  #      should be set as 0. 'num_like' and 'num_favor' should be set as their true numbers recored in our db.
  #Returns: A dict. Below is a hard-coded example.    
  
  context = {'id':'0','name':'Avatar','director':'James_Cameron', 'director_id':0, \
  'stars':'CCH Pounder', 'stars_id':10, 'duration':'178','color':'COLOR',\
  'content_rating':'PG-13','year':'2009','language':'English','country':'USA',\
  'budget':'237000000','gross':'760505847','score':'7.9',\
  'imdb_link':'http://www.imdb.com/title/tt0499549/?ref_=fn_tt_tt_1',\
  'genre':'Sci-Fi', 'iflike':0, 'iffavor':0, 'num_like':10005, 'num_favor':433}
  if session.has_key('logged_in') and session['logged_in']:
    ##TODO: Check in db if current user likes and favors this movie.
    #       If True, you shoud set context['iflike'] and context['iffavor'] as 1.
    pass

  if request.values.get('like'):
    
    context['iflike'] = 1
    ##TODO: A user likes this movie. You should update related table.
    #       Use session['username'] to get the username. Use id to get the movie id.
  if request.values.get('cancellike'):
    
    context['iflike'] = 0
    ##TODO: A user cancels his like on this movie. You should update related table.
    #       Use session['username'] to get the username. Use id to get the movie id.
  if request.values.get('favor'):

    context['iffavor'] = 1
    ##TODO: A user favors this movie. You should update related table.
    #       Use session['username'] to get the username. Use id to get the movie id.
  if request.values.get('cancelfavor'):

    context['iffavor'] = 0
    ##TODO: A user cancels his favor on this movie. You should update related table.
    #       Use session['username'] to get the username. Use id to get the movie id.
  
  ##TODO: Also you need to fetch all comments data related to this movie.
  #Returns: A list of dicts. Each dict records user_name, time and content for a comment.
  #         Below is a hard-coded example.
  comments = [{'user_name':'leijh', 'time':'2018-10-01 15:39:20', 'content':'I like this movie.'},{'user_name':'leijh2', 'time':'2018-10-01 15:44:20', 'content':'I don\'t like this movie.'}]

  return render_template("movie.html", data=context, comments=comments)


@app.route('/people', methods=['GET'])
def people():

  id = int(request.values.get("id"))

  #TODO: This route needs to get the detailed information for a person and display it.
  #      Given the people id above, you should return some attributes of this person like the example below.
  #Returns: A dict. Below is a hard-coded example.    
  
  context = {'id':'0','name':'James Cameron','country':'Canada','gender':'M',\
  'birth_date':'1954-08-16','profile_pic':'James_Cameron.jpg',\
  'bio':'James Francis Cameron (born August 16, 1954) is a Canadian filmmaker, philanthropist, and deep-sea explorer.'
  }
  
  return render_template("people.html", data=context)


@app.route('/tologin')
def do_admin_login():
    return render_template("login.html")

@app.route('/seefavor')
def seefavor():
    ##TODO: Given user id, you should return all movies this user favors.
    #       Use session['username'] to obtain the username.
    #Returns: A list of dicts. Each dict records movie id, name and year of a movie.
    #         Below is a hard-coded example.
    data = [{'id':0, 'name':'Avatar', 'year':'2009'}]
    return render_template("seefavor.html", data=data, username=session['username'])

@app.route('/login', methods=['POST'])
def login():
    ##TODO: When logging in, you should check if username matches with paswword.
    #       Modify this 'if' statement only. It is currently a hard-coded statement.
    if request.form['password'] == '1' and request.form['username'] == 'admin':
        session['logged_in'] = True
        session['username'] = request.form['username']
        if session['refer'] is not None:
          return redirect('/movie?id=%s'%(session['refer']))
        else:
          return redirect('/')
    else:
      flash('wrong password!')
      return redirect('/tologin')


@app.route('/comment', methods=['POST'])
def comment():

    ##TODO: A user makes a new comment. You should update related trable.
    #       The movie id, comment content, timestamp and username can be obtained via 
    #       request.form['mid'], request.form['new_comment'], 
    #       request.form['timestamp'] and session['username'].
    return redirect('/movie?id=%s'%(request.form['mid']))
    

@app.route('/tosignup')
def do_sign_up():
    if session.has_key('sign_up'):
      sleep(1)
      return redirect('/')
    else:
      return render_template("signup.html")


@app.route('/signup', methods=['POST'])
def signup():
    ##TODO: When signing up, you should check if username has been registered.
    #       If success, you should update related table. The username, password and email
    #       can be obtained via request.form['username'], request.form['password'] and request.form['email']
    #       Modify this 'if' statement only.
    if 1:
      #print request.form['username'], request.form['password'], request.form['email']
      flash('sign up success!')
      session['sign_up'] = True
    else:
      flash('username has been used!')
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