# -*- coding: utf-8 -*-
import os
import platform

if 'windows' in platform.platform().lower():
    MYSQL_HOST = "bgmi.acg.tools"
    MYSQL_DBNAME = "bgm_ip_viewer"
    MYSQL_USER = "root"
    MYSQL_PASSWORD = 'password'
else:
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_DBNAME = os.environ.get('MYSQL_DBNAME')
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
