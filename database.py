import sqlite3
import time


class Database:
    def __init__(self):
        database = sqlite3.connect('data.db')
        c = database.cursor()
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            second_name TEXT
        )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            film_name TEXT,
            kinopoisk_link TEXT,
            time_point INTEGER
        )
        ''')

        c.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            film_name TEXT,
            kinopoisk_link TEXT,
            counter INTEGER
        )
        ''')
        database.commit()
        self.database = database

    def add_note(self, message, json_data, kinopoisk_link) -> None:
        c = self.database.cursor()

        # добавляю в таблицу запись о пользователе, если таковой ещё нет
        c.execute("SELECT * FROM users WHERE user_id = ?",
                  (message.from_user.id,))
        row = c.fetchone()
        if not row:
            c.execute("INSERT INTO users \
            (user_id, username, first_name, second_name) VALUES (?, ?, ?, ?)",
                      (message.from_user.id,
                          message.from_user.username,
                          message.from_user.first_name,
                          message.from_user.last_name))

        # добавляю в таблицу статистики запись о фильме, если таковой ещё нет
        # иначе увеличиваю счётчик
        c.execute("SELECT * FROM stats WHERE user_id = ? AND film_name = ?",
                  (message.from_user.id, json_data['nameRu']))
        row = c.fetchone()
        if not row:
            c.execute("INSERT INTO stats \
            (user_id, film_name, kinopoisk_link, counter) VALUES (?, ?, ?, ?)",
                      (message.from_user.id, json_data['nameRu'],
                          kinopoisk_link, 1))
        else:
            c.execute("UPDATE stats\
            SET counter = counter + 1 WHERE user_id = ? AND film_name = ?",
                      (message.from_user.id, json_data['nameRu']))

        # добавляю в таблицу истории запись о фильме, если таковой ещё нет
        # иначе обновляю время
        c.execute("SELECT * FROM history WHERE user_id = ? AND film_name = ?",
                  (message.from_user.id, json_data['nameRu']))
        row = c.fetchone()
        if not row:
            c.execute("INSERT INTO history \
            (user_id, film_name, kinopoisk_link, time_point) \
            VALUES (?, ?, ?, ?)",
                      (message.from_user.id,
                       json_data['nameRu'],
                       kinopoisk_link,
                       time.time()))
        else:
            c.execute("UPDATE history \
            SET time_point = ? WHERE user_id = ? AND film_name = ?",
                      (time.time(), message.from_user.id, json_data['nameRu']))

        self.database.commit()
        c.close()
        return

    def retrieve_history(self, message) -> list:
        c = self.database.cursor()
        c.execute('SELECT * FROM history \
        WHERE user_id = ? ORDER BY time_point DESC',
                  (message.from_user.id,))
        history = c.fetchall()
        c.close()
        return history

    def retrieve_stats(self, message) -> list:
        c = self.database.cursor()
        c.execute('SELECT * FROM stats \
        WHERE user_id = ? ORDER BY counter DESC',
                  (message.from_user.id,))
        stats = c.fetchall()
        c.close()
        return stats
