import ConfigParser
import csv
import datetime
import matplotlib.pyplot as plt
import logging
import os
import numpy
import random
import sys
import scipy
from scipy.stats import lognorm, bayes_mvs


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
        input = csv.DictReader(csvFile, delimiter=";")
        for row in input:
            generators.append(eval(row.get('function')))

    return generators


def plotUsage(data, drop_log, num_sims, num_runs, cap, drop_probability, TOFILE):
    # fig, axes = plt.subplots(num_sims, num_runs, sharex=True, sharey=True, figsize=(num_sims*10, num_runs*2))
    count = -1
    for i in range(0, num_sims):
        a_x = []
        a_y = []
        dx = []
        dy = []
        for j in range(0, num_runs):
            fig = plt.figure(dpi=100)
            count += 1
            x_list = list()
            y_list = list()
            for item in data[count]:
                try:
                    x = float(item[0])
                    y1, y2 = float(item[1]), float(last[1])
                    x_list.append(x)
                    y_list.append(max(y1, y2))
                except:
                    x_list.append(.0)
                    y_list.append(.0)
                last = item

            a_x.append(x_list)
            a_y.append(y_list)
            max_x = int(max(x_list))
            max_y = int(cap[count] + 2)
            if (max_x <= 200):
                tick = 10
            elif (200 < max_x <= 1500):
                tick = 50
            else:
                tick = 100
            # ax = plt.subplot(num_sims, num_runs, count + 1)
            # ax.axhline(cap[count], color='g', linestyle='--')
            # ax.step(x_list, y_list, label='Resource usage over time')
            plt.axhline(
                cap[count], color='g', linestyle='--')
            plt.step(x_list, y_list, label='processes in queue')
            drop_x = drop_log[count]
            drop_y = len(drop_x) * [int(max(y_list))]
            dx.append(drop_x)
            dy.append(drop_y)
            plt.plot(drop_x, drop_y, 'rv', label='process dropped')
            if (num_runs == 1):
                fig.suptitle(
                    'Sim. %d [cap: %d] -> %.2f%% loss' % (i + 1, cap[count], drop_probability[count]))
            else:
                fig.suptitle(
                    'Sim. %d [cap: %d; run: %d] -> %.2f%% loss' % (i + 1, cap[count], j + 1, drop_probability[count]))
            # Check if output folder exists
            plt.xticks(range(0, min(max_x, 500), tick))
            plt.yticks(range(0, max_y))
            plt.xlim(xmax=min(max_x, 500))
            plt.xlabel('time [tu]')
            plt.ylabel('queue capacity')
            plt.legend(fontsize='small', fancybox=True, shadow=True)
            plt.grid()
            # limit to 2 files/windows output...
            if (j < 2):
                if (TOFILE):
                    plt.tight_layout()
                    plt.savefig('./figs/usage/simulation%d-%d.png' %
                                (i + 1, j + 1), dpi=(100))
                else:
                    plt.show()

            plt.close()
            del x_list, y_list
        # plot x in one image
        fig = plt.figure(dpi=100)
        plt.axhline(
            cap[count], color='g', linestyle='--')
        for x in xrange(0, len(a_x)):
            plt.step(a_x[x], a_y[x], label='run %d' % (x + 1))
            plt.plot(dx[x], dy[x], 'v', label='run %d drop' % (x + 1))

        if (num_runs == 1):
            fig.suptitle('Sim. %d [cap: %d]' % (i + 1, cap[count]))
        else:
            fig.suptitle(
                'Sim. %d [cap: %d; run: %d]' % (i + 1, cap[count], j + 1))
        # Check if output folder exists
        plt.xticks(range(0, max_x, tick))
        plt.yticks(range(0, max_y))
        plt.xlabel('time [tu]')
        plt.ylabel('queue capacity')
        plt.legend(fontsize='x-small', loc='upper center', bbox_to_anchor=(0.5, -0.05),
                   fancybox=True, shadow=True, ncol=num_sims)
        plt.grid()
        # limit to 4 files/windows output...
        if (TOFILE):
            plt.tight_layout()
            plt.savefig('./figs/usage/simulation%d.png' % (i + 1), dpi=(100))
        else:
            plt.show()
        del a_x, a_y, dx, dy
        plt.close()


