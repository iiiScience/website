from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Config import Config

config = Config()

# Database stuff
_engine = create_engine(config.get('database', 'path'))
Session = sessionmaker(bind=_engine)

app = Flask(
	__name__, 
	static_folder=config.get('flask', 'static_folder', 'static')
)
app.debug=config.get_bool('flask', 'debug')

entities = ['contact', 'institution', 'keyword', 'department', 'equipment', 'protocol']
fields = ['name', 'email', 'institution', 'keywords', 'department', 'details', 'url']
actions = ['list', 'search']