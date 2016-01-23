import simpy
import simpy.rt
import random
import logging
import csv
import sys
# import os
import time, datetime

from utils import *
from simclass import Sim_source

LOG = 'INFO'
LOG_TO_FILE = False
PLOT_CDF_TIME_IN_SYS = True
PLOT_USAGE = True
RT_DEMO = False             # Variable to demonstrate Realtime Simulation


def main():
    """ Read configuration file, set parameters and start simulation """
    # Set logging level:
    if(LOG == 'DEBUG'):
        logging.basicConfig(
            level=logging.DEBUG, format='%(levelname)s: %(message)s')
    elif (LOG == 'INFO'):
        logging.basicConfig(
            level=logging.INFO, format='%(levelname)s: %(message)s')
    else:
        logging.basicConfig(
            level=logging.WARN, format='%(levelname)s: %(message)s')

    logging.info('Start of Simulation')
    logging.debug('Using python version: %s' % (sys.version))
    CheckDir('./figs/cdf/time_in_sys')
    CheckDir('./figs/usage')
    # read config file; try catch block... for missing file
    logging.debug('reading config file...')
    config = readConfig('./opt/sim.cfg', 'default')
    logging.info('Simulation Configuration:\n\t arrival function \t\t= %s, param = %stu \n\t service time function \t= %s, param = %stu \n\t patience function \t\t= %s, param = %stu \n\t simulated timeunits = %stu' % (
        config['interarrival_gen'], config['avg_interarrival_time'],
        config['service_time_gen'], config['service_time'],
        config['patience_gen'], config['avg_patience'], config['simulation_duration'])
    )
    adv_config = readConfig('./opt/sim.cfg', 'advanced')

    logging.info('setting parameters...')
    # set values according to sim.cfg
    simulation_duration = int(config['simulation_duration'])
    num_runs = int(adv_config['number_of_repetitions_per_simulation'])
    num_sims = int(adv_config['number_of_simulations'])
    alter_capacity_by = int(adv_config['alter_capacity_by'])
    seeds = ConfigureSeeds(config, num_runs)

    # !!! you have to put an int into capacity, or it will not work !!!
    number_of_queues = int(config['capacity'])

    logging.info('\n\tNumber of Simulations: %d\n\tNumber of runs: %d\n\tin sum %dtu are going to be processed.' %
                 (num_sims, num_runs, num_runs * num_sims * int(config['simulation_duration'])))

    cap = []
    all_data = []
    data_log = []
    drop_log = []
    time_in_sys_log = []
    progress = 0
    endVal = num_sims * num_runs
    # START of SIMULATION
    # progressbar(0, endVal, 30)
    started_at = time.time()
    for sim_run in range(0, num_sims):
        logging.debug('--- Simulation %2d ---' % (sim_run + 1))
        actual_capacity = number_of_queues + (sim_run * alter_capacity_by)
        for repetition in range(0, len(seeds)):
            cap.append(actual_capacity)
            logging.debug('Setting seed to: %d' % (seeds[repetition]))
            random.seed(int(seeds[repetition]))

            # initialize environment and resource
            if (RT_DEMO):
                env = simpy.rt.RealtimeEnvironment(factor=1.0)
            else:
                env = simpy.Environment()
            res = simpy.Resource(env, capacity=actual_capacity)
            # creating queue object
            queue = Sim_source(env, res, config, adv_config, sim_run)
            # starting simulation for ''' configured duration '''
            env.run(until=simulation_duration)

            # By default create sorted logfiles, additionally log to console.
            # queue.log.sort()
            logging.debug('Measured:\n%s' % (queue.log))

            all_data.append(queue.log)
            data_log.append(queue.plot_log)
            drop_log.append(queue.drop_log)
            time_in_sys_log.append(queue.time_in_system_log)
            if (PLOT_CDF_TIME_IN_SYS):
                plotCDF(queue.time_in_system_log, sim_run,
                        repetition, actual_capacity, True)

            if (LOG_TO_FILE):
                LogToCSV('./logs/', 'simlog%.2d-%.2d.csv' %
                         (sim_run + 1, repetition + 1), queue.log)

            # logs data of current run
            # delete old queue object
            del queue, env, res
            progress += 1
            progressbar(progress, endVal, 30)
            #
        #
    # END of SIMULATION
    ended_at = time.time()
    print('\nSimulation took %.3fs.\n' % (ended_at-started_at))
    drop_prob = calc_drop_probability(num_sims, num_runs, all_data)
    logging.debug('Drop probabilities:\n%s' % (drop_prob))
    boxplot_time_in_system_data(num_sims, num_runs, time_in_sys_log)
    errorbarplot_time_in_system_data(num_sims, num_runs, time_in_sys_log, 0.95)

    # All simulations are finished... calculate and display data!
    if (PLOT_USAGE):
        plotUsage(data_log, drop_log, num_sims, num_runs, cap, drop_prob, True)
    print('Run ended after %.3fs.\n' % (time.time()-started_at))


def calc_drop_probability(sim_count, run_count, logs):
    logging.debug('Found %dx%d = %d entries' %
                  (sim_count, run_count, len(logs)))
    generated_processes = 0
    dropped_processes = 0
    drop_prob = []
    for item in logs:
        for element in item:
            # Here we evaluate if a drop happened, else the values will be
            generated_processes = element[0]
            if (element[5]):
                dropped_processes += 1
        drop_prob.append(
            float((float(dropped_processes) / float(generated_processes)) * 100))
        logging.debug('Drop Rate:%s/%s %.2f%%' % (dropped_processes, generated_processes, float((float(dropped_processes) / float(generated_processes)) * 100)))
        generated_processes = 0
        dropped_processes = 0
    return drop_prob

if (__name__ == '__main__'):
    main()
