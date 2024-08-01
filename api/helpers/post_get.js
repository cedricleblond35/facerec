'use strict';
const PATH = require('path');
const fs = require('fs');
const request = require('request');
const logger = require('../../logger');
const http = require('http');


//https://developer.mozilla.org/fr/docs/Web/HTTP/Basics_of_HTTP/MIME_types/Complete_list_of_MIME_types
const mimeType = {
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpeg',
    '.mp3': 'audio/mpeg',
    '.svg': 'image/svg+xml',
    '.pdf': 'application/pdf',
    '.doc': 'application/msword',
    '.zip': 'application/zip',
    '.gz': 'application/zip',
    '.7z': 'application/x-7z-compressed'
};
/**
 * Returns https.get request options with default headers,
 * for a specified URI.
 * @param {string} uri
 */
// function httpRequest(uri) {
//     const { hostname, pathname, search } = new url.URL(uri)
//     return {
//         hostname,
//         path: `${pathname}${search}`,
//         method: 'GET',
//         headers: { 'User-Agent': 'YVM' },
//     }
// }


function doRequest_post_http(url, files) {
    let domain_name = URL.parse(url).hostname;
    let pathname = URL.parse(url).pathname;
    const extension = PATH.extname(files[0]);
    let variable_url = url.split("?Purpose=");
    let filename = PATH.basename(files[0], extension);

    const options = {
        host: domain_name,
        port: 80,
        path: pathname,
        form: {'Purpose': variable_url[1]},
        method: 'POST',
        headers: {
            'Content-Type': mimeType[extension],
            // 'Content-Length': data.length
        }
    };
    return new Promise(function (resolve, reject) {
        console.log("url:"+url);
        console.log(options);
        const req =  http.request(options, (res) => {
            console.log(`statusCode: ${res.statusCode}`)

            res.setEncoding('utf8');
            let rawData = '';
            res.on('data', (chunk) => { rawData += chunk; });
            res.on('end', () => {
                try {
                    //console.log(parsedData);
                    resolve(rawData);
                } catch (e) {
                    console.error(e.message);
                }
            });
        })

        req.on('error', (error) => {
            console.error(error)
        });

        req.write(files[0]);
        req.end();


    });
}

function doRequest_get_http(url) {
    return new Promise(function (resolve, reject) {
        http.get(url, (res) => {
            const { statusCode } = res;
            const contentType = res.headers['content-type'];

            let error;
            if (statusCode !== 200) {
                error = new Error('Request Failed.\n' +
                    `Status Code: ${statusCode}`);
            } else if (!/^application\/json/.test(contentType)) {
                error = new Error('Invalid content-type.\n' +
                    `Expected application/json but received ${contentType}`);
            }
            if (error) {
                console.error(error.message);
                // Consume response data to free up memory
                res.resume();
                return;
            }

            res.setEncoding('utf8');
            let rawData = '';
            res.on('data', (chunk) => { rawData += chunk; });
            res.on('end', () => {
                try {
                    const parsedData = JSON.parse(rawData);
                    //console.log(parsedData);
                    resolve(parsedData);
                } catch (e) {
                    console.error(e.message);
                }
            });
        })
            .on('error', (e) => {
                console.error(`Got error: ${e.message}`);
            });
    });

}


function handleFailure(err) { console.log(err); };


class Post_Get {
    /**
     *
     * @param url
     * @param files : tableaux de fichiers
     * @returns {Promise<void>}
     *
     * Documentation : https://github.com/request/request
     * https://stackoverflow.com/questions/38428027/why-await-is-not-working-for-node-request-module
     */
    static async post_http(url, files) {
        // return await doRequest_post_http(url, files).then(response => {
        //     return response;
        // })
        //     .catch(error => {
        //         console.log(error);
        //     });;

        return new Promise(function (resolve, reject) {
            try {
                console.log('post_http ---------------------------------')
                console.log('url---'+url)
                console.log('file --'+files[0])
                const extension = PATH.extname(files[0]);
                console.log('extension --'+extension);
                let filename = PATH.basename(files[0], extension);

                var req = request.post(url, function (err, resp, body) {
                    if (err) {
                        console.log('Error!'+err);
                        reject(err);
                    } else {
                        console.log('URL: ' + body);
                        resolve({ "post_http" : true});

                    }
                });
                var form = req.form();
                form.append('file', fs.createReadStream(files[0]));

            }catch (e) {
                console.error(e.toString());
            }

        });




    }
    static async get_http(url){
        try {
            return await doRequest_get_http(url);
        } catch (error) {
            logger.log({
                level: 'error',
                message: 'train :' + e.toString()
            });
        }
    }


    /**
     *
     * @param url
     * @param dest
     * @param cb
     * @returns {Promise<void>}
     */
    static async get_http_received_octect(source, destination, siteID){

        try {
            const file_tmp = destination+siteID+'_knn_model.clf.gz';
            console.log('file_tmp :'+file_tmp);
            let body = [];
            console.log(source)
            // const options = {
            //     uri: url, /* Set url here. */
            //     headers: {
            //         'Content-Type': 'application/octet-stream'
            //     }
            // };
            return new Promise((resolve, reject) => {
                const file = fs.createWriteStream(file_tmp);
                request.get(source)
                    .on('data', (chunk) => {
                        body.push(chunk);
                        file.write(chunk);
                    })
                    .on('end', function () {
                        file.end();
                    })
                    .on('response', function(response) {
                        resolve({response : response, file : file_tmp});
                    })
                    .on('error', (error) => {
                        // au cas où request rencontre une erreur, on efface le fichier partiellement écrit
                        // puis on passe l'erreur au callback
                        fs.unlink(file);
                        reject(error);
                    })
                    .end();
            });


        } catch (error) {
            logger.log({
                level: 'error',
                message: 'get_http_received_octect :' + error.toString()
            });
        }
    }
}
module.exports = Post_Get;