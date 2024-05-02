import networkx as nx
import threading
import matplotlib.pyplot as plt
plt.switch_backend('agg')
import os
from copy import deepcopy

class TopologyStateSaver:
    states = []
    graphs = []

    def __init__(self) -> None:
        pass

    def save_state(self, topology):
        # Put a thread lock here
        # with Lock():
        self.states.append({k: v.selected_as_mpr for k, v in topology.nodes.items()})
        self.graphs.append(deepcopy(topology.G))

    def save_each_state(self):
        # Save each state using plot_topology
        for graph, state in zip(self.graphs, self.states):
            for node, selected_as_mpr in state.items():
                graph.nodes[node]['selected_as_mpr'] = selected_as_mpr
            plot_topology(graph, in_thread=False)

    def produce_gif(self):
        # Save each state using plot_topology
        try:
            from PIL import Image
        except ImportError:
            raise ImportError("You need to have the Python Imaging Library (PIL) installed to create a GIF.")
        self.save_each_state()
        images = []
        for i in range(len(self.states)):
            images.append(Image.open(f'plots/{i + 1}.png'))
        images[0].save('plots/animation.gif', save_all=True, append_images=images[1:], optimize=False, duration=500, loop=0)
            
        

def plot_topology(topology, in_thread=True):
    if in_thread:
        # Create a new thread for plotting
        plot_thread = threading.Thread(target=_plot_topology, args=(topology,))
        # plot_thread.daemon = True
        plot_thread.start()
    else:
        _plot_topology(topology)

def _plot_topology(topology):
    # Create a new figure and axis
    fig, ax = plt.subplots(figsize=(8, 6))

    # Check if the input is a NetworkX graph
    if isinstance(topology, nx.Graph):
        # Get the selected_as_mpr attributes of the nodes
        selected_as_mpr = nx.get_node_attributes(topology, 'selected_as_mpr')

        # Create a list of colors for each node
        colors = ['blue' if selected_as_mpr.get(node, False) else 'red' for node in topology.nodes]
        
        # Set the graph to the input
        G = topology
    else:
        # Create a list of colors for each node
        colors = ['blue' if getattr(node, 'selected_as_mpr', False) else 'red' for node in topology.nodes.values()]
        
        # Set the graph to the graph of the topology
        G = topology.G

    # Modify the colors of one-hop neighbors of blue nodes to green
    for node in G.nodes:
        if colors[list(G.nodes).index(node)] == 'blue':
            for neighbor in G.neighbors(node):
                if colors[list(G.nodes).index(neighbor)] == 'red':
                    colors[list(G.nodes).index(neighbor)] = 'green'

    # Draw the graph
    pos = nx.kamada_kawai_layout(G)
    nx.draw(G, pos, with_labels=True, font_weight='bold', ax=ax, node_color=colors)

    # Set the title and labels
    ax.set_title("Topology Plot")
    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    # Display the plot
    plt.tight_layout()

    # Create the plots directory if it doesn't exist
    if not os.path.exists('plots'):
        os.makedirs('plots')

    # Find the highest numbered file in the plots directory
    highest_num = 0
    for file in os.listdir('plots'):
        if file.endswith('.png'):
            num = int(file.split('.')[0])
            if num > highest_num:
                highest_num = num

    # Save the plot with the next number
    plt.savefig(f'plots/{highest_num + 1}.png')