import psycopg2
from studyhelperbot.handlers.errors import error_info
from studyhelperbot.config import config
import logging


class AnalizaDB:
    def __init__(self):
        self.conn = None
        self.is_connected = False

    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            params = config("postgresql")
            logging.info("Connecting to the PostgreSQL database...")
            self.conn = psycopg2.connect(**params)

            # Display PostgreSQL version
            cur = self.conn.cursor()
            cur.execute('SELECT version()')
            logging.info(f"PostgreSQL database version: {cur.fetchone()}")
            cur.close()

        except (Exception, psycopg2.DatabaseError):
            logging.error(error_info())

        if self.conn is not None:
            self.is_connected = True

    def get_expected_answer(self, bot_chat_id):
        """Retrieves `wait_for_answer` and `expected_answer` values
        for a specific `bot_chat_id` conversation."""
        cur = self.conn.cursor()
        cur.execute("SELECT wait_for_answer, expected_answer "
                    "FROM   users "
                    "WHERE  bot_chat_id = %s;", (bot_chat_id,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"GET expected answer for bot_chat_id={bot_chat_id} :: "
                      f"wait_for_answer={ans[0]}; expected_answer='{ans[1]}'")
        return ans

    def set_expected_answer(self, bot_chat_id, wait_for_answer, expected_answer):
        """Updates `wait_for_answer` and `expected_answer` values
        for a specific `bot_chat_id` conversation."""
        cur = self.conn.cursor()
        cur.execute(f"UPDATE users "
                    f"SET   wait_for_answer = %(wait_for_ans)s, "
                    f"      expected_answer = %(exp_ans)s  "
                    f"WHERE bot_chat_id = %(bot_chat_id)s;",
                    {
                        "wait_for_ans": wait_for_answer,
                        "exp_ans": expected_answer,
                        "bot_chat_id": bot_chat_id,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"SET expected answer for bot_chat_id={bot_chat_id} :: "
                      f"wait_for_answer={wait_for_answer}; "
                      f"expected_answer='{expected_answer}'")

    def disconnect(self):
        """ Disconnect from the PostgreSQL database server """
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = AnalizaDB()
    db.connect()
    print(db.get_expected_answer(bot_chat_id=98762378))
    db.disconnect()
