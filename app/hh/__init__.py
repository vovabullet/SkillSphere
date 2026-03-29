from flask import Blueprint

bp = Blueprint('hh', __name__)

from app.hh import routes
