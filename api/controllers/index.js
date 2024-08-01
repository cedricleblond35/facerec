const fs = require('fs');
const FunctionGB = require('../../../Common_NodeJS/FunctionGB');
const MAILER =  require('../helpers/mailer');
const detection = require('../services/detection');
const recognition = require('../services/recognition');
const faceRecognitionLearn = require('../services/faceRecognitionLearn');
const config = require('../config/config');
const POST_GET = require('../helpers/post_get');
const PATH = require('path');
const PATH_ABSOLUTE = config.path_server;
const VERIF_DATA = require('../helpers/verif_data');
const CRYPTO = require('../helpers/cryptographic');
const FILES = require('../helpers/files');
const directory_images_recognition = "_images";
const logger = require('../../logger');
const errors = require('../helpers/error-handling');
const errorModel = require('../helpers/errorResponse');
const jp = require('jsonpath');
const util = require('util');



let list_files_download = 0; //liste des fichiers qui n'ont pas été téléchargé


var controllers = {
    /*******************************************************************************************
     * Flouttage des visages
     *
     * @param req
     * @param res
     * @param next
     */
    get_blurFace: (req,  res, next) => {
        try {
            console.log('req :', req);
            detection.face_blur(req.query.data_url, req.query.siteID, req.get('host'))
                .then((result) => {
                    let response = JSON.parse(result.data);

                    if(response.error) {
                        MAILER.sendTC({
                            message:response.error,
                            req: req ,
                            file: PATH.dirname(process.mainModule.filename)
                        });
                        res.setHeader('Content-Type', 'application/zip');
                        res.send("error");
                    }
                    res.download(response.pictures)
                });
        } catch (e) {
            logger.log({
                level: 'error',
                message: 'get_blurFace:' + e.toString()
            });
        }
    },
    post_blurFace: (req,  res, next) => {
        try {
            detection.face_blur(req.body.data_url, req.body.siteID, req.get('host'))
                .then((result) => {
                    let response = JSON.parse(result.data);

                    if(response.error) {
                        MAILER.sendTC({
                            message:response.error,
                            req: req ,
                            file: PATH.dirname(process.mainModule.filename)
                        });
                        res.send("error");
                    }
                    res.setHeader('Content-Type', 'application/zip');
                    res.download(response.pictures)
                });
        }catch (e) {
            logger.log({
                level: 'error',
                message: 'get_blurFace:' + e.toString()
            });
        }
    },
    /*******************************************************************************************
     * Détection faciale
     * @param req
     * @param res
     * @param next
     */
    get_detection: (req,  res, next) => {
        console.log('req => ', req.get('host'));
        detection.face_detect(req.query.data_url, req.query.siteID, req.get('host'))
            .then((result) => {
                res.setHeader('Content-Type', 'application/json');
                res.end(result.data);
            });

    },
    post_detection: (req,  res, next) => {
        detection.face_detect(req.body.data_url, req.body.siteID, req.get('host'))
            .then((result) => {
                res.setHeader('Content-Type', 'application/json');
                res.end(result.data);
            });
    },
    /*********************************************************************************************
     * Apprentissage des différents visages
     * @param req
     * @param res
     * @param next
     */
    get_FaceRecognitionLearn: (req,  res, next) => {
        try {
            logger.log({
                level: 'info',
                message: '---------start ---------'
            });
            console.log('req :', req);
            console.log('req => ', req.get('host'));
            faceRecognition_POST_GET3(req.query.data_url, req.query.siteID, req.get('host'));
            res.setHeader('Content-Type', 'text/plain');
            res.send("Process running");
        } catch (e) {
            let error = new errorModel.errorResponse(errors.invalid_operation.withDetails(e.toString()));
            MAILER.sendTC({
                message:error,
                req: req ,
                file: PATH.dirname(process.mainModule.filename)
            });
            logger.log({
                level: 'error',
                message: 'post_FaceRecognitionLearn:' + e.toString()
            });
        }
    },
    post_FaceRecognitionLearn: (req,  res, next) => {
        try {
            logger.log({
                level: 'info',
                message: '---------start ---------'
            });
            //console.log("data_url : ", req.body.data_url);
            //console.log("SiteID : "+req.body.SiteID);
            faceRecognition_POST_GET3(req.body.data_url, req.body.siteID, req.get('host'));
            res.setHeader('Content-Type', 'text/plain');
            res.send("Process running");
        } catch (e) {
            let error = new errorModel.errorResponse(errors.invalid_operation.withDetails(e.toString()));
            MAILER.sendTC({
                message:error,
                req: req ,
                file: PATH.dirname(process.mainModule.filename)
            });
            logger.log({
                level: 'error',
                message: 'post_FaceRecognitionLearn:' + e.toString()
            });
        }

    },
    /*********************************************************************************************
     * Reconnaissance faciale
     * @param req
     * @param res
     * @param next
     */
    get_Recognition: (req,  res, next) => {
            recognition_POST_GET(req.query.data_url, req.query.siteID, req.query.lazzy, req.get('host'))
                .then((resultat) => {
                    if(resultat.hasOwnProperty('error')){
                        console.log("erreur : =>>>"+resultat.error);
                        throw "resultat.error";
                    } else {
                        res.setHeader('Content-Type', 'application/json');
                        res.send(resultat)
                    }
                }).catch((e)=>
                {
                    logger.log({
                        level: 'error',
                        message: 'get_Recognition  ====>:' + e.toString()
                    });

                    let error = new errorModel.errorResponse(errors.invalid_operation.withDetails(e.toString()));
                    MAILER.sendTC({
                        message:error,
                        req: req ,
                        file: PATH.dirname(process.mainModule.filename)
                    });
                });

    },
    post_Recognition: (req,  res, next) => {
        recognition_POST_GET(req.body.data_url, req.body.siteID, req.body.lazzy,  req.get('host'))
            .then((resultat) => {
                res.setHeader('Content-Type', 'application/json');
                res.send(resultat)
            });
    },

};



