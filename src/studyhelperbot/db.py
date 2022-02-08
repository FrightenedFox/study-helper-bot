import logging

import psycopg2
import sqlalchemy
import pandas as pd

from studyhelperbot import log_exception, config


# TODO: implement typesetting f(x: int, y: real)
class StudyHelperBotDB:
    """ Makes the communication with the database easier."""
    sqlalchemy_engine: sqlalchemy.engine.base.Engine

    def __init__(self):
        self.conn = None
        self.is_connected = False

    def connect(self):
        """Connect to the PostgreSQL database server."""
        try:
            params = config("postgresql")
            logging.info("Connecting to the PostgreSQL database...")
            self.conn = psycopg2.connect(**params)
            self.sqlalchemy_engine = sqlalchemy.create_engine(
                'postgresql+psycopg2://',
                creator=lambda: self.conn)

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
            self.sqlalchemy_engine.dispose()
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

    def insert_new_user_account(self, tg_user_id, tg_chat_id, permission=1):
        """Creates new record in the `users` table."""
        cur = self.conn.cursor()
        query = ("INSERT INTO users (tg_user_id, tg_chat_id, permission) "
                 "VALUES (%(tg_user_id)s, %(tg_chat_id)s, %(permission)s);")
        cur.execute(query, {"tg_user_id": tg_user_id,
                            "tg_chat_id": tg_chat_id,
                            "permission": permission})
        self.conn.commit()
        cur.close()
        logging.debug(f"Add {tg_user_id=}, {tg_chat_id=}, {permission=}")

    def insert_chat_record(self, tg_chat_id, chat_type):
        """Creates new record in the `chats` table."""
        cur = self.conn.cursor()
        query = ("INSERT INTO chats (tg_chat_id, chat_type) "
                 "VALUES ( %(tg_chat_id)s, %(tg_chat_id)s ); ")
        cur.execute(query, {"tg_chat_id": tg_chat_id,
                            "chat_type": chat_type})
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
        cur.execute(query, {"usos_id": usos_id,
                            "first_name": first_name,
                            "last_name": last_name,
                            "verified": verified,
                            "tg_user_id": tg_user_id})
        self.conn.commit()
        cur.close()
        logging.debug(f"Set verified to {verified} to {tg_user_id=} "
                      f"name: {first_name} {last_name}.")

    def get_user_id(self, distinguishable_col, col_value):
        """Get user_id by any distinguishable_col"""
        # TODO: remove if unused
        cur = self.conn.cursor()
        query = (f"SELECT tg_user_id "
                 f"FROM   users "
                 f"WHERE  {distinguishable_col} = %s;")
        cur.execute(query, (col_value,))
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"{distinguishable_col=} - {col_value}")
        return ans

    def get_all_user_courses(self, tg_user_id):
        query = (f"SELECT DISTINCT c.course_id, c.course_name "
                 f"FROM users_groups "
                 f"JOIN unit_groups ug  ON "
                 f"  users_groups.group_id = ug.unit_group_id "
                 f"JOIN usos_units uu   ON ug.usos_unit_id = uu.usos_unit_id "
                 f"JOIN courses c       ON uu.course = c.course_id "
                 f"WHERE users_groups.user_id = %(tg_user_id)s;")
        df = pd.read_sql(query, self.sqlalchemy_engine,
                         params={"tg_user_id": tg_user_id})
        df.columns = ["course_id", "course_name"]
        logging.debug(f"{tg_user_id=}")
        return df

    def get_user_activities_details(self, tg_user_id, start_date=None,
                                    end_date=None, course_id=None):
        course_id_query, end_date_query, start_date_query = "", "", ""
        query_dict = {"tg_user_id": tg_user_id}
        if start_date:
            start_date_query = " AND act.start_time >= %(start_date)s"
            query_dict["start_date"] = start_date
        # else:
        #     start_date_query = " AND act.start_time >= current_timestamp"
        if end_date:
            end_date_query = "AND act.start_time <= %(end_date)s"
            query_dict["end_date"] = end_date
        if course_id:
            course_id_query = "AND crs.course_id = %(course_id)s"
            query_dict["course_id"] = course_id
        query = (f"SELECT act.activity_id, "
                 f"       act.start_time at time zone 'cet', "
                 f"       act.end_time at time zone 'cet', "
                 f"       act.room, "
                 f"       grt.group_type_id, "
                 f"       ung.group_number, "
                 f"       crs.course_name "
                 f"FROM courses crs "
                 f"JOIN usos_units ON "
                 f"  crs.course_id = usos_units.course "
                 f"JOIN unit_groups ung ON "
                 f"  ung.usos_unit_id = usos_units.usos_unit_id "
                 f"JOIN group_types grt ON "
                 f"  ung.group_type = grt.group_type_id "
                 f"JOIN users_groups ON "
                 f"  ung.unit_group_id = users_groups.group_id "
                 f"JOIN activities act ON "
                 f"  act.unit_group = ung.unit_group_id "
                 f"WHERE users_groups.user_id = %(tg_user_id)s "
                 f"  {end_date_query} {course_id_query} {start_date_query} "
                 f"ORDER BY act.start_time;")
        df = pd.read_sql(query, self.sqlalchemy_engine, params=query_dict,
                         parse_dates={"start_date": {"format": "%Y-%m-%d"},
                                      "end_date":   {"format": "%Y-%m-%d"}})
        df.columns = ["activity_id", "start_time", "end_time", "room",
                      "group_type", "group_number", "course_name"]
        logging.debug(f"{tg_user_id=} {course_id=} {end_date}")
        return df

    def get_specific_value(self, where, where_value, col_name, table="users"):
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

    def update_specific_value(self, where, where_value,
                              col_name, col_name_value,
                              table="users"):
        """Updates a specific value from a specific row."""
        cur = self.conn.cursor()
        query = (f"UPDATE    {table} "
                 f"SET       {col_name} = %(col_name_value)s "
                 f"WHERE     {where} = %(where_value)s; ")
        cur.execute(query, {"col_name_value": col_name_value,
                            "where_value": where_value, })
        self.conn.commit()
        cur.close()
        logging.debug(f"{query=}\t{col_name_value=}, {where_value=}")

    def upsert_course(self, course_id, course_name, term_id):
        """Updates or inserts a course."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.courses (course_id, course_name, term_id)"
                 "VALUES (%(course_id)s, %(course_name)s, %(term_id)s)"
                 "ON CONFLICT (course_id) "
                 "DO UPDATE SET course_name = excluded.course_name;")
        cur.execute(query, {"course_id": course_id,
                            "course_name": course_name,
                            "term_id": term_id})
        self.conn.commit()
        cur.close()
        logging.debug(f"{course_name=}, {course_id=}, {term_id=}")

    def upsert_teacher(self, teacher_usos_id, first_name, last_name):
        """Updates or inserts a teacher."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.teachers "
                 "(teacher_usos_id, first_name, last_name) "
                 "VALUES (%(teacher_usos_id)s, %(first_name)s, %(last_name)s)"
                 "ON CONFLICT (teacher_usos_id) "
                 "DO UPDATE SET first_name = excluded.first_name,"
                 "              last_name  = excluded.last_name;")
        cur.execute(query, {"teacher_usos_id": teacher_usos_id,
                            "first_name": first_name,
                            "last_name": last_name})
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
        cur.execute(query, {"usos_unit_id": usos_unit_id,
                            "course": course})
        self.conn.commit()
        cur.close()
        logging.debug(f"{usos_unit_id=}, {course=}")

    def upsert_group_types(self, group_type_id, group_type_name):
        """Updates or inserts a group type."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.group_types (group_type_id, group_type_name) "
                 "VALUES (%(group_type_id)s, %(group_type_name)s)"
                 "ON CONFLICT (group_type_id) "
                 "DO UPDATE SET group_type_name = excluded.group_type_name;")
        cur.execute(query, {"group_type_id": group_type_id,
                            "group_type_name": group_type_name})
        self.conn.commit()
        cur.close()
        logging.debug(f"{group_type_id=}, {group_type_name=}")

    def upsert_unit_group(self,
                          usos_unit_id,
                          group_number,
                          group_type):
        """Updates or inserts a student group."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.unit_groups (usos_unit_id,"
                 " group_number, group_type) VALUES ("
                 "%(usos_unit_id)s, %(group_number)s, %(general_group)s) "
                 "ON CONFLICT (usos_unit_id, group_number) DO "
                 "UPDATE SET group_type = excluded.group_type "
                 "RETURNING unit_group_id;")
        cur.execute(query, {"usos_unit_id": usos_unit_id,
                            "group_number": group_number,
                            "general_group": group_type})
        ans_id = cur.fetchone()[0]
        self.conn.commit()
        cur.close()
        logging.debug(f"{usos_unit_id=}, {group_number=}, {group_type=}.")
        return ans_id

    def upsert_activities(self, start_time, end_time, room, unit_group):
        """Updates or inserts an activity."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.activities "
                 "(start_time, end_time, room, unit_group) VALUES "
                 "(%(start_time)s, %(end_time)s, %(room)s, %(unit_group)s)"
                 "ON CONFLICT (start_time, end_time, unit_group) "
                 "DO UPDATE SET room = excluded.room;")
        cur.execute(query, {"start_time": start_time,
                            "end_time": end_time,
                            "room": room,
                            "unit_group": unit_group})
        self.conn.commit()
        cur.close()
        logging.debug(f"{unit_group=} {start_time=} {end_time=} {room=}")

    def insert_group_teacher(self, unit_group, teacher):
        """Inserts a teacher if he doesn't exist."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.group_teacher (unit_group, teacher) "
                 "VALUES (%(unit_group)s, %(teacher)s)"
                 "ON CONFLICT (unit_group, teacher) DO NOTHING ;")
        cur.execute(query, {"unit_group": unit_group,
                            "teacher": teacher})
        self.conn.commit()
        cur.close()
        logging.debug(f"{unit_group=}, {teacher=}")

    def insert_term(self, usos_term_id, term_name, start_date, end_date):
        """Inserts a term if it doesn't exist."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.terms (usos_term_id, "
                 "term_name, start_date, end_date) "
                 "VALUES (%(usos_term_id)s, %(term_name)s, "
                 "%(start_date)s, %(end_date)s)"
                 "ON CONFLICT (usos_term_id) DO NOTHING ;")
        cur.execute(query, {"usos_term_id": usos_term_id,
                            "term_name": term_name,
                            "start_date": start_date,
                            "end_date": end_date})
        self.conn.commit()
        cur.close()
        logging.debug(f"{usos_term_id=} {term_name=} {start_date=} {end_date=}")

    def insert_room(self, room_id):
        """Inserts a room if it doesn't exist."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.rooms (room_id) "
                 "VALUES (%(room_id)s)"
                 "ON CONFLICT (room_id) DO NOTHING ;")
        cur.execute(query, {"room_id": room_id})
        self.conn.commit()
        cur.close()
        logging.debug(f"{room_id=}")

    def insert_user_group(self, tg_user_id, usos_unit_id, group_number):
        """Insert a user-unit_group connection if it doesn't exist."""
        cur = self.conn.cursor()
        group_id_query = (f"SELECT unit_group_id "
                          f"FROM   public.unit_groups "
                          f"WHERE (usos_unit_id, group_number) = "
                          f"(%(usos_unit_id)s, %(group_number)s);")
        cur.execute(group_id_query, {"usos_unit_id": usos_unit_id,
                                     "group_number": group_number})
        ans = cur.fetchone()
        if ans is None:
            logging.warning(f"Group {usos_unit_id=} {group_number=} "
                            f"is unknown, skipping")
        else:
            unit_group_id = ans[0]
            insert_student_query = ("INSERT INTO public.users_groups "
                                    "(user_id, group_id) "
                                    "VALUES (%(user_id)s, %(group_id)s)"
                                    "ON CONFLICT (user_id, group_id) "
                                    "DO NOTHING ;")
            cur.execute(insert_student_query, {"user_id": tg_user_id,
                                               "group_id": unit_group_id})
            logging.debug(f"{tg_user_id=}, {unit_group_id=}")
        self.conn.commit()
        cur.close()

    def insert_study_programme(self, programme_id, programme_name):
        """Inserts a programme if it doesn't exist."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.study_programmes "
                 "(programme_id, programme_name) "
                 "VALUES (%(programme_id)s, %(programme_name)s)"
                 "ON CONFLICT (programme_id) DO NOTHING ;")
        cur.execute(query, {"programme_id": programme_id,
                            "programme_name": programme_name})
        self.conn.commit()
        cur.close()
        logging.debug(f"{programme_id=}, {programme_name=}")

    def insert_user_programme(self, user_id, programme_id):
        """Insert a user-programme connection if it doesn't exist."""
        cur = self.conn.cursor()
        query = ("INSERT INTO public.user_programme (user_id, programme_id) "
                 "VALUES (%(user_id)s, %(programme_id)s)"
                 "ON CONFLICT (user_id, programme_id) DO NOTHING;")
        cur.execute(query, {"user_id": user_id,
                            "programme_id": programme_id})
        self.conn.commit()
        cur.close()
        logging.debug(f"{user_id=} {programme_id=}")

    def insert_activity_log(self, user_answers: dict):
        """Insert an activity log."""
        # TODO: separate activities and homeworks
        key_list = [
            "activity:lecture_description",
            # "activity:hw_turn_in_method",
            # "activity:hw_short_description",
            # "activity:hw_full_description",
            # "activity:hw_done_by_activity",
            # "activity:hw_due_date",
            # "activity:hw_turn_in_method",
            "activity:attached_files",
            "activity:other_details",
        ]
        cols = ""
        values = ""
        query_dict = {
            "activity": user_answers["activity_id"],
            "topics_discussed": user_answers["activity:topics_discussed"],
        }
        for key, val in user_answers.items():
            if key in key_list and val:
                proper_name = key.split(':')[1]
                cols += f", {proper_name}"
                values += f", %({proper_name})s"
                query_dict.update({proper_name: val})
        cur = self.conn.cursor()
        query = (f"INSERT INTO public.log_activities "
                 f"(activity, topics_discussed {cols}) "
                 f"VALUES (%(activity)s, %(topics_discussed)s {values});")
        cur.execute(query, query_dict)
        self.conn.commit()
        cur.close()
        logging.debug(f"{query_dict}")

    def get_all_unit_groups(self):
        cur = self.conn.cursor()
        query = ("SELECT (unit_group_id, usos_unit_id, group_number) "
                 "FROM unit_groups;")
        cur.execute(query)
        ans = cur.fetchall()
        cur.close()
        logging.debug(f"Get all groups from unit_groups table")
        return [row[0][1:-1].split(",") for row in ans]

    def get_unit_group_term_info(self, usos_unit_id):
        cur = self.conn.cursor()
        query = ("SELECT terms.end_date "
                 "FROM terms, courses, usos_units "
                 "WHERE (usos_unit_id) = %(usos_unit_id)s "
                 "AND usos_units.course = courses.course_id "
                 "AND courses.term_id = terms.usos_term_id;")
        cur.execute(query, {"usos_unit_id": usos_unit_id})
        ans = cur.fetchone()
        cur.close()
        logging.debug(f"{usos_unit_id=}, term end date {ans}")
        return ans[0]


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    db = StudyHelperBotDB()
    db.connect()
    print(type(db.conn))
    db.disconnect()
