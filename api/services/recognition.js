const logger = require('../../logger');
const execute_command = require('../helpers/execute_command');
const FILE = require('../helpers/files');
const VERIF_DATA = require('../helpers/verif_data');

const FILES = require('../helpers/files');

const MAILER =  require('../helpers/mailer');
const PATH = require('path');



const DIRECTORY = require('../helpers/directory');
const POST_GET = require('../helpers/post_get');
const config = require('../config/config');
const fs = require('fs');
const jp = require('jsonpath');


/**
 *
 * @param responses
 * @param path_tmp
 * @param siteID
 * @returns {Promise<void>}
 */
copy_file_clf = async ({responses, path_tmp, siteID}) => {
    try {
        if(!fs.existsSync(responses.file)) throw "Pas de fichier à decompresser :"+responses.file;

        await execute_command.execute_command('gunzip -fk '+responses.file);

        let source_file = path_tmp +siteID+'/' + siteID + '_knn_model.clf';
        let dest_file = config.path_server  + '/save/'+  + siteID + '_knn_model.clf';
        if(fs.existsSync(source_file)){
            fs.copyFileSync(source_file, dest_file);
        } else {
            throw "Pas de fichier clf " + source_file;
        }
    } catch (e) {
        logger.log({
            level: 'error',
            message: 'copy_file_clf :' + e.toString()
        });
    }

};



/**
 * Retourne la liste des url à analyser pour les photos
 * @param url_picture
 * @returns {Promise<never|string[]>}
 */
create_list_url_pictures = async (url_picture) => {
    try {

        let url_pictures_array = url_picture.split('|');
        //supprimer url des cibles sont si ko
        if(url_pictures_array.length == 0) throw Error("Problème d url");
        if(url_pictures_array.length > 1) {
            for (let i = 0; i < url_pictures_array.length; i++) {
                let response = await VERIF_DATA.verif_data.test_url_with_http(url_pictures_array[i]);
                if (response.response == false) {
                    url_pictures_array.splice(index, 1);
                }
            }
        } else {
            let response = VERIF_DATA.verif_data.test_url_with_http(url_pictures_array[0]);
            if(response == false) throw Error("URL cible non correcte pour face_recognition : "+ url_pictures_array[0]);
        }
        return url_pictures_array;
    }catch (e) {
        logger.log({
            level: 'error',
            message: 'create_list_url_pictures :' + e.toString()
        });
    }
}

/**
 * Execute la commande de python pour la reconnaissance
 * @param json
 * @param file
 * @returns {Promise<{data: *}>}
 */
execute_face_recognition = async ({path, json, file }) => {
    try {

        let cmd = `python3 python/face_recognition_knn-perso2.py ${json} ${file} ${path}`;
         console.log("=============> cmd :"+cmd);
        // console.time('execute_face_recognition');
        let result = await execute_command.execute_command(cmd);
        // console.timeEnd('execute_face_recognition');
        console.log("result execute_face_recognition:",result.data);
        return result.data;
    } catch (e) {
        logger.log({
            level: 'error',
            message: '**********************************execute_face_recognition :' + e.toString()
        });
        MAILER.sendTC({
            message:'execute_face_recognition :' + e.toString(),
            req: '' ,
            file: PATH.dirname(process.mainModule.filename)
        });
    }

};

/**
 * Chercher le md5 correspondant au siteId
 * @param siteID
 * @returns {Promise<string>}
 */
find_md5 = async ({ siteID}) => {
    let md5_find = 'inconnu';
    try {
        if(fs.existsSync(config.path_server_save_file_info)){
            let jsonStr  = await FILES.read(config.path_server_save_file_info);
            let jsonObj = JSON.parse(jsonStr);
            let list_siteID = jp.query(jsonObj, '$..siteID');

            //on parcour la liste des siteid pour trouver le md5
            for (let i = 0; i < list_siteID.length; i++)
            {
                if(list_siteID[i] == siteID)  md5_find = jsonObj["md5"][i].md5;
            }
        }
    }catch (e) {
        logger.log({
            level: 'error',
            message: 'find_md5 :' + e.toString()
        });
    }

    return md5_find;
};


/**
 * Télécharge le fichier d'apprentissage
 * @param md5_file
 * @param siteID
 * @param path_tmpdirectory
 * @returns {Promise<void>}
 */
dowload_learningfile = async ({md5_file, siteID, path_tmpdirectory, host}) =>{
    let url_PostTrain = "http://"+ host+ config.url_FaceRecognitionLearn + config.Purpose.GetLearningFile + '&MD5='+ md5_file + '&SiteID='+siteID;
    //console.log(`dowload_learningfile => post: ${url_PostTrain} siteID:${siteID} path_tmpdirectory:${path_tmpdirectory}`);
    return   await POST_GET.get_http_received_octect(url_PostTrain,path_tmpdirectory+siteID+'/', siteID);

};
/**
 * Ajout les informations ( { siteID : siteID, md5 : md5 }) dans le fichier json
 * @param responses
 * @param siteID
 * @param path_tmpdirectory
 * @returns {Promise<void>}
 */
