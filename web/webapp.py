from flask import Flask, render_template, jsonify, request ,redirect, url_for
from core.status import AppStatus, status_manager

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    status = status_manager.get_status()

    if request.method == 'POST':
        obj = request.form.get('obj')
        if isinstance(obj, str) and obj.strip():
            try:
                status_manager.set_status(AppStatus.POINTING, obj.strip())
            except ValueError as e:
                return f"Erreur : {e}", 400

            return redirect(url_for('index'))

    return render_template(
        'index.html',
        status=status['status'],
        target_name=status['target'],
        established=status['established']
    )

@app.route('/status')
def status():
    return jsonify(status_manager.get_status())

if __name__=="__main__":
    app.run()