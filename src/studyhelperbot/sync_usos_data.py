import json
from datetime import date

from studyhelperbot import usosapi
from studyhelperbot.db import StudyHelperBotDB


def user_activation(
        db: StudyHelperBotDB,
        tg_user_id: str,
        usos_con: usosapi.USOSAPIConnection):
    usos_response = usos_con.current_identity()
    usos_response["usos_id"] = usos_response.pop("id")
    db.verify_user(tg_user_id=tg_user_id, verified=True, **usos_response)


def global_sync(
        db: StudyHelperBotDB,
        tg_user_id: str,
        usos_con: usosapi.USOSAPIConnection):

    groups_participant = usos_con.get(
        service="services/groups/participant",
        fields="course_unit_id|group_number|class_type|class_type_id|"
               "course_id|course_name|term_id|lecturers",
        active_terms=True,
    )
    active_terms = []
    for term in groups_participant["terms"]:
        if date.today() < date.fromisoformat(term["end_date"]):
            active_terms.append(term["id"])

    # get all courses id for this student
    unit_ids = []
    for active_term in active_terms:
        for group in groups_participant["groups"][active_term]:
            # Course
            db.upsert_course(group["course_id"], group["course_name"]["pl"])
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
                # TODO: get other info about lecturers
            # Student groups
            student_group_index = db.upsert_student_group(
                unit_id,
                group["group_number"],
            )
            # Group teachers
            for lecturer_id in lecturers_ids:
                db.upsert_group_teacher(student_group_index, lecturer_id)

            # TODO: class year, group type and general groups info

def activities_sync(
        db: StudyHelperBotDB,
        tg_user_id: str,
        usos_con: usosapi.USOSAPIConnection):
    pass



if __name__ == '__main__':
    db = StudyHelperBotDB()
    db.connect()
    activities_sync(db, None, None)
    db.disconnect()

# groups_participant = usos_con.get(
#     service="services/groups/participant",
#     fields="course_unit_id|group_number|class_type|class_type_id|"
#            "course_id|course_name|term_id|lecturers",
#     active_terms=True,
# )

# timetable_user = usos_con.get(
#     service="services/tt/user",
#     start="2022-01-03",
#     days=5,
#     fields="start_time|end_time|name|course_id|course_name|"
#            "classtype_name|lecturer_ids|group_number|"
#            "classgroup_profile_url|building_name|building_id|"
#            "room_number|room_id|unit_id|classtype_id",
# )

# courses_unit = usos_con.get(
#         service="services/courses/unit",
#         unit_id="113494",
#         fields="id|groups[group_number|class_type|class_type_id|lecturers]"
#     )
