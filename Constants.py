from flask import Flask
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Database stuff
_engine = create_engine('postgresql://iiiscience:Q7l%2F%2F#En25@localhost:5432/iiiscience')
Session = sessionmaker(bind=_engine)

app = Flask(__name__)

entities = ['contact', 'institution', 'keyword', 'department', 'equipment', 'protocol']
fields = ['name', 'email', 'institution', 'keywords', 'department', 'details', 'url']
actions = ['list', 'search']