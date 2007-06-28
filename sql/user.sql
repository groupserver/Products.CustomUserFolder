SET CLIENT_ENCODING = 'UTF8';
SET CHECK_FUNCTION_BODIES = FALSE;
SET CLIENT_MIN_MESSAGES = WARNING;

CREATE TABLE USER_EMAIL (
    USER_ID           TEXT                      NOT NULL,
    EMAIL             TEXT                      UNIQUE NOT NULL,
    IS_PREFERRED      BOOLEAN                   NOT NULL DEFAULT 'false',
    VERIFIED_DATE     TIMESTAMP WITH TIME ZONE  DEFAULT NULL
);

-- The combination of user_id and email is unique within the system
CREATE UNIQUE INDEX USER_ID_EMAIL_PKEY ON USER_EMAIL
       USING BTREE (user_id, email);

-- Email is unique within the system
CREATE UNIQUE INDEX USER_EMAIL_EMAIL_LOWER_IDX ON USER_EMAIL
       USING BTREE (lower(email));

CREATE TABLE GROUP_USER_EMAIL (
    USER_ID           TEXT                      NOT NULL,
    SITE_ID	      TEXT			NOT NULL DEFAULT ''::TEXT,
    GROUP_ID          TEXT			NOT NULL,
    EMAIL             TEXT                      NOT NULL REFERENCES USER_EMAIL (EMAIL) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE UNIQUE INDEX user_site_group_email_pkey ON group_user_email USING BTREE
       (user_id, site_id, group_id, lower(email));

CREATE TABLE EMAIL_SETTING (
    USER_ID           TEXT                      NOT NULL,
    SITE_ID	      TEXT			NOT NULL DEFAULT ''::TEXT,
    GROUP_ID          TEXT			NOT NULL DEFAULT ''::TEXT,
    SETTING	      TEXT			NOT NULL
);

CREATE UNIQUE INDEX email_setting_pkey ON email_setting USING BTREE
       (user_id, site_id, group_id);
