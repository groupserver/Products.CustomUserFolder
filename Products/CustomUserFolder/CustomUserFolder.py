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
from Products.XWFCore.XWFUtils import locateDataDirectory
import os

import DateTime
import re
import sqlalchemy as sa

import logging
log = logging.getLogger('CustomUserFolder')

try:
    # richard: mailboxer was merged into XWFMailingListManager
    from Products.XWFMailingListManager import MailBoxerTools
    HaveMailBoxer = True
except:
    HaveMailBoxer = False

class CustomUserFolder(UserFolderWithGroups):
    """ A user folder for CampusUser users, based on the NuxUserGroup UserFolder
    interface.
    
    """
    implements(ICustomUserFolder)

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
        userEmailTable = da.createTable('user_email')
        
        statement = userEmailTable.select()
        statement.append_whereclause(email == sa.func.lower(userEmailTable.c.email))
        
        r = statement.execute().fetchone()
        if r:
            return r['user_id']

        return None
        
    security.declareProtected(Perms.manage_users, 'get_userIdByEmailVerificationId')
    def get_userIdByEmailVerificationId(self, verificationId):
        """Get the user ID from a email-verification ID
        """
        da = self.zsqlalchemy
        evt = da.createTable('email_verification')
        
        s1 = evt.select()
        s1.append_whereclause(evt.c.verification_id == verificationId)
        r1 = s1.execute().fetchone()
        
        retval = ''
        if r1:
            return self.get_userIdByEmail(r1['email'])
        assert type(retval) == str
        return retval
        
    security.declareProtected(Perms.manage_users, 'get_userByEmailVerificationId')
    def get_userByEmailVerificationId(self, verificationId):
        """ Get the user by verification ID
        """
        m = 'CustomUserFolder.get_userByEmailVerificationId is '\
          'deprecated: it should never be used. Use '\
          'gs.profile.email.verify.emailverificationuser.EmailVerificationUserFromId '\
          'instead. Called from %s.' % self.REQUEST.URL
        log.warn(m)
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
        pvt = da.createTable('password_reset')

        s1 = pvt.select()
        s1.append_whereclause(pvt.c.verification_id == verificationId)
        r1 = s1.execute().fetchone()

        retval = ''
        if r1:
            retval = r1['user_id']
        assert type(retval) == str
        return retval

    security.declareProtected(Perms.manage_users, 'get_userByPasswordVerificationId')
    def get_userByPasswordVerificationId(self, verificationId):
        assert verificationId
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
        assert name, 'User ID not set'
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
                    
        CustomUser.addCustomUser(user_folder, name, password, roles, domains)
        self.setGroupsOfUser(groups, name)
        
        user = self.getUser(name)
        
        user.init_properties()
        user.title = name
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
        assert not(self.get_userIdByEmail(email)), '<%s> exists' % email

        self._doAddUser(userId, '', [], [], [])
        user = self.getUser(userId)
        assert user, \
          'Did not create the user %s with the email %s' %\
          (displayName, userId)

        user.manage_changeProperties(fn=displayName)
        # For now
        user.manage_addProperty('creation_date', DateTime.DateTime(), 
                                'date')
  
        assert user
        assert userId == user.getId()
        # --=mpj17=-- Trick for young players: the following assert 
        # *should* work, but it does not necessarily work, as a race
        # condition is created between this code and the relational
        # database.
        # assert email in user.get_emailAddresses()
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

    security.declarePublic('verify_address')
    def verify_address(self, Mail):
        """Verify the email address of an existing user.
        
        This method is designed to be called from the mail server.
        
        ARGUMENTS
          Mail: the mail message to process.
          
        SIDE EFFECTS
          The email address associated the verification ID in the subject
          is verified.
          
        RETURNS
          None.
        """
        assert Mail
        if not HaveMailBoxer:
            raise ImportError, ('MailBoxerTools is not available, unable to '
                                'verify user from email')
        
        mailHeader, mailBody = MailBoxerTools.splitMail(Mail) #@UnusedVariable
        subjHdr = mailHeader.get('subject', '')
        subject = MailBoxerTools.mime_decode_header(subjHdr)
        assert subject, 'No subject in verification mail message'

        m = 'verify_address: Processing message "%s"' % subject
        log.info(m)
        
        verificationId = re.findall('{(.*?)}', subject)[0]
        verificationId = re.sub('\s', '', verificationId)
        assert verificationId, 'No verification ID in verification mail message'
        
        user = self.get_userByEmailVerificationId(verificationId)
        assert user, 'No user for the verification ID "%s"' % verificationId
        email = user.verify_emailAddress(verificationId) #@UnusedVariable
        # TODO: send out a notification to the user, informing him or her
        #   that the address has been verified.
        
    security.declarePublic('get_userIdByNickname')
    def get_userIdByNickname(self, nickname):
        assert nickname
        assert type(nickname) in (str, unicode)

        da = self.zsqlalchemy
        unt = da.createTable('user_nickname')

        statement = unt.select()
        statement.append_whereclause(unt.c.nickname == nickname)
        
        r = statement.execute()
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
                name, password, domains, remote_user_mode = info #@UnusedVariable
                self._doDelUsers(self.getUserNames())
                self._doAddUser(name, password, ('Manager',), domains)
                try:
                    os.remove(os.path.join(INSTANCE_HOME, 'inituser'))
                except:
                    pass

    security.declareProtected(Perms.view, 'migrate_images')
    def migrate_images(self):
        """ Migrate the images to disk
        
        """
        siteId = self.site_root().getId()
        contactImageDir = locateDataDirectory("groupserver.user.image",
                                              (siteId,))
        for image in self.contactsimages.objectValues():
            if image.meta_type == 'Image':
                filePath = os.path.join(contactImageDir, image.getId())
                f = file(filePath, 'a+') 
                f.write(str(image.data))
                f.close()

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

