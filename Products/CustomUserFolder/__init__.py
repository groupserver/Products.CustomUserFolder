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
