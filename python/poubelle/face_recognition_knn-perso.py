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

import urllib.request
import math
from sklearn import neighbors
import os
import os.path
import sys
import json
import pickle
from PIL import Image, ImageDraw
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder

from classes.url import Url

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def predict(X_img_path, knn_clf=None, model_path=None, distance_threshold=0.6):
    """
    Reconnaît les visages d'une image donnée à l'aide d'un classifieur KNN formé

    :param X_img_path: path to image to be recognized
    :param knn_clf: (optional) a knn classifier object. if not specified, model_save_path must be specified.
    :param model_path: (optional) path to a pickled knn classifier. if not specified, model_save_path must be knn_clf.
    :param distance_threshold: (optional) distance threshold for face classification. the larger it is, the more chance
           of mis-classifying an unknown person as a known one.
    :return: a list of names and face locations for the recognized faces in the image: [(name, bounding box), ...].
        For faces of unrecognized persons, the name 'unknown' will be returned.
    """
    if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in ALLOWED_EXTENSIONS:
        raise Exception("Invalid image path: {}".format(X_img_path))

    if knn_clf is None and model_path is None:
        raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

    # Charger un modèle KNN formé (si un modèle a été transmis)
    if knn_clf is None:
        with open(model_path, 'rb') as f:
            knn_clf = pickle.load(f)

    # Charger un fichier image et trouver les emplacements des visages
    X_img = face_recognition.load_image_file(X_img_path)
    X_face_locations = face_recognition.face_locations(X_img)

    # Si aucun visage n'est trouvé dans l'image, retournez un résultat vide.
    if len(X_face_locations) == 0:
        return []

    # Rechercher des encodages pour les visages dans l'image test
    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)

    # Utilisez le modèle KNN pour trouver les meilleures correspondances pour la face de test
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Prédire les classes et supprimer les classifications qui ne sont pas comprises dans le seuil
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]


def show_prediction_labels_on_image(img_path, predictions):
    """
    Affiche les résultats de la reconnaissance faciale visuellement.

    :param img_path: chemin de l'image à reconnaître
    :param predictions: résultats de la fonction de prédiction
    :return:
    """
    pil_image = Image.open(img_path).convert("RGB")
    draw = ImageDraw.Draw(pil_image)
    

    for name, (top, right, bottom, left) in predictions:
        # Dessinez un cadre autour du visage à l'aide du module Pillow
        draw.rectangle(((left, top), (right, bottom)), outline=(0, 0, 255))

        # Il y a un bogue dans Pillow qui explose avec du texte non-UTF-8 lors de l'utilisation de la police bitmap par défaut
        name = name.encode("UTF-8")

        # Dessinez une étiquette avec un nom sous le visage
        text_width, text_height = draw.textsize(name)
        draw.rectangle(((left, bottom - text_height - 10), (right, bottom)), fill=(0, 0, 255), outline=(0, 0, 255))
        draw.text((left + 6, bottom - text_height - 5), name, fill=(255, 255, 255, 255))

    # Supprimer la bibliothèque de dessins de la mémoire conformément à la documentation Pillow
    del draw

    # Display the resulting image

    pil_image.show()

	#transforme les coordonnées pixels en %
def pourcentage(image,top, left, bottom, right):
	size_img = Image.open(image)
	x1 = left / size_img.size[0] * 100
	y1 = top / size_img.size[1] * 100
	x2 = right / size_img.size[0] * 100
	y2 = bottom / size_img.size[1] * 100
	return x1, y1, x2, y2

	#transforme les coordonnées du dernier point (bottom, right) en (width, height)  pixels en %
def pixel(top, left, bottom, right):
	x = left
	y = top
	w = right - left
	h = bottom - top
	return x, y, w, h




if __name__ == "__main__":
	try:
		#url fourni
		json_url_picture = sys.argv[1]
		#2eme argument : repertoire de stockage pour le fichier d apprentissage
		trained_knn_model = sys.argv[2]
		#name file
		str1 = json_url_picture.replace(']','').replace('[','')
		array_url_picture = str1.replace('"','').split(",")
		
		predictions = []
		for url in array_url_picture:
			url_check = Url(url)
			image = url_check.download_file()
			id_image = image.split("/")[-1].split(".")[0].split("_")[0]
			
			# Trouver toutes les personnes dans l'image à l'aide d'un modèle de classificateur formé
			# Note: Vous pouvez transmettre un nom de fichier de classificateur ou une instance de modèle de classificateur.
			predictions.append(predict(image, model_path=trained_knn_model))
			
		# Print results on the console
		data_array = []
		for prediction in predictions:
			for name, (top, right, bottom, left) in prediction:
				x1_pourcentage, y1_pourcentage, x2_pourcentage, y2_pourcentage = pourcentage(image, top, left, bottom, right)
				x_pixel, y_pixel, w_pixel, h_pixel = pixel(top, left, bottom, right)
				data_json = {
								  "id_Image" : id_image,
								  "Id_name" : name,
								  "Rectangle":
								  { 
									"pourcentage":
									{
									"X":x1_pourcentage,
									"Y":y1_pourcentage,
									"W":x2_pourcentage,
									"H":y2_pourcentage
									},
									"pixel" :
									{
									  "X":x_pixel,
									  "Y":y_pixel,
									  "W":w_pixel,
									  "H":h_pixel
									}
								  }
								}
				data_array.append(data_json)

		print(json.dumps(data_array))

	except urllib.error.HTTPError as e:
		print(e.code)
		print(e.read())
	