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


def plotUsage(data, drop_log, tick, num_sims, num_runs, cap):
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
			max_y = cap[count]+2

			ax = plt.subplot(num_sims, num_runs, count+1)
			ax.axhline(cap[count], color='g', linestyle='--')
			ax.step(x, y, label='Resource usage over time')
			drop_x = drop_log[count]
			drop_y = len(drop_x) * [int(max(y))]
			ax.plot(drop_x, drop_y, 'rv')
			if (num_runs == 1):
				ax.set_title('Sim. %d [cap: %d]' % (i+1, cap[count]))
			else:
				ax.set_title('Sim. %d [cap: %d; run: %d]' % (i+1, cap[count], j+1))

			plt.xticks(range(0, max_x, tick))
			plt.yticks(range(0, max_y))
			plt.grid()

			del x,y

	logging.debug('plotUsage -> Drop Events at:\n%s' % drop_log)
	# Workaround for User Warning "tight_layout"
	plt.tight_layout()
	plt.show()