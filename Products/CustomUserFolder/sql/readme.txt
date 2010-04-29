=====================
Ordering of SQL Files
=====================

:Authors: Michael JasonSmith
:Contact: Michael JasonSmith <mpj17@onlinegroups.net>
:Date: 2010-04-24
:Organization: OnlineGroups.Net <http://onlinegroups.net>`


Some SQL files depend on others. If the files are not run in the correct
order the PostgreSQL database will not be made correctly during buildout.
I use the the same method to order the files as init.d: I prefix the
filename with the order-number. The builout script globs these files,
then sorts them into the correct order. The actual Python modules are
explicitly ordered in the buildout script.

