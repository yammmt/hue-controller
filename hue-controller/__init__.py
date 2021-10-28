import os

from dotenv import load_dotenv
from flask import Flask
from flask import render_template
import requests

from . import party_color


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

    party_color_thread = []

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/on')
    def on():
        send_json_to_bridge({"on": True})
        return render_template('index.html')

    @app.route('/off')
    def off():
        send_json_to_bridge({"on": False})
        return render_template('index.html')

    @app.route('/d50')
    def d50():
        stop_gradation()
        send_json_to_bridge({"ct": 200})
        return render_template('index.html')

    @app.route('/d65')
    def d65():
        stop_gradation()
        send_json_to_bridge({"ct": 153})
        return render_template('index.html')

    @app.route('/lamp')
    def lamp():
        stop_gradation()
        send_json_to_bridge({"ct": 357})
        return render_template('index.html')

    @app.route('/start_party')
    def start_party():
        # boost saturation to describe colors
        send_json_to_bridge({"sat": 200})
        start_gradation()
        return render_template('index.html')

    @app.route('/stop_party')
    def stop_party():
        stop_gradation()
        return render_template('index.html')

    def start_gradation():
        print("start_gradation")
        if party_color_thread:
            return

        t = party_color.PartyColor(send_json_to_bridge)
        t.start()
        party_color_thread.append(t)

    def stop_gradation():
        print("stop_gradation")
        if not party_color_thread:
            return

        party_color_thread[0].stop()
        del party_color_thread[0]

    # TODO: use logger instead of `print`
    def send_json_to_bridge(json_data):
        r = requests.put(
            API_ENDPOINT,
            json=json_data
        )
        print(r.text)

    return app
