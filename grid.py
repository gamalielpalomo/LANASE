
# #######################
#	By:					#
#	Gamaliel Palomo		#
#	Alfonso Calderon	#
#	Jonatan Mendieta	#
#########################

#!
# -*- coding: utf-8 -*-
#------------------ LIBRARIES
from Tkinter import *
import ttk
import tkMessageBox
from tkFileDialog import *
from Tkinter import PhotoImage
from PIL import ImageTk, Image
from subprocess import call
import paramiko
import getfiles
import threading
import time
import sys

#----------------- FUNCTIONS
def getVal(linetoread):
	cont1 = 0
	cont2 = 0
	indice = 0
	for x in linetoread:
		if x=="\"":
			cont1=cont2
			cont2=indice
			pass
		indice +=1
		pass
	final=linetoread[cont1+1:cont2]
	return final
	pass

def loggin(x):
	global monitor
	global demultThread
	varList.set("")
	if(varUser.get()=="")or(varPass.get()==""):
		print("-> Control: Authentication fields are empty")
		varStatus.set("Entry fields should not be empty")
		root.update()
	else:
		try:
			ssh = paramiko.SSHClient()
			ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			ssh.connect(hostname=hostName, port=sshPort, username=varUser.get(), password=varPass.get())
			
			print("-> Control: Authentication successful for user: '"+varUser.get()+"'")
			varStatus.set("")
			root.update()
			if x==1:
				ssh.close()	
				buildCommand()
			elif x==2:
				global labelList
				labelList.delete(0,END)
				(stdin, stdout, stderr) = ssh.exec_command('ls ')
				for line in stdout.readlines():
					#varList.set(varList.get()+line+" ")
					l=u""+line
					labelList.insert(END,l)
				ssh.close()	
			elif (x==3)and(varDirectory.get()!=""):
				user=varUser.get()
				directory= "/home/"+varUser.get()+"/"+varDirectory.get().replace(" ","\ ")
				newDirectory = "/home/"+varUser.get()+"/"+"RESULTS_"+varDirectory.get().replace(" ","\ ")

				(stdin, stdout, stderr) = ssh.exec_command('mkdir '+newDirectory)
				for line in stdout.readlines():
					print (line)
				varStatus.set("Demultiplexing file...")
				root.update()
				aux = directory.replace("\n","")
				aux2 = newDirectory.replace("\n","")
				command = "bcl2fastq --runfolder-dir "+aux+"/"+ " --output-dir " + aux2+"/"+" --input-dir " +aux+"/Data/Intensities/BaseCalls/"
				demultThread = threading.Thread(target=demultFunc, args=(command,))
				monitor = threading.Thread(target=monitoring)
				ssh.close()	
				demultThread.start()
				monitor.start()
			elif x==4:
				ssh.close()
				download()
			ssh.close()	
		except paramiko.AuthenticationException: 
			print("-> Control: Failed to authenticate user '"+varUser.get()+"'")
			varStatus.set("Failed to authenticate user")
			labelList.delete(0,END)
			root.update()

def compare():
	loggin(1)

def hide():
	loggin(2)

def demult():
	loggin(3)

def down():
	loggin(4)

def onselect(evt):
	global labelList
	index=labelList.curselection()
	varDirectory.set(labelList.get(index))

def more():
	global buttonDemultiplexing, labelDirectory, entryDirecotry, buttonList, buttonHide, labelList, buttonDownload, iconList, iconHide, iconDemult, iconDownload
	buttonMore.config(state=DISABLED)
	labelDirectory = ttk.Label(mainframe, text="Directory:", style='label.TLabel')
	labelDirectory.grid(row=4, sticky=(N, W, E))
	entryDirecotry = ttk.Entry(mainframe, style='entry.TEntry', textvariable=varDirectory)
	entryDirecotry.grid(row=4, column=1, sticky=(N,W,E))
	buttonList = ttk.Button(mainframe, compound=LEFT, image=iconList, text="List",command=hide)
	buttonList.grid(row=4,column=2, sticky=(W,E))
	buttonDemultiplexing = ttk.Button(mainframe, compound=LEFT, image=iconDemult, text="Demultiplex", command=demult)
	buttonDemultiplexing.grid(row=4,column=4, sticky=(W,E))
	buttonHide = ttk.Button(mainframe, compound=LEFT, image=iconHide, text="Hide",command=hideMe)
	buttonHide.grid(row=5,column=4,sticky=(N, W, E))
	buttonDownload=ttk.Button(mainframe, compound=LEFT, image=iconDownload, text="Download", command=down)
	buttonDownload.grid(row=4,column=3, sticky=(W,E))
	labelList = Listbox(mainframe)
	labelList.grid(row=5, column=2,columnspan=2, sticky=(N, W, E, S))
	labelList.bind('<<ListboxSelect>>', onselect)
	root.update()

