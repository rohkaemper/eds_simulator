""" Simulation object """
import utils
import logging
import pprint
import decimal


class sim_queue(object):

    def __init__(self, env, res, config, seed, capacity):
        self.env = env
        self.res = res
        self.seed_conf = int(seed)
        self.capacity = int(config['capacity'])
        self.interarrival_rate = int(config['avg_interarrival_time'])
        self.service_duration = int(config['service_time'])
        self.avg_patience = config['avg_patience']
        self.generators = utils.read_generators('./opt/generator.csv')
        self.interarrival_generator = self.generators[
            int(config['interarrival_gen'])]
        self.service_time_generator = self.generators[
            int(config['service_time_gen'])]
        self.patience_generator = self.generators[int(config['patience_gen'])]
        self.generated_processes = 0
        self.log = []
        logging.debug('Source object initialized')

        # This generates a process of instantiated object
        env.process(self.run())

    def run(self):
        """ The source is responsible to generate processeses as long as the simulation is active """

        while(True):
            # generate time for next process and it's service time
            next_event = self.interarrival_generator(self.interarrival_rate)
            process_service_time = self.service_time_generator(
                self.service_duration)
            process_patience = .0
            if (self.avg_patience.isdigit() and (float(self.avg_patience) > .0)):
                process_patience = self.patience_generator(float(self.avg_patience))
            elif (self.avg_patience == 'max'):
                process_patience = float('inf')
            else:
                process_patience = 0
            assert process_patience >= 0, 'Value must be positive!'
            process_patience = max(process_patience, 0)
            yield self.env.timeout(next_event)
            # generate new process
            config = self.env, self.res, process_service_time, process_patience
            NewProcess = Process(config, self.log)
            self.env.process(NewProcess.run())


class Process(object):

    def __init__(self, config, log):
        env, res, service_time, process_patience = config
        self.env = env
        self.res = res
        self.entered_system = self.env.now
        self.wait = .0
        self.service_time = service_time
        self.process_patience = process_patience
        self.dropped_out = False
        self.time_in_system = .0

        self.log = log
        logging.debug('Process object generated.')

    def run(self):
        self.res_usage_in = int(self.res.count)
        with self.res.request() as req:
            result = yield req | self.env.timeout(self.process_patience)

            self.wait = self.env.now - self.entered_system
            if req not in result:
                self.drop_out()
            else:
                yield self.env.timeout(self.service_time)
                self.time_in_system = self.env.now - self.entered_system
                logging.debug(
                    'Process has been served [%.2f->%.2f].' % (self.entered_system, self.env.now))

        self.res_usage_out = int(self.res.count)
        self.log.append([self.entered_system, self.wait, self.service_time,
                         self.time_in_system, self.dropped_out, self.res_usage_in, self.res_usage_out])

    def drop_out(self):
        self.time_in_system = (self.env.now - self.entered_system)
        self.dropped_out = True
        logging.debug('Process dropped out at %.2f.')
