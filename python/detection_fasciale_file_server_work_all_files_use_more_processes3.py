import sys
import json
import os.path

#bibliothèque face
from PIL import Image
import face_recognition

#multiprocessing
from multiprocessing.pool import ThreadPool as Pool
import multiprocessing

""""
Vérifier si l image sur le disque contient 1 et 1 seule face
1 face : True
0 ou plusieurs faces : False
"""


#Dossier de stockage
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# define worker function before a Pool is instantiated
def worker(personndict):
	try:
		data_worker = []
		# print("---------------------------------------------------------------------------------------------------")
		# print("dicojson : {}".format(personndict))
		for path_id_personn, images_array in personndict.items():
			array = path_id_personn.split("/")
			id_personn = array[-1]
			del array[-1]
			path = "/"
			for v in array:
				path += v+"/"
			
			# print("id_personn : {}, {}".format(id_personn, images_array))
			for image in images_array:
				image_face = face_recognition.load_image_file(path+id_personn+'/'+image)
				face_locations = face_recognition.face_locations(image_face)
				if len(face_locations) == 1 :
					top, right, bottom, left = face_locations[0]
					pixels = (right - left) * ( bottom - top)

					if pixels >= 8000 :
						#on retient seulement les visages faisant au moins 10000 pixels pour un apprentissage correcte
						data_worker.append({
								"id_personn" : id_personn,
								"Image": image.split(".")[0],
								"Extension": image.split(".")[1],
								"face": "ok"
							})
					else:
						data_worker.append({
							"id_personn": id_personn,
							"Image": image.split(".")[0],
							"Extension": image.split(".")[1],
							"face": "ko",
							"cause": "small"
						})

				else:
					data_worker.append({
							"id_personn" : id_personn,
							"Image": image.split(".")[0],
							"Extension": image.split(".")[1],
							"face": "ko",
							"cause": "no detect"
						})
		return data_worker
	except ValueError as ve:
		print("worker python : Unexpected error:", sys.exc_info()[0])
		print(ve)



pool_size = 3  # your "parallelness"
pool = Pool(pool_size)


#url fourni
#path_image = sys.argv[1] 

#lister toutes les images dans le repertoire de la personne--------------------------------------
def find_file(directory):
	files_list = os.listdir(directory)
	number_files = len(files_list)
	list_files = [None] * number_files
	i = 0
	for file_image in files_list:
		list_files[i] = file_image
		i += 1
	return list_files


try:
	# Variables --------------------------------------------------------------------------------
	path_general = sys.argv[1]
	path_personn = sys.argv[2]
	# liste des repertoires (id des personnes) ds personn
	directories = os.listdir(path_personn)
	number_directory = len(directories)
	
	file_face_ok = path_general+'face_ok.json'
	file_face_ko = path_general+'face_ko.json'
	
	# Construction d'une liste comportant tous les fichiers à analyser--------------------------
	i = 0
	list_directories = [None] * number_directory
	for directory in directories:
		personndict = {}
		if os.path.isdir(path_personn+directory):
			list_files = find_file(path_personn+directory)
			personndict[path_personn+directory] = list_files
			list_directories[i] = personndict
			i += 1


	# Parallélisme par processus-----------------------------------------------------------------
	pool2 = int(multiprocessing.cpu_count()*4/5)
	p = multiprocessing.Pool(pool2)
	result_json = p.map(worker, list_directories)
	pool.close()
	pool.join()
	
	list_face_ok = []
	list_face_ko = []
	i=0
	while i < len(result_json):
		l = 0
		while l < len(result_json[i]):
			if result_json[i][l].get("face") == "ok":
				list_face_ok.append(result_json[i][l])
			else:
				list_face_ko.append(result_json[i][l])
			l += 1
		i += 1
	
	# Création des json---------------------------------------------------------------------------
	with open(file_face_ok, 'w') as outfile:
		json.dump(list_face_ok, outfile)
	
	with open(file_face_ko, 'w') as outfile:
		json.dump(list_face_ko, outfile)
	
	# information sur le fichier créé à savoir face_ok.json et face_ko.json-----------------------
	file_return_json = []
	file_return_json.append({"file_face_ok" : file_face_ok, "file_face_ko" : file_face_ko})
	data_json = json.dumps(file_return_json)
	print(data_json)
	
except OSError as err:
    print("Application python : OS error: {0}".format(err))
except:
    print("Application python : Unexpected error:", sys.exc_info()[0])
    raise
	