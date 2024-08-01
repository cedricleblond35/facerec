'use strict';

const fs = require('fs');

const logger = require('../../logger');
const FunctionGB = require('../../../Common_NodeJS/FunctionGB');
const EXECUTE_COMMAND = require('../helpers/execute_command');
const config = require('../config/config');

class Directory {

    static create(path, recursive = false, mode = "0777") {
        try {
            return fs.mkdirSync(path, { recursive: recursive, mode:mode  });
        } catch (stderr) {
            logger.log({
                level: 'error',
                message: stderr
            });
        }


    }
    static read(path) {   }
    static rename(path, new_path) { }
    static remove(path) {
           return  EXECUTE_COMMAND.execute_command(`rm -rf ${path}`)

    }

    static create_path_tmp_directory(){
        try {
            return FunctionGB.createTmpDirectory(config.path_server, config.create_directory_tmp.time,config.create_directory_tmp.nbRepToKeep);
        } catch (e) {
            logger.log({
                level: 'error',
                message: 'create_path_tmp_directory :' + e.toString()
            });
        }
    }
}

module.exports = Directory;