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

# --- ДОДАТИ ЦЕ В SERVER.PY ---

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    try:
        family_id = request.args.get('family_id')
        if not family_id:
            return jsonify({'error': 'No family_id provided'}), 400

        # 1. Отримуємо ресурси з бази
        # (припустимо, що у вас є функція get_resources або схожий запит)
        # Якщо використовуєте database.py, замініть це на реальний виклик
        # resources = database.get_resources(family_id) 
        
        # ТИМЧАСОВА ІМІТАЦІЯ (замініть на запит до БД):
        con = sqlite3.connect("resourses.db")
        cur = con.cursor()
        # Приклад запиту (підлаштуйте під вашу структуру таблиці!)
        cur.execute("SELECT iron, fuel, money FROM resources WHERE family_id = ?", (family_id,))
        row = cur.fetchone()
        con.close()
        
        resources_data = {}
        if row:
             resources_data = {
                'iron': row[0],
                'fuel': row[1],
                'coins': row[2]
            }
        else:
             # Якщо запису немає, повертаємо нулі
             resources_data = {'iron': 0, 'fuel': 0, 'coins': 0}


        # 2. Отримуємо куплені модулі
        # Тут треба взяти список ID куплених модулів і співставити їх з описом
        # Цю структуру краще взяти з ваших файлів tree_*.js, але тут приклад:
        
        con = sqlite3.connect("space.db") # або де ви зберігаєте апгрейди
        cur = con.cursor()
        cur.execute("SELECT upgrade_id FROM upgrades WHERE family_id = ?", (family_id,))
        upgrades_rows = cur.fetchall()
        con.close()
        
        owned_ids = [r[0] for r in upgrades_rows]
        
        # Простий каталог модулів (щоб сервер знав назви)
        # В ідеалі це має бути в окремому файлі config.py
        catalog = {
            'gu1': {'name': 'Конус-верхівка', 'type': 'nose', 'tier': 'I', 'desc': 'Базовий обтікач.'},
            'gu2': {'name': 'Сенсорний шпиль', 'type': 'nose', 'tier': 'II', 'desc': 'З датчиками.'},
            'nc1': {'name': 'Корпус', 'type': 'body', 'tier': 'I', 'desc': 'Алюмінієвий корпус.'},
            'h1': {'name': 'Сталевий Корпус', 'type': 'body', 'tier': 'II', 'desc': 'Посилений корпус.'},
            'e1': {'name': 'Турбіна', 'type': 'engine', 'tier': 'I', 'desc': 'Базовий двигун.'},
            'e2': {'name': 'Турбо-нагнітач', 'type': 'engine', 'tier': 'II', 'desc': 'Потужна тяга.'},
            'a1': {'name': 'Надкрилки', 'type': 'fins', 'tier': 'I', 'desc': 'Стабілізація.'},
            'a2': {'name': 'Активні закрилки', 'type': 'fins', 'tier': 'II', 'desc': 'Маневрування.'}
        }

        modules_list = []
        for uid in owned_ids:
            if uid in catalog:
                mod_info = catalog[uid]
                mod_info['id'] = uid # додаємо ID в об'єкт
                modules_list.append(mod_info)

        return jsonify({
            'resources': resources_data,
            'modules': modules_list
        })

    except Exception as e:
        print(f"Inventory Error: {e}")
        return jsonify({'error': str(e)}), 500