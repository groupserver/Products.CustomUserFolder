CREATE TABLE user_invitation (
    INVITATION_ID     TEXT                        PRIMARY KEY,
    USER_ID           TEXT                        NOT NULL,
    ADMIN_USER_ID     TEXT                        NOT NULL,
    SITE_ID           TEXT                        NOT NULL,
    GROUP_ID          TEXT                        NOT NULL,
    INVITATION_DATE   TIMESTAMP WITH TIME ZONE    DEFAULT NULL
);
--=mpj17=-- There is no foreign key for user_id, yet

--=mpj17=-- Each user can only be invited to each group once
CREATE UNIQUE INDEX group_invite_idx ON user_invitation USING BTREE 
    (user_id, site_id, group_id);
    

