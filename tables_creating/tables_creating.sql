CREATE TABLE Address (
    address_id SERIAL PRIMARY KEY,
    street VARCHAR(100) NOT NULL,
    postal_code INTEGER NOT NULL
);

CREATE TABLE School (
    school_id SERIAL PRIMARY KEY,
    school_name VARCHAR(150) NOT NULL,
    address_id INTEGER NOT NULL,
    school_number INTEGER,
    FOREIGN KEY (address_id) REFERENCES Address(address_id)
);

CREATE TABLE Subject (
    subject_id SERIAL PRIMARY KEY,
    name VARCHAR(30) NOT NULL,
    score_mapping_json JSONB
);

CREATE TYPE person_role AS ENUM ('SchoolChild', 'Teacher');

CREATE TABLE Person (
    person_id SERIAL PRIMARY KEY,
    passport_series VARCHAR(10) NOT NULL,
    passport_number VARCHAR(10) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    middle_name VARCHAR(50),
    birthday DATE NOT NULL,
    role person_role NOT NULL,
    address_id INTEGER,
    school_id INTEGER NOT NULL,
    subject_id INTEGER,
    FOREIGN KEY (address_id) REFERENCES Address(address_id) ON DELETE SET NULL,
    FOREIGN KEY (school_id) REFERENCES School(school_id),
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE SET NULL
);

CREATE TABLE Classroom (
    classroom_id SERIAL PRIMARY KEY,
    number VARCHAR(10) NOT NULL,
    school_id INTEGER NOT NULL,
    FOREIGN KEY (school_id) REFERENCES School(school_id) ON DELETE CASCADE
);

CREATE TABLE Exam (
    exam_id SERIAL PRIMARY KEY,
    date_time TIMESTAMP NOT NULL,
    subject_id INTEGER NOT NULL,
    classroom_id INTEGER NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (classroom_id) REFERENCES Classroom(classroom_id) ON DELETE CASCADE
);

CREATE TABLE Task (
    task_id SERIAL PRIMARY KEY,
    number INTEGER NOT NULL,
    description VARCHAR,
    price INTEGER,
    variant INTEGER,
    subject_id INTEGER NOT NULL,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE
);

CREATE TYPE exam_result_status AS ENUM (
    'Registered',
    'Passed',
    'Failed',
    'Absent',
    'Appealed',
    'Canceled',
    'Processing',
    'Waiting'
);

CREATE TABLE ExamResult (
    exam_result_id SERIAL PRIMARY KEY,
    score INTEGER,
    status exam_result_status NOT NULL,
    comments VARCHAR,
    person_id INTEGER NOT NULL,
    subject_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES Exam(exam_id) ON DELETE CASCADE
);


CREATE TABLE WrittenTask (
    task_id INTEGER NOT NULL,
    person_id INTEGER NOT NULL,
    grade INTEGER,
    PRIMARY KEY (task_id, person_id),
    FOREIGN KEY (task_id) REFERENCES Task(task_id) ON DELETE CASCADE,
    FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE
);

CREATE TABLE PersonExam (
    person_id INTEGER NOT NULL,
    exam_id INTEGER NOT NULL,
    PRIMARY KEY (person_id, exam_id),
    FOREIGN KEY (person_id) REFERENCES Person(person_id) ON DELETE CASCADE,
    FOREIGN KEY (exam_id) REFERENCES Exam(exam_id) ON DELETE CASCADE
);