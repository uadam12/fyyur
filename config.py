import os
SECRET_KEY = "12345"
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
#SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost/fyyur'

SQLALCHEMY_TRACK_MODIFICATIONS = False
