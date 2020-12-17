#This code includes the definition of classes and functions

#This class is used for defining configuration messages
class Config:
    def __init__(self, root_name,root_dist,sender_name):
        self.root_name=root_name
        self.root_dist=root_dist
        self.sender_name=sender_name

#This function is to compare two configs and output the better config
def Config_compare(old_config,rec_config):
    if(rec_config.root_name<old_config.root_name):
        return rec_config
    elif(rec_config.root_name==old_config.root_name and rec_config.root_dist<old_config.root_dist):
        return rec_config
    elif(rec_config.root_name==old_config.root_name and rec_config.root_dist==old_config.root_dist and rec_config.sender_name<old_config.sender_name):
        return rec_config
    else:
        return old_config

#This class is used in the second part of the code when a packet is being sent from a source host to a destination host
class Packet:
    def __init__(self,src,dest,sender_index,lan_index,receiver_index):
        self.src=src
        self.dest=dest
        self.sender_index=sender_index #Index of sender bridge
        self.lan_index=lan_index #Index of LAN segement on which this packet currently is
        self.receiver_index=receiver_index #Index of receiver bridge

#This class is a shell for transferring config messages
class Message:
    def __init__(self, config, sender_index, lan_index, receiver_index):
        self.config=config
        self.sender_index=sender_index #Index of sender bridge
        self.lan_index=lan_index #Index of LAN segment on which this message is being sent
        self.receiver_index=receiver_index #Index of receiver bridge

#Class for storing information about bridge
class Bridge:

    def __init__(self, name, index, lan_names):
        self.name=name
        self.index=index #Have defined index separately to make indexing in arrays easier
        self.lan_names=lan_names #Array of names of lan segments this bridge is connected to
        self.lan_indices=[] #Array of indices of lan segments this bridge is connected to
        self.configs=[] #Each element of this array is the config for that port
        self.best_root_name=name #The root bridge according to this bridge (initialized to itself)
        self.best_dist=0 #Distance to root bridge (initialized to 0)
        self.best_neighbour=name #best_neighbour represents nearest neighbour in route to root
        self.forwarding_table=[] #Array, each element tells the forwarding lan for that host

#Takes input the list of all lan segments and adds the ones connected to this bridge to the list for this bridge
    def define_lan_indices(self, lan_segments):

        for i in range(0,len(self.lan_names)):
            self.lan_indices.append(lan_segments.index(self.lan_names[i]))
            self.configs.append(Config(self.name,0,self.name))

#Class for storing information about LAN segment
class Lan_segment:
    def __init__(self,name,index):
        self.name=name
        self.index=index #Have defined index separately to make indexing in arrays easier
        self.bridge_names=[] #Names of bridges it is connected to
        self.bridge_indices=[] #Indices of bridges it is connected to
        self.hosts=[] #Hosts connected to this lan

    def add_host(self,host):
        self.hosts.append(host)

#A class which has arrays of all bridges, lans, hosts etc. Also contains the functions for implementing protocols
class Network:
    def __init__(self):
        self.bridges=[]
        self.lans=[]
        self.num_of_bridges=0
        self.num_of_lans=0
        self.num_of_hosts=0
        self.hosts=[]

    def add_bridge(self,bridge):
        self.bridges.append(bridge)
        self.num_of_bridges+=1

    def add_lan(self,lan):
        self.lans.append(lan)

#We define a (kind of) adjacency matrix where each row represents a bridge and each column is a lan segment (using th indices defined)
    def define_adjacency(self,lan_segments):
        self.num_of_lans=len(lan_segments)
        self.adjacency=[[-1 for i in range(self.num_of_lans)] for j in range(self.num_of_bridges)]

        #During STP algo, -1 means no port, 0 means null port, 1 mean designated port, 2 means root port

        for i in range(0,self.num_of_bridges):
            for j in range(0,self.num_of_lans):
                if(j in self.bridges[i].lan_indices):
                    self.adjacency[i][j]=1
