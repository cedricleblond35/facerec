'use strict';
const fs = require('fs');
// path = require('path');
//const ABSPATH = path.dirname(process.mainModule.filename);
const request = require('request');
/**
 * Class gérant les fichiers
 */
class Files {
    static read(path, encoding = 'utf8') {
        return new Promise((resolve, reject) => {
            let readStream = fs.createReadStream(path, encoding);
            let data = '';
            readStream.on('data', chunk => {
                data += chunk;
            }).on('end', () => {
                resolve(data);
            }).on('error', err => {
                reject(err);
            });
        });
    }
    static create(path, contents) {
        return new Promise((resolve, reject) => {
            fs.writeFile( path, contents, (err, data) => {
                if(!err) {
                    resolve(data);
                } else {
                    reject(err);
                }
            });
        });
    }
    static copy(source, destination) {
        return new Promise((resolve, reject) => {
            fs.copyFile( source, destination, (err, data) => {
                if(!err) {
                    resolve(data);
                } else {
                    reject(err);
                }
            });
        });
    }
    static remove_asyn(path) {
        return new Promise((resolve, reject) => {
            fs.unlink( path, err => {
                if(!err) {
                    resolve(path);
                } else {
                    reject(err);
                }
            });
        });
    }
    /*
    supprimer tous les fichiers ds un répertoire
     */
    static removeall_asyn(directory) {
        return new Promise((resolve, reject) => {
            fs.readdir(directory, (err, files) => {
                reject(err);

                for (const file of files) {
                    fs.unlink(directory+file, err => {
                        if (err) reject(err);
                    });
                }
            });
            resolve(directory);
        })


    }
    static exists(path) {
        return new Promise((resolve, reject) => {
            fs.access( path, fs.constants.F_OK, err => {
                if(!err) {
                    resolve(true);
                } else {
                    resolve(false);
                    //reject(false);
                }
            });
        });
    }
    static list(path){
        return new Promise((resolve, reject) => {
            fs.readdir(path, (err, files) => {
                if(!err) {
                    resolve(files);
                } else {
                    reject(err);
                }
            });
        });
    }
    static download(url, path, file_name){
        const file = fs.createWriteStream(path+'/'+file_name);

        return new Promise((resolve, reject) => {
            let stream = request({
                /* Here you should specify the exact link to the file you are trying to download */
                uri: url,
                headers: {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8,ro;q=0.7,ru;q=0.6,la;q=0.5,pt;q=0.4,de;q=0.3',
                    'Cache-Control': 'max-age=0',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                },
                /* GZIP true for most of the websites now, disable it if you don't need it */
                gzip: true
            })
            // écrit directement le fichier téléchargé
                .pipe(file)
                .on('finish', () => {
                    resolve(path+'/'+file_name);
                })
                .on('error', (error) => {
                    // au cas où request rencontre une erreur
                    // on efface le fichier partiellement écrit
                    // puis on passe l'erreur au callback
                    fs.unlink(path+'/'+file_name);
                    reject(error);
                })
        });
    }
}
module.exports = Files;
