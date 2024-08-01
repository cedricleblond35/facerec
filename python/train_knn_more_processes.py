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
import time

from classes.numberFile import Counter

"""
import pour reconnaissance fasciale
"""
import face_recognition
from face_recognition.face_recognition_cli import image_files_in_folder
import pickle

"""
import pour multiprocessing
"""
from multiprocessing.pool import ThreadPool as Pool
import multiprocessing

"""
import pour avoir des infos sur le micropresseur
https://pypi.org/project/psutil/
doc : https://psutil.readthedocs.io/en/latest/
"""
import psutil

"""
import pour compression  
"""
import gzip
import shutil

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
pool_size = 3  # your "parallelness"
pool = Pool(pool_size)

# 1ere argument : repertoire parent des personnes
path_personn = sys.argv[1]
# 2eme argument : repertoire de stockage pour le fichier d apprentissage
path_trained_knn_model = sys.argv[2]

def checkCPU():
    cpu_t_percent = psutil.cpu_times_percent(interval=1, percpu=False)
    return cpu_t_percent.user

def compressGzip(file, outfile):
    with open(file, 'rb') as f_in:
        with gzip.open(outfile, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def worker(list_directories):
    try:
        general = []
        X = []
        Y = []
        for id_personn, file in list_directories.items():
            # print("chemin :{}".format( file))
            image = face_recognition.load_image_file(file)
            # face_bounding_boxes = face_recognition.face_locations(image, number_of_times_to_upsample=1, model='hog')
            # face_bounding_boxes = face_recognition.face_locations(image, number_of_times_to_upsample=1, num_jitters=2, model='large')
            # face_bounding_boxes = face_recognition.face_locations(image, number_of_times_to_upsample=1, model='hog')
            face_bounding_boxes = face_recognition.face_locations(image)
            if len(face_bounding_boxes) == 1:
                # Ajouter un codage de visage pour l'image en cours au kit de formation
                X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                Y.append(id_personn)
                general.append(X)
                general.append(Y)
        return general
    except NameError as error:
        print("NameError :", error)
    except Exception as exception:
        print("exception :", exception)


def train(path_personn, model_save_path=None, knn_algo='ball_tree'):
    try:
        X = []
        Y = []
        list_directories = []
        i = 0
        for id_personn in os.listdir(path_personn):
            if not os.path.isdir(os.path.join(path_personn, id_personn)):
                continue
            #
            # Imposer un minimum de photo d'apprentissage
            pathId_personn = path_personn + id_personn
            counter = Counter(pathId_personn)
            number = 0
            for cls in counter.work():
                number = int(cls.files)
                pass

            if number < 3:
                continue

            # Boucle à travers chaque image de formation pour la personne actuelle
            for img_path in image_files_in_folder(os.path.join(path_personn, id_personn)):
                personndict = {}
                personndict[id_personn] = img_path
                list_directories.append(personndict)

        strlist = list((filter(None, list_directories)))
        # print(strlist)
        # Parallélisme par processus-----------------------------------------------------------------
        pool2 = int(multiprocessing.cpu_count() * 15 / 16)
        p = multiprocessing.Pool(pool2)
        result_worker = p.map(worker, strlist)
        pool.close()
        pool.join()

        i = 0
        while i < len(result_worker):
            if (len(result_worker[i][1]) > 0):
                Y.append(result_worker[i][1][0])
                X.append(result_worker[i][0][0])
            i += 1

        n_neighbors = int(round(math.sqrt(len(X))))
        # Créer et former le classifieur KNN
        knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
        knn_clf.fit(X, Y)

        # Enregistrer le classificateur KNN formé
        if model_save_path is not None:
            with open(model_save_path, 'wb') as f:
                pickle.dump(knn_clf, f)

        return knn_clf
    except NameError as error:
        print("NameError :", error)
    except Exception as exception:
        print("exception :", exception)


def waited(time_start):
    if (checkCPU() < 75):
        # print(time.strftime('%M # %S ',time.localtime()))
        montemps = time.time()
        # STEP 1: Former le classifieur KNN et l'enregistrer sur le disque
        trained_knn_model = path_trained_knn_model + "trained_knn_model.clf"
        train(path_personn, model_save_path=trained_knn_model)
        compressGzip(trained_knn_model, trained_knn_model + '.gz')

        print("Training complete!")
    else:
        time_intermediaire = time.time()
        dif = time_intermediaire - time_start
        if (dif < 600):
            # print("waited")
            waited(time_start)


if __name__ == "__main__":
    waited(time.time())
