import secrets

from flask import Flask, render_template, jsonify, request ,redirect, url_for, flash

from core.status import status_manager
from core.manager import Manager
from core.helpers import handle_error
from core.websocket import socketio

app = Flask(__name__)
manager = Manager()
app.config['SECRET_KEY'] = secrets.token_hex(16)

socketio.init_app(app)

@socketio.on('connect')
def handle_connect():
    status = status_manager.get_status()
    socketio.emit('status_update', status)


@socketio.on('disconnect')
def handle_disconnect():
    pass

@app.route('/', methods=['GET'])
@app.route('/index', methods=['GET'])
def index():
    status = status_manager.get_status()

    return render_template(
        'index.html',
        status=status['status'],
        target_name=status['target'],
        established=status['established']
    )

@app.route('/pointing', methods=['POST'])
@handle_error
def pointing():
    obj = request.form.get('obj')
    manager.point_to(obj) # type: ignore

    return redirect(url_for("index"))

@app.route('/stop_pointing', methods=['POST'])
@handle_error
def stop_pointing():
    manager.stop_pointing()

    return redirect(url_for('index'))

@app.route('/status')
def status():
    return jsonify(status_manager.get_status())

if __name__=="__main__":
    socketio.run(app, host="0.0.0.0", port=8080, debug=True)