#!/usr/bin/python3
import sys
import json
#bibliothèque face
from PIL import Image
import face_recognition
import os.path

import urllib.request
import time

import _thread

directory = "/tmp/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
# define worker function before a Pool is instantiated
def worker(item):

	try:
		image_face = face_recognition.load_image_file('/tmp/facerecognition/_images/'+element)
		face_locations = face_recognition.face_locations(image_face)

		if len(face_locations) == 1 :
			print("++ 1 face minimum de trouvée : ok")
		else:
			print("-- Aucune face de trouvée : ok")
		
	except:
		print('error with item')


try:
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

			_thread.start_new_thread( worker, (element, ) )
	
	

	y=time.time()-montemps
	print(time.strftime('%M # %S ',time.localtime()))
	print("nombre de fichier :{}".format(i))
	
except urllib.error.HTTPError as e:
	print(e.code)
	print(e.read())
	