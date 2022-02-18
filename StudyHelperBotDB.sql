CREATE SEQUENCE log_homeworks_homework_id_seq1;

CREATE TABLE permissions
(
    permission_id          integer GENERATED ALWAYS AS IDENTITY
        CONSTRAINT permissions_pk
            PRIMARY KEY,
    permission_description text,
    talk_with_bot          boolean DEFAULT TRUE  NOT NULL,
    list_lectures          boolean DEFAULT FALSE NOT NULL,
    list_exams             boolean DEFAULT FALSE NOT NULL,
    list_stats             boolean DEFAULT FALSE NOT NULL,
    add_lectures           boolean DEFAULT FALSE NOT NULL,
    add_exams              boolean DEFAULT FALSE NOT NULL,
    accept_lectures        boolean DEFAULT FALSE NOT NULL,
    accept_exams           boolean DEFAULT FALSE NOT NULL,
    manage_lectures        boolean DEFAULT FALSE NOT NULL,
    manage_exams           boolean DEFAULT FALSE NOT NULL,
    course_sync            boolean DEFAULT FALSE NOT NULL,
    list_users             boolean DEFAULT FALSE NOT NULL,
    add_users              boolean DEFAULT FALSE NOT NULL,
    remove_users           boolean DEFAULT FALSE NOT NULL,
    manage_permissions     boolean DEFAULT FALSE NOT NULL,
    list_server_status     boolean DEFAULT FALSE NOT NULL,
    list_logs              boolean DEFAULT FALSE NOT NULL
);

CREATE UNIQUE INDEX permissions_permission_id_uindex
    ON permissions (permission_id);

CREATE TABLE chats
(
    tg_chat_id bigint NOT NULL
        CONSTRAINT chats_pk
            PRIMARY KEY,
    chat_type  text   NOT NULL
);

CREATE UNIQUE INDEX chats_tg_chat_id_uindex
    ON chats (tg_chat_id);

