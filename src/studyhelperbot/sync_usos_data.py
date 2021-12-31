import asyncio
import datetime as dt

import pytz

from studyhelperbot import usosapi
from studyhelperbot.db import StudyHelperBotDB

pl_tz = pytz.timezone("Europe/Warsaw")


async def user_verification(
        db: StudyHelperBotDB,
        tg_user_id: str,
        usos_con: usosapi.USOSAPIConnection):
    """Verifies the user, gets his name and usos id."""
    usos_response = usos_con.current_identity()
    usos_response["usos_id"] = usos_response.pop("id")
    db.verify_user(tg_user_id=tg_user_id, verified=True, **usos_response)
    student_programmes = usos_con.get(
        service="services/progs/student",
        user_id=usos_response["usos_id"],
    )
    for programme in student_programmes:
        db.insert_study_programme(
            programme_id=programme["programme"]["id"],
            programme_name=programme["programme"]["description"]["pl"],
        )
        db.insert_user_programme(
            user_id=tg_user_id,
            programme_id=programme["programme"]["id"],
        )


def get_active_terms(groups_participant):
    active_terms = []
    for term in groups_participant["terms"]:
        if dt.date.today() < dt.date.fromisoformat(term["end_date"]):
            active_terms.append(term["id"])
    return active_terms


async def course_sync(
        db: StudyHelperBotDB,
        tg_user_id: str,
        usos_con: usosapi.USOSAPIConnection):
    """Get all groups related to the courses
    current user participates in."""
    groups_participant = usos_con.get(
        service="services/groups/participant",
        fields="course_unit_id|group_number|class_type|class_type_id|"
               "course_id|course_name|term_id|lecturers",
        active_terms=True,
    )
    # get all courses id for this student
    unit_ids = []
    for active_term in get_active_terms(groups_participant):
        for group in groups_participant["groups"][active_term]:
            # Term
            if not db.row_exists(key_value=active_term,
                                 key_column="usos_term_id",
                                 table="terms"):
                active_term_info = usos_con.get(
                    service="services/terms/term",
                    term_id=active_term,
                    fields="name|start_date|end_date"
                )
                db.insert_term(active_term,
                               active_term_info["name"]["pl"],
                               active_term_info["start_date"],
                               active_term_info["end_date"])
            # Course
            db.upsert_course(group["course_id"],
                             group["course_name"]["pl"],
                             active_term)
            # USOS unit id
            db.upsert_usos_units(group["course_unit_id"], group["course_id"])
            unit_ids.append(group["course_unit_id"])

    # get all groups for this course id
    for unit_id in unit_ids:
        courses_unit_response = usos_con.get(
            service="services/courses/unit",
            unit_id=unit_id,
            fields="id|groups[group_number|class_type|class_type_id|lecturers]"
        )
        for group in courses_unit_response["groups"]:
            # Lecturers
            lecturers_ids = []
            for lecturer in group["lecturers"]:
                lecturers_ids.append(lecturer["id"])
                db.upsert_teacher(lecturer["id"],
                                  lecturer["first_name"],
                                  lecturer["last_name"])
            # Group type
            db.upsert_group_types(group_type_id=group["class_type_id"],
                                  group_type_name=group["class_type"]["pl"])
            # Unit groups
            unit_group_index = db.upsert_unit_group(unit_id,
                                                    group["group_number"],
                                                    group["class_type_id"])
            # Group teachers
            for lecturer_id in lecturers_ids:
                db.insert_group_teacher(unit_group_index, lecturer_id)


async def personal_groups_sync(
        db: StudyHelperBotDB,
        tg_user_id: str,
        usos_con: usosapi.USOSAPIConnection):
    """Add student to his groups in the unit_groups table."""
    groups_participant = usos_con.get(
        service="services/groups/participant",
        fields="course_unit_id|group_number|term_id",
        active_terms=True,
    )
    for active_term in get_active_terms(groups_participant):
        for group in groups_participant["groups"][active_term]:
            db.insert_user_group(tg_user_id,
                                 group["course_unit_id"],
                                 group["group_number"])


async def activities_sync(
        db: StudyHelperBotDB,
        tg_user_id: str,
        usos_con: usosapi.USOSAPIConnection):
    groups = db.get_all_unit_groups()
    for group in groups:
        d_group = dict(zip(["id", "usos_unit_id", "group_number"], group))
        term_end_date = db.get_unit_group_term_info(d_group["usos_unit_id"])
        current_date = dt.date.today()
        while current_date < term_end_date:
            timetable_group = usos_con.get(
                service="services/tt/classgroup",
                unit_id=d_group["usos_unit_id"],
                group_number=d_group["group_number"],
                start=current_date.isoformat(),
                days=7,
                fields="start_time|end_time|room_number",
            )
            for activity in timetable_group:
                start_time_naive = dt.datetime.fromisoformat(activity["start_time"])
                end_time_naive = dt.datetime.fromisoformat(activity["end_time"])
                start_time_pl_tz = pl_tz.localize(start_time_naive, is_dst=1)
                end_time_pl_tz = pl_tz.localize(end_time_naive, is_dst=1)

                db.insert_room(activity["room_number"])
                db.upsert_activities(
                    start_time=start_time_pl_tz,
                    end_time=end_time_pl_tz,
                    room=activity["room_number"],
                    unit_group=d_group["id"],
                )
            # Jump to the next week
            current_date += dt.timedelta(days=7)
        # Artificially slow down requests, so that USOS doesn't get angry
        await asyncio.sleep(3)
    pass


async def debug_sync(
        db: StudyHelperBotDB,
        tg_user_id: str,
        usos_con: usosapi.USOSAPIConnection):
    response = usos_con.get(
        service="services/progs/student",
        user_id="234394",
    )
    print(response)


if __name__ == '__main__':
    db = StudyHelperBotDB()
    db.connect()
    debug_sync(db, None, None)
    db.disconnect()
