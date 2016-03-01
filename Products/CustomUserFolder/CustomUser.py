# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012,
# 2013, 2014, 2016 OnlineGroups.net and Contributors.
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
from __future__ import absolute_import
import os
try:
    # zope 2.12+
    from zope.container.interfaces import (IObjectRemovedEvent,
                                           IObjectAddedEvent)
except ImportError:
    #lint:disable
    from zope.app.container.interfaces import (IObjectRemovedEvent,
                                               IObjectAddedEvent)
    #lint:enable
from AccessControl import (ClassSecurityInfo, Permissions as Perms,
                           allow_class)
from AccessControl.User import User
from App.class_init import InitializeClass
from OFS.Folder import Folder
from zope.interface import implements
from Products.CustomUserFolder.interfaces import ICustomUser
from Products.XWFCore.XWFUtils import locateDataDirectory
from gs.image import GSImage
from .queries import UserQuery

import logging
log = logging.getLogger('CustomUser')


def user_image_path(context, user_id):
        siteId = context.site_root().getId()
        dataDir = locateDataDirectory("groupserver.user.image", (siteId,))
        fileName = '%s.jpg' % user_id
        imagePath = os.path.join(dataDir, fileName)

        retval = None
        if os.path.isfile(imagePath):
            retval = imagePath
        return retval


