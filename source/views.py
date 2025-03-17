from flask import Blueprint, render_template
import time

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
def home():
    return render_template('base.html')

@views.route("/clearlog")
def clearlog():
    with open('condenserr_debug.log', 'w'):
        pass
    return 'Debug Log Cleared', 200

