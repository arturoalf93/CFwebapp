from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()

class userstest(db.Model): #this is imported then in main.py, so if the name changes, change the name there as well
	#by default, the table will created using the same name as the class, if we wanted to create a table with a different name (not sure why we would):
	#__tablename__ = 'users'

	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(50), unique = True)
	email = db.Column(db.String(40))
	password = db.Column(db.String(94))
	#In order for the FK to work:
	comments = db.relationship('Comment') #name of the class, not of the table (usually it would be the same.). A column will not be created
	created_date = db.Column(db.DateTime, default = datetime.datetime.now)

	def __init__(self, username, password, email):
		self.username = username
		self.password = self.__create_password(password)
		self.email = email

	def __create_password(self, password):
		return generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password, password)


class Comment(db.Model):
	__tablename__ = 'comments'

	id = db.Column(db.Integer, primary_key = True)
	user_id = db.Column(db.Integer, db.ForeignKey('userstest.id')) #FOREIGN KEY. We also have to write the relationship in userstest
	text = db.Column(db.Text()) #Text is just larger than String
	created_date = db.Column(db.DateTime, default = datetime.datetime.now)
