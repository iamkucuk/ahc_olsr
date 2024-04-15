from enum import Enum
from adhoccomputing.Experimentation.Topology import Event
from adhoccomputing.GenericModel import GenericMessage, GenericModel, GenericMessageHeader
from adhoccomputing.Generics import Event, AHCTimer, MessageDestinationIdentifiers

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

        self.hello_timer = AHCTimer(5, self.send_hello)
        self.tc_timer = AHCTimer(10, self.send_tc)

        self.neighbor_set = set()
        self.routing_table = {}

    def send_hello(self):
        hello_message = HelloMessage(
            message_from=self.componentinstancenumber,
            message_to=MessageDestinationIdentifiers.LINKLAYERBROADCAST,
            payload=None
        )
        self.send_peer(Event(self, OLSREventTypes.HELLO, hello_message))

    def send_tc(self):
        tc_message = TCMessage(
            message_from=self.componentinstancenumber,
            message_to=MessageDestinationIdentifiers.NETWORKLAYERBROADCAST,
            payload=self.neighbor_set,
            nexthop=MessageDestinationIdentifiers.LINKLAYERBROADCAST
        )
        self.send_peer(Event(self, OLSREventTypes.TC, tc_message))

    def on_hello(self, eventobj: Event):
        hello_message = eventobj.eventcontent
        self.neighbor_set.add(hello_message.header.messagefrom)
        self.routing_table[hello_message.header.messagefrom] = {
            "nexthop": hello_message.header.messagefrom,
            "distance": 1
        }        

    def on_tc(self, eventobj: Event):
        tc_message = eventobj.eventcontent
        self.routing_table[tc_message.header.messagefrom] = {
            "nexthop": tc_message.header.messagefrom,
            "distance": self.routing_table.get(tc_message.header.messagefrom, {}).get("distance", 1) + 1
        }
        for neighbor in tc_message.payload:
            if neighbor not in self.neighbor_set:
                self.neighbor_set.add(neighbor)
                self.send_hello()




