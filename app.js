//framework de routage
let express = require('express');






//e module de chemin fournit des utilitaires pour travailler avec les chemins de fichiers et de répertoires
const path = require('path');

//Analyser les corps des demandes entrantes dans un middleware avant vos gestionnaires, disponible dans la propriété req.body.
let bodyParser = require('body-parser');

//L'objet de processus est un objet global qui fournit des informations sur le processus Node.js actuel et le contrôle de celui-ci.
const process = require('process');


var compression = require('compression');

//var mailsend = require('api/helpers/mailer');
var methodOverride = require('method-override');
var createError = require('http-errors')



const logger = require('./logger');
let configuration = require('./api/config/config');
const port = process.env.NODE_ENV === 'development' ? configuration.development.port : configuration.production.port;


let app = express();
app.use(compression());         // compress all responses

app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));


/***************************** session **********************************/
var session = require('express-session');
app.set('trust proxy', 1) // trust first proxy
app.use(session({
    secret: 'keyboard cat',
    cookie: { maxAge: 600 },
    proxy: true,
    resave: true,
    saveUninitialized: true
}))
app.disable('x-powered-by');



// error handler
app.use(function(err, req, res, next) {
    // set locals, only providing error in development
    res.locals.message = err.message;
    res.locals.error = req.app.get('env') === 'development' ? err : {};

    // render the error page
    res.status(err.status || 500);
    res.render('error');
});


/********************* Route des microservice **************************/
let routes = require('./api/routes/index');
routes(app);


/********************* demarrage du  microservice **************************/
app.listen(port, function (err) {
    console.log('----------- server started -----------');
    console.log("Port utilisé :%s", port);
    console.log('pid is ' + process.pid);
});


process.on('exit', (code) => {
    console.log(`About to exit with code: ${code}`);
});