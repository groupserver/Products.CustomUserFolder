# coding=utf-8
# Copyright (C) 2003,2004 IOPEN Technologies Ltd.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# You MUST follow the rules in http://iopen.net/STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
#
import rfc822, re, os
try:
    # zope 2.12+
    from zope.container.interfaces import IObjectRemovedEvent,IObjectAddedEvent #@UnresolvedImport @UnusedImport
except:
    from zope.app.container.interfaces import IObjectRemovedEvent,IObjectAddedEvent #@Reimport
from AccessControl import ClassSecurityInfo, Permissions as Perms, allow_class
from AccessControl.User import User
from App.class_init import InitializeClass
from OFS.Folder import Folder
from zope.component import createObject
from zope.interface import implements
from Products.CustomUserFolder.interfaces import ICustomUser
from Products.XWFCore import XWFUtils
from Products.XWFCore.XWFUtils import locateDataDirectory
from gs.image import GSImage
from queries import UserQuery
from gs.profile.notify.interfaces import IGSNotifyUser

import logging
log = logging.getLogger('CustomUser')


def user_image_path(context, user_id):
        siteId = context.site_root().getId()
        dataDir = locateDataDirectory("groupserver.user.image",
                                              (siteId,))
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

    def send_notification(self, n_type, n_id, n_dict=None, email_only=()):
        m = 'CustomUser.send_notication is deprecated: ' \
          'it should never be used. Use '\
          'from gs.profile.notify.interfaces import IGSNotifyUser; '\
          'notify = IGSNotifyUser(userInfo); '\
          'notify.send_notification(...). The new send_notification '\
          'has the same API.'
        assert False, m

    security.declareProtected(Perms.manage_properties,
                                'add_groupWithNotification')

    def add_groupWithNotification(self, group):
        """ Add a group to the user, and if available, send them a notification.

        """
        # --=AM mpj17=-- Dear God, this is an awful place!
        # If people wonder why group-IDs must be unique across sites, this
        #    function is one of the reasons.

        from Products.XWFCore.XWFUtils import getOption, get_user, \
            get_user_realnames, get_support_email
        from Products.XWFCore.XWFUtils import get_site_by_id, \
            get_group_by_siteId_and_groupId

        site_root = self.site_root()
        acl_users = getattr(site_root, 'acl_users')

        groupNames = acl_users.getGroupNames()
        assert group in groupNames, '%s not in %s' % (group, groupNames)

        if acl_users:
            try:
                acl_users.addGroupsToUser([group], self.getId())
            except:
                return 0

        listManagers = site_root.objectValues('XWF Mailing List Manager')
        possible_list_match = re.search('(.*)_member', group)
        groupList = None
        if possible_list_match:
            possible_list_id = possible_list_match.groups()[0]
            for listManager in listManagers:
                try:
                    groupList = listManager.get_list(possible_list_id)
                except:
                    continue
                if not groupList.getProperty('moderate_new_members', False):
                    continue
                if groupList.hasProperty('moderated_members'):
                    moderated_members = filter(None,
                        list(groupList.getProperty('moderated_members', [])))
                    if self.getId() not in moderated_members:
                        moderated_members.append(self.getId())
                        groupList.manage_changeProperties(
                                        moderated_members=moderated_members)
                else:
                    moderated_members = [self.getId()]
                    groupList.manage_addProperty('moderated_members',
                                                  moderated_members, 'lines')

        n_dict = {}
        if groupList:
            siteId = groupList.getProperty('siteId', '')
            site_obj = get_site_by_id(groupList, siteId)
            assert site_obj

            groupId = groupList.getId()
            group_obj = get_group_by_siteId_and_groupId(groupList, siteId,
                                                        groupId)
            assert group_obj

            group_email = groupList.getProperty('mailto', '')
            ptn_coach_id = group_obj.getProperty('ptn_coach_id', '')
            ptn_coach_user = get_user(group_obj, ptn_coach_id)
            ptnCoach = get_user_realnames(ptn_coach_user, ptn_coach_id)
            realLife = group_obj.getProperty('real_life_group', '') \
                or group_obj.getProperty('membership_defn', '')
            supportEmail = get_support_email(group_obj, siteId)

            n_dict = {
                        'groupId': groupId,
                        'groupName': group_obj.title_or_id(),
                        'siteId': siteId,
                        'siteName': site_obj.title_or_id(),
                        'canonical': getOption(group_obj, 'canonicalHost'),
                        'grp_email': group_email,
                        'ptnCoachId': ptn_coach_id,
                        'ptnCoach': ptnCoach,
                        'realLife': realLife,
                        'supportEmail': supportEmail
                      }
            groupsInfo = createObject('groupserver.GroupsInfo', site_obj)
            groupsInfo.clear_groups_cache()

        try:
            notify = IGSNotifyUser(self)
            notify.send_notification('add_group', group, n_dict)
        except:
            # we really can't do much, because if we fail here, we may
            # cause the person to get an email over and over if they're
            # joining more than one group
            pass

        m = u'add_groupWithNotification: Added group %s to the '\
          'user "%s"' % (group, self.getId())
        log.info(m)

        return 1

    security.declareProtected(Perms.manage_properties, 'del_group')

    def del_group(self, group):
        """ Remove a group from the user"""
        if not group:
            m = u'No group provided'
            raise ValueError(m)
        if type(group) not in (unicode, str):
            m = 'Group ID is a "{0}", not a string'.format(type(group))
            raise TypeError(m)

        m = 'del_group: Removing {0} ({1}) from {2}'
        msg = m.format(self.getProperty('fn', ''), self.getId(), group)
        log.info(msg)

        acl_users = getattr(self, 'acl_users', None)
        acl_users.delGroupsFromUser([group], self.getId())

    security.declareProtected(Perms.manage_properties,
                                'del_groupWithNotification')

    def del_groupWithNotification(self, group):
        """ Remove a group from the user, and if available, send them a
        notification. """
        # AM: Copy and paste of horrendous code follows.
        from Products.XWFCore.XWFUtils import getOption, get_user, \
            get_user_realnames, get_support_email
        from Products.XWFCore.XWFUtils import get_site_by_id, \
            get_group_by_siteId_and_groupId

        try:
            self.del_group(group)
        except Exception as e:
            log.error(e)
            return 0

        site_root = self.site_root()
        listManagers = site_root.objectValues('XWF Mailing List Manager')
        possible_list_match = re.search('(.*)_member', group)
        groupList = None
        if possible_list_match:
            possible_list_id = possible_list_match.groups()[0]
            for listManager in listManagers:
                try:
                    groupList = listManager.get_list(possible_list_id)
                except:
                    continue

        n_dict = {}
        if groupList:
            siteId = groupList.getProperty('siteId', '')
            site_obj = get_site_by_id(groupList, siteId)
            assert site_obj

            groupId = groupList.getId()
            group_obj = get_group_by_siteId_and_groupId(groupList, siteId,
                                                        groupId)
            assert group_obj

            group_email = groupList.getProperty('mailto', '')
            ptn_coach_id = group_obj.getProperty('ptn_coach_id', '')
            ptn_coach_user = get_user(group_obj, ptn_coach_id)
            ptnCoach = get_user_realnames(ptn_coach_user, ptn_coach_id)
            realLife = group_obj.getProperty('real_life_group', '') \
                            or group_obj.getProperty('membership_defn', '')
            supportEmail = get_support_email(group_obj, siteId)

            n_dict = {
                        'groupId': groupId,
                        'groupName': group_obj.title_or_id(),
                        'siteName': site_obj.title_or_id(),
                        'canonical': getOption(group_obj, 'canonicalHost'),
                        'grp_email': group_email,
                        'ptnCoachId': ptn_coach_id,
                        'ptnCoach': ptnCoach,
                        'realLife': realLife,
                        'supportEmail': supportEmail
                      }
            groupsInfo = createObject('groupserver.GroupsInfo', site_obj)
            groupsInfo.clear_groups_cache()

        try:
            notify = IGSNotifyUser(self)
            notify.send_notification('del_group', group, n_dict)
        except:
            # we really can't do much, because if we fail here, we may
            # cause the person to get an email over and over if they're
            # joining more than one group
            pass

        return 1

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
        retval = GSImage(f).get_cache_name(x, y, maintain_aspect, only_smaller)
        return retval

    security.declareProtected(Perms.manage_properties, 'get_emailAddresses')

    def get_emailAddresses(self):
        """ Returns a list of all the user's email addresses.

            A helper method to purify the list of addresses.

        """
        m = 'CustomUser.get_emailAddresses is deprecated: it should '\
          'never be used. Use '\
          'gs.profile.email.base.emailuser.EmailUser.get_addresses '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)
        raise NotImplemented

    security.declareProtected(Perms.manage_properties,
                                'validate_emailAddresses')

    def validate_emailAddresses(self):
        """ Validate all the user's email addresses.
            Deprecated.
        """
        for email in self.get_emailAddresses():
            self._validateAndNormalizeEmail(email)

    security.declarePrivate('_validateAndNormalizeEmail')

    def _validateAndNormalizeEmail(self, email):
        """ Validates and normalizes an email address.

        """
        m = 'CustomUser._validateAndNormalizeEmail is deprecated: it should '\
          'never be used. Use '\
          'gs.profile.email.base.emailuser.EmailUser._validateAndNormalizeEmail'\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)

        email = email.strip()
        if not email:
            raise ValidationError('No email address given')
        try:
            a = rfc822.AddressList(email)
        except:
            raise ValidationError('Email address was not compliant with rfc822')
        if len(a.addresslist) > 1:
            raise ValidationError('More than one email address was given')
        try:
            email = a.addresslist[0][1]
        except:
            raise ValidationError('Unexpected validation error')

        if not email:
            raise ValidationError('No email address given')

        return email

    security.declareProtected(Perms.manage_properties, 'add_emailAddress')

    def add_emailAddress(self, email, is_preferred=False):
        """ Add an email address to the list of the user's known email
        addresses.

        """
        m = 'CustomUser.add_emailAddress is deprecated: it should '\
          'never be used. Use '\
          'gs.profile.email.base.emailuser.EmailUser.add_address '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)
        raise NotImplemented

    # Email verification methods. Most of these are deprecated and
    # have been moved to gs.profile.email.verify.

    security.declareProtected(Perms.manage_properties,
        'verify_emailAddress')

    def verify_emailAddress(self, verificationId):
        """Verify the email address associated with the verification ID
        """
        m = 'CustomUser.verify_emailAddress is deprecated: it should '\
          'never be used. Use '\
          'gs.profile.email.verify.emailverificationuser.EmailVerificationUser.verify_email '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)

        assert verificationId
        uq = UserQuery(self)
        assert uq.userEmail_verificationId_valid(verificationId), \
          'Invalid verification ID: "%s"' % verificationId

        email = uq.verify_userEmail(verificationId)

        m = u'verify_emailAddress: Verified <%s> for the user %s (%s)' %\
              (email, self.getProperty('fn', ''), self.getId())
        log.info(m)

        assert email
        return email

    def add_emailAddressVerification(self, verificationId, email):
        """Add a verification ID for a particular email address"""
        m = 'CustomUser.add_emailAddressVerification is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.verify.emailverificationuser.EmailVerificationUser.add_verification_id '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)

        assert verificationId
        uq = UserQuery(self)
        assert not uq.userEmail_verificationId_valid(verificationId), \
          'Email Verification ID %s exists' % verificationId
        assert email in self.get_emailAddresses(), \
          'User "%s" does not have the address <%s>' % (self.getId(), email)

        uq.add_userEmail_verificationId(verificationId, email)

        m = u'add_emailAddressVerification: Added the verification ID '\
          u'"%s" for the address <%s> for the user %s (%s)' % \
          (verificationId, email, self.getProperty('fn', ''), self.getId())
        log.info(m)

    def remove_emailAddressVerification(self, email):
        """Remove all entries in the email address verification table
        associated with a particular address"""
        m = 'CustomUser.remove_emailAddressVerification is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.verify.emailverificationuser.EmailVerificationUser.clear_verification_ids '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)

        assert email
        assert email in self.get_emailAddresses(), \
          'User "%s" does not have the address <%s>' % (self.getId(), email)
        uq = UserQuery(self)
        uq.remove_userEmail_verificationId(email)

        m = 'remove_emailAddressVerification: removed email address '\
          'verification data associated with the address <%s> '\
          'for %s (%s)' % (email, self.getProperty('fn', ''), self.getId())
        log.info(m)

    def emailAddress_isVerified(self, email):
        """Check to see if an address is verified."""
        m = 'CustomUser.emailAddress_isVerified is deprecated: it should '\
          'never be used. Use '\
          'gs.profile.email.base.emailuser.EmailUser.is_address_verified '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)
        assert email
        assert email in self.get_emailAddresses(), \
          'User "%s" does not have the address <%s>' % (self.getId(), email)
        uq = UserQuery(self)
        return uq.userEmail_verified(email)

    security.declareProtected(Perms.manage_properties,
        'remove_emailAddress')

    def remove_emailAddress(self, email):
        """ Remove an email address from the list of user's email
        addresses.

        """
        m = 'CustomUser.remove_emailAddress is deprecated: it should '\
          'never be used. Use '\
          'gs.profile.email.base.emailuser.EmailUser.remove_address '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)
        raise NotImplemented

    security.declareProtected(Perms.view,
      'get_verifiedEmailAddresses')

    def get_verifiedEmailAddresses(self):
        """Get the verified email addresses for the user

        ARGUMENTS
          None
        SIDE EFFECTS
          None.
        RETURNS
          A list of email addresses, which have a verification date set.
        """
        m = 'CustomUser.get_verifiedEmailAddresses is deprecated: it should '\
          'never be used. Use '\
          'gs.profile.email.base.emailuser.EmailUser.get_verified_addresses '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)
        raise NotImplemented

    security.declareProtected(Perms.manage_properties,
      'get_preferredEmailAddresses')
    security.declareProtected(Perms.manage_properties,
      'get_defaultDeliveryEmailAddresses')

    def get_defaultDeliveryEmailAddresses(self):
        """ Get the user's default delivery email addresses.

        """
        m = 'CustomUser.get_defaultDeliveryEmailAddresses is deprecated: '\
          'it should never be used. Use '\
          'gs.profile.email.base.emailuser.EmailUser.get_delivery_addresses '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)
        raise NotImplemented

    get_preferredEmailAddresses = get_defaultDeliveryEmailAddresses

    security.declareProtected(Perms.manage_properties,
      'add_defaultDeliveryEmailAddress')

    def add_defaultDeliveryEmailAddress(self, email):
        """ Add an address to the list of addresses to which email will be
            delivered by default.

        """
        m = 'CustomUser.add_defaultDeliveryEmailAddress is deprecated: it should '\
          'never be used. Use '\
          'gs.profile.email.base.emailuser.EmailUser.set_delivery '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)
        raise NotImplemented

    add_preferredEmailAddress = add_defaultDeliveryEmailAddress

    security.declareProtected(Perms.manage_properties,
      'add_defaultDeliveryEmailAddresses')

    def add_defaultDeliveryEmailAddresses(self, addresses):
        """ Set all the addresses to which email will be delivered by default.
            Deprecated.
        """
        uq = UserQuery(self)

        # first clear all the preferredEmailAddresses
        uq.clear_preferredEmail()

        for email in addresses:
            self.add_preferredEmailAddress(email)

    add_preferredEmailAddresses = add_defaultDeliveryEmailAddresses

    security.declareProtected(Perms.manage_properties,
                            'remove_defaultDeliveryEmailAddress')

    def remove_defaultDeliveryEmailAddress(self, email):
        """ Remove an email address from the list of addresses to which
            email will be delivered by default.

        """
        m = 'CustomUser.add_defaultDeliveryEmailAddress is deprecated: it '\
          'should never be used. Use '\
          'gs.profile.email.base.emailuser.EmailUser.drop_delivery '\
          'instead. Called from %s.' % self.REQUEST['PATH_INFO']
        log.debug(m)
        raise NotImplemented

    remove_preferredEmailAddress = remove_defaultDeliveryEmailAddress

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

    security.declareProtected(Perms.manage_properties, 'set_disableDigestByKey')

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
            group_email_addresses = self.get_specificEmailAddressesByKey(key)# TODO: Check email addr
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
        """ Add an email address as a modified delivery option for a specific
        group.

        """
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
        """ Remove an email address as a modified delivery option for a specific
        group.

        """
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

    def reset_password(self):
        """Resets the user password."""
        m = 'CustomUser.reset_password is deprecated: it should ' \
            'never be used. Called from %s' % self.REQUEST['PATH_INFO']
        log.debug(m)

        newPassword = XWFUtils.generate_password(8)
        self.set_password(newPassword)

        return newPassword

    def set_password(self, newPassword, updateCookies=True):
        """Sets the user's password"""
        m = 'CustomUser.set_password is deprecated: it is replaced ' \
            'by gs.profile.password.passworduser.set_password. Called '\
            'from %s' % self.REQUEST['PATH_INFO']
        log.debug(m)

        site_root = self.site_root()
        user = site_root.acl_users.getUser(self.getId())
        roles = user.getRoles()
        domains = user.getDomains()
        userID = user.getId()

        site_root.acl_users.userFolderEditUser(userID, newPassword,
                                               roles, domains)

        if updateCookies:
            logged_in_user = self.REQUEST.AUTHENTICATED_USER.getId()
            if (logged_in_user):
                site_root.cookie_authentication.credentialsChanged(user,
                                                                   userID,
                                                                   newPassword)
        m = 'set_password: Set password for %s (%s)' % \
          (self.getProperty('fn', ''), self.getId())
        log.info(m)

    def add_password_verification(self, verificationId):
        """Adds a verificationId to the password-reset table"""
        m = 'CustomUser.add_password_verification is deprecated: it is '\
            'replaced by ' \
            'gs.profile.password.passworduser.add_password_verification. '\
            'Called from %s' % self.REQUEST['PATH_INFO']
        log.debug(m)

        uq = UserQuery(self)
        uq.set_userPasswordResetVerificationId(verificationId)

    def clear_userPasswordResetVerificationIds(self):
        """Clears verification IDs, for a particular user, from the
           password-reset table"""
        m = 'CustomUser.clear_userPasswordResetVerificationIds is '\
            'deprecated: it is replaced by ' \
            'gs.profile.password.passworduser.clear_password_verification. '\
            'Called from %s' % self.REQUEST['PATH_INFO']
        log.debug(m)

        uq = UserQuery(self)
        uq.clear_userPasswordResetVerificationIds()

        m = u'clear_userPasswordResetVerificationIds: Clearing IDs '\
          'for "%s"' % self.getId()
        log.info(m)

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
            group._delUsers((self.getId(),))
        m = 'clear_groups: Cleared groups from  %s (%s)' %\
          (self.getProperty('fn', ''), self.getId())
        log.info(m)

    def clear_addresses(self):
        for email in self.get_emailAddresses():
            self.remove_emailAddress(email)
        m = 'clear_addresses: Cleared addresses from  %s (%s)' %\
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
    ob.clear_addresses()
    # FIX
    # ob.clear_userPasswordResetVerificationIds()
    ob.clear_nicknames()
    m = u'removedCustomUser: Deleted "%s"' % uid
    log.info(m)

    return


def movedCustomUser(ob, event):
    """A CustomUser was moved.
    """
    if not IObjectRemovedEvent.providedBy(event):
        return
    if not IObjectAddedEvent.providedBy(event):
        removedCustomUser(ob, event)
