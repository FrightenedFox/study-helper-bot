import json

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
    pass


def activities_sync(
        db: StudyHelperBotDB,
        tg_user_id: str,
        usos_con: usosapi.USOSAPIConnection):
    pass


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
