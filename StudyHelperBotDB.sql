create table permissions
(
    permission_id          integer generated always as identity,
    permission_description text,
    talk_with_bot          bool default true  not null,
    list_lectures          bool default false not null,
    list_exams             bool default false not null,
    list_stats             bool default false not null,
    add_lectures           bool default false not null,
    add_exams              bool default false not null,
    accept_lectures        bool default false not null,
    accept_exams           bool default false not null,
    manage_lectures        bool default false not null,
    manage_exams           bool default false not null,
    course_sync            bool default false not null,
    list_users             bool default false not null,
    add_users              bool default false not null,
    remove_users           bool default false not null,
    manage_permissions     bool default false not null,
    list_server_status     bool default false not null,
    list_logs              bool default false not null
);

create unique index permissions_permission_id_uindex
    on permissions (permission_id);

alter table permissions
    add constraint permissions_pk
        primary key (permission_id);


create table chats
(
    tg_chat_id      int                not null,
    chat_type       text               not null,
    wait_for_answer bool default false not null,
    expected_method text,
    other_details   text
);

create unique index chats_tg_chat_id_uindex
    on chats (tg_chat_id);

alter table chats
    add constraint chats_pk
        primary key (tg_chat_id);


create table users
(
    tg_user_id       int                                   not null,
    tg_chat_id       int                                   not null
        constraint users_tg_chat_id_fk
            references chats
            on delete restrict,
    usos_id          int,
    joined_timestamp timestamptz default current_timestamp not null,
    first_name       text,
    last_name        text,
    verified         bool        default false             not null,
    permission       int                                   not null
        constraint users_permission_fk
            references permissions
            on delete restrict
);

create unique index users_tg_chat_id_uindex
    on users (tg_chat_id);

create unique index users_tg_user_id_uindex
    on users (tg_user_id);

create unique index users_usos_id_uindex
    on users (usos_id);

alter table users
    add constraint users_pk
        primary key (tg_user_id);


create table group_types
(
    group_type_id   text not null,
    group_type_name text,
    max_group_size  int
);

create unique index group_types_group_type_id_uindex
    on group_types (group_type_id);

alter table group_types
    add constraint group_types_pk
        primary key (group_type_id);


create table terms
(
    usos_term_id text not null,
    term_name    text,
    start_date   date not null,
    end_date     date not null
);

create unique index terms_usos_term_id_uindex
    on terms (usos_term_id);

alter table terms
    add constraint terms_pk
        primary key (usos_term_id);



create table courses
(
    course_id   text not null,
    course_name text not null,
    term_id     text not null
        constraint courses_term_id_fk
            references terms
            on delete restrict
);

create unique index courses_course_id_uindex
    on courses (course_id);

alter table courses
    add constraint courses_pk
        primary key (course_id);


create table rooms
(
    room_id  text not null,
    capacity int default 0
);

comment on table rooms is 'Info about rooms';

create unique index rooms_room_id_uindex
    on rooms (room_id);

alter table rooms
    add constraint rooms_pk
        primary key (room_id);


create table teachers
(
    teacher_usos_id int  not null,
    first_name      text not null,
    last_name       text not null,
    email           text,
    title           text,
    private_room    text
        constraint teachers_private_room_fk
            references rooms
            on delete restrict
);

create unique index teachers_usos_id_uindex
    on teachers (teacher_usos_id);

alter table teachers
    add constraint teachers_pk
        primary key (teacher_usos_id);


create table study_programmes
(
    programme_id   text not null,
    programme_name text
);

create unique index study_programmes_id_uindex
    on study_programmes (programme_id);

alter table study_programmes
    add constraint study_programmes_pk
        primary key (programme_id);


create table user_programme
(
    user_id      int  not null
        constraint user_fk
            references users (tg_user_id)
            on delete restrict,
    programme_id text not null
        constraint programme_fk
            references study_programmes
            on delete restrict
);

create unique index user_programme_uindex
    on user_programme (user_id, programme_id);


create table usos_units
(
    usos_unit_id int  not null,
    course       text not null
        constraint usos_units_course_fk
            references courses
            on delete restrict
);

create unique index usos_units_usos_unit_id_uindex
    on usos_units (usos_unit_id);

alter table usos_units
    add constraint usos_units_pk
        primary key (usos_unit_id);


create table unit_groups
(
    unit_group_id integer generated always as identity,
    usos_unit_id  int  not null
        constraint unit_groups_course_fk
            references usos_units (usos_unit_id)
            on delete restrict,
    group_number  int  not null,
    group_type    text not null
        constraint unit_groups_group_type_fk
            references group_types
            on delete restrict
);

comment on table unit_groups is 'Groups per each course unit';

create unique index unit_id_group_number_uindex
    on unit_groups (usos_unit_id, group_number);

alter table unit_groups
    add constraint course_groups_pk
        primary key (unit_group_id);


create table group_teacher
(
    unit_group int not null
        constraint group_fk
            references unit_groups
            on delete restrict,
    teacher    int not null
        constraint teacher_fk
            references teachers (teacher_usos_id)
            on delete restrict
);

create unique index group_teacher_uindex
    on group_teacher (unit_group, teacher);


create table activities
(
    activity_id integer generated always as identity,
    start_time  timestamptz not null,
    end_time    timestamptz not null,
    room        text        not null
        constraint activities_room_fk
            references rooms
            on delete restrict,
    unit_group  int         not null
        constraint activities_unit_group_fk
            references unit_groups
            on delete restrict
);

