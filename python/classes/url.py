import urllib.error
from urllib.request import urlretrieve

from classes.mailHTML import MailHTML
from datetime import datetime
import subprocess
import sys, traceback, psutil

from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError
class Url:
    def __init__(self, url, path_save_picture):
        self.url = url
        self.path_save_picture = path_save_picture
        self.file = ""

    def get_file(self):
        """Methode qui sera appelée quand on souhaitera accéder en lecture à l'attribut 'file'"""
        self.file = self.url.split("/")[-1]

    def download_file(self):
        """Méthode permettant de télécharger un fichier """
        try:
            self.get_file()
            urllib.request.urlretrieve(self.url, self.path_save_picture + self.file)

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
            message_error = {"error" : "true"}
            print(message_error)
            raise exception

        return self.path_save_picture + self.file
