# Copyright (c) 2003, IOPEN Technologies Ltd.
# Author: richard@iopen.co.nz
#
from Products.PageTemplates.PageTemplateFile import PageTemplateFile
from AccessControl import ClassSecurityInfo
from AccessControl.User import BasicUserFolder
from Globals import InitializeClass, PersistentMapping
from OFS.Folder import Folder
from Products.NuxUserGroups import UserFolderWithGroups

class CustomUserFolder(UserFolderWithGroups):
    """ A user folder for CampusUser users, based on the NuxUserGroup UserFolder
    interface.
    
    """
    meta_type = "Custom User Folder"
    id ='acl_users'
    title = 'Custom User Folder'
    icon ='p_/UserFolder'
    
    def __init__(self, user_folder_id):
        """ Initialize the data storage.
           
        """
        self.user_folder_id = user_folder_id
        
    def _getUserFolder(self):
        """ Return the folder object that contains the user objects,  or None.
        
        """
        return getattr(self, self.user_folder_id, None)

    def get_userByEmail(self, email):
        """ Get the user by email address.
        
        """
        for user in self.getUsers():
            if email in user.get_emailAddresses():
                return user
        return None
        
    def getUserNames(self):
        """ Return a list of usernames.
        
        """
        user_folder = self._getUserFolder()
        names = user_folder.objectIds('Custom User')
        names.sort()
        
        return names
    
    def getUsers(self):
        """ Return a list of user objects.
        
        """
        user_folder = self._getUserFolder()
        users = user_folder.objectValues('Custom User')
        
        return users
    
    def getUser(self, name):
        """ Return the named user object or None.
        
        """
        user_folder = self._getUserFolder()
        return getattr(user_folder, name, None)
    
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
        
        return 1

    def _doChangeUser(self, name, password, roles, domains, groups=None, **kw):
        user = self.getUser(name)
        if password is not None:
            if self.encrypt_passwords:
                password = self._encryptPassword(password)
            user.__ = password
        user.roles = roles
        user.domains = domains
        
        if groups is not None:
            self.setGroupsofUser(groups, name)

    def _doDelUsers(self, names):
        user_folder = self._getUserFolder()
        user_folder.manage_delObjects(names)
        
        for username in names:
            user = self.getUser(username)
            if user is None:
                raise KeyError, 'User "%s" does not exist' % username
            groupnames = user.getGroups()
            self.delGroupsFromUser(groupnames, username)
        
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
