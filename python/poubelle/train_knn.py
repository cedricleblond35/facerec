"""
Ceci est un exemple d'utilisation de l'algorithme kN-plus proche-voisin (KNN) pour la reconnaissance faciale.

Quand devrais-je utiliser cet exemple?
Cet exemple est utile lorsque vous souhaitez reconnaître un grand nombre de personnes connues,
et faire une prédiction pour une personne inconnue dans un temps de calcul possible.

Description de l'algorithme:
Le classifieur knn est d'abord entraîné sur un ensemble de visages étiquetés (connus) et peut ensuite prédire la personne
dans une image inconnue en recherchant les k faces les plus similaires (images avec des traits de visages rapprochés sous une distance euclédienne)
dans son ensemble d’entraînement et en réalisant un vote majoritaire (éventuellement pondéré) sur leur étiquette.

Par exemple, si k = 3, et que les trois images de visage les plus proches de l’image donnée dans l’apprentissage sont une image de Biden
et deux images d'Obama, le résultat serait "Obama".

* Cette implémentation utilise un vote pondéré, de telle sorte que les votes des voisins plus proches sont pondérés plus fortement.

Usage:

1. Préparez une série d’images des personnes connues que vous souhaitez reconnaître. Organiser les images dans un seul répertoire
   avec un sous-répertoire pour chaque personne connue.

2. Appelez ensuite la fonction 'train' avec les paramètres appropriés. Assurez-vous de passer le 'model_save_path' si vous
   souhaitez enregistrer le modèle sur le disque afin de pouvoir le réutiliser sans avoir à le réentraîner.

3. Appelez «predict» et transmettez votre modèle formé pour reconnaître les personnes dans une image inconnue.

REMARQUE: Cet exemple nécessite l'installation de scikit-learn! Vous pouvez l'installer avec pip:

$ pip3 installe scikit-learn
"""
import sys
import math
from sklearn import neighbors
import os
import os.path
import pickle
from PIL import Image, ImageDraw
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
import time
import gzip
import shutil

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

#1ere argument : repertoire parent des personnes
path_personn = sys.argv[1]
#2eme argument : repertoire de stockage pour le fichier d apprentissage
path_trained_knn_model = sys.argv[2]

def compressGzip(file, outfile, option):
	with open(file, 'rb') as f_in:
		with gzip.open(outfile, 'wb') as f_out:
			shutil.copyfileobj(f_in, f_out)

def train(train_dir, model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
	X = []
	y = []
	compte = 0
	compte2 = 0
    # Boucle à travers chaque personne dans l'ensemble de formation
	for class_dir in os.listdir(train_dir):
		if not os.path.isdir(os.path.join(train_dir, class_dir)):
			continue
		
		compte2 += len(image_files_in_folder(os.path.join(train_dir, class_dir)))
        # Boucle à travers chaque image de formation pour la personne actuelle
		for img_path in image_files_in_folder(os.path.join(train_dir, class_dir)):
			image = face_recognition.load_image_file(img_path)
			face_bounding_boxes = face_recognition.face_locations(image)
			compte += 1
			# print("image : {}".format(compte))
			if len(face_bounding_boxes) != 1:
                # S'il n'y a personne (ou trop de personnes) dans une image de formation, ignorez l'image.
				if verbose:
					print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))
			else:
				
                # Ajouter un codage de visage pour l'image en cours au kit de formation
				X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
				y.append(class_dir)
	
	# print(y)
	
	# print(X)
	# print(len(X))
	# print("cp2 {}:".format(compte2))
    # Déterminez le nombre de voisins à utiliser pour la pondération dans le classificateur KNN
	if n_neighbors is None:
		n_neighbors = int(round(math.sqrt(len(X))))
		if verbose:
			print("Chose n_neighbors automatically:", n_neighbors)


    # Créer et former le classifieur KNN
	knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
	knn_clf.fit(X, y)

    # Enregistrer le classificateur KNN formé
	if model_save_path is not None:
		with open(model_save_path, 'wb') as f:
			pickle.dump(knn_clf, f)

	return knn_clf


if __name__ == "__main__":
	print(time.strftime('%M # %S ',time.localtime()))
	montemps=time.time()
    # STEP 1: Former le classifieur KNN et l'enregistrer sur le disque
	trained_knn_model = path_trained_knn_model+"trained_knn_model.clf"
	classifier = train(path_personn, model_save_path=trained_knn_model, n_neighbors=2)
	compressGzip(trained_knn_model, path_trained_knn_model+'trained_knn_model.gz', 'best')
	y=time.time()-montemps
	print(time.strftime('%M # %S ',time.localtime()))
	print("{}".format(y))
	print("Training complete!")