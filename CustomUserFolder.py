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
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl import AuthEncoding
from AccessControl import Permissions as Perms
from AccessControl.User import BasicUserFolder, _remote_user_mode
from Globals import InitializeClass
from OFS.Folder import Folder
from Products.NuxUserGroups import UserFolderWithGroups
from Products.XWFCore import XWFUtils

import DateTime

import sqlalchemy as sa

try:
    from Products.MailBoxer import MailBoxerTools
    HaveMailBoxer = True
except:
    HaveMailBoxer = False

class CustomUserFolder(UserFolderWithGroups):
    """ A user folder for CampusUser users, based on the NuxUserGroup UserFolder
    interface.
    
    """
    security = ClassSecurityInfo()
    
    meta_type = "Custom User Folder"
    id = 'acl_users'
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
        return AuthEncoding.pw_encrypt(pw, 'SHA')
        
    security.declarePrivate('_getUserFolder')
    def _getUserFolder(self):
        """ Return the folder object that contains the user objects,  or None.
        
        """
        return getattr(self, self.user_folder_id, None)


    security.declareProtected(Perms.manage_users, 'get_userIdByEmail')
    def get_userIdByEmail(self, email):
        """ Get a user ID by email address.
        
        """
        email = email.lower()
        da = self.zsqlalchemy
        userEmailTable = da.createMapper('user_email')[1]
        
        statement = userEmailTable.select()      
        statement.append_whereclause(userEmailTable.c.email.op('ILIKE')(email))
        
        r = statement.execute().fetchone()
        if r:
            return r['user_id']

        return None
        
    security.declareProtected(Perms.manage_users, 'get_userIdByEmailVerificationId')
    def get_userIdByEmailVerificationId(self, verificationId):
        """Get the user ID from a email-verification ID
        """
        da = self.zsqlalchemy
        uet = da.createMapper('user_email')[1]
        evt = da.createMapper('email_verification')[1]
        
        s1 = evt.select()
        s1.append_whereclause(evt.c.verification_id == verificationId)
        r1 = s1.execute().fetchone()
        
        retval = ''
        if r1:
            email = r1['email']
            s2 = uet.select()
            s2.append_whereclause(uet.c.email.op('ILIKE')(email))
            r2 = s2.execute().fetchone()
            if r2:
                return r2['user_id']
        assert type(retval) == str
        return retval
        
    security.declareProtected(Perms.manage_users, 'get_userByEmailVerificationId')
    def get_userByEmailVerificationId(self, verificationId):
        """ Get the user by verification ID
        
        """
        user_id = self.get_userIdByEmailVerificationId(verificationId)
        if user_id:
            return self.getUser(user_id)
        return None

    security.declareProtected(Perms.manage_users, 'get_userByEmail')
    def get_userByEmail(self, email):
        """ Get the user by email address.
        
        """
        user_id = self.get_userIdByEmail(email)
        if user_id:
            return self.getUser(user_id)

        return None

    security.declareProtected(Perms.manage_users, 'get_userByVerificationCode')
    def get_userByVerificationCode(self, verification_code):
        """ Get the user by verification code.
        
        """
        if not verification_code:
            return None
        
        for user in self.getUsers():
            if verification_code == user.get_verificationCode():
                return user
        
        return None

    security.declareProtected(Perms.manage_users, 'get_userIdByPasswordVerificationId')
    def get_userIdByPasswordVerificationId(self, verificationId):
        """Get the user ID from a email-verification ID
        """
        da = self.zsqlalchemy
        pvt = da.createMapper('password_reset')[1]
        
        s1 = pvt.select()
        s1.append_whereclause(pvt.c.verification_id == verificationId)
        r1 = s1.execute().fetchone()

        retval = r1['user_id']
        assert type(retval) == str
        return retval

    security.declareProtected(Perms.manage_users, 'get_userByPasswordVerificationId')
    def get_userByPasswordVerificationId(self, verificationId):
        user_id = self.get_userIdByPasswordVerificationId(verificationId)
        if user_id:
            return self.getUser(user_id)

        return None
        
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
                    
        CustomUser.addCustomUser(user_folder, name, password, roles, domains)
        self.setGroupsOfUser(groups, name)
        
        user = self.getUser(name)
        
        user.init_properties()
        user.title = name
        user.shortName = name
        user.manage_setLocalRoles(name, ['Owner'])
        
        return 1

    security.declarePrivate('_doChangeUser')
    def _doChangeUser(self, name, password, roles, domains, groups=None, **kw):
        user = self.getUser(name)
        if password is not None:
            if self.encrypt_passwords:
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
                raise KeyError, 'User "%s" does not exist' % username
            groupnames = user.getGroups()
            self.delGroupsFromUser(groupnames, username)

    security.declareProtected(Perms.manage_users, 'simple_register_user')
    def simple_register_user(self, email, userId, displayName):
        assert email
        assert userId
        assert displayName
        assert not(self.getUser(userId))
        assert not(self.get_userIdByEmail(email))

        self._doAddUser(userId, '', [], [], [])
        user = self.getUser(userId)
        assert user, \
          'Did not create the user %s with the email %s' %\
          (displayName, userId)

        user.manage_changeProperties(preferredName=displayName)

        # For now
        user.manage_addProperty('fn', displayName, 'string')
        user.manage_addProperty('creation_date', DateTime.DateTime(), 
                                'date')

        user.add_defaultDeliveryEmailAddress(email)
  
        assert user
        assert userId == user.getId()
        assert email in user.get_emailAddresses()
        assert displayName == user.getProperty('fn')
        return user
    
    security.declareProtected(Perms.manage_users, 'register_user')
    def register_user(self, email, user_id='', preferred_name='', first_name='', 
                      last_name='', password_length=8, roles=[], groups=[],
                      post_groups=[]):
        """ A method for a user to allow a user to register themselves.
        
        """
        import string
        
        validChars = string.letters+string.digits+'.'
        
        # unverified members always get this placeholder group till verified
        groups = list(groups)
        groups.append('unverified_member')
        
        user_id_provided = False
        if user_id:
            user_id_provided = True
        
        if user_id_provided and user_id:
            if self.getUser(user_id):
                raise KeyError, 'User ID %s already exists' % user_id
        
        if self.get_userByEmail(email):
            raise KeyError, 'A user already exists with email address %s' % email
        
        valid_id = False
        gen_user_id = XWFUtils.generate_user_id(user_id, '', '', email)
        if not user_id:
            user_id = gen_user_id.next()
        while not valid_id:
            if not self.getUser(user_id):
                for char in user_id:
                    if char not in validChars:
                        if user_id_provided:
                            raise KeyError, ('User ID %s contains an invalid character'
                                        ' (%s). Valid characters are %s.' % (user_id, char, validChars))
                        else:
                            break
                valid_id = True
            
            if valid_id:
                break
            
            user_id = gen_user_id.next()
            user_id_provided = False
        
        password = XWFUtils.generate_password(password_length)
        
        self._doAddUser(str(user_id), password, roles, [], groups)
        user = self.getUser(user_id)
        if user:
            if first_name and last_name:
                lhs = first_name + ' ' + last_name
            else:
              try:
                  lhs = email.split('@')[0]
              except:
                  lhs = ''
            preferred_name = preferred_name or lhs            
            user.manage_changeProperties(preferredName=preferred_name)
            
            if hasattr(user, 'fn'):
                user.manage_changeProperties(fn=preferred_name)
            else:
                user.manage_addProperty('fn', preferred_name, 'string')
                
            if first_name and hasattr(user, 'givenName'):
                user.manage_changeProperties(givenName=first_name)
            elif first_name:
                user.manage_addProperty('givenName', first_name, 'string')

            if last_name and hasattr(user, 'familyName'):
                user.manage_changeProperties(familyName=last_name)
            elif last_name:
                user.manage_addProperty('familyName', last_name, 'string')
            
            user.manage_addProperty('creation_date', DateTime.DateTime(),
                                    'date')
                             
            user.add_defaultDeliveryEmailAddress(email)
            
            verification_code = user.set_verificationCode()
            
            user.set_verificationGroups(post_groups)
            
            return (user_id, password, verification_code)
            
        return None
        
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

    security.declarePublic('verify_userFromEmail')
    def verify_userFromEmail(self, Mail):
        """ Verify the user from an email.

        """
        import re

        if not HaveMailBoxer:
            raise ImportError, ('MailBoxerTools is not available, unable to '
                                'verify user from email')
        
        acl_users = getattr(self, 'acl_users', None)
        mailHeader, mailBody = MailBoxerTools.splitMail(Mail)
        
        subject = MailBoxerTools.mime_decode_header(mailHeader.get('subject',
                                                                   ''))
        try:
            verification_code = re.findall('{(.*?)}', subject)[0]
            verification_code = re.sub('\s', '', verification_code)
        except:
            verification_code = ''

        user = self.get_userByVerificationCode(verification_code)
        
        if user:
            return user.verify_user(verification_code)
        
        return 0

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
        return self.manage_main(self,REQUEST)
    
InitializeClass(CustomUserFolder)

def initialize(context):
    context.registerClass(
        CustomUserFolder,
        permission='Manage users',
        constructors=(manage_addCustomUserFolderForm,
                      manage_addCustomUserFolder,),
        icon='icons/customuserfolder.gif'
        )
