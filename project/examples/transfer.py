import sys
sys.path.append('..')

from src.sim import Sim
from src.node import Node
from src.link import Link
from src.transport import Transport
from src.tcp import TCP

from networks.network import Network

import optparse
import os
import subprocess

class AppHandler(object):
    def __init__(self,filename,unique_file_id):
        file_title,file_extension = filename.split('.')
        self.filename = file_title + str(unique_file_id) + '.' + file_extension
        self.directory = 'received'
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.f = open("%s/%s" % (self.directory,self.filename),'w')

    def receive_data(self,data):
        # Sim.trace('AppHandler',"application got %d bytes" % (len(data)))
        self.f.write(data)
        self.f.flush()

class Main(object):
    def __init__(self):
        self.directory = 'received'
        self.parse_options()
        tcp_flows = self.run()
        self.diff(tcp_flows)

    def parse_options(self):
        parser = optparse.OptionParser(usage = "%prog [options]",
                                       version = "%prog 0.1")

        parser.add_option("-f","--filename",type="str",dest="filename",
                          default='internet-architecture.pdf',
                          help="filename to send")

        parser.add_option("-l","--loss",type="float",dest="loss",
                          default=0.0,
                          help="random loss rate")

        (options,args) = parser.parse_args()
        self.filename = options.filename
        self.loss = options.loss

    def diff(self, tcp_flows):
        file_title,file_extension = self.filename.split('.')

        for i in range(0,tcp_flows):
            new_file_name = file_title + str(i+1) + '.' + file_extension
            args = ['diff', '-u', self.filename, self.directory + '/' + new_file_name]
            result = subprocess.Popen(args, stdout=subprocess.PIPE).communicate()[0]
            print
            if not result:
                print "# File transfer correct: " + new_file_name + '!'
            else:
                print "# File transfer failed. Here is the diff:"
                print
                print result

    def run(self):
        # parameters
        Sim.scheduler.reset()
        Sim.set_debug('AppHandler')
        Sim.set_debug('TCP')

        # setup network
        net = Network('../networks/one-hop.txt')
        net.loss(self.loss)

        # setup routes
        n1 = net.get_node('n1')
        n2 = net.get_node('n2')

        n1.add_forwarding_entry(address=n2.get_address('n1'),link=n1.links[0])  # n1 -> n2
        n2.add_forwarding_entry(address=n1.get_address('n2'),link=n2.links[0])  # n1 <- n2

        # setup transport
        t1 = Transport(n1)
        t2 = Transport(n2)

        # setup application
        tcp_flows = 1
        a1 = AppHandler(self.filename, 1)

        # setup connection
        c1a = TCP(t1, n1.get_address('n2'), 1, n2.get_address('n1'), 1, 3000, a1)
        c2a = TCP(t2, n2.get_address('n1'), 1, n1.get_address('n2'), 1, 3000, a1)

        # send a file
        with open(self.filename,'r') as f:
            while True:
                data = f.read(1000)
                if not data:
                    break
                Sim.scheduler.add(delay=0, event=data, handler=c1a.send)

        # run the simulation
        Sim.scheduler.run()
        return tcp_flows

if __name__ == '__main__':
    m = Main()
