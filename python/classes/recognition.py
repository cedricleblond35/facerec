import urllib.request
import os
import os.path
import operator
import json
import pickle
import face_recognition
from classes.face import Face
from utils.picture_utils import Picture_utils
# import PIL.Image
from PIL import Image

from classes.mailHTML import MailHTML
from datetime import datetime
import subprocess
import sys, traceback, psutil
import numpy as np
# multiprocessing
from multiprocessing.pool import ThreadPool as Pool
import multiprocessing
from time import perf_counter

from classes.mailHTML import MailHTML

class Recognition(Face):
    """
    Class permettant de faire de la reconnaissance faciale
    """

    def __init__(self, json_url_picture, path_save_picture, trained_knn_model):
        super().__init__(json_url_picture, path_save_picture)
        self.__trained_knn_model = trained_knn_model
        self.__ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    def __recognition(self, image, trained_knn_model):
        """

        :param image:
        :param trained_knn_model:
        :return:
        """
        try:
            # Trouver toutes les personnes dans l'image à l'aide d'un modèle de classificateur formé
            # Note: Vous pouvez transmettre un nom de fichier de classificateur ou une instance de modèle de classificateur.
            # t1_start = perf_counter()
            prediction = self.__predict(image, model_path=trained_knn_model)
            # t1_stop = perf_counter()
            # print("Elapsed time:", t1_stop, t1_start)
            # print("Elapsed time during the whole program in seconds:  => __predict =>",
            #        t1_stop - t1_start)
            face_array = []

            for face_id, (top, right, bottom, left), distances in prediction:
                coordinate = {
                    "top": top,
                    "left": left,
                    "right": right,
                    "bottom": bottom
                }

                # print("coordinate :", coordinate)
                # print("face_id :", face_id)
                if face_id is not "":
                    Face_percent = int((1 - distances) * 100)
                    face_array.append(self._build_faces_json(image, coordinate, face_id, Face_percent))
                else:
                    face_array.append(self._build_faces_json(image, coordinate, "", ""))

            return len(prediction), face_array

        except urllib.error.HTTPError as e:
            mail = MailHTML()
            mail.set_message("reconnaissance faciale", e.code)
            mail.send_all()
            print(e.code)
            print(e.read())

    def __augementation_dimention(self, source, dim, img_path, tauxAugmentation=1.00, augmentation=False):
        """

        :param dim:
        :param img_path:
        :param tauxAugmentation:
        :param augmentation:
        :return:
        """
        ratio = 0
        image_face = ""
        if max(dim.values()) > 1600:
            im = Image.open(img_path)
            file, ext = os.path.splitext(img_path)
            hey_max_value = max(dim.items(), key=operator.itemgetter(1))[0]
            ratio = 1600 / dim.get(hey_max_value)
            width = int(round(ratio * dim.get("width"), 2))
            height = int(round(ratio * dim.get("height"), 2))
            img = im.resize((int(width), int(height)), Image.LANCZOS)
            img.save(file + '____thumbnail' + ext)
            image_face = face_recognition.load_image_file(file + '____thumbnail' + ext)

        if augmentation and tauxAugmentation < 1.3:
            """
            Augmentation max 50%
            """
            im = Image.open(img_path)
            file, ext = os.path.splitext(img_path)
            hey_max_value = min(dim.items(), key=operator.itemgetter(1))[0]
            tauxAugmentation += 0.05
            ratio = min(dim.values()) * tauxAugmentation / dim.get(hey_max_value)
            width = int(round(ratio * dim.get("width"), 2))
            height = int(round(ratio * dim.get("height"), 2))
            img = im.resize((int(width), int(height)), Image.LANCZOS)
            img.save(file + '____thumbnail' + ext)
            image_face = face_recognition.load_image_file(file + '____thumbnail' + ext)

        if ratio == 0:
            #si aucun modif, on prend l image originale
            face_locations = face_recognition.face_locations(source, number_of_times_to_upsample=2, model='hog')
            #face_locations = face_recognition.face_locations(source, number_of_times_to_upsample=0, model="cnn")
        else:
            #face_locations = face_recognition.face_locations(image_face, number_of_times_to_upsample=0, model='hog')
            face_locations = face_recognition.face_locations(image_face, number_of_times_to_upsample=2, model="cnn")

        if len(face_locations) == 0 and tauxAugmentation < 1.3:
            face_locations = self.__augementation_dimention(source, dim, img_path, tauxAugmentation, True)

        # remise à l'echelle des coordonnées de la détection selon les images
        if ratio > 0:
            for x in face_locations:
                list_x = list(x)
                for value_list in list_x:
                    list_x[list_x.index(value_list)] = round(value_list / ratio)

                t = tuple(list_x)
                face_locations[face_locations.index(x)] = t

        return face_locations, tauxAugmentation-1

    def __predict(self, X_img_path, knn_clf=None, model_path=None, distance_threshold=0.8):
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
        try:
            if not os.path.isfile(X_img_path) or os.path.splitext(X_img_path)[1][1:] not in self.__ALLOWED_EXTENSIONS:
                raise Exception("Invalid image path: {}".format(X_img_path))

            if knn_clf is None and model_path is None:
                raise Exception("Must supply knn classifier either thourgh knn_clf or model_path")

            # Charger un modèle KNN formé (si un modèle a été transmis)
            if knn_clf is None:
                with open(model_path, 'rb') as f:
                    knn_clf = pickle.load(f)
            # Charger un fichier image et trouver les emplacements des visages -------------------
            image_face = face_recognition.load_image_file(X_img_path)

            # calcul du coef si besoin
            dim = {"height": image_face.shape[0], "width": image_face.shape[1]}
            face_locations, tauxAugmentation = self.__augementation_dimention(image_face, dim, X_img_path)

            # test ----------------------------------------------------------------------------------------------
            # face_locations = face_recognition.face_locations(image_face, number_of_times_to_upsample=0, model="hog")
            # face_locations1 = face_recognition.face_locations(image_face, number_of_times_to_upsample=0, model="cnn")
            # face_location_finish = []
            # for face_location_hog in face_locations:
            #     # Print the location of each face in this image
            #     top_Big_Image0, right_Big_Image0, bottom_Big_Image0, left_Big_Image0 = face_location_hog
            #     centerY0 = bottom_Big_Image0 - top_Big_Image0
            #     centerX0 = right_Big_Image0 - left_Big_Image0
            #
            #     for face_location_cnn in face_locations1:
            #         # Print the location of each face in this image
            #         top_Big_Image1, right_Big_Image1, bottom_Big_Image1, left_Big_Image1 = face_location_cnn
            #
            #         if top_Big_Image1 < centerY0 < bottom_Big_Image1 and left_Big_Image1 < centerX0 < right_Big_Image1 :
            #             top = [top_Big_Image1, top_Big_Image0].sort()[-1]
            #             right =[right_Big_Image0, right_Big_Image1].sort()[-1]
            #             bottom = [bottom_Big_Image0, bottom_Big_Image1].sort()[-1]
            #             left = [left_Big_Image0, left_Big_Image1].sort()[-1]
            #             face_location_bis = [top, right, bottom, left]
            #             face_location_finish.append(face_location_bis)

            # Si aucun visage n'est trouvé dans l'image, retournez un résultat vide.
            if len(face_locations) == 0:
                return []

            # Rechercher des encodages pour les visages dans l'image test
            faces_encodings = face_recognition.face_encodings(image_face, known_face_locations=face_locations)


            # Utilisez le modèle KNN pour trouver les meilleures correspondances pour la face de test
            closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
            # closest_distances = knn_clf.kneighbors(faces_encodings)

            are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(face_locations))]

            distances = []
            for i in range(len(face_locations)):
                distances.append(closest_distances[0][i][0])

            # Prédire les classes et supprimer les classifications qui ne sont pas comprises dans le seuil
            return [(pred, loc, per) if rec else ("", loc, "") for pred, loc, rec, per in
                    zip(knn_clf.predict(faces_encodings), face_locations, are_matches, distances)]
        except urllib.error.HTTPError as e:
            mail = MailHTML()
            mail.set_message("reconnaissance faciale", e.code)
            mail.send_all()
            print(e.code)
            print(e.read())

    def _worker_multiprocessing(self, url):
        # t1_start = perf_counter()
        try:

            image = self._check_image(url)
            width, height = Picture_utils.size_image(image)
            count, face_array, = self.__recognition(image, self.__trained_knn_model)

            # t1_stop = perf_counter()
            # print("Elapsed time:", t1_stop, t1_start)
            # print("Elapsed time during the whole program in seconds:  => _worker_multiprocessing =>",
            #       t1_stop - t1_start)
        except Exception as exception:
            raise exception
        return self._build_json(url, width, height, count, face_array)

    def processing(self):
        """

        :return:
        """
        try:
            # t1_start = perf_counter()


            array_url_picture = super()._clean_url(self._json_url_picture)
            people_dictionary = {}

            pool_size = int(multiprocessing.cpu_count() * 4 / 5)  # your "parallelness"
            pool = Pool(pool_size)
            pool2 = int(multiprocessing.cpu_count() * 4 / 5)
            p = multiprocessing.Pool(pool2)
            result = p.map(self._worker_multiprocessing, array_url_picture)
            pool.close()
            pool.join()
            people_dictionary["Results"] = result

            # hold version ######################################################
            people_dictionary["Size"] = {
                "W": people_dictionary["Results"][0]["ImageSize"]["W"],
                "H": people_dictionary["Results"][0]["ImageSize"]["H"]
            }

            faceNb = len(people_dictionary["Results"][0]["Faces"])
            people_dictionary["Face_id"] = people_dictionary["Results"][0]["Faces"][0]["Face_id"] if faceNb > 0 else ""
            people_dictionary["Face_percent"] = people_dictionary["Results"][0]["Faces"][0][
                "Face_percent"] if faceNb > 0 else ""
            people_dictionary["Count"] = people_dictionary["Results"][0]["Count"] if faceNb > 0 else ""
            originalData = []
            percents = []
            for coordinatedData in people_dictionary["Results"][0]["Faces"]:
                percents.append(coordinatedData["Percent"])
                originalData.append(coordinatedData["Pixel"])

            people_dictionary["OriginalData"] = originalData
            people_dictionary["Rectangles"] = percents
            # # end hold version ######################################################

            data_json = json.dumps(people_dictionary)
            print(data_json)

            # t1_stop = perf_counter()
            # print("Elapsed time:", t1_stop, t1_start)
            # print("Elapsed time during the whole program in seconds:  => processing =>",
            #       t1_stop - t1_start)


        except Exception as exception:

            exc_type, exc_value, exc_traceback = sys.exc_info()

            exc_traceback_info = traceback.extract_tb(exc_traceback,

                                                      limit=2)

            stack_info = traceback.extract_stack()

            now = datetime.now()

            cpu = psutil.cpu_percent(interval=1, percpu=True)

            mem = psutil.virtual_memory()

            disk = psutil.disk_usage('/')

            ip = psutil.net_if_addrs()

            result = subprocess.run(['hostname'], stdout=subprocess.PIPE)

            serverName = result.stdout.decode('utf-8')

            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

            mail = MailHTML()

            mail.set_message({"date": dt_string,

                              "server": serverName,

                              "message": " exception: {0}".format(exception),

                              "traceback": exc_traceback_info,

                              "stack": stack_info,

                              "cpu": cpu,

                              "memory": mem,

                              "disk": disk,

                              "network": ip

                              },

                             "reconnaissance faciale")

            mail.send_all()

            raise
