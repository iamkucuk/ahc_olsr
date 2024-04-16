from enum import Enum
from adhoccomputing.Experimentation.Topology import Event
from adhoccomputing.GenericModel import GenericMessage, GenericModel, GenericMessageHeader
from adhoccomputing.Generics import Event, AHCTimer, MessageDestinationIdentifiers
import networkx as nx

class OLSREventTypes(Enum):
    HELLO = "hello"
    TC = "topology_control"

class HelloMessage(GenericMessage):
    def __init__(
            self, 
            message_from, 
            message_to, 
            nexthop=float('inf'), 
            interfaceid=float('inf'), 
            sequencenumber=-1, 
            payload=None
        ):
        header = GenericMessageHeader(
            OLSREventTypes.HELLO,
            message_from,
            message_to,
            nexthop=nexthop,
            interfaceid=interfaceid,
            sequencenumber=sequencenumber
        )
        super().__init__(header, payload=payload)

class TCMessage(GenericMessage):
    def __init__(
            self, 
            message_from, 
            message_to, 
            payload,
            nexthop=float('inf'), 
            interfaceid=float('inf'), 
            sequencenumber=-1, 
        ):
        header = GenericMessageHeader(
            OLSREventTypes.TC,
            message_from,
            message_to,
            nexthop=nexthop,
            interfaceid=interfaceid,
            sequencenumber=sequencenumber
        )
        super().__init__(header, payload=payload)

class OLSRComponent(GenericModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.eventhandlers[OLSREventTypes.HELLO] = self.on_hello
        self.eventhandlers[OLSREventTypes.TC] = self.on_tc

        self.hello_timer = AHCTimer(2, self.send_hello)
        self.tc_timer = AHCTimer(5, self.send_tc)

        self.neighbor_set = set()
        self.topology = {}

    def send_hello(self):
        hello_message = HelloMessage(
            message_from=self.componentinstancenumber,
            message_to=MessageDestinationIdentifiers.LINKLAYERBROADCAST,
            payload=self.neighbor_set,
        )
        self.send_down(Event(self, OLSREventTypes.HELLO, hello_message))

    def send_tc(self):
        tc_message = TCMessage(
            message_from=self.componentinstancenumber,
            message_to=MessageDestinationIdentifiers.NETWORKLAYERBROADCAST,
            payload=self.select_mpr(),
            nexthop=MessageDestinationIdentifiers.LINKLAYERBROADCAST
        )
        self.send_down(Event(self, OLSREventTypes.TC, tc_message))

    def on_hello(self, eventobj: Event):
        hello_message = eventobj.eventcontent
        self.neighbor_set.add(hello_message.header.messagefrom)
        self.routing_table[hello_message.header.messagefrom] = {
            "nexthop": hello_message.header.messagefrom,
            "distance": 1
        }

    def on_tc(self, eventobj: Event):
        tc_message = eventobj.eventcontent
        mpr_selectors = tc_message.payload['mpr_selectors']
        self.topology[tc_message.header.messagefrom] = {
            "mpr_selectors": mpr_selectors
        }

    def select_mpr(self):
        two_hop_neighbors = set()
        for neighbor in self.neighbor_set:
            for neighbor_neighbor in self.topology[neighbor]['mpr_selectors']:
                two_hop_neighbors.add(neighbor_neighbor)
        
        two_hop_neighbors.discard(self.componentinstancenumber)

        mpr_set = set()
        while two_hop_neighbors:
            best_neighbor = max(self.neighbor_set, key=lambda x: len(two_hop_neighbors.intersection(self.topology[x]['mpr_selectors'])))
            mpr_set.add(best_neighbor)
            two_hop_neighbors.difference_update(self.topology[best_neighbor]['mpr_selectors'])

        return mpr_set
    
    def calculate_routing_table(self):
        for node in self.topology:
            self.routing_table[node] = {
                "nexthop": None,
                "distance": float('inf')
            }
        
        self.routing_table[self.componentinstancenumber] = {
            "nexthop": self.componentinstancenumber,
            "distance": 0
        }

        for neighbor in self.neighbor_set:
            self.routing_table[neighbor] = {
                "nexthop": neighbor,
                "distance": 1
            }

        for node in self.topology:
            for neighbor in self.topology[node]['mpr_selectors']:
                if self.routing_table[node]['distance'] + 1 < self.routing_table[neighbor]['distance']:
                    self.routing_table[neighbor] = {
                        "nexthop": node,
                        "distance": self.routing_table[node]['distance'] + 1
                    }
    
    # def get_shortest_path(self, destination):
    #     graph = nx.Graph()
    #     for node in self.topology:
    #         for neighbor in self.topology[node]['mpr_selectors']:
    #             graph.add_edge(node, neighbor)

    #     if not nx.has_path(graph, self.componentinstancenumber, destination):
    #         return None
        
    #     return nx.shortest_path(graph, self.componentinstancenumber, destination)





