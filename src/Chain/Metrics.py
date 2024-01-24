import pickle
import statistics as st
from Chain.Parameters import Parameters

import matplotlib.pyplot as plt
import numpy as np
class SimulationState:
    '''
        Stores the state of the simulation.
    '''
    blockchain_state = {}
    events = {"consensus":{}, "other": {}}

    @staticmethod
    def store_state(sim):
        '''
            store_state can be called given a simulator object.
            store_state serializes and stores the simulator state
        ''' 
        for n in sim.nodes:
            SimulationState.blockchain_state[n.id] = n.to_serializable()
    
    @staticmethod
    def load_state(sim):
        pass

    @staticmethod
    def store_event(event):
        if 'block' in event.payload.keys():
            block_id = event.payload['block'].id
            if block_id in SimulationState.events["consensus"].keys():
                SimulationState.events["consensus"][block_id].append(event.to_serializable())
            else:
                SimulationState.events["consensus"][block_id] = [event.to_serializable()] 
        else:
            type = event.payload['type']
            if type in SimulationState.events["other"].keys():
                SimulationState.events[type].append(event.to_serializable())
            else:
                SimulationState.events[type] = [event.to_serializable()]
            
class Metrics:
    latency = {}
    throughput = {}
    blocktime = {}

    decentralisation = {}

    
    @staticmethod
    def measure_all(state):
        Metrics.measure_latency(state)
        Metrics.measure_throughput(state)
        # Metrics.measure_interblock_time(state)
        # Metrics.measure_decentralisation_nodes(state)
        # return Metrics.latency, Metrics.throughput, Metrics.blocktime

    @staticmethod
    def print_metrics():
        averages = {n:{} for n in Metrics.latency.keys()}
        val = "{v:.3f}"

        #latency
        for key, value in Metrics.latency.items():
            averages[key]["Latency"] = val.format(v=value["AVG"])

        # throughput
        for key, value in Metrics.throughput.items():
            averages[key]["Throughput"] = val.format(v=value)

        # blockctime
        for key, value in Metrics.blocktime.items():
            averages[key]["Blocktime"] = val.format(v=value["AVG"])

        # decentralisation
        for key, value in Metrics.decentralisation.items():
            val = "{v:.6f}"
            averages[key]["Decentralisation"] = val.format(v=value)

        print("-"*30, "METRICS", "-"*30)

        for key, value in averages.items():
            print(f"Node: {key} -> {value}")

    @staticmethod
    def measure_latency(bc_state):
        for node_id, node_state in bc_state.items():
            Metrics.latency[node_id] = {"values": {}}
            for b in node_state["blockchain"]:
                Metrics.latency[node_id]["values"][b["id"]] = st.mean(
                    [b["time_added"] - t.timestamp for t in b["transactions"]]
                )
            
            Metrics.latency[node_id]["AVG"] = st.mean(
                [b_lat for _, b_lat in Metrics.latency[node_id]["values"].items()]
            )
    
    @staticmethod
    def measure_throughput(bc_state):
        """
            Measured as:  sum_processed_txions / simTime

            TODO: Measure in intervals (possibly missleading??)
        """
        for node_id, node_state in bc_state.items():
            sum_tx = sum([len(x["transactions"]) for x in node_state["blockchain"]])
            Metrics.throughput[node_id] = sum_tx/Parameters.simulation["simTime"]

    @staticmethod
    def measure_interblock_time(bc_state):
        for node_id, node_state in bc_state.items():
            # for each pair of blocks create the key valie pair "curr -> next": next.time_added - curre.time_added
            diffs = { f"{curr['id']} -> {next['id']}" : next["time_added"] - curr["time_added"] 
                     for curr, next in zip(node_state["blockchain"][:-1], node_state["blockchain"][1:]) }
            
            Metrics.blocktime[node_id] = {"values": diffs, "AVG": st.mean(diffs.values())}
    @staticmethod
    def plot_metrics(bc_state):
        """
        Plots the average latency and throughput for each node in the blockchain simulation, with error bars representing the variance.

        Latency and throughput are plotted in separate subplots.

        Parameters:
            bc_state: The blockchain state data used for calculating variances.
        """
        # Create a new figure with two subplots
        fig, axs = plt.subplots(1, 2, figsize=(15, 5))

        # Plot latency with variance
        latency_values = [v["AVG"] for v in Metrics.latency.values()]
        latency_variances = [st.variance(v["values"].values()) if len(v["values"].values()) > 1 else 0 for v in Metrics.latency.values()]
        axs[0].bar(Metrics.latency.keys(), latency_values, yerr=latency_variances, capsize=5)
        axs[0].set_title('Average Latency per Node')
        axs[0].set_xlabel('Node ID')
        axs[0].set_ylabel('Latency (s)')

        # Plot throughput with variance
        throughput_values = list(Metrics.throughput.values())
        throughput_variances = [st.variance([len(x["transactions"]) for x in node["blockchain"]]) if len(node["blockchain"]) > 1 else 0 for node in bc_state.values()]
        axs[1].bar(Metrics.throughput.keys(), throughput_values, yerr=throughput_variances, capsize=5)
        axs[1].set_title('Average Throughput per Node')
        axs[1].set_xlabel('Node ID')
        axs[1].set_ylabel('Throughput (transactions/s)')

        # Adjust layout and show the plot
        plt.tight_layout()
        plt.show()
