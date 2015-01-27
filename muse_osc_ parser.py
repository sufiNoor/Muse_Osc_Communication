from liblo import *
import sys
import time
import csv
import numpy

calib_ongoing = 0
calib = 0
calib_data = [[0 for x in range(5)] for x in range(5)]
done = 0
alphabaseline = 0.0
calib_done = 0
alpha_data = []
state_data = []
time_data = []
i = 0
class MuseServer(ServerThread):
    #listen for messages on port 5001
    def __init__(self):
        ServerThread.__init__(self, 5001)

    #receive accelrometer data

    #receive EEG data
    @make_method('/muse/elements/alpha_relative', 'ffff')
    def eeg_callback(self, path, args):
        global calib_done
        global calib_ongoing
        global alphabaseline
        global i
        current = time.time()
        split = current-start
        l_ear, l_forehead, r_forehead, r_ear = args
        alpha_data.append((l_ear+r_ear)/2)
        if calib_ongoing == 1 and int(split) < 10:
            #print "Calibrating!! %f" % split
            calib_data[0].append(path)
            calib_data[1].append(l_ear)
            calib_data[2].append(l_forehead)
            calib_data[3].append(r_forehead)
            calib_data[4].append(r_ear)
        elif calib_ongoing == 1 and calib_done == 0 and int(split) > 10:
            #print "Calibration done!"
            alphabaseline = (numpy.mean(calib_data[4])+numpy.mean(calib_data[3]))/2
            #alphabaseline = numpy.mean(calib_data[1])
            print "Alpha baseline: %f" % alphabaseline
            calib_done = 1
            calib_ongoing = 0
        if l_ear > alphabaseline*2 and alphabaseline != 0:
            #print "Wow! You are so deep!"
            state_data.append(0)
        elif l_ear <  alphabaseline/2 and  alphabaseline != 0:
            #print "I'm so excited, I just can't hide it!"
            state_data.append(2)
        else:
            state_data.append(1)
        print "%s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)
        time_data.append(time.time()-abstart)
        with open('data.csv', 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=' ')
            #writer.writerow(state_data)
            writer.writerow(alpha_data)
            writer.writerow(time_data)
            writer.writerow([alphabaseline])
        print "Sampling rate: %f" % (i/split)
        i += 1
        #with open('data.csv', 'wb') as csvfile:
            #spamwriter = csv.writer(csvfile, delimiter='x ')

            #spamwriter.writerow(alpha_data)
            #spamwriter.writerow([alphabaseline])

try:
    server = MuseServer()
except ServerError, err:
    print str(err)
    sys.exit()

server.start()
start = time.time()

if __name__ == "__main__":
    abstart = time.time()
    while 1:
        if calib == 0:
            print "Calibration starting in 5 seconds..."
            time.sleep(5)
            calib_ongoing = 1
            start = time.time()
            calib = 1
        time.sleep(1)