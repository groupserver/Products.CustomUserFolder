import zope.interface 
from zope.interface import implements, implementedBy
from zope.component import adapts, createObject
from interfaces import IGSUserInfo, ICustomUser
from zope.component.interfaces import IFactory

class GSUserInfoFromIDFactory(object):
    implements(IFactory)
    title=u'User Info from ID Factory'
    description=u'Create a User Info instance from a user ID'
    
    #--=mpj17=-- See zope.component.__init__ for details of createObject
    
    def __call__(self, context, userId):
        retval = None
        acl_users = context.acl_users
        user = acl_users.getUser(userId)
        # assert user, 'User with the ID %s not found' % userId
        if user:
            retval = GSUserInfo(user)
        else:
            retval = GSAnonymousUserInfo()
        assert retval
        return retval
        
    def getInterfaces(self):
        retval = implementedBy(GSUserInfo)
        assert retval
        return retval

class GSUserInfo(object):
    implements( IGSUserInfo )
    adapts( ICustomUser )
    
    def __init__(self, user):
        self.user = user
        self.__fn = None
        self.__url = None
        self.__nickname = None
        
    @property
    def id(self):
        retval = self.user.getId()
        return retval

    @property
    def url(self):
        if self.__url == None:
            # This needs to get a little more complex
            self.__url = '/p/%s' % self.nickname
        assert self.__url != None
        return self.__url

    @property
    def name(self):
        if self.__fn == None:
            self.__fn = self.user.getProperty('fn', 
              self.user.getProperty('preferredName'))
        assert self.__fn != None
        return self.__fn
        
    @property
    def imageUrl(self):
        retval = self.user.get_image()
        return retval
    
    @property
    def nickname(self):
        if self.__nickname == None:
            self.__nickname = self.user.get_canonicalNickname()
        assert self.__nickname != None
        return self.__nickname
        
    def get_property(self, prop, default=None):
        retval = self.user.getProperty(prop, default)
        return retval


class GSAnonymousUserInfo(object):
    implements( IGSUserInfo )
    
    def __init__(self):
        self.id = ''
        self.url = '#'
        self.name = 'Anonymous User'
        self.imageUrl = ''
        self.nickname = ''
                
    def get_property(self, prop, default=None):
        retval = default
        return retval

