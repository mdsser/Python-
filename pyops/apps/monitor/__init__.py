from flask import Blueprint

monitor_bp = Blueprint('monitor', __name__)

from . import views