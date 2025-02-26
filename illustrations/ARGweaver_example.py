import collections
import io
import sys
from pathlib import Path

import networkx as nx
import matplotlib.pyplot as plt

# useful scripts in the top level dir
sys.path.append(str(Path(__file__).parent.parent.absolute()))
from constants import NODE_IS_RECOMB, NODE_IS_ALWAYS_UNARY, NODE_IS_SOMETIMES_UNARY
import convert
import ts_process
import argdraw

ts = convert.arg_to_ts(io.StringIO(
"""\
start=0	end=1000
name	event	age	pos	parents	children
1	recomb	132.704741329	918	5,16	n2
2	coal	441.51496637	0	11	n5,n1
3	recomb	441.51496637	271	26,25	n6
4	recomb	1160.13100175	670	14,7	n0
5	coal	1160.13100175	0	10	n3,1
6	recomb	2832.38458802	59	18,9	n7
7	recomb	2832.38458802	782	8,14	4
8	coal	2832.38458802	0	15	7,n4
9	recomb	2832.38458802	714	10,20	6
10	coal	2832.38458802	0	21	9,5
11	recomb	2832.38458802	254	12,13	2
12	recomb	2832.38458802	7	13,16	11
13	coal	2832.38458802	0	17	12,11
14	coal	2832.38458802	0	20	7,4
15	recomb	2832.38458802	826	29,28	8
16	coal	2832.38458802	0	23	12,1
17	recomb	6723.79797033	695	27,18	13
18	coal	6723.79797033	0	19	17,6
19	recomb	6723.79797033	41	28,22	18
20	coal	6723.79797033	0	26	14,9
21	recomb	6723.79797033	484	35,23	10
22	recomb	6723.79797033	834	24,25	19
23	coal	6723.79797033	0	30	21,16
24	recomb	6723.79797033	222	39,29	22
25	coal	6723.79797033	0	37	22,3
26	coal	6723.79797033	0	32	20,3
27	recomb	6723.79797033	6	40,30	17
28	coal	6723.79797033	0	31	19,15
29	coal	6723.79797033	0	31	24,15
30	coal	6723.79797033	0	33	23,27
31	coal	6723.79797033	0	34	29,28
32	recomb	6723.79797033	474	33,45	26
33	coal	6723.79797033	0	41	30,32
34	recomb	6723.79797033	710	36,37	31
35	recomb	6723.79797033	314	42,36	21
36	coal	6723.79797033	0	39	34,35
37	coal	6723.79797033	0	38	34,25
38	recomb	6723.79797033	731	51,40	37
39	coal	6723.79797033	0	54	24,36
40	coal	6723.79797033	0	43	27,38
41	recomb	6723.79797033	734	44,43	33
42	recomb	6723.79797033	100	45,44	35
43	coal	15779.3014157	0	46	41,40
44	coal	15779.3014157	0	47	42,41
45	coal	15779.3014157	0	46	32,42
46	coal	15779.3014157	0	48	43,45
47	recomb	15779.3014157	194	48,50	44
48	coal	15779.3014157	0	49	46,47
49	recomb	15779.3014157	636	51,50	48
50	coal	15779.3014157	0	52	49,47
51	coal	15779.3014157	0	52	49,38
52	coal	15779.3014157	0	53	50,51
53	recomb	36851.8872842	598	54,55	52
54	coal	36851.8872842	0	55	53,39
55	coal	36851.8872842	0		54,53
n0	gene	0.0	0	4	
n1	gene	0.0	0	2	
n2	gene	0.0	0	1	
n3	gene	0.0	0	5	
n4	gene	0.0	0	8	
n5	gene	0.0	0	2	
n6	gene	0.0	0	3	
n7	gene	0.0	0	6	
"""))

with open(Path(__file__).parent / "ARGweaver_trees.svg", "wt") as f:
    f.write(ts.draw_svg())

ts = ts_process.flag_unary_nodes(ts) 
ts = ts_process.add_individuals_to_coalescence_nodes(ts) # optional - can help if simplifying away rRE and CA nodes

G = ts_process.to_networkx_graph(ts)

nodes_at_time = collections.defaultdict(list)
colour_map = []
for nd in G.nodes(data=True):
    nodes_at_time[nd[1]["time"]].append(nd[0])
    colour = "lightgreen"
    if nd[1]["flags"] & NODE_IS_RECOMB:
        colour = "red"
    elif nd[1]["flags"] & NODE_IS_ALWAYS_UNARY:
        colour = "cyan"
    elif nd[1]["flags"] & NODE_IS_SOMETIMES_UNARY:
        colour = "lightseagreen"
    colour_map.append(colour)
        
    
# Turn into graphviz
A = nx.nx_agraph.to_agraph(G)
# First cluster all nodes at the same times (probably mostly samples)
for t, nodes in nodes_at_time.items():
    if len(nodes) > 1:
        A.add_subgraph(nodes, level="same", name=f"cluster_t{t}")
# We could also cluster nodes from a single individual together here

# Get the positions from graphviz
A.layout(prog="dot")
pos = {n: [float(x) for x in A.get_node(n).attr["pos"].split(",")] for n in G.nodes()}

fig = plt.figure(1, figsize=(10, 15))
argdraw.draw_with_curved_multi_edges(G, pos, colour_map, 20)
plt.savefig(Path(__file__).parent / 'ARGweaver_arg.pdf')  