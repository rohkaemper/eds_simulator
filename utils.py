import ConfigParser
import csv
import random

def readConfig(file, section):
	""" Reads information from 'file' with 'section' """
	config = ConfigParser.ConfigParser()
	config.read(file)
	keyval = dict()

	items = config.items('%s' % section)
	for entry in items:
		keyval[entry[0]] = entry[1]
	return keyval

def read_generators(filename):
    generators = []
    with open(filename) as csvFile:
        input = csv.DictReader(csvFile, delimiter = ";")
        for row in input:
            generators.append(eval(row.get('function')))

    return generators