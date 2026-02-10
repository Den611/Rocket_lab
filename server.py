from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from database import Database
import os

# Вказуємо, що статичні файли (html, css, js) лежать прямо тут ('.')
app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# Підключення до бази (залишається як було)
db = Database() 

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

# --- НОВІ МАРШРУТИ ДЛЯ САЙТУ ---

@app.route('/')
def index():
    # Головна сторінка
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Будь-які інші файли (CSS, JS, картинки, інші HTML)
    return send_from_directory('.', path)

# -------------------------------

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        family_id = request.args.get('family_id')
        if not family_id:
            return jsonify({'error': 'No family_id provided'}), 400

        data = db.get_family_resources(family_id)
        if not data:
            return jsonify({'error': 'Family not found'}), 404

        resources_data = {
            'coins': data[0],
            'iron': data[1],
            'fuel': data[2],
            'regolith': data[3],
            'he3': data[4],
            'silicon': data[5],
            'oxide': data[6],
            'hydrogen': data[7],
            'helium': data[8]
        }

        owned_ids = db.get_family_unlocked_modules(family_id)
        
        modules_list = []
        for uid in owned_ids:
            if uid in CATALOG:
                mod_info = CATALOG[uid].copy()
                mod_info['id'] = uid
                modules_list.append(mod_info)

        return jsonify({
            'resources': resources_data,
            'modules': modules_list
        })
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/get_upgrades', methods=['GET'])
def get_upgrades():
    family_id = request.args.get('family_id')
    if not family_id:
        return jsonify([])
    # Отримуємо список ID відкритих модулів із бази даних
    unlocked_modules = db.get_family_unlocked_modules(family_id)
    return jsonify(unlocked_modules)

@app.route('/api/upgrade', methods=['POST'])
def upgrade_module():
    try:
        data = request.json
        family_id = data.get('family_id')
        module_id = data.get('module_id')
        cost = data.get('cost')
        req = data.get('req')

        if not family_id or not module_id:
            return jsonify({'success': False, 'error': 'Недостатньо даних (відсутній ID сім\'ї або модуля)'})

        # Формуємо об'єкт модуля, як того очікує database.py
        module_params = {
            'id': module_id,
            'cost': cost,
            'req': req
        }

        # ВИПРАВЛЕНО: Виклик існуючого методу buy_module_upgrade замість buy_upgrade
        success, message = db.buy_module_upgrade(family_id, module_params)
        
        if success:
            return jsonify({'success': True, 'message': message})
        else:
            return jsonify({'success': False, 'error': message})
            
    except Exception as e:
        print(f"Помилка на сервері: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
    
def run_flask():
    # Port 5000 стандартний, Render сам його прокине
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)