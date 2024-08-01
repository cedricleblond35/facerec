'use strict';
const NODEMAILER = require('nodemailer');
const config = require('../config/config');
let transporter = NODEMAILER.createTransport({
    host: 'smheb.essos.lan',
    port: 25,
    secure: false,
    tls: {
        rejectUnauthorized: false
    }
});
/**
 * Class permettant de crypter des données sur différent algotithme
 */
class Mailer {
    /**
     *
     * @param string
     * @param algorithm
     * @param hex
     * @returns {Promise<string>}
     */
    static async send(message) {
        try {
            transporter.sendMail(
                {
                    from: 'essai@agelia.com',
                    to: config.mail.to,
                    subject: 'Erreur Node.js : ${JSON.stringify(req.headers.host)}',
                    html: `<b>/!\\ Une erreur a été détectée sur le site. /!\ <br> Voici ses informations :</b>
                <table border="1px solid black">
                <tr><td style='bold; background: #6D6262'>Host</td><td>${JSON.stringify(req.headers.host)}</td></tr>
                <tr><td style='bold; background: #6D6262'>os.hostname()</td><td>${os.hostname()}</td></tr>
                <tr><td style='bold; background: #6D6262'>Statut</td><td>${statusCode}</td></tr>
                <tr><td style='bold; background: #6D6262'>Accept</td><td>${JSON.stringify(req.headers.accept)}</td></tr>
                <tr><td style='bold; background: #6D6262'>Cookie</td><td>${JSON.stringify(req.headers.cookie)}</td></tr>
                <tr><td style="bold; background: #6D6262">Url</td><td>${req.url}</td></tr>
                <tr><td style="bold; background: #6D6262">Message</td><td>${statusMessage}</td></tr>
                <tr><td style="bold; background: #6D6262">Session</td><td>${JSON.stringify(req.session)}</td></tr>
                <tr><td style="bold; background: #6D6262">Mémoire utilisée</td><td>${JSON.stringify(process.memoryUsage())}</td></tr>
                </table>
`
                }
                , function(error, info){
                    if (error) {
                        console.log(error);
                    } else {
                        console.log('Email sent: ' + info.response);
                    }
                });
        } catch (e) {
            logger.log({
                level: 'error',
                message: 'train :' + e.toString()
            });
        }
    }
    static async sendTC({message, req, file}) {
        let date = new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '')
        try {
            transporter.sendMail(
                {
                    from: 'microservicre@agelia.com',
                    to: config.mail.to,
                    subject: 'Erreur Node.js : ',
                    html: `<b>/!\\ Une erreur a été détectée sur le site. /!\ <br> Voici ses informations :</b>
                <table border="1px solid black">
                <tr><td style='bold;'>Date : ${date}</td></tr>
                <tr><td style='bold;'>Statut</td><td>${message.HTTP}</td></tr>
                <tr><td style='bold;'>Detail</td><td>${message.DETAILS}</td></tr>
                <tr><td style='bold;'>Host</td><td>${JSON.stringify(req.headers.host)}</td></tr>
                <tr><td style="bold;">Url</td><td>${req.url}</td></tr>
                <tr><td style="bold;" >File</td><td>${file}</td></tr>
                <tr><td style="bold;">Session</td><td>${JSON.stringify(req.session)}</td></tr>
                <tr><td style="bold;">Message complet</td><td>${message}</td></tr>
                 </table>
`
                }
                , function(error, info){
                    if (error) {
                        console.log(error);
                    } else {
                        console.log('Email sent: ' + info.response);
                    }
                });
        } catch (e) {
            console.log(e.toString())
        }
    }
    static async sendTC2({message}) {
        console.log("message : "+message);
        try {
            transporter.sendMail(
                {
                    from: 'microservicre@agelia.com',
                    to: config.mail.to,
                    subject: 'Erreur Node.js : ',
                    html: `<b>/!\\ Une erreur a été détectée sur le site. /!\ <br> Voici ses informations :</b>
                <table border="1px solid black">
                <tr><td style='bold;'>Date : ${message}</td></tr>
                 </table>
`
                }
                , function(error, info){
                    if (error) {
                        console.log(error);
                    } else {
                        console.log('Email sent: ' + info.response);
                    }
                });
        } catch (e) {
            console.log(e.toString())
        }
    }
}
module.exports = Mailer;