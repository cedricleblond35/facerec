import sys
import urllib.request

from classes.detection import Detection

# from time import perf_counter


""""
Collecte une image selon une url fourni et envoie un json contenant Id_name, et le rectangle en % et en pixel
selon la détection fasciale.


"""
if __name__ == "__main__":
    try:
        # url fourni
        json_url_picture = sys.argv[1]
        # repertoire de stockage d image
        path_save_picture = sys.argv[2]
        # t1_start = perf_counter()
        detection = Detection(json_url_picture, path_save_picture)
        detection.processing()
        # t1_stop = perf_counter()
        # print("Elapsed time during the whole program in seconds:  => Detection =>",
        #       t1_stop - t1_start)


    except urllib.error.HTTPError as e:
        print(e.code)
        print(e.read())