#     @staticmethod
#     def plot_metrics():
#         """
#         Plots the average latency and throughput for each node in the blockchain simulation, with error bars representing the variance.

#         Latency and throughput are plotted in separate subplots.
#         """
#         # Create a new figure with two subplots
#         fig, axs = plt.subplots(1, 2, figsize=(15, 5))

#         # Plot latency with variance
#         latency_values = [v["AVG"] for v in Metrics.latency.values()]
#         latency_variances = [st.variance(v["values"].values()) if len(v["values"].values()) > 1 else 0 for v in Metrics.latency.values()]
#         axs[0].bar(Metrics.latency.keys(), latency_values, yerr=latency_variances, capsize=5)
#         axs[0].set_title('Average Latency per Node')
#         axs[0].set_xlabel('Node ID')
#         axs[0].set_ylabel('Latency (s)')

#         # Plot throughput with variance
#         throughput_values = list(Metrics.throughput.values())
#         throughput_variances = [st.variance([len(x["transactions"]) for x in node["blockchain"]]) if len(node["blockchain"]) > 1 else 0 for node in bc_state.values()]
#         axs[1].bar(Metrics.throughput.keys(), throughput_values, yerr=throughput_variances, capsize=5)
#         axs[1].set_title('Average Throughput per Node')
#         axs[1].set_xlabel('Node ID')
#         axs[1].set_ylabel('Throughput (transactions/s)')

#         # Adjust layout and show the plot
#         plt.tight_layout()
#         plt.show()

# # Example usage:
#         # Create a new figure
#         fig, axs = plt.subplots(1, 2, figsize=(15, 10))

#         # Plot latency
#         axs[0, 0].bar(Metrics.latency.keys(), [v["AVG"] for v in Metrics.latency.values()])
#         axs[0, 0].set_title('Latency')
#         axs[0, 0].set_xlabel('Node')
#         axs[0, 0].set_ylabel('Latency')

#         # Plot throughput
#         axs[0, 1].bar(Metrics.throughput.keys(), Metrics.throughput.values())
#         axs[0, 1].set_title('Throughput')
#         axs[0, 1].set_xlabel('Node')
#         axs[0, 1].set_ylabel('Throughput')

#         # Show the figure
#         plt.tight_layout()
#         plt.show()
        
    @staticmethod
    def metrics_result():
        """
        Calculates and returns the average metrics and their variances over all nodes in the blockchain simulation.

        Returns:
            A dictionary containing the average and variance of latency, throughput, blocktime, and decentralisation.
        """
        latency_averages = [v["AVG"] for v in Metrics.latency.values()]
        throughput_averages = list(Metrics.throughput.values())
        average_metrics = {
            "Average Latency": st.mean(latency_averages),
            "Latency Variance": st.variance(latency_averages) if len(latency_averages) > 1 else 0,
            "Average Throughput": st.mean(throughput_averages),
            "Throughput Variance": st.variance(throughput_averages) if len(throughput_averages) > 1 else 0,
        }

        return average_metrics

    @staticmethod
    def gini_coeficient(cumulative_dist):
        lorenz_curve = [(x+1)/len(cumulative_dist) for x in range(len(cumulative_dist))]
        x_axis = [x for x in range(len(lorenz_curve))]
        '''
            TODO: Validate that this is indeed correct
            NOTE: seems kind of correct
        '''

        # calculate the area of the lorenze curve
        lor_area = np.trapz(lorenz_curve, x_axis) 
        # calculate the area of the actual cumulatice distribution
        act_area = np.trapz(cumulative_dist, x_axis) 
        # calculate what percentage is the area between the lorenze cruve and the actual curve
        return 1 - act_area / lor_area
        

    @staticmethod
    def measure_decentralisation_nodes(bc_state):
        '''
            TODO: 
                Consider how nodes entering and exiting the consensus can be taken into account

            NOTE: 
                This method assumes all nodes are accounted for in the final system state 
                and no later added nodes produced blocks and left

                !IF NODES THAT HAVE PRODUCED BLOCKS ARE NOT IN THE GIVEN SYSTEM STATE THIS BREAKS!

                if an extra node joins later this skews the decentralisaion since
                the node did not have equal proposing chances as the other nodes 

                    -- dont know if this is considered when measuring decentralisation
                       but seems like it should not be since the node was not there so 
                       its not the algorithms faults that the system is "less decentralised"

                NOTE:
                    possible solution:
                        Note when nodes enter and left (might be (probably is) hard to know when a node leaves)
                        calculating decentralisaion seperatatly for each interval where nodes are "stable"
                        average the decentralisations out
        '''        
        nodes = [int(x) for x in bc_state.keys()]
        for node_id, node_state in bc_state.items():
            block_distribution = {x:0 for x in nodes}
            total_blocks = len(node_state["blockchain"])

            for b in node_state["blockchain"]:
                block_distribution[b["miner"]] += 1

            dist = sorted([(key, value) for key, value in block_distribution.items()], key=lambda x:x[1])
            dist = [(x[0], x[1]/total_blocks) for x in dist]        
            cumulative_dist = [sum([x[1] for x in dist[:i+1]]) for i in range(len(dist))]
                
            gini = Metrics.gini_coeficient(cumulative_dist)

            Metrics.decentralisation[node_id] = gini