class CustomUser(User, Folder):
    """ A Custom user, based on the builtin user object.

    """
    implements(ICustomUser)

    version = 1.9

    security = ClassSecurityInfo()

    meta_type = "Custom User"

    firstName = ''
    lastName = ''
    preferredName = ''
    shortName = ''
    fn = ''
    biography = ''
    title = ''
    currentDivision = ''
    restrictImage = 1
    unrestrictedImageRoles = []
    _properties_def = (
        {'id': 'firstName', 'type': 'string', 'mode': 'w'},
        {'id': 'lastName', 'type': 'string', 'mode': 'w'},
        {'id': 'preferredName', 'type': 'string', 'mode': 'w'},
        {'id': 'shortName', 'type': 'string', 'mode': 'w'},
        {'id': 'fn', 'type': 'ustring', 'mode': 'w'},
        {'id': 'unrestrictedImageRoles', 'type': 'lines', 'mode': 'w'},
        {'id': 'biography', 'type': 'text', 'mode': 'w'},
        {'id': 'restrictImage', 'type': 'boolean', 'mode': 'w'},
        {'id': 'title', 'type': 'string', 'mode': 'w'},
        {'id': 'currentDivision', 'type': 'string', 'mode': 'w'},
        )

    _properties = _properties_def

    security.declarePrivate('init_properties')

    def init_properties(self):
        self.firstName = ''
        self.lastName = ''
        self.preferredName = ''
        self.shortName = ''
        self.fn = ''
        self.biography = ''
        self.title = ''
        self.restrictImage = 1
        self.currentDivision = ''
        self.unrestrictedImageRoles = []
        self._p_changed = 1

    security.declareProtected(Perms.manage_properties, 'del_group')

    def del_group(self, group):
        """ Remove a group from the user"""
        if not group:
            m = u'No group provided'
            raise ValueError(m)
        if type(group) not in (unicode, str):
            m = u'Group ID is a "{0}", not a string'.format(type(group))
            raise TypeError(m)

        m = u'del_group: Removing {0} ({1}) from {2}'
        msg = m.format(self.getProperty('fn', ''), self.getId(), group)
        log.info(msg)

        acl_users = getattr(self, 'acl_users', None)
        try:
            acl_users.delGroupsFromUser([group], self.getId())
        except ValueError:
            m = u'The group {0} not in the list of groups for {1}'
            msg = m.format(group, self.getId())
            log.warn(msg)

    security.declareProtected(Perms.manage_properties, 'refresh_properties')

    def refresh_properties(self):
        """ Refresh the properties from the class definition.

        """
        self._properties = self._properties_def

    def get_xsendfile_header(self):
        sendfile_header = None
        # check that we're actually being called from a browser first
        if not(hasattr(self, 'REQUEST')):
            sendfile_header = None
        elif 'X-Sendfile-Type' in self.REQUEST:
            sendfile_header = self.REQUEST.get('X-Sendfile-Type')
        elif 'HTTP_X_SENDFILE_TYPE' in self.REQUEST:
            sendfile_header = self.REQUEST.get('HTTP_X_SENDFILE_TYPE')

        return sendfile_header

    security.declareProtected(Perms.view, 'get_image')

    def get_image(self, url_only=True):
        """ Get the URL or actual image object for a user.

        """
        retval = None
        imagePath = self.get_image_path()
        if imagePath:
            if url_only:
                retval = '/p/%s/photo' % self.get_canonicalNickname()
            else:
                f = file(imagePath, 'rb')
                sendfile_header = self.get_xsendfile_header()
                if sendfile_header:
                    # we can use x-sendfile, so just return some string
                    # to stop apache choking up
                    gsimage = GSImage(f)
                    cache_path = gsimage.get_resized(81, 108, True,
                                                     return_cache_path=True)
                    self.REQUEST.response.setHeader('Content-Type',
                                                    gsimage.contentType)
                    if cache_path:
                        self.REQUEST.response.setHeader(sendfile_header,
                                                        cache_path)
                    else:
                        self.REQUEST.response.setHeader(sendfile_header,
                                                        imagePath)
                    retval = 'image'
                else:
                    retval = GSImage(f).get_resized(81, 108, True)
        return retval

    security.declareProtected(Perms.view, 'get_image_path')

    def get_image_path(self):
        """ Get the image path for a user.

        """
        return user_image_path(self, self.getId())

    security.declareProtected(Perms.view, 'get_resized_image_path')

    def get_resized_image_path(self, x, y, maintain_aspect=True,
                               only_smaller=True):
        """ Get the resized image path for a user.

        """
        imagePath = self.get_image_path()
        f = file(imagePath, 'rb')
        retval = GSImage(f).get_cache_name(x, y, maintain_aspect,
                                           only_smaller)
        return retval

    # Most of the "ByKey" methods can be removed. Just waiting on
    # gs.group.member.invite.base to be updated

    security.declareProtected(Perms.manage_properties,
                              'set_disableDeliveryByKey')

    def set_disableDeliveryByKey(self, key):
        """ Disable the email delivery for a given key.

            The key normally represents a group, but may
            represent something else in the future.

        """
        uq = UserQuery(self)
        # TODO: we don't quite support site_id yet
        site_id = ''
        group_id = key
        uq.set_groupEmailSetting(site_id, group_id, 'webonly')

    security.declareProtected(Perms.manage_properties,
                              'set_enableDeliveryByKey')

    def set_enableDeliveryByKey(self, key):
        """ Enable the email delivery for a given key.

            The key normally represents a group, but may
            represent something else in the future.

        """
        uq = UserQuery(self)
        # TODO: we don't quite support site_id yet
        site_id = ''
        group_id = key
        uq.clear_groupEmailSetting(site_id, group_id)
        #uq.set_groupEmailSetting(site_id, group_id, '')

    security.declareProtected(Perms.manage_properties,
                              'set_enableDigestByKey')

    def set_enableDigestByKey(self, group_id, site_id=''):
        """ Enable the email digest for a given key.

            The key normally represents a group, but may
            represent something else in the future.

        """
        uq = UserQuery(self)
        # TODO: we don't quite support site_id yet
        uq.set_groupEmailSetting(site_id, group_id, 'digest')

        m = '%s (%s) enabling digest mode for %s' % \
            (self.getProperty('fn', ''), self.getId(), group_id)
        log.info(m)

    security.declareProtected(Perms.manage_properties,
                              'set_disableDigestByKey')

    def set_disableDigestByKey(self, group_id, site_id=''):
        """ Disable the email digest for a given key.

            The key normally represents a group, but may
            represent something else in the future.

        """
        uq = UserQuery(self)
        uq.clear_groupEmailSetting(site_id, group_id)

        m = '%s (%s) disabling digest mode for %s' % \
            (self.getProperty('fn', ''), self.getId(), group_id)
        log.info(m)

    security.declareProtected(Perms.manage_properties,
                              'get_deliverySettingsByKey')

    def get_deliverySettingsByKey(self, key):
        """ Get the settings for the given key.

            returns 1 if default, 2 if non-default, 3 if digest,
                    or 0 if disabled.
        """
        uq = UserQuery(self)

        # TODO: we don't quite support site_id yet
        site_id = ''
        group_id = key

        setting = uq.get_groupEmailSetting(site_id, group_id)

        # --=mpj17=--
        # TODO: we do not report if there is a specific delivery address
        #   for web only or diget modes, only one email per post mode.
        if setting == 'webonly':
            return 0
        elif setting == 'digest':
            return 3
        elif uq.get_groupUserEmail(site_id, group_id):
            return 2
        else:
            return 1

    security.declareProtected(Perms.manage_properties,
                              'get_deliveryEmailAddressesByKey')

    def get_deliveryEmailAddressesByKey(self, key):
        """ Get the user's preferred delivery email address. If none is
        set, it defaults to the first in the list.

        """
        retval = []

        # First, check to see if we are not web only
        groupSetting = self.get_deliverySettingsByKey(key)
        if groupSetting != 0:
            # Next, check to see if we've customised the delivery options
            #   for that group
            # TODO: Check email addr
            group_email_addresses = \
                self.get_specificEmailAddressesByKey(key)
            if group_email_addresses:
                retval = group_email_addresses
            else:
                # If there are no specific settings for the group, return
                #   the default settings
                retval = self.get_preferredEmailAddresses()

        return retval

    security.declareProtected(Perms.manage_properties,
                              'get_specificEmailAddressesByKey')

    def get_specificEmailAddressesByKey(self, key):
        '''Get the specific email addresses for a group (alias "key")

        ARGUMENTS
            "key":    The ID of the group to look up.

        RETURNS
            A list of email addresses that the current user has set for
            specific delivery. If no addresses are set an empty list is
            returned.

        SIDE EFFECTS
            None.'''

        # TODO: we don't quite support site_id yet
        site_id = ''
        group_id = key

        uq = UserQuery(self)
        retval = uq.get_groupUserEmail(site_id, group_id)

        return retval

    security.declareProtected(Perms.manage_properties,
                              'add_deliveryEmailAddressByKey')

    def add_deliveryEmailAddressByKey(self, key, email):
        """ Add an email address as a modified delivery option for a
        specific group."""
        uq = UserQuery(self)
        email = self._validateAndNormalizeEmail(email)

        # TODO: we don't support site_id
        site_id = ''
        group_id = key

        if email not in uq.get_groupUserEmail(site_id, group_id):
            uq.add_groupUserEmail(site_id, group_id, email)

            m = 'Added the address <%s> from the delivery settings for '\
                'the %s group for %s (%s)' % \
                (email, group_id, self.getProperty('fn', ''), self.getId())
            log.info(m)

    security.declareProtected(Perms.manage_properties,
                              'remove_deliveryEmailAddressByKey')

    def remove_deliveryEmailAddressByKey(self, key, email):
        """ Remove an email address as a modified delivery option for a
        specific group. """
        uq = UserQuery(self)
        email = self._validateAndNormalizeEmail(email)

        # TODO: we don't support site_id
        site_id = ''
        group_id = key

        uq.remove_groupUserEmail(site_id, group_id, email)

        m = 'Removed the address <%s> from the delivery settings for the '\
            '%s group for %s (%s)' % \
            (email, group_id, self.getProperty('fn', ''), self.getId())
        log.info(m)
        email_addresses = uq.get_groupUserEmail(site_id, group_id)
        return email_addresses

    # Password-related methods. Most of these have been moved to
    #   gs.profile.password.passworduser.PasswordUser

    security.declareProtected(Perms.manage_properties, 'get_password')

    def get_password(self):
        """ Get the user's password. Note, if the password is encrypted,
        this won't be of much use.

        RETURNS
          The password in clear-text.
        """
        return self._getPassword()

    # Nickname related methods.

    def get_canonicalNickname(self):
        uq = UserQuery(self)
        nickname = uq.get_latestNickname()
        if nickname is None:
            nickname = self.getId()

        return nickname

    def add_nickname(self, nickname):
        uq = UserQuery(self)
        uq.add_nickname(nickname)
        m = 'add_nickname: Added nickname "%s" to %s (%s)' %\
            (nickname, self.getProperty('fn', ''), self.getId())
        log.info(m)

    def clear_nicknames(self):
        uq = UserQuery(self)
        uq.clear_nicknames()
        m = 'clear_nicknames: Cleared nicknames from  %s (%s)' %\
            (self.getProperty('fn', ''), self.getId())
        log.info(m)

    def clear_groups(self):
        acl_users = getattr(self, 'acl_users', None)
        assert acl_users, 'Could not get acl_users'
        for groupname in self.getGroups():
            group = acl_users.getGroupById(groupname)
            try:
                group._delUsers((self.getId(),))
            except ValueError:
                msg = 'Could not remove user "{0}" from the group "{1}": not in the group'
                log.warn(msg)
        m = 'clear_groups: Cleared groups from  %s (%s)' %\
            (self.getProperty('fn', ''), self.getId())
        log.info(m)

    #
    # Views and Workflow
    #

    def index_html(self):
        """ Return the default view.

        """
        return self.REQUEST.RESPONSE.redirect('/')

    def upgrade(self):
        """ Upgrade existing objects.

        """
        # originally we weren't setting the ID correctly
        self.id = self.getId()

InitializeClass(CustomUser)


class ValidationError(Exception):
    """ Raised if an email address is invalid.

    """

allow_class(ValidationError)


def addCustomUser(self, name, password, roles, domains):
    """ Add a CustomUser to a folder.

    """
    ob = CustomUser(name, password, roles, domains)
    ob.id = ob.getId()  # make sure we have an actual ID
    self._setObject(name, ob)


def removedCustomUser(ob, event):
    """ A CustomUser was removed.

    """
    assert ob
    uid = ob.getId()
    ob.clear_groups()
    # FIX
    # ob.clear_userPasswordResetVerificationIds()
    try:
        ob.clear_nicknames()
    except IndexError:
        msg = 'Index error when clearing nicknames of "{0}". Ignoring.'.format(uid)
        log.warn(msg)
    m = u'removedCustomUser: Deleted "%s"' % uid
    log.info(m)
    # FIXME: Get the EmailUser to handle this event.
    return


def movedCustomUser(ob, event):
    """A CustomUser was moved.
    """
    if not IObjectRemovedEvent.providedBy(event):
        return
    if not IObjectAddedEvent.providedBy(event):
        removedCustomUser(ob, event)
