# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012,
# 2013, 2014 OnlineGroups.net and Contributors.
#
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
import os
import DateTime
import sqlalchemy as sa
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl import AuthEncoding
from AccessControl import Permissions as Perms
from Globals import INSTANCE_HOME
from App.class_init import InitializeClass
from Products.NuxUserGroups import UserFolderWithGroups
from zope.interface import implements
from Products.CustomUserFolder.interfaces import ICustomUserFolder
from AccessControl.User import readUserAccessFile
from gs.core import (to_unicode_or_bust)
from gs.database import getTable, getSession

import logging
log = logging.getLogger('CustomUserFolder')


class CustomUserFolder(UserFolderWithGroups):
    """ A user folder for CampusUser users, based on the NuxUserGroup
    UserFolder interface."""
    implements(ICustomUserFolder)

    security = ClassSecurityInfo()

    meta_type = "Custom User Folder"
    id = 'acl_users'  # lint:ok
    title = 'Custom User Folder'
    icon = 'p_/UserFolder'

    security.declarePrivate('_mainUser')
    _mainUser = PageTemplateFile('zpt/mainUser.zpt', globals(),
                                 __name__='manage_main')
    manage = manage_main = _mainUser

    def __init__(self, user_folder_id):
        """ Initialize the data storage.

        """
        self.user_folder_id = user_folder_id
        UserFolderWithGroups.__init__(self)

    def _encryptPassword(self, pw):
        # we need to override the default, because if we encrypt with SSHA
        # we have trouble when we do the wire protocol
        upw = to_unicode_or_bust(pw)
        utf8pw = upw.encode('utf-8', 'ignore')
        return AuthEncoding.pw_encrypt(utf8pw, 'SHA')

    security.declarePrivate('_getUserFolder')

    def _getUserFolder(self):
        """ Return the folder object that contains the user objects,  or
        None."""
        return getattr(self, self.user_folder_id, None)

    security.declareProtected(Perms.manage_users, 'get_userIdByEmail')

    def get_userIdByEmail(self, email):
        """ Get a user ID by email address.

        """
        email = email.lower()
        uet = getTable('user_email')
        s = sa.select([uet.c.user_id], limit=1)
        s.append_whereclause(email == sa.func.lower(uet.c.email))

        session = getSession()
        r = session.execute(s).fetchone()
        if r:
            return r['user_id']

        return None

    security.declareProtected(Perms.manage_users, 'get_userByEmail')

    def get_userByEmail(self, email):
        """ Get the user by email address.
        """
        user_id = self.get_userIdByEmail(email)
        retval = None
        if user_id:
            retval = self.getUser(user_id)
        return retval

    security.declareProtected(Perms.manage_users, 'get_userByEmail')

    def getUserNames(self):
        """ Return a list of usernames.

        """
        user_folder = self._getUserFolder()
        names = list(user_folder.objectIds('Custom User'))
        names.sort()

        return names

    security.declareProtected(Perms.manage_users, 'getUsers')

    def getUsers(self):
        """ Return a list of user objects.

        """
        user_folder = self._getUserFolder()
        users = list(user_folder.objectValues('Custom User'))
        user_list = []
        for user in users:
            user_list.append(user.__of__(self))
        return user_list

    security.declareProtected(Perms.manage_users, 'getUser')

    def getUser(self, name):
        """ Return the named user object or None.

        """
        if not name:
            log.error("User ID was not set in getUser")
            return None

        assert type(name) in (str, unicode), \
            'User ID is a %s not a string (%s)' % (type(name), name)
        user_folder = self._getUserFolder()
        user = getattr(user_folder, name, None)
        if user:
            return user.__of__(self)
        return None

    security.declarePrivate('_doAddUser')

    def _doAddUser(self, name, password, roles, domains, groups=(), **kw):
        """ Create a new user.

        """
        import CustomUser

        user_folder = self._getUserFolder()
        if password is not None and self.encrypt_passwords:
            password = self._encryptPassword(password)

        CustomUser.addCustomUser(user_folder, name, password, roles,
                                 domains)
        self.setGroupsOfUser(groups, name)

        user = self.getUser(name)

        user.init_properties()
        user.title = name
        user.manage_setLocalRoles(name, ['Owner'])

        return 1

    security.declarePrivate('_doChangeUser')

    def _doChangeUser(self, name, password, roles, domains, groups=None,
                      **kw):
        user = self.getUser(name)
        if password is not None:
            if (self.encrypt_passwords
                    and (not self._isPasswordEncrypted(password))):
                password = self._encryptPassword(password)
            user.__ = password
        user.roles = roles
        user.domains = domains

        if groups is not None:
            self.setGroupsOfUser(groups, name)

    security.declarePrivate('_doDelUsers')

    def _doDelUsers(self, names):
        user_folder = self._getUserFolder()
        user_folder.manage_delObjects(names)

        for username in names:
            user = self.getUser(username)
            if user is None:
                raise KeyError('User "%s" does not exist' % username)
            groupnames = user.getGroups()
            self.delGroupsFromUser(groupnames, username)

    security.declareProtected(Perms.manage_users, 'simple_register_user')

    def simple_register_user(self, email, userId, displayName):
        assert email
        assert userId
        assert displayName
        assert not(self.getUser(userId))
        assert not(self.get_userIdByEmail(email)), '<%s> exists' % email

        self._doAddUser(userId, '', [], [], [])
        user = self.getUser(userId)
        assert user, 'Did not create the user %s with the email %s' %\
            (displayName, userId)

        user.manage_changeProperties(fn=displayName)
        # For now
        user.manage_addProperty('creation_date', DateTime.DateTime(),
                                'date')

        assert user
        assert userId == user.getId()
        assert displayName == user.getProperty('fn')
        return user

    security.declareProtected(Perms.manage_users, 'wf_manage_users')

    def wf_manage_users(self, submit=None, REQUEST=None, RESPONSE=None):
        """ A helper submission method for the modified ZMI interface,
        to handle the multiple selection box.

        """
        if submit == 'Edit':
            try:
                REQUEST['name'] = REQUEST['names'][0]
            except:
                pass

        return self.manage_users(submit, REQUEST, RESPONSE)

    security.declarePublic('get_userIdByNickname')

    def get_userIdByNickname(self, nickname):
        assert nickname
        assert type(nickname) in (str, unicode)
        unt = getTable('user_nickname')
        s = sa.select([unt.c.user_id], limit=1)
        s.append_whereclause(unt.c.nickname == nickname)

        session = getSession()
        r = session.execute(s)
        retval = ''
        if r.rowcount:
            retval = r.fetchone()['user_id']
        return retval

    security.declarePublic('get_userByNickname')

    def get_userByNickname(self, nickname):
        assert nickname
        assert type(nickname) in (str, unicode)
        userId = self.get_userIdByNickname(nickname)
        retval = None
        if userId:
            retval = self.getUser(userId)
        return retval

    security.declarePrivate('_createInitialUser')

    def _createInitialUser(self):
        """
        If there are no users or only one user in this user folder,
        populates from the 'inituser' file in INSTANCE_HOME.
        We have to do this even when there is already a user
        just in case the initial user ignored the setup messages.
        We don't do it for more than one user to avoid
        abuse of this mechanism.
        Called only by OFS.Application.initialize().
        """
        if len(self.data) <= 1:
            info = readUserAccessFile('inituser')
            if info:
                name, password, domains, remote_user_mode = info
                self._doDelUsers(self.getUserNames())
                self._doAddUser(name, password, ('Manager',), domains)
                try:
                    os.remove(os.path.join(INSTANCE_HOME, 'inituser'))
                except:
                    pass

manage_addCustomUserFolderForm = PageTemplateFile(
    'zpt/manage_addCustomUserFolderForm.zpt',
    globals(),
    __name__='manage_addCustomUserFolderForm')


def manage_addCustomUserFolder(self, id='users', REQUEST=None):
    """ Add a CustomUserFolder to a container as acl_users.

    """
    ob = CustomUserFolder(id)
    self._setObject('acl_users', ob)
    if REQUEST is not None:
        return self.manage_main(self, REQUEST)

InitializeClass(CustomUserFolder)


def initialize(context):
    context.registerClass(
        CustomUserFolder,
        permission='Manage users',
        constructors=(manage_addCustomUserFolderForm,
                      manage_addCustomUserFolder,),
        icon='icons/customuserfolder.gif'
        )