#Spanning Tree Protocol
    def STP(self, trace):
        t=0   #time
        messages=[] #This array stores all the messages generated at that time
        for i in range(0, self.num_of_bridges): #Generates message for each bridge at time 0
            sender_bridge_index=i
            for j in range(0, len(self.bridges[i].lan_indices)):
                lan_index=self.bridges[i].lan_indices[j]
                for k in range(0, len(self.lans[lan_index].bridge_indices)):
                    rec_bridge_index=self.lans[lan_index].bridge_indices[k]
                    if(sender_bridge_index!=rec_bridge_index):
                        message=Message(self.bridges[i].configs[j],sender_bridge_index,lan_index,rec_bridge_index)
                        messages.append(message)
                        if(trace==1):
                            print(t," ",sender_bridge_index," ",rec_bridge_index," ",lan_index," (",self.bridges[i].configs[j].root_name," ",self.bridges[i].configs[j].root_dist," ",self.bridges[i].configs[j].sender_name,")")

        while(messages): #If this array is empty, then the algorithm has converged
            t+=1
            #This loop reads all the messages in the array and updates local configs for ports at each bridge
            for m in range(0,len(messages)):
                message=messages[m]
                rec_bridge_index=message.receiver_index
                lan_index=message.lan_index
                j=self.bridges[rec_bridge_index].lan_indices.index(lan_index)
                old_config=self.bridges[rec_bridge_index].configs[j]
                rec_config=message.config
                new_config=Config_compare(old_config,rec_config)
                self.bridges[rec_bridge_index].configs[j]=new_config

            messages.clear()
            best_change=[0]*self.num_of_bridges #Initialized with 0, if best info according to a bridge changes then that respective element becomes 1

            #Goes to each bridge. At each bridge, checks if local config at any port is better than the current best according to that bridge, if better updates info for the bridge
            for i in range(0, self.num_of_bridges):
                bridge_dummy=self.bridges[i]
                for j in range(0,len(bridge_dummy.lan_indices)):
                    config_dummy=bridge_dummy.configs[j]
                    if(config_dummy.root_name<bridge_dummy.best_root_name):
                        bridge_dummy.best_root_name=config_dummy.root_name
                        bridge_dummy.best_dist=config_dummy.root_dist+1
                        bridge_dummy.best_neighbour=config_dummy.sender_name
                        best_change[i]=1
                    elif(config_dummy.root_name==bridge_dummy.best_root_name and config_dummy.root_dist+1<bridge_dummy.best_dist):
                        bridge_dummy.best_root_name=config_dummy.root_name
                        bridge_dummy.best_dist=config_dummy.root_dist+1
                        bridge_dummy.best_neighbour=config_dummy.sender_name
                        best_change[i]=1
                    elif(config_dummy.root_name==bridge_dummy.best_root_name and config_dummy.root_dist+1==bridge_dummy.best_dist and config_dummy.sender_name<bridge_dummy.best_neighbour):
                        bridge_dummy.best_root_name=config_dummy.root_name
                        bridge_dummy.best_dist=config_dummy.root_dist+1
                        bridge_dummy.best_neighbour=config_dummy.sender_name
                        best_change[i]=1

                self.bridges[i]=bridge_dummy

            #Again goes to each bridge. For each port checks if it is a DP, RP or NP
            for i in range(0,self.num_of_bridges):
                bridge_dummy=self.bridges[i]
                sender_bridge_index=i
                for j in range(0,len(bridge_dummy.lan_indices)):
                    config_dummy=bridge_dummy.configs[j]
                    lan_index=bridge_dummy.lan_indices[j]
                    if(bridge_dummy.best_root_name<config_dummy.root_name):
                        config_dummy.root_name=bridge_dummy.best_root_name
                        config_dummy.root_dist=bridge_dummy.best_dist
                        config_dummy.sender_name=bridge_dummy.name
                        self.adjacency[sender_bridge_index][lan_index]=1 #DP
                    elif(bridge_dummy.best_root_name==config_dummy.root_name and bridge_dummy.best_dist<config_dummy.root_dist):
                        config_dummy.root_name=bridge_dummy.best_root_name
                        config_dummy.root_dist=bridge_dummy.best_dist
                        config_dummy.sender_name=bridge_dummy.name
                        self.adjacency[sender_bridge_index][lan_index]=1 #DP
                    elif(bridge_dummy.best_root_name==config_dummy.root_name and bridge_dummy.best_dist==config_dummy.root_dist and bridge_dummy.name<config_dummy.sender_name):
                        config_dummy.root_name=bridge_dummy.best_root_name
                        config_dummy.root_dist=bridge_dummy.best_dist
                        config_dummy.sender_name=bridge_dummy.name
                        self.adjacency[sender_bridge_index][lan_index]=1 #DP
                    elif(bridge_dummy.best_root_name==config_dummy.root_name and bridge_dummy.best_dist-1==config_dummy.root_dist and bridge_dummy.best_neighbour==config_dummy.sender_name):
                        self.adjacency[sender_bridge_index][lan_index]=2 #RP
                    elif(bridge_dummy.best_root_name==config_dummy.root_name and bridge_dummy.best_dist-1==config_dummy.root_dist and bridge_dummy.best_neighbour<config_dummy.sender_name):
                        self.adjacency[sender_bridge_index][lan_index]=0 #NP
                    elif(bridge_dummy.best_root_name==config_dummy.root_name and bridge_dummy.best_dist==config_dummy.root_dist and bridge_dummy.name>config_dummy.sender_name):
                        self.adjacency[sender_bridge_index][lan_index]=0 #NP

                    bridge_dummy.configs[j]==config_dummy
                    #If best_change[i] is 1 then it generates a new message for each port marked as DP
                    if(best_change[i]==1 and self.adjacency[sender_bridge_index][lan_index]==1):
                        for k in range(0, len(self.lans[lan_index].bridge_indices)):
                            rec_bridge_index=self.lans[lan_index].bridge_indices[k]
                            if(sender_bridge_index!=rec_bridge_index):
                                message=Message(config_dummy,sender_bridge_index,lan_index,rec_bridge_index)
                                messages.append(message)
                                if(trace==1):
                                    print(t," ",sender_bridge_index," ",rec_bridge_index," ",lan_index," (",config_dummy.root_name," ",config_dummy.root_dist," ",config_dummy.sender_name,")")

                self.bridges[i]=bridge_dummy
            #When two ports get marked as root port. This happens when there are two lans between a bridge and its best neighbour.
            #In this case, lan segment with lower name is taken as root and others are marked null.
            for i in range(0,self.num_of_bridges):
                num_of_root=0
                for j in range(0,self.num_of_lans):
                    if(self.adjacency[i][j]==2):
                        num_of_root+=1
                        if(num_of_root>1):
                            self.adjacency[i][j]=0

    #Prints the spanning tree
    def output_spanning_tree(self,to_be_printed):
        a=to_be_printed
        for i in range(0,self.num_of_bridges):
            bridge=self.bridges[i]
            a+="B"
            a+=str(bridge.name)
            a+=": "
            for j in (bridge.lan_indices):
                a+=self.lans[j].name
                a+="-"
                if(self.adjacency[i][j]==1):
                    a+="DP"
                elif(self.adjacency[i][j]==2):
                    a+="RP"
                elif(self.adjacency[i][j]==0):
                    a+="NP"
                if(j!=bridge.lan_indices[-1]):
                    a+=" "
            a+="\n"
        return a


    #Initiates forwarding table as array of -1's
    def define_forwarding_table(self):
        for i in range(0,self.num_of_bridges):
            self.bridges[i].forwarding_table=[-1]*self.num_of_hosts

    def update_forwarding_table(self,src,dest,trace):
        t=0
        packets=[] #Array of packets
        packets_new=[]
        src_index=self.hosts.index(src)
        dest_index=self.hosts.index(dest)
        for i in range(0,self.num_of_lans): #Finding lan of source
            if(src in self.lans[i].hosts):
                src_lan_index=i
        for i in (self.lans[src_lan_index].bridge_indices): #Generating packet for t=0
            if(self.adjacency[i][src_lan_index]==1 or self.adjacency[i][src_lan_index]==2):
                packet=Packet(src,dest,-1,src_lan_index,i)
                packets.append(packet)
                if(trace==1):
                    print(t," ",src," ",dest," ",-1," ",src_lan_index," ",i)
        while(packets): #When it gets empty, we can end the function
            t+=1
            for p in range(0,len(packets)): #Goes through each packet
                packet=packets[p]
                self.bridges[packet.receiver_index].forwarding_table[src_index]=packet.lan_index
                if(self.bridges[packet.receiver_index].forwarding_table[dest_index]!=-1 and self.bridges[packet.receiver_index].forwarding_table[dest_index]!=packet.lan_index): #If present in the forwarding table
                    new_lan_index=self.bridges[packet.receiver_index].forwarding_table[dest_index]
                    for i in (self.lans[new_lan_index].bridge_indices):
                        if(self.adjacency[i][new_lan_index]==1 or self.adjacency[i][new_lan_index]==2):
                            if(i!=packet.receiver_index):
                                packet_new=Packet(src,dest,packet.receiver_index,new_lan_index,i)
                                packets_new.append(packet_new)
                                if(trace==1):
                                    print(t," ",src," ",dest," ",packet.receiver_index," ",new_lan_index," ",i)
                elif(self.bridges[packet.receiver_index].forwarding_table[dest_index]==-1): #If not present in the forwarding table
                    for j in (self.bridges[packet.receiver_index].lan_indices):
                        if(j!=packet.lan_index):
                            if(self.adjacency[packet.receiver_index][j]==1 or self.adjacency[packet.receiver_index][j]==2):
                                new_lan_index=j
                                for i in (self.lans[new_lan_index].bridge_indices):
                                    if(self.adjacency[i][new_lan_index]==1 or self.adjacency[i][new_lan_index]==2):
                                        if(i!=packet.receiver_index):
                                            packet_new=Packet(src,dest,packet.receiver_index,new_lan_index,i)
                                            packets_new.append(packet_new)
                                            if(trace==1):
                                                print(t," ",src," ",dest," ",packet.receiver_index," ",new_lan_index," ",i)

            packets.clear()
            packets=packets_new.copy()
            packets_new.clear()

    #Prints forwarding table
    def output_forwarding_table(self,to_be_printed):
        a=to_be_printed
        for i in range(0,self.num_of_bridges):
            bridge=self.bridges[i]
            a+="B"
            a+=str(bridge.name)
            a+=":\nHOST ID | FORWARDING PORT\n"
            for j in range(0,self.num_of_hosts):
                if(bridge.forwarding_table[j]!=-1):
                    a+="H"
                    a+=str(self.hosts[j])
                    a+=" | "
                    a+=str(self.lans[bridge.forwarding_table[j]].name)
                    a+="\n"
        a+="\n"
        return a
