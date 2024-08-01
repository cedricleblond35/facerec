import sys
import json
#bibliothèque face
from PIL import Image
import face_recognition
import os.path

import urllib.request
import time

from threading import Thread

from multiprocessing.pool import ThreadPool as Pool
import multiprocessing

from classes.url import Url


""""
Vérifier si l image sur le disque contient 1 et 1 seule face
1 face : True
0 ou plusieurs faces : False
"""


#Dossier de stockage
directory = "/tmp/"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

nbre_valide = 0


def find_file(directory):
	files = os.listdir('/tmp/facerecognition/personn/'+directory)
	number_files = len(files)
	list_files = [None] * number_files
	i=0
	# for file in files:	
		# if not os.path.splitext(file)[1] not in ALLOWED_EXTENSIONS:
			# raise Exception("Invalid image extention: {}".format(directory))
		
		# list_files[i] = file
		# i=i+1
		# print("{} : {} ".format(directory, list_files)
	


#Creating Array
data_worker = []
# define worker function before a Pool is instantiated
def worker(item):
	try:
		image_face = face_recognition.load_image_file('/tmp/facerecognition/_images/'+element)
		face_locations = face_recognition.face_locations(image_face)
		
		if len(face_locations) == 1 :
			data_worker.append({
					"id_personn" : element.split("/")[0],
					"Image": element,
					"face": "ok"
				})
	
		else:
			data_worker.append({
					"id_personn" : element.split("/")[0],
					"Image": element,
					"face": "ko"
				})
		return data_worker
	except:
		print('error with item')


pool_size = 3  # your "parallelness"
pool = Pool(pool_size)


#url fourni
#path_image = sys.argv[1] 


try:
	#extraire le nom du fichier
	#image = path_image.split("/")[-1]
	
	montemps=time.time()	
	myList = os.listdir('/tmp/facerecognition/_images/')
	number = len(myList)
	i = 0
	
	liste = [None] * number
	for element in myList:
		if os.path.isfile('/tmp/facerecognition/_images/'+element):
			print("% 1d / %1d  =>  '%s' " %(i, number, element))  
			
			
		
			if not os.path.splitext(element)[1] not in ALLOWED_EXTENSIONS:
				raise Exception("Invalid image extention: {}".format(element))

			liste[i] = element
			
			i = i +1
	
	pool2 = int(multiprocessing.cpu_count()*3/4)
	p = multiprocessing.Pool(pool2)
	print ("cpu utilisé 1111 : {}".format(pool2))
	result_json = p.map(worker, liste)	
	pool.close()
	pool.join()
	
	with open('face.json', 'w') as outfile:
		json.dump(result_json, outfile)
	
	

	y=time.time()-montemps
	print(time.strftime('%M # %S ',time.localtime()))
	print("temps : {}".format(y))
	print("nombre de fichier :{}".format(i))
	
except urllib.error.HTTPError as e:
	print(e.code)
	print(e.read())
	