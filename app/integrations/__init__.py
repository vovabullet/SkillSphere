from flask import Blueprint

bp = Blueprint('integrations', __name__)

from app.integrations import routes
