import logging
from datetime import datetime, timedelta

import psycopg2
from studyhelperbot.handlers import error_info
from studyhelperbot.config import config


class AnalizaDB:
    def __init__(self):
        self.conn = None
        self.is_connected = False

    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            params = config("postgresql")
            logging.debug("db.py:Connecting to the PostgreSQL database...")
            self.conn = psycopg2.connect(**params)

            # Display PostgreSQL version
            cur = self.conn.cursor()
            cur.execute('SELECT version()')
            logging.debug(f"db.py:PostgreSQL database version: {cur.fetchone()}")
            cur.close()

        except (Exception, psycopg2.DatabaseError):
            logging.error(error_info())

        if self.conn is not None:
            self.is_connected = True

    def create_new_user_account(self, telegram_id, bot_chat_id):
        """Creates new record in the `users` table"""
        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO users (telegram_id, bot_chat_id) "
                    f"VALUES (%(telegram_id)s, %(bot_chat_id)s);",
                    {
                        "telegram_id": telegram_id,
                        "bot_chat_id": bot_chat_id,
                    })
        self.conn.commit()
        cur.close()
        logging.info(f"db.py:A new user account was created :: "
                     f"telegram_id={telegram_id}; bot_chat_id={bot_chat_id}")

    def delete_user_account(self, bot_chat_id=None, telegram_id=None):
        """Removes user account from the table.
        `bot_chat_id` or 'telegram_id' should be provided"""
        if bot_chat_id is None and telegram_id is None:
            raise Exception("bot_chat_id or telegram_id should be provided.")
        elif telegram_id is not None:
            where, value_id = 'telegram_id', telegram_id
        else:
            where, value_id = 'bot_chat_id', bot_chat_id

        cur = self.conn.cursor()
        cur.execute(f"DELETE FROM users "
                    f"WHERE {where}=%s;", (value_id,))
        self.conn.commit()
        cur.close()
        logging.info(f"db.py:The following user account was deleted :: "
                     f"{where}={value_id}")

    def new_user_verification_record(self, user_id, password, email, expire_minutes=10):
        """Creates as new record in the `user_verification` table"""
        time_sent = datetime.utcnow()
        time_expires = time_sent + timedelta(minutes=expire_minutes)
        cur = self.conn.cursor()
        cur.execute(f"INSERT INTO user_verification "
                    f"(user_id, one_time_password, email, datetime_sent, datetime_expires)"
                    f"VALUES "
                    f"(%(user_id)s, %(password)s, %(email)s, %(time_sent)s, %(time_expires)s);",
                    {
                        "user_id": user_id,
                        "password": password,
                        "email": email,
                        "time_sent": time_sent,
                        "time_expires": time_expires,
                    })
        self.conn.commit()
        cur.close()
        logging.info(f"db.py:A new user verification record created :: "
                     f"user_id={user_id}; password={password}; "
                     f"email={email}; time_sent={time_sent}; "
                     f"time_expires={time_expires}")

    def get_specific_column(self, where, where_value, col_name, table="users"):
        """Retrieves a specific value from a specific row"""
        cur = self.conn.cursor()
        cur.execute(f"SELECT {col_name} "
                    f"FROM   {table} "
                    f"WHERE  {where} = %s;", (where_value,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"db.py:Run the following SQL query :: "
                      f"SELECT {col_name} FROM {table} "
                      f"WHERE {where}={where_value}")
        logging.debug(f"db.py:Result :: {ans}")
        return ans

    def set_specific_column(self, where, where_value,
                            col_name, col_name_value,
                            table="users"):
        """Updates a specific value from a specific row"""
        cur = self.conn.cursor()
        cur.execute(
                    f"UPDATE    {table} "
                    f"SET       {col_name} = %(col_name_value)s "
                    f"WHERE     {where} = %(where_value)s;",
                    {
                        "col_name_value": col_name_value,
                        "where_value": where_value,
                    }
        )
        self.conn.commit()
        cur.close()
        logging.debug(f"db.py:Run the following SQL query :: "
                      f"UPDATE {table} SET {col_name}={col_name_value} WHERE {where}={where_value}")

    def get_expected_answer(self, bot_chat_id):
        """Retrieves `wait_for_answer` and `expected_answer` values
        for a specific `bot_chat_id` conversation."""
        cur = self.conn.cursor()
        cur.execute("SELECT wait_for_answer, expected_answer "
                    "FROM   users "
                    "WHERE  bot_chat_id = %s;", (bot_chat_id,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"db.py:GET expected answer for bot_chat_id={bot_chat_id} :: "
                      f"wait_for_answer={ans[0]}; expected_answer='{ans[1]}'")
        return ans

    def set_expected_answer(self, bot_chat_id,
                            wait_for_answer=False, expected_answer=None):
        """Updates `wait_for_answer` and `expected_answer` values
        for a specific `bot_chat_id` conversation."""
        cur = self.conn.cursor()
        cur.execute(f"UPDATE    users "
                    f"SET       wait_for_answer = %(wait_for_ans)s, "
                    f"          expected_answer = %(exp_ans)s  "
                    f"WHERE     bot_chat_id = %(bot_chat_id)s;",
                    {
                        "wait_for_ans": wait_for_answer,
                        "exp_ans": expected_answer,
                        "bot_chat_id": bot_chat_id,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"db.py:SET expected answer for bot_chat_id={bot_chat_id} :: "
                      f"wait_for_answer={wait_for_answer}; "
                      f"expected_answer='{expected_answer}'")

    def disconnect(self):
        """ Disconnect from the PostgreSQL database server """
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            logging.debug("db.py:Database connection closed.")
            self.is_connected = False
        else:
            # executes when there was no connection
            logging.warning("db.py:Database was asked to be closed, "
                            "but there was no connection.")
            logging.warning(f"db.py:self.is_connected set to False "
                            f"(before it was {self.is_connected}).")
            self.is_connected = False


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = AnalizaDB()
    db.connect()
    # print(db.get_expected_answer(bot_chat_id=98762378))
    # db.set_expected_answer(bot_chat_id=219836423479)
    # print(db.get_specific_column('user_id', 5, 'prz_email'))
    # db.set_specific_column('user_id', 3, 'telegram_id', 1010)
    # print(db.get_specific_column('user_id', 3, 'telegram_id'))
    # db.create_new_user_account(1231122, 54352353)
    # db.delete_user_account(telegram_id=1231122)
    db.disconnect()
