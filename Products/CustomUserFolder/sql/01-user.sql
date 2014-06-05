SET CLIENT_ENCODING = 'UTF8';
SET CLIENT_MIN_MESSAGES = WARNING;

-- These are email addresses that are *never* allowed to
-- participate in the system. Oddly enough, while it is declared
-- here (for sentemental reasons) it is only ever used by
-- Products.XWFMailingListManager. It probabily should be
-- refactored, along with the mailing-list manager.
CREATE TABLE email_blacklist (
    email  TEXT  NOT NULL
);

