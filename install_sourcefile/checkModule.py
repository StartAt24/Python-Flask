#/bin/python3.4

import pip
import os
	
def getCurModules():
	installed_packages = pip.get_installed_distributions()
	installed_packages_list = sorted(["%s %s"% (i.key, i.version) for i in installed_packages])
	for i in installed_packages_list:
		print(i)
	return installed_packages_list


Required = ["click 6.7", "eventlet 0.16.1", "flask 0.12.1", "flask-socketio 2.9.3", 
	"flask-uploads 0.2.1", "greenlet 0.4.12", "itsdangerous 0.24", "jinja2 2.9.6", "markupsafe 1.0",
	"python-engineio 2.0.1", "python-socketio 1.8.4", "pytz 2017.2", "six 1.11.0", "werkzeug 0.12.1"]


def scramble(big, small):
	for i in set(small):
		if small.count(i) <= big.count(i):
			pass
		else:
			return False
	return True
	
	
def checkModules():
	cur = getCurModules()
	if scramble(cur, Required):
		print("---------------------")
		print("Have enough modules? True!")
		print("---------------------")
		return True
	else:		
		print("---------------------")
		print("Have enough modules? False!")
		print("---------------------")
		return False
		
		
if __name__ == '__main__':
	if checkModules() != True:
		os.system("chmod 777 pyInstall.sh")
		os.system("./pyInstall.sh")
	
		
		
		