import sqlite3
import random
import string
import datetime


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # 1. Сім'ї
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS families (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                invite_code TEXT UNIQUE,
                balance INTEGER DEFAULT 0,

                -- Прокачка ракети
                engine_lvl INTEGER DEFAULT 1,
                hull_lvl INTEGER DEFAULT 1,

                -- Прогрес
                current_planet TEXT DEFAULT 'Earth',

                -- РЕСУРСИ
                res_iron INTEGER DEFAULT 0,      -- Земля (Залізо)
                res_fuel INTEGER DEFAULT 0,      -- Земля (Паливо)

                res_regolith INTEGER DEFAULT 0,  -- Місяць (Реголіт)
                res_he3 INTEGER DEFAULT 0,       -- Місяць (Гелій-3)

                res_silicon INTEGER DEFAULT 0,   -- Марс (Кремній)
                res_oxide INTEGER DEFAULT 0,     -- Марс (Оксид)

                res_hydrogen INTEGER DEFAULT 0,  -- Юпітер (Водень)
                res_helium INTEGER DEFAULT 0,    -- Юпітер (Гелій)

                -- Майнінг
                mine_lvl INTEGER DEFAULT 0,
                last_collection DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 2. Користувачі
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                family_id INTEGER DEFAULT NULL,
                role TEXT DEFAULT 'recruit',
                FOREIGN KEY(family_id) REFERENCES families(id)
            )
        """)
        # 3. Місії
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS missions (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT,
                difficulty INTEGER,
                reward INTEGER,
                planet TEXT DEFAULT 'Earth',
                is_boss_mission BOOLEAN DEFAULT 0
            )
        """)
        # 4. Запуски
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
        self.connection.commit()

    # --- КОРИСТУВАЧІ ТА СІМ'Ї ---
    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchall()
            return bool(len(result))

    def add_user(self, user_id, username):
        if not self.user_exists(user_id):
            with self.connection:
                self.cursor.execute("INSERT INTO users (user_id, username) VALUES (?, ?)", (user_id, username))

    def get_user_family(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT family_id FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return result[0] if result else None

    def create_family(self, user_id, family_name):
        invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        with self.connection:
            self.cursor.execute("INSERT INTO families (name, invite_code, balance) VALUES (?, ?, 0)",
                                (family_name, invite_code))
            family_id = self.cursor.lastrowid
            self.cursor.execute("UPDATE users SET family_id = ?, role = 'captain' WHERE user_id = ?",
                                (family_id, user_id))
            return invite_code

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

    # --- ЕКОНОМІКА І РЕСУРСИ (ОНОВЛЕНО) ---
    def get_family_resources(self, family_id):
        with self.connection:
            # Повертає: balance, iron, fuel, regolith, he3, silicon, oxide, hydrogen, helium, mine_lvl, time, planet
            return self.cursor.execute("""
                SELECT balance, 
                       res_iron, res_fuel, 
                       res_regolith, res_he3,
                       res_silicon, res_oxide, 
                       res_hydrogen, res_helium, 
                       mine_lvl, last_collection, current_planet 
                FROM families WHERE id = ?
            """, (family_id,)).fetchone()

    def update_balance(self, family_id, amount):
        with self.connection:
            self.cursor.execute("UPDATE families SET balance = balance + ? WHERE id = ?", (amount, family_id))

    def upgrade_mine(self, family_id, cost):
        with self.connection:
            self.cursor.execute(
                "UPDATE families SET balance = balance - ?, mine_lvl = mine_lvl + 1, last_collection = CURRENT_TIMESTAMP WHERE id = ?",
                (cost, family_id))

    def collect_resources(self, family_id, res1_col, amount1, res2_col, amount2):
        with self.connection:
            query = f"UPDATE families SET {res1_col} = {res1_col} + ?, {res2_col} = {res2_col} + ?, last_collection = CURRENT_TIMESTAMP WHERE id = ?"
            self.cursor.execute(query, (amount1, amount2, family_id))

    def update_upgrade(self, family_id, upgrade_type):
        with self.connection:
            self.cursor.execute(f"UPDATE families SET {upgrade_type} = {upgrade_type} + 1 WHERE id = ?", (family_id,))

    def move_family_to_planet(self, family_id, new_planet):
        with self.connection:
            # При перельоті шахта скидається
            self.cursor.execute("UPDATE families SET current_planet = ?, mine_lvl = 0 WHERE id = ?",
                                (new_planet, family_id))

    # --- МІСІЇ ---
    def add_mission(self, name, description, difficulty, reward, planet, is_boss=False):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO missions (name, description, difficulty, reward, planet, is_boss_mission) VALUES (?, ?, ?, ?, ?, ?)",
                (name, description, difficulty, reward, planet, is_boss)
            )

    def get_missions_by_planet(self, planet_name):
        with self.connection:
            return self.cursor.execute(
                "SELECT id, name, description, reward, is_boss_mission FROM missions WHERE planet = ?",
                (planet_name,)).fetchall()

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