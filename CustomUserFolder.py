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
# You MUST follow the rules in STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
#
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl import Permissions as Perms
from AccessControl.User import BasicUserFolder, _remote_user_mode
from Globals import InitializeClass
from OFS.Folder import Folder
from Products.NuxUserGroups import UserFolderWithGroups

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
        
    security.declarePrivate('_getUserFolder')
    def _getUserFolder(self):
        """ Return the folder object that contains the user objects,  or None.
        
        """
        return getattr(self, self.user_folder_id, None)

    security.declareProtected(Perms.manage_users, 'get_userByEmail')
    def get_userByEmail(self, email):
        """ Get the user by email address.
        
        """
        for user in self.getUsers():
            if email in user.get_emailAddresses():
                return user
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
        
        return users
    
    security.declareProtected(Perms.manage_users, 'getUser')
    def getUser(self, name):
        """ Return the named user object or None.
        
        """
        user_folder = self._getUserFolder()
        return getattr(user_folder, name, None)
    
    security.declarePrivate('_doAddUser')
    def _doAddUser(self, name, password, roles, domains, groups=(), **kw):
        """ Create a new user.
        
        """
        import CustomUser
        user_folder = self._getUserFolder()
        if password is not None and self.encrypt_passwords:
            password = self._encryptPassword(password)
                    
        CustomUser.addCustomUser(user_folder, name, password, roles, domains)
        
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
