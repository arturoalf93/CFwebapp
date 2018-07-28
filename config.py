import os #because we should read the secret_key from an environment variable, not from the code itself
import sys


try:
	emailpwd = os.environ["MY_TEST_EMAIL_PWD"]
except KeyError:
	print ("Please set the environment variable MY_TEST_EMAIL_PWD")
	sys.exit(1)

class Config(object):
	SECRET_KEY = 'my_secret_key_here_or_env_var'
	'''try:
		SECRET_KEY = os.environ["ABC"]
	except KeyError:
		print ("Please set the environment variable")
		sys.exit(1)'''
	MAIL_SERVER = 'smtp.gmail.com'
	MAIL_PORT = 587
	MAIL_USE_SSL = False
	MAIL_USE_TLS = True
	MAIL_USERNAME = 'solutionmaptest@gmail.com'
	MAIL_PASSWORD = emailpwd

try:
	dbpwd = os.environ["MY_DB_PWD"]
except KeyError:
	print ("Please set the environment variable MY_DB_PWD")
	sys.exit(1)

class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = 'mysql://root:' + dbpwd + '@localhost/solutionmaps'
	SQLALCHEMY_TRACK_MODIFICATIONS = False #to avoid the warning every time we exceute

#we would have a production environment as well here