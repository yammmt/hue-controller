import os

from dotenv import load_dotenv
from flask import Flask
from flask import render_template
import requests


def create_app(test_config=None):
    # create and configure the app
    load_dotenv()
    # TODO: add dotenv check: if required env doesn't exist, raise error
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )

    # create API endpoint URL
    API_ENDPOINT = "http://{}/api/{}/groups/{}/action".format(
        os.getenv('BRIDGE_IP_ADDR'),
        os.getenv('USERNAME'),
        os.getenv('GROUP')
    )
    print(API_ENDPOINT)

    # TODO: check meaning
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/on')
    def on():
        r = requests.put(
            API_ENDPOINT,
            json={"on": True}
        )
        print(r.text)
        return render_template('index.html')

    @app.route('/off')
    def off():
        r = requests.put(
            API_ENDPOINT,
            json={"on": False}
        )
        print(r.text)
        return render_template('index.html')

    @app.route('/d50')
    def d50():
        r = requests.put(
            API_ENDPOINT,
            json={"ct": 200}
        )
        print(r.text)
        return render_template('index.html')

    @app.route('/d65')
    def d65():
        r = requests.put(
            API_ENDPOINT,
            json={"ct": 153}
        )
        print(r.text)
        return render_template('index.html')

    @app.route('/lamp')
    def lamp():
        r = requests.put(
            API_ENDPOINT,
            json={"ct": 357}
        )
        print(r.text)
        return render_template('index.html')

    return app
