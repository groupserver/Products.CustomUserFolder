# -*- coding: utf-8 -*-
############################################################################
#
# Copyright © 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012,
# 2013, 2014 OnlineGroups.net and Contributors.
#
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
############################################################################
#lint:disable
import CustomUserFolder
import CustomUser
import audituser

#lint:enable
from AccessControl import ModuleSecurityInfo
from AccessControl import allow_class

from queries import UserQuery
q_security = ModuleSecurityInfo('Products.CustomUserFolder.queries')
q_security.declarePublic('UserQuery')
allow_class(UserQuery)

from userinfo import GSUserInfo, GSLoggedInUserFactory, GSAnonymousUserInfo
m_security = ModuleSecurityInfo('Products.CustomUserFolder.userinfo')
m_security.declarePublic('GSUserInfo')
m_security.declarePublic('GSLoggedInUserFactory')
m_security.declarePublic('GSAnonymousUserInfo')
allow_class(GSUserInfo)
allow_class(GSLoggedInUserFactory)
allow_class(GSAnonymousUserInfo)


def initialize(context):
    # import lazily and defer initialization to the module
    CustomUserFolder.initialize(context)
