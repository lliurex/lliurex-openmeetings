#!/usr/bin/env python3
import sys
import os
from PySide2.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig
PROJECT="OpenMeetings"

app=QApplication(["%s Setup"%PROJECT])
config=appConfig("%s"%PROJECT,{'app':app})
config.setTextDomain('lliurex-openmeetings-setup')
config.setWiki('https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Lliurex+Lab+%28bionic%29')
config.setRsrcPath("/usr/share/lliurex-openmeetings/rsrc")
config.setIcon('%s'%PROJECT.lower())
config.setBanner('%s_banner.png'%PROJECT.lower())
config.setBackgroundImage('%s_login.svg'%PROJECT.lower())
config.setConfig(confDirs={'system':'/usr/share/lliurex-openmeetings','user':'%s/.config'%os.environ['HOME']},confFile="%s.conf"%PROJECT.lower())
config.Show()
config.setFixedSize(config.width(),config.height())

app.exec_()
