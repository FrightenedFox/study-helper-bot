import logging
from datetime import datetime, timedelta

import psycopg2

from studyhelperbot import log_exception, config


class StudyHelperBotDB:
    # TODO: maybe move all sql strings to a separate file?
    def __init__(self):
        self.conn = None
        self.is_connected = False

    def connect(self):
        """Connect to the PostgreSQL database server."""
        try:
            params = config("postgresql")
            logging.info("Connecting to the PostgreSQL database...")
            self.conn = psycopg2.connect(**params)

            # Display PostgreSQL version
            cur = self.conn.cursor()
            cur.execute('SELECT version()')
            logging.info(f"PostgreSQL version:\t{cur.fetchone()}")
            cur.close()

        except (Exception, psycopg2.DatabaseError):
            log_exception()

        if self.conn is not None:
            self.is_connected = True

    def disconnect(self):
        """Disconnect from the PostgreSQL database server."""
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            logging.info("Database connection closed.")
            self.is_connected = False
        else:
            # executes when there was no connection
            logging.warning("Database was asked to be closed, but there was no connection.")
            logging.warning(f"self.is_connected set to False (before it was {self.is_connected}).")
            self.is_connected = False

    def row_exists(self, key_value, key_column="tg_user_id", table="users"):
        """Checks whether there is a record with
        the same `key_value` in the specified `table`."""
        cur = self.conn.cursor()
        query = (f"SELECT {key_column} "
                 f"FROM   {table} "
                 f"WHERE  {key_column} = %s;")
        cur.execute(query, (key_value,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"Check if exists {key_column}::{key_value} in {table}.")
        if ans is None:
            return False
        else:
            return True

    def user_is_banned(self, tg_user_id):
        cur = self.conn.cursor()
        query = ("SELECT permissions.talk_with_bot "
                 "FROM   users, permissions "
                 "WHERE  users.tg_user_id = %s;")
        cur.execute(query, (tg_user_id,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"Check tg_user_id::{tg_user_id}.")
        if ans is None:
            return False
        else:
            return not ans[0]
        pass

    def create_new_user_account(self, tg_user_id, tg_chat_id, permission=1):
        """Creates new record in the `users` table."""
        cur = self.conn.cursor()
        query = ("INSERT INTO users (tg_user_id, tg_chat_id, permission) "
                 "VALUES (%(tg_user_id)s, %(tg_chat_id)s, %(permission)s);")
        cur.execute(query,
                    {
                        "tg_user_id":   tg_user_id,
                        "tg_chat_id":   tg_chat_id,
                        "permission":   permission,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"Add tg_user_id={tg_user_id}, tg_chat_id={tg_chat_id}, perm={permission}")

    def create_chat_record(self, tg_chat_id, chat_type):
        """Creates new record in the `chats` table."""
        cur = self.conn.cursor()
        query = ("INSERT INTO chats (tg_chat_id, chat_type) "
                 "VALUES (%(tg_chat_id)s, %(tg_chat_id)s);")
        cur.execute(query,
                    {
                        "tg_chat_id":   tg_chat_id,
                        "chat_type":    chat_type,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"Add tg_chat_id={tg_chat_id}, chat_type={chat_type}")

    def set_expected_method(self, tg_chat_id,
                            wait_for_answer=False,
                            expected_method=None,
                            other_details=None):
        """Updates `wait_for_answer` and `expected_answer` values
        for a specific `tg_chat_id` conversation."""
        cur = self.conn.cursor()
        query = ("UPDATE    chats "
                 "SET       wait_for_answer = %(wait_for_answer)s, "
                 "          expected_method = %(expected_method)s,"
                 "          other_details = %(other_details)s "
                 "WHERE     tg_chat_id = %(tg_chat_id)s;")
        cur.execute(query,
                    {
                        "wait_for_answer":  wait_for_answer,
                        "expected_method":  expected_method,
                        "other_details":    other_details,
                        "tg_chat_id":       tg_chat_id,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"tg_chat_id={tg_chat_id} wait_for_answer={wait_for_answer} "
                      f"expected_answer='{expected_method}'")

    def get_expected_method(self, tg_chat_id):
        """Retrieves `wait_for_answer` and `expected_answer` values
        for a specific `tg_chat_id` conversation."""
        cur = self.conn.cursor()
        query = ("SELECT wait_for_answer, expected_method, other_details "
                 "FROM   chats "
                 "WHERE  tg_chat_id = %s;")
        cur.execute(query, (tg_chat_id,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"tg_chat_id={tg_chat_id} wait_for_answer={ans[0]} "
                      f"expected_answer='{ans[1]}'")
        return ans

    def get_user_id(self, distinguishable_col, col_value):
        """Get user_id by any distinguishable_col"""
        cur = self.conn.cursor()
        query = (f"SELECT tg_user_id "
                 f"FROM   users "
                 f"WHERE  {distinguishable_col} = %s;")
        cur.execute(query, (col_value,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"distinguishable_col={col_value}")
        return ans

    def get_specific_column(self, where, where_value, col_name, table="users"):
        """Retrieves a specific value from a specific row."""
        cur = self.conn.cursor()
        query = (f"SELECT {col_name} "
                 f"FROM   {table} "
                 f"WHERE  {where} = %s;")
        cur.execute(query, (where_value,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"{query}\t{where_value}")
        return ans

    def set_specific_column(self, where, where_value,
                            col_name, col_name_value,
                            table="users"):
        """Updates a specific value from a specific row."""
        cur = self.conn.cursor()
        query = (f"UPDATE    {table} "
                 f"SET       {col_name} = %(col_name_value)s, "
                 f"WHERE     where = %(where_value)s;")
        cur.execute(query,{"col_name_value": col_name_value,"where_value": where_value, })
        self.conn.commit()
        cur.close()
        logging.debug(f"{query}\tcnv {col_name_value}\twv {where_value}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = StudyHelperBotDB()
    db.connect()
    db.disconnect()
