#!/usr/bin/python3
import sys
import os
import subprocess
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QGridLayout,QHBoxLayout,QComboBox,QCheckBox, QListWidget,QFileDialog,QFrame
from PyQt5 import QtGui
from PyQt5.QtCore import Qt,QSize
from appconfig.appConfigStack import appConfigStack as confStack
import tempfile

import gettext
_ = gettext.gettext

class validate():
	def __init__(self):
		self.err=0
		self.errMsg=""
		self.errCode={"10":_("Invalid username"),"20":_("Special characters not allowed"),"30":_("Invalid password lenght"),"40":_("No special characters detected")}
	#def __init__
	
	def chkTxt(self,txt,alphaStrict=False):
		self.err=0
		if (len(txt)>50 or len(txt)<1):
			self.err=10
		else:
			if (alphaStrict==True and txt.isalnum()==False): 
				self.err=20
			elif txt.strip()=="root":
				self.err=10
				
		self.errMsg=self.errCode.get(str(self.err),"")
	#def chkTxt
	
	def chkPwd(self,pwd,alphaStrict=False):
		self.err=0
		if (len(pwd)>50 or len(pwd)<8):
			self.err=30
		else:
			if (alphaStrict==True and pwd.isalnum()==False): 
				self.err=20
			elif (alphaStrict==False and pwd.isalnum()==True):
				self.err=40
		self.errMsg=self.errCode.get(str(self.err),"")
	#def chkPwd
	
	def chkMail(self,mail):
		mailstring=str(mail)
		retval=False
		if "@" in mailstring and len(mailstring)<75:
			mailparts=mailstring.split("@")
			if ("." in mailparts[1]):
				domain=mailparts[1].split(".")
				if (len(domain[1])>=2 and domain[1].isalnum() and len(domain[0])>=2 and domain[0].isalnum() and len(mailparts[0])>=2 and mailparts[0].isalnum()):
					retval=True
		return retval

