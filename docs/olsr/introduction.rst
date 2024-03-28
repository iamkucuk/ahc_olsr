.. include:: substitutions.rst

Introduction
============


The Optimized Link State Routing (OLSR) algorithm is a key player in the dynamic world of network communication, particularly in mobile ad hoc networks (MANETs). The problem it addresses is straightforward yet complex: how to efficiently route data between mobile nodes in a constantly changing network topology. This challenge is not only interesting but also crucial, as solving it enables reliable and efficient communication in military operations, disaster recovery, and other critical mobile network applications.

The importance of OLSR lies in its potential to provide robust and responsive network routing. Without effective solutions like OLSR, mobile networks could suffer from slow data transmission, high overhead costs, and poor scalability, significantly hampering their operational effectiveness.

However, crafting an efficient routing protocol for such networks is hard. Naive approaches often fall short due to the dynamic nature of MANETs, where network topology can change rapidly due to node mobility. Traditional routing protocols that work well in static networks become inefficient when faced with such volatility.

Previous solutions to this problem have been varied, but many were plagued by high overhead and slow reaction to topological changes. OLSR distinguishes itself by using an optimized version of the classic link state algorithm, which aggressively reduces the amount of routing information broadcasted in the network by using multipoint relays (MPRs). This innovation significantly decreases the overhead and improves the protocol's scalability.

The key components of the OLSR algorithm include:
- Multipoint Relays (MPRs): A selected set of nodes that forward broadcast messages during the flooding process, which reduces the number of transmissions required.
- Periodic message exchange: To maintain route information, OLSR nodes periodically exchange control messages, which keeps the network's routing information up-to-date.
- Hop-by-hop routing: Each node uses its most recent information to route data, ensuring that the path used is as current as possible.

However, OLSR is not without its limitations. Its performance can degrade in highly mobile scenarios due to the periodic updating of routes, which may not keep pace with the rate of topological changes.

Contributions of the OLSR algorithm to the field of network routing are significant and can be summarized as follows:

- It provides an efficient and proactive routing protocol for mobile ad hoc networks.
- It reduces the routing overhead in such networks through the use of MPRs.
- It improves the scalability of network routing, accommodating larger and more dynamic networks.