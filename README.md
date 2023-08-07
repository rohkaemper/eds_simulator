# eds_simulator
Configurable Event Discrete Simulator for (GI/GI/n) Queuing Systems

Configuration of Simulation in """sim.cfg""".

section [default]:
  -> select initial seed:
    - recommended value: rand

  -> select initial capacity of queue

  -> select simulation duration

  -> select values and generator for:
    - interarrival rate
    - service time
    - patience of process
    Note: Drop queue if patience = 0, never drop if patience = max

section [advanced]:
  -> number of simulation (with varied parameters like capacity)
  -> number of repetitions (with same parameters, but different seed)

  -> alter parameter:
    - capacity by (e.g. 1, per simulation)
    - ... more to come!

This project is not maintained any more.
Regards
