import socket
import numpy as np
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import *
import pyqtgraph.opengl as gl
import sys
import re
import concurrent.futures

class Simulation(object):
    def __init__(self, type):
        self.app = QtGui.QApplication(sys.argv)
        self.window = gl.GLViewWidget()
        self.window.setGeometry(480, 270, 800, 600)
        self.window.setWindowTitle("Simulation")
        self.window.setCameraPosition(distance=30, elevation=100)

        self.type = type

        self.points_list = []

        if self.type == "live":
            self.s = socket.socket()
            while True:
                host = input(str("Insert the host address of the server \n"))
                try:
                    port = 8080
                    self.s.connect((host, port))
                    print ("connected to " + host)
                    break
                except Exception:
                    print("Could not connect :(")
                    continue
            self.window.show()
            self.three_dim_grid()
            file = open("filename.nmspmm", "wb")
            filedata = self.s.recv(9999999)
            file.write(filedata)
            file.flush()
            file.close()
            file = open("filename.nmspmm", "rb")
            filename_list = str(file.read(10240)).split("b", -1)
            #print(filename_list)
            filename = filename_list[1]
            filename = filename.replace(":", "_")
            self.received_filename = "received_"+filename.replace(".", "_")
            self.saved_filename = "saved_"+filename.replace(".", "_")
            self.animation()

        elif self.type == "offline":
            self.window.show()
            self.three_dim_grid()
            self.load()

    def three_dim_grid(self):
        gx = gl.GLGridItem()
        gx.rotate(90, 0, 1, 0)
        gx.translate(-10, 0, 0)
        self.window.addItem(gx)
        gy = gl.GLGridItem()
        gy.rotate(90, 1, 0, 0)
        gy.translate(0, -10, 0)
        self.window.addItem(gy)
        gz = gl.GLGridItem()
        gz.translate(0, 0, -10)
        self.window.addItem(gz)

    def update(self):
        received_flight_file = open(self.received_filename+".fsm", "wb")
        received_flight_data = self.s.recv(np.int64(10737418240))
        received_flight_file.write(received_flight_data)
        received_flight_file.flush()
        received_flight_file.close()

        received_flight_file = open(self.received_filename+".fsm", "r")
        content = received_flight_file.read(np.int64(10737418240))
        splitted = str(content).split()
        #for index in splitted:
        #    try:
        #        index = float(index) 
        #    except Exception:
        #        splitted.pop(indexcount)
        #    indexcount += 1
        splitted = [float(index)for index in splitted]
        print(splitted)

        self.new_points = [tuple(splitted[i:i+3]) for i in range(0, len(splitted), 3)]
        print(self.new_points)
        #add the new point to the points list
        indexcount = 0
        for _ in self.new_points:
            try:
                if len(_) == 3: 
                    self.points_list.append(_)
                    continue
                else: _.pop(indexcount)
            except Exception:
                _.pop(indexcount)
        #print(self.points_list)
        self.points = np.array(self.points_list) #convert the points list to an array of tuples
        print(self.points_list)
        print(len(self.new_points))
        #saved_flight_file = open(self.saved_filename+"fsm", "w")
        #saved_flight_file.write(str(self.points))
        self.draw() #run the draw function
        
    def load(self):
        self.saved_filename = input(str("Write the filename of the saved simulation:\n"))
        try:        
            flight_file = open(self.saved_filename, "r")
        except Exception:
            self.load()
        flight_data = flight_file.read(np.int64(10737418240))
        splitted = str(flight_data).split() 
        splitted = [float(index)for index in splitted]
        global points
        points = [tuple(splitted[i:i+3]) for i in range(0, len(splitted), 3)]
        print(points)
        #points = np.array(points_list) #convert the points list to an array of tuples
        #print(points)
        self.draw() #run the draw function
        self.start()


    def draw(self):
        drawpoints = gl.GLLinePlotItem(pos=self.points, width=1, antialias=True) #make a variable to store drawing data(specify the points, set antialiasing)
        self.window.addItem(drawpoints) #draw the item
        print("done")

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(20)
        self.start()
        self.update()

    def start(self):
        QtGui.QApplication.instance().exec_()    

def begin():
    menu = input(str("Choose what to do: \n [1]: Live Simulation \n [2]: Load Simulation\n"))
    if menu == "1": Simulation("live")
    elif menu == "2": Simulation("offline")
    else: begin()

begin()