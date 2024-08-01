#!/usr/bin/env python
import os
import zipfile
import datetime

'''
Class permettant de gérer les ZIP

Doc : https://pymotw.com/2/zipfile/
'''


class Zip:
    def __init__(self, filename):
        self.__filename = filename

    # Créer un fichier zip
    @staticmethod
    def compress(path, filename):
        try:
            zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)

            # ziph is zipfile handle
            for root, dirs, files in os.walk(path):
                for file in files:
                    zipf.write(os.path.join(root, file))

        finally:
            zipf.close()

    # Créer un fichier zip sans la structure des répertoires
    @staticmethod
    def compressWithoutStructure(path, filename):
        try:
            zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
            abs_src = os.path.abspath(path)
            for root, dirs, files in os.walk(path):
                for file in files:
                    absname = os.path.abspath(os.path.join(root, file))
                    # list[<start>:<stop>:<step>] :
                    #   https://stackoverflow.com/questions/31633635/what-is-the-meaning-of-inta-1-in-python
                    arcname = absname[len(abs_src) + 1:]
                    zipf.write(absname, arcname)
        finally:
            zipf.close()

    # Information sur le fichier zip
    @staticmethod
    def print_info(archive_name):
        zf = zipfile.ZipFile(archive_name)
        for info in zf.infolist():
            print(info.filename)
            print('\tComment:\t', info.comment)
            print('\tModified:\t', datetime.datetime(*info.date_time))
            print('\tSystem:\t\t', info.create_system, '(0 = Windows, 3 = Unix)')
            print('\tZIP version:\t', info.create_version)
            print('\tCompressed:\t', info.compress_size, 'bytes')
            print('\tUncompressed:\t', info.file_size, 'bytes')

    # Accéder aux données d'un membre d'archive
    @staticmethod
    def extractArchivedFiles(archive_name, filenames):
        zf = zipfile.ZipFile(archive_name)
        for filename in filenames:
            try:
                data = zf.read(filename)
            except KeyError:
                print
                'ERROR: Did not find %s in zip file' % filename
            else:
                print(filename, ':', repr(data))
