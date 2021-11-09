import os

from dotenv import load_dotenv
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
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

    # create API endpoint UR
    GET_ENDPOINT = "http://{}/api/{}/groups/{}".format(
        os.getenv('BRIDGE_IP_ADDR'),
        os.getenv('USERNAME'),
        os.getenv('GROUP')
    )
    app.logger.info("endpoint (get): {}".format(GET_ENDPOINT))
    POST_ENDPOINT = "http://{}/api/{}/groups/{}/action".format(
        os.getenv('BRIDGE_IP_ADDR'),
        os.getenv('USERNAME'),
        os.getenv('GROUP')
    )
    app.logger.info("endpoint (post): {}".format(POST_ENDPOINT))

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

    # const values
    DEFAULT_HUE_INC = 5000
    DEFAULT_COLOR_CMD_INTERVAL_SEC = 3.0

    party_color_thread = []

    @app.route('/')
    def index():
        r = requests.get(GET_ENDPOINT)
        bri = r.json()['action']['bri']
        sat = r.json()['action']['sat']
        return render_template('index.html', bri=bri, sat=sat)

    @app.route('/on')
    def on():
        send_json_to_bridge({"on": True})
        return redirect(url_for('index'))

    @app.route('/off')
    def off():
        send_json_to_bridge({"on": False})
        return redirect(url_for('index'))

    # TODO: add GET method
    @app.route('/brightness', methods=["POST"])
    def brightness():
        send_json_to_bridge({"bri": int(request.form['brightness'])})
        return redirect(url_for('index'))

    # TODO: add GET method
    @app.route('/saturation', methods=["POST"])
    def saturation():
        send_json_to_bridge({"sat": int(request.form['saturation'])})
        return redirect(url_for('index'))

    # TODO: add GET method
    @app.route('/transitiontime', methods=["POST"])
    def transitiontime():
        send_json_to_bridge({"transitiontime": int(request.form['transition_time']) // 100})
        return redirect(url_for('index'))

    @app.route('/d50')
    def d50():
        stop_gradation()
        send_json_to_bridge({"ct": 200})
        return redirect(url_for('index'))

    @app.route('/d65')
    def d65():
        stop_gradation()
        send_json_to_bridge({"ct": 153})
        return redirect(url_for('index'))

    @app.route('/lamp')
    def lamp():
        stop_gradation()
        send_json_to_bridge({"ct": 357})
        return redirect(url_for('index'))

    @app.route('/start_party')
    def start_party():
        stop_gradation()
        start_gradation()
        return redirect(url_for('index'))

    @app.route('/start_intense_party')
    def start_party_danger():
        stop_gradation()
        start_gradation(
            hue_inc=7000,
            cmd_interval_sec=0.3
        )
        return redirect(url_for('index'))

    @app.route('/stop_party')
    def stop_party():
        stop_gradation()
        return redirect(url_for('index'))

    def start_gradation(
        hue_inc=DEFAULT_HUE_INC,
        cmd_interval_sec=DEFAULT_COLOR_CMD_INTERVAL_SEC
    ):
        app.logger.debug("start_gradation")
        if party_color_thread:
            return

        t = party_color.PartyColor(
            send_json_to_bridge,
            hue_inc,
            cmd_interval_sec
        )
        t.start()
        party_color_thread.append(t)

    def stop_gradation():
        app.logger.debug("stop_gradation")
        if not party_color_thread:
            return

        party_color_thread[0].stop()
        del party_color_thread[0]

    def send_json_to_bridge(json_data):
        r = requests.put(
            POST_ENDPOINT,
            json=json_data
        )
        app.logger.info(r.text)

    return app
