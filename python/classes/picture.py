import os

from PIL import Image
from shutil import copyfile


class Picture:
    def __init__(self, file):
        self.__file = file
        self.__fileTemp = ""

    def removeFileTemp(self):
        """
        Supprime un fichier sur le disque local
        :return:
        """
        if self.__fileTemp != "" and os.path.exists(self.__fileTemp):
            os.remove(self.__fileTemp)

    def convertPNGtoJPG(self, filename):
        """
        Converti une image PNG en JPG
		:param filename: chemin de l'image
		:return:
		"""
        try:
            save = filename + '.jpg'
            im = Image.open(self.__file)
            rgb_im = im.convert('RGB')
            rgb_im.save(save)
            os.remove(self.__file)

        except OSError  as e:
            print(e.code)
            print(e.read())
        return save

    def enlarging(self, filename, file_extension):
        """
        Agrandissement de l'image avec une largeur et hauteur au minimun de 1800px, interpolations  : BICUBIC
        :param filename: chemin de l'image
        :param file_extension: extension de l'image
        :return: retourne le coef d'agrandissement
        """
        try:

            im = Image.open(self.getFile())
            coef = 1
            if im.size[0] < 1800 or im.size[1] < 1800:
                if im.size[0] < im.size[1]:
                    coef = int(1800 / im.size[0])
                else:
                    coef = int(1800 / im.size[1])

                resize_picture = self.resize(coef, "BICUBIC")
                self.setFileTemp(filename + "_resize" + file_extension)
                resize_picture.save(self.getFileTemp())
            else:
                # si le coef =1, pas agrandissement
                self.setFileTemp(filename + "_resize" + file_extension)
                copyfile(self.getFile(), self.getFileTemp())
        except OSError  as e:
            print(e.code)
            print(e.read())
        return coef

    def resize(self, coef, type):
        """
        Redimenssionnement selon un coeficient et type de
        :param coef: coef de redimensionnement
        :param type: interpolations
        :return:
        """
        try:
            im1 = Image.open(self.__file)
            width = im1.size[0] * coef
            height = im1.size[1] * coef

            if type == "NEAREST":
                im2 = im1.resize((width, height), Image.NEAREST)  # use nearest neighbour
            elif type == "BILINEAR":
                im2 = im1.resize((width, height), Image.BILINEAR)
            elif type == "BICUBIC":
                im2 = im1.resize((width, height), Image.BICUBIC)
            elif type == "ANTIALIAS":
                im2 = im1.resize((width, height), Image.ANTIALIAS)
            else:
                print("Aucun type")
        except OSError  as e:
            print(e.code)
            print(e.read())

        return im2

    def getFile(self):
        return self.__file

    def setFile(self, value):
        self.__file = value

    def getFileTemp(self):
        return self.__fileTemp

    def setFileTemp(self, value):
        self.__fileTemp = value
