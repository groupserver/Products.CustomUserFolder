CREATE TABLE PASSWORD_RESET (
    VERIFICATION_ID  TEXT    PRIMARY KEY,
    USER_ID          TEXT    NOT NULL
);
--=mpj17=-- There is no foreign key for user_id, yet

