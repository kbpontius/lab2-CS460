import optparse
import sys

import matplotlib
from pylab import *

# Parse a file of rates and plot a smoothed graph. The rate is smoothed
# by summing all the bytes sent over a 1 second interval, and sliding
# the window every 0.1 seconds.
class Plotter:
    def __init__(self,file):
        """ Initialize plotter with a file name. """
        self.file = file
        self.data = []
        self.min_time = None
        self.max_time = None
        self.min_window_size = None
        self.max_window_size = None

    def parse(self):
        """ Parse the data file """
        first = None
        f = open(self.file)
        for line in f.readlines():
            if line.startswith("#"):
                continue
            try:
                t,size = line.split()
            except:
                continue

            # append data to a list of tuples
            t = float(t)
            size = int(size)
            self.data.append((t,size))

            # Keep track of the minimum and maximum time seen
            if not self.min_time or t < self.min_time:
                self.min_time = t
            if not self.max_time or t > self.max_time:
                self.max_time = t

            # Keep track of min/max window size.
            if not self.min_window_size or size < self.min_window_size:
                self.min_window_size = size
            if not self.max_window_size or size > self.max_window_size:
                self.max_window_size = size

    def plot(self):
        """ Create a line graph of the rate over time. """
        clf()
        x = []
        y = []

        for (t,size) in self.data:
            x.append(t)
            y.append(size)
        
        plot(x,y)
        xlabel('Time (seconds)')
        ylabel('Window Size (bytes)')
        ylim([0,self.max_window_size])
        savefig('window_size.png')

def parse_options():
        # parse options
        parser = optparse.OptionParser(usage = "%prog [options]",
                                       version = "%prog 0.1")

        parser.add_option("-f","--file",type="string",dest="file",
                          default=None,
                          help="file")

        (options,args) = parser.parse_args()
        return (options,args)


if __name__ == '__main__':
    (options,args) = parse_options()
    if options.file == None:
        print "plot.py -f file"
        sys.exit()
    p = Plotter(options.file)
    p.parse()
    p.plot()