def hideMe():
	global labelList, labelDirectory, entryDirecotry, buttonDemultiplexing, buttonList, buttonHide, buttonDownload
	labelList.grid_forget()
	labelDirectory.grid_forget()
	entryDirecotry.grid_forget()
	buttonDemultiplexing.grid_forget()
	buttonList.grid_forget()
	buttonHide.grid_forget()
	buttonDownload.grid_forget()
	varDirectory.set("")
	buttonMore.config(state=NORMAL)
	root.update()

	
def download():
	global sendThread
	global monitor

	if varDirectory.get()!="":
		fileSelected = varDirectory.get().replace("\n","")
		root.filename = askdirectory(initialdir = "C:/", title = "Select Directory")
		path=(root.filename).replace("C:/","")
		if path!="":
			if fileSelected.find(".")!=-1:		#File Selected for download
				print("File selected")
				fileSelected = varDirectory.get().replace("\n","")
				command = "globus-url-copy -p 16 -tcp-bs 20MB -r \"ftp://"+gridUser+":"+gridPass+"@"+hostName+":"+gridPort+"/home/"+varUser.get()+"/" +fileSelected+"\""+ " file:///"+path+"/"
				print (command)
				varStatus.set("Downloading file...")
				root.update()
				sendThread = threading.Thread(name="sendThread",target=executeCommand, args=(command,))
				monitor = threading.Thread(target=monitoring, name="monitor")
				sendThread.start()
				monitor.start()
			else:
				print("Directory selected")		#Directory delected for download
				try:
					ssh = paramiko.SSHClient()
					ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
					ssh.connect(hostname=hostName, port=sshPort, username=varUser.get(), password=varPass.get())
					tempFile = open('temp2', 'w')

					(stdin, stdout, stderr) = ssh.exec_command('find /home/'+varUser.get()+"/"+fileSelected+" -type f")
					x=0
					for line in stdout.readlines():
						
						line=line.replace("\n","")
						pathVar = "\"ftp://"+gridUser+":"+gridPass+"@"+hostName+":"+gridPort+line+"\""+" \"file:///"+path+"/" +line.replace("/home/"+varUser.get()+"/","") +"\""
						tempFile.write(pathVar+"\n")
						print (line)
					ssh.close()

					command = "globus-url-copy -p 16 -tcp-bs 20MB -r -cd -f temp2"
					varStatus.set("Downloading directory...")
					root.update()
					sendThread = threading.Thread(name="sendThread",target=executeCommand, args=(command,))
					monitor = threading.Thread(name="monitor",target=monitoring)
					sendThread.start()
					monitor.start()

					
				except paramiko.AuthenticationException: 
					print("-> Control: Failed to authenticate user '"+varUser.get()+"'")
					varStatus.set("Filed to authenticate user")
					root.update()
	else:
		print("Select a file")


def getFile():
	global varControl
	varControl=1

	if(varUser.get()=="")or(varPass.get()==""):
		print("-> Control: Authentication fields are empty")
		varStatus.set("Entry fields should not be empty")
		root.update()
	else:
		varStatus.set("")
		root.update()
		root.filename = askopenfilename(initialdir = "C:/", title = "Select file")
		filePath.set(root.filename)
		print("-> Control: (getFile). File selected is: "+filePath.get())


def getDirectory():
	global varControl
	varControl=2
	
	if(varUser.get()=="")or(varPass.get()==""):
		print("-> Control: Authentication fields are empty")
		varStatus.set("Entry fields should not be empty")
		root.update()
	else:
		varStatus.set("")
		root.update()
		root.filename = askdirectory(initialdir = "C:/", title = "Select Directory")
		filePath.set(root.filename)
		auxPath = filePath.get()
		print("-> Control: (getDirectory). Directory selected is: "+filePath.get())
		getfiles.makeTemp(auxPath,varUser.get(),gridUser,gridPass,hostName,gridPort)
	

