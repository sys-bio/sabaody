import arrow
from roadrunner import RoadRunner
r = RoadRunner('../../../../../sbml/b2.xml')

class StalledSimulation(RuntimeError):
    pass

# r.integrator.stiff = False
# r.integrator.maximum_time_step = 1e-3
# r.integrator.minimum_time_step = 1e-9
r.integrator = 'rk4'
print(r.integrator)

time_start = arrow.utcnow()
from interruptingcow import timeout
try:
    with timeout(1, StalledSimulation):
        r.simulate(0,1000,10000)
except (StalledSimulation):
    print('')
    print('timed out')
time_end = arrow.utcnow()
print('Total time: {}'.format(time_end-time_start))
