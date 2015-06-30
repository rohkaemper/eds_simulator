import simpy
import random
import logging
import numpy as np
import sys

from utils import *
from processes import *

LOG = 'DEBUG'
avg_wait = .0
drop_probability = .0

def main():
	""" Read configuration file, set parameters and start simulation """
	# Set logging level:
	if(LOG == 'DEBUG'):
		logging.basicConfig(level=logging.DEBUG, format='%(levelname)s: %(message)s')
	elif (LOG == 'INFO'):
		logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
	else:
		logging.basicConfig(level=logging.WARN, format='%(levelname)s: %(message)s')

	logging.info('Start of Simulation')
	# read config file; try catch block... for missing file
	logging.info('reading config file...')
	config = readConfig('./opt/sim.cfg', 'default')
	avg_interarrival = int(config['avg_interarrival_time'])
	service_time = int(config['service_time'])

	logging.debug(config)
	# TODO: this needs to be implemented yet
	adv_config = readConfig('./opt/sim.cfg', 'advanced')
	logging.info(adv_config)

	# configure generators
	# generator_func = read_generators('generator.csv')
	# interarrival_gen = generator_func[int(config['interarrival'])]
	# service_time_gen = generator_func[int(config['service_time_gen'])]

	logging.info('setting parameters...')
	# set values according to sim.cfg
	simulation_duration = config['simulation_duration']
	# !!! you have to put an int into capacity, or else it will not work !!!
	number_of_queues = int(config['capacity'])

	if (config['seed'] == 'rand'):
		seed = random.randint(0, sys.maxint)
		logging.warning('Randomized initial seed used for measurements (seed = %d)!' % seed)
		random.seed(seed)
	else:
		random.seed(config['seed'])

	# initialize numpy array with zeros
	data = [.0, .0]
	logging.debug('Data initialized %s' % data)

	# initialize environment and resource
	env = simpy.Environment()
	res = simpy.Resource(env, capacity=number_of_queues)

	logging.info('starting simulation!')

	# create processes
	s = env.process(Source(env, res, data))
	logging.debug('%10.1f: start' % env.now)

	env.run(until=int(simulation_duration))
	logging.debug('%10.1f: end' % env.now)

	logging.info('Simulation ended with: \n\t avg. waiting time \t= %.2f \n\t drop_probability \t= %.2f' % (data[0], data[1]))
	logging.info('evaluating and displaying data')


if (__name__ == '__main__'):
	main()