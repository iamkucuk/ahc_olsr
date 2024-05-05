.. include:: substitutions.rst
========
Abstract
========

The Optimized Link State Routing (OLSR) protocol enhances traditional link state routing for mobile ad hoc networks by utilizing multipoint relays (MPRs). These special nodes are selected to reduce the overhead associated with widespread broadcasting. By employing MPRs, OLSR reduces broadcast repetitions by approximately 95%, from 17,784 in basic broadcasting down to just 971.

In OLSR, only MPRs transmit link state information, focusing on their direct connections rather than the entire network. This selective approach not only minimizes the volume of control messages but also enhances the efficiency of data distribution, aiding in the calculation of more accurate and optimal routing paths. My findings show that OLSR adapts effectively to changing network topologies, often delivering near-optimal routing results.

However, the protocol faces stability challenges due to its operation without full knowledge of the actual network topology, which can sometimes result in sub-optimal routing decisions. Despite these limitations, OLSR proves highly effective in large and dense networks, making it a robust choice for future mobile wireless LANs due to its significant reduction in broadcast overhead and ability to maintain route accuracy.