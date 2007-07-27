##############################################################################
#
# Copyright (c) 2004, 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.interface import implements
from zope.app.size.interfaces import ISized

def test_userinfo():
    """
    Test User Info

    Set up:
      >>> from zope.app.testing.placelesssetup import setUp, tearDown
      >>> setUp()
      >>> import Products.Five
      >>> import Products.CustomUserFolder
      >>> from Products.Five import zcml

      >>> zcml.load_config('meta.zcml', Products.Five)
      >>> zcml.load_config('permissions.zcml', Products.Five)
      >>> zcml.load_config('configure.zcml', Products.CustomUserFolder)

      >>> from Products.ZSQLAlchemy.ZSQLAlchemy import manage_addZSQLAlchemy  
      >>> from Products.CustomUserFolder.CustomUser import CustomUser
      >>> from Products.CustomUserFolder.queries import UserQuery
      >>> name = 'testtesttest'
      >>> password = 'testpass'
      >>> roles = ('test',)
      >>> domains = ()
      >>> cu = CustomUser(name, password, roles, domains)

    Setup ZSQLAlchemy:
      >>> alchemy_adaptor = manage_addZSQLAlchemy(app, 'zalchemy')
      >>> alchemy_adaptor.manage_changeProperties( hostname='localhost',
      ...                                             port=5432,
      ...                                             username='postgres',
      ...                                             password='',
      ...                                             dbtype='postgres',
      ...                                             database='gs')

      >>> uq = UserQuery(cu, alchemy_adaptor)
      
      >>> uq.add_userEmail('np@test.com', is_preferred=False)
      >>> uq.add_userEmail('p@test.com', is_preferred=True)

      >>> r = uq.get_userEmail()
      >>> r.sort()
      >>> r
      ['np@test.com', 'p@test.com']

      >>> r = uq.get_userEmail(preferred_only=True)
      >>> r.sort()
      >>> r
      ['p@test.com']

      >>> uq.set_preferredEmail('np@test.com', is_preferred=True)

      >>> r = uq.get_userEmail(preferred_only=True)
      >>> r.sort()
      >>> r
      ['np@test.com', 'p@test.com']

      >>> uq.set_preferredEmail('np@test.com', is_preferred=False)

      >>> r = uq.get_userEmail(preferred_only=True)
      >>> r
      ['p@test.com']

      >>> uq.clear_preferredEmail()

      >>> r = uq.get_userEmail(preferred_only=True)
      >>> r
      []

      >>> uq.add_groupUserEmail('blarg', 'foo', 'p@test.com')
      >>> uq.get_groupUserEmail('blarg', 'foo')
      ['p@test.com']
      >>> uq.remove_groupUserEmail('blarg', 'foo', 'p@test.com')
      >>> uq.get_groupUserEmail('blarg', 'foo')
      []
      
      >>> uq.get_groupEmailSetting('blarg', 'foo') == None
      True
      >>> uq.set_groupEmailSetting('blarg', 'foo', 'digest')
      >>> uq.get_groupEmailSetting('blarg', 'foo')
      'digest'
      >>> uq.set_groupEmailSetting('blarg', 'foo', 'webonly')
      >>> uq.get_groupEmailSetting('blarg', 'foo')
      'webonly'
      >>> uq.clear_groupEmailSetting('blarg', 'foo')
      >>> uq.get_groupEmailSetting('blarg', 'foo') == None
      True
      
      >>> uq.remove_userEmail('p@test.com')
      >>> uq.remove_userEmail('np@test.com')
      >>> r = uq.get_userEmail()
      >>> r
      []

    Clean up:
      >>> tearDown()
      
    """

def test_suite():
    from Testing.ZopeTestCase import ZopeDocTestSuite
    return ZopeDocTestSuite()

if __name__ == '__main__':
    framework()