/**
 * verifier si le fichier à une taille differente de 0 bytes
 * si 1 fichier n a pas debuté le téchargement, faire une pause
 * @returns {Promise<Promise<*|boolean>|boolean>}
 */
async function verif_file(){
    try {
        //vérifier si un fichier se trouve encore ds la liste , si c'est la cas, attendre
        if( list_files_download > 1){
            await wainted(10);
            return verif_file();
        }
    } catch (e) {
        logger.log({
            level: 'error',
            message: e.toString()
        });
    }
    return true;
}

/**
 *
 * @param url_data
 * @param siteID
 * @param host
 * @returns {Promise<T | * | *>}
 */
async function faceRecognition_POST_GET3  (url_data, siteID, host){
    //mettre le compteur à 0
    list_files_download = 0;
    try {
        return  VERIF_DATA.verif_data.test_url_with_http(url_data+'&SiteID='+siteID)
            .then((response) => {
                    if(response.response === false)
                        throw new Error("Problème avec url cible ");

                    return POST_GET.get_http(url_data+'&SiteID='+siteID)
                        .then(json => {
                            siteID = json['SiteId'];
                            return  faceRecognitionLearn.create_path_tmp_directory()
                                .then(path_tmpdirectory => {
                                    path_tmpdirectory = path_tmpdirectory  + siteID+'/';
                                    return faceRecognitionLearn.create_directory(path_tmpdirectory, directory_images_recognition)
                                        .then((result_create_directory) => {
                                            if(result_create_directory == false) throw new Error("Répertoire non créer" + PATH_ABSOLUTE + "/" + directory_images_recognition);  // génère un objet Error avec le message "Obligatoire" ;
                                            return true;
                                        }).then((response) => {
                                            return {"json" : json, "path_tmpdirectory" : path_tmpdirectory}

                                        });
                                });

                        });

            })
            .then(({json, path_tmpdirectory}) => {
                return downloadFile({"json" : json, "path_tmpdirectory" : path_tmpdirectory})
                    .then(({files}) =>{
                        return {"json" : json, "path_tmpdirectory" : path_tmpdirectory, "files" : files};
                });
            }).then(({json, path_tmpdirectory, files}) => {
                return croppe(
                    {
                        "json" : json,
                        "path_tmpdirectory" : path_tmpdirectory,
                        "files" : files
                    })
                    .then((result) => {
                        return { "path_tmpdirectory" : path_tmpdirectory};
                    })
            }).then(({path_tmpdirectory}) => {
                return verif_face({ "path_tmpdirectory" : path_tmpdirectory, "siteID" : siteID, "host" : host});
            });
    } catch (e) {
        let error = new errorModel.errorResponse(errors.invalid_operation.withDetails(e.toString()));
        MAILER.sendTC({
            message:error,
            req: req ,
            file: PATH.dirname(process.mainModule.filename)
        });
        logger.log({
            level: 'error',
            message: 'get_FaceRecognitionLearn:' + e.toString()
        });
    }
}

/**
 *
 * @param path_tmpdirectory
 * @param siteID
 * @param host
 * @returns {Promise<T | *>}
 */
