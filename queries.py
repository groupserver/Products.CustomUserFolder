from sqlalchemy.exceptions import NoSuchTableError
import sqlalchemy as sa

possible_settings = ['webonly', 'digest']

class UserQuery(object):
    def __init__(self, context, da):
        self.context = context

        session = da.getSession()
        metadata = session.getMetaData()

        self.emailSettingTable = sa.Table('email_setting',
                                           metadata, autoload=True)
        
    def get_groupEmailSetting(self, site_id, group_id):
        """ Given a site_id and group_id, check to see if the user
            has any specific email settings.
        
        """
        est = self.emailSettingTable
        statement = est.select()
        statement.append_whereclause(est.c.user_id==self.context.getUserName())
        statement.append_whereclause(est.c.site_id==site_id)
        statement.append_whereclause(est.c.group_id==group_id)
        r = statement.execute()
        
        setting = None
        if r.rowcount:
            result = r.fetchone()
            setting = result['setting']
        
        return setting

    def set_groupEmailSetting(self, site_id, group_id, setting):
        """ Given a site_id, group_id and a setting, set the email_setting
            table.

        """
        
        assert setting in possible_settings, "Unknown setting %s" % setting

        est = self.emailSettingTable
        and_ = sqlalchemy.and_

        curr_setting = self.get_groupEmailSetting(site_id, group_id)
        if not curr_setting:
            i = est.insert()
            i.execute(user_id=self.context.getUserName(),
                      site_id=site_id,
                      group_id=group_id,
                      setting=setting)
            
        else:
            u = est.update(and_(est.c.user_id==self.context.getUserName(),
                                est.c.site_id==site_id,
                                est.c.group_id==group_id))
            u.execute(setting=setting)