def buildCommand():
	global sendThread
	global monitor
	path = StringVar()
	path = u""+filePath.get()
	if(path == ""):
		varStatus.set("No file selected")
		root.update()
		print("-> Control: No file selected")
	else:
		path = filePath.get().replace("C:/","")
		if varControl==1:
			path = "\""+path+"\""
			#aux = "u\'"+path+"\'"
			#var = aux.decode('utf-8')
			command = StringVar()
			command = "globus-url-copy -p 16 -tcp-bs 20MB -r file:///"+path+" ftp://"+gridUser+":"+gridPass+"@"+hostName+":"+gridPort+"/home/"+varUser.get()+"/"
			print (command)
			print("-> Control: Sending file")
			varStatus.set("Sending file...")
			root.update()
			sendThread = threading.Thread(name="sendThread",target=executeCommand, args=(command,))
			monitor = threading.Thread(target=monitoring, name="monitor")
			sendThread.start()
			monitor.start()

		elif varControl==2:
			command = "globus-url-copy -p 16 -tcp-bs 20MB -r -cd -f temp"
			print("-> Control: Sending directory")
			varStatus.set("Sending directory...")
			root.update()
			sendThread = threading.Thread(name="sendThread",target=executeCommand, args=(command,))
			monitor = threading.Thread(name="monitor",target=monitoring)
			sendThread.start()
			#sendThread.join()
			monitor.start()
		else:
			print("-> Control: Not an allowed option")

def executeCommand(commandToExec):
	call(commandToExec.encode(sys.stdout.encoding),shell=True)

def showInfo():
	tkMessageBox.showinfo("About","LANASE GridFTP File Transfer\nVersion 1.1.2\nDesigned and developed by:\nGamaliel Palomo\nAlfonso Calderon\nJonatan Mendieta")

#----------------------- THREAD FUNCTIONS
def demultFunc(command):
	try:
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname=hostName, port=sshPort, username=varUser.get(), password=varPass.get())
		(stdin, stdout, stderr) = ssh.exec_command(command)
		for line in stdout.readlines():
			print ("  "+line)
		for line in stderr.readlines():
			print ("  "+line)
	except paramiko.AuthenticationException: 
		print("-> Control: Failed to authenticate user '"+varUser.get()+"'")
		varStatus.set("Filed to authenticate user")
		root.update()

def monitoring():
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(hostname=hostName, port=sshPort, username=varUser.get(), password=varPass.get())
	global buttonFile
	global buttonDemultiplexing, buttonDownload
	while sendThread.isAlive():
		buttonSend.config(state=DISABLED)
		buttonDemultiplexing.config(state=DISABLED)
		buttonDownload.config(state=DISABLED)
		time.sleep(1)
		varStatus.set("Sending file...")
		print "-> control: sendThread Alive"
	while demultThread.isAlive():
		buttonSend.config(state=DISABLED)
		buttonDemultiplexing.config(state=DISABLED)
		buttonDownload.config(state=DISABLED)
		time.sleep(1)
		varStatus.set("Demultiplexing file...")
		print "-> control: demultThread Alive"
	print "-> Control: Modifying permissions"
	cmd = "sudo /etc/./chownscript.sh "+varUser.get()
	#cmd = "ls"
	print (cmd)
	(stdin, stdout, stderr) = ssh.exec_command(cmd)
	for line in stdout.readlines():
			print ("  "+line)
	for line in stderr.readlines():
			print ("  "+line)
	print "-> Control: Modifying permissions: Done!"
	ssh.close()
	buttonSend.config(state=NORMAL)
	buttonDemultiplexing.config(state=NORMAL)
	buttonDownload.config(state=NORMAL)
	varStatus.set("Completed!")
	print("-> Control: Transfer completed")

#-------------- ---MAIN FRAME BUILDING
root = Tk()
root.title("LANASE GridFTP File transfer")
root.iconbitmap("icon-lanase.ico")
root.resizable("false", "false")
mainframe = ttk.Frame(root, padding="10 10 10 1", style='frame.TFrame')
mainframe.grid(row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)


#------------- ----STYLES
style = ttk.Style()
style.configure('frame.TFrame', background='#7c94b6')
style.configure('label.TLabel', background='#7c94b6', foreground='white', font=('Estrangelo Edessa',16,'bold'))
style.configure('labelInfo.TLabel', background='#7c94b6', foreground='white', font=('Estrangelo Edessa',10,'bold'))
style.configure('labelFile.TLabel', background='#7c94b6', foreground='black', font=('Estrangelo Edessa',30))
style.configure('entry.TEntry', background='#7c94b6')

