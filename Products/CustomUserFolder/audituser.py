# coding=utf-8
from datetime import date
from zope.component import createObject
from zope.component.interfaces import IFactory
from zope.interface import implements, implementedBy
from Products.GSAuditTrail import IAuditEvent, BasicAuditEvent, \
  AuditQuery, event_id_from_data
from interfaces import IGSUserInfo

SUBSYSTEM = 'groupserver.CustomUser'
import logging
log = logging.getLogger(SUBSYSTEM) #@UndefinedVariable

UNKNOWN        = 0
CHANGE_PROFILE = 1

class CustomUserAuditEventFactory(object):
    implements(IFactory)

    title=u'Custom User Audit-Event Factory'
    description=u'Creates a GroupServer audit event for custom user'

    def __call__(self, context, eventId,  code, d,
        userInfo, instanceUserInfo,  siteInfo,  
        instanceDatum, supplementaryDatum):

        if code == CHANGE_PROFILE:
            event = SetPasswordEvent(context, eventId, d, 
              userInfo, instanceUserInfo, siteInfo,
              instanceDatum, supplementaryDatum)
        else:
            event = BasicAuditEvent(context, eventId, UNKNOWN, d, 
              userInfo, instanceUserInfo, siteInfo, None, 
              instanceDatum, supplementaryDatum, SUBSYSTEM)
        return event
    
    def getInterfaces(self):
        return implementedBy(BasicAuditEvent)

class ChangeProfileEvent(BasicAuditEvent):
    implements(IAuditEvent)

    def __init__(self, context, id, d, userInfo, instanceUserInfo, 
        siteInfo, instanceDatum,  supplementaryDatum):
        
        BasicAuditEvent.__init__(self, context, id, 
          CHANGE_PROFILE, d, userInfo, instanceUserInfo, 
          siteInfo, None,  instanceDatum, supplementaryDatum, 
          SUBSYSTEM)
    
    def __str__(self):
        retval = u'%s (%s) set password on %s (%s)' %\
          (self.instanceUserInfo.name, self.instanceUserInfo.id,
           self.siteInfo.name, self.siteInfo.id)
        return retval

    @property
    def xhtml(self):
        cssClass = u'audit-event profile-event-%s' % self.eventCode
        retval = u'<span class="%s">%s set password</span>' % \
          (cssClass, 
           userInfo_to_anchor(self.instanceUserInfo),
           self.instanceDatum)
        return retval

def userInstanceModified(instance, event):
    log.info('Stuff')

class foo(object):
    def __init__(self, user):
        self.user = user
        self.userInfo = createObject('groupserver.LoggedInUser',user)
        self.instanceUserInfo = IGSUserInfo(user)
        self.siteInfo = createObject('groupserver.SiteInfo', user)
        
        da = user.zsqlalchemy
        self.queries = AuditQuery(da)
      
        self.factory = ProfileAuditEventFactory()
        
    def info(self, code, instanceDatum = '', supplementaryDatum = ''):
        d = date.today()
        eventId = event_id_from_data(self.userInfo, 
          self.instanceUserInfo, self.siteInfo, code, instanceDatum,
          supplementaryDatum)
        e = self.factory(self.user, eventId,  code, d,
          self.userInfo, self.instanceUserInfo, self.siteInfo,
          instanceDatum, supplementaryDatum)
        self.queries.store(e)
        log.info(e)

