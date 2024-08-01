'use strict';

/**
 * Module dependencies.
 */
const crypto = require('crypto');
const fs = require('fs');
const logger = require('../../logger');


/**
 * Class permettant de crypter des données sur différent algotithme
 */
class Crypto {
    /**
     *
     * @param string : text
     * @param algorithm : type d'algometrie
     * @param hex
     * @returns {Promise<string>}
     */
    static async crypto_text(string, algorithm = 'md5', hex = 'hex') {
        try {
            if(string == '') throw 'Aucune tring à hasher'
            return crypto.createHash(algorithm).update(string).digest(hex);
        } catch (e) {
            logger.log({
                level: 'error',
                message: 'train :' + e.toString()
            });
        }
    }
    /**
     *
     * @param string : text
     * @param algorithm : type d'algometrie
     * @param hex
     * @returns {Promise<string>}
     */
    static async crypto_file(file, hashName = 'md5', hex = 'hex') {
        try {
            return new Promise((resolve, reject) => {
                const hash = crypto.createHash(hashName);
                const stream = fs.createReadStream(file);
                stream.on('error', err => reject(err));
                stream.on('data', chunk => hash.update(chunk));
                stream.on('end', () => resolve(hash.digest('hex')));
            });
        } catch (e) {
            logger.log({
                level: 'error',
                message: 'train :' + e.toString()
            });
        }
    }
}


module.exports = Crypto;