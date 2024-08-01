# """
# Ceci est un exemple d'utilisation de l'algorithme kN-plus proche-voisin (KNN) pour la reconnaissance faciale.
#
# Quand devrais-je utiliser cet exemple?
# Cet exemple est utile lorsque vous souhaitez reconnaître un grand nombre de personnes connues,
# et faire une prédiction pour une personne inconnue dans un temps de calcul possible.
#
# Description de l'algorithme:
# Le classifieur knn est d'abord entraîné sur un ensemble de visages étiquetés (connus) et peut ensuite prédire la personne
# dans une image inconnue en recherchant les k faces les plus similaires (images avec des traits de visages rapprochés sous une distance euclédienne)
# dans son ensemble d’entraînement et en réalisant un vote majoritaire (éventuellement pondéré) sur leur étiquette.
#
# Par exemple, si k = 3, et que les trois images de visage les plus proches de l’image donnée dans l’apprentissage sont une image de Biden
# et deux images d'Obama, le résultat serait "Obama".
#
# * Cette implémentation utilise un vote pondéré, de telle sorte que les votes des voisins plus proches sont pondérés plus fortement.
#
# Usage:
#
# 1. Préparez une série d’images des personnes connues que vous souhaitez reconnaître. Organiser les images dans un seul répertoire
#    avec un sous-répertoire pour chaque personne connue.
#
# 2. Appelez ensuite la fonction 'train' avec les paramètres appropriés. Assurez-vous de passer le 'model_save_path' si vous
#    souhaitez enregistrer le modèle sur le disque afin de pouvoir le réutiliser sans avoir à le réentraîner.
#
# 3. Appelez «predict» et transmettez votre modèle formé pour reconnaître les personnes dans une image inconnue.
#
# REMARQUE: Cet exemple nécessite l'installation de scikit-learn! Vous pouvez l'installer avec pip:
#
# $ pip3 installe scikit-learn
# """
#
import urllib.request
import sys
from classes.recognition import Recognition

# from time import perf_counter

if __name__ == "__main__":
    try:
        # t1_start = perf_counter()
        # url fourni
        json_url_picture = sys.argv[1]
        # repertoire de stockage d image
        trained_knn_model = sys.argv[2]
        # repertoire de stockage d image
        path_save_picture = sys.argv[3]

        recognition = Recognition(json_url_picture, path_save_picture, trained_knn_model)
        recognition.processing()

        # t1_stop = perf_counter()
        # print("Elapsed time:", t1_stop, t1_start)
        # print("Elapsed time during the whole program in seconds:  => Recognition =>",
        #       t1_stop - t1_start)


    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())
