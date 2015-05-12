Changelog
=========

11.2.2 (2015-05-12)
-------------------

* Fixing the case where the person being removed from a group is
  not in a group

11.2.1 (2014-10-16)
-------------------

* Coping with non-ascii encrypted passwords
* Ensure the password is not encrypted before encrypting it

11.2.0 (2014-10-09)
-------------------

* Moving to GitHub as the primary code repository, and naming the
  reStructuredText files as such
* Removing unused methods
* Added a README

11.0.0 (2014-06-19)
-------------------

* Moving the ``clear_addresses`` method to the
  ``gs.profile.email.base`` product
* Cleanup for the ``configure.zcml``

10.4.0 (2014-06-05)
-------------------

* Fixes for a circular dependency
* Moving the email-settings SQL to the
  ``gs.group.member.email.base`` product

10.3.0 (2013-10-09)
-------------------

* Adding the ``del_group`` method
* A code tidy for PEP-8 and ``absolute_import``

10.2.0 (2013-06-05)
-------------------

* Updated the ``add_groupWithNotification`` method and the
  ``del_groupWithNotification`` method to use ``IGSNotifyUser``

10.1.0 (2013-03-27)
-------------------

* Removing the old photo-method

10.0.3 (2012-10-17)
-------------------

* Adding the ``gs.email`` product to the product dependencies

10.0.2 (2012-08-24)
-------------------

* More deprecation work

10.0.1 (2012-07-25)
-------------------

* Stop using some of the deprecated methods

10.0.0 (2012-06-28)
-------------------

* Switching to ``gs.database``

9.0.2 (2011-04-29)
------------------

* Silenced the SQL table creation scripts

9.0.1 (2011-04-05)
------------------

* Bug fix because the URL is ``self.REQUEST['URL']``
* Updates to the deprecation

9.0.0 (2011-01-31)
------------------

* Moving some email-code to the ``gs.profile.email.base`` product
* Moving some verification code to the
  ``gs.profile.email.verification`` product

8.1.5 (2011-01-01)
------------------

* Deprecating all the things

8.1.4 (2010-11-22)
------------------

* Deleting the password-reset SQL, as it has move to the
  ``gs.profile.password`` product
* Fixing some typos and an indentation issue

8.1.3 (2010-11-05)
------------------

* Filtering out duplicates from the group-specific email
  addresses
* Code tidy

8.1.2 (2010-08-06)
------------------

* Fixes with the automatic version numbering

8.1.1 (2010-07-30)
------------------

* Removing the ``user_invitation`` table, as code has moved to
  ``gs.group.member.invite``

8.1.0 (2010-06-09)
------------------

* Support for Zope2 2.12

8.0.0 (2010-04-29)
------------------

* Moving ``send_notification`` to the new ``gs.profile.notify``
  product
* Use the lowered index to search the ``user_email`` table
* Reordering the SQL files, because of their dependency

7.0.0 (2009-11-04)
------------------

* Turned into an egg
* Added support for Mercurial
* Added support for ``x-sendfile`` headers

6.5.0 (2009-08-06)
------------------

* Added support for an email blacklist

6.4.0 (2009-06-03)
------------------

* Added a method for getting a path to the re-sized image of the
  user, and associated fixes

6.3.3 (2009-02-27)
------------------

* Code cleanup

6.3.2 (2008-12-10)
------------------

* Fixes for deleting

6.3.1 (2008-10-02)
------------------

* Performance updates

6.3.0 (2008-09-08)
------------------

* Retrieve images from disk, rather than the ZODB
* Fixes to image re-sizing
* Updates related to the creation of the ``gs.image`` product

6.2.0 (2008-08-18)
------------------

* Added a factory for the user-info object for the currently
  logged in user
* Fix for the anonymous user-info class

6.1.2 (2008-06-24)
------------------

* Fix and optimise the nickname cache

6.1.1 (2008-06-17)
------------------