def plotCDF(list_elements, sim_run, repetition, actual_capacity, TOFILE):
    N = len(list_elements)
    x = numpy.sort(list_elements)
    y = numpy.linspace(0, 1, N)

    plt.step(x, y * 100)
    plt.title('Simulation %d-%d with capacity of %d' %
              (sim_run + 1, repetition + 1, actual_capacity))
    plt.xlabel('average time in system [tu]')
    # displaying tick range. Adjustments needed for long run simulations!
    plt.ylim(0, 100)
    if (max(x) >= 500):
        tickrange = 50
    elif (500 > max(x) >= 100):
        tickrange = 25
    elif (100 > max(x) >= 20):
        tickrange = 5
    else:
        tickrange = 1

    plt.xticks(range(0, int(max(x))+2, tickrange))
    plt.yticks(range(0, 100, 10))
    plt.ylim(ymax=101)
    plt.grid()
    if (TOFILE):
        plt.tight_layout()
        plt.savefig('./figs/cdf/time_in_sys/simulation%d-%d.png' %
                    (sim_run + 1, repetition + 1), dpi=(150))
    else:
        plt.show()
    plt.close()


def reformat_input(input, number_of_lists, number_of_runs):
    # Reformat input (list into data for each simulation)
    mydata = list()
    # create list of lists
    for x in range(number_of_lists):
        mydata.append([])
    i = 0
    j = 0
    eval_time_sys = numpy.asarray(input)
    # flatten data of each simulation with same parameters into single list
    if number_of_runs > 1:
        for item in eval_time_sys:
            mydata[j] += item
            if (i < number_of_runs):
                i += 1
            else:
                i = 1
                j += 1
    else:
        return eval_time_sys

    # return reformatted list
    return mydata


def boxplot_time_in_system_data(num_sims, num_runs, data):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Decoration of plot ;-)
    plt.title('Time in System - Varyiing capacity')
    plt.xlabel('Capacity')
    plt.ylabel('Measured values')
    plt.grid()

    mydata = reformat_input(data, num_sims, num_runs)

    # boxplot it
    bp = ax.boxplot(mydata)

    # plt.show()
    plt.savefig('./figs/cdf/time_in_sys/boxplot.png')
    plt.close()


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * numpy.array(data)
    n = len(a)
    m, se = numpy.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t._ppf((1 + confidence) / 2., n - 1)
    return m, h


def errorbarplot_time_in_system_data(num_sims, num_runs, data, conf):
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Decoration of plot ;-)
    plt.title('Time in System - Varyiing capacity with %d%% confidence' % (int(conf*100)))
    plt.xlabel('Capacity')
    plt.ylabel('Measured values')
    plt.grid()

    mydata = reformat_input(data, num_sims, num_runs)

    xlist = list()
    ylist  = list()
    yerrlist = list()
    x=0
    for errordata in mydata:
        x+=1
        xlist.append(x)
        y, yerr = mean_confidence_interval(errordata, conf)
        ylist.append(y)
        yerrlist.append(yerr)

    # plot it with errorbars
    bp = ax.errorbar(xlist, ylist, yerr=yerrlist, fmt='o')
    plt.xticks(range(0,num_sims+2))
    # plt.ylim(ymin=0)
    # eventuell noch die mittelwerte interpolieren
    # plt.show()
    plt.savefig('./figs/cdf/time_in_sys/errorbars.png')
    plt.close()


def ConfigureSeeds(config, runs):
    seeds = []

    if (config['seed'] == 'rand'):
        for i in xrange(0, runs):
            seeds.append(random.randint(0, sys.maxint))
        logging.debug(
            'Randomized initial seed used for measurements (seeds = %s)!' % seeds)
    else:
        seeds.append(int(config['seed']))
        # logging.WARN('Single Seed configured -> enforcing single simulation run with seed %s.' % (seeds[0]))

    return seeds


def CheckDir(dir):
    """ Checks if path exists, and creates it if necessary """
    if not os.path.exists(dir):
        os.makedirs(dir)


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


def progressbar(i, end_val, bar_length=20):
    percent = float(i) / end_val
    hashes = '#' * int(round(percent * bar_length))
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rSimulation progress: [{0}] {1}%".format(
        hashes + spaces, int(round(percent * 100))))
    sys.stdout.flush()
