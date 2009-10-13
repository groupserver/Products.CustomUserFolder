# coding=utf-8
import zope.interface 
from zope.interface import implements, implementedBy
from zope.component import adapts
from interfaces import IGSUserInfo, ICustomUser
from zope.component.interfaces import IFactory
from AccessControl.User import nobody
from AccessControl import getSecurityManager

class GSUserInfoFromIDFactory(object):
    implements(IFactory)
    title=u'User Info from ID Factory'
    description=u'Create a User Info instance from a user ID'
    
    #--=mpj17=-- See zope.component.__init__ for details of createObject
    
    def __call__(self, context, userId):
        retval = None
        acl_users = context.acl_users
        user = None
        if userId:
            user = acl_users.getUser(userId)
        if user:
            try:
                retval = GSUserInfo(user)
            except AssertionError, e:
                retval = GSAnonymousUserInfo()
        else:
            retval = GSAnonymousUserInfo()
        assert retval
        return retval
        
    def getInterfaces(self):
        retval = implementedBy(GSUserInfo)
        assert retval
        return retval

class GSLoggedInUserFactory(object):
    implements(IFactory)
    title=u'Logged in User Info Factory'
    description=u'Create a User Info instance for the logged in user'
    
    #--=mpj17=-- See zope.component.__init__ for details of createObject
    
    def __call__(self, context):
        retval = None
        acl_users = context.acl_users
        user = getSecurityManager().getUser()
        if user:
            retval = GSUserInfoFromIDFactory()(context, user.getId())
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
    anonymous = False
    
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
            self.__url = '/p/%s' % self.nickname.encode('utf-8','ignore')
        assert self.__url != None
        return self.__url

    @property
    def name(self):
        if self.__fn == None:
            fn = self.get_property('fn')
            if not fn:
                fn = self.get_property('preferredName')
            self.__fn = fn
             
        assert self.__fn != None
        return self.__fn
        
    @property
    def imageUrl(self):
        retval = self.user.get_image()
        return retval
    
    @property
    def nickname(self):
        if self.__nickname == None:
            nn = self.user.get_canonicalNickname()
            if isinstance(nn, str):
                nn = unicode(nn, 'utf-8', 'ignore')
            self.__nickname = nn
        assert self.__nickname != None
        return self.__nickname
        
    def get_property(self, prop, default=None):
        retval = self.user.getProperty(prop, default)
        if isinstance(retval, str):
            retval = unicode(retval, 'utf-8', 'ignore')
        
        return retval


class GSAnonymousUserInfo(object):
    implements( IGSUserInfo )
    
    def __init__(self):
        self.id = ''
        self.url = '#'
        self.name = u'Anonymous User'
        self.imageUrl = ''
        self.nickname = ''
        self.user = nobody
        self.anonymous = True
                
    def get_property(self, prop, default=None):
        retval = default
        return retval

def userInfo_to_anchor(userInfo):
    assert isinstance(userInfo, GSUserInfo), 'Not a user info'
    retval = u'<a class="fn" href="%s">%s</a>' % \
      (userInfo.url, userInfo.name)
    assert type(retval) == unicode
    assert retval
    return retval
