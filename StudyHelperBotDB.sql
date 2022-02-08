create sequence log_homeworks_homework_id_seq1;

create table permissions
(
    permission_id          integer generated always as identity
        constraint permissions_pk
            primary key,
    permission_description text,
    talk_with_bot          boolean default true  not null,
    list_lectures          boolean default false not null,
    list_exams             boolean default false not null,
    list_stats             boolean default false not null,
    add_lectures           boolean default false not null,
    add_exams              boolean default false not null,
    accept_lectures        boolean default false not null,
    accept_exams           boolean default false not null,
    manage_lectures        boolean default false not null,
    manage_exams           boolean default false not null,
    course_sync            boolean default false not null,
    list_users             boolean default false not null,
    add_users              boolean default false not null,
    remove_users           boolean default false not null,
    manage_permissions     boolean default false not null,
    list_server_status     boolean default false not null,
    list_logs              boolean default false not null
);

create unique index permissions_permission_id_uindex
    on permissions (permission_id);

create table chats
(
    tg_chat_id integer not null
        constraint chats_pk
            primary key,
    chat_type  text    not null
);

create unique index chats_tg_chat_id_uindex
    on chats (tg_chat_id);

create table users
(
    tg_user_id       integer                                            not null
        constraint users_pk
            primary key,
    tg_chat_id       integer                                            not null
        constraint users_tg_chat_id_fk
            references chats
            on delete restrict,
    usos_id          integer,
    joined_timestamp timestamp with time zone default CURRENT_TIMESTAMP not null,
    first_name       text,
    last_name        text,
    verified         boolean                  default false             not null,
    permission       integer                                            not null
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

create table group_types
(
    group_type_id   text not null
        constraint group_types_pk
            primary key,
    group_type_name text,
    max_group_size  integer
);

create unique index group_types_group_type_id_uindex
    on group_types (group_type_id);

create table terms
(
    usos_term_id text not null
        constraint terms_pk
            primary key,
    term_name    text,
    start_date   date not null,
    end_date     date not null
);

create unique index terms_usos_term_id_uindex
    on terms (usos_term_id);

create table courses
(
    course_id   text not null
        constraint courses_pk
            primary key,
    course_name text not null,
    term_id     text not null
        constraint courses_term_id_fk
            references terms
            on delete restrict
);

create unique index courses_course_id_uindex
    on courses (course_id);

create table rooms
(
    room_id  text not null
        constraint rooms_pk
            primary key,
    capacity integer default 0
);

comment on table rooms is 'Info about rooms';

create unique index rooms_room_id_uindex
    on rooms (room_id);

create table teachers
(
    teacher_usos_id integer not null
        constraint teachers_pk
            primary key,
    first_name      text    not null,
    last_name       text    not null,
    email           text,
    title           text,
    private_room    text
        constraint teachers_private_room_fk
            references rooms
            on delete restrict
);

create unique index teachers_usos_id_uindex
    on teachers (teacher_usos_id);

create table study_programmes
(
    programme_id   text not null
        constraint study_programmes_pk
            primary key,
    programme_name text
);

create unique index study_programmes_id_uindex
    on study_programmes (programme_id);

create table user_programme
(
    user_id      integer not null
        constraint user_fk
            references users
            on delete restrict,
    programme_id text    not null
        constraint programme_fk
            references study_programmes
            on delete restrict
);

create unique index user_programme_uindex
    on user_programme (user_id, programme_id);

create table usos_units
(
    usos_unit_id integer not null
        constraint usos_units_pk
            primary key,
    course       text    not null
        constraint usos_units_course_fk
            references courses
            on delete restrict
);

create unique index usos_units_usos_unit_id_uindex
    on usos_units (usos_unit_id);

create table unit_groups
(
    unit_group_id integer generated always as identity
        constraint course_groups_pk
            primary key,
    usos_unit_id  integer not null
        constraint unit_groups_course_fk
            references usos_units
            on delete restrict,
    group_number  integer not null,
    group_type    text    not null
        constraint unit_groups_group_type_fk
            references group_types
            on delete restrict
);

comment on table unit_groups is 'Groups per each course unit';

create unique index unit_id_group_number_uindex
    on unit_groups (usos_unit_id, group_number);

create table group_teacher
(
    unit_group integer not null
        constraint group_fk
            references unit_groups
            on delete restrict,
    teacher    integer not null
        constraint teacher_fk
            references teachers
            on delete restrict
);

create unique index group_teacher_uindex
    on group_teacher (unit_group, teacher);

create table activities
(
    activity_id integer generated always as identity
        constraint activities_pk
            primary key,
    start_time  timestamp with time zone not null,
    end_time    timestamp with time zone not null,
    room        text                     not null
        constraint activities_room_fk
            references rooms
            on delete restrict,
    unit_group  integer                  not null
        constraint activities_unit_group_fk
            references unit_groups
            on delete restrict
);

create unique index activities_activity_id_uindex
    on activities (activity_id);

create unique index activities_group_collision_uindex
    on activities (unit_group, start_time, end_time);

create table log_activities
(
    log_activity_id     integer generated always as identity
        constraint log_activities_pk
            primary key,
    activity            integer                                not null
        constraint log_activities_activity_fk
            references activities
            on delete restrict,
    topics_discussed    text                                   not null,
    lecture_description text,
    message_url         text,
    attached_files      text,
    other_details       text,
    accepted            boolean                  default false not null,
    added_by            integer
        constraint log_activities_added_by_fk
            references users
            on delete restrict,
    added_timestamp     timestamp with time zone default CURRENT_TIMESTAMP,
    accepted_by         integer
        constraint log_activities_accepted_by_fk
            references users
            on delete restrict,
    accepted_timestamp  timestamp with time zone
);

create unique index log_activities_log_activity_id_uindex
    on log_activities (log_activity_id);

create table log_tests
(
    log_test_id        integer generated always as identity
        constraint log_tests_pk
            primary key,
    activity           integer
        constraint log_tests_activity_fk
            references activities
            on delete restrict,
    test_type          text,
    num_questions      integer,
    duration_min       integer,
    message_url        text,
    attached_files     text,
    other_details      text,
    accepted           boolean                  default false not null,
    added_by           integer
        constraint log_tests_added_by_fk
            references users
            on delete restrict,
    added_timestamp    timestamp with time zone default CURRENT_TIMESTAMP,
    accepted_by        integer
        constraint log_tests_accepted_by_fk
            references users
            on delete restrict,
    accepted_timestamp timestamp with time zone,
    exam_timestamp     timestamp
);

create unique index log_tests_log_test_id_uindex
    on log_tests (log_test_id);

create table course_manager
(
    course  text    not null
        constraint course_fk
            references courses
            on delete restrict,
    manager integer not null
        constraint manager_fk
            references teachers
            on delete restrict
);

create unique index course_manager_uindex
    on course_manager (course, manager);

create table users_groups
(
    user_id  integer not null
        constraint users_fk
            references users
            on delete restrict,
    group_id integer
        constraint groups_fk
            references unit_groups
            on delete restrict
);

comment on table users_groups is 'N groups - N users';

create unique index user_group_uindex
    on users_groups (user_id, group_id);

create table activities_per_test
(
    test_id     integer not null
        constraint test_fk
            references log_tests
            on delete restrict,
    activity_id integer not null
        constraint activities_fk
            references log_activities
            on delete restrict
);

create unique index activities_test_uindex
    on activities_per_test (test_id, activity_id);

create table log_homeworks
(
    homework_id          integer generated always as identity
        constraint log_homeworks_pk
            primary key,
    hw_short_description text                                               not null,
    hw_full_description  text,
    hw_turn_in_method    text,
    hw_due_date          timestamp with time zone                           not null,
    attached_files       text,
    from_activity        integer
        constraint log_homeworks_from_activity_fk
            references activities
            on delete set null,
    added_timestamp      timestamp with time zone default CURRENT_TIMESTAMP not null,
    accepted             boolean                  default false             not null,
    accepted_by          integer
        constraint log_homeworks_accepted_by_fk
            references users
            on delete set null,
    accepted_timestamp   timestamp with time zone,
    other_details        text,
    added_by             integer                                            not null
        constraint log_homeworks_added_by_fk
            references users
            on delete set null
);

alter sequence log_homeworks_homework_id_seq1 owned by log_homeworks.homework_id;

create unique index log_homeworks_homework_id_uindex
    on log_homeworks (homework_id);


