from classes.face import Face
import urllib.request
import face_recognition
import json
from PIL import Image
import os
import os.path

import operator

from utils.picture_utils import Picture_utils

# multiprocessing
from multiprocessing.pool import ThreadPool as Pool
import multiprocessing


class Detection(Face):
    """

    """
    def __init__(self, json_url_picture, path_save_picture):
        super().__init__(json_url_picture, path_save_picture)

    def detectionForCorp(img_path):
        try:
            image_face = face_recognition.load_image_file(img_path)

            # calcul du coef si besoin
            dim = {"height": image_face.shape[0], "width": image_face.shape[1]}

            ratio = 0
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

            if min(dim.values()) < 1000:
                im = Image.open(img_path)
                file, ext = os.path.splitext(img_path)
                hey_max_value = min(dim.items(), key=operator.itemgetter(1))[0]
                ratio = 1000 / dim.get(hey_max_value)
                width = int(round(ratio * dim.get("width"), 2))
                height = int(round(ratio * dim.get("height"), 2))
                img = im.resize((int(width), int(height)), Image.LANCZOS)
                img.save(file + '____thumbnail' + ext)
                image_face = face_recognition.load_image_file(file + '____thumbnail' + ext)

            face_locations = face_recognition.face_locations(image_face, number_of_times_to_upsample=0, model='hog')

            # remise a l'echelle des coordonnees de la detection selon les images
            for x in face_locations:
                list_x = list(x)
                for value_list in list_x:
                    list_x[list_x.index(value_list)] = round(value_list / ratio)

                t = tuple(list_x)
                face_locations[face_locations.index(x)] = t

            # variable permettant d indiquer si il y a 1 seul personne de detecte
            oneFace = True if len(face_locations) == 1 else False
            # coordonnees de la personne trouvee
            coordinate = {}
            if oneFace:
                for face_location in face_locations:
                    top, right, bottom, left = face_location
                    coordinate = {
                        "top": top,
                        "left": left,
                        "right": right,
                        "bottom": bottom
                    }

            return coordinate, oneFace

        except NameError as error:
            print("NameError :", error)
        except Exception as exception:
            print("exception :", exception)

    def __detection(self, img_path):
        """

        :param img_path:
        :return:
        """
        try:
            image_face = face_recognition.load_image_file(img_path)

            # calcul du coef si besoin
            dim = {"height": image_face.shape[0], "width": image_face.shape[1]}

            ratio = 0
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

            if min(dim.values()) < 1000:
                im = Image.open(img_path)
                file, ext = os.path.splitext(img_path)
                hey_max_value = min(dim.items(), key=operator.itemgetter(1))[0]
                ratio = 1000 / dim.get(hey_max_value)
                width = int(round(ratio * dim.get("width"), 2))
                height = int(round(ratio * dim.get("height"), 2))
                img = im.resize((int(width), int(height)), Image.LANCZOS)
                img.save(file + '____thumbnail' + ext)
                image_face = face_recognition.load_image_file(file + '____thumbnail' + ext)

            face_locations = face_recognition.face_locations(image_face, number_of_times_to_upsample=0, model='hog')

            # remise à l'echelle des coordonnées de la détection selon les images
            for x in face_locations:
                list_x = list(x)
                for value_list in list_x:
                    list_x[list_x.index(value_list)] = round(value_list / ratio)

                t = tuple(list_x)
                face_locations[face_locations.index(x)] = t

            #face_locations = face_recognition.face_locations(image_face, number_of_times_to_upsample=0, model="cnn")
            face_array = []
            for face_location in face_locations:
                # Print the location of each face in this img_path
                top, right, bottom, left = face_location
                coordinate = {
                    "top": top,
                    "left": left,
                    "right": right,
                    "bottom": bottom
                }

                face_array.append(self._build_faces_json(img_path, coordinate))

            return len(face_locations), face_array

        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.read())

    def _worker_multiprocessing(self, url):
        image = self._check_image(url)
        width, height = Picture_utils.size_image(image)
        count, face_array, = self.__detection(image)

        return self._build_json(url, width, height, count, face_array)

    def processing(self):
        """

        :return:
        """
        try:
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

            # # # hold version ######################################################
            people_dictionary["Size"] = {
                "W": people_dictionary["Results"][0]["ImageSize"]["W"],
                "H": people_dictionary["Results"][0]["ImageSize"]["H"]
            }
            people_dictionary["Count"] = people_dictionary["Results"][0]["Count"]
            originalData = []
            percents = []
            for coordinatedData in people_dictionary["Results"][0]["Faces"]:
                percents.append(coordinatedData["Percent"])
                originalData.append(coordinatedData["Pixel"])

            people_dictionary["OriginalData"] = originalData
            people_dictionary["Rectangles"] = percents
            # # # end hold version ######################################################

            data_json = json.dumps(people_dictionary)
            print(data_json)

        except urllib.error.HTTPError as e:
            print(e.code)
            print(e.read())
