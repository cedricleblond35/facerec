import sys
import json
import os

# bibliothèque face
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
import face_recognition
import urllib.request
import os
import os.path

import operator

from classes.url import Url
from classes.picture import Picture
from classes.zip import Zip

"""
multiprocessing  
"""
from multiprocessing.pool import ThreadPool as Pool
import multiprocessing

""""
Collecte une image selon une url fourni et envoie un json contenant Id_name, et le rectangle en % et en pixel 
selon la détection fasciale.


"""

from time import perf_counter


# define worker function before a Pool is instantiated
def worker(dataJson):
    """

    :param dataJson:
    :return:
    """

    s1 = json.dumps(dataJson)  # take a dictionary as input and returns a string as output.
    dataObject = json.loads(s1)  # take a string as input and returns a dictionary as output.

    # check file ###############################################################################################
    url_check = Url(dataObject["url"], dataObject["path_save_picture"])
    image = url_check.download_file()

    picture = Picture(image)

    # variable #################################################################################################
    filename, file_extension = os.path.splitext(image)

    # Convertion format image ##################################################################################
    if file_extension == ".png":
        image = picture.convertPNGtoJPG(filename)
        picture.setFile(image)

    im = Image.open(picture.getFile())
    # Agrandissement et sauvegarde de la photo #################################################################
    coef = picture.enlarging(filename, file_extension)

    # Create rounded rectangle mask
    mask = Image.new('L', im.size, 0)
    draw = ImageDraw.Draw(mask)

    # detection faciale ########################################################################################
    image_face = face_recognition.load_image_file(picture.getFileTemp())

    # traitement de toutes les faces : flottage des visages détectés ###########################################
    """
    model – Which face detection model to use. “hog” is less accurate but faster on CPUs. “cnn” is a more accurate 
    deep-learning model which is GPU/CUDA accelerated (if available). The default is “hog”.
    """
    # t1_start = perf_counter()
    # execute < 1s
    face_locations = face_recognition.face_locations(image_face, number_of_times_to_upsample=0, model="hog")



    # Stop the stopwatch / counter
    # t1_stop = perf_counter()
    # print("Elapsed time:", t1_stop, t1_start)
    # print("Elapsed time during the whole program in seconds:  => face_locations : hog =>",
    #       t1_stop - t1_start)
    for face_location in face_locations:
        # Print the location of each face in this image
        top_Big_Image, right_Big_Image, bottom_Big_Image, left_Big_Image = face_location

        x1_pourcentage, y1_pourcentage, x2_pourcentage, y2_pourcentage = pourcentage(picture.getFileTemp(),
                                                                                     top_Big_Image,
                                                                                     left_Big_Image,
                                                                                     bottom_Big_Image,
                                                                                     right_Big_Image)

        circle(draw,
               (im.size[0] * x1_pourcentage / 100,
                im.size[1] * y1_pourcentage / 100,
                im.size[0] * x2_pourcentage / 100,
                im.size[1] * y2_pourcentage / 100),
               fill=255)

        nameMark = filename + 'mask' + '.png'
        mask.save(nameMark)

        # Blur image
        blurred = im.filter(ImageFilter.GaussianBlur(6))

        # Paste blurred region and save result
        im.paste(blurred, mask=mask)

        # im.save(img)
        # im.save(picture.getFile())

    # face_locations1 = face_recognition.face_locations(image_face, number_of_times_to_upsample=0, model="cnn")
    # for face_location in face_locations1:
    #     # Print the location of each face in this image
    #     top_Big_Image, right_Big_Image, bottom_Big_Image, left_Big_Image = face_location
    #
    #     x1_pourcentage, y1_pourcentage, x2_pourcentage, y2_pourcentage = pourcentage(picture.getFileTemp(),
    #                                                                                  top_Big_Image,
    #                                                                                  left_Big_Image,
    #                                                                                  bottom_Big_Image,
    #                                                                                  right_Big_Image)
    #
    #     circle(draw,
    #            (im.size[0] * x1_pourcentage / 100,
    #             im.size[1] * y1_pourcentage / 100,
    #             im.size[0] * x2_pourcentage / 100,
    #             im.size[1] * y2_pourcentage / 100),
    #            fill=255)
    #
    #     nameMark = filename + 'mask' + '.png'
    #     mask.save(nameMark)
    #
    #     # Blur image
    #     blurred = im.filter(ImageFilter.GaussianBlur(6))
    #
    #     # Paste blurred region and save result
    #     im.paste(blurred, mask=mask)



    # im.save(img)


    im.save(picture.getFile())
    #suppression du fichier tmp et du marsk car ils ne doivent pas être dans le zip
    picture.removeFileTemp()
    os.remove(nameMark)


