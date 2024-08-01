// The contents of this file are in the public domain. See LICENSE_FOR_EXAMPLE_PROGRAMS.txt
/*

    This example program shows how to find frontal human faces in an image.  In
    particular, this program shows how you can take a list of images from the
    command line and display each on the screen with red boxes overlaid on each
    human face.

    The examples/faces folder contains some jpg images of people.  You can run
    this program on them and see the detections by executing the following command:
        ./face_detection_ex faces/*.jpg

    
    This face detector is made using the now classic Histogram of Oriented
    Gradients (HOG) feature combined with a linear classifier, an image pyramid,
    and sliding window detection scheme.  This type of object detector is fairly
    general and capable of detecting many types of semi-rigid objects in
    addition to human faces.  Therefore, if you are interested in making your
    own object detectors then read the fhog_object_detector_ex.cpp example
    program.  It shows how to use the machine learning tools which were used to
    create dlib's face detector. 


    Finally, note that the face detector is fastest when compiled with at least
    SSE2 instructions enabled.  So if you are using a PC with an Intel or AMD
    chip then you should enable at least SSE2 instructions.  If you are using
    cmake to compile this program you can enable them by using one of the
    following commands when you create the build project:
        cmake path_to_dlib_root/examples -DUSE_SSE2_INSTRUCTIONS=ON
        cmake path_to_dlib_root/examples -DUSE_SSE4_INSTRUCTIONS=ON
        cmake path_to_dlib_root/examples -DUSE_AVX_INSTRUCTIONS=ON
    This will set the appropriate compiler options for GCC, clang, Visual
    Studio, or the Intel compiler.  If you are using another compiler then you
    need to consult your compiler's manual to determine how to enable these
    instructions.  Note that AVX is the fastest but requires a CPU from at least
    2011.  SSE4 is the next fastest and is supported by most current machines.  
*/





#include <dlib/image_processing/frontal_face_detector.h>
#include <dlib/image_processing/generic_image.h>
#include <dlib/gui_widgets.h>
#include <dlib/image_io.h>
#include <dlib/image_transforms.h>


#include <iostream>
#include <string>
#include <sys/types.h>
#include <dirent.h>
#include <errno.h>
#include <vector>
#include <sstream>

using namespace dlib;
using namespace std;
/*
Retourner un tableau composé du nom du fichier et de son extension.
*/
std::vector<std::string> split(std::string strToSplit, char delimeter)
{
    std::stringstream ss(strToSplit);
    std::string item;
    std::vector<std::string> splittedStrings;
    while (std::getline(ss, item, delimeter))
    {
       splittedStrings.push_back(item);
    }
    return splittedStrings;
}

// ----------------------------------------------------------------------------------------
/**
* Scanner tous les fichiers images
*
**/
std::vector<std::string> getdir ()
{
	DIR *dir;
	struct dirent *ent;
	const char*  directory = "/home/jenkins/web-calcul/www/opencv/data/";
	
	std::vector<std::string> split_name;
	
	if ((dir = opendir ( directory)) != NULL) {
	  /* print all the files and directories within directory */
	  while ((ent = readdir (dir)) != NULL) {
		  std::string filename = ent->d_name;
		  //cout << "\n" << "filename : " << filename;
		  if(filename != "." && filename != "..")
		  {
			  std::ostringstream oss;
			  oss << directory << filename ;
			  std::string file_directory = oss.str();
			  cout << "\n" << "filename : " << filename;

			  split_name = split(filename, '.');
			  
			  cout << "\n" << "name : " << split_name[0] ;
		  }
		   
	  }
	  closedir (dir);
	} else {
	  /* could not open directory */
	  perror ("");
	  //return EXIT_FAILURE;
	}
	
	return split_name;

}
int main(int argc, char** argv)
{  

// a pointer to an int.
   std::vector<std::string> split_name;
   split_name = getdir ();
    try
    {
        if (argc == 1)
        {
            cout << "Give some image files as arguments to this program." << endl;
            return 0;
        }

        frontal_face_detector detector = get_frontal_face_detector();
        //image_window win;

        // Loop over all the images provided on the command line.
        for (int i = 1; i < argc; ++i){
            cout << "processing image " << argv[i] << endl;
            array2d<unsigned char> img;
            load_image(img, argv[i]);
            
			
			// Agrandissez l’image par un facteur deux. Ceci est utile car le détecteur de visage recherche les visages d’environ 80 x 80 pixels ou plus.
			// Par conséquent, si vous souhaitez trouver des faces plus petites que cela, vous devez sur-échantillonner l'image comme nous le faisons ici en appelant pyramid_up (). Cela lui permettra donc de détecter les visages d’au moins 40 x 40 pixels.
			// Nous pourrions appeler pyramid_up () à nouveau pour trouver des faces encore plus petites, mais notez que chaque fois que nous sur-échantillonnons l'image, le détecteur fonctionne plus lentement, car il doit traiter une image plus grande.
            pyramid_up(img);

            // Dites maintenant au détecteur de visage de nous donner une liste de boîtes englobantes autour de tous les visages qu’elle peut trouver dans l’image.
            std::vector<rectangle> dets = detector(img);

            cout << "Number of faces detected: " << dets.size() << endl;
			
            // Maintenant, nous montrons l'image sur l'écran et les détections de visage sous forme de zones de superposition rouges.
            
			//win.clear_overlay();
            //win.set_image(img);
            //win.add_overlayadd_overlay(dets, rgb_pixel(255,0,0));

            //cout << "Hit enter to process the next image..." << endl;
            //cin.get();
			
			for (i=0; i<= 6; i=i+1)
			{
				cout << "cord " <<  i <<  " : " << dets[i] << endl;
				dlib::draw_rectangle(img, dets[i], dlib::rgb_pixel(255, 0, 0), 1);
				
			}
			
			save_png(img, "detected.jpg");
        }
    }
    catch (exception& e)
    {
        cout << "\nexception thrown!" << endl;
        cout << e.what() << endl;
    }
}

// ----------------------------------------------------------------------------------------

