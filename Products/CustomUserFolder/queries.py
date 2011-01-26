# coding=utf-8
import pytz, datetime
import sqlalchemy as sa

import logging
log = logging.getLogger("CustomUserFolder")

possible_settings = ['webonly', 'digest']

class UserQuery(object):
    def __init__(self, context, da):
        self.context = context

        self.user_id = context.getUserName()

        self.emailSettingTable = da.createTable('email_setting')
        self.userEmailTable = da.createTable('user_email')
        self.groupUserEmailTable = da.createTable('group_user_email')
        self.emailVerificationTable = da.createTable('email_verification')
        self.passwordResetTable = da.createTable('password_reset')
        self.nicknameTable = da.createTable('user_nickname')

    def add_userEmail(self, email_address, is_preferred=False):
        m = 'UserQuery.add_userEmail is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.base.queries.UserQuery.add_address '\
          'instead.'
        log.warn(m)
        uet = self.userEmailTable
        
        i = uet.insert()
        
        i.execute(user_id=self.user_id,
                  email=email_address,
                  is_preferred=is_preferred,
                  verified_date=None)
    
    def userEmail_verified(self, email):
        m = 'UserQuery.userEmail_verified is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.base.queries.UserQuery.address_verified '\
          'instead.'
        log.warn(m)
        assert email
        uet = self.userEmailTable
        s1 = uet.select(sa.func.lower(uet.c.email) == email.lower())
        rs1 = s1.execute()

        retval = False
        if rs1.rowcount == 1:
            retval = rs1.fetchone()['verified_date'] != None
        assert type(retval) == bool
        return retval
    
    # Verification methods: mostly deprecated and moved to 
    # gs.profile.email.verify.
    def add_userEmail_verificationId(self, verificationId, email):
        m = 'UserQuery.add_userEmail_verificationId is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.verify.queries.EmailQuery.set_verification_id '\
          'instead.'
        log.warn(m)
        assert verificationId
        assert email
        evt = self.emailVerificationTable
        i = evt.insert()
        # --=mpj17=-- With email addresses, we try and be case-insensitive
        # but case preserving (like NTFS). So we *add* the address with
        # full capitalisation, but remove it (in the function 
        # remove_userEmail_verificationId below) by being case-insensitive.
        i.execute(verification_id=verificationId, email=email)
        # Change the user_email table?
        
    def remove_userEmail_verificationId(self, email):
        m = 'UserQuery.remove_userEmail_verificationId is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.verify.queries.EmailQuery.clear_verification_ids '\
          'instead.'
        log.warn(m)
        assert email
        evt = self.emailVerificationTable
        d = evt.delete(sa.func.lower(evt.c.email) == email.lower())
        d.execute()
        self.remove_userEmail(email)

    def userEmail_verificationId_valid(self, verificationId):
        m = 'UserQuery.userEmail_verificationId_valid is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.verify.queries.VerificationQuery.verificationId_status '\
          'instead.'
        log.warn(m)
        assert verificationId
        evt = self.emailVerificationTable

        # Get the email address        
        s1 = evt.select(evt.c.verification_id == verificationId)
        rs1 = s1.execute()
        retval = rs1.rowcount == 1
        assert type(retval) == bool
        return retval

    def verify_userEmail(self, verificationId):
        m = 'UserQuery.verify_userEmail is deprecated: it should ' \
          'never be used. Use '\
          'gs.profile.email.verify.queries.EmailQuery.verify_address '\
          'instead.'
        log.warn(m)
        assert verificationId
        uet = self.userEmailTable
        evt = self.emailVerificationTable

        # Get the email address        
        s1 = evt.select(evt.c.verification_id == verificationId)
        rs1 = s1.execute()
        assert rs1.rowcount == 1
        email = rs1.fetchone()['email']
        
        # Set the email address as verified
        d = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        s2 = uet.update(sa.func.lower(uet.c.email) == email.lower())
        s2.execute(verified_date = d  )
          
        # Remove the old verification code(s)
        s3 = evt.delete(sa.func.lower(evt.c.email) == email.lower())
        s3.execute()
        
        assert email
        return email

    def unverify_userEmail(self, email):
        uet = self.userEmailTable
        
        # Set the email address as unverified
        s2 = uet.update(sa.func.lower(uet.c.email) == email.lower())
        s2.execute(verified_date = None  )
        
        return email
    
    def remove_userEmail(self, email_address):
        m = 'UserQuery.remove_userEmail is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.base.queries.UserQuery.remove_address '\
          'instead.'
        log.warn(m)
        uet = self.userEmailTable        
        and_ = sa.and_
        uet.delete(and_(sa.func.lower(uet.c.email)==email_address.lower())).execute()

    def get_userEmail(self, preferred_only=False, verified_only=True):
        m = 'UserQuery.get_userEmail is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.base.queries.UserQuery.get_addresses '\
          'instead.'
        log.warn(m)
        uet = self.userEmailTable
        statement = sa.select([uet.c.email], uet.c.user_id==self.user_id)
        if preferred_only:
            statement.append_whereclause(uet.c.is_preferred==preferred_only)
        if verified_only:
            statement.append_whereclause(uet.c.verified_date!=None)
        r = statement.execute()
        email_addresses = []
        for row in r.fetchall():
            email_addresses.append(row['email'])
        return email_addresses
        
    def set_preferredEmail(self, email_address, is_preferred):
        m = 'UserQuery.set_preferredEmail is deprecated: ' \
          'it should never be used. Use '\
          'gs.profile.email.base.queries.UserQuery.update_delivery '\
          'instead.'
        log.warn(m)
        uet = self.userEmailTable
        and_ = sa.and_
        
        u = uet.update(and_(uet.c.user_id==self.user_id,
                            sa.func.lower(uet.c.email)==email_address.lower()))
        u.execute(is_preferred=is_preferred)

    def clear_preferredEmail(self):
        uet = self.userEmailTable
        
        u = uet.update(uet.c.user_id==self.user_id)
        u.execute(is_preferred=False)
        
    def add_groupUserEmail(self, site_id, group_id, email_address):
        uet = self.groupUserEmailTable
        
        i = uet.insert()
        
        i.execute(user_id=self.user_id,
                  site_id=site_id,
                  group_id=group_id,
                  email=email_address)
        
    def remove_groupUserEmail(self, site_id, group_id, email_address):
        uet = self.groupUserEmailTable        
        and_ = sa.and_

        uet.delete(and_(uet.c.user_id==self.user_id,
               uet.c.site_id==site_id,
               uet.c.group_id==group_id,
               sa.func.lower(uet.c.email)==email_address.lower())).execute()

    def get_groupUserEmail(self, site_id, group_id, verified_only=True):
        guet = self.groupUserEmailTable
        
        statement = guet.select()
        statement.append_whereclause(guet.c.user_id==self.user_id)
        statement.append_whereclause(guet.c.site_id==site_id)
        statement.append_whereclause(guet.c.group_id==group_id)
        if verified_only:
            uet = self.userEmailTable
            statement.append_whereclause(uet.c.user_id == guet.c.user_id)
            statement.append_whereclause(uet.c.verified_date!=None)
    
        r = statement.execute()
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
            i = est.insert()
            i.execute(user_id=self.user_id,
                      site_id=site_id,
                      group_id=group_id,
                      setting=setting)
            
        else:
            u = est.update(and_(est.c.user_id==self.context.getUserName(),
                                est.c.site_id==site_id,
                                est.c.group_id==group_id))
            u.execute(setting=setting)

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

