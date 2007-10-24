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
from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as Perms
from AccessControl.User import User
from AccessControl import allow_class

from queries import UserQuery

from OFS.Folder import Folder
from Products.XWFCore import XWFUtils

from Globals import InitializeClass
import string

from zope.interface import implements
from Products.CustomUserFolder.interfaces import ICustomUser

class CustomUser(User, Folder):
    """ A Custom user, based on the builtin user object.
    
    """
    implements(ICustomUser)

    version = 1.9
    
    security = ClassSecurityInfo()
    
    meta_type = "Custom User"
        
    emailAddresses = []
    preferredEmailAddresses = []
    firstName = ''
    lastName = ''
    preferredName = ''
    honorific = ''
    nickname = ''
    biography = ''
    title = ''
    shortName = ''
    currentDivision = ''
    restrictImage = 1
    unrestrictedImageRoles = []
    _properties_def = (
        {'id': 'emailAddresses', 'type': 'lines', 'mode': 'w'},
        {'id': 'preferredEmailAddresses', 'type': 'lines', 'mode': 'w'},
        {'id': 'unrestrictedImageRoles', 'type': 'lines', 'mode': 'w'},
        {'id': 'firstName', 'type': 'string', 'mode': 'w'},
        {'id': 'lastName', 'type': 'string', 'mode': 'w'},
        {'id': 'preferredName', 'type': 'string', 'mode': 'w'},
        {'id': 'honorific', 'type': 'string', 'mode': 'w'},
        {'id': 'nickname', 'type': 'string', 'mode': 'w'},
        {'id': 'biography', 'type': 'text', 'mode': 'w'},
        {'id': 'restrictImage', 'type': 'boolean', 'mode': 'w'},
        {'id': 'title', 'type': 'string', 'mode': 'w'},
        {'id': 'shortName', 'type': 'string', 'mode': 'w'},
        {'id': 'currentDivision', 'type': 'string', 'mode': 'w'},    
        )

    _properties = _properties_def
    
    security.declarePrivate('init_properties')
    def init_properties(self):
        self.emailAddresses = []
        self.preferredEmailAddresses = []
        self.firstName = ''
        self.lastName = ''
        self.preferredName = ''
        self.honorific = ''
        self.nickname = ''
        self.biography = ''
        self.title = ''
        self.shortName = ''
        self.restrictImage = 1
        self.currentDivision = ''
        self.unrestrictedImageRoles = []
        self._p_changed = 1

    def send_notification(self, n_type, n_id, n_dict=None, email_only=()):
        """ Send a notification to the user based on the type and ID of the
            notification.

            An optional dictionary of values may be passed to the template.

        """
        site_root = self.site_root()
        presentation = site_root.Templates.email.notifications.aq_explicit
        
        ptype_templates = getattr(presentation, n_type, None)
        if not ptype_templates:
            return None

        if not n_dict:
            n_dict = {}

        # AM: This is a dreadful hack to prevent the add_group notification
        #   from being sent when the "group" joined is a site
        ignore_ids = getattr(ptype_templates, 'ignore_ids', [])
        if n_id in ignore_ids:
            return None        

        template = (getattr(ptype_templates.aq_explicit, n_id, None) or
                    getattr(ptype_templates.aq_explicit, 'default', None))
        if not template:
            return None
        
        try:
            mailhost = site_root.superValues('Mail Host')[0]
        except:
            raise AttributeError, "Can't find a Mail Host object"

        email_addresses = []
        if email_only:
            # make sure the email address are really addresses of our user
            email_only = map(lambda x: x.lower(), email_only)
            for email in self.get_emailAddresses():
                if email.lower() in email_only:
                    email_addresses.append(email)
        else:
            email_addresses = self.get_emailAddresses()
        
        email_strings = []
        for email_address in email_addresses:
            email_strings.append(
                template(self, self.REQUEST,
                         to_addr=email_address,
                         n_id=n_id,
                         n_type=n_type,
                         n_dict=n_dict))
         
        for email_string in email_strings:
            support_email = XWFUtils.getOption(self, 'supportEmail')
            if not support_email:
                raise AttributeError, "supportEmail was not defined in configuration"
            mailhost._send(mfrom=support_email,
                           mto=email_addresses[email_strings.index(email_string)],
                           messageText=email_string)
        
        return 1

    security.declareProtected(Perms.manage_properties, 'add_groupWithNotification')
    def add_groupWithNotification(self, group):
        """ Add a group to the user, and if available, send them a notification.
        
        """
        import re
         
        acl_users = getattr(self, 'acl_users', None)
        site_root = self.site_root()        
        context = self.context

        if acl_users:
            try:
                acl_users.addGroupsToUser([group], self.getId())
            except:
                return 0                
        
        listManagers = site_root.objectValues('XWF Mailing List Manager')
        possible_list_match = re.search('(.*)_member', group)
        group_email = ''
        if possible_list_match:
            possible_list_id = possible_list_match.groups()[0]
            for listManager in listManagers:
                try:
                    groupList = listManager.get_list(possible_list_id)
                except:
                    continue
                group_email = groupList.getProperty('mailto', '')
                if not groupList.getProperty('moderate_new_members', False):
                    continue
                if groupList.hasProperty('moderated_members'):
                    moderated_members = list(groupList.getProperty('moderated_members', []))
                    if self.getId() not in moderated_members:
                        moderated_members.append(self.getId())
                        groupList.manage_changeProperties(moderated_members=moderated_members)
                else:
                    moderated_members = [self.getId()]
                    groupList.manage_addProperty('moderated_members',
                                                  moderated_members, 'lines')

        group_obj = context.Scripts.get.group_by_id(group.split('_member')[0])
        ptn_coach_id = group_obj.getProperty('ptn_coach_id','')

        n_dict = {  group     : group_obj,
                    groupName : group_obj.title_or_id(),
                    groupId   : group_obj.getId(),
                    siteName  : group_obj.Scripts.get.division_object().title_or_id(),
                    canonical : group_obj.Scripts.get.option('canonicalHost'),
                    grp_email : group_email,
                    ptnCoachId: ptn_coach_id,
                    ptnCoach  : ptn_coach_id and context.Scripts.get.user_realnames(ptn_coach_id),
                    realLife  : group_obj.getProperty('real_life_group','') or group_obj.getProperty('membership_defn','')
                  }

        try:
            self.send_notification('add_group', group, n_dict)
        except:
            # we really can't do much, because if we fail here, we may
            # cause the person to get an email over and over if they're
            # joining more than one group
            pass
        
        return 1

    security.declareProtected(Perms.manage_properties, 'del_groupWithNotification')
    def del_groupWithNotification(self, group):
        """ Remove a group from the user, and if available, send them a notification.
        
        """
        acl_users = getattr(self, 'acl_users', None)

        if acl_users:
            try:
                acl_users.delGroupsFromUser([group], self.getId())
            except:
                return 0                

        try:
            self.send_notification('del_group', group)
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
        
    security.declareProtected(Perms.view, 'get_image')
    def get_image(self):
        """ Get the URL of the user's image.

        """
        from AccessControl import getSecurityManager
        
        contactsimages = getattr(self, 'contactsimages', None)
        if not contactsimages:
            return None
        fname = self.firstName.lower()
        lname = self.lastName.lower()
        pname = self.preferredName.lower()
        valid_chars = string.letters+string.digits+'_.'
        imageurl = None
        for id in ['%s.jpg' % self.getId(),
                    '%s_%s_%s.jpg' % (lname, fname, self.getId())]:
            newid = ''
            for char in id:
                if char in valid_chars:
                    newid += char
                else:
                    newid += '-'
            image = getattr(contactsimages, newid, None)
            
            if image:
                imageurl = image.absolute_url(1)
                break
        
        # if we don't have an image, shortcut the checks
        if not imageurl: return None
        
        # check to see if we have a global override
        globalconfig = getattr(self, 'GlobalConfiguration', None)
        if globalconfig:
            if getattr(globalconfig, 'alwaysShowMemberPhotos'):
                return imageurl
        
        user = getSecurityManager().getUser()
        roles = user.getRoles()
        allowbyrole = 0
        for role in roles:
            if role in self.unrestrictedImageRoles:
                allowbyrole = 1
                break
                
        imageurl = None
        if self.restrictImage and (not allowbyrole) and \
           user.getId() != self.getId():
            return imageurl
            
        return imageurl
        
    security.declareProtected(Perms.manage_properties, 'get_emailAddresses')    
    def get_emailAddresses(self):
        """ Returns a list of all the user's email addresses.
        
            A helper method to purify the list of addresses.
            
        """
        uq = UserQuery(self, self.zsqlalchemy)
        
        return uq.get_userEmail(preferred_only=False)

    security.declareProtected(Perms.manage_properties, 'validate_emailAddresses')
    def validate_emailAddresses(self):
        """ Validate all the user's email addresses.
            
        """
        for email in self.get_emailAddresses():
            self._validateAndNormalizeEmail(email)

    security.declarePrivate('_validateAndNormalizeEmail')
    def _validateAndNormalizeEmail(self, email):
        """ Validates and normalizes an email address.
            
        """
        import rfc822
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
    def add_emailAddress(self, email):
        """ Add an email address to the list of the user's known email
        addresses.
        
        """
        uq = UserQuery(self, self.zsqlalchemy)

        email = self._validateAndNormalizeEmail(email)
        
        uq.add_userEmail(email)        
            
    security.declareProtected(Perms.manage_properties, 'remove_emailAddress')
    def remove_emailAddress(self, email):
        """ Remove an email address from the list of user's email
        addresses.
        
        """
        uq = UserQuery(self, self.zsqlalchemy)

        email = self._validateAndNormalizeEmail(email)

        uq.remove_userEmail(email)        
    
    security.declareProtected(Perms.manage_properties, 'get_preferredEmailAddresses')
    security.declareProtected(Perms.manage_properties, 'get_defaultDeliveryEmailAddresses')
    def get_defaultDeliveryEmailAddresses(self):
        """ Get the user's default delivery email addresses.
        
        """
        uq = UserQuery(self, self.zsqlalchemy)
        
        return uq.get_userEmail(preferred_only=True)        
    
    get_preferredEmailAddresses = get_defaultDeliveryEmailAddresses
    
    security.declareProtected(Perms.manage_properties, 'add_defaultDeliveryEmailAddress')
    def add_defaultDeliveryEmailAddress(self, email):
        """ Add an address to the list of addresses to which email will be
            delivered by default.
        
        """
        email = self._validateAndNormalizeEmail(email)

        uq = UserQuery(self, self.zsqlalchemy)
        
        user_email = uq.get_userEmail(preferred_only=False)
    
        # if we don't have the email address in the database yet, add it
        # and set it as preferred
        if email not in user_email:
            uq.add_userEmail(email, is_preferred=True)
        
        # otherwise just set it as preferred
        else:
            uq.set_preferredEmail(email, is_preferred=True)

    add_preferredEmailAddress = add_defaultDeliveryEmailAddress
        
    security.declareProtected(Perms.manage_properties, 'add_defaultDeliveryEmailAddresses')
    def add_defaultDeliveryEmailAddresses(self, addresses):
        """ Set all the addresses to which email will be delivered by default.
        
        """
        uq = UserQuery(self, self.zsqlalchemy)

        # first clear all the preferredEmailAddresses
        uq.clear_preferredEmail()
        
        for email in addresses:
            self.add_preferredEmailAddress(email)
            
    add_preferredEmailAddresses = add_defaultDeliveryEmailAddresses
    
    security.declareProtected(Perms.manage_properties, 'remove_defaultDeliveryEmailAddress')
    def remove_defaultDeliveryEmailAddress(self, email):
        """ Remove an email address from the list of addresses to which
            email will be delivered by default.
        
        """
        uq = UserQuery(self, self.zsqlalchemy)

        email = self._validateAndNormalizeEmail(email)

        uq.set_preferredEmail(email, is_preferred=False)        
            
    remove_preferredEmailAddress = remove_defaultDeliveryEmailAddress
    
    security.declareProtected(Perms.manage_properties, 'set_disableDeliveryByKey')
    def set_disableDeliveryByKey(self, key):
        """ Disable the email delivery for a given key.
        
            The key normally represents a group, but may
            represent something else in the future.
        
        """
        uq = UserQuery(self, self.zsqlalchemy)
        # TODO: we don't quite support site_id yet
        site_id = ''
        group_id = key
        uq.set_groupEmailSetting(site_id, group_id, 'webonly')
                
    security.declareProtected(Perms.manage_properties, 'set_enableDeliveryByKey')
    def set_enableDeliveryByKey(self, key):
        """ Enable the email delivery for a given key.
        
            The key normally represents a group, but may
            represent something else in the future.
            
        """
        uq = UserQuery(self, self.zsqlalchemy)
        # TODO: we don't quite support site_id yet
        site_id = ''
        group_id = key
        uq.clear_groupEmailSetting(site_id, group_id)
        #uq.set_groupEmailSetting(site_id, group_id, '')
        
    security.declareProtected(Perms.manage_properties, 'set_enableDigestByKey')
    def set_enableDigestByKey(self, key):
        """ Enable the email digest for a given key.
        
            The key normally represents a group, but may
            represent something else in the future.
            
        """
        uq = UserQuery(self, self.zsqlalchemy)
        # TODO: we don't quite support site_id yet
        site_id = ''
        group_id = key
        uq.set_groupEmailSetting(site_id, group_id, 'digest')
        
    security.declareProtected(Perms.manage_properties, 'set_disableDigestByKey')
    def set_disableDigestByKey(self, key):
        """ Disable the email digest for a given key.
        
            The key normally represents a group, but may
            represent something else in the future.
            
        """
        uq = UserQuery(self, self.zsqlalchemy)
        # TODO: we don't quite support site_id yet
        site_id = ''
        group_id = key
        uq.clear_groupEmailSetting(site_id, group_id)
        #uq.set_groupEmailSetting(site_id, group_id, '')
    
    security.declareProtected(Perms.manage_properties, 'get_deliverySettingsByKey')
    def get_deliverySettingsByKey(self, key):
        """ Get the settings for the given key.
        
            returns 1 if default, 2 if non-default, 3 if digest,
	            or 0 if disabled.
        """
        uq = UserQuery(self, self.zsqlalchemy)

        # TODO: we don't quite support site_id yet
        site_id = ''
        group_id = key

        setting = uq.get_groupEmailSetting(site_id, group_id)
        
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
            group_email_addresses = self.get_specificEmailAddressesByKey(key)
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
        retval = []
        
        uq = UserQuery(self, self.zsqlalchemy)
        retval = uq.get_groupUserEmail(site_id, group_id)
        
        return retval
        
    security.declareProtected(Perms.manage_properties, 'add_deliveryEmailAddressByKey')
    def add_deliveryEmailAddressByKey(self, key, email):
        """ Add an email address as a modified delivery option for a specific
        group.
        
        """
        uq = UserQuery(self, self.zsqlalchemy)
        email = self._validateAndNormalizeEmail(email)

        # TODO: we don't support site_id
        site_id = ''
        group_id = key
        
        if email not in uq.get_groupUserEmail(site_id, group_id):
            uq.add_groupUserEmail(site_id, group_id, email)
            
    security.declareProtected(Perms.manage_properties, 'remove_deliveryEmailAddressByKey')
    def remove_deliveryEmailAddressByKey(self, key, email):
        """ Remove an email address as a modified delivery option for a specific
        group.
        
        """
        uq = UserQuery(self, self.zsqlalchemy)
        email = self._validateAndNormalizeEmail(email)

        # TODO: we don't support site_id
        site_id = ''
        group_id = key
        
        uq.remove_groupUserEmail(site_id, group_id, email)

        email_addresses = uq.get_groupUserEmail(site_id, group_id)
                        
    security.declareProtected(Perms.manage_properties, 'set_verificationCode')
    def set_verificationCode(self):
        """ Set the methods that will be called on the user post verification.
        
        """
        vc = XWFUtils.generate_accesscode(self.getId())
        self._verificationCode = vc
        
        return vc
        
    security.declareProtected(Perms.manage_properties, 'get_verificationCode')
    def get_verificationCode(self):
        """ Get the methods that will be called on the user post verification.
        
        """
        return getattr(self, '_verificationCode', None)
            
    security.declareProtected(Perms.manage_properties, 'set_verificationGroups')
    def set_verificationGroups(self, groups):
        """ Set the groups that user will be assigned to post verification.
        
        """
        self._verificationGroups = groups
        
        return 1
    
    security.declareProtected(Perms.manage_properties, 'get_verificationGroups')
    def get_verificationGroups(self):
        """ Get the groups that the user will be assigned to post verification.
        
        """
        return getattr(self, '_verificationGroups', ())

    security.declareProtected(Perms.manage_properties, 'verify_user')
    def verify_user(self, verification_code):
        """ Verify the user, and if they verify, set the post verification
            groups.

        """
        acl_users = getattr(self, 'acl_users', None)
        if acl_users:
            try:
                acl_users.delGroupsFromUser(['unverified_member'], self.getId())
            except:
                pass
            
        if not verification_code == self.get_verificationCode():
            return 0
        
        for group in self.get_verificationGroups():
            self.add_groupWithNotification(group)

        return 1
   
    security.declareProtected(Perms.manage_properties, 'send_userVerification')
    def send_userVerification(self, password='', site='', n_id='default'):
        """ Send the user a verification email.
        
        """
        site_root = self.site_root()
        presentation = site_root.Templates.email.notifications.aq_explicit
                
        p_templates = getattr(presentation, 'confirm_registration', None)
        if not p_templates:
            raise AttributeError, "Can't find a confirm_registration template"

        template = getattr(p_templates.aq_explicit, n_id, None)
        if not template:
            raise AttributeError, "Unable to find confirm_registration/%s" % n_id 
            
        try:
            mailhost = site_root.superValues('Mail Host')[0]
        except:
            raise AttributeError, "Can't find a Mail Host object"
        
        email_addresses = self.get_emailAddresses()
        email_strings = []
        for email_address in email_addresses:
            email_strings.append(
                template(self,
                         self.REQUEST,
                         site=site,
                         to_addr=email_address,
                         verification_code=self.get_verificationCode(),
                         first_name=self.getProperty('firstName', ''),
                         last_name=self.getProperty('lastName', ''),
                         user_id=self.getId(),
                         password=password))
        
        for email_string in email_strings:
            verification_email = XWFUtils.getOption(self, 'userVerificationEmail')
            if not verification_email:
                raise AttributeError, "userVerificationEmail was not defined in configuration"
            
            mailhost._send(mfrom=verification_email,
                           mto=email_addresses[email_strings.index(email_string)],
                           messageText=email_string)
        
        return email_strings
    
    security.declareProtected(Perms.manage_properties, 'get_password')
    def get_password(self):
        """ Get the user's password. Note, if the password is encrypted,
        this won't be of much use.
        
        RETURNS
          The password in clear-text.
        """
        return self._getPassword()

    def reset_password(self):
        """Resets the user password. This should be called when the
        user forgets the password.

        SIDE-EFFECTS
           Changes the password by calling "self.set_password".

        RETURNS
           The newly created password."""

        newPassword = XWFUtils.generate_password(8)
        self.set_password(newPassword)

        return newPassword

    def set_password(self, newPassword):
        """Sets the user's password to 'newPassword'.

        SIDE-EFFECTS
          Changes the user-information in 'site_root.acl_users' and
          'site_root.cookie_authentication'.

        RETURNS
          None."""

        site_root = self.site_root()	
        user =  site_root.acl_users.getUser(self.getId())
        roles = user.getRoles()
        domains = user.getDomains()
        userID = user.getId()

        site_root.acl_users.userFolderEditUser(userID, newPassword,
                                               roles, domains)

	logged_in_user = self.REQUEST.AUTHENTICATED_USER.getId() 
	if (logged_in_user):
	        site_root.cookie_authentication.credentialsChanged(user, userID,
        	                                                   newPassword)
		
    #
    # Views and Workflow
    #
    def index_html(self):
        """ Return the default view.

        """
        return self.REQUEST.RESPONSE.redirect(self.absolute_url()+'/'+'userinfo.xml')

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
    ob.id = ob.getId() # make sure we have an actual ID
    self._setObject(name, ob)
    
def removedCustomUser(ob, event):
    """ A CustomUser was removed.

    """
    for email in ob.get_emailAddresses():
        ob.remove_emailAddress(email)
    return
    
from zope.app.container.interfaces import IObjectRemovedEvent,IObjectAddedEvent
def movedCustomUser(ob, event):
    """A CustomUser was moved. 
    """
    if not IObjectRemovedEvent.providedBy(event):
        return
    if not IObjectAddedEvent.providedBy(event):
        removedCustomUser(ob, event)

