#
# Skeleton ZopeTestCase
#
import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from Testing import ZopeTestCase

ZopeTestCase.installProduct('CustomUserFolder')

from Products.CustomUserFolder import CustomUserFolder
class TestCustomUserFolder(ZopeTestCase.ZopeTestCase):
    def afterSetUp(self):
        pass
        
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
