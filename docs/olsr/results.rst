.. include:: substitutions.rst

Implementation, Results and Discussion
======================================

Implementation and Methodology
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For this work, I used the adhoccomputing library which is a Python-based framework for simulating and programming ad hoc networks. The library gives access to a wide variety of components and abstractions to build event-driven models and combine them in order to create more complex network topologies. One of these components is the OLSR protocol, an essential building block for realistic experiments. 

The OLSR implementation is composed of several main components: 

OLSRComponent : This is the main component that represents an OLSR node in the network and extends the GenericModel class provided by the adhoccomputing library. It maintains a neighbor set, a topology table and a routing table and handles all events of type HELLO messages, TC (Topology Control) messages and message forwarding.

HelloMessage and TCMessage : These are custom message classes representing HELLO and TC messages in the OLSR protocol. They extend the GenericMessage class and contain message source, destination and payload.

OLSREventTypes : It is an enumeration that defines event types used by the OLSR implementation. These include HELLO and TC events. 


The OLSRComponent initializes timers for periodically sending HELLO and TC messages. When a HELLO message is received, the component updates its neighbor set with the information about the one-hop neighbor. When a TC message is received, the component updates its topology table with the topology information received from other nodes.


The OLSR protocol uses a method called Multi-Point Relays (MPRs) to decrease the burden of transmitting topology information everywhere. Every node selects a group of MPRs from its one-hop neighbors so that these MPRs cover all their two-hop neighbors. The select_mpr function in the OLSRComponent applies the MPR selection algorithm by using two-hop neighbor details.

The OLSRComponent's calculate_routing_table method is responsible for computing the routing table according to the present topological info. It uses Dijkstra's algorithm in order to determine shortest paths towards every accessible node within network.

The send_hello, send_tc, on_hello and on_tc functions are managing the sending and receiving of HELLO and TC messages. The method send_down is for sending events to lower layer parts like channel.

Results
~~~~~~~~

Present your AHCv2 run results, plot figures.


TO BE FILLED IN WHEN THE IMPLEMENTATION IS COMPLETE

Discussion
~~~~~~~~~~

TO BE FILLED IN WHEN THE IMPLEMENTATION IS COMPLETE