#----------------- LOGOS
logoLanase = ImageTk.PhotoImage((Image.open('lanase-logo.png').resize((250,64),Image.ANTIALIAS)))
logoEnes = ImageTk.PhotoImage((Image.open('logo-enes.png').resize((100,61),Image.ANTIALIAS)))
logoUagro = ImageTk.PhotoImage((Image.open('logo-uagro.png').resize((100,61),Image.ANTIALIAS)))
logoConacyt = ImageTk.PhotoImage((Image.open('logo-conacyt.png').resize((100,58),Image.ANTIALIAS)))
labelLogoLanase = ttk.Label(mainframe, image=logoLanase, style='label.TLabel').grid(row=0, columnspan=2)
labelLogoEnes = ttk.Label(mainframe, image=logoEnes,style='label.TLabel').grid(row=0, column=2)
labelLogoUagro = ttk.Label(mainframe, image=logoUagro,style='label.TLabel').grid(row=0, column=3)
labelLogoConacyt = ttk.Label(mainframe, image=logoConacyt,style='label.TLabel').grid(row=0, column=4)
iconInfo = ImageTk.PhotoImage(Image.open('info.png'))
iconList = ImageTk.PhotoImage(Image.open('search.png'))
iconDoc = ImageTk.PhotoImage(Image.open('business.png'))
iconDir = ImageTk.PhotoImage(Image.open('interface.png'))
iconSend = ImageTk.PhotoImage(Image.open('up-arrow.png'))
iconMore = ImageTk.PhotoImage(Image.open('bars.png'))
iconHide = ImageTk.PhotoImage(Image.open('arrows.png'))
iconDemult = ImageTk.PhotoImage(Image.open('tool.png'))
iconDownload = ImageTk.PhotoImage(Image.open('download.png'))

#----------------- FORMS
varUser = StringVar()
varPass = StringVar()
labelUser = ttk.Label(mainframe, text="Username:", style='label.TLabel').grid(row=2, sticky=(N, W, E, S))
labelPass = ttk.Label(mainframe, text="Password:", style='label.TLabel').grid(row=3, sticky=(N, W, E, S))
entryUser = ttk.Entry(mainframe, style='entry.TEntry', textvariable=varUser)
entryUser.grid(row=2, column=1)
entryPass = ttk.Entry(mainframe, style='entry.TEntry', textvariable=varPass,show="*").grid(row=3, column=1)
filePath = StringVar()
labelPath =  ttk.Entry(mainframe, textvariable=filePath, style='labelFile.TLabel', width=60).grid(row=2,column=2,columnspan=3,)
varStatus = StringVar()
labelStatus = ttk.Label(mainframe, textvariable=varStatus, style='label.TLabel').grid(rowspan=2,columnspan=3,row=2,column=2)
buttonInfo = ttk.Button(mainframe,image=iconInfo,command=showInfo)
buttonInfo.grid(column=4,sticky=(E))
buttonMore = ttk.Button(mainframe,compound=LEFT, image=iconMore, text="More", command=more)
buttonMore.grid(row=1,column=1,sticky=(W,E))
buttonFile = ttk.Button(mainframe,compound=LEFT, image=iconDoc, text="File", command=getFile)
buttonFile.grid(row=1,column=2,sticky=(W,E))
buttonDirectory = ttk.Button(mainframe,compound=LEFT, image=iconDir, text="Directory", command=getDirectory).grid(row=1,column=3,sticky=(W,E))
buttonSend = ttk.Button(mainframe,compound=LEFT, image=iconSend, text="Send",command=compare)
buttonSend.grid(row=1,column=4,sticky=(W,E))
buttonDemultiplexing = ttk.Button()
varDirectory = StringVar()
varList = StringVar()
labelList = Listbox()
buttonList = ttk.Button()
buttonHide = ttk.Button()
buttonDownload = ttk.Button()
labelDirectory = ttk.Label()
entryDirecotry = ttk.Entry()

#------------------ MAIN

lines = [line.rstrip('\n') for line in open('LANASE_config.conf')]
varControl = -1
hostName = str(getVal(lines[0])).replace(" ","")
sshPort = int(getVal(lines[1]))
gridPort = str(getVal(lines[2])).replace(" ","")
gridUser = str(getVal(lines[3])).replace(" ","")
gridPass = str(getVal(lines[4]))
sendThread = threading.Thread()
demultThread = threading.Thread()
monitor = threading.Thread()
for child in mainframe.winfo_children(): child.grid_configure(padx=1, pady=5)
entryUser.focus()
root.mainloop()
