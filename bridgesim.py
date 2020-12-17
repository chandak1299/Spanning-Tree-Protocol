#This code includes taking the input, storing them into classes, calling functions and printing the output
import sys
from bridge import Bridge
from bridge import Network
from bridge import Lan_segment

trace=int(sys.stdin.readline())
num_of_bridges=int(sys.stdin.readline())
network=Network()
lan_segments=set()

#Taking input about the bridges
for i in range(0,num_of_bridges):
    bridge_info=sys.stdin.readline().rstrip()
    bridge_split=bridge_info.split(": ")

    name=int(bridge_split[0][1])
    bridge_lans=sorted(((bridge_split[1].split("\n"))[0]).split(" "))
    bridge_dummy=Bridge(name, i, bridge_lans)

    for j in range(0,len(bridge_lans)):
        lan_segments.add(bridge_lans[j])

    network.add_bridge(bridge_dummy)

lan_segments=sorted(lan_segments)
num_of_lans=len(lan_segments)

for i in range(num_of_bridges):
    network.bridges[i].define_lan_indices(lan_segments)

network.define_adjacency(lan_segments)

for i in range(0,num_of_lans):
    lan=Lan_segment(lan_segments[i],i)
    for j in range(0,num_of_bridges):
        if(network.adjacency[j][i]==1):
            lan.bridge_indices.append(j)
            lan.bridge_names.append(network.bridges[j].name)
    network.add_lan(lan)

to_be_printed=""
network.STP(trace)  #Runs the spanning tree protocol
to_be_printed=network.output_spanning_tree(to_be_printed)  #Prints the first part of the output: spanning tree

#Taking input about the hosts on each lan segments
hosts_list=[]
for i in range(0,network.num_of_lans):
    line=sys.stdin.readline().rstrip()
    lan_name=line.split(": ")[0]
    index=lan_segments.index(line.split(":")[0])
    hosts=(line.split(":")[1].split("\n")[0]).split(" H")
    for j in range(1,len(hosts)):
        network.lans[index].add_host(int(hosts[j]))
        hosts_list.append(int(hosts[j]))

hosts_list=sorted(hosts_list)
network.hosts=hosts_list
network.num_of_hosts=len(hosts_list)
network.define_forwarding_table()

#Taking the message transfer input
num_of_transfers=int(sys.stdin.readline())
for i in range(0,num_of_transfers):
    line=sys.stdin.readline().rstrip()
    src=int(line.split("H")[1])
    dest=int(line.split("H")[2].split("\n")[0])
    network.update_forwarding_table(src,dest,trace)  #Updating forwarding table

    to_be_printed=network.output_forwarding_table(to_be_printed)
print(to_be_printed)
