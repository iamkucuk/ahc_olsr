# import sys

# sys.path.insert(0, '/root/code')

from adhoccomputing.Experimentation.Topology import Event
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import Event, AHCTimer, MessageDestinationIdentifiers, EventTypes, logger
from OLSR.message_types import HelloMessage, TCMessage, Message
from OLSR.enums import OLSREventTypes, Willingness
from OLSR.helpers import TopologyStateSaver
import networkx as nx

state_saver = TopologyStateSaver()

class OLSRComponent(GenericModel):
    def __init__(self, *args, **kwargs):
        """
        Represents an OLSR component(node).

        Args:
            *args: Variable length arguments for GenericModel arguments passthrough.
            **kwargs: Keyword arguments for GenericModel arguments passthrough.
        """
        super().__init__(*args, **kwargs)

        self.hello_timer = AHCTimer(2, self.send_hello)
        self.tc_timer = AHCTimer(5, self.send_tc)

        self.willingness = Willingness.WILL_DEFAULT

        self.neighbor_set = {}
        self.known_topology = {}

        self._selected_as_mpr = False
        self.routing_table = {}

        self.tc_counter = 1

    def set_parameters(self, hello_interval=None, tc_interval=None, willingness=None):
        """
        Sets the parameters for the OLSR component.

        Args:
            hello_interval (int, optional): The interval for sending Hello messages. Defaults to None.
            tc_interval (int, optional): The interval for sending TC messages. Defaults to None.
            willingness (Willingness, optional): The willingness of the node. Defaults to None.
        """
        if hello_interval:
            self.hello_timer.interval = hello_interval
        if tc_interval:
            self.tc_timer.interval = tc_interval
        if willingness:
            self.willingness = willingness

    def increase_tc_counter(self):
        self.tc_counter += 1

    @property
    def selected_as_mpr(self):
        return self._selected_as_mpr
    
    @selected_as_mpr.setter
    def selected_as_mpr(self, value):
        if value != self._selected_as_mpr:
            self._selected_as_mpr = value
            if value:
                state_saver.save_state(self.topology, self.tc_counter)
                

    def on_init(self, eventobj: Event):
        """
        This method is called when the object is initialized.

        Parameters:
        - eventobj: An instance of the Event class.

        Returns:
        - None
        """
        self.hello_timer.start()
        self.tc_timer.start()
    
    def on_message_from_bottom(self, eventobj: Event):
        """
        Handles incoming messages from the bottom layer.

        Args:
            eventobj (Event): The event object containing the message.

        Returns:
            None
        """        
        if eventobj.eventcontent.header.messagetype == OLSREventTypes.HELLO:
            self.on_hello(eventobj)
        elif eventobj.eventcontent.header.messagetype == OLSREventTypes.TC:
            self.on_tc(eventobj)
        else:
            self.on_else(eventobj)
        

    def on_message_from_top(self, eventobj: Event):
        logger.debug(f"{self.componentname}-{self.componentinstancenumber} RECEIVED FROM TOP {str(eventobj)}")

    def on_else(self, eventobj: Event):
        """
        Handles arbitrary events when the destination of a data packet is not the current node.

        Args:
            eventobj (Event): The event object containing the data packet.

        Returns:
            None
        """
        logger.debug(f"{self.componentname}-{self.componentinstancenumber} RECEIVED ELSE {str(eventobj)}")
        data_packet = eventobj.eventcontent
        destination = data_packet.header.messageto

        if destination == self.componentinstancenumber:
            # If the current node is the destination, consume it somehow
            self.send_up(eventobj)
        else:
            # Forward the packet to the next hop according to the routing table
            if destination in self.routing_table:
                next_hop = self.routing_table[destination]
                forwarded_packet = Message(
                    message_from=data_packet.header.messagefrom,
                    message_to=destination,
                    payload=data_packet.payload,
                    nexthop=next_hop,
                    sequencenumber=data_packet.header.sequencenumber+1
                )
                self.send_down(Event(self, EventTypes.MFRT, forwarded_packet))
            else:
                # If no route is found, drop the packet (or implement error handling as needed)
                logger.error(f"No route found for destination {destination}. Dropping packet.")

    def send_hello(self):
        """
        Sends a Hello message to the link layer broadcast address.
        """
        hello_message = HelloMessage(
            message_from=self.componentinstancenumber,
            message_to=MessageDestinationIdentifiers.LINKLAYERBROADCAST,
            payload={
                'neighbors': set(self.neighbor_set.keys()),
                'willingness': self.willingness,
            },
            nexthop=MessageDestinationIdentifiers.LINKLAYERBROADCAST
        )
        self.send_down(Event(self, EventTypes.MFRT, hello_message))

    def send_tc(self):
        """
        Sends a TC (Topology Control) message to the link layer broadcast address.
        """
        self.increase_tc_counter()
        tc_message = TCMessage(
            message_from=self.componentinstancenumber,
            payload={'mpr_selectors': self.select_mpr()},
            message_to=MessageDestinationIdentifiers.LINKLAYERBROADCAST,
            sequencenumber=self.tc_counter,
            nexthop=MessageDestinationIdentifiers.LINKLAYERBROADCAST
        )
        self.send_down(Event(self, EventTypes.MFRT, tc_message))

    def on_hello(self, eventobj: Event):
        """
        Handles the reception of a Hello message.

        Args:
            eventobj (Event): The event object containing the Hello message.

        Returns:
            None
        """
        # if event_content.messagefrom != self.componentinstancenumber:
        self.neighbor_set[eventobj.eventcontent.header.messagefrom] = {
            "neighbors": eventobj.eventcontent.payload['neighbors'],
            "willingness": eventobj.eventcontent.payload['willingness']
        } #eventobj.eventcontent.payload['neighbors']
        self.known_topology[eventobj.eventcontent.header.messagefrom] = {
            "nexthop": eventobj.eventcontent.header.messagefrom,
            "distance": 1
        }

        logger.debug(f"{self.componentname}-{self.componentinstancenumber} RECEIVED HELLO FROM {eventobj.eventcontent.header.messagefrom} - NEIGHBORS: {eventobj.eventcontent.payload['neighbors']} - EVENT: {str(eventobj)}")

    def on_tc(self, eventobj: Event):
        """
        Handle the TC event.

        Args:
            eventobj (Event): The event object containing the TC message.

        Returns:
            None
        """
        tc_message = eventobj.eventcontent
        mpr_selectors = tc_message.payload['mpr_selectors']
        if tc_message.header.messagefrom not in self.known_topology:
            self.known_topology[tc_message.header.messagefrom] = {}
        self.known_topology[tc_message.header.messagefrom].update({
            "mpr_selectors": mpr_selectors
        })
        logger.debug(f"{self.componentname}-{self.componentinstancenumber} RECEIVED TC FROM {tc_message.header.messagefrom} - MPR SELECTOR - EVENT: {str(eventobj)}")

        if self.componentinstancenumber in mpr_selectors:
            logger.info(f"{self.componentname}-{self.componentinstancenumber} SELECTED AS MPR")
            self.selected_as_mpr = True
            self.send_down(Event(self, EventTypes.MFRT, tc_message))
        else:
            self.selected_as_mpr = False

        self.calculate_routing_table()

    def select_mpr(self):
        """
        Selects the Multi-Point Relays (MPRs) based on the OLSR protocol.

        Returns:
            set: A set of selected MPRs.

        Algorithm:
            1. Create a dictionary to keep track of which one-hop neighbors cover which two-hop neighbors.
            2. While there are still two-hop neighbors that are not covered:
                a. Find the neighbors with the maximum number of unique uncovered two-hop neighbors.
                b. Select the candidate with the highest willingness.
                c. Update the set of covered two-hop neighbors.
                d. Remove covered two-hop neighbors from all sets in the coverage map.
            3. Return the set of selected MPRs.
        """
        covered_two_hop_neighbors = set()
        mpr_set = set()

        # Create a dictionary to keep track of which one-hop neighbors cover which two-hop neighbors
        coverage_map = {}
        for one_hop_neighbor, neighbor_data in self.neighbor_set.items():
            two_hop_set = set(neighbor_data['neighbors']) - {self.componentinstancenumber} - set(self.neighbor_set.keys())
            coverage_map[one_hop_neighbor] = {
                'two_hop_set': two_hop_set,
                'willingness': neighbor_data['willingness']
            }

        # While there are still two-hop neighbors that are not covered
        while any(data['two_hop_set'] for data in coverage_map.values()):
            # Find the neighbors with the maximum number of unique uncovered two-hop neighbors
            max_uncovered_count = max(len(data['two_hop_set'] - covered_two_hop_neighbors) for data in coverage_map.values())
            candidates = [neighbor for neighbor, data in coverage_map.items() if len(data['two_hop_set'] - covered_two_hop_neighbors) == max_uncovered_count]

            # Select the candidate with the highest willingness
            mpr_candidate = max(candidates, key=lambda x: coverage_map[x]['willingness'].value)
            mpr_set.add(mpr_candidate)

            # Update the set of covered two-hop neighbors
            covered_two_hop_neighbors.update(coverage_map[mpr_candidate]['two_hop_set'])

            # Remove covered two-hop neighbors from all sets in the coverage map
            for neighbor_data in coverage_map.values():
                neighbor_data['two_hop_set'].difference_update(covered_two_hop_neighbors)

        return mpr_set

    def calculate_routing_table(self):
        """
        Calculates the routing table based on the known topology.

        This method creates a graph from the known topology and calculates the shortest paths from the current node to all other nodes.
        It then updates the routing table with the next hop for each destination.

        Returns:
            None
        """
        # Create a new graph from the topology
        G = nx.Graph()

        # Add edges for each node in the topology
        for node, node_data in self.known_topology.items():
            if 'nexthop' in node_data:
                G.add_edge(self.componentinstancenumber, node, weight=node_data['distance'])

            if 'mpr_selectors' in node_data:
                for mpr_selector in node_data['mpr_selectors']:
                    G.add_edge(node, mpr_selector, weight=1)

        # Calculate the shortest paths from the current node to all other nodes
        shortest_paths = nx.single_source_dijkstra_path(G, self.componentinstancenumber)

        # Update the routing table with the next hop for each destination
        self.routing_table = {}
        for dest, path in shortest_paths.items():
            if dest != self.componentinstancenumber and len(path) > 1:
                self.routing_table[dest] = path[1]

# def main(number_of_nodes):
#     from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
#     import time
#     from adhoccomputing.Experimentation.Topology import Topology
#     import os
#     from helpers import plot_topology

#     # Remove plots folder if it exists
#     if os.path.exists("plots"):
#         import shutil
#         shutil.rmtree("plots")
    
#     topo = Topology()

#     G = nx.random_geometric_graph(number_of_nodes, 0.4)

#     topo.construct_from_graph(G, OLSRComponent, GenericChannel)
#     plot_topology(topo)

#     logger.warning("Up and ready.")
#     topo.start()

#     time.sleep(15)
    
#     topo.exit()
#     state_saver.produce_gif()
#     logger.info(f"Converged at step: {state_saver.converged_step}")


# if __name__ == '__main__':
#     from adhoccomputing.Generics import setAHCLogLevel, DEBUG, INFO

#     setAHCLogLevel(INFO)

#     main(50)
