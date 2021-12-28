import logging
from datetime import datetime, timedelta

import psycopg2

from studyhelperbot import error_info, config


class StudyHelperBotDB:
    # TODO: maybe move all sql strings to a separate file?
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
    db = StudyHelperBotDB()
    db.connect()
    db.disconnect()
