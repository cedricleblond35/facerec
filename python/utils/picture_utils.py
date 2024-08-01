from PIL import Image

class Picture_utils:
    def pourcentage(image, top, left, bottom, right):
        """
        transforme les coordonnées pixels en %
        :param top:
        :param left:
        :param bottom:
        :param right:
        :return:
        """
        size_img = Image.open(image)
        x1 = left / size_img.size[0] * 100
        y1 = top / size_img.size[1] * 100
        x2 = (right / size_img.size[0] * 100) - x1
        y2 = (bottom / size_img.size[1] * 100) - y1
        return x1, y1, x2, y2

    def pixel(top, left, bottom, right):
        """
        transforme les coordonnées du dernier point (bottom, right) en (width, height)  pixels en %
        :param left:
        :param bottom:
        :param right:
        :return:
        """
        x = left
        y = top
        w = right - left
        h = bottom - top
        return x, y, w, h


    def size_image(url):
        """
        Dimension de l image
        :return: largeur et hauteur
        """
        im = Image.open(url)
        width, height = im.size
        return width, height