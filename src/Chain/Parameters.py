import yaml, os

def read_yaml(path):
    with open(path, 'rb') as f:
        data = yaml.safe_load(f)
    return data

class Parameters:
    '''
        Contains all the parameters defining the simulator
    '''
    simulation = {}
    application = {}
    execution = {}
    data = {}
    consensus = {}
    network = {}

    BigFoot = {}
    PBFT = {}

    @staticmethod
    def export_state():
        return {
            "simulation": Parameters.simulation,
            "application": Parameters.application,
            "execution": Parameters.execution,
            "data": Parameters.data,
            "consensus": Parameters.consensus,
            "network": Parameters.network,

            "BigFoot": Parameters.BigFoot,
            "PBFT": Parameters.PBFT
        }
    
    @staticmethod
    def load_state(state):
        Parameters.simulation = state["simulation"]
        Parameters.application = state["application"]
        Parameters.execution = state["execution"]
        Parameters.data = state["data"]
        Parameters.consensus = state["consensus"]
        Parameters.network = state["network"]

        Parameters.BigFoot = state["BigFoot"]
        Parameters.PBFT = state["PBFT"]

    @staticmethod
    def load_params_from_config():
        params = read_yaml(f"Configs/{os.environ['config']}.yaml")

        Parameters.simulation = params["simulation"]
        Parameters.simulation["events"] = {} # cnt events of each type
        
        Parameters.behaiviour = params["behaviour"]

        Parameters.network = params["network"]

        Parameters.application = params["application"]
        Parameters.application["txIDS"] = 0 # incremental txion ids starting on...
        Parameters.execution = params["execution"]
        Parameters.calculate_fault_tolerance()

        Parameters.data = params["data"]

        Parameters.BigFoot = read_yaml(params['consensus']['BigFoot'])
        Parameters.PBFT = read_yaml(params['consensus']['PBFT'])


    @staticmethod
    def calculate_fault_tolerance():
        #print("test",Parameters.execution)
        alpha=Parameters.execution["alpha"]
        if alpha==1:
            Parameters.application["f"] = int((Parameters.application["Nn"] - 1) / 3)
            Parameters.application["required_messages"] = (2 * Parameters.application["f"]) + 1
        else:
            Parameters.application["f"] = int((Parameters.application["Nn"]*alpha - 1) / 3)
            Parameters.application["required_messages"] =(2 * Parameters.application["f"]) + 1
    # this is the number of messages required to reach consensus