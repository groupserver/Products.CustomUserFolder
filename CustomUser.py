# Copyright (c) 2003, IOPEN Technologies Ltd.
# Author: richard@iopen.co.nz
#

from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as Perms
from AccessControl.User import User
from ZODB import PersistentList
from AccessControl import allow_class
from OFS.Folder import Folder

class CustomUser(User, Folder):
    """ A Custom user, based on the builtin user object.
    
    """
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
                
    security.declareProtected(Perms.manage_properties, 'refresh_properties')
    def refresh_properties(self):
        """ Refresh the properties from the class definition.

        """
        self._properties = self._properties_def
    
    security.declareProtected(Perms.view, 'get_image')
    def get_image(self):
        """ Get the URL of the user's image.

        """
        import sys
        from AccessControl import getSecurityManager
        
        contactsimages = getattr(self, 'contactsimages', None)
        if not contactsimages:
            return None
        
        imageurl = None
        for id in ['%s.jpg' % self.getId(),
                       '%s_%s_%s.jpg' % (self.lastName.lower(), self.firstName.lower(), self.getId()),
                       '%s_%s_%s.jpg' % (self.lastName.lower(), self.preferredName.lower(), self.getId())]:
            image = getattr(contactsimages, id.replace(' ', '-'), None)
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
        """ Add an email address to the list of the user's email
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
    def get_preferredEmailAddresses(self):
        """ Get the user's preferred delivery email address. If none is
        set, it defaults to the first in the list.
        
        """
        return list(filter(None, self.preferredEmailAddresses))
    
    security.declareProtected(Perms.manage_properties, 'add_preferredEmailAddress')
    def add_preferredEmailAddress(self, email):
        """ Set the user's preferred delivery email address.
        
        """
        email = self._validateAndNormalizeEmail(email)
        if email not in self.preferredEmailAddresses:
            self.preferredEmailAddresses.append(email)
        if email not in self.get_emailAddresses():
            self.add_emailAddress(email)
        self._p_changed = 1

    security.declareProtected(Perms.manage_properties, 'add_preferredEmailAddresses')
    def add_preferredEmailAddresses(self, addresses):
        """ Set all the preferred delivery email addresses.
        
        """
        # first clear all the preferredEmailAddresses
        self.preferredEmailAddresses = []
        for email in addresses:
            self.add_preferredEmailAddress(email)
        self._p_changed = 1

    security.declareProtected(Perms.manage_properties, 'remove_preferredEmailAddress')
    def remove_preferredEmailAddress(self, email):
        """ Remove an email address from the list of user's 
        preferred email addresses.
        
        """
        email = self._validateAndNormalizeEmail(email)
        preferredEmailAddresses = self.get_preferredEmailAddresses()
        if email in preferredEmailAddresses:
            preferredEmailAddresses.remove(email)
            self.preferredEmailAddresses = preferredEmailAddresses
        self._p_changed = 1
        
    security.declareProtected(Perms.manage_properties, 'get_password')
    def get_password(self):
        """ Get the user's password. Note, if the password is encrypted,
        this won't be of much use.
        
        """
        return self._getPassword()

class ValidationError(Exception):
    """ Raised if an email address is invalid.
    
    """
    
allow_class(ValidationError)

def addCustomUser(self, name, password, roles, domains):
    """ Add a CustomUser to a folder.

    """
    ob = CustomUser(name, password, roles, domains)
    self._setObject(name, ob)
    
