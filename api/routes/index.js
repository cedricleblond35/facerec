'use strict';

let controller = require('../controllers/index');

module.exports = function(app) {
    /**
     * Détection facial
     * GET http://xxxxxxxxx.lan:3000/FACE:/detection/?siteID=180&data_url=http://yyyyyyyyyyy.lan/fs01/IEL01/180/f/5d7777b70000000000000000_BIG.png
     *
     * POST http://xxxxxxxxx.lan:3000/FACE:/detection/
     * Body => x-www-form-urlencoded :
     *  data_url :  http://photos-mds.test.alphasia.com/fs01/IEL01/222/f/5d9610770000000000000000_BIG.png?T=20191004.192921|http://www.olivierroller.com/archives/photos/normal/biehle-jurgen1.jpg
     *  siteId :    180
     */
    app.route('/:FACE:/detection')
        .get(controller.get_detection);
    app.route('/:FACE:/detection')
        .post(controller.post_detection);


    /**
     * Apprentissage
     *
     * GET  http://xxxxxxxxx.lan:3000/FACE:/recognitionLearn/?data_url=http://yyyyyyyyyyy.lan/ws/FaceRecognitionLearn.php?Purpose=GetFiles&SiteID=180
     *
     * POST http://xxxxxxxxx.lan:3000/FACE:/recognitionLearn/
     * Body => x-www-form-urlencoded :
     *  data_url :  http://yyyyyyyyyyy.lan/ws/FaceRecognitionLearn.php?Purpose=GetFiles
     *  SiteID :    180
     */
    app.route('/:FACE:/recognitionLearn')
        .get(controller.get_FaceRecognitionLearn);
    app.route('/:FACE:/recognitionLearn')
        .post(controller.post_FaceRecognitionLearn);

    /**
     * Reconnaissance faciale
     * GET http://xxxxxxxxx.lan:3000/FACE:/recognition/?siteID=180&lazzy=1&data_url=http://www.olivierroller.com/archives/photos/normal/biehle-jurgen1.jpg|http://www.deuframat.de/fileadmin/_processed_/csm_bild04_09_079fa65f20.jpg
     *
     * POST http://xxxxxxxxx.lan:3000/FACE:/recognition/
     * Body => x-www-form-urlencoded :
     *  data_url :  http://www.olivierroller.com/archives/photos/normal/biehle-jurgen1.jpg|http://yyyyyyyyyyy.lan/fs01/IEL01/180/f/5a86a42d0000000000000002_BIG.jpg
     *  SiteID :    180
     *  lazzy = 0
     *
     */
    app.route('/:FACE:/recognition')
        .get(controller.get_Recognition);
    app.route('/:FACE:/recognition')
        .post(controller.post_Recognition);

    //4) route utilisée pour faire du blur
    /**
     * route utilisée pour flouter des visages sur des photos
     * GET http://xxxxxxxxx.lan:3000/FACE:/blurFace/?siteID=180&data_url=http://yyyyyyyyyyy.lan/fs01/IEL01/180/f/5d7777b70000000000000000_BIG.png|http://yyyyyyyyyyy.lan/fs01/IEL01/180/f/5ad08c900000000000000000_BIG.jpg
     *
     * POST => http://xxxxxxxxx.lan:3000/FACE:/blurFace/
     *  data_url : http://yyyyyyyyyyy.lan/fs01/IEL01/180/f/5d7777b70000000000000000_BIG.png|http://yyyyyyyyyyy.lan/fs01/IEL01/180/f/5ad08c900000000000000000_BIG.jpg
     *  siteID = 180
     */
    app.route('/:FACE:/blurFace')
        .get(controller.get_blurFace);
    app.route('/:FACE:/blurFace')
        .post(controller.post_blurFace);



};
