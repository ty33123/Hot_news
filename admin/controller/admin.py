from web import app
from flask import render_template
import json
from admin.controller.data_source import get_hot_news
# pc = Blueprint('pc',__name__)


@app.route('/get_hot_news')
def get_news():
    return json.dumps(get_hot_news())


@app.route('/')
def index():
    return render_template('hot_news.html')
