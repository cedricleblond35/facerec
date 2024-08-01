'use strict';
class Verif_data {
    static async test_url_with_http(url) {
        //regex pour http://www.google.com
        const expression = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/gi;
        let regex = new RegExp(expression);
        if (url.match(regex)) {
            return { response : true };
        } else {
            return { response : false };
        }
    }
    static async test_url_without_http(url) {
        //regex pour www.google.com
        const expression = /[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)?/gi;
        let regex = new RegExp(expression);
        if (url.match(regex)) {
            return { response : true };
        } else {
            return { response : false };
        }
    }
}
module.exports = {
    verif_data : Verif_data
};