async function verif_face({path_tmpdirectory, siteID, host}){
    logger.log({
        level: 'info',
        message: '--------- start verif face ---------'
    });
    let path_personn = path_tmpdirectory + "personn/";
    return faceRecognitionLearn.verif_face(path_tmpdirectory, path_personn)
        .then((files_json) => {
            logger.log({
                level: 'info',
                message: '--------- end verif face ---------'
            });
            logger.log({
                level: 'info',
                message: '--------- start delete file face ko ---------'
            });
            logger.log({
                level: 'warn',
                message: '--------- files_json :'+files_json
            });
            console.log("data :",files_json);
            if (files_json["data"] == "") files_json["data"] = "{}";
            let myJSON = JSON.parse(files_json["data"]);
            let file_face_ko = myJSON[0]["file_face_ko"];
            return faceRecognitionLearn.delete_file_face_ko(path_personn, file_face_ko)
                .then((result) => {
                    logger.log({
                        level: 'info',
                        message: '--------- end delete file face ko ---------'
                    });
                    if(result == 'ok')
                    {
                        return faceRecognition(path_tmpdirectory, siteID, host)
                            .then(result=>
                            {
                                console.log("result.result :"+result.result)
                                return result.result;

                            });                                                                            }
                });
        });
}

/**
 *
 * @param json
 * @param path_tmpdirectory
 * @param files
 * @returns {Promise<*>}
 */
async function croppe({json, path_tmpdirectory, files}){
    logger.log({
        level: 'info',
        message: '--------- start croppe ---------'
    });
    console.log('json :', json);
    const data_json = path_tmpdirectory+"json_data.json";
    const file_json = path_tmpdirectory+"json_download.json";
    console.log("start croppe : "+file_json);
    fs.writeFileSync(data_json, JSON.stringify(json["Results"]), 'utf8' );
    fs.writeFileSync(file_json, JSON.stringify(files), 'utf8' );

    return faceRecognitionLearn.crop_picture2(data_json, file_json, path_tmpdirectory)
        .then((result) => {
            logger.log({
                level: 'info',
                message: '--------- end croppe ---------'
            });
            return result;
        })
}

/**
 *
 * @param json
 * @param path_tmpdirectory
 * @returns {Promise<{files: Array}>}
 */
async function downloadFile({json, path_tmpdirectory}){
    logger.log({
        level: 'info',
        message: '--------- start downloadFile ---------'
    });
    //let number_images = 5000;
    const number_images = json["Results"].length;
    console.log("number_images :"+number_images);

    console.log(util.inspect(json, {showHidden: false, depth: null}))
    let limit = 50;
    let x = 0;

    let files = [];
    for (let i = 0; i < number_images ; i=i+limit) {
        //pause de 1/2 seconde pour le techargement 40 images
        await verif_file();

        //Ajuster la limit pour le pas depasser le nombre d'image
        if(i+limit > number_images) limit = number_images-i;

        list_files_download = list_files_download+limit;
        let jsonBis = json["Results"].slice(i, i + limit);


        await jsonBis.forEach(function (value) {
            let personn_no_found = faceRecognitionLearn.verif_file_personn(path_tmpdirectory, value);
            //si au moins 1 personne n est pas trouvé sur la photo alors on la télécharge
            if(personn_no_found != 0) {
                faceRecognitionLearn.download_file(value["Image"], path_tmpdirectory+directory_images_recognition)
                    .then( ({url, path}) => {
                        x++;
                        const file = {
                            filesDownload: path,
                            urlDownload: url
                        };
                        files.push(file);
                        list_files_download--;
                        console.log("ficher telechargé :"+x)
                    });
            }
        });

    }
    await verif_file();
    logger.log({
        level: 'info',
        message: '--------- end downloadFile ---------'
    });
    console.log('downloadFile :', files);
    return {"files" : files};
}


/**
 * Fonction pour la reconnaissance faciale
 * @param url_picture
 * @param siteID
 * @param lazzy
 * @returns {Promise<*>}
 */
async function recognition_POST_GET (url_picture, siteID, lazzy, host) {
    try {

        return recognition.face_recognition(config.path_server_save, siteID, lazzy, url_picture, host)
            .then((result) => {
                    // console.log(Object.prototype.toString.call(result));
                    // console.log(Object.values(result));
                    if(result == undefined)  {
                        let json_error = {"error" : "recognition_POST_GET:recognition.face_recognition = "+result};
                        console.error(json_error);
                        return json_error;
                    } else {
                        let json = JSON.parse(result);
                        return   json;
                    }




            });
    } catch (e) {

        logger.log({
            level: 'error',
            message: 'recognition_POST_GET : '+ e.toString()
        });
        throw e;
    }
}

/**
 * Apprentissage des visages identifiés et envoie des fichiers file_trainning_gz et file_Face_ko
 * @param path_tmpdirectory
 * @returns {Promise<{result: boolean}>}
 */
