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

        # Використовуємо існуючий об'єкт db, який вже має ATTACH DATABASE
        # Отримуємо дані через один метод, щоб не відкривати нові з'єднання
        data = db.get_family_resources(family_id)
        
        if not data:
            return jsonify({'error': 'Family not found'}), 404

        # Мапінг даних згідно з вашим методом get_family_resources у database.py:
        # index 0: balance, 1: res_iron, 2: res_fuel, ...
        resources_data = {
            'coins': data[0],
            'iron': data[1], # JS чекає 'iron'
            'fuel': data[2], # JS чекає 'fuel'
            'regolith': data[3]
        }

        # Отримуємо модулі
        owned_ids = db.get_family_unlocked_modules(family_id)
        
        catalog = {
            'gu1': {'name': 'Конус-верхівка', 'type': 'nose', 'tier': 'I'},
            'nc1': {'name': 'Корпус', 'type': 'body', 'tier': 'I'},
            'e1': {'name': 'Турбіна', 'type': 'engine', 'tier': 'I'},
            'a1': {'name': 'Надкрилки', 'type': 'fins', 'tier': 'I'}
        }

        modules_list = []
        for uid in owned_ids:
            if uid in catalog:
                mod_info = catalog[uid].copy()
                mod_info['id'] = uid
                modules_list.append(mod_info)

        return jsonify({
            'resources': resources_data,
            'modules': modules_list
        })

    except Exception as e:
        print(f"Inventory Error: {e}")
        return jsonify({'error': str(e)}), 500
def run_flask():
    # host='0.0.0.0' дозволяє підключатися зовні
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)