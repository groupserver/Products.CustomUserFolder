# coding=utf-8
from sqlalchemy.exceptions import NoSuchTableError
import sqlalchemy as sa
import pytz, datetime

possible_settings = ['webonly', 'digest']

class UserQuery(object):
    def __init__(self, context, da):
        self.context = context

        self.user_id = context.getUserName()

        self.emailSettingTable = da.createMapper('email_setting')[1]
        self.userEmailTable = da.createMapper('user_email')[1]
        self.groupUserEmailTable = da.createMapper('group_user_email')[1]
        self.emailVerificationTable = da.createMapper('email_verification')[1]
        self.passwordResetTable = da.createMapper('password_reset')[1]
        self.invitationTable = da.createMapper('user_invitation')[1]

    def add_userEmail(self, email_address, is_preferred=False):
        uet = self.userEmailTable
        
        i = uet.insert()
        
        i.execute(user_id=self.user_id,
                  email=email_address,
                  is_preferred=is_preferred,
                  verified_date=None)
    
    def userEmail_verified(self, email):
        assert email
        uet = self.userEmailTable
        s1 = uet.select(uet.c.email == email)
        rs1 = s1.execute()

        retval = False
        if rs1.rowcount == 1:
            retval = rs1.fetchone()['verified_date'] != None
        assert type(retval) == bool
        return retval

    def add_userEmail_verificationId(self, verificationId, email):
        assert verificationId
        assert email
        evt = self.emailVerificationTable
        i = evt.insert()
        i.execute(verification_id=verificationId, email=email)
        # Change the user_email table?
        
    def remove_userEmail_verificationId(self, email):
        assert email
        evt = self.emailVerificationTable
        d = evt.delete(evt.c.email == email)
        d.execute()
        self.remove_userEmail(email)

    def userEmail_verificationId_valid(self, verificationId):
        assert verificationId
        evt = self.emailVerificationTable

        # Get the email address        
        s1 = evt.select(evt.c.verification_id == verificationId)
        rs1 = s1.execute()
        retval = rs1.rowcount == 1
        assert type(retval) == bool
        return retval
        
    def verify_userEmail(self, verificationId):
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
        s2 = uet.update(uet.c.email == email)
        s2.execute(verified_date = d  )
          
        # Remove the old verification code(s)
        s3 = evt.delete(evt.c.email == email)
        s3.execute()
        
        assert email
        return email
    
    def remove_userEmail(self, email_address):
        uet = self.userEmailTable        
        and_ = sa.and_
        d = uet.delete(and_(uet.c.email==email_address)).execute()

    def get_userEmail(self, preferred_only=False):
        uet = self.userEmailTable
        
        statement = uet.select()
        statement.append_whereclause(uet.c.user_id==self.user_id)
        if preferred_only == True:
            statement.append_whereclause(uet.c.is_preferred==preferred_only)
        
        r = statement.execute()
        email_addresses = []
        for row in r.fetchall():
            email_addresses.append(row['email'])
        
        return email_addresses
        
    def set_preferredEmail(self, email_address, is_preferred):
        uet = self.userEmailTable
        and_ = sa.and_
        
        u = uet.update(and_(uet.c.user_id==self.user_id,
                            uet.c.email==email_address))
        u.execute(is_preferred=is_preferred)

    def clear_preferredEmail(self):
        uet = self.userEmailTable
        and_ = sa.and_
                
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

        d = uet.delete(and_(uet.c.user_id==self.user_id,
                            uet.c.site_id==site_id,
                            uet.c.group_id==group_id,
                            uet.c.email==email_address)).execute()      

    def get_groupUserEmail(self, site_id, group_id):
        uet = self.groupUserEmailTable
        
        statement = uet.select()
        statement.append_whereclause(uet.c.user_id==self.user_id)
        statement.append_whereclause(uet.c.site_id==site_id)
        statement.append_whereclause(uet.c.group_id==group_id)
        
        r = statement.execute()
        email_addresses = []
        for row in r.fetchall():
            email_addresses.append(row['email'])
        
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

        d = est.delete(and_(est.c.user_id==self.user_id,
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

    def get_invitation(self, invitationId):
        ivt = self.invitationTable
        statement = ivt.select()
        statement.append_whereclause(ivt.c.invitation_id == invitationId)
        
        r = statement.execute()
        retval = {}
        if r.rowcount:
            res = r.fetchone()
            retval = {
              'invitation_id':    res['invitation_id'],
              'user_id':          res['user_id'],
              'inviting_user_id': res['inviting_user_id'],
              'site_id':          res['site_id'],
              'group_id':         res['group_id'],
              'invitation_date':  res['invitation_date']
            }
        return retval

    def get_userInvitations(self, userId):
        ivt = self.invitationTable
        statement = ivt.select()
        statement.append_whereclause(ivt.c.user_id == user_id)
        
        r = statement.execute()
        retval = []
        if r.rowcount:
            retval = [{
                'invitation_id':    invite['invitation_id'],
                'user_id':          invite['user_id'],
                'inviting_user_id': invite['inviting_user_id'],
                'site_id':          invite['site_id'],
                'group_id':         invite['group_id'],
                'invitation_date':  invite['invitation_date']
              } for invite in r.fetchall()]
        return retval

    def get_userInvitationsForGroup(self, groupId, siteId):
        ivt = self.invitationTable
        statement = ivt.select()
        statement.append_whereclause(ivt.c.user_id == self.userId)
        statement.append_whereclause(ivt.c.group_id == groupId)
        statement.append_whereclause(ivt.c.site_id == siteId)
        
        r = statement.execute()
        retval = []
        if r.rowcount:
            retval = [{
                'invitation_id':    invite['invitation_id'],
                'user_id':          invite['user_id'],
                'inviting_user_id': invite['inviting_user_id'],
                'site_id':          invite['site_id'],
                'group_id':         invite['group_id'],
                'invitation_date':  invite['invitation_date']
              } for invite in r.fetchall()]
        return retval

    def add_invitation(self, invitationId, invitingUserId, siteId, groupId):
        
        ivt = self.invitationTable
        d = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        statement = ivt.insert()
        statement.execute(invitation_id = invitationId, 
          user_id = self.user_id,  inviting_user_id = invitingUserId, 
          site_id = siteId, group_id = groupId, invitation_date = d)

    def clear_invitations(self):
        ivt = self.invitationTable
        d = ivt.delete(ivt.c.user_id == self.user_id)
        d.execute()

