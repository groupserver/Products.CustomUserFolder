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
import codecs
import os
from setuptools import setup, find_packages
from version import get_version

version = get_version()

with codecs.open('README.rst', encoding='utf-8') as f:
    long_description = f.read()
with codecs.open(os.path.join("docs", "HISTORY.rst"),
                 encoding='utf-8') as f:
    long_description += '\n' + f.read()

setup(name='Products.CustomUserFolder',
      version=get_version(),
      description="",
      long_description=long_description,
      classifiers=[
          "Programming Language :: Python",
      ],
      keywords='',
      author='Richard Waid',
      author_email='richard@iopen.net',
      maintainer='Michael JasonSmith',
      maintainer_email='mpj17@onlinegroups.net',
      url='http://groupserver.org',
      license='ZPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['Products'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'sqlalchemy',
          'zope.component',
          'zope.interface',
          'zope.schema',
          'zope.sqlalchemy',
          'AccessControl',
          'Zope2',
          'gs.database',
          'gs.email',
          'gs.image',
          'Products.NuxUserGroups',
          'Products.XWFCore',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
