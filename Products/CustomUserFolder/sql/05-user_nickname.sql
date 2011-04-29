SET CLIENT_ENCODING = 'UTF8';
SET CHECK_FUNCTION_BODIES = FALSE;
SET CLIENT_MIN_MESSAGES = WARNING;

CREATE TABLE user_nickname (
    USER_ID           TEXT                        NOT NULL,
    NICKNAME          TEXT                        PRIMARY KEY,
    DATE              TIMESTAMP WITH TIME ZONE    NOT NULL
);

