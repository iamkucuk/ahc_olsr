import networkx as nx
import time

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import * #Event, setAHCLogLevel, ConnectorTypes, EventTypes, logger, AHCTimer, DEBUG
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from adhoccomputing.DistributedAlgorithms.Broadcasting.Broadcasting import ControlledFlooding,BroadcastingEventTypes
import logging

repeat_counter = 0

class ApplicationLayer(GenericModel): 
  def on_message_from_bottom(self, eventobj: Event):
    logger.applog(f"{self.componentname}-{self.componentinstancenumber} RECEIVED {str(eventobj)}")

class AdHocNode(GenericModel):
  def on_message_from_top(self, eventobj: Event):
    eventobj.event = EventTypes.MFRT
    global repeat_counter
    repeat_counter += 1
    self.send_down(eventobj)

  def on_message_from_bottom(self, eventobj: Event):
    eventobj.event = EventTypes.MFRB
    global repeat_counter
    repeat_counter += 1
    self.send_up(eventobj)

  def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
    super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
    # SUBCOMPONENTS
    self.appl = ApplicationLayer("ApplicationLayer", componentinstancenumber, topology=topology)
    self.broadcastservice = ControlledFlooding("ControlledFlooding", componentinstancenumber, topology=topology)
    self.linklayer = GenericLinkLayer("GenericLinkLayer", componentinstancenumber, topology=topology)

    self.components.append(self.appl)
    self.components.append(self.broadcastservice)
    self.components.append(self.linklayer)

    
    # CONNECTIONS AMONG SUBCOMPONENTS
    self.appl.connect_me_to_component(ConnectorTypes.DOWN, self.broadcastservice)
    self.broadcastservice.connect_me_to_component(ConnectorTypes.UP, self.appl)

    self.broadcastservice.connect_me_to_component(ConnectorTypes.DOWN, self.linklayer)
    self.linklayer.connect_me_to_component(ConnectorTypes.UP, self.broadcastservice)

    # Connect the bottom component to the composite component....
    self.linklayer.connect_me_to_component(ConnectorTypes.DOWN, self)
    self.connect_me_to_component(ConnectorTypes.UP, self.linklayer)

topo = Topology()

def send_broadcast_message_event():
  topo.nodes[0].broadcastservice.trigger_event(Event(None, BroadcastingEventTypes.BROADCAST, "BROADCAST MESSAGE"))

def main(number_of_nodes=50):
  global repeat_counter
  repeat_counter = 0
  #A random geometric graph, undirected and without self-loops
  G = nx.random_geometric_graph(number_of_nodes, 0.4, seed=42)
    
  topo.construct_from_graph(G, AdHocNode, GenericChannel)
  topo.start()
  t = AHCTimer(1, send_broadcast_message_event)
  t.start()

  time.sleep(5)
  t.cancel()
  topo.exit()

  logger.info(f"Repeat counter: {repeat_counter} for {number_of_nodes} nodes")
  return repeat_counter


if __name__ == "__main__":
  #NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
  setAHCLogLevel(INFO)

  counts = []
  for number_of_nodes in range(10, 60, 10):
    count = main(number_of_nodes)
    counts.append(count)
  
  import matplotlib.pyplot as plt
  plt.plot(range(10, 60, 10), counts)
  plt.xlabel("Number of nodes")
  plt.ylabel("Number of messages")
  plt.title("Broadcasting")
  plt.savefig("broadcast.png")
  plt.close()

  # write the results to a file
  with open("broadcast.txt", "w") as f:
    f.write("Number of nodes, Number of messages\n")
    for i in range(len(counts)):
      f.write(f"{10 + i * 10}, {counts[i]}\n")