async function faceRecognition(path_tmpdirectory, siteID, host){
    let path_personn = path_tmpdirectory + "personn/";
    await deleteDirectoryEmpty(path_personn);
    logger.log({
        level: 'info',
        message: '--------- start learning ---------'
    });
    let valueTrain = await faceRecognitionLearn.train(path_personn, path_tmpdirectory);

    if(valueTrain == "Training complete!")
    {
        let md5 = await CRYPTO.crypto_file(path_tmpdirectory + config.file_trainning_gz);
        await faceRecognitionLearn.saveDirectoryTrain(path_tmpdirectory, config.file_trainning, config.path_server_save, siteID);
        //lire le jsonfile --------------------------------------------------------------------------------
        try {
            let filename = config.path_server_save_file_info;
            if(fs.existsSync(filename)){
                //on ajout le siteid et le md5 du fichier d apprentissage compressé
                let jsonStr  = await FILES.read(filename);
                let jsonObj = JSON.parse(jsonStr);
                let list_siteID = jp.query(jsonObj, '$..siteID');
                let find_siteId = false;


                for (let i = 0; i < list_siteID.length; i++)
                {
                    //on cherche le meme iteid
                    if(list_siteID[i] == siteID) {
                        find_siteId = true;
                        //on verifie si le md5 est identique
                        if(jsonObj["md5"][i].md5 != md5){
                            jsonObj["md5"][i].md5 = md5;
                        }
                    }
                }
                //si le siteid n'est pas trouvé, alors il faut le créer
                if(find_siteId == false){
                    let md5_json = { siteID : siteID, md5 : md5 };
                    jsonObj["md5"].push(md5_json);
                }
                //sauvegarde de la nouvelle structure json
                let data = JSON.stringify(jsonObj);
                FILES.create(filename, data);
            } else {
                //si le fichier n'existe, creation du fichier avec les données
                let md5_json ={
                    "md5": [
                        { siteID : siteID, md5 : md5 }
                    ]};
                let data = JSON.stringify(md5_json);
                fs.writeFileSync(filename, data, 'utf8');
            }

        } catch (e) {
            logger.log({
                level: 'error',
                message: 'jsonfile :' + e.toString()
            });
        }
        logger.log({
            level: 'info',
            message: '--------- end learning ---------'
        });
        logger.log({
            level: 'info',
            message: '--------- post learning and face_ko---------'
        });
        let url_PostTrain = "http://"+ host + config.url_FaceRecognitionLearn + config.Purpose.SetLearningFile + '&SiteID='+siteID;
        let status = await faceRecognitionLearn.post_data(url_PostTrain, [path_tmpdirectory + config.file_trainning_gz]);

        let url_PostFace_ko =  "http://"+ host + config.url_FaceRecognitionLearn + config.Purpose.BadFace + '&SiteID='+siteID;
        faceRecognitionLearn.post_data(url_PostFace_ko, [path_tmpdirectory + config.file_Face_ko]);


        let result_post_train = JSON.stringify(status);
        logger.log({
            level: 'info',
            message: '--------- verif post ' + url_PostTrain +' ---------'
        });
        if(JSON.parse(result_post_train).post_http == true)  return {result : true};
    }
    return {result : false};
}

/**
 * Pause de x ms
 * @param ms
 * @returns {Promise<any>}
 */
function wainted(ms) {
    return new Promise(resolve => {
        //console.log("pause -------------------------------------------");
        setTimeout(() => { resolve(ms); }, ms);
    });
}
/**
 * Supprimer les repertoires vides
 * @param path
 * @param path_personn
 */
function deleteDirectoryEmpty(path_personn) {
    //lister les repertoires
    const { readdirSync } = require('fs');
    const getDirectories = source =>
        readdirSync(source, { withFileTypes: true })
            .filter(dirent => dirent.isDirectory())
            .map(dirent => dirent.name);
    let directories = getDirectories(path_personn);
    directories.forEach(function ( directory_id) {
        //nombre de fichier (tuiles) ds le repertoire split
        //Exporter tous les fichiers dans base mongo
        FunctionGB.list_files_directory_recursive_parallel(path_personn+ directory_id, (err, results) =>{
            if (err) throw err;

            //pousser toutes les tuiles en dures du serveur local vers le serveur distant (MongoDb)
            for(let i = 0; i < results.length; i++)
            {
                if(results[i] == 0){
                    deleteFolderRecursive(path_personn+ directory_id);
                }
            }
        });
    });
}
/**
 * supprimer les repertoires recurcivement
 * @type {module:fs}
 */
var deleteFolderRecursive = function(path) {
    if( fs.existsSync(path) ) {
        fs.readdirSync(path).forEach(function(file,index){
            var curPath = path + "/" + file;
            if(fs.lstatSync(curPath).isDirectory()) { // recurse
                deleteFolderRecursive(curPath);
            } else { // delete file
                fs.unlinkSync(curPath);
            }
        });
        fs.rmdirSync(path);
    }
};
module.exports = controllers;