* Not lowering the email-address when we add it (case preserving,
  but case insensitive)
* Code tidy

6.1.0 (2008-06-07)
------------------

* Being more robust when searching for an email address
* Added a helper to unverify an email 
* Cache fixes
* Fixed a memory leak

6.0.1 (2008-05-20)
------------------

* Clearing the caches when someone is added or removed from a
  group

6.0.0 (2008-04-12)
------------------

* Removing the old registration code
* Added support for nicknames
* Only use verified email-addresses for notifications by default
* More robustness for the user-info factory

5.2.0 (2008-02-14)
------------------

* Invitiation support
* Further improvements to delete

5.1.0 (2008-01-30)
------------------

* Improved image search
* Verify email-addresses, rather than people

5.0.0 (2008-01-16)
------------------

* New password-reset system
* Remove a user from all groups when the user-object is deleted
* Using ``fn`` as the default displayed name


4.4.0 (2007-12-11)
------------------

* Updated the name-system to use ``preferredName``, rather than
  ``firstName`` or ``lastName``

4.3.1 (2007-12-04)
------------------

* Fixes to email-address verification

4.3.0 (2007-11-30)
------------------

* Added support for the new registration page
* Separate the rendering of a notification from the sending of a
  notification

4.2.0 (2007-10-24)
------------------

* Removed logic from the ``add_group`` notification
* Removed logic from the ``del_group`` notification
* Moved some code to ``XWFUtils``

4.1.2 (2007-10-12)
------------------

* Send some notifications to all email addresses of a user
* Delete settings when a user-object is deleted

4.1.1 (2007-10-01)
------------------

* More robust default parameters

4.1.0 (2007-09-13)
------------------

* Remove the email addresses of a use when the user-object is
  deleted

4.0.0 (2007-07-11)
------------------

* Added a user-info class
* Email-settings now in the relational database (PostgreSQL)
* Support for getting user-IDs by email-address

3.2.1 (2007-05-17)
------------------

* Fixing a registration issue

3.2.0 (2007-04-12)
------------------

* Remove hardcoding of email addresses from notifications
* Make sure ``user_id`` is ASCII

3.1.5 (2007-03-20)
------------------

* Bugfix to get some messages out

3.1.4 (2007-01-30)
------------------

* Explicitly ensure encryption is ``SHA`` not ``SSHA`` because of
  the wire protocol

3.1.3 (2006-08-29)
------------------

* Fix a security issue with a URL

3.1.2 (2006-04-09)
------------------

* Explicitly pass the password to the verification notification

3.1.1 (2006-03-16)
------------------

* Send site-names out in email-verification messages

3.1.0 (2006-03-02)
------------------

* Added auto-moderation support

3.0.0 (2006-02-14)
------------------

* Added ``set_password`` and ``reset_passwords`` to the user
* Bug fixes

2.3.1 (2005-12-03)
------------------

* Zope 2.8+ compatibility fixes

2.3.0 (2005-05-05)
------------------

* Flexible registration messages

2.2.1 (2005-02-20)
------------------

* Fixed a security bug

2.2.0 (2005-02-08)
------------------

* Turn off individual notifications
* Fixed issue with verification
* Fixed issue with removing email addresses

2.1.1 (2005-01-25)
------------------

* Email-address capitalisation fix

2.1.0 (2005-01-04)
------------------

* Delete (leave) groups with a notification
* Added topic-digest configuration support
* Fixed an error with verification

2.0.0 (2004-12-08)
------------------

* Support for registration

1.2.0 (2004-10-27)
------------------

* Added support for configurable email-delivery addresses

1.1.1 (2004-08-15)
------------------

* Bug fixes

1.1.0 (2004-05-28)
------------------

* Added profile image handling

1.0.0 (2004-02-18)
------------------

* Group aware
* More robust email handling

0.0.2 (2003-08-27)
------------------

* Updated the unit tests

0.0.1 (2003-03-24)
------------------

* Initial release
