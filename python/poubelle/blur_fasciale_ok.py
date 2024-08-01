import sys
import json
import os

from os import listdir
from os.path import isfile, join

#bibliothèque face
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter
import face_recognition
import urllib.request

from classes.url import Url
from classes.picture import Picture


"""
import pour compression  
"""
import gzip
import shutil
""""
Collecte une image selon une url fourni et envoie un json contenant Id_name, et le rectangle en % et en pixel 
selon la détection fasciale.


"""


#Dossier de stockage
#directory = "/tmp/"

def rounded_rectangle(draw, xy, rad, fill=None):
	x0, y0, x1, y1 = xy
	draw.rectangle([ (x0, y0 + rad), (x1, y1 - rad) ], fill=fill)
	draw.rectangle([ (x0 + rad, y0), (x1 - rad, y1) ], fill=fill)
	draw.pieslice([ (x0, y0), (x0 + rad * 2, y0 + rad * 2) ], 180, 270, fill=fill)
	draw.pieslice([ (x1 - rad * 2, y1 - rad * 2), (x1, y1) ], 0, 90, fill=fill)
	draw.pieslice([ (x0, y1 - rad * 2), (x0 + rad * 2, y1) ], 90, 180, fill=fill)
	draw.pieslice([ (x1 - rad * 2, y0), (x1, y0 + rad * 2) ], 270, 360, fill=fill)



if __name__ == "__main__":
	try:
		#url fourni
		json_url_picture = sys.argv[1]
		
		#repertoire de stockage d image
		path_save_picture = sys.argv[2]
		
		#repertoire de stockage du zip
		path_save_zip = sys.argv[3]
		
		str1 = json_url_picture.replace(']','').replace('[','')
		array_url_picture = str1.replace('"','').split(",")
		data = []
		people_dictionary  = {}
		
		
		for url in array_url_picture:
			#check file ###############################################
			url_check = Url(url, path_save_picture)
			image = url_check.download_file()
			
			picture = Picture(image)
			
			print("image :{}".format(image))
			
			#variable ################################################
			#Creating Array
			
			rectangles_pourcentage_array = []
			rectangles_pixel_array = []
			face_array = []
			
			
			filename, file_extension = os.path.splitext(image)
			
			if(file_extension == ".png"):
				image = picture.convertPNGtoJPG(filename)
				picture.setFile(image)
			
			#Agrandissement et sauvegarde de la photo
			resize_picture = picture.resize(2, "BICUBIC")
			resize_picture.save(picture.getFile())
			

			#detection faciale ############################################
			img = picture.getFile()
			image_face = face_recognition.load_image_file(img)
			i = 1
			face_locations = face_recognition.face_locations(image_face)
			count = len(face_locations)
			
			for face_location in face_locations:
				# Print the location of each face in this image
				top, right, bottom, left = face_location
				print("face :{}".format(i))
				i += 1
				
				im = Image.open(img)
				# Create rounded rectangle mask
				mask = Image.new('L', im.size, 0)
				draw = ImageDraw.Draw(mask)
				rounded_rectangle(draw, (left, top, right, bottom), rad=30, fill=255)
				mask.save('mask.png')

				# Blur image
				blurred = im.filter(ImageFilter.GaussianBlur(6))
				
				# Paste blurred region and save result
				im.paste(blurred, mask=mask)
				im.save(img)
				

		#onlyfiles = [f for f in listdir(path_save_picture) if isfile(join(path_save_picture, f))]
		
		#tar -czvf /tmp/facerecognition/20191212_14/180/image.gz -C /tmp/facerecognition/20191212_14/180/ blur_face/
		filecompress = path_save_zip + 'image.gz'
		
		command = 'tar -czf {} -C {} blur_face'.format(filecompress, path_save_zip)
		os.system(command)
		
		data_json = { "pictures" : filecompress}
		print(json.dumps(data_json))
		

	except OSError  as e:
		print(e.code)
		print(e.read())
	except urllib.error.HTTPError as e:
		print(e.code)
		print(e.read())
	