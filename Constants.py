from flask import Flask
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

# Database stuff
_engine = create_engine('sqlite:///iiiscience.db')
def _fk_pragma_on_connect(dbapi_con, con_record):
    dbapi_con.execute('pragma foreign_keys=ON')
event.listen(_engine, 'connect', _fk_pragma_on_connect)
Session = sessionmaker(bind=_engine)

app = Flask(__name__)

entities = ['contact', 'institution', 'keyword', 'department', 'equipment', 'protocol']
fields = ['name', 'email', 'institution', 'keywords', 'department', 'details', 'url']
actions = ['list', 'search']