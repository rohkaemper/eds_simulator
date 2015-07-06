import ConfigParser
import csv
import random
import matplotlib.pyplot as plt
import logging

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


def plotUsage(data, drop_log, tick, num_sims, num_runs):
	fig, axes = plt.subplots(num_sims, num_runs, sharex=True, sharey=True)
	count = -1
	for i in range(0,num_sims):
		for j in range(0,num_runs):
			count += 1
			x = list()
			y = list()
			for item in data[count]:
				try:
					x.append(float(item[0]))
					y.append(float(item[1]))
				except:
					x.append(.0)
					y.append(.0)

			max_x = int(max(x))
			max_y = int(max(y)) + 2

			ax = plt.subplot(num_sims, num_runs, count+1)
			ax.step(x, y, label='Resource usage over time')
			drop_x = drop_log[count]
			drop_y = len(drop_x) * [int(max(y))]
			ax.plot(drop_x, drop_y, 'rv')

			ax.set_title('Simulation %d (%d)' % (i+1, j+1))

			plt.xticks(range(0, max_x, tick))
			plt.yticks(range(0, max_y))
			plt.grid()

			del x,y

	logging.debug('plotUsage -> Drop Events at:\n%s' % drop_log)
	# Workaround for User Warning "tight_layout"
	plt.tight_layout()
	plt.show()