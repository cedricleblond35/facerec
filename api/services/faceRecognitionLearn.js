const FunctionGB = require('../../../Common_NodeJS/FunctionGB');
const config = require('../config/config');
const fs = require('fs');
const PATH = require('path');
const PROCESS = require('process');
const logger = require('../../logger');
const execute_command = require('../helpers/execute_command');
const DIRECTORY = require('../helpers/directory');
const POST_GET = require('../helpers/post_get');
const FILE = require('../helpers/files');
const ERROR_HANDLING = require('../helpers/error-handling');
let faceRecognitionLearn = {
    /**
     * Créer le répertoire temporaire
     * @param path_absolute
     * @returns {Promise<void>}
     */
    async create_path_tmp_directory(){
        try {
            return FunctionGB.createTmpDirectory(config.path_server, config.create_directory_tmp.time,config.create_directory_tmp.nbRepToKeep);
        } catch (e) {
            logger.log({
                level: 'error',
                message: 'create_path_tmp_directory :' + e.toString()
            });
        }
    },
    /**
     * Fait une copie de sauvegarde du fichier d'apprentissage dans le répertoire path_save
     * Nommage du fichier : siteId + '_knn_model.clf'
     *
     * @param path_tmp_directory :  {string} /tmp/facerecognition/date/
     * @param filename :  {string} trained_knn_model.clf
     * @param path_save : {string} /tmp/facerecognition/save
     * @param siteId : {number}
     * @returns {Promise<void>}
     */
    async saveDirectoryTrain(path_tmp_directory, filename, path_save, siteId) {
        try {
            let oldFile = path_tmp_directory + filename;
            let newFile = path_save + siteId + '_knn_model.clf';

            await fs.mkdirSync(path_save, { recursive: true });
            await fs.copyFileSync(oldFile, newFile);
            logger.log({
                level: 'warn',
                message: '---------------- fichier entrainement sauvegardé ---------------'
            });
        } catch (e) {
            logger.log({
                level: 'error',
                message: 'saveDirectoryTrain :' + e.toString()
            });
        }
    },
    /**
     *
     * @param url
     * @param file
     * @returns {Promise<void>}
     */
    async post_data(url, files){
        return await POST_GET.post_http(url, files);
    },
    /**
     *
     * @param path_personn
     * @param path_trained_knn_model
     * @returns {Promise<{data: *}>}
     */
    async train(path_personn, path_trained_knn_model){
        let value = '';
        let cmd = `python3 python/train_knn_more_processes.py ${path_personn} ${path_trained_knn_model}`;
        try {
            logger.log({
                level: 'warn',
                message: cmd+ '---------------- Début de l apprentissage -------------',
            });
            value = await execute_command.execute_command(cmd);
            logger.log({
                level: 'warn',
                message: '---------------- entrainement fini ---------------'
            });
            return value.data;
        } catch (e) {
            logger.log({
                level: 'error',
                message: 'train :' + e.toString()
            });
        }
    },
    /**
     * Suppression des images faisant partie de la liste des ko dans le fichier json : face_ko.json
     * @param PATH_ABSOLUTE
     * @param file_face_ko
     * @returns {Promise<string>}
     */
    async delete_file_face_ko(path_personn, file_face_ko){
        try {
            let data = await fs.readFileSync(file_face_ko, 'utf8');
            let  data_array= JSON.parse(data);
            for (const personn of data_array)
            {
                let directory = path_personn + personn["id_personn"] + '/';
                await FILE.remove_asyn(directory+personn["Image"] + '.' + personn["Extension"]);

                if(await FILE.list(directory) == 0) { await DIRECTORY.remove(directory); }
            }
            return 'ok';
        } catch (stderr) {
            logger.log({
                level: 'error',
                message: 'stderr :' + stderr
            });
        }
    },
    /**
     * Vérifier si l'image de la personne existe deja ds le répertoire
     * Si une personne n 'est pas trouvé alors retourner personn_no_found = 1 afin de signaler qu'elle n'a pas
     * été traité
     * @param path_tmpdirectory
     * @param json
     * @returns {Promise<number>}
     */
    async verif_file_personn(path_tmpdirectory, json){
        let personn_no_found = 0;
        const path_array = json["Image"].split("/");
        let image =  path_array[path_array.length-1];
        let image_array = image.split(".");
        let name_image = image_array[0].replace('_BIG','');
        try {
            for (const rectangle of json["Rectangle"])
            {
                let personn = rectangle["V"];
                let path = path_tmpdirectory+"personn/"+personn+"/"+ name_image+"."+image_array[1];
                if (!fs.existsSync(path)) {
                    personn_no_found = 1;
                    break;
                }
            }
        } catch(err) {
            logger.log({
                level: 'error',
                message: 'verif_file_personn :' + err.toString()
            });
        }
        return personn_no_found;
    },
    /**
     *
     * @param url
     * @param path
     * @returns {Promise<string>}
     */
    async download_file(url, path) {
        let file_name_array = url.split("/");
        let file_name = file_name_array[file_name_array.length - 1];
        try {
            await FILE.download(url, path, file_name);
            return {"url" :url,  "path": path + '/' + file_name};
        } catch (e) {
            logger.log({
                level: 'error',
                message: 'download_file :' + e.toString()
            });
            return "false";
        }
    }
    ,
    /**
     *
     * @param name
     * @returns {Promise<void>}
     */
    async create_directory(path, name){
        let regex = /[\da-w]/g;
        let found = name.match(regex);
        let dir = path + '/' + name;
        if(found != null)
        {
            try {
                return await fs.mkdirSync(dir, { recursive: true });
            } catch (e) {
                ERROR_HANDLING.errorhandling(
                    {   label: PATH.basename(PROCESS.mainModule.filename),
                        date: new Date().toISOString().replace(/T/, ' ').replace(/\..+/, ''),
                        error: e.toString() });
                logger.log({
                    level: 'error',
                    message: 'create_directory mkdirSync:' + e.toString()
                });
                return  false;
            }
        } else {
            logger.log({
                level: 'error',
                message: 'create_directory :' + dir
            });
            return  false;
        }
    },
    /**
     *
     * @param path
     * @param name
     * @param info_image
     * @returns {Promise<string>}
     */
    // async create_directory_id_personn(path, name, info_image){
    //     try {
    //         const regex = /[\da-f]{24}/g;
    //         let found = name.match(regex);
    //         let dir = path +  name;
    //         //vérifier si le idnom respecte de regex
    //         if(name.match(regex) != null)
    //         {
    //             //si le repertoire n 'existe, le créer
    //             if (!fs.existsSync(dir)){
    //                 await DIRECTORY.create(dir, true);
    //                 return "true";
    //             }
    //             else {
    //                 return "true";
    //             }
    //         } else {
    //             throw "Id la personne :" + name +" ne respecte pas le regex pour l image:"+info_image;
    //         }
    //     } catch (e) {
    //         return new Error(e.toString());
    //         logger.log({
    //             level: 'error',
    //             message: 'create_directory_id_personn : '+e
    //         });
    //     }
    // },

    /**
     *
     * @param data_json
     * @param file_json
     * @param path_tmpdirectory
     * @returns {Promise<boolean>}
     */
    async crop_picture2(data_json, file_json, path_tmpdirectory){
        try {
            const cmd= `python3 python/crop_picture.py ${data_json} ${file_json} ${path_tmpdirectory}`;
            console.log('cmd crop :'+cmd);
            let result = await execute_command.execute_command(cmd);
            console.log('result : '+result)
            return true;
        } catch (e) {
            logger.log({
                level: 'error',
                message: 'crop_picture :' + e
            });
        }

    },
    /**
     *
     * @param image
     * @param dest_directory répertoire de sourvegarde de l'image croppée (id de la personne)
     * @param file_created nom de fichier enregistré
     * @param image_W point X du rectangle de croppage
     * @param image_H point Y du rectangle de croppage
     * @param width_percentage largeur de l image en %
     * @param height_percentage hauteur de l image en %
     * @param x_percentage
     * @param y_percentage
     * @returns {Promise<string>}
     */
    // async crop_picture(image,
    //                    file_created,
    //                    image_W,
    //                    image_H,
    //                    width_percentage,
    //                    height_percentage,
    //                    x_percentage,
    //                    y_percentage)
    // {
    //     try {
    //         console.log("----------------------------------------------------------------")
    //         console.log("crop photo :"+image)
    //         let x = image_W * x_percentage/100;
    //         let y = image_H * y_percentage/100;
    //         let width = image_W * width_percentage/100;
    //         let height = image_H * height_percentage/100;
    //         let cmd = `convert ${image} -crop ${width}x${height}+${x}+${y} ${file_created}`;
    //         console.log("commande :"+cmd)
    //         await execute_command.execute_command(cmd);
    //         console.log("crop photo fini :"+image)
    //         return file_created;
    //     } catch (stderr) {
    //         logger.log({
    //             level: 'error',
    //             message: 'crop_picture :' + stderr
    //         });
    //     }
    // },
    /**
     * Vérifier si l image contient une tête
     * @returns {Promise<string>}
     */
    async verif_face(pathTmp, path_personn){
        try {
            let cmd = `python3 python/detection_fasciale_file_server_work_all_files_use_more_processes3.py ${pathTmp} ${path_personn}`;
            console.log("verif_face :"+cmd);
            let value = await execute_command.execute_command(cmd);
            return value;
        } catch (stderr) {
            logger.log({
                level: 'error',
                message: 'verif_face :' + stderr
            });
        }
    }
};
module.exports = faceRecognitionLearn;