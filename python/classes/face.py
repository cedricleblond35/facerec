import os
from utils.picture_utils import Picture_utils
from classes.picture import Picture
from classes.url import Url

from classes.mailHTML import MailHTML
from datetime import datetime
import subprocess
import sys, traceback, psutil
class Face:
    """
    Class mère détermina,t la construction du json, et le téléchargement des images si besoin.
    """

    def __init__(self, json_url_picture, path_save_picture):
        # Protected
        self._json_url_picture = json_url_picture
        self._path_save_picture = path_save_picture

        # Private
        self.__allowed_extensions = {'png', 'jpg', 'jpeg'}

    def _clean_url(self, json_url_picture):
        """
        Nettoyage de l'url
        :param json_url_picture:
        :return:
        """
        return json_url_picture.replace(']', '').replace('[', '').replace('"', '').split(",")

    def _build_faces_json(self, image, coordinate, face_id=None, face_percent=None):
        """
        Créer la partie du json contenu dans le tableau Faces
        :param image: chemin et fichier de l'image
        :param coordinate: coordonnées d'une tête
        :param face_id: identité de la personne dans le cas d'une reconnaissance faciale
        :return:
        """
        # calcul pourcentage & pixel
        x1_pourcentage, y1_pourcentage, x2_pourcentage, y2_pourcentage = Picture_utils.pourcentage(
            image, coordinate.get("top"), coordinate.get("left"), coordinate.get("bottom"), coordinate.get("right"))

        x_pixel, y_pixel, w_pixel, h_pixel = Picture_utils.pixel(coordinate.get("top"), coordinate.get("left"),
                                                                 coordinate.get("bottom"), coordinate.get("right"))

        faces = {
            "Percent": {
                "X": x1_pourcentage,
                "Y": y1_pourcentage,
                "W": x2_pourcentage,
                "H": y2_pourcentage
            },
            "Pixel": {
                "X": x_pixel,
                "Y": y_pixel,
                "W": w_pixel,
                "H": h_pixel
            }
        }

        if face_id is not None:
            # Ajouter l identite de la tête ds le cas d une reconnaissance
            faces["Face_id"] = face_id
            self.__idname = face_id

        if face_percent is not None:
            # Ajouter l identite de la tête ds le cas d une reconnaissance
            faces["Face_percent"] = face_percent
            self.__face_percent = face_percent

        return faces

    def _build_json(self, url, width, height, count, face_array):
        """
        Créer la struture du json pour une image
        :return:
        """
        return {
            "Url": url,
            "Count": count,
            "ImageSize": {
                "W": width,
                "H": height
            },
            "Faces": face_array,
        }

    def _check_image(self, url):
        """
        Télécharger une image et là transformer en jpg si besoin
        :param url: url http ou https
        :return: l'image
        """
        try:
            url_check = Url(url, self._path_save_picture)
            image = url_check.download_file()

            picture = Picture(image)
            filename, file_extension = os.path.splitext(image)

            # Convertion format image ##############################################################################
            if file_extension == ".png":
                image = picture.convertPNGtoJPG(filename)
                picture.setFile(image)
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
            raise exception

        return image


