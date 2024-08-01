#!/usr/bin/env python3
# coding: utf-8

""" Compter le nombre de fichiers de chaque dossier.
    Les liens symboliques sont ignorés.
"""

import os.path
from os import scandir


class Counter(object):
    """ Classe qui gère le listage et le comptage de chaque dossier. """

    def __init__(self, path):
        """ Initialisation des variables. """

        if not path:
            raise ValueError('A girl needs a path.')

        self.path = path
        self.files = 0

    def work(self):
        """ La méthode qui scanne le dossier et fait le décompte. """

        # `entry` contient pas mal d'informations. Voir :
        #  https://docs.python.org/3/library/os.html#os.DirEntry
        for entry in scandir(self.path):

            # S'il s'agit d'un dossier qui n'est pas un lien symbolique...
            if entry.is_dir() and not entry.is_symlink():

                # ... On instancie une autre classe de `Counter` afin de faire
                # le décompte des fichiers de ce dossier.
                path = os.path.join(self.path, entry.name)
                counter = Counter(path)

                # `yield from` permet de capter et renvoyer le `yield self` du
                # compteur que l'on vient d'instancier. Pour faire plus simple,
                # on récupère la classe une fois que le décompte du dossier
                # est terminé.
                yield from counter.work()
            else:
                # Il s'agit d'un fichier, on incrémente le compteur.
                self.files += 1

        # On renvoie la classe elle-même. On pourrait aussi renvoyer seulement
        # les infos nécessaires avec un `yield (self.path, self.files)`.
        yield self

    def __str__(self):
        """ Représentation de la classe. Permet de faire :
            >>> print(cls)
            /etc 115
        """

        return '{} {}'.format(self.path, self.files)