CREATE TABLE users
(
    tg_user_id       bigint                                             NOT NULL
        CONSTRAINT users_pk
            PRIMARY KEY,
    tg_chat_id       bigint                                             NOT NULL
        CONSTRAINT users_tg_chat_id_fk
            REFERENCES chats
            ON DELETE RESTRICT,
    usos_id          integer,
    joined_timestamp timestamp WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    first_name       text,
    last_name        text,
    verified         boolean                  DEFAULT FALSE             NOT NULL,
    permission       integer                                            NOT NULL
        CONSTRAINT users_permission_fk
            REFERENCES permissions
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX users_usos_id_uindex
    ON users (usos_id);

CREATE UNIQUE INDEX users_tg_user_id_uindex
    ON users (tg_user_id);

CREATE UNIQUE INDEX users_tg_chat_id_uindex
    ON users (tg_chat_id);

CREATE TABLE group_types
(
    group_type_id   text NOT NULL
        CONSTRAINT group_types_pk
            PRIMARY KEY,
    group_type_name text,
    max_group_size  integer
);

CREATE UNIQUE INDEX group_types_group_type_id_uindex
    ON group_types (group_type_id);

CREATE TABLE terms
(
    usos_term_id text NOT NULL
        CONSTRAINT terms_pk
            PRIMARY KEY,
    term_name    text,
    start_date   date NOT NULL,
    end_date     date NOT NULL
);

CREATE UNIQUE INDEX terms_usos_term_id_uindex
    ON terms (usos_term_id);

CREATE TABLE courses
(
    course_id   text NOT NULL
        CONSTRAINT courses_pk
            PRIMARY KEY,
    course_name text NOT NULL,
    term_id     text NOT NULL
        CONSTRAINT courses_term_id_fk
            REFERENCES terms
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX courses_course_id_uindex
    ON courses (course_id);

CREATE TABLE rooms
(
    room_id  text NOT NULL
        CONSTRAINT rooms_pk
            PRIMARY KEY,
    capacity integer DEFAULT 0
);

COMMENT ON TABLE rooms IS 'Info about rooms';

CREATE UNIQUE INDEX rooms_room_id_uindex
    ON rooms (room_id);

CREATE TABLE teachers
(
    teacher_usos_id integer NOT NULL
        CONSTRAINT teachers_pk
            PRIMARY KEY,
    first_name      text    NOT NULL,
    last_name       text    NOT NULL,
    email           text,
    title           text,
    private_room    text
        CONSTRAINT teachers_private_room_fk
            REFERENCES rooms
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX teachers_usos_id_uindex
    ON teachers (teacher_usos_id);

CREATE TABLE study_programmes
(
    programme_id   text NOT NULL
        CONSTRAINT study_programmes_pk
            PRIMARY KEY,
    programme_name text
);

CREATE UNIQUE INDEX study_programmes_id_uindex
    ON study_programmes (programme_id);

CREATE TABLE user_programme
(
    user_id      bigint NOT NULL
        CONSTRAINT user_fk
            REFERENCES users
            ON DELETE RESTRICT,
    programme_id text   NOT NULL
        CONSTRAINT programme_fk
            REFERENCES study_programmes
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX user_programme_uindex
    ON user_programme (user_id, programme_id);

CREATE TABLE usos_units
(
    usos_unit_id integer NOT NULL
        CONSTRAINT usos_units_pk
            PRIMARY KEY,
    course       text    NOT NULL
        CONSTRAINT usos_units_course_fk
            REFERENCES courses
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX usos_units_usos_unit_id_uindex
    ON usos_units (usos_unit_id);

CREATE TABLE unit_groups
(
    unit_group_id integer GENERATED ALWAYS AS IDENTITY
        CONSTRAINT course_groups_pk
            PRIMARY KEY,
    usos_unit_id  integer NOT NULL
        CONSTRAINT unit_groups_course_fk
            REFERENCES usos_units
            ON DELETE RESTRICT,
    group_number  integer NOT NULL,
    group_type    text    NOT NULL
        CONSTRAINT unit_groups_group_type_fk
            REFERENCES group_types
            ON DELETE RESTRICT
);

COMMENT ON TABLE unit_groups IS 'Groups per each course unit';

CREATE UNIQUE INDEX unit_id_group_number_uindex
    ON unit_groups (usos_unit_id, group_number);

CREATE TABLE group_teacher
(
    unit_group integer NOT NULL
        CONSTRAINT group_fk
            REFERENCES unit_groups
            ON DELETE RESTRICT,
    teacher    integer NOT NULL
        CONSTRAINT teacher_fk
            REFERENCES teachers
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX group_teacher_uindex
    ON group_teacher (unit_group, teacher);

CREATE TABLE activities
(
    activity_id integer GENERATED ALWAYS AS IDENTITY
        CONSTRAINT activities_pk
            PRIMARY KEY,
    start_time  timestamp WITH TIME ZONE NOT NULL,
    end_time    timestamp WITH TIME ZONE NOT NULL,
    room        text                     NOT NULL
        CONSTRAINT activities_room_fk
            REFERENCES rooms
            ON DELETE RESTRICT,
    unit_group  integer                  NOT NULL
        CONSTRAINT activities_unit_group_fk
            REFERENCES unit_groups
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX activities_activity_id_uindex
    ON activities (activity_id);

CREATE UNIQUE INDEX activities_group_collision_uindex
    ON activities (unit_group, start_time, end_time);

CREATE TABLE log_activities
(
    log_activity_id     integer GENERATED ALWAYS AS IDENTITY
        CONSTRAINT log_activities_pk
            PRIMARY KEY,
    activity            integer                                NOT NULL
        CONSTRAINT log_activities_activity_fk
            REFERENCES activities
            ON DELETE RESTRICT,
    topics_discussed    text                                   NOT NULL,
    lecture_description text,
    message_url         text,
    attached_files      text,
    other_details       text,
    accepted            boolean                  DEFAULT FALSE NOT NULL,
    added_by            bigint
        CONSTRAINT log_activities_added_by_fk
            REFERENCES users
            ON DELETE RESTRICT,
    added_timestamp     timestamp WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    accepted_by         bigint
        CONSTRAINT log_activities_accepted_by_fk
            REFERENCES users
            ON DELETE RESTRICT,
    accepted_timestamp  timestamp WITH TIME ZONE
);

CREATE UNIQUE INDEX log_activities_log_activity_id_uindex
    ON log_activities (log_activity_id);

CREATE TABLE log_tests
(
    log_test_id        integer GENERATED ALWAYS AS IDENTITY
        CONSTRAINT log_tests_pk
            PRIMARY KEY,
    activity           integer
        CONSTRAINT log_tests_activity_fk
            REFERENCES activities
            ON DELETE RESTRICT,
    test_type          text,
    num_questions      integer,
    duration_min       integer,
    message_url        text,
    attached_files     text,
    other_details      text,
    accepted           boolean                  DEFAULT FALSE NOT NULL,
    added_by           bigint
        CONSTRAINT log_tests_added_by_fk
            REFERENCES users
            ON DELETE RESTRICT,
    added_timestamp    timestamp WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    accepted_by        bigint
        CONSTRAINT log_tests_accepted_by_fk
            REFERENCES users
            ON DELETE RESTRICT,
    accepted_timestamp timestamp WITH TIME ZONE,
    exam_timestamp     timestamp
);

CREATE UNIQUE INDEX log_tests_log_test_id_uindex
    ON log_tests (log_test_id);

CREATE TABLE course_manager
(
    course  text    NOT NULL
        CONSTRAINT course_fk
            REFERENCES courses
            ON DELETE RESTRICT,
    manager integer NOT NULL
        CONSTRAINT manager_fk
            REFERENCES teachers
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX course_manager_uindex
    ON course_manager (course, manager);

CREATE TABLE users_groups
(
    user_id  bigint  NOT NULL
        CONSTRAINT users_fk
            REFERENCES users
            ON DELETE RESTRICT,
    group_id integer NOT NULL
        CONSTRAINT groups_fk
            REFERENCES unit_groups
            ON DELETE RESTRICT
);

COMMENT ON TABLE users_groups IS 'N groups - N users';

CREATE UNIQUE INDEX user_group_uindex
    ON users_groups (user_id, group_id);

CREATE TABLE activities_per_test
(
    test_id     integer NOT NULL
        CONSTRAINT test_fk
            REFERENCES log_tests
            ON DELETE RESTRICT,
    activity_id integer NOT NULL
        CONSTRAINT activities_fk
            REFERENCES log_activities
            ON DELETE RESTRICT
);

CREATE UNIQUE INDEX activities_test_uindex
    ON activities_per_test (test_id, activity_id);

CREATE TABLE log_homeworks
(
    homework_id          integer GENERATED ALWAYS AS IDENTITY
        CONSTRAINT log_homeworks_pk
            PRIMARY KEY,
    hw_short_description text                                               NOT NULL,
    hw_full_description  text,
    hw_turn_in_method    text,
    hw_due_date          timestamp WITH TIME ZONE                           NOT NULL,
    attached_files       text,
    from_activity        integer
        CONSTRAINT log_homeworks_from_activity_fk
            REFERENCES activities
            ON DELETE SET NULL,
    added_timestamp      timestamp WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    accepted             boolean                  DEFAULT FALSE             NOT NULL,
    accepted_by          bigint
        CONSTRAINT log_homeworks_accepted_by_fk
            REFERENCES users
            ON DELETE SET NULL,
    accepted_timestamp   timestamp WITH TIME ZONE,
    other_details        text,
    added_by             bigint                                             NOT NULL
        CONSTRAINT log_homeworks_added_by_fk
            REFERENCES users
            ON DELETE SET NULL
);

ALTER SEQUENCE log_homeworks_homework_id_seq1 OWNED BY log_homeworks.homework_id;

CREATE UNIQUE INDEX log_homeworks_homework_id_uindex
    ON log_homeworks (homework_id);


