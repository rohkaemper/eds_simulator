import simpy
import random
import logging
import numpy as np
import sys

from utils import *
from processes import *

LOG = 'INFO'
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

    logging.info('setting parameters...')
    # set values according to sim.cfg
    simulation_duration = config['simulation_duration']
    num_runs = int(adv_config['number_of_repetitions_per_simulation'])+1
    num_sims = int(adv_config['number_of_simulations'])+1
    alter_capacity_by = int(adv_config['alter_capacity_by'])
    seed = []
    if (config['seed'] == 'rand'):

        for i in xrange(0,num_runs):
            seed.append(random.randint(0, sys.maxint))
        logging.warning('Randomized initial seed used for measurements (seed = %s)!' % seed)

    else:
        seed.append(int(config['seed']))
        logging.info('Single Seed configured -> enforcing single simulation run with seed %d.' % seed[0])
        # offset of 1
        num_runs = 1

    # initialize numpy array with zeros
    data = [.0, .0]
    avg_over_runs = [.0, .0]
    # !!! you have to put an int into capacity, or it will not work !!!
    number_of_queues = int(config['capacity'])
    simlog = []
    runlog = []

    for sim_run in xrange(0,num_sims-1):
        logging.info('--- Simulation %2d ---' % (sim_run+1))
        actual_capacity = number_of_queues + (sim_run*alter_capacity_by)

        for repetition in xrange(0, num_runs-1):
            logging.debug('Setting seed to: %d' %(seed[repetition]))
            random.seed(int(seed[repetition]))
            runlog.append('%.2d-%.2d' % (sim_run+1, repetition+1))
            # initialize environment and resource
            env = simpy.Environment()
            res = simpy.Resource(env, capacity=actual_capacity)
            # create processes
            s = env.process(Source(env, res, data))
            logging.debug('%10.1f: start' % env.now)

            env.run(until=int(simulation_duration))
            logging.debug('%10.1f: end' % env.now)
            logging.info('Queue capacity:\t %d' % (res._capacity))
            logging.info('Simulation (%d) ended with: \n\t avg. waiting time \t= %.2ftu \n\t drop_probability \t= %.2f%%' % (repetition+1, data[0], 100*data[1]))
            # logging.info('evaluating and displaying data')
            avg_over_runs[0] = (avg_over_runs[0] + data[0]) / 2
            avg_over_runs[1] = (avg_over_runs[1] + data[1]) / 2
            # logs data of current run
            runlog.append(data)
            data = [.0, .0]

        logging.debug('Appending current evaluation to list -> %s' % (avg_over_runs))
        simlog.append(avg_over_runs)
        avg_over_runs = [.0, .0]


    logging.info('Simulation Configuration:\n\t arrival function \t\t= %s, param = %stu \n\t service time function \t= %s, param = %stu \n\t patience function \t\t= %s, param = %stu' % (
        config['interarrival_gen'], config['avg_interarrival_time'],
        config['service_time_gen'], config['service_time'],
        config['patience_gen'], config['avg_patience'])
    )
    # TODO: Muss angepasst werden an simrun -> Auswertung von "simlog"
    # logging.info('Final result after %d runs: \n\t avg. waiting time \t= %.2ftu \n\t drop_probability \t= %.2f%%' % (num_runs-1, avg_over_runs[0], 100*avg_over_runs[1]))
    logging.info(runlog)
    logging.info(simlog)

if (__name__ == '__main__'):
    main()
