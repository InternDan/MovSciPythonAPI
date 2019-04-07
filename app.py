from flask import Flask
import configs

app = Flask(__name__)
app.config['DEBUG'] = configs.debug     # displays runtime errors in the browser, too