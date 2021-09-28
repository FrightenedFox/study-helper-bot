import psycopg2
import studyhelperbot.handlers
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

    def disconnect(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            logging.info("Database connection closed.")
            self.is_connected = False
        else:
            logging.warning("Database was asked to be closed, but there was no connection.")
            logging.warning(f"self.is_connected set to False (before it was {self.is_connected}).")
            self.is_connected = False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    db = AnalizaDB()
    db.connect()
    db.disconnect()
