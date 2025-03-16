from flask import Blueprint, render_template
import time

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def home():
    return 'success', 200

@views.route("/clearlog")
def clearlog():
    with open('app.log', 'w'):
        pass
    return 'Debug Log Cleared', 200