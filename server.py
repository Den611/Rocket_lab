from flask import Flask, request, jsonify
from database import Database

app = Flask(__name__)
# Вказуємо шлях до основної бази. resourses.db підключиться автоматично через ATTACH в __init__
db = Database("space.db")

# Каталог модулів (має збігатися з ID у ваших tree_*.js)
CATALOG = {
    'gu1': {'name': 'Конус-верхівка', 'type': 'nose', 'tier': 'I', 'desc': 'Базовий обтікач.'},
    'gu2': {'name': 'Сенсорний шпиль', 'type': 'nose', 'tier': 'II', 'desc': 'З датчиками.'},
    'nc1': {'name': 'Корпус', 'type': 'body', 'tier': 'I', 'desc': 'Алюмінієвий корпус.'},
    'h1': {'name': 'Сталевий Корпус', 'type': 'body', 'tier': 'II', 'desc': 'Посилений корпус.'},
    'e1': {'name': 'Турбіна', 'type': 'engine', 'tier': 'I', 'desc': 'Базовий двигун.'},
    'e2': {'name': 'Турбо-нагнітач', 'type': 'engine', 'tier': 'II', 'desc': 'Потужна тяга.'},
    'a1': {'name': 'Надкрилки', 'type': 'fins', 'tier': 'I', 'desc': 'Стабілізація.'},
    'a2': {'name': 'Активні закрилки', 'type': 'fins', 'tier': 'II', 'desc': 'Маневрування.'}
}

@app.route('/api/get_upgrades')
def get_upgrades():
    family_id = request.args.get('family_id')
    return jsonify(db.get_family_unlocked_modules(family_id))

@app.route('/api/upgrade', methods=['POST'])
def upgrade():
    data = request.json
    # Перевірка наявності ключів
    if not data or 'family_id' not in data or 'module' not in data:
        return jsonify({"success": False, "message": "Missing data"}), 400
    
    success, msg = db.buy_module_upgrade(data['family_id'], data['module'])
    return jsonify({"success": success, "message": msg})

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        family_id = request.args.get('family_id')
        if not family_id:
            return jsonify({'error': 'No family_id provided'}), 400

        data = db.get_full_inventory(family_id)
        if not data:
            return jsonify({'error': 'Family not found'}), 404

        # Співставляємо ID куплених модулів з інформацією з каталогу
        modules_details = []
        for mid in data['owned_modules']:
            if mid in CATALOG:
                info = CATALOG[mid].copy()
                info['id'] = mid
                modules_details.append(info)

        return jsonify({
            'resources': data['resources'],
            'modules': modules_details
        })

    except Exception as e:
        app.logger.error(f"Inventory Route Error: {e}")
        return jsonify({'error': "Internal Server Error"}), 500

def run_flask():
    # host='0.0.0.0' дозволяє підключатися зовні
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)