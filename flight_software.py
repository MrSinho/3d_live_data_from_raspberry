import socket
import numpy as np
import pyqtgraph as pg
import numpy as np
from pyqtgraph.Qt import *
import pyqtgraph.opengl as gl
import sys
import re
import concurrent.futures
import ast
from ast import literal_eval

np.set_printoptions(threshold=sys.maxsize)

class Simulation(object):
    def __init__(self, type):
        self.app = QtGui.QApplication(sys.argv)
        self.window = gl.GLViewWidget()
        self.window.setGeometry(480, 270, 800, 600)
        self.window.setWindowTitle("Simulation")
        self.window.setCameraPosition(distance=30, elevation=100)

        self.type = type

        self.points_list = []
        self.points_backup = []

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
            self.full_filename = "full_"+filename.replace(".", "_")
            self.animation()
            
            

        elif self.type == "offline":
            self.load()

    def three_dim_grid(self):
        g1 = gl.GLGridItem()
        g1.rotate(90, 0, 1, 0)
        g1.scale(100, 100, 100)
        g1.translate(-1000, 0, 0)
        self.window.addItem(g1)
        g2 = gl.GLGridItem()
        g2.rotate(90, 1, 0, 0)
        g2.scale(100, 100, 100)
        g2.translate(0, -1000, 0)
        self.window.addItem(g2)
        g3 = gl.GLGridItem()
        g3.scale(100, 100, 100)
        g3.translate(0, 0, -1000)
        self.window.addItem(g3)
        #g4 = gl.GLGridItem()
        #g4.rotate(90, 0, 1, 0)
        #g4.scale(1000, 1000, 1000)
        #g4.translate(10000, 0, 0)
        #self.window.addItem(g4)
        #g5 = gl.GLGridItem()
        #g5.rotate(90, 1, 0, 0)
        #g5.scale(1000, 1000, 1000)
        #g5.translate(0, 10000, 0)
        #self.window.addItem(g5)
        #g6 = gl.GLGridItem()
        #g6.scale(1000, 1000, 1000)
        #g6.translate(0, 0, 10000)
        #self.window.addItem(g6)

    def recv_data(self):
        while True:
            received_flight_file = open(self.received_filename+".fsm", "wb")
            received_flight_data = self.s.recv(np.int64(10737418240))
            received_flight_file.write(received_flight_data)
            received_flight_file.flush()
            received_flight_file.close()

            received_flight_file = open(self.received_filename+".fsm", "r")
            content = received_flight_file.read(np.int64(10737418240))
            self.splitted = str(content).split()
            self.splitted = [float(index)for index in self.splitted]
            #print(splitted)
            self.new_points = [tuple(self.splitted[i:i+3]) for i in range(0, len(self.splitted), 3)]
            print("received")
            time.sleep(.1)
            #move on recv_data

    def save_all(self):
        while True:
            try:
                full_flight = open(f"{self.full_filename}data.fsm", "w")
                full_flight.write(str(self.points_list))
                full_flight.flush()
                full_flight.close()
                print("saved all")
            except Exception: print("did not save :(")
            time.sleep(.1)

    def check (self):
        while True:
            indexcount = 0
            try:
                for _ in self.new_points:         
                    if len(_) == 3: 
                        self.points_list.append(_)
                        continue
                    else: _.pop(indexcount)
                print("checked")
            except Exception: print("did not check")
            time.sleep(.1)
    
    def update(self):
        #indexcount = 0
        #try:
            #for _ in self.new_points:         
            #    if len(_) == 3: 
            #        self.points_list.append(_)
            #        continue
            #    else: _.pop(indexcount)
        try:
            try: 
                self.window.removeItem(self.drawpoints)
                print("deleted previous line")
            except Exception: "could not delete previous line :("
            #print(self.points_list)
            print(f"length new points: {len(self.new_points)}")
            print(f"total points: {len(self.points_list)}")
            self.points = np.array(self.points_list) #convert the points list to an array of tuples
            self.drawpoints = gl.GLLinePlotItem(pos=self.points, width=1, antialias=True) #make a variable to store drawing data(specify the points, set antialiasing)
            self.draw() #run the draw function
        except Exception: print("did not draw")
        
        
    def load(self):
        full_flight_filename = input(str("Write the filename of the saved simulation:\n"))
        try:        
            full_flight = open(full_flight_filename, "r")
        except Exception:
            print("could not find the file :(")
            self.load()
        flight_data = full_flight.read(np.int64(10737418240))
        self.points_list = list(ast.literal_eval(str(flight_data))) #convert the points list to an array of tuples
        print(self.points_list)
        while True:
            input_scale_fit = input(str("Insert the scale value, type 1 to keep default."))
            try: 
                scale_fit = int(input_scale_fit)
                print(scale_fit)
                break
            except Exception: continue
        self.points_list = [_*scale_fit for __ in self.points_list for _ in __]
        self.points_list = self.new_points = [tuple(self.points_list[i:i+3]) for i in range(0, len(self.points_list), 3)]
        print(self.points_list)
        self.points = np.array(self.points_list)
        self.drawpoints = gl.GLLinePlotItem(pos=self.points, width=1, antialias=True) #make a variable to store drawing data(specify the points, set antialiasing)
        self.window.addItem(self.drawpoints) #run the draw function
        self.window.show()
        self.three_dim_grid()
        self.start()


    def draw(self):
        self.window.addItem(self.drawpoints) #draw the item
        print("drawed line")      

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(10)
        self.start()

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            if self.type == "live":
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    recv_thread = executor.submit(self.recv_data)
                    check_thread = executor.submit(self.check)
                    save_thread = executor.submit(self.save_all)
                    exec_thread = executor.submit(QtGui.QApplication.instance().exec_())
            elif self.type == "offline":
                QtGui.QApplication.instance().exec_()

def begin():
    menu = input(str("Choose what to do: \n [1]: Live Simulation \n [2]: Load Simulation\n"))
    if menu == "1": 
        if __name__ == "__main__":
            Simulation("live")
    elif menu == "2": Simulation("offline")
    else: begin()

begin()