add_data_file_info = async ({responses, siteID, path_tmpdirectory}) => {
    try {
        // statusCode == 200 : reception du fichier d'apprentissage
        // statusCode == 304 : aucun fichier à receptionner car md5 identique
        if(responses.response.statusCode == 200){
            if(fs.existsSync(config.path_server_save_file_info)){
                let jsonStr  = await FILES.read(config.path_server_save_file_info);
                let jsonObj = JSON.parse(jsonStr);
                let list_siteID = jp.query(jsonObj, '$..siteID');
                let find_siteId = false;

                for (let i = 0; i < list_siteID.length; i++)
                {
                    if(list_siteID[i] == siteID) {
                        find_siteId = true;
                        jsonObj["md5"][i].md5 = responses.response.headers.md5;
                        let data = JSON.stringify(jsonObj);
                        FILES.create(config.path_server_save_file_info, data);

                    }
                }
                //si le siteid n'est pas trouvé, alors il faut le créer
                if(find_siteId == false){
                    let md5_json = { siteID : siteID, md5 : md5 };
                    jsonObj["md5"].push(md5_json);
                    let data = JSON.stringify(jsonObj);
                    FILES.create(config.path_server_save_file_info, data);
                }

            } else {
                //si le fichier n'existe pas, creation du fichier avec les données
                let md5_json ={"md5": [{ siteID : siteID, md5 : responses.response.headers.md5 }]};
                let data = JSON.stringify(md5_json);
                fs.writeFileSync(config.path_server_save_file_info, data);
            }

            //si le md5 est different on copie le fichier d apprentissage
            await copy_file_clf({responses : responses, path_tmp : path_tmpdirectory, siteID : siteID});
        }
    } catch (e) {
        logger.log({
            level: 'error',
            message: 'add_data_file_info :' + e.toString()
        });
    }

};
/**
 *
 * @type {{face_recognition(*, *=, *=, *=): Promise<{data: *}>}}
 */
let recognition = {
    /**
     *
     * @param url
     * @param path_trainning : chemin du fichier d entrainement , ex : /tmp/face
     * @returns {Promise<{data: *}>}
     */
    async face_recognition(path_server_save, siteID, lazzy, url_picture, host) {
        let data_face_recognition = '';

        let file_trainning = path_server_save+ siteID + '_knn_model.clf';
        let md5_file = '';

        try {
            //tester si le répertoire de stockage des fichier d'apprentissage existe
            if(!fs.existsSync(config.path_server_save)) {
                fs.mkdirSync(config.path_server_save), { recursive: true };
                lazzy = 1;
            }

            let list_url_pictures = await create_list_url_pictures(url_picture);
            let json_url_pictures = JSON.stringify(list_url_pictures);
            //console.log('json_url_pictures:'+json_url_pictures)

            let path_tmpdirectory = await DIRECTORY.create_path_tmp_directory();
            const path_recognition = path_tmpdirectory+siteID+"/recognition/";
            await fs.mkdirSync(path_recognition, { recursive: true });


            if(lazzy != undefined && lazzy == 1 && FILE.exists(file_trainning)){
                //Faire une reconnaissance puis une une mise à jours du .dat
                //console.log(('Faire une reconnaissance puis une une mise à jours du .dat'))

                //--------------------------- reconnaissance fasciale -----------------------------------------------------
                data_face_recognition = await execute_face_recognition({path : path_recognition, json :json_url_pictures, file : file_trainning});


                //Mettre à jour le fichier d'apprentissage ----------------------------------------------------------------
                md5_file = await find_md5({ siteID : siteID});
                let responses = await dowload_learningfile({md5_file : md5_file, siteID : siteID, path_tmpdirectory : path_tmpdirectory, host: host});
                add_data_file_info({responses : responses, siteID : siteID, path_tmpdirectory : path_tmpdirectory});




            }
            else {
                //Faire une mise à jours du .dat puis une reconnaissance
                console.log('Faire une mise à jours du .dat puis une reconnaissance')

                //Mettre à jour le fichier d'apprentissage ----------------------------------------------------------------
                md5_file = await find_md5({ siteID : siteID});
                let responses = await dowload_learningfile({md5_file : md5_file, siteID : siteID, path_tmpdirectory : path_tmpdirectory, host: host});
                await add_data_file_info({responses : responses,  siteID : siteID, path_tmpdirectory : path_tmpdirectory});

                //--------------------------- reconnaissance fasciale -----------------------------------------------------
                data_face_recognition = await execute_face_recognition({path : path_recognition, json :json_url_pictures, file : file_trainning});
            }

            logger.log({
                level: 'info',
                message: 'face_recognition :' + data_face_recognition
            });

            return data_face_recognition;


        } catch (e) {
            logger.log({
                level: 'error',
                message: 'face_recognition :' + e.toString()
            });
        }
    }
};
module.exports = recognition;