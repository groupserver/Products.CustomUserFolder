# coding=utf-8
import pytz, datetime
import sqlalchemy as sa
from zope.sqlalchemy import mark_changed 
from gs.database import getTable, getSession

import logging
log = logging.getLogger("CustomUserFolder")

possible_settings = ['webonly', 'digest']

class UserQuery(object):
    def __init__(self, context, da):
        self.context = context

        self.user_id = context.getUserName()

        self.emailSettingTable = getTable('email_setting')
        self.userEmailTable = getTable('user_email')
        self.groupUserEmailTable = getTable('group_user_email')
        self.emailVerificationTable = getTable('email_verification')
        self.passwordResetTable = getTable('password_reset')
        self.nicknameTable = getTable('user_nickname')

    def add_userEmail(self, email_address, is_preferred=False):
        m = 'UserQuery.add_userEmail is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.base.queries.UserQuery.add_address '\
          'instead.'
        log.debug(m)
        assert False

    def userEmail_verified(self, email):
        m = 'UserQuery.userEmail_verified is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.base.queries.UserQuery.address_verified '\
          'instead.'
        log.debug(m)
        assert False
    
    # Verification methods: mostly deprecated and moved to 
    # gs.profile.email.verify.
    def add_userEmail_verificationId(self, verificationId, email):
        m = 'UserQuery.add_userEmail_verificationId is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.verify.queries.EmailQuery.set_verification_id '\
          'instead.'
        log.debug(m)
        assert False
        
    def remove_userEmail_verificationId(self, email):
        m = 'UserQuery.remove_userEmail_verificationId is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.verify.queries.EmailQuery.clear_verification_ids '\
          'instead.'
        log.debug(m)
        assert False

    def userEmail_verificationId_valid(self, verificationId):
        m = 'UserQuery.userEmail_verificationId_valid is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.verify.queries.VerificationQuery.verificationId_status '\
          'instead.'
        log.debug(m)
        assert False

    def verify_userEmail(self, verificationId):
        m = 'UserQuery.verify_userEmail is deprecated: it should ' \
          'never be used. Use '\
          'gs.profile.email.verify.queries.EmailQuery.verify_address '\
          'instead.'
        log.debug(m)
        assert False

    def unverify_userEmail(self, email):
        '''Set the email address as unverified'''
        uet = self.userEmailTable
        u = uet.update(sa.func.lower(uet.c.email) == email.lower())
        d = {'verified_date': None }

        session = getSession()
        session.execute(u, params=d)
        mark_changed(session)
        return email
    
    def remove_userEmail(self, email_address):
        m = 'UserQuery.remove_userEmail is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.base.queries.UserQuery.remove_address '\
          'instead.'
        log.debug(m)
        assert False

    def get_userEmail(self, preferred_only=False, verified_only=True):
        m = 'UserQuery.get_userEmail is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.base.queries.UserQuery.get_addresses '\
          'instead.'
        log.debug(m)
        assert False
        
    def set_preferredEmail(self, email_address, is_preferred):
        m = 'UserQuery.set_preferredEmail is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.base.queries.UserQuery.update_delivery '\
          'instead.'
        log.debug(m)
        assert False

    def clear_preferredEmail(self):
        uet = self.userEmailTable
        u = uet.update(uet.c.user_id==self.user_id)
        d = {'is_preferred': False}

        session = getSession()
        session.execute(u, params=d)
        mark_changed(session)

    def add_groupUserEmail(self, site_id, group_id, email_address):
        uet = self.groupUserEmailTable
        i = uet.insert()
        d = {'user_id': self.user_id,
             'site_id': site_id,
             'group_id': group_id,
             'email': email_address}

        session = getSession()
        session.execute(i, params=d)
        mark_changed(session)
        
    def remove_groupUserEmail(self, site_id, group_id, email_address):
        uet = self.groupUserEmailTable        
        and_ = sa.and_
        d = uet.delete(and_(uet.c.user_id==self.user_id,
                            uet.c.site_id==site_id,
                            uet.c.group_id==group_id,
                            sa.func.lower(uet.c.email)==email_address.lower()))

        session = getSession()
        session.execute(d)
        mark_changed(session)
        
    def get_groupUserEmail(self, site_id, group_id, verified_only=True):
        guet = self.groupUserEmailTable
        s = guet.select()
        s.append_whereclause(guet.c.user_id==self.user_id)
        s.append_whereclause(guet.c.site_id==site_id)
        s.append_whereclause(guet.c.group_id==group_id)
        if verified_only:
            uet = self.userEmailTable
            s.append_whereclause(uet.c.user_id == guet.c.user_id)
            s.append_whereclause(uet.c.verified_date!=None)
    
        session = getSession()
        r = session.execute(s)
        email_addresses = []
        for row in r.fetchall():
            email_address = row['email']
            if email_address not in email_addresses:
                email_addresses.append(email_address)
                
        return email_addresses

    def set_groupEmailSetting(self, site_id, group_id, setting):
        """ Given a site_id, group_id and a setting, set the email_setting
            table.
        """
        assert setting in possible_settings, "Unknown setting %s" % setting
        est = self.emailSettingTable
        and_ = sa.and_
        curr_setting = self.get_groupEmailSetting(site_id, group_id)
        if not curr_setting:
            iOrU = est.insert()
            d = {'user_id': self.user_id,
                 'site_id': site_id,
                 'group_id': group_id,
                 'setting': setting}
            
        else:
            iOrU = est.update(and_(est.c.user_id==self.context.getUserName(),
                                   est.c.site_id==site_id,
                                   est.c.group_id==group_id))
            d = {'setting':setting}

        session = getSession()
        session.execute(iOrU, parms = d)
        mark_changed(session)
    # --=mpj17==-- Up to here.

    def clear_groupEmailSetting(self, site_id, group_id):
        est = self.emailSettingTable        
        and_ = sa.and_

        est.delete(and_(est.c.user_id==self.user_id,
                        est.c.site_id==site_id,
                        est.c.group_id==group_id)).execute()
        
    def get_groupEmailSetting(self, site_id, group_id):
        """ Given a site_id and group_id, check to see if the user
            has any specific email settings.
        
        """
        est = self.emailSettingTable
        statement = est.select()
        statement.append_whereclause(est.c.user_id==self.user_id)
        statement.append_whereclause(est.c.site_id==site_id)
        statement.append_whereclause(est.c.group_id==group_id)
        r = statement.execute()
        
        setting = None
        if r.rowcount:
            result = r.fetchone()
            setting = result['setting']
        
        return setting
        
    def set_userPasswordResetVerificationId(self, verificationId):
        prt = self.passwordResetTable
        i = prt.insert()
        i.execute(verification_id = verificationId, user_id = self.user_id)

    def clear_userPasswordResetVerificationIds(self):
        prt = self.passwordResetTable
        d = prt.delete(prt.c.user_id == self.user_id)
        d.execute()
        
    def get_latestNickname(self):
        unt = self.nicknameTable
        statement = unt.select()
        statement.append_whereclause(unt.c.user_id == self.user_id)
        statement.order_by(sa.desc(unt.c.date))
        statement.limit = 1
        
        r = statement.execute()
        if r.rowcount:
            retval = r.fetchone()['nickname']
        else:
            retval = None
        return retval

    def add_nickname(self, nickname):
        unt = self.nicknameTable
        statement = unt.insert()
        statement.execute(user_id = self.user_id, nickname = nickname,
          date = datetime.datetime.now())

    def clear_nicknames(self):
        unt = self.nicknameTable
        d = unt.delete(unt.c.user_id == self.user_id)
        d.execute()

