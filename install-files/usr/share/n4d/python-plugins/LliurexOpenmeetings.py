#!/usr/bin/env python3
#import xmlrpclib
import os
import sys
import subprocess
import MySQLdb as mdb
import hashlib
import tempfile
import n4d.server.core as n4dcore
import n4d.responses
from n4d.utils import get_backup_name, n4d_mv


class LliurexOpenmeetings:
	
	STUDENT=1
	TEACHER=3
	

	def __init__(self):
		self.core=n4dcore.Core.get_core()
		if __name__ == "__main__" :
	
			om=LliurexOpenmeetings()
			om.add_current_ldap_users()

	def mysql_password(str):
	
		pass1 = hashlib.md5(str).hexdigest()
		return pass1.lower()	
		
	#def mysql_password
	
	def get_ldap_students(self):
		
		students=self.core.get_plugin('Golem').get_student_list()
		return n4d.responses.build_successful_call_response(students)

		#c=xmlrpclib.ServerProxy("https://server:9779")
		#try:
	#		lst=c.get_student_list(self.n4d_key,"Golem")
	#	
	#		if type(lst) != type([]):
	#			return []
	#		return lst
	#	except Exception as e:
	#		print e
	#		return []
		
	#def get_ldap_students
	
	def get_ldap_teachers(self):
		
		teachers=self.core.get_plugin('Golem').get_teacher_list()
		return n4d.responses.build_successful_call_response(teachers)
#		c=xmlrpclib.ServerProxy("https://server:9779")
#		try:
#			lst=c.get_teacher_list(self.n4d_key,"Golem")
#			if type(lst) != type([]):
#				return []
#			return lst
#		except Exception as e:
#			print e
#			return []
		
	#def get_ldap_students
	
	def add_current_ldap_users(self):
	
		if self.check_root():
		
		
			try:
				student_list=self.get_ldap_students()
				teacher_list=self.get_ldap_teachers()
		
				for user in student_list:
					self.add_user(user,self.STUDENT)
			
				for user in teacher_list:
					self.add_user(user,self.TEACHER)	

				#return True
				return n4d.responses.build_successful_call_response()
				
			except Exception as e:
				
				#return False
				return n4d.responses.build_failed_call_response('',str(e))
				
		return n4d.responses.build_failed_call_response('')
		
	#def add_current_ldap_users
	
	def add_user(self,user,user_type):
		
		if self.check_root():
		
			try:
		
				firstname=user["cn"]
				lastname=user["sn"]
				language_id="8"
				#level_id=str(user_type)
				login=user["uid"]
				#password=mysql_password("lliurex")
				password="NULL"

				con=mdb.connect('localhost',self.mysql_user,self.mysql_passwd,"openmeetings")
				cur=con.cursor()
				
				query="SELECT * FROM om_user WHERE login='%s'"%login
				cur.execute(query)
				data=cur.fetchone()
				
				if data==None:
					

					print ("* Adding %s to OpenMeetings ... {}".format(login))
					#query="INSERT INTO `om_user` VALUES (NULL,NULL,NOW(),1,'\0',NULL,NULL,'%s','\0',%s,NOW(),'%s',0,%s,'%s',NULL,%s,NULL,NOW(),NULL,1,'\0','\0','\1',NOW(),1,'Europe/Madrid','user',NULL,'','',NULL,NULL)"
					query="INSERT INTO `om_user` VALUES (NULL,NULL,NOW(),'\0',NULL,NULL,NULL,'%s','\0',%s,NOW(),'%s',0,'%s',NULL,%s,NULL,NOW(),NULL,1,'\0','\0',1,NOW(),'Europe/Madrid','user',NULL,'','',NULL,NULL)"
					#def_query=query%(firstname,language_id,lastname,level_id,login,password)
					def_query=query%(firstname,language_id,lastname,login,password)

					cur.execute(def_query)	
					cur.execute("SELECT MAX(id) from om_user WHERE login='%s'"%login)
					data=cur.fetchone()
					id=str(data[0])
					cur.execute("INSERT INTO organisation_users (user_id,organisation_id) VALUES (%s,2)"%id)
					con.commit()
					
				return n4d.responses.build_successful_call_response()
				
			except Exception as e:
				
				print (e)
				return n4d.responses.build_failed_call_response('',str(e))
		
		return n4d.responses.build_failed_call_response('')
		#return False
	
	#def add_student
	
	def delete_user(self,user):

		if self.check_root():
				
			try:

				con=mdb.connect('localhost',self.mysql_user,self.mysql_passwd,"openmeetings")
				cur=con.cursor()
				
					
				query="SELECT * FROM om_user WHERE login='%s'"%user["uid"]
				cur.execute(query)
				data=cur.fetchone()
				
				if data==None:
					return True
						
				query="UPDATE om_user SET deleted='\1' WHERE login='%s'"%user["uid"]
				cur.execute(query)
				con.commit()
				
				#return True
				return n4d.responses.build_successful_call_response()
					
			except Exception as e:
				print (e)
				#return False
				return n4d.responses.build_failed_call_response('',str(e))
					
		return n4d.responses.build_failed_call_response('')
