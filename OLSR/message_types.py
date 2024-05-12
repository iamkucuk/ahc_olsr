from adhoccomputing.GenericModel import GenericMessage, GenericMessageHeader

from OLSR.enums import OLSREventTypes

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
        """
        Represents a Hello message in the OLSR protocol.

        Args:
            message_from (int): The identifier of the sender.
            message_to (int): The identifier of the receiver.
            nexthop (float, optional): The next hop for the message. Defaults to float('inf').
            interfaceid (float, optional): The interface ID. Defaults to float('inf').
            sequencenumber (int, optional): The sequence number of the message. Defaults to -1.
            payload (Any, optional): The payload of the message. Defaults to None.
        """
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
        """
        Represents a TC (Topology Control) message in the OLSR protocol.

        Args:
            message_from (int): The identifier of the sender.
            message_to (int): The identifier of the receiver.
            payload (Any): The payload of the message.
            nexthop (float, optional): The next hop for the message. Defaults to float('inf').
            interfaceid (float, optional): The interface ID. Defaults to float('inf').
            sequencenumber (int, optional): The sequence number of the message. Defaults to -1.
        """
        header = GenericMessageHeader(
            OLSREventTypes.TC,
            message_from,
            message_to,
            nexthop=nexthop,
            interfaceid=interfaceid,
            sequencenumber=sequencenumber
        )
        super().__init__(header, payload=payload)

class Message(GenericMessage):
    def __init__(
            self, 
            message_from, 
            message_to, 
            payload,
            nexthop=float('inf'), 
            interfaceid=float('inf'), 
            sequencenumber=-1, 
        ):
        """
        Represents a generic message to be passed through.

        Args:
            message_from (int): The identifier of the sender.
            message_to (int): The identifier of the receiver.
            payload (Any): The payload of the message.
            nexthop (float, optional): The next hop for the message. Defaults to float('inf').
            interfaceid (float, optional): The interface ID. Defaults to float('inf').
            sequencenumber (int, optional): The sequence number of the message. Defaults to -1.
        """
        header = GenericMessageHeader(
            'Generic',
            message_from,
            message_to,
            nexthop=nexthop,
            interfaceid=interfaceid,
            sequencenumber=sequencenumber
        )
        super().__init__(header, payload=payload)