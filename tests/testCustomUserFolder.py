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
# You MUST follow the rules in http://iopen.net/STYLE before checking in code
# to the trunk. Code which does not follow the rules will be rejected.
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('CustomUserFolder')

from Products.CustomUserFolder import CustomUserFolder
from Products.CustomUserFolder import CustomUser
class TestCustomUserFolder(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        self.folder.manage_delObjects(['acl_users'])
        self.folder.manage_addFolder('users')
        CustomUserFolder.manage_addCustomUserFolder(self.folder, 'users')
        
        self._addUser(False)
        
        self._initialStateTest()
        
    def _initialStateTest(self):
        self.failUnless(self.auser.get_preferredEmailAddresses()==[])
        self.failUnless(self.auser.get_emailAddresses()==[])
        
    def _addUser(self, encrypt_password):
        self.folder.acl_users.encrypt_passwords = encrypt_password
        self.folder.acl_users._doAddUser('user', 'password', [], [])
        self.auser = self.folder.acl_users.getUser('user')
        
    def _delUser(self):
        self.folder.acl_users._doDelUsers(['user'])
        
    def test_01_getPassword(self):
        self.failUnless(self.auser.get_password()=='password')
    
    def test_02_getEncryptedPassword(self):
        self._delUser()
        self._addUser(True)
        self.failUnless(self.folder.acl_users._isPasswordEncrypted(self.auser.get_password())\
                        == 1)
    
    
    
    def test_05_setupInitialEmailAddresses(self):
        self.auser.add_emailAddress('richard@iopen.co.nz')
        self.failUnless(self.auser.get_emailAddresses()==['richard@iopen.co.nz'])
    
    # old style delivery customisation, using the old method names. Leave for
    # backward compatibility
    def test_06_customiseDefaultDelivery(self):
        self.test_05_setupInitialEmailAddresses()
        self.auser.add_preferredEmailAddress('richard@iopen.net')
        self.auser.add_preferredEmailAddress('wibble@iopen.net')
        
        self.failUnless(self.auser.get_preferredEmailAddresses()\
                        == ['richard@iopen.net','wibble@iopen.net'])
        
        self.failUnless(self.auser.get_emailAddresses()\
                        == ['richard@iopen.co.nz','richard@iopen.net','wibble@iopen.net'])
        
    # the same as test_06, except updated to the new method names
    def test_07_customiseDefaultDelivery(self):
        self.test_05_setupInitialEmailAddresses()
        self.auser.add_defaultDeliveryEmailAddress('richard@iopen.net')
        self.auser.add_defaultDeliveryEmailAddress('wibble@iopen.net')
        
        self.failUnless(self.auser.get_defaultDeliveryEmailAddresses()\
                        == ['richard@iopen.net','wibble@iopen.net'])
        
        self.failUnless(self.auser.get_emailAddresses()\
                        == ['richard@iopen.co.nz','richard@iopen.net','wibble@iopen.net'])
        
    def test_10_customiseDeliveryByKey(self):
        self.test_06_customiseDefaultDelivery()
        
        self.auser.add_deliveryEmailAddressByKey('fooGroup', 'richard@iopen.net')
        self.failUnless(self.auser.get_deliverySettingsByKey('fooGroup')==2)
        self.failUnless(self.auser.get_deliveryEmailAddressesByKey('fooGroup')\
                        == ['richard@iopen.net'])
        
        self.auser.add_deliveryEmailAddressByKey('fooGroup', 'richard@iopen.co.nz')
        self.failUnless(self.auser.get_deliverySettingsByKey('fooGroup')==2)
        self.failUnless(self.auser.get_deliveryEmailAddressesByKey('fooGroup')\
                        == ['richard@iopen.net', 'richard@iopen.co.nz'])
        
        self.auser.remove_deliveryEmailAddressByKey('fooGroup', 'richard@iopen.net')
        self.failUnless(self.auser.get_deliverySettingsByKey('fooGroup')==2)
        self.failUnless(self.auser.get_deliveryEmailAddressesByKey('fooGroup')\
                        == ['richard@iopen.co.nz'])
        
        self.auser.remove_deliveryEmailAddressByKey('fooGroup', 'richard@iopen.co.nz')
        self.failUnless(self.auser.get_deliverySettingsByKey('fooGroup')==1)
        self.failUnless(self.auser.get_deliveryEmailAddressesByKey('fooGroup')\
                        == ['richard@iopen.net','wibble@iopen.net'])
                        
        self.auser.set_disableDeliveryByKey('fooGroup')
        self.failUnless(self.auser.get_deliverySettingsByKey('fooGroup')==0)
        self.failUnless(self.auser.get_deliveryEmailAddressesByKey('fooGroup')==[])
        
        self.auser.set_enableDeliveryByKey('fooGroup')
        self.failUnless(self.auser.get_deliverySettingsByKey('fooGroup')==1)
        self.failUnless(self.auser.get_deliveryEmailAddressesByKey('fooGroup')\
                        == ['richard@iopen.net', 'wibble@iopen.net'])

	self.auser.set_enableDigestByKey('fooGroup')
	self.failUnless(self.auser.get_deliverySettingsByKey('fooGroup')==3)
	self.failUnless(self.auser.get_deliveryEmailAddressesByKey('fooGroup')\
                        == ['richard@iopen.net', 'wibble@iopen.net'])
	self.auser.set_disableDigestByKey('fooGroup')
	self.failUnless(self.auser.get_deliverySettingsByKey('fooGroup')==1)
	

        self.failUnless(self.auser.get_preferredEmailAddresses()\
                        == ['richard@iopen.net', 'wibble@iopen.net'])
        self.failUnless(self.auser.get_emailAddresses() \
                        == ['richard@iopen.co.nz', 'richard@iopen.net', 'wibble@iopen.net'])
        
    def afterClear(self):
        pass    

if __name__ == '__main__':
    framework(descriptions=1, verbosity=1)
else:
    import unittest
    def test_suite():
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(TestCustomUserFolder))
        return suite
