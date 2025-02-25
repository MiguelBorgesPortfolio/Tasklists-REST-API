-- USERS
DROP TABLE IF EXISTS user;
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    username TEXT,
    password TEXT
);

INSERT INTO user VALUES (NULL, 'Homer Simpson', 'homer@simpsons.org', 'homer', '1234');
INSERT INTO user VALUES (NULL, 'Bart Simpson', 'bart@simpsons.org', 'bart', '1234');

-- PROJECTS
DROP TABLE IF EXISTS project;
CREATE TABLE project (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    title TEXT,
    creation_date TEXT,
    last_updated TEXT,
    FOREIGN KEY(user_id) REFERENCES user(id)
);

INSERT INTO project VALUES (NULL, 1, 'Doughnuts', '2020-05-01', '2020-06-01');
INSERT INTO project VALUES (NULL, 1, 'Eat well', '2020-05-01', '2020-05-02');
INSERT INTO project VALUES (NULL, 2, 'Save the world!', '2020-05-07', '2020-06-01');

-- TASKS
DROP TABLE IF EXISTS task;
CREATE TABLE task (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    title TEXT,
    creation_date TEXT,
    completed INTEGER,
    FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE
);

INSERT INTO task VALUES (NULL, 1, 'Search for doughnuts', '2020-05-05', 1);
INSERT INTO task VALUES (NULL, 1, 'Eat cream', '2020-05-05', 0);
INSERT INTO task VALUES (NULL, 2, 'Eat vegetables everyday', '2020-05-10', 1);
INSERT INTO task VALUES (NULL, 2, 'Eat doughnuts everyday', '2020-05-11', 1);
INSERT INTO task VALUES (NULL, 2, 'Eat lots of sugar', '2020-05-12', 0);
INSERT INTO task VALUES (NULL, 3, 'See who needs to be saved', '2020-05-07', 0);
INSERT INTO task VALUES (NULL, 3, 'Save those who need to be saved', '2020-05-07', 0);
INSERT INTO task VALUES (NULL, 3, 'Save those from being not saved', '2020-05-08', 1);

-- MESSAGES
DROP TABLE IF EXISTS message;
CREATE TABLE message (
    id INTEGER PRIMARY KEY,
    sender_id INTEGER,
    receiver_id INTEGER,
    content TEXT,
    timestamp TEXT,
    FOREIGN KEY(sender_id) REFERENCES user(id),
    FOREIGN KEY(receiver_id) REFERENCES user(id)
);
