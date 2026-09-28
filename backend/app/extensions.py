"""Shared Flask extensions."""

from flask_sqlalchemy import SQLAlchemy
from flask_session import Session

db = SQLAlchemy()
server_session = Session()
