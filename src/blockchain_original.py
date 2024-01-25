from datetime import datetime

from Chain.Manager import Manager

import random, numpy

import Chain.Consensus.BigFoot.BigFoot as BigFoot
import Chain.Consensus.PBFT.PBFT as PBFT
from Chain.Parameters import Parameters
import Chain.tools as tools
from Chain.Metrics import SimulationState, Metrics

############### SEEDS ############
seed = 5
random.seed(seed)
numpy.random.seed(seed)
############### SEEDS ############

def run():
    manager = Manager()
    tools.set_env_vars_from_config()
    Parameters.load_params_from_config()
    manager.set_up()

    t = datetime.now()
    manager.run()
    runtime = datetime.now() - t

    for n in manager.sim.nodes:
        print(n, '| Total_blocks:', n.blockchain_length(),
            '| pbft:',len([x for x in n.blockchain if x.consensus == PBFT]),
            '| bf:',len([x for x in n.blockchain if x.consensus == BigFoot]),
            )
    
    SimulationState.store_state(manager.sim)

    Metrics.measure_all(SimulationState.blockchain_state)
    Metrics.print_metrics()
    print(Metrics.metrics_result())

    print(f"\nSIMULATION EXECUTION TIME: {runtime}")

    
    

run()