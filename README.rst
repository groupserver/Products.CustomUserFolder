=============================
``Products.CustomUserFolder``
=============================
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
The user-object in GroupServer
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:Author: `Michael JasonSmith`_
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2014-10-09
:Organization: `GroupServer.org`_
:Copyright: This document is licensed under a
  `Creative Commons Attribution-Share Alike 4.0 International License`_
  by `OnlineGroups.Net`_.

Introduction
============

The *custom user* is a warning. The warning is in the name: it
was **intended** to be a customisation of the underlying
``AccessControl.User``. However, as features were added to
GroupServer the ``CustomUser`` became larger and larger, ending
up at over a thousand lines.

With time, and experience, we have managed to knock this back to
a rather svelte 500-ish lines. The code is now in the
``gs.profile.*`` and ``gs.group.member.*`` products.

Resources
=========

- Code repository: https://github.com/groupserver/Products.CustomUserFolder
- Questions and comments to http://groupserver.org/groups/development
- Report bugs at https://redmine.iopen.net/projects/groupserver

.. _GroupServer: http://groupserver.org/
.. _GroupServer.org: http://groupserver.org/
.. _OnlineGroups.Net: https://onlinegroups.net
.. _Michael JasonSmith: http://groupserver.org/p/mpj17
.. _Creative Commons Attribution-Share Alike 4.0 International License:
    http://creativecommons.org/licenses/by-sa/4.0/
