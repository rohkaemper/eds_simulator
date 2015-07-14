import ConfigParser
import csv
import random
import matplotlib.pyplot as plt
import logging
import os
import numpy

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


def plotUsage(data, drop_log, tick, num_sims, num_runs, cap, drop_probability, TOFILE):
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
            plt.xticks(range(0, max_x, tick))
            plt.yticks(range(0, max_y))
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
            plt.step(a_x[x], a_y[x], label='run %d' % (x+1))
            plt.plot(dx[x], dy[x], 'v', label='run %d drop' % (x+1))

        if (num_runs == 1):
            fig.suptitle('Sim. %d [cap: %d]' % (i+1, cap[count]))
        else:
            fig.suptitle(
                'Sim. %d [cap: %d; run: %d]' % (i + 1, cap[count], j+1))
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
    fig = plt.figure()
    N = len(list_elements)
    x = numpy.sort(list_elements)
    y = numpy.linspace(0,1,N)

    logging.info(y)
    plt.step(x,y*100)
    plt.title('Simulation %d-%d with capacity of %d' % (sim_run+1, repetition+1, actual_capacity))
    plt.xlabel('average time in system')
    plt.ylim(0,100)
    if (max(x) > 20):
        tickrange = 5
    else:
        tickrange = 1
    plt.xticks(range(0,int(max(x)),tickrange))
    plt.yticks(range(0,100,10))
    plt.grid()
    if (TOFILE):
        plt.tight_layout()
        plt.savefig('./figs/cdf/time_in_sys/simulation%d-%d.png' % (sim_run+1, repetition+1), dpi=(150))
    else:
        plt.show()
    plt.close()



def CheckDir(dir):
    """ Checks if path exists, and creates it if necessary """
    if not os.path.exists(dir):
        os.makedirs(dir)