#		return False
		
	#def delete_user
	
	def check_root(self):
	
		try:
			f=open("/etc/n4d/key")
			self.n4d_key=f.readline().strip("\n")
			f.close()
			p=subprocess.run(["mysql_root_passwd","-g"],capture_output=True)
			#p=subprocess.Popen(["mysql_root_passwd -g"],shell=True,stdout=subprocess.PIPE)
			#output=p.communicate()[0].strip("\n")
			self.mysql_user="root"
			self.mysql_passwd=p.stdout.decode().strip("\n")
			
			return True
			
		except Exception as e:
			print("You need root privileges: {}".format(e))
			
			return False
			#sys.exit(0)
			
	#def check_root
	
	
	def remote_initialization(self, template_content):
		
		try:
		
			file_path=tempfile.mktemp()
			f=open(file_path,"w")
			f.write(template_content)
			f.close()
		
			output=subprocess.Popen(["lliurex-openmeetings -t %s"%file_path],shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
		
			#return [True,output]
			return n4d.responses.build_successful_call_response(output)
					
			
		except Exception as e:
			
				#return [False,str(e)]
			return n4d.responses.build_failed_call_response('',str(e))
		
		
	#def remote_initialization
	
	def remote_service_start(self):
		
		state=objects["ZCenterVariables"].get_state("lliurex-openmeetings")
		
		if state==1:
			os.system("lliurex-openmeetings-service start")
		
			#return [True,""]
			return n4d.responses.build_successful_call_response()
		else:
			
				#return [False,"NOT_INITIALIZED"]
			return n4d.responses.build_failed_call_response('',str("NOT_INITIALIZED"))
		
	#def remote_service_start()
	
	def remote_service_stop(self):
		
		state=objects["ZCenterVariables"].get_state("lliurex-openmeetings")
		
		if state==1:
			os.system("lliurex-openmeetings-service stop")
			return n4d.responses.build_successful_call_response()
			#return [True,""]
		else:
			#return [False,"NOT_INITIALIZED"]
			return n4d.responses.build_failed_call_response('',str("NOT_INITIALIZED"))
		
	#def remote_service_start()
	
	def remote_service_is_running(self):
		
		
		state=objects["ZCenterVariables"].get_state("lliurex-openmeetings")
		
		if state==1:
		
			p=subprocess.Popen(["lliurex-openmeetings-service status"],shell=True,stdout=subprocess.PIPE).communicate()
			if "STOPPED" in p[0]:
					#return [False,""]
				return n4d.responses.build_failed_call_response('',str("Stopped"))
			else:
					#return [True,""]
				return n4d.responses.build_successful_call_response()
		
		
		#return [False,-1]
		return n4d.responses.build_failed_call_response('',str("stopped"))
		
	#def remote_service_status
	
	
	
#class OMUsers


