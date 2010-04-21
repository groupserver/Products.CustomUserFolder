CREATE TABLE user_invitation (
    INVITATION_ID     TEXT                        PRIMARY KEY,
    USER_ID           TEXT                        NOT NULL,
    INVITING_USER_ID  TEXT                        NOT NULL,
    SITE_ID           TEXT                        NOT NULL,
    GROUP_ID          TEXT                        NOT NULL,
    INVITATION_DATE   TIMESTAMP WITH TIME ZONE    DEFAULT NULL
);
--=mpj17=-- There is no foreign key for user_id, yet

