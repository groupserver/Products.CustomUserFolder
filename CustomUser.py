# Copyright (c) 2003, IOPEN Technologies Ltd.
# Author: richard@iopen.co.nz
#

from AccessControl import ClassSecurityInfo
from AccessControl.User import User
from ZODB import PersistentList
from AccessControl import allow_class
from OFS.Folder import Folder

class CustomUser(User, Folder):
    """ A Custom user, based on the builtin user object.
    
    """
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
    restrictImage = 1
    _properties_def = (
        {'id': 'emailAddresses', 'type': 'lines', 'mode': 'w'},
        {'id': 'preferredEmailAddresses', 'type': 'lines', 'mode': 'w'},
        {'id': 'firstName', 'type': 'string', 'mode': 'w'},
        {'id': 'lastName', 'type': 'string', 'mode': 'w'},
        {'id': 'preferredName', 'type': 'string', 'mode': 'w'},
        {'id': 'honorific', 'type': 'string', 'mode': 'w'},
        {'id': 'nickname', 'type': 'string', 'mode': 'w'},
        {'id': 'biography', 'type': 'text', 'mode': 'w'},
        {'id': 'restrictImage', 'type': 'boolean', 'mode': 'w'},
        {'id': 'title', 'type': 'string', 'mode': 'w'},
        {'id': 'shortName', 'type': 'string', 'mode': 'w'},
        )

    _properties = _properties_def

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
        self._p_changed = 1
                
    def refresh_properties(self):
        """ Refresh the properties from the class definition.

        """
        self._properties = self._properties_def

    #
    # generic user attribute getter/setters
    #
    def get_firstName(self):
        """ Get the user's first name.

        """
        return self.firstName

    def set_firstName(self, first_name):
        """ Set the user's first name.

        """
        self.firstName = first_name.strip()

    def get_lastName(self):
        """ Get the user's last name.

        """
        return self.lastName

    def set_lastName(self, last_name):
        """ Set the user's last name.

        """
        self.lastName = last_name.strip()

    def get_preferredName(self):
        """ Get the user's preferred name.

        """
        return self.preferredName

    def set_preferredName(self, preferred_name):
        """ Set the user's preferred_name.

        """
        self.preferredName = preferred_name.strip()

    def get_honorific(self):
        """ Get the user's honorific.

        """
        return self.honorific

    def set_honorific(self, honorific):
        """ Set the user's honorific.

        """
        self.honorific = honorific.strip()

    def get_nickname(self):
        """ Get the user's nickname.

        """
        return self.nickname

    def set_nickname(self, nickname):
        """ Set the user's nickname.

        """
        self.nickname = nickname.strip()

    def get_biography(self):
        """ Get the user's biography.

        """
        return self.biography

    def set_biography(self, biography):
        """ Set the user's biography.

        """
        self.biography = biography.strip()

    def get_image(self):
        """ Get the URL of the user's image.

        """
        import sys
        from AccessControl import getSecurityManager
        user = getSecurityManager().getUser()

        return None

    def get_emailAddresses(self):
        """ Returns a list of all the user's email addresses.

        """
        return filter(None, self.emailAddresses)
    
    def validate_emailAddresses(self):
        """ Validate all the user's email addresses.

        """
        for email in self.get_emailAddresses():
            self._validateAndNormalizeEmail(email)

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
    
    def add_emailAddress(self, email):
        """ Add an email address to the list of the user's email
        addresses.
        
        """
        email = self._validateAndNormalizeEmail(email)
        email_addresses = self.emailAddresses
        if email not in email_addresses:
            email_addresses.append(email)
        
        self.emailAddresses = email_addresses
        self._p_changed = 1
            
    def remove_emailAddress(self, email):
        """ Remove an email address from the list of user's email
        addresses.
        
        """
        email = self._validateAndNormalizeEmail(email)
        if email in self.get_emailAddresses():
            self.emailAddresses.remove(email)
        if email in self.get_preferredEmailAddresses():
            self.preferredEmailAddresses.remove(email)
        self._p_changed = 1            

    def get_preferredEmailAddresses(self):
        """ Get the user's preferred delivery email address. If none is
        set, it defaults to the first in the list.
        
        """
        if self.preferredEmailAddresses:
            return filter(None, self.preferredEmailAddresses)
        
        #email_addresses = self.get_emailAddresses()
        #if email_addresses:
        #    self.add_preferredEmailAddress(email_addresses[0])
        #    return filter(None, self.preferredEmailAddresses)
        
        return []
    
    def add_preferredEmailAddress(self, email):
        """ Set the user's preferred delivery email address.
        
        """
        email = self._validateAndNormalizeEmail(email)
        if email not in self.preferredEmailAddresses:
            self.preferredEmailAddresses.append(email)
        if email not in self.get_emailAddresses():
            self.add_emailAddress(email)
        self._p_changed = 1

    def add_preferredEmailAddresses(self, addresses):
        """ Set all the preferred delivery email addresses.
        
        """
        # first clear all the preferredEmailAddresses
        self.preferredEmailAddresses = []
        for email in addresses:
            self.add_preferredEmailAddress(email)
        self._p_changed = 1

    def remove_preferredEmailAddress(self, email):
        """ Remove an email address from the list of user's 
        preferred email addresses.
        
        """
        email = self._validateAndNormalizeEmail(email)
        if email in self.get_preferredEmailAddresses():
            self.preferredEmailAddresses.remove(email)            
        self._p_changed = 1
        
    def get_password(self):
        """ Get the user's password.
        
        """
        return self._getPassword()

class ValidationError(Exception):
    """ Raised if an email address is invalid.
    
    """
    
allow_class(ValidationError)

def addCustomUser(self, name, password, roles, domains, groups):
    """ Add a CustomUser to a folder.

    """
    ob = CustomUser(name, password, roles, domains, groups)
    self._setObject(name, ob)
    
#InitializeClass(CustomUser)

#def initialize(context):
#    context.registerClass(
#        CustomUser,
#        permission='Manage users',
#        constructors=(addCustomUser,),
#        )
