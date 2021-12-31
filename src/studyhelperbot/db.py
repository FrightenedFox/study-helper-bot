import logging

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
        logging.debug(f"Check if exists {key_column=} {key_value=} in {table}"
                      f"Response {True if ans is not None else False}.")
        if ans is None:
            return False
        else:
            return True

    def user_can(self, tg_user_id, permission):
        cur = self.conn.cursor()
        query = (f"SELECT permissions.{permission} "
                 f"FROM   users, permissions "
                 f"WHERE  users.tg_user_id = %s "
                 f"AND    users.permission = permissions.permission_id;")
        cur.execute(query, (tg_user_id,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"Check permission {tg_user_id=} {permission=}. "
                      f"Response: {ans}.")
        if ans is None:
            return False
        else:
            return ans[0]
        pass

    def user_is_banned(self, tg_user_id):
        cur = self.conn.cursor()
        query = ("SELECT permissions.talk_with_bot "
                 "FROM   users, permissions "
                 "WHERE  users.tg_user_id = %s;")
        cur.execute(query, (tg_user_id,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"Check {tg_user_id=}. Response: {ans}.")
        if ans is None:
            return False
        else:
            return not ans[0]
        pass

    def user_is_verified(self, tg_user_id):
        cur = self.conn.cursor()
        query = ("SELECT users.verified "
                 "FROM   users "
                 "WHERE  users.tg_user_id = %s;")
        cur.execute(query, (tg_user_id,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"Check {tg_user_id=}. Response: {ans}.")
        if ans is None:
            return False
        else:
            return ans[0]
        pass

    def create_new_user_account(self, tg_user_id, tg_chat_id, permission=1):
        """Creates new record in the `users` table."""
        cur = self.conn.cursor()
        query = ("INSERT INTO users (tg_user_id, tg_chat_id, permission) "
                 "VALUES (%(tg_user_id)s, %(tg_chat_id)s, %(permission)s);")
        cur.execute(query,
                    {
                        "tg_user_id": tg_user_id,
                        "tg_chat_id": tg_chat_id,
                        "permission": permission,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"Add {tg_user_id=}, {tg_chat_id=}, {permission=}")

    def create_chat_record(self, tg_chat_id, chat_type):
        """Creates new record in the `chats` table."""
        cur = self.conn.cursor()
        query = ("INSERT INTO chats (tg_chat_id, chat_type) "
                 "VALUES ( %(tg_chat_id)s, %(tg_chat_id)s ); ")
        cur.execute(query,
                    {
                        "tg_chat_id": tg_chat_id,
                        "chat_type": chat_type,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"Add {tg_chat_id=}, {chat_type=}")

    def verify_user(self, tg_user_id,
                    usos_id, first_name,
                    last_name, verified=True):
        cur = self.conn.cursor()
        query = ("UPDATE    users "
                 "SET       usos_id = %(usos_id)s, "
                 "          first_name = %(first_name)s, "
                 "          last_name = %(last_name)s,"
                 "          verified = %(verified)s "
                 "WHERE     tg_user_id = %(tg_user_id)s;")
        cur.execute(query,
                    {
                        "usos_id": usos_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "verified": verified,
                        "tg_user_id": tg_user_id,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"Set verified to {verified} to {tg_user_id=}"
                      f"name: {first_name} {last_name}.")

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
                        "wait_for_answer": wait_for_answer,
                        "expected_method": expected_method,
                        "other_details": other_details,
                        "tg_chat_id": tg_chat_id,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"{tg_chat_id=} {wait_for_answer=} {expected_method=}")

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
        logging.debug(f"{tg_chat_id=} wait_for_answer={ans[0]} "
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
        logging.debug(f"{distinguishable_col=} - {col_value}")
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
        logging.debug(f"{query=}\t{where_value=}")
        return ans

    def set_specific_column(self, where, where_value,
                            col_name, col_name_value,
                            table="users"):
        """Updates a specific value from a specific row."""
        cur = self.conn.cursor()
        query = (f"UPDATE    {table} "
                 f"SET       {col_name} = %(col_name_value)s "
                 f"WHERE     {where} = %(where_value)s; ")
        cur.execute(query, {"col_name_value": col_name_value, "where_value": where_value, })
        self.conn.commit()
        cur.close()
        logging.debug(f"{query=}\t{col_name_value=}, {where_value=}")

    def upsert_course(self, course_id, course_name):
        """Updates or inserts a course."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.courses (course_id, course_name)"
                 "VALUES (%(course_id)s, %(course_name)s)"
                 "ON CONFLICT (course_id) "
                 "DO UPDATE SET course_name = excluded.course_name;")
        cur.execute(query,
                    {
                        "course_id": course_id,
                        "course_name": course_name,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"{course_name=}, {course_id=}")

    def upsert_teacher(self, teacher_usos_id, first_name, last_name):
        """Updates or inserts a teacher."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.teachers (teacher_usos_id, first_name, last_name) "
                 "VALUES (%(teacher_usos_id)s, %(first_name)s, %(last_name)s)"
                 "ON CONFLICT (teacher_usos_id) "
                 "DO UPDATE SET first_name = excluded.first_name,"
                 "              last_name  = excluded.last_name;")
        cur.execute(query,
                    {
                        "teacher_usos_id": teacher_usos_id,
                        "first_name": first_name,
                        "last_name": last_name,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"{teacher_usos_id=}, {first_name=}, {last_name=}")

    def upsert_usos_units(self, usos_unit_id, course):
        """Updates or inserts an usos unit."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.usos_units (usos_unit_id, course) "
                 "VALUES (%(usos_unit_id)s, %(course)s)"
                 "ON CONFLICT (usos_unit_id) "
                 "DO UPDATE SET course = excluded.course;")
        cur.execute(query,
                    {
                        "usos_unit_id": usos_unit_id,
                        "course": course,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"{usos_unit_id=}, {course=}")

    def upsert_student_group(self,
                             usos_unit_id,
                             group_number,
                             general_group=None):
        """Updates or inserts a student group."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.student_groups (usos_unit_id,"
                 " group_number, general_group) VALUES ("
                 "%(usos_unit_id)s, %(group_number)s, %(general_group)s) "
                 "ON CONFLICT (usos_unit_id, group_number) DO "
                 "UPDATE SET general_group = excluded.general_group "
                 "RETURNING student_group_id;")
        cur.execute(query,
                    {
                        "usos_unit_id": usos_unit_id,
                        "group_number": group_number,
                        "general_group": general_group,
                    })
        ans_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        logging.debug(f"{usos_unit_id=}, {group_number=}, {general_group=}.")
        return ans_id

    def upsert_group_teacher(self, student_group, teacher):
        """Updates or inserts an usos unit."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.group_teacher (student_group, teacher) "
                 "VALUES (%(student_group)s, %(teacher)s)"
                 "ON CONFLICT (student_group, teacher) DO NOTHING ;")
        cur.execute(query,
                    {
                        "student_group": student_group,
                        "teacher": teacher,
                    })
        self.conn.commit()
        cur.close()
        logging.debug(f"{student_group=}, {teacher=}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = StudyHelperBotDB()
    db.connect()
    db.disconnect()
