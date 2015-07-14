import simpy
import random
import logging
import csv
import sys
import os
import datetime

from utils import readConfig, plotUsage, CheckDir, plotCDF
from simclass import sim_queue

LOG = 'INFO'
LOG_TO_CONSOLE = True
LOG_TO_FILE = False
PLOT_CDF_TIME_IN_SYS = True
PLOT_USAGE = True

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
    CheckDir('./figs/cdf/time_in_sys')
    CheckDir('./figs/usage')
    # read config file; try catch block... for missing file
    logging.debug('reading config file...')
    config = readConfig('./opt/sim.cfg', 'default')
    logging.info('Simulation Configuration:\n\t arrival function \t\t= %s, param = %stu \n\t service time function \t= %s, param = %stu \n\t patience function \t\t= %s, param = %stu' % (
        config['interarrival_gen'], config['avg_interarrival_time'],
        config['service_time_gen'], config['service_time'],
        config['patience_gen'], config['avg_patience'])
    )
    adv_config = readConfig('./opt/sim.cfg', 'advanced')

    logging.info('setting parameters...')
    # set values according to sim.cfg
    simulation_duration = int(config['simulation_duration'])
    num_runs = int(adv_config['number_of_repetitions_per_simulation'])
    num_sims = int(adv_config['number_of_simulations'])
    alter_capacity_by = int(adv_config['alter_capacity_by'])
    seed = ConfigureSeeds(config, num_runs)

    # !!! you have to put an int into capacity, or it will not work !!!
    number_of_queues = int(config['capacity'])

    logging.info('\n\tNumber of Simulations: %d\n\tNumber of runs: %d' %
                 (num_sims, num_runs))

    cap = []
    all_data = []
    data_log = []
    drop_log = []
    time_in_sys_log = []
    # START of SIMULATION
    for sim_run in range(0, num_sims):
        logging.info('--- Simulation %2d ---' % (sim_run + 1))
        actual_capacity = number_of_queues + (sim_run * alter_capacity_by)

        for repetition in range(0, len(seed)):
            cap.append(actual_capacity)
            logging.debug('Setting seed to: %d' % (seed[repetition]))
            random.seed(int(seed[repetition]))

            # initialize environment and resource
            env = simpy.Environment()
            res = simpy.Resource(env, capacity=actual_capacity)
            # creating queue object
            queue = sim_queue(env, res, config, 42, 1)
            # starting simulation for ''' configured duration '''
            env.run(until=simulation_duration)

            # By default create sorted logfiles, additionally log to console.
            # queue.log.sort()
            if (LOG_TO_CONSOLE):
                logging.debug('Measured:\n%s' % (queue.log))

            all_data.append(queue.log)
            data_log.append(queue.plot_log)
            drop_log.append(queue.drop_log)
            time_in_sys_log.append(queue.time_in_system_log)
            if (PLOT_CDF_TIME_IN_SYS):
                plotCDF(queue.time_in_system_log, sim_run, repetition, actual_capacity, True)

            if (LOG_TO_FILE):
                LogToCSV('./logs/', 'simlog%.2d-%.2d.csv' %
                         (sim_run + 1, repetition + 1), queue.log)

            # logs data of current run
            # delete old queue object
            del queue
            #
        #
    # END of SIMULATION
    logging.debug('Gathered data:\n%s' % (data_log))
    drop_prob = Evaluate_Simulation(num_sims, num_runs, all_data)
    logging.info(drop_prob)
    # All simulations are finished... calculate and display data!
    if (PLOT_USAGE):
        plotUsage(data_log, drop_log, max(10, simulation_duration/10), num_sims, num_runs, cap, drop_prob, True)

def ConfigureSeeds(config, runs):
    seed = []

    if (config['seed'] == 'rand'):
        for i in xrange(0, runs):
            seed.append(random.randint(0, sys.maxint))
        logging.info(
            'Randomized initial seed used for measurements (seeds = %s)!' % seed)
    else:
        seed.append(int(config['seed']))
        logging.info(
            'Single Seed configured -> enforcing single simulation run with seed %d.' % seed[0])
        # offset of 1

    return seed


def LogToCSV(dir, file, log):
    now = str(datetime.datetime.now().strftime('%Y%m%d_%H-%M'))
    dir += now
    if not os.path.exists(dir):
        os.makedirs(dir)

    with open(os.path.join(dir, file), 'wb') as csvout:
        writer = csv.writer(csvout)
        writer.writerows([['t_in', 'waited_for', 'got_served_for',
                           'time_in_sys', 'got_dropped', 'in_res_usage', 'out_res_usage']])
        writer.writerows(log)
        csvout.close()


def Evaluate_Simulation(sim_count, run_count, logs):
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
        drop_prob.append(float((float(dropped_processes)/float(generated_processes)) * 100))
        logging.debug('Drop Rate:%s/%s %.2f%%' % (dropped_processes, generated_processes, float((float(dropped_processes)/float(generated_processes)) * 100)))
        generated_processes = 0
        dropped_processes = 0
    return drop_prob

if (__name__ == '__main__'):
    main()
