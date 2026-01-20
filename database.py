import sqlite3
import random
import string


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.create_tables()

    def create_tables(self):
        # 1. Таблиця сімей
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS families
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                name
                                TEXT
                                NOT
                                NULL,
                                invite_code
                                TEXT
                                UNIQUE,
                                balance
                                INTEGER
                                DEFAULT
                                0
                            )
                            """)
        # 2. Таблиця користувачів
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users
                            (
                                user_id
                                INTEGER
                                PRIMARY
                                KEY,
                                username
                                TEXT,
                                family_id
                                INTEGER
                                DEFAULT
                                NULL,
                                role
                                TEXT
                                DEFAULT
                                'recruit',
                                FOREIGN
                                KEY
                            (
                                family_id
                            ) REFERENCES families
                            (
                                id
                            )
                                )
                            """)
        # 3. Таблиця місій
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS missions
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY,
                                name
                                TEXT
                                NOT
                                NULL,
                                description
                                TEXT,
                                difficulty
                                INTEGER,
                                reward
                                INTEGER,
                                requirements
                                TEXT
                            )
                            """)
        # 4. Таблиця запусків (історія)
        self.cursor.execute("""
                            CREATE TABLE IF NOT EXISTS launches
                            (
                                id
                                INTEGER
                                PRIMARY
                                KEY
                                AUTOINCREMENT,
                                family_id
                                INTEGER,
                                mission_id
                                INTEGER,
                                status
                                TEXT
                                DEFAULT
                                'pending',
                                signatures
                                TEXT
                                DEFAULT
                                '',
                                start_time
                                DATETIME
                                DEFAULT
                                CURRENT_TIMESTAMP,
                                FOREIGN
                                KEY
                            (
                                family_id
                            ) REFERENCES families
                            (
                                id
                            ),
                                FOREIGN KEY
                            (
                                mission_id
                            ) REFERENCES missions
                            (
                                id
                            )
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
            self.cursor.execute("INSERT INTO families (name, invite_code) VALUES (?, ?)", (family_name, invite_code))
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
            return self.cursor.execute("SELECT name, invite_code, balance FROM families WHERE id = ?",
                                       (family_id,)).fetchone()

    def get_family_members(self, family_id):
        with self.connection:
            return self.cursor.execute("SELECT username, role FROM users WHERE family_id = ?", (family_id,)).fetchall()

    def leave_family(self, user_id):
        with self.connection:
            self.cursor.execute("UPDATE users SET family_id = NULL, role = 'recruit' WHERE user_id = ?", (user_id,))

    # --- МІСІЇ ТА ЗАПУСКИ ---
    def add_mission(self, name, description, difficulty, reward):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO missions (name, description, difficulty, reward) VALUES (?, ?, ?, ?)",
                (name, description, difficulty, reward)
            )

    def get_all_missions(self):
        with self.connection:
            return self.cursor.execute("SELECT id, name, description, reward FROM missions").fetchall()

    def start_launch(self, family_id, mission_id):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO launches (family_id, mission_id) VALUES (?, ?)",
                (family_id, mission_id)
            )
            return self.cursor.lastrowid

    def sign_launch(self, launch_id, user_id):
        with self.connection:
            row = self.cursor.execute("SELECT signatures FROM launches WHERE id = ?", (launch_id,)).fetchone()
            if not row: return False

            sigs = row[0].split(',') if row[0] else []
            if str(user_id) in sigs:
                return False

            sigs.append(str(user_id))
            new_sigs = ",".join(filter(None, sigs))

            self.cursor.execute("UPDATE launches SET signatures = ? WHERE id = ?", (new_sigs, launch_id))
            return len(sigs)