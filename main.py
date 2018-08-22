from flask import Flask
from flask import render_template
from flask import request
#from flask_wtf import CsrfProtect #this is what the video said, but it gives a warning, the one one line below works without warnings
from flask_wtf import CSRFProtect
import forms
from flask import make_response #for the cookie
from flask import session

from flask import url_for
from flask import redirect

from flask import flash

from flask import g #to allow global variables. They will be alive until the end of after_request, i.e. return response.
#It will be used in only one petition. Two clients cannot share the same global variable.

from config import DevelopmentConfig

from models import db
from models import userstest #name of the MODEL, not table to import
from models import Comment 

from helper import date_format

from flask_mail import Mail
from flask_mail import Message

import threading  #to send the emails in the background so the app is faster
from flask import copy_current_request_context

app = Flask(__name__)
app.config.from_object(DevelopmentConfig) #here is where we decide if Development or Production.

#before using config:
#app.secret_key = 'my_secret_key' #though it is a good practice to use os.get() to get the secret key, and not write it in the code

#before using config:
#csrf = CsrfProtect(app)

#after config
#csrf = CsrfProtect() #now we do this at the end, in if __name__...
#this is what the video said, but it gives a warning, the one one line below works without warnings
#csrf = CSRFProtect() THIS WASN'T WORKING
csrf = CSRFProtect(app) #from https://flask-wtf.readthedocs.io/en/stable/csrf.html
mail = Mail()

def send_email(user_email, username): #to know where to send it and write the username in the email
	msg = Message('Thank you for signing up!', #title of the email.
		  sender = app.config['MAIL_USERNAME'], 
		  recipients = [user_email])
	msg.html = render_template('email.html', username = username)
	mail.send(msg) #here we actually send the message

@app.errorhandler(404)
def page_not_found(e): #anything works, not only an 'e'
	return render_template('404.html'), 404 #flask doesn't send the error number, we have to do it.


@app.before_request #we use this to validate , like if the user has permission to access that url, or even if we need a visit counter to that url, 
def before_request():
	if 'username' not in session:
		print (request.endpoint) #this gives you the last part of the url
		print ('User needs to log in!')

	#validate the url...validate if the user is authenticated, let's imagine we want to make 'comment' only accessible to authenticated users
	if 'username' not in session and request.endpoint in ['comment']:
		return redirect(url_for('login'))
	elif 'username' in session and request.endpoint in ['login', 'create']: #why an authenticated user would go to login or create, let's send him/her to index
		return redirect(url_for('index')) #the function index, not the route.

	g.test = 'test' #here we create the global variables. ?I guess we could pull all of one vendor's data here??


@app.route('/')
def index():

	'''
	#we are reading cookies here
	#custome_cookie = request.cookies.get('custome_cookie') this would receive the custome_cookie we created and sent ('Eduardo')
	custome_cookie = request.cookies.get('custome_cookies', 'Undefined') #this does: if you don't find custome_cookie within custome_cookies, it returns undefined
	print (custome_cookie)
	'''

	if 'username' in session: #session is our sessions dictionary
		username = session['username']
	title = "Index"
	return render_template('index.html', title = title)



@app.route('/logout') #here we destroy the cookies
def logout():
	if 'username' in session:
		session.pop('username') #destroy cookie
	return redirect(url_for('login')) # to redirect, using url_for we type the function name, not the path, so just 'login', no /asddad/adad/login

@app.route('/login', methods = ['GET', 'POST'])
def login():
	login_form = forms.LoginForm(request.form)
	if request.method == 'POST' and login_form.validate():
		username = login_form.username.data
		password = login_form.password.data

		user = userstest.query.filter_by(username = username).first() #select * from users where username = username limit 1. It returns an object with the information of the user. If not found, it will return a None
		if user is not None and user.verify_password(password):
			success_message = 'Welcome {}'.format(username)
			flash(success_message)
			session['username'] = username
			session['user_id'] = user.id
			return redirect( url_for('index') )
		else:
			error_message = 'Invalid username or password'
			flash(error_message)

		#after a;dding session['username'] = username a few lines above, isn't this one left over?
		#session['username'] = login_form.username.data #a session variable called username will be created each time whose value is the own username
	return render_template('login.html', form = login_form)

@app.route('/cookie')
def cookie():
	#we are creating cookies here
	response = make_response( render_template('cookie.html'))
	response.set_cookie('custome_cookie', 'Eduardo')
	return response

#by default in flask, only method GET, we have to specify POST
@app.route('/comment', methods = ['GET', 'POST'])
def comment():
	comment_form = forms.CommentForm(request.form)
	
	if request.method == 'POST' and comment_form.validate(): #to validate forms inputs. We also had to add it in _macro.html, in the list {{field.errors}}
		'''print(comment_form.username.data)
		print(comment_form.email.data)
		print(comment_form.comment.data)
	else:
		print ("Error in the form!!")'''


		user_id = session['user_id'] #since we work with cookies, this is the way to get the user_id
		comment = Comment(user_id = user_id, 
						  text = comment_form.comment.data)

		print(comment)
		db.session.add(comment)
		db.session.commit()
		success_message = "New comment created"
		flash(success_message)

	title = "Flask Course"
	return render_template('comment.html', title = title, form = comment_form)

@app.route('/create', methods = ['GET', 'POST'])
def create():
	create_form = forms.CreateForm(request.form)
	if request.method == 'POST' and create_form.validate():

		user = userstest(create_form.username.data,
						 create_form.password.data,
						 create_form.email.data)

		db.session.add(user) #this needs an objects heredated from model, like user
		db.session.commit() #here we insert it in the database
		#SQLAlchemy is clever enough to know hwo to open and close connections, so we don't have to worry about that if we wrtie those two lines.


		@copy_current_request_context #this is like the bridge to send the email in the background..
		def send_message(email,username):
			send_email(email, username)
		sender = threading.Thread(name='mail_sender', 
								  target = send_message,
								  args = (user.email, user.username)) #arguments of the function that sends the email.

		sender.start()

		success_message = 'User registered in the database'
		flash(success_message)

	return render_template('create.html', form = create_form)

@app.route('/reviews/', methods=['GET'])
@app.route('/reviews/<int:page>', methods = ['GET']) #we have to write it twice to make pages
def reviews(page = 1): # =1 is only the default value, so /reviews/ and /reviews/1 is the same
	per_page = 1000
	comment_list = Comment.query.join(userstest).add_columns(
					userstest.username,  #the model, not the table
					Comment.text,
					Comment.created_date).paginate(page,per_page,True) #(page, rows per page, if True=404, if False: empty)
	return render_template('reviews.html', comments = comment_list, date_format = date_format) #we send the function as a parameter


@app.after_request
def after_request(response):
	return response #always return response

db.init_app(app) #this was supposed to be inside if __name__ but it didn't work: https://stackoverflow.com/questions/30764073/sqlalchemy-extension-isnt-registered-when-running-app-with-gunicorn
mail.init_app(app) #same as db.init_app

if __name__ == '__main__':
	#before config:
	#app.run(debug=True)

	csrf.init_app(app) #this one after config
	#db.init_app(app)
	#mail.init_app(app)

	with app.app_context():
		db.create_all() #this will create every table that IS NOT created already

	app.run()





