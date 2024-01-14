from Chain.Event import MessageEvent
from Chain.Parameters import Parameters

import Chain.tools as tools

import numpy as np, glob, pandas as pd
from sys import getsizeof

import random

import json

class Network:
    '''
        Models the blockchain p2p network
            nodes: list of BP's
            locations: list of various locations node can be in
            latency_map: map of propgation latencies between locations
    '''
    nodes = None
    locations = None
    latency_map = None
    distance_map = None
    
    @staticmethod
    def size(msg):
        size = Parameters.network["base_msg_size"]

        for key in msg.payload:
            if key == "block":
                size += msg.payload[key].size
            else:
                size += float(getsizeof(msg.payload[key])/1000000)

        return size

    @staticmethod
    def send_message(creator, event):
        with open("metrics.txt", "a") as file:
            if Parameters.network["type"]=="gossip":
                Network.multicast(creator, event)
            elif Parameters.network["type"]=="broadcast":
                Network.broadcast(creator, event)
            elif Parameters.network["type"]=="smallworld":
                Network.smallworld_message(creator, event)
                 
            elif Parameters.network["type"]=="lattice":
                Network.lattice_message(creator, event)
                 
            else: 
                print("wrong network type", file=file)

    @staticmethod
    def multicast(node, event):
        for n in node.neighbours:
            msg = MessageEvent.from_Event(event, n)
            Network.gossip_message(node, n, msg)

    @staticmethod
    def gossip_message(sender, receiver, msg):
        # if the receiver has received this event (ignore) or the receiver created the message
        if receiver.queue.contains_event_message(msg) or msg.creator == receiver:
            return 0

        Network.message(sender, receiver, msg)
        
    @staticmethod
    def broadcast(node, event):
        for n in Network.nodes:
            if n != node:
                msg = MessageEvent.from_Event(event, n)
                Network.message(node, n, msg)

    @staticmethod
    def message(sender, receiver, msg, delay=True):
        delay = Network.calculate_message_propagation_delay(
            sender, receiver, Network.size(msg))

        msg.time += delay
        
        receiver.add_event(msg)
    @staticmethod
    def smallworld_message(node, event):
        # Get the immediate neighbours
        immediate_neighbours = node.neighbours

        # Get a list of all nodes in the network
        all_nodes = Network.nodes

        # Remove the immediate neighbours and the current node from the list of all nodes
        distant_nodes = [n for n in all_nodes if n not in immediate_neighbours and n != node]

        # Choose a few distant nodes at random
        # beta is the rewiring probability
        beta1=0.5
        approx_value = round(beta1 * len(all_nodes))
        num_distant_nodes = min(approx_value, len(distant_nodes))  # Change this number as needed
        chosen_distant_nodes = random.sample(distant_nodes, num_distant_nodes)

        # Combine the immediate neighbours and chosen distant nodes
        chosen_nodes = immediate_neighbours + chosen_distant_nodes

        # Send the message to the chosen nodes
        for n in chosen_nodes:
            msg = MessageEvent.from_Event(event, n)
            Network.message(node, n, msg)
            
    @staticmethod
    def lattice_message(node, event):
        # Get the immediate neighbours in the lattice
        immediate_neighbours = node.neighbours

        # Send the message to the immediate neighbours
        for n in immediate_neighbours:
            msg = MessageEvent.from_Event(event, n)
            Network.message(node, n, msg)
            
    @staticmethod
    def init_network(nodes, speeds=None):
        ''' 
            Initialises the Netowrk modules
                - Gets a refenrence to the node list
                - Calculates latency_map and locations
                - Assigns locations and bandwidth to nodes
                - Assigns neibhours to nodes (Gossip, Sync etc...)
        '''
        Network.nodes = nodes

        Network.parse_latencies()
        Network.parse_distances()
    
        Network.assign_location_to_nodes()

        Network.set_bandwidths()

        Network.assign_neighbours()

    @staticmethod
    def set_bandwidths(node=None):
        if node is None:
            for n in Network.nodes:
                Network.set_bandwidths(n)
        else:
            if Parameters.network["bandwidth"]["debug"]:
                node.bandwidth = 1
            else:
                node.bandwidth = random.normalvariate(Parameters.network["bandwidth"]["mean"], Parameters.network["bandwidth"]["dev"])
                print(node.bandwidth)
    # @staticmethod
    # def assign_neighbours(node=None):
    #     '''
    #         (default) node -> None
    #         Randomly assing neibhours to all nodes (based on the config)
    #         if node is provided assign to just that node
    #     '''
    #     if node is None:
    #         for n in Network.nodes:
    #             Network.assign_neighbours(n)
    #     else:
    #         node.neighbours = random.sample(
    #             [x for x in Network.nodes if x != node],
    #             Parameters.network["num_neighbours"])
    @staticmethod
    def assign_neighbours(node=None, num_neighbours=2, beta1=0.5):
        num_neighbours=Parameters.network["num_neighbours"]
        '''
            (default) node -> None
            Randomly assing neibhours to all nodes (based on the config)
            if node is provided assign to just that node
        '''
        if node is None:
            for n in Network.nodes:
                Network.assign_neighbours(n)       
        elif Parameters.network["type"]=="gossip":
            node.neighbours = random.sample(
                [x for x in Network.nodes if x != node],
                num_neighbours)
        elif Parameters.network["type"]=="broadcast":
                node.neighbours = [x for x in Network.nodes if x != node]
        elif Parameters.network["type"]=="smallworld":
            # Check if there are enough nodes to sample from
            if len(Network.nodes) > num_neighbours:
                # Assign a small number of random neighbors
                node.neighbours = random.sample(
                    [x for x in Network.nodes if x != node],
                    num_neighbours)
            else:
                raise ValueError("Not enough nodes to sample from")

            # # Add a few long-range connections
            # for _ in range(int(beta1 * num_neighbours)):
            #     # Check if there are nodes to choose from
            #     if Network.nodes:
            #         while True:
            #             potential_neighbour = random.choice(Network.nodes)
            #             if potential_neighbour != node and potential_neighbour not in node.neighbours:
            #                 node.neighbours.append(potential_neighbour)
            #                 break
            #     else:
            #         raise IndexError("No nodes to choose from")

        elif Parameters.network["type"]=="lattice":
                print("------------------")
                print("lattice")
                # Assign neighbors based on communication speed
                speeds = [(other, Network.calculate_message_propagation_delay(node, other, 1)) 
                        for other in Network.nodes if other != node]
                speeds.sort(key=lambda x: x[1], reverse=False)
                node.neighbours = [other for other, speed in speeds[:num_neighbours]]
        else:
            print("parameter is ",Parameters.network["type"]) 
            raise Exception("Wrong network type")

    @staticmethod
    def calculate_message_propagation_delay(sender, receiver, message_size):
        '''
            Calculates the message propagation delay as
            transmission delay + propagation delay + queueing delay + processing_delay
        '''
        # transmission delay
        delay = message_size / Network.get_bandwidth(sender, receiver)

        if Parameters.network["use_latency"] == "measured":
            delay += Network.latency_map[sender.location][receiver.location][0] / 1000
        elif Parameters.network["use_latency"] == "distance":
            dist = Network.distance_map[sender.location][receiver.location]
            dist = dist * 0.621371 # conversion to miles since formula is based on miles
            '''
                y = 0.022x + 4.862 is fitted to match the round trip latency between 2
                locations based on distance source: 
                Goonatilake, Rohitha, and Rafic A. Bachnak. "Modeling latency in a network distribution." Network and Communication Technologies 1.2 (2012): 1
                
                / 2 to get the single trip latency
                / 1000 to get seconds (formula fitted on ms)
            '''
            delay += ((0.022 * dist + 4.862) / 2) / 1000
        

        delay += Parameters.network["queueing_delay"] + Parameters.network["processing_delay"]

        return delay

    @staticmethod
    def assign_location_to_nodes(node=None, location=None):
        '''
            node->Node (default)
            Assings random locations to nodes by default
            if node is provided assing a random location to just this node
        '''
        if node is None:
            for n in Network.nodes:
                n.location = random.choice(Network.locations)
                tools.debug_logs(msg=f"{n}: {n.location}")

        else:
            if location is None:
                node.location = random.choice(Network.locations)
            else:
                node.location = location

    @staticmethod
    def get_bandwidth(sender, receiver):
        return min(sender.bandwidth, receiver.bandwidth)
    
    @staticmethod
    def parse_latencies():
        '''
            Initialised the Network.locations list the Network.latency map from the JSON dataset
        '''
        Network.locations = []
        Network.latency_map = {}

        with open("NetworkLatencies/latency_map.json","rb") as f:
            Network.latency_map = json.load(f)
        
        Network.locations = list(Network.latency_map.keys())

        for loc in Network.locations:
            Network.latency_map[loc][loc] = (
                Parameters.network["same_city_latency_ms"],
                Parameters.network["same_city_dev_ms"]
            )
    
    def parse_distances():
        Network.locations = []
        Network.distance_map = {}
    
        with open("NetworkLatencies/point_distances_km.json","rb") as f:
            Network.distance_map = json.load(f)
        
        # overwritting the locations is fine to gurantee that they exists 
        # (this is the case if we laoded latencied before and prevents an error if we dont want to use latencies)
        Network.locations = list(Network.distance_map.keys())

