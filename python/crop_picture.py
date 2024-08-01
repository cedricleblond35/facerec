import sys
import json
import os.path
import time
import re

"""
import pour avoir des infos sur me micropresseur
https://pypi.org/project/psutil/
doc : https://psutil.readthedocs.io/en/latest/
"""
import psutil

"""
import pour multiprocessing
"""
from multiprocessing.pool import ThreadPool as Pool
import multiprocessing

from classes.detection import Detection

#from classes.detection. import Detection

json_data = sys.argv[1]
json_download = sys.argv[2]
path_tmpdirectory = sys.argv[3]



def worker(list_directories):
    try:

        file = ""
        for fileDownload in list_directories["downloadObject"]:
            if list_directories["image"]["Image"] == fileDownload["urlDownload"]:
                file = fileDownload["filesDownload"]

        if file != "":
            print(list_directories["image"])
            print(" ----> file :", file)

            for rect in list_directories["image"]["Rectangle"]:
                if "$oid" in rect["V"]:
                    id_personn = rect["V"]["$oid"]
                else:
                    id_personn = rect["V"]

                print('id_personn :', id_personn)

                # Si le visage possede des coordonnees, on crope directe selon coordonnees
                # sinon on detecte puis on crope
                if "X" in rect and "Y" in rect and "W" in rect and "H" in rect:
                    if id_personn != "" and rect["X"] != "" and rect["Y"] != "" and rect["W"] != "" and rect[
                        "W"] is not None and rect["H"] != "" and rect["H"] != None:
                        id_image_face_array = list_directories["image"]["Image"].split("/")
                        id_image = id_image_face_array[len(id_image_face_array) - 1].split("_")[0]
                        extension = id_image_face_array[len(id_image_face_array) - 1].split(".")[1]
                        file_created = id_image + "." + extension
                        directory_name = id_personn

                        directory_ok = create_directory_id_personn(list_directories["path_personn"], directory_name)

                        if directory_ok:
                            x = round(int(list_directories["image"]["Image_W"]) * rect["X"] / 100, 2)
                            y = round(int(list_directories["image"]["Image_H"]) * rect["Y"] / 100, 2)
                            width = round(int(list_directories["image"]["Image_W"]) * rect["W"] / 100, 2)
                            height = round(int(list_directories["image"]["Image_H"]) * rect["H"] / 100, 2)

                            cmd = "convert " + str(file) + " -crop " + str(width) + "x" + str(height) + "+" + str(
                                x) + "+" + str(y) + " " + str(
                                list_directories["path_personn"] + directory_name) + '/' + str(file_created)
                            os.system(cmd)
                else:
                    print("--------> file pour detection: ", file)
                    coordinate, oneFace = Detection.detectionForCorp(file)
                    # detection sur l'image filesDownload
                    # coordinate, oneFace = Detection.detectionForCorp(file)
                    if oneFace:
                        id_image_face_array = list_directories["image"]["Image"].split("/")
                        id_image = id_image_face_array[len(id_image_face_array) - 1].split("_")[0]
                        extension = id_image_face_array[len(id_image_face_array) - 1].split(".")[1]
                        file_created = id_image + "." + extension
                        directory_name = id_personn

                        directory_ok = create_directory_id_personn(list_directories["path_personn"], directory_name)

                        if directory_ok:
                            x = coordinate["left"]
                            y = coordinate["top"]
                            x1 = coordinate["right"]
                            y1 = coordinate["bottom"]
                            width = x1 - x
                            height = y1 - y

                            cmd = "convert " + str(file) + " -crop " + str(width) + "x" + str(height) + "+" + str(
                                x) + "+" + str(y) + " " + str(
                                list_directories["path_personn"] + directory_name) + '/' + str(file_created)
                            os.system(cmd)


        print("------------------------------")
    except NameError as error:
        print("NameError :", error)
    except Exception as exception:
        print("exception :", exception)


def create_directory_id_personn(path_personn, directory_name):
    try:
        regex = '[\da-f]{24}'
        result = re.match(regex, directory_name)
        # print("result : {} pour {}".format(result, directory_name))
        dir = path_personn + directory_name
        if result is not None:
            if not os.path.exists(dir):
                os.makedirs(dir)
            return True
        else:
            return False
    except FileExistsError:
        print("Directory ", dir, " already exists")


def checkCPU():
    cpu_t_percent = psutil.cpu_times_percent(interval=1, percpu=False)
    return cpu_t_percent.user


def waited(time_start):
    if (checkCPU() < 75):
        with open(json_data) as data:
            data_dict = json.load(data)

        with open(json_download) as data:
            download_dict = json.load(data)

        download = json.dumps(download_dict)
        downloadObject = json.loads(download)

        path_personn = path_tmpdirectory + 'personn/'

        data = json.dumps(data_dict)
        dataObject = json.loads(data)

        list_directories = []
        for value in dataObject:
            personndict = {}
            personndict["image"] = value
            personndict["downloadObject"] = downloadObject
            personndict["path_personn"] = path_personn
            list_directories.append(personndict)

        strlist = list((filter(None, list_directories)))

        pool2 = int(multiprocessing.cpu_count() * 15 / 16)
        p = multiprocessing.Pool(pool2)
        p.map(worker, strlist)
        pool_size = 3  # your "parallelness"
        pool = Pool(pool_size)
        pool.close()
        pool.join()
        print("finish")

    else:
        time_intermediaire = time.time()
        dif = time_intermediaire - time_start
        if (dif < 600):
            # print("waited")
            waited(time_start)


if __name__ == "__main__":
    waited(time.time())
