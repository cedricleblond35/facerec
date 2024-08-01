#!/usr/bin/python3

import threading
import time

import sys
import json
#bibliothèque face
from PIL import Image
import face_recognition
import os.path

import urllib.request
import time



exitFlag = 0

directory = "/tmp/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

class myThread (threading.Thread):
	def __init__(self, threadID, name):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
	def run(self):
		try:
			image_face = face_recognition.load_image_file('/tmp/facerecognition/_images/'+self.name)
			face_locations = face_recognition.face_locations(image_face)

			if len(face_locations) == 1 :
				print("++ 1 face minimum de trouvée : ok")
			else:
				print("-- Aucune face de trouvée : ok")
			
		except:
			print('error with item')


#extraire le nom du fichier
#image = path_image.split("/")[-1]

montemps=time.time()	
myList = os.listdir('/tmp/facerecognition/_images/')
number = len(myList)
i = 0
for element in myList:
	if os.path.isfile('/tmp/facerecognition/_images/'+element):
		print("% 1d / %1d  =>  '%s' " %(i, number, element))  
		i = i +1
		
	
		if not os.path.splitext(element)[1] not in ALLOWED_EXTENSIONS:
			raise Exception("Invalid image extention: {}".format(element))

		thread1 = myThread(1, element)
		thread1.start()
		
thread1.join()


y=time.time()-montemps
print(time.strftime('%M # %S ',time.localtime()))
print("nombre de fichier :{}".format(i))
	

print ("Exiting Main Thread")