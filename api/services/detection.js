const logger = require('../../logger');
const execute_command = require('../helpers/execute_command');

const DIRECTORY = require('../helpers/directory');
const FILES = require('../helpers/files');
const fs = require('fs');


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
                //vérifier la structure de url
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

let detection = {
    async face_blur(url, siteID, host){
      try {
          console.time('face_blur_nodejs');
          if(siteID == null || siteID == ""){
              const crypto = require('crypto');
              siteID =crypto.createHash('md5').update(host).digest("hex");
          }
          const list_url_pictures = await create_list_url_pictures(url);
          const json_url_pictures = JSON.stringify(list_url_pictures);

          let path_tmpdirectory = await DIRECTORY.create_path_tmp_directory();
          const path_save_zip = path_tmpdirectory+siteID+"/";
          const path_blur_face = path_tmpdirectory+siteID+"/blur_face/";

          if (fs.existsSync(path_blur_face)) {
              await FILES.removeall_asyn(path_blur_face);

          } else {
              await fs.mkdirSync(path_blur_face, { recursive: true });
          }
          // console.timeEnd('face_blur_nodejs');

          let cmd = `python3 python/blur_fasciale_more_processes.py ${json_url_pictures} ${path_blur_face} ${path_save_zip}`;
          console.time('face_blur_blur_fasciale_more_processes.py');
          let value = await execute_command.execute_command(cmd);
          // console.timeEnd('face_blur_blur_fasciale_more_processes.py');

          return value;

      }  catch (e) {
          logger.log({
              level: 'error',
              message: 'face_blur :' + e.toString()
          });
      }
    },
    async face_detect(url, siteID, host){
        try {
            if(siteID == null || siteID == ""){
                const crypto = require('crypto');
                siteID =crypto.createHash('md5').update(host).digest("hex");
            }
            const list_url_pictures = await create_list_url_pictures(url);
            const json_url_pictures = JSON.stringify(list_url_pictures);

            let path_tmpdirectory = await DIRECTORY.create_path_tmp_directory();
            const path_recognition = path_tmpdirectory+siteID+"/recognition/";
            await fs.mkdirSync(path_recognition, { recursive: true });
            let cmd = `python3 python/detection_fasciale.py ${json_url_pictures} ${path_recognition}`;
            //console.log(cmd);
            //console.time('face_blur_nodejsxxxxxxxxxx');
            let v=  await execute_command.execute_command(cmd);
            //console.timeEnd('face_blur_nodejsxxxxxxxxxx');
            return v;
        }catch (e) {
            logger.log({
                level: 'error',
                message: 'face_detect :' + e.toString()
            });
        }
    }
};
module.exports = detection;