create unique index activities_activity_id_uindex
    on activities (activity_id);

create unique index activities_group_collision_uindex
    on activities (unit_group, start_time, end_time);

alter table activities
    add constraint activities_pk
        primary key (activity_id);


create table log_activities
(
    log_activity_id      integer generated always as identity,
    activity             int                                   not null
        constraint log_activities_activity_fk
            references activities
            on delete restrict,
    topics_discussed     text                                  not null,
    lecture_description  text,
    hw_short_description text,
    hw_full_description  text,
    hw_turn_in_method    text,
    hw_done_by_activity  int
        constraint log_activities_hw_done_by_fk
            references activities
            on delete restrict,
    hw_due_date          date,
    message_url          text,
    attached_files       text,
    other_details        text,
    added_by             int                                   not null
        constraint log_activities_addeb_by_fk
            references users (tg_user_id)
            on delete restrict,
    added_timestamp      timestamptz default current_timestamp not null,
    accepted_by          int
        constraint log_activities_accepted_by_fk
            references users (tg_user_id)
            on delete restrict,
    accepted_timestamp   timestamptz,
    accepted             bool        default false             not null
);

create unique index log_activities_log_activity_id_uindex
    on log_activities (log_activity_id);

alter table log_activities
    add constraint log_activities_pk
        primary key (log_activity_id);

create table log_tests
(
    log_test_id        integer generated always as identity,
    activity           int                                   not null
        constraint log_tests_activity_fk
            references activities
            on delete restrict,
    test_type          text,
    num_questions      int,
    duration_min       int,
    message_url        text,
    attached_files     text,
    other_details      text,
    added_by           int                                   not null
        constraint log_activities_addeb_by_fk
            references users (tg_user_id)
            on delete restrict,
    added_timestamp    timestamptz default current_timestamp not null,
    accepted_by        int
        constraint log_activities_accepted_by_fk
            references users (tg_user_id)
            on delete restrict,
    accepted_timestamp timestamptz,
    accepted           bool        default false             not null
);

create unique index log_tests_log_test_id_uindex
    on log_tests (log_test_id);

alter table log_tests
    add constraint log_tests_pk
        primary key (log_test_id);

create table course_manager
(
    course  text not null
        constraint course_fk
            references courses (course_id)
            on delete restrict,
    manager int  not null
        constraint manager_fk
            references teachers (teacher_usos_id)
            on delete restrict
);

create unique index course_manager_uindex
    on course_manager (course, manager);


create table users_groups
(
    user_id  int not null
        constraint users_fk
            references users (tg_user_id)
            on delete restrict,
    group_id int
        constraint groups_fk
            references unit_groups
            on delete restrict
);

comment on table users_groups is 'N groups - N users';

create unique index user_group_uindex
    on users_groups (user_id, group_id);


create table activities_per_test
(
    test_id     int not null
        constraint test_fk
            references log_tests
            on delete restrict,
    activity_id int not null
        constraint activities_fk
            references log_activities
            on delete restrict
);

create unique index activities_test_uindex
    on activities_per_test (test_id, activity_id);

INSERT INTO public.permissions (permission_description)
VALUES ('New user'::text);

INSERT INTO public.permissions (permission_description, talk_with_bot, list_lectures, list_exams,
                                list_stats, add_lectures, add_exams, accept_lectures, accept_exams, manage_lectures,
                                manage_exams, course_sync, list_users, add_users, remove_users, manage_permissions,
                                list_server_status, list_logs)
VALUES ('Main admin'::text, true::boolean, true::boolean, true::boolean, true::boolean, true::boolean,
        true::boolean, true::boolean, true::boolean, true::boolean, true::boolean, true::boolean, true::boolean,
        true::boolean, true::boolean, true::boolean, true::boolean, true::boolean);

SELECT terms.end_date
FROM terms,
     courses,
     usos_units
WHERE usos_unit_id = 113493
  AND usos_units.course = courses.course_id
  AND courses.term_id = terms.usos_term_id;


SELECT DISTINCT courses.course_id, courses.course_name
FROM courses,
     usos_units,
     unit_groups,
     users_groups
WHERE users_groups.user_id = 533847507
  AND unit_groups.unit_group_id = users_groups.group_id
  AND usos_units.usos_unit_id = unit_groups.usos_unit_id
  AND courses.course_id = usos_units.course;

SELECT activities.activity_id,
       activities.start_time at time zone 'cet',
       activities.end_time at time zone 'cet',
       activities.room,
       group_types.group_type_name,
       unit_groups.group_number,
       courses.course_name
FROM courses,
     usos_units,
     users_groups,
     unit_groups,
     activities,
     group_types
WHERE users_groups.user_id = 533847507
  AND courses.course_id = usos_units.course
  AND unit_groups.usos_unit_id = usos_units.usos_unit_id
  AND unit_groups.group_type = group_types.group_type_id
  AND users_groups.group_id = unit_groups.unit_group_id
  AND activities.unit_group = unit_groups.unit_group_id
  AND activities.start_time <= '2022-01-05'::date
ORDER BY activities.start_time;

select DISTINCT results.first_name, results.last_name
from (SELECT * from users inner join users_groups ug on users.tg_user_id = ug.user_id ) as "results"
where results.group_id = 4;