def circle(draw, xy, fill=None):
    """
    Tracer un cercle sur l image draw
    :param draw: image
    :param xy: coordonnées x et y
    :param fill: remplassage
    :return: void
    """
    x0, y0, x1, y1 = xy
    # draw.rectangle([(x0, y0 + rad), (x1, y1 - rad)], fill=fill)
    draw.pieslice([(x0, y0), (x1, y1)], 0, 360, fill=fill)


def pourcentage(image, top, left, bottom, right):
    """
    :param image: chemin de l'image
    :param top: coordonné Y du premier point
    :param left: coordonné X du premier point
    :param bottom: coordonné Y du deuxième point
    :param right: coordonné X du deuxième point
    :return: x1, y1, x2, y2 en pourcentage
    """
    size_img = Image.open(image)
    x1 = left / size_img.size[0] * 100
    y1 = top / size_img.size[1] * 100
    x2 = right / size_img.size[0] * 100
    y2 = bottom / size_img.size[1] * 100
    return x1, y1, x2, y2


def deleteFiles(folder):
    """

    :param folder:
    :return:
    """
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


if __name__ == "__main__":
    try:
        # chronometre --------------
        # t1_start = perf_counter()


        # url fourni
        json_url_picture = sys.argv[1]

        # repertoire de stockage d image
        path_save_picture = sys.argv[2]

        # repertoire de stockage du zip
        path_save_zip = sys.argv[3]

        # Supprimer tous les fichiers existants dans le répertoire
        deleteFiles(path_save_picture)

        str1 = json_url_picture.replace(']', '').replace('[', '')
        array_url_picture = str1.replace('"', '').split(",")

        # Vérifier qu'il y ai bien 1 image unique dans le tableau pour éviter plantage
        # flag = len(set(array_url_picture)) == len(array_url_picture)

        # Supprimer les eventuels doublons
        list_set = set(array_url_picture)
        # convertir le set en une list
        array_url_picture_unique = (list(list_set))

        list_url = []
        for url in array_url_picture_unique:
            # données pour traitement ----------------------------------------------------------------------------------
            data_worker = {
                "url": url,
                "path_save_picture": path_save_picture
            }
            list_url.append(data_worker)

        # Parallélisme par processus-----------------------------------------------------------------
        pool_size = 15 # your "parallelness"
        pool = Pool(pool_size)
        pool2 = int(multiprocessing.cpu_count() * 4 / 5)
        p = multiprocessing.Pool(pool2)
        result_json = p.map(worker, list_url)
        pool.close()
        pool.join()

        # chronometre -----------------------------------------
        # Stop the stopwatch / counter
        # t1_stop = perf_counter()
        # print("Elapsed time:", t1_stop, t1_start)
        # print("Elapsed time during the whole program in seconds:",
        #       t1_stop - t1_start)

        # onlyfiles = [f for f in listdir(path_save_picture) if isfile(join(path_save_picture, f))]

        # compression des images #######################################################################################
        filenameCompress = path_save_zip + 'image.zip'
        Zip.compressWithoutStructure(path_save_picture, filenameCompress)
        print(json.dumps({"pictures": filenameCompress}))

    except OSError as e:
        print(json.dumps({"error": "Python : blur_fasciale_more_processes.py => OSError main, " + str(e)}))
    except urllib.error.HTTPError as e:
        print(json.dumps({"error": "urllib main : blur_fasciale_more_processes.py =>  " + str(e)}))
