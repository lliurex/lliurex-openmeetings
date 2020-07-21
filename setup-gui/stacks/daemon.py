#!/usr/bin/python3
import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QSlider, QLabel, QWidget, QPushButton,QVBoxLayout,QCheckBox,QGridLayout,QHBoxLayout,QComboBox,QCheckBox, QListWidget,QFileDialog,QFrame
from PyQt5 import QtGui
from PyQt5.QtCore import Qt,QSize
from appconfig.appConfigStack import appConfigStack as confStack
from appconfig.appConfigN4d import appConfigN4d as n4d
import tempfile

import gettext
_ = gettext.gettext


class daemon(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("daemon load")
		self.description=(_("Openmeetings daemon setup"))
		self.menu_description=(_("Conifgure openmeetings service setup"))
		self.icon=('openmeetings')
		self.tooltip=(_("Start/stop the service or launch at boot"))
		self.index=2
		self.enabled=True
		self.level='system'
		self.n4d=n4d()
#		self.hideControlButtons()
		self.setStyleSheet(self._setCss())
	#def __init__
	
	def _load_screen(self):

		box=QGridLayout()
		self.btn_service=QPushButton()
		self.btn_service.setCheckable(True)
		self.btn_service.toggled.connect(self._ctrlRun)
		box.addWidget(self.btn_service,0,0,1,1,Qt.AlignCenter)
		self.chk_startup=QCheckBox(_("Launch at startup"))
		box.addWidget(self.chk_startup,1,0,1,1,Qt.AlignTop)
		self.chk_kurento=QCheckBox(_("Disable videconference (remove webcam and microphone support)"))
		box.addWidget(self.chk_kurento,2,0,1,1,Qt.AlignTop)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def _check_isRunning(self):
		cmd=["/usr/sbin/lliurex-openmeetings-service","status"]
		a=subprocess.check_output(cmd).decode().strip()
		if a=="STOPPED":
			return False
		else:
			return True
	#def _check_isRunning

	def _ctrlRun(self,*args):
		if self._check_isRunning():
			self.n4d.n4dQuery("LliurexOpenmeetings","remote_service_stop")
		else:
			self.n4d.n4dQuery("LliurexOpenmeetings","remote_service_start")
		self.updateScreen()
	#def _ctrlRun

	def _getServiceStatus(self):
		if os.path.isfile("/etc/systemd/system/lliurex-openmeetings.service"):
			return True
		else:
			return False
	#def _getStatus

	def _ctrlService(self,*args):
		self.updateScreen()
	#def _ctrlService

	def updateScreen(self):
		if self._check_isRunning():
			self.btn_service.setText(_("Stop service"))
			self.btn_service.setStyleSheet("background:red;color:white")
		else:
			self.btn_service.setText(_("Start service"))
			self.btn_service.setStyleSheet("background:green;color:black")

		self.chk_startup.setCheckState(False)
		if self._getServiceStatus():
			self.chk_startup.setCheckState(True)
		return True
	#def _udpate_screen
	
	def writeConfig(self):
		if self.chk_startup.checkState():
			cmd=["/bin/systemctl","enable","lliurex-openmeetings"]
		else:
			cmd=["/bin/systemctl","disable","lliurex-openmeetings"]
		subprocess.run(cmd)
		
		if self.chk_kurento.checkState():
			cmd=["/bin/systemctl","disable","kurento-media-server"]
		else:
			cmd=["/bin/systemctl","enable","kurento-media-server"]
		subprocess.run(cmd)
		return True
	#def writeConfig

	def _setCss(self):
		css="""
			#error{
				color:white;
			}"""
		return(css)
	#def _setCss

