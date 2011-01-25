SET CLIENT_ENCODING = 'UTF8';
SET CHECK_FUNCTION_BODIES = FALSE;
SET CLIENT_MIN_MESSAGES = WARNING;

-- TODO: Move to gs.group.member.base

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

-- These are email addresses that are *never* allowed to participate in the system
CREATE TABLE EMAIL_BLACKLIST (
	EMAIL        TEXT        NOT NULL
);

