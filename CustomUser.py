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
from ZODB import PersistentList
from AccessControl import allow_class
from OFS.Folder import Folder
from Products.XWFCore import XWFUtils

class CustomUser(User, Folder):
    """ A Custom user, based on the builtin user object.
    
    """
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

    def send_notification(self, n_type, n_id):
        """ Send a notification to the user based on the type and ID of the
            notification.

        """
        site_root = self.site_root()
        presentation = self.Templates.email.notifications
                
        ptype_templates = getattr(presentation, n_type, None)
        if not ptype_templates:
            return None
        
        template = (getattr(ptype_templates, n_id, None) or
                    getattr(ptype_templates, 'default', None))
        if not template:
            return None
        
        try:
            mailhost = site_root.superValues('Mail Host')[0]
        except:
            raise AttributeError, "Can't find a Mail Host object"
        
        email_addresses = self.get_defaultDeliveryEmailAddresses()
        
        email_strings = []
        for email_address in email_addresses:
            email_strings.append(
                template(self, self.REQUEST,
                         to_addr=email_address,
                         n_id=n_id,
                         n_type=n_type))
                
        for email_string in email_strings:
            mailhost.send(email_string)
        
        return 1

    security.declareProtected(Perms.manage_properties, 'add_groupWithNotification')
    def add_groupWithNotification(self, group):
        """ Add a group to the user, and if available, send them a notification.
        
        """
        acl_users = getattr(self, 'acl_users', None)
        
        if acl_users:
            try:
                acl_users.addGroupsToUser([group], self.getId())
            except:
                return 0                
  
        self.send_notification('add_group', group)

        return 1

    security.declareProtected(Perms.manage_properties, 'del_groupWithNotification')
    def del_groupWithNotification(self, group):
        """ Add a group to the user, and if available, send them a notification.
        
        """
        acl_users = getattr(self, 'acl_users', None)
        site_root = self.site_root()

        if acl_users:
            try:
                acl_users.delGroupsFromUser([group], self.getId())
            except:
                return 0                
  
        self.send_notification('del_group', group)
        
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
        import sys, string
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
                       '%s_%s_%s.jpg' % (lname, fname, self.getId()),
                       '%s_%s_%s.jpg' % (lname, pname, self.getId())]:
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
        return list(filter(None, self.emailAddresses))

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
        email = self._validateAndNormalizeEmail(email)
        email_addresses = self.get_emailAddresses()
        if email not in email_addresses:
            email_addresses.append(email)
        
        self.emailAddresses = email_addresses
        self._p_changed = 1
        
    security.declareProtected(Perms.manage_properties, 'remove_emailAddress')
    def remove_emailAddress(self, email):
        """ Remove an email address from the list of user's email
        addresses.
        
        """
        email = self._validateAndNormalizeEmail(email)
        emailAddresses = self.get_emailAddresses()
        if email in emailAddresses:
            emailAddresses.remove(email)
            self.emailAddresses = emailAddresses
        preferredEmailAddresses = self.get_preferredEmailAddresses()
        if email in preferredEmailAddresses:
            preferredEmailAddresses.remove(email)
            self.preferredEmailAddresses = preferredEmailAddresses
        self._p_changed = 1

    security.declareProtected(Perms.manage_properties, 'get_preferredEmailAddresses')
    def get_defaultDeliveryEmailAddresses(self):
        """ Get the user's default delivery email addresses.
        
        """
        return list(filter(None, self.preferredEmailAddresses))
    
    get_preferredEmailAddresses = get_defaultDeliveryEmailAddresses
    
    security.declareProtected(Perms.manage_properties, 'add_defaultDeliveryEmailAddress')
    def add_defaultDeliveryEmailAddress(self, email):
        """ Add an address to the list of addresses to which email will be delivered
            by default.
        
        """
        email = self._validateAndNormalizeEmail(email)
        
        email_addresses = self.get_preferredEmailAddresses()
        if email not in email_addresses:
            email_addresses.append(email)
            
        self.preferredEmailAddresses = email_addresses
        
        if email not in self.get_emailAddresses():
            self.add_emailAddress(email)
        
        self._p_changed = 1

    add_preferredEmailAddress = add_defaultDeliveryEmailAddress
        
    security.declareProtected(Perms.manage_properties, 'add_defaultDeliveryEmailAddresses')
    def add_defaultDeliveryEmailAddresses(self, addresses):
        """ Set all the addresses to which email will be delivered by default.
        
        """
        # first clear all the preferredEmailAddresses
        self.preferredEmailAddresses = []
        for email in addresses:
            self.add_preferredEmailAddress(email)
        self._p_changed = 1
    
    add_preferredEmailAddresses = add_defaultDeliveryEmailAddresses
    
    security.declareProtected(Perms.manage_properties, 'remove_defaultDeliveryEmailAddress')
    def remove_defaultDeliveryEmailAddress(self, email):
        """ Remove an email address from the list of addresses to which email will
            be delivered by default.
        
        """
        email = self._validateAndNormalizeEmail(email)
        preferredEmailAddresses = self.get_preferredEmailAddresses()
        if email in preferredEmailAddresses:
            preferredEmailAddresses.remove(email)
            self.preferredEmailAddresses = preferredEmailAddresses
        self._p_changed = 1
    
    remove_preferredEmailAddress = remove_defaultDeliveryEmailAddress
    
    security.declareProtected(Perms.manage_properties, 'set_disableDeliveryByKey')
    def set_disableDeliveryByKey(self, key):
        """ Disable the email delivery for a given key.
        
            The key normally represents a group, but may
            represent something else in the future.
        
        """
        disabled_property = '%s_deliveryDisabled' % key
        if self.hasProperty(disabled_property):
            self.manage_changeProperties({disabled_property: 1})
	else:
	    self.manage_addProperty(disabled_property, 1, 'boolean')
        
    security.declareProtected(Perms.manage_properties, 'set_enableDeliveryByKey')
    def set_enableDeliveryByKey(self, key):
        """ Enable the email delivery for a given key.
        
            The key normally represents a group, but may
            represent something else in the future.
            
        """
        disabled_property = '%s_deliveryDisabled' % key
        # we don't create the property if it doesn't exist
        if self.hasProperty(disabled_property):
            self.manage_changeProperties({disabled_property: 0})
    
    security.declareProtected(Perms.manage_properties, 'set_enableDigestByKey')
    def set_enableDigestByKey(self, key):
        """ Enable the email digest for a given key.
        
            The key normally represents a group, but may
            represent something else in the future.
            
        """
        digest_property = '%s_digest' % key
        if self.hasProperty(digest_property):
            self.manage_changeProperties({digest_property: 1})
        else:
	    self.manage_addProperty(digest_property, 1, 'boolean')
    
    security.declareProtected(Perms.manage_properties, 'set_disableDigestByKey')
    def set_disableDigestByKey(self, key):
        """ Disable the email digest for a given key.
        
            The key normally represents a group, but may
            represent something else in the future.
            
        """
        digest_property = '%s_digest' % key
        # we don't create the property if it doesn't exist
        if self.hasProperty(digest_property):
            self.manage_changeProperties({digest_property: 0})
    
    security.declareProtected(Perms.manage_properties, 'get_deliverSettingsByKey')
    def get_deliverySettingsByKey(self, key):
        """ Get the settings for the given key.
        
            returns 1 if default, 2 if non-default, 3 if digest,
	            or 0 if disabled.
        """
        disabled_property = '%s_deliveryDisabled' % key
        preferred_property = '%s_emailAddresses' % key
	digest_property = '%s_digest' % key
        if self.getProperty(disabled_property, 0):
            return 0
	elif self.getProperty(digest_property, 0):
	    return 3
        elif filter(None, self.getProperty(preferred_property, [])):
            return 2
        else:
            return 1
    
    security.declareProtected(Perms.manage_properties, 'get_deliveryEmailAddressesByKey')
    def get_deliveryEmailAddressesByKey(self, key):
        """ Get the user's preferred delivery email address. If none is
        set, it defaults to the first in the list.
        
        """
        preferred_property = '%s_emailAddresses' % key
        disabled_property = '%s_deliveryDisabled' % key
        # first check to see if delivery has been disabled for that group
        if self.getProperty(disabled_property, 0):
            return []
        
        # next check to see if we've customised the delivery options for that group
        group_email_addresses = list(filter(None,
                                            self.getProperty(preferred_property, [])))
        if group_email_addresses:
            return group_email_addresses
        
        # finally, return the default settings
        return list(filter(None, self.preferredEmailAddresses))
    
    security.declareProtected(Perms.manage_properties, 'add_deliveryEmailAddressByKey')
    def add_deliveryEmailAddressByKey(self, key, email):
        """ Add an email address as a modified delivery option for a specific
        group.
        
        """
        email = self._validateAndNormalizeEmail(email)
        property = '%s_emailAddresses' % key
        if not self.hasProperty(property):
            self.manage_addProperty(property, '', 'ulines')
        
        email_addresses = list(self.getProperty(property, []))
        email_addresses.append(email)
        
        self.manage_changeProperties({property: email_addresses})
    
    security.declareProtected(Perms.manage_properties, 'remove_deliveryEmailAddressByKey')
    def remove_deliveryEmailAddressByKey(self, key, email):
        """ Remove an email address as a modified delivery option for a specific
        group.
        
        """
        email = self._validateAndNormalizeEmail(email)
        property = '%s_emailAddresses' % key
        
        email_addresses = list(self.getProperty(property, []))
        if email in email_addresses:
            email_addresses.remove(email)
        # if we have email addresses still, update the property
        if email_addresses:
            self.manage_changeProperties({property: email_addresses})
        # otherwise remove the property entirely
        else:
            self.manage_delProperties([property])
                
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
            acl_users.delGroupsFromUser(['unverified_member'], self.getId())
        
        if not verification_code == self.get_verificationCode():
            return 0
        
        for group in self.get_verificationGroups():
            self.add_groupWithNotification(group)

        return 1
   
    security.declareProtected(Perms.manage_properties, 'send_userVerification')
    def send_userVerification(self):
        """ Send the user a verification email.
        
        """
        presentation = self.Templates.email
        site_root = self.site_root()
                
        try:
            mailhost = site_root.superValues('Mail Host')[0]
        except:
            raise AttributeError, "Can't find a Mail Host object"
        
        email_addresses = self.get_emailAddresses()
        email_strings = []
        for email_address in email_addresses:
            email_strings.append(
                presentation.confirm_registration(self,
                                                  self.REQUEST,
                                                  to_addr=email_address,
                                                  verification_code=self.get_verificationCode(),
                                                  first_name=self.getProperty('firstName', ''),
                                                  last_name=self.getProperty('lastName', ''),
                                                  user_id=self.getId(),
                                                  password=self.get_password()))
        
        for email_string in email_strings:
            mailhost.send(email_string)
        
        return email_strings
    
    security.declareProtected(Perms.manage_properties, 'get_password')
    def get_password(self):
        """ Get the user's password. Note, if the password is encrypted,
        this won't be of much use.
        
        """
        return self._getPassword()

    #
    # Views and Workflow
    #
    def index_html(self):
        """ Return the default view.

        """
        try:
            presentation = getattr(self, 'userinfo.xml')
        except:
            presentation = getattr(self, 'index_html')
        return presentation()

class ValidationError(Exception):
    """ Raised if an email address is invalid.
    
    """
    
allow_class(ValidationError)

def addCustomUser(self, name, password, roles, domains):
    """ Add a CustomUser to a folder.

    """
    ob = CustomUser(name, password, roles, domains)
    self._setObject(name, ob)
    
