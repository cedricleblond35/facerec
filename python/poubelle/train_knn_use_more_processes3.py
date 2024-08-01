import sys
import math
from sklearn import neighbors
import os
import os.path

from PIL import Image, ImageDraw

import time

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
import pour avoir des infos sur me micropresseur
https://pypi.org/project/psutil/
doc : https://psutil.readthedocs.io/en/latest/
"""
import psutil
