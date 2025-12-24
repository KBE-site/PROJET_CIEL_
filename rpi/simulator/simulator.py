from flask import Flask, render_template, jsonify

from core.status import status_manager

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/status')
def status():
    return jsonify(status_manager.get_status())

if __name__=="__main__":
    app.run(host="0.0.0.0", port=8081, debug=True)