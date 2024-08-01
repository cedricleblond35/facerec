#!/usr/bin/env python
#
import psutil
# gives a single float value
import sys
import json
import pickle




valeur1 = psutil.cpu_percent(interval=1, percpu=True)
print("valeur1 : {}".format(valeur1))
	
print("------ nb de cpu------------------")
nb_cpu = psutil.cpu_count()
print("{}".format(nb_cpu))

i=0
while i != 1:
	# cpu_t_percent= psutil.cpu_times_percent(interval=1, percpu=False)
	# print("valeur1 : {}".format(cpu_t_percent.user))
	valeur1 = psutil.cpu_percent(interval=1, percpu=True)
	print("valeur1 : {}".format(valeur1))


# gives an object with many fields
valeur2 = psutil.virtual_memory()
# you can convert that object to a dictionary 
valeur3 = dict(psutil.virtual_memory()._asdict())



