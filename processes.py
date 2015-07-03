import logging
import sys

from utils import *

""" Source and Process and Monitor definition """
avg_wait = .0
drop_count = 0
drop_probability = .0
number_of_generated_processes = 0
avg_service_time = .0

def Source(env, res, data):
	""" Generates Processes according to configured generator """
	config = readConfig('./opt/sim.cfg', 'default')
	avg_interarrival = int(config['avg_interarrival_time'])
	service_time = int(config['service_time'])
	patience = config['avg_patience']
	global number_of_generated_processes
	number_of_generated_processes = 0
	global avg_wait
	avg_wait = .0
	global drop_count
	drop_count = 0
	global drop_probability
	drop_probability = .0
	global number_of_generated_processes
	number_of_generated_processes = 0
	global avg_service_time
	avg_service_time = .0
	logging.debug('configuring generators according to sim.cfg')
	generator_func = read_generators('./opt/generator.csv')
	interarrival_gen = generator_func[int(config['interarrival_gen'])]
	service_time_gen = generator_func[int(config['service_time_gen'])]
	patience_gen = generator_func[int(config['patience_gen'])]

	while(True):
		next_event = interarrival_gen(avg_interarrival)
		event_service_time = service_time_gen(service_time)
		if (patience.isdigit() and (float(patience) > .0)):
			event_patience = patience_gen(float(patience))
		elif (patience == 'max'):
			event_patience = float('inf')
		else:
			logging.debug('Using Fallback Value!')
			event_patience = 0

		yield env.timeout(next_event)
		p = Process(env, res, event_service_time, event_patience, data)
		number_of_generated_processes += 1
		logging.debug('%d: Process enters at t = %.2f for d = %.2f with patience %.2f' % (number_of_generated_processes, env.now, event_service_time, event_patience))
		env.process(p)

def Process(env, res, service_time, patience, data):
	entered_system = env.now
	logging.debug('Resource utilization: %s/%s, queue length: %s' % (res.count, res.capacity, len(res.queue)))

	with res.request() as req:
		results = yield req | env.timeout(patience)
		global avg_wait
		global drop_count
		global drop_probability
		global number_of_generated_processes
		global avg_service_time

		wait = env.now - entered_system
		logging.debug('Calculate avg_wait: (%.2f + %.2f) / 2 = %.2f' % (avg_wait, wait, (avg_wait+wait)/2 ))
		avg_wait = float((avg_wait + wait) / 2)

		if req not in results:
			drop_count += 1.0
			drop_probability = float(drop_count) / number_of_generated_processes
			logging.debug('Process dropped out after %.2f. (%2.2f)' % (patience, drop_probability))
		else:
			logging.debug('Process waited for %.2f, to get served for %.2f' % (wait, service_time))
			yield env.timeout(service_time)
			avg_service_time = float((avg_service_time + service_time) / 2)
			logging.debug('Process finished at %.2f.' % (env.now))
	logging.debug('Average Waiting Value: %10.2f' % (avg_wait))
	data[0] = avg_wait
	data[1] = drop_probability
	data[2] = avg_service_time
	logging.debug('Values in data at end of run %s' % data)

	# left_system = env.now

	# mittlere wartezeit
	# mittlere auslastung bedieneinheiten
	# mittlere warteschlangenzeit
	# mittglere verweildauer sytem
	# verlustwarhscheinlichkeit / blockierwahrscheinlichkeit
