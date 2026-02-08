from flask import Flask, request, jsonify
from flask_cors import CORS  # Потрібно встановити: pip install flask-cors
from database import Database

app = Flask(__name__)
CORS(app) # Дозволяє запити з будь-яких доменів (зокрема з Netlify)

db = Database("space.db")

# Повний каталог з описами, які очікує JS
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

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        family_id = request.args.get('family_id')
        if not family_id:
            return jsonify({'error': 'No family_id provided'}), 400

        data = db.get_family_resources(family_id)
        if not data:
            return jsonify({'error': 'Family not found'}), 404

        # Мапінг усіх ресурсів з бази (індекси 0-8)
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
        return jsonify({'error': str(e)}), 500

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)