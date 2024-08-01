module.exports = {
    "production": {
        "port": "3000",
        "host": "xxxxxxxxxxxx.lan"

    },
    "test": {
        "port": "3000",
        "host": "xxxxxxxxxxxx.lan"
    },
    "development": {
        "port": "3000",
        "host": "xxxxxxxxxxxx.lan"

    },

    //Répertoire de stockage des fichiers temporaires du microservice
    "path_server" : "/tmp/facerecognition",

    //Répertoire de sauvegarde des fichiers d apprentissage des différents clients
    "path_server_save"              : "/tmp/facerecognition/save/",
    "path_server_save_file_info"    : "/tmp/facerecognition/save/file_info.json",

    //url permettant de poster ou de recuperer le fichier d apprentissage
    //"url_FaceRecognitionLearn" : "http://yyyyyyyyyyyy.lan/ws/FaceRecognitionLearn.php?Purpose=",
    "url_FaceRecognitionLearn" : "/ws/FaceRecognitionLearn.php?Purpose=",

    //Choix pour envoyer ou receptionner des données
    //ex : http://yyyyyyyyyyyy.lan/ws/FaceRecognitionLearn.php?Purpose=GetFiles
    "Purpose":{
        "SetLearningFile": "SetLearningFile",   // envoie du fichier d’apprentissage
        "BadFace" : "BadFace",                  // envoie du fichier JSON des visages foireux
        "GetFiles" : "GetFiles&SiteID=",                // recuperation du json contenant url images/ Face_id ...
        "GetLearningFile" : "GetLearningFile"   // recuperation du dernier fichier reçu de LearningFile (fichier d'apprentissage)
    },

    //parametre de création des répertoire tempraire
    "create_directory_tmp" : {
        "time" : 1,
        "nbRepToKeep" : 2
    },

    "file_trainning" : "trained_knn_model.clf",
    "file_trainning_gz" : "trained_knn_model.clf.gz",
    "file_Face_ko" : "face_ko.json",

    //email recevant les erreurs survenu lors de l'execution
    "mail" : {
            "to": "xxxx@gmail.com"
        }


}
