import subprocess
import xmlrpclib

#ARGV -> List of users,
#User -> dictionary:
#	"group_type" [  Students / Teachers ]
#	"uid"
#	"cn"
#	"sn"

try:

	f=open("/etc/n4d/key")
	n4d_key=f.readline().strip("\n")
	f.close()

	client=xmlrpclib.ServerProxy("https://localhost:9779")

	if NEVERLAND_VAR == "add_user":
		
		STUDENT=1
		TEACHER=3
		
		for user in ARGV:
		
			user_type=STUDENT
			if user["group_type"]=="Teachers":
				user_type=TEACHER
		
			client.add_user(n4d_key,"LliurexOpenmeetings",user,user_type)

	if NEVERLAND_VAR == "delete_user": 
		
		for user in ARGV:
			client.delete_user(n4d_key,"LliurexOpenmeetings",user)
			

	if NEVERLAND_VAR == "update_user": 
		
		pass


except Exception as e:
	print "[OpenMeetings] Hook error:"
	print e