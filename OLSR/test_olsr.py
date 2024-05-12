import sys

sys.path.insert(0, '/root/code')

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Generics import Event
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from OLSR.OLSR import OLSRComponent, state_saver
from helpers import plot_topology

import networkx as nx

number_of_hops = []

class ApplicationLayer(GenericModel):
    def on_message_from_bottom(self, eventobj: Event):
        logger.applog(f"{self.componentname}-{self.componentinstancenumber} RECEIVED {str(eventobj)}")
        number_of_hops.append(eventobj.eventcontent.header.sequencenumber)

class AdHocNode(GenericModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.aapl = ApplicationLayer("ApplicationLayer", self.componentinstancenumber, topology=self.topology)
        self.olsr = OLSRComponent("OLSR", self.componentinstancenumber, topology=self.topology)
        self.link_layer  = GenericLinkLayer("GenericLinkLayer", self.componentinstancenumber, topology=self.topology)

        self.components.extend([self.aapl, self.olsr, self.link_layer])

        self.aapl.D(self.olsr)
        self.olsr.U(self.aapl)

        self.olsr.D(self.link_layer)
        self.link_layer.U(self.olsr)

        self.link_layer.D(self)
        self.U(self.link_layer)

    @property
    def selected_as_mpr(self):
        return self.olsr.selected_as_mpr
    @property
    def routing_table(self):
        return self.olsr.routing_table

    def on_message_from_top(self, eventobj: Event):
        eventobj.event = EventTypes.MFRT
        self.send_down(eventobj)

    def on_message_from_bottom(self, eventobj: Event):
        eventobj.event = EventTypes.MFRB
        self.send_up(eventobj)

    def random_send_message(self):
        # Randomly select a node to send the message
        import random
        from OLSR.message_types import Message

        while True:
            node_number = random.choice(list(self.routing_table.keys())) # Because some nodes may be disconnected.
            if node_number != self.componentinstancenumber:
                break

        # Forge a message and send it to the selected node
        message = Message(
            self.componentinstancenumber,
            node_number, 
            f"Test message from {self.componentinstancenumber} to {node_number}",
            sequencenumber=1
        )
        self.olsr.trigger_event(Event(self, EventTypes.MFRB, message))

def main(number_of_nodes=10):
    import os
    import random
    # Remove plots folder if it exists
    if os.path.exists("plots"):
        import shutil
        shutil.rmtree("plots")

    number_of_hops.clear()

    topo = Topology()

    G = nx.random_geometric_graph(number_of_nodes, 0.4, seed=42)

    topo.construct_from_graph(G, AdHocNode, GenericChannel)

    plot_topology(topo)
    topo.start()
    time.sleep(10) # Wait for the network to stabilize
    
    for _ in range(1000):
        # Pick a random node to send a message
        node = random.choice(topo.nodes)
        t = AHCTimer(1, node.random_send_message)
        t.start()        

    time.sleep(20)
    topo.exit()
    logger.info(f"Avg number of hops: {sum(number_of_hops) / len(number_of_hops)}")
    state_saver.produce_gif()

    return sum(number_of_hops) / len(number_of_hops)
    

if __name__ == '__main__':
    from adhoccomputing.Generics import setAHCLogLevel, DEBUG, INFO
    setAHCLogLevel(INFO)

    main(30)
    
    