class config(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("config load")
		self.description=(_("Openmeetings setup"))
		self.menu_description=(_("Main configure for openmeetings"))
		self.menu_description=(_("Configure database access and users"))
		self.icon=('openmeetings')
		self.tooltip=(_("Configure database access and users for openmeetings"))
		self.index=1
		self.enabled=True
		self.level='system'
#		self.hideControlButtons()
		self.setStyleSheet(self._setCss())
	#def __init__
	
	def _load_screen(self):

		box=QGridLayout()
		box.addWidget(QLabel(_("Database user")),0,0,1,1,Qt.AlignBottom)
		self.inp_user=QLineEdit()
		self.inp_user.setPlaceholderText(_("openmeetingsuser"))
		box.addWidget(self.inp_user,1,0,1,1,Qt.AlignTop)
		box.addWidget(QLabel(_("User password")),2,0,1,1,Qt.AlignTop)
		box.addWidget(QLabel(_("* At least 8 character")),3,0,1,1,Qt.AlignTop)
		box.addWidget(QLabel(_("SPECIAL CHARACTERS NOT ALLOWED")),4,0,1,1,Qt.AlignTop)
		self.inp_pwd=QLineEdit()
		self.inp_pwd.setPlaceholderText(_("p4ssw0rd"))
		box.addWidget(self.inp_pwd,5,0,1,1,Qt.AlignTop)
		self.inp_pwd2=QLineEdit()
		self.inp_pwd2.setPlaceholderText(_("p4ssw0rd"))
		box.addWidget(self.inp_pwd2,6,0,1,1,Qt.AlignTop)
		box.addWidget(QLabel(_("Admin user")),7,0,1,1,Qt.AlignBottom)
		self.inp_admin=QLineEdit()
		self.inp_admin.setPlaceholderText(_("admin"))
		box.addWidget(self.inp_admin,8,0,1,1,Qt.AlignTop)
		box.addWidget(QLabel(_("Admin password")),9,0,1,1,Qt.AlignTop)
		box.addWidget(QLabel(_("* At least 8 character")),10,0,1,1,Qt.AlignTop)
		box.addWidget(QLabel(_("* Uppercase and lowercase\n* Alphanumeric\n* With special characters (!, #, &...) ")),11,0,1,1,Qt.AlignTop)
		self.inp_apwd=QLineEdit()
		self.inp_apwd.setPlaceholderText(_("P4ssw0rd!"))
		box.addWidget(self.inp_apwd,12,0,1,1,Qt.AlignTop)
		self.inp_apwd2=QLineEdit()
		self.inp_apwd2.setPlaceholderText(_("P4ssw0rd!"))
		box.addWidget(self.inp_apwd2,13,0,1,1,Qt.AlignTop)
		box.addWidget(QLabel(_("Admin email")),14,0,1,1,Qt.AlignTop)
		self.inp_mail=QLineEdit()
		self.inp_mail.setPlaceholderText(_("lluna@lliurex.net"))
		box.addWidget(self.inp_mail,15,0,1,1,Qt.AlignTop)
		self.setLayout(box)
		self.updateScreen()
		return(self)
	#def _load_screen

	def _loadAppData(self,air=""):
		pass
	#def _loadAppData

	def _validate(self):
		val=validate()
		retval=True
		#Check a valid username is given
		val.chkTxt(self.inp_user.text(),True)
		if val.errMsg:
			retval=False
			self.inp_user.setObjectName("error")
			self._debug(val.errMsg)
		else:
			if self.inp_pwd.text()!=self.inp_pwd2.text():
				retval=False
				self.inp_pwd.setObjectName("error")
				err=_("Passwords don't match")
				self._debug(err)
			else:
				val.chkPwd(self.inp_pwd.text(),True)
				if val.errMsg:
					retval=False
					self.inp_pwd.setObjectName("error")
					self._debug(val.errMsg)
		if val.errMsg=="":
			val.chkTxt(self.inp_admin.text(),True)
			if val.errMsg:
				retval=False
				self.inp_admin.setObjectName("error")
				self._debug(val.errMsg)
			else:
				if self.inp_apwd.text()!=self.inp_apwd2.text():
					retval=False
					self.inp_apwd.setObjectName("error")
					err=_("Passwords don't match")
					self._debug(err)
				else:
					val.chkPwd(self.inp_apwd.text(),False)
					if val.errMsg:
						retval=False
						self.inp_apwd.setObjectName("error")
						self._debug(val.errMsg)
		if val.errMsg=="":
			if (val.chkMail(self.inp_mail.text()))==False:
				retval=False
				self.inp_mail.setObjectName("error")
				self._debug(_("Invalid mail"))
	
		return(retval)

	def updateScreen(self):
		return True
	#def _udpate_screen
	
	def writeConfig(self):
		val=self._validate()
		if val:
			tmpf="/tmp/lliurex-openmeetings.conf"
			try:
				with open(tmpf,"w") as f:
					f.write("[openmeetings]\n")
					f.write("admin=%s\n"%self.inp_admin.text())
					f.write("password=%s\n"%self.inp_apwd.text())
					f.write("db_user=%s\n"%self.inp_user.text())
					f.write("db_pass=%s\n"%self.inp_pwd.text())
					f.write("email=%s\n"%self.inp_mail.text())
			except Exception as e:
				print("Failed when writing conffig: %s"%e)
				val=False
			if val:
				cmd=["/usr/sbin/lliurex-openmeetings","-t","/tmp/lliurex-openmeetings.conf"]
				try:
					a=subprocess.run(cmd)
				except Exception as e:
					print("Failed when updating config: %s"%e)
					val=False
				if a.returncode:
					print("Failed when running lliurex-openmeetings")
					val=False
		if val:
			self.showMsg(_("Openmeetings configuration updated"))
		else:
			self.showMsg(_("An error ocurred. Check permissions"))
	#def writeConfig

	def _setCss(self):
		css="""
			#error{
				color:white;
			}"""
		return(css)
	#def _setCss

