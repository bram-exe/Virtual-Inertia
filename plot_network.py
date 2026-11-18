import andes
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ss = andes.load('9bus_sim.xlsx', no_output=True)

G = nx.Graph()
for b in ss.Bus.idx.v:
    G.add_node(b)
for b1, b2, vn1, vn2 in zip(ss.Line.bus1.v, ss.Line.bus2.v, ss.Line.Vn1.v, ss.Line.Vn2.v):
    G.add_edge(b1, b2, xfmr=(vn1 != vn2))

pos = {2:(0,2), 7:(1,2), 8:(2,2), 9:(3,2), 3:(4,2),
       5:(1,1), 6:(3,1), 4:(2,0.4), 1:(2,-0.4)}

gen_buses  = {ss.GENROU.bus.v[0]: 'Gas', ss.REGCA1.bus.v[0]: 'Solar', ss.REGCV1.bus.v[0]: 'HVDC (GFM)'}
LOAD_ROLE = {'PQ_0': 'Utility', 'PQ_1': 'Utility', 'PQ_2': 'Utility', 'DC_7': 'Data center'}
load_buses = {bus: LOAD_ROLE.get(idx, 'Load') for idx, bus in zip(ss.PQ.idx.v, ss.PQ.bus.v)}

COLORS = {'gen': 'tab:orange', 'Utility': 'tab:blue', 'Data center': 'tab:purple', 'none': 'lightgray'}
def bus_color(b):
    if b in gen_buses:  return COLORS['gen']
    if b in load_buses: return COLORS[load_buses[b]]
    return COLORS['none']
color = [bus_color(b) for b in G.nodes]

fig, ax = plt.subplots(figsize=(9, 5))
lines = [e for e in G.edges if not G.edges[e]['xfmr']]
xfmrs = [e for e in G.edges if G.edges[e]['xfmr']]
nx.draw_networkx_edges(G, pos, edgelist=lines, ax=ax, width=2)
nx.draw_networkx_edges(G, pos, edgelist=xfmrs, ax=ax, width=2, style='dashed')
nx.draw_networkx_nodes(G, pos, node_color=color, node_size=700, ax=ax)
nx.draw_networkx_labels(G, pos, ax=ax, font_color='white', font_weight='bold')

for b, name in gen_buses.items():
    x, y = pos[b]
    dy = -0.3 if y < 0 else 0.25
    ax.text(x, y + dy, name, ha='center', fontsize=9)
for b, role in load_buses.items():
    x, y = pos[b]
    left = x < 2
    ax.text(x - 0.15 if left else x + 0.15, y - 0.2, role,
            ha='right' if left else 'left', fontsize=9)

key = [
    Line2D([], [], marker='o', ls='', ms=12, color=COLORS['gen'],         label='Generator'),
    Line2D([], [], marker='o', ls='', ms=12, color=COLORS['Utility'],     label='Utility load'),
    Line2D([], [], marker='o', ls='', ms=12, color=COLORS['Data center'], label='Data center load'),
    Line2D([], [], marker='o', ls='', ms=12, color=COLORS['none'],        label='Transmission bus'),
    Line2D([], [], color='k', lw=2,          label='Line'),
    Line2D([], [], color='k', lw=2, ls='--', label='Transformer'),
]
ax.legend(handles=key, loc='upper left', bbox_to_anchor=(1.0, 1.0), frameon=False)
ax.set_title('WSCC 9-bus system')
ax.axis('off')
plt.tight_layout()
plt.show()