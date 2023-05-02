import yaml

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
    def load_params_from_config():
        params = read_yaml("Configs/new_base.yaml")

        Parameters.simulation = params["simulation"]
        Parameters.simulation["events"] = {} # cnt events of each type
        
        Parameters.behaiviour = params["behaviour"]

        Parameters.network = params["network"]

        Parameters.application = params["application"]
        Parameters.application["txIDS"] = 0 # incremental txion ids starting on...
        Parameters.calculate_fault_tolerance()

        Parameters.execution = params["execution"]

        Parameters.data = params["data"]

        Parameters.BigFoot = read_yaml(params['consensus']['BigFoot'])
        Parameters.PBFT = read_yaml(params['consensus']['PBFT'])


    @staticmethod
    def calculate_fault_tolerance():
        Parameters.application["f"] = int((Parameters.application["Nn"] - 1) / 3)
        Parameters.application["required_messages"] = (2 * Parameters.application["f"]) + 1