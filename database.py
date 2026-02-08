import sqlite3
import random
import string
import datetime

class Database:
    def __init__(self, db_file):
        # ВИПРАВЛЕНО: додано check_same_thread=False для стабільної роботи з Flask
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()
        
        # Підключаємо другу базу даних як 'res'
        self.cursor.execute("ATTACH DATABASE 'resourses.db' AS res")
        self.create_tables()

    def create_tables(self):
        # 1. Сім'ї (У 'space.db' залишаємо тільки гроші і прогрес)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                invite_code TEXT UNIQUE,
                balance INTEGER DEFAULT 1000,

                engine_lvl INTEGER DEFAULT 1,
                hull_lvl INTEGER DEFAULT 1,
                current_planet TEXT DEFAULT 'Earth',

                mine_lvl INTEGER DEFAULT 0,
                last_collection DATETIME DEFAULT CURRENT_TIMESTAMP,

                mission_end_time DATETIME DEFAULT NULL,
                active_launch_id INTEGER DEFAULT NULL,
                active_mission_id INTEGER DEFAULT NULL,
                upgrade_end_time DATETIME DEFAULT NULL,

                last_raid_time DATETIME DEFAULT NULL,
                shield_until DATETIME DEFAULT NULL
            )
        """)
        
        # 2. Таблиця ресурсів у другій базі (якщо раптом не створена)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS res.storage (
                family_id INTEGER PRIMARY KEY,
                res_iron INTEGER DEFAULT 0, res_fuel INTEGER DEFAULT 0,
                res_regolith INTEGER DEFAULT 0, res_he3 INTEGER DEFAULT 0,
                res_silicon INTEGER DEFAULT 0, res_oxide INTEGER DEFAULT 0,
                res_hydrogen INTEGER DEFAULT 0, res_helium INTEGER DEFAULT 0,
                bonus_received BOOLEAN DEFAULT 0
            )
        """)

        # 3. Інші таблиці (Користувачі, Місії, Запуски) - без змін
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                family_id INTEGER DEFAULT NULL,
                role TEXT DEFAULT 'recruit',
                FOREIGN KEY(family_id) REFERENCES families(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                difficulty INTEGER,
                reward INTEGER,
                planet TEXT DEFAULT 'Earth',
                is_boss_mission BOOLEAN DEFAULT 0,
                cost_money INTEGER DEFAULT 0,
                req_res_name TEXT DEFAULT NULL,
                req_res_amount INTEGER DEFAULT 0,
                flight_time INTEGER DEFAULT 10,
                pirate_risk INTEGER DEFAULT 10
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS launches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER,
                mission_id INTEGER,
                status TEXT DEFAULT 'pending',
                signatures TEXT DEFAULT '',
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(family_id) REFERENCES families(id),
                FOREIGN KEY(mission_id) REFERENCES missions(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS family_upgrades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                family_id INTEGER,
                module_id TEXT,  -- ID з вашого JS (наприклад, 'hull_mk2', 'eng_ultimate')
                unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(family_id) REFERENCES families(id)
            )
        """)
        self.connection.commit()

    # --- МЕТОДИ ДЛЯ РОБОТИ З ДВОМА БАЗАМИ ---

    def create_family(self, user_id, family_name):
        invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        with self.connection:
            # 1. Створюємо сім'ю в основній базі
            self.cursor.execute("INSERT INTO families (name, invite_code, balance) VALUES (?, ?, 1000)",
                                (family_name, invite_code))
            family_id = self.cursor.lastrowid
            
            # 2. Створюємо запис в resourses.db
            self.cursor.execute("INSERT INTO res.storage (family_id) VALUES (?)", (family_id,))
            
            self.cursor.execute("UPDATE users SET family_id = ?, role = 'captain' WHERE user_id = ?",
                                (family_id, user_id))
            return invite_code

    def get_family_resources(self, family_id):
        with self.connection:
            # ВИПРАВЛЕНО: Чітко визначаємо порядок полів для мапінгу в server.py
            res = self.cursor.execute("""
                SELECT 
                    f.balance, 
                    r.res_iron, r.res_fuel, r.res_regolith, r.res_he3, 
                    r.res_silicon, r.res_oxide, r.res_hydrogen, r.res_helium, 
                    f.mine_lvl, f.last_collection, f.current_planet 
                FROM families f
                LEFT JOIN res.storage r ON f.id = r.family_id
                WHERE f.id = ?
            """, (family_id,)).fetchone()
            return res

    def deduct_resources(self, family_id, money, res_name=None, res_amount=0):
        with self.connection:
            if money > 0:
                self.cursor.execute("UPDATE families SET balance = balance - ? WHERE id = ?", (money, family_id))
            
            if res_name and res_amount > 0:
                # Звертаємось до таблиці res.storage
                query = f"UPDATE res.storage SET {res_name} = {res_name} - ? WHERE family_id = ?"
                self.cursor.execute(query, (res_amount, family_id))

    def collect_resources(self, family_id, res1_col, amount1, res2_col, amount2):
        MAX_STORAGE = 10000
        with self.connection:
            query = f"UPDATE res.storage SET {res1_col} = {res1_col} + ?, {res2_col} = {res2_col} + ? WHERE family_id = ?"
            self.cursor.execute(query, (amount1, amount2, family_id))
            self.cursor.execute("UPDATE families SET last_collection = CURRENT_TIMESTAMP WHERE id = ?", (family_id,))

    def admin_add_resources(self, family_id):
        with self.connection:
            self.cursor.execute("UPDATE families SET balance = balance + 50000 WHERE id = ?", (family_id,))
            self.cursor.execute("""
                UPDATE res.storage SET 
                res_iron = res_iron + 1000, res_fuel = res_fuel + 1000,
                res_regolith = res_regolith + 1000, res_he3 = res_he3 + 1000,
                res_silicon = res_silicon + 1000, res_oxide = res_oxide + 1000,
                res_hydrogen = res_hydrogen + 1000, res_helium = res_helium + 1000
                WHERE family_id = ?
            """, (family_id,))

    # --- НОВИЙ МЕТОД ДЛЯ БОНУСА ---
    def claim_bonus(self, family_id, amount=100):
        with self.connection:
            # Перевіряємо в resourses.db
            row = self.cursor.execute("SELECT bonus_received FROM res.storage WHERE family_id = ?", (family_id,)).fetchone()
            if row and row[0]: # Якщо 1 (True)
                return False
            
            # Нараховуємо ресурси
            self.cursor.execute(f"""
                UPDATE res.storage SET 
                res_iron = res_iron + {amount}, res_fuel = res_fuel + {amount},
                res_regolith = res_regolith + {amount}, res_he3 = res_he3 + {amount},
                res_silicon = res_silicon + {amount}, res_oxide = res_oxide + {amount},
                res_hydrogen = res_hydrogen + {amount}, res_helium = res_helium + {amount},
                bonus_received = 1
                WHERE family_id = ?
            """, (family_id,))
            return True

    # --- СТАНДАРТНІ МЕТОДИ (Без змін, але потрібні для роботи) ---
    def user_exists(self, user_id):
        with self.connection:
            return bool(self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall())

    def add_user(self, user_id, username):
        if not self.user_exists(user_id):
            with self.connection:
                self.cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))

    def get_user_family(self, user_id):
        with self.connection:
            res = self.cursor.execute("SELECT family_id FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return res[0] if res else None

    def join_family(self, user_id, invite_code):
        with self.connection:
            family = self.cursor.execute("SELECT id FROM families WHERE invite_code = ?", (invite_code,)).fetchone()
            if family:
                self.cursor.execute("UPDATE users SET family_id = ? WHERE user_id = ?", (family[0], user_id))
                return True
            return False

    def get_family_info(self, family_id):
        with self.connection:
            return self.cursor.execute(
                "SELECT name, invite_code, balance, engine_lvl, hull_lvl, current_planet FROM families WHERE id = ?",
                (family_id,)).fetchone()

    def get_family_members(self, family_id):
        with self.connection:
            return self.cursor.execute("SELECT username, role FROM users WHERE family_id = ?", (family_id,)).fetchall()

    def leave_family(self, user_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET family_id = NULL, role = 'recruit' WHERE user_id = ?", (user_id,))

    def update_balance(self, family_id, amount):
        with self.connection:
            self.cursor.execute("UPDATE families SET balance = balance + ? WHERE id = ?", (amount, family_id))

    def move_family_to_planet(self, family_id, new_planet):
        with self.connection:
            self.cursor.execute("UPDATE families SET current_planet = ?, mine_lvl = 0 WHERE id = ?", (new_planet, family_id))

    def update_upgrade(self, family_id, upgrade_type):
        with self.connection:
            self.cursor.execute(f"UPDATE families SET {upgrade_type} = {upgrade_type} + 1 WHERE id = ?", (family_id,))

    # Методи місій та запусків
    def add_mission(self, name, description, difficulty, reward, planet, is_boss, cost_money=0, req_res=None, req_amt=0, flight_time=10, pirate_risk=10):
        with self.connection:
            self.cursor.execute("""
                INSERT INTO missions (name, description, difficulty, reward, planet, is_boss_mission, cost_money, req_res_name, req_res_amount, flight_time, pirate_risk) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, description, difficulty, reward, planet, is_boss, cost_money, req_res, req_amt, flight_time, pirate_risk))

    def get_missions_by_planet(self, planet_name):
        with self.connection:
            return self.cursor.execute("""
                SELECT id, name, description, reward, is_boss_mission, cost_money, flight_time, pirate_risk 
                FROM missions WHERE planet = ?
            """, (planet_name,)).fetchall()

    def get_mission_by_id(self, mission_id):
        with self.connection:
            return self.cursor.execute("SELECT * FROM missions WHERE id = ?", (mission_id,)).fetchone()

    def start_launch(self, family_id, mission_id):
        with self.connection:
            self.cursor.execute("INSERT INTO launches (family_id, mission_id) VALUES (?, ?)", (family_id, mission_id))
            return self.cursor.lastrowid

    def sign_launch(self, launch_id, user_id):
        with self.connection:
            row = self.cursor.execute("SELECT signatures FROM launches WHERE id = ?", (launch_id,)).fetchone()
            if not row: return False
            sigs = row[0].split(',') if row[0] else []
            if str(user_id) in sigs: return False
            sigs.append(str(user_id))
            new_sigs = ",".join(filter(None, sigs))
            self.cursor.execute("UPDATE launches SET signatures = ? WHERE id = ?", (new_sigs, launch_id))
            return len(sigs)

    def update_launch_status(self, launch_id, status):
        with self.connection:
            self.cursor.execute("UPDATE launches SET status = ? WHERE id = ?", (status, launch_id))

    def get_timers(self, family_id):
        with self.connection:
            return self.cursor.execute("SELECT mission_end_time, active_launch_id, active_mission_id, upgrade_end_time FROM families WHERE id = ?", (family_id,)).fetchone()

    def set_mission_timer(self, family_id, minutes, launch_id, mission_id):
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        with self.connection:
            self.cursor.execute("UPDATE families SET mission_end_time = ?, active_launch_id = ?, active_mission_id = ? WHERE id = ?", (end_time, launch_id, mission_id, family_id))

    def clear_mission_timer(self, family_id):
        with self.connection:
            self.cursor.execute("UPDATE families SET mission_end_time = NULL, active_launch_id = NULL, active_mission_id = NULL WHERE id = ?", (family_id,))

    def set_upgrade_timer(self, family_id, minutes):
        end_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
        with self.connection:
            self.cursor.execute("UPDATE families SET upgrade_end_time = ? WHERE id = ?", (end_time, family_id))

    def finish_upgrade(self, family_id):
        with self.connection:
            self.cursor.execute("UPDATE families SET mine_lvl = mine_lvl + 1, last_collection = CURRENT_TIMESTAMP, upgrade_end_time = NULL WHERE id = ?", (family_id,))

    def get_expired_missions(self):
        with self.connection:
            return self.cursor.execute("SELECT id, active_mission_id, active_launch_id, current_planet FROM families WHERE mission_end_time <= CURRENT_TIMESTAMP AND mission_end_time IS NOT NULL").fetchall()

    def get_expired_upgrades(self):
        with self.connection:
            return self.cursor.execute("SELECT id, current_planet, mine_lvl FROM families WHERE upgrade_end_time <= CURRENT_TIMESTAMP AND upgrade_end_time IS NOT NULL").fetchall()

    def get_family_user_ids(self, family_id):
        with self.connection:
            res = self.cursor.execute("SELECT user_id FROM users WHERE family_id = ?", (family_id,)).fetchall()
            return [row[0] for row in res]
            
    def admin_skip_timers(self, family_id):
        with self.connection:
            past_time = datetime.datetime.now() - datetime.timedelta(minutes=1)
            self.cursor.execute("UPDATE families SET mission_end_time = ? WHERE id = ? AND mission_end_time IS NOT NULL", (past_time, family_id))
            self.cursor.execute("UPDATE families SET upgrade_end_time = ? WHERE id = ? AND upgrade_end_time IS NOT NULL", (past_time, family_id))

    # PvP методи
    def get_family_power(self, family_id):
        with self.connection:
            row = self.cursor.execute("SELECT engine_lvl, hull_lvl, mine_lvl FROM families WHERE id = ?", (family_id,)).fetchone()
            if row: return row[0] + row[1] + int(row[2] / 2)
            return 0

    def get_random_enemy(self, my_family_id):
        with self.connection:
            return self.cursor.execute("""
                SELECT id, name, balance, hull_lvl, current_planet 
                FROM families 
                WHERE id != ? 
                  AND current_planet NOT IN ('Earth', 'Moon')
                  AND (shield_until IS NULL OR shield_until <= CURRENT_TIMESTAMP)
                ORDER BY RANDOM() LIMIT 1
            """, (my_family_id,)).fetchone()

    def get_all_families_for_events(self):
        with self.connection:
            return self.cursor.execute("SELECT id, current_planet, hull_lvl, engine_lvl, balance FROM families").fetchall()

    def set_raid_cooldown(self, fid, mins):
        t = datetime.datetime.now() + datetime.timedelta(minutes=mins)
        with self.connection: self.cursor.execute("UPDATE families SET last_raid_time = ? WHERE id = ?", (t, fid))

    def get_last_raid(self, fid):
        with self.connection:
            r = self.cursor.execute("SELECT last_raid_time FROM families WHERE id = ?", (fid,)).fetchone()
            return r[0] if r else None

    def set_shield(self, fid, mins):
        t = datetime.datetime.now() + datetime.timedelta(minutes=mins)
        with self.connection: self.cursor.execute("UPDATE families SET shield_until = ? WHERE id = ?", (t, fid))
    def get_family_unlocked_modules(self, family_id):
        """Повертає список ID всіх розблокованих модулів для JS-інтерфейсу"""
        with self.connection:
            res = self.cursor.execute(
                "SELECT module_id FROM family_upgrades WHERE family_id = ?", 
                (family_id,)
            ).fetchall()
            return [row[0] for row in res]

    def buy_module_upgrade(self, family_id, module_data):
        """
        module_data: словник з даними модуля (id, cost, req)
        Логіка: Перевірка грошей -> Ресурсів -> Попереднього модуля -> Запис в БД
        """
        m_id = module_data['id']
        req_id = module_data.get('req')
        costs = module_data.get('cost', {'iron': 0, 'fuel': 0, 'coins': 0})

        with self.connection:
            # 1. Перевірка, чи не куплено вже
            already = self.cursor.execute(
                "SELECT id FROM family_upgrades WHERE family_id = ? AND module_id = ?",
                (family_id, m_id)
            ).fetchone()
            if already: return False, "Вже досліджено"

            # 2. Перевірка вимоги (якщо є req)
            if req_id:
                has_req = self.cursor.execute(
                    "SELECT id FROM family_upgrades WHERE family_id = ? AND module_id = ?",
                    (family_id, req_id)
                ).fetchone()
                if not has_req: return False, "Не виконано умови (потрібен попередній модуль)"

            # 3. Перевірка грошей та ресурсів
            # Отримуємо поточний баланс та ресурси
            current = self.get_family_resources(family_id)
            # current[0] - balance, [1] - iron, [2] - fuel
            if current[0] < costs['coins']: return False, "Недостатньо монет"
            if current[1] < costs['iron']: return False, "Недостатньо заліза"
            if current[2] < costs['fuel']: return False, "Недостатньо палива"

            # 4. Знімаємо оплату (Гроші в families, ресурси в res.storage)
            self.cursor.execute("UPDATE families SET balance = balance - ? WHERE id = ?", (costs['coins'], family_id))
            self.cursor.execute("""
                UPDATE res.storage 
                SET res_iron = res_iron - ?, res_fuel = res_fuel - ? 
                WHERE family_id = ?
            """, (costs['iron'], costs['fuel'], family_id))

            # 5. Записуємо розблокування
            self.cursor.execute(
                "INSERT INTO family_upgrades (family_id, module_id) VALUES (?, ?)",
                (family_id, m_id)
            )
            
            # 6. (Опціонально) Оновлюємо загальний рівень в таблиці families для PvP
            if 'engine' in m_id:
                self.cursor.execute("UPDATE families SET engine_lvl = engine_lvl + 1 WHERE id = ?", (family_id,))
            elif 'hull' in m_id:
                self.cursor.execute("UPDATE families SET hull_lvl = hull_lvl + 1 WHERE id = ?", (family_id,))

            return True, "Успішно досліджено!"

    def get_full_inventory(self, family_id):
        """Отримує баланс, ресурси та список куплених модулів одним викликом"""
        try:
            with self.connection:
                # 1. Отримуємо ресурси та баланс (використовуємо реальні назви колонок: res_iron, res_fuel тощо)
                res = self.cursor.execute("""
                    SELECT 
                        f.balance, r.res_iron, r.res_fuel, r.res_regolith, 
                        r.res_he3, r.res_silicon, r.res_oxide, r.res_hydrogen, r.res_helium
                    FROM families f
                    LEFT JOIN res.storage r ON f.id = r.family_id
                    WHERE f.id = ?
                """, (family_id,)).fetchone()

                # 2. Отримуємо розблоковані модулі
                upgrades = self.cursor.execute(
                    "SELECT module_id FROM family_upgrades WHERE family_id = ?", 
                    (family_id,)
                ).fetchall()
                
                owned_ids = [row[0] for row in upgrades]

                if not res:
                    return None

                return {
                    "resources": {
                        "coins": res[0],
                        "iron": res[1],
                        "fuel": res[2],
                        "regolith": res[3],
                        "he3": res[4],
                        "silicon": res[5],
                        "oxide": res[6],
                        "hydrogen": res[7],
                        "helium": res[8]
                    },
                    "owned_modules": owned_ids
                }
        except Exception as e:
            print(f"DB Inventory Error: {e}")
            return None