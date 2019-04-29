from flask import Flask

app = Flask(__name__)

from admin.controller import admin
#from admin.controller.admin import pc
#app.register_blueprint(pc,url_prefix='/pc')