from flask import Flask, request, jsonify
from database import Database

app = Flask(__name__)
db = Database("space.db")

@app.route('/api/get_upgrades')
def get_upgrades():
    family_id = request.args.get('family_id')
    return jsonify(db.get_family_unlocked_modules(family_id))

@app.route('/api/upgrade', methods=['POST'])
def upgrade():
    data = request.json
    success, msg = db.buy_module_upgrade(data['family_id'], data['module'])
    return jsonify({"success": success, "message": msg})

def run_flask():
    app.run(host='0.0.0.0', port=5000)