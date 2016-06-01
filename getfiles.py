# #######################
#	By:					#
#	Gamaliel Palomo		#
#	Alfonso Calderon	#
#	Jonatan Mendieta	#
#########################

import os
from fnmatch import fnmatch

def directory(auxPath):
	cont = 0
	indice = 0
	for x in auxPath:
		if x=="/":
			cont=indice
			pass
		indice +=1
		pass
	final=auxPath[cont:]
	return final
	#print(directory)
	pass

def makeTemp(rootPath,varUser,gridUser,varPass,host,port):
	root = rootPath
	#print(root[0])
	pattern = "*.*"
	tempFile = open('temp', 'w')
	for path, subdirs, files in os.walk(root):
	    for name in files:
	        if fnmatch(name, pattern):
	        	pathVar = os.path.join(path, name).replace("\\","/")
	        	#pathVar = auxpathVar.replace("/","\\",1)
	        	if root[0]!="/":
	        		pathVar = "\"file:///"+pathVar+"\" \"ftp://"+gridUser+":"+varPass+"@"+host+":"+port+"/home/"+varUser+directory(root)+pathVar.replace(root,"")+"\""
	        		tempFile.write(pathVar+"\n")
	        	else:
	        		pathVar = "\"file://"+pathVar+"\" \"ftp://"+gridUser+":"+varPass+"@"+host+":"+port+"/home/"+varUser+directory(root)+pathVar.replace(root,"")+"\""
	        		tempFile.write(pathVar+"\n")
	print("-> Control: temp File making was successful")

def kill():
	if(os.path.exists('temp')):
		os.remove('temp')
