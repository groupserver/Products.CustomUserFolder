'''Interface definitions for a GroupServer User'''
from zope.interface import Interface
import zope.component, zope.publisher.interfaces
import zope.viewlet.interfaces, zope.contentprovider.interfaces 
from zope.schema import *

class IGSUserInfo( Interface ):
    """Information about a specific user. The information that is visible
    may be different for different users, depending on the privacy settings
    of the user, the site, and the installation."""

    emailVisibility = Choice(title=u'Email Visibility',
      description=u"Visibility of the user's email addresses",
      values=[u'hidden', u'request', u'visible'])

    def get_id():
        """Get ID
        
        DESCRIPTION
            Gets the ID of the GroupServer user. This ID is unique for
            all users across all sites in the GroupServer instance.
        
        ARGUMENTS
            None.
        
        RETURNS
            The ID of the GroupServer user as a string.
        """

    def get_profile_url():
        """Get Profile URL
        
        DESCRIPTION
            Returns the URL of the user's profile, on the current site.
            
        ARGUMENTS
            None
            
        RETURNS
            The URL of the user's profile, on the current site, as a 
            string.
        """

    def get_names():
        """Get Names
        
        DESCRIPTION
            Gets the names of the GroupServer user.
        
        ARGUMENTS
            None.
        
        RETURNS
            A dictionary consisting of "first", "last" and "display" names,
            with values as strings.
        """
    
    def get_display_name():
        """Get Display Name
        
        DESCRIPTION
            Gets the display-name (nee preferred name) of the user.
            
        ARGUMENTS
            None.
            
        RETURNS
            The user's display name as a string.
        """
    
    def get_image_url():
        """Get Image URL
        
        DESCRIPTION
            Gets the URL of the user's image.
        
        ARGUMENTS
            None.
        
        RETURNS
            The URL of the user's image, as a string.
        """

    
    def get_groups():
        """Get Groups
        
        DESCRIPTION
            Gets the list of groups that the GroupServer user is in.
            However, this list is modified, so only groups that the
            *requesting* user can see are shown. Effectively, this method
            returns an intersection of the groups that user represented by 
            the User Info is in, and the groups that the requesting user
            can see.
        
        ARGUMENTS
            None.
            
        RETURNS
            A list of instances that conform to the IGSGroupInfo interface.
        """
    
    def get_email_address_visibility():
        """Get Email Address Visibility
        
        DESCRIPTION
            Get the visibility of the user's email addresses.
        
        ARGUMENTS
            None.
            
        RETURNS
            A string representing the user's email address visibility.
              * 'hidden':  Visible to only the user.
              * 'request': The requesting user may make a request to see
                  the email address.
              * 'visible': The email address is visible to all logged in
                  members of the site.
        """
    
    def get_all_email_addresses():
        """Get All Email Addresses
        
        DESCRIPTION
            Get all the email addresses that are visible to the requesting
            user.
        
        ARGUMENTS
            None.
        
        RETURNS
            A list of strings.
        """

    def get_preferred_email_addresses():
        """Get Preferred Email Addresses
        
        DESCRIPTION
            Get a list of the all the user's preferred email addresses
            that are visible to the requesting user.
        
        ARGUMENTS
            None.
            
        RETURNS
            A list of strings.
        """
    
    def get_timezone():
        """Get Timezone
        
        DESCRIPTION
            Get the user's preferred timezone
        
        ARGUMENTS
            None
        
        RETURNS
            The user's preferred timezone, as a string.
        """
    
    def get_properties():
        """Get Properties
        
        DESCRIPTION
            Gets a dictionary of all user-properties that are visible to 
            the requesting user.
        
        ARGUMENTS
            None
        
        RETURNS
            A dictionary of {'property': value}.
        """

    def get_property():
        """Get Property
        
        DESCRIPTION
            Get a particular property.
            
        ARGUMENTS
            "property": The property to get, as a string.
            "default": The default value to return.
            
        RETURNS
            The value of the property "property", or "default" if
            "property" is not set. If the requesting user cannot see
            the property then "default" is returned. [--mpj17=--?]
        """

