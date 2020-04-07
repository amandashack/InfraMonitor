import os
import json
import cv2
import numpy as np

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from qtpy import QtCore
from pydm import Display
from qtpy.QtWidgets import (QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QScrollArea, QFrame,
    QApplication, QWidget, QGraphicsView, QGraphicsScene, QGraphicsRectItem, 
    QGraphicsItem, QSizePolicy)

from pydm.widgets import PyDMEmbeddedDisplay
from pydm.utilities import connection


#tomorrow: make the items clickable and have a new blank window open within the scene
#maybe tomorrow: undo/back and redo/forward functionality

#This is the kind of thing we would want to structure in a JSON file

Map = {'Buildings': {"B750": [], "B950": [], "B208": []}} # dictionary used for necessary hard coded information

class GraphicsRectItem(QGraphicsRectItem):
    def __init__(self, i, parent=None):
        super(GraphicsRectItem, self).__init__(parent)
        
        self.name = list(Map['Buildings'].keys())[i]
        self.rect = Map['Buildings'][self.name][1]
        self.color = Map['Buildings'][self.name][0]


    def paint(self, painter, option, widget=None):

        super(GraphicsRectItem, self).paint(painter, option, widget)
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect, self.color)
        painter.setPen(Qt.black)
        painter.setFont(QFont('Arial', 10))
        painter.drawText(self.rect, Qt.AlignCenter, self.name)
        painter.restore()
        

class GraphicsItemGroup(QGraphicsItemGroup):

    def __init__(self, parent=None):
        super(GraphicsItemGroup, self).__init__(parent)

class GraphicsScene(QGraphicsScene):

    def __init__(self, parent = None):
        super(GraphicsScene, self).__init__(parent)
    
    def mousePressEvent(self, event):

        print(event.pos())


class InfrastructureDisplay(Display):

    def __init__(self, parent=None, args=[], macros=None):

        super(InfrastructureDisplay, self).__init__(parent=parent,args=args, macros=None)

        #reference to PyDMApplication - this line is what makes it so that you can avoid 
        #having to define main() and instead pydm handles that for you - it is a subclass of QWidget
        self.app = QApplication.instance()
        #load data from file
        self.load_data()
        #assemble widgets
        self.setup_ui()
    
    def minimumSizeHint(self):
        
        return(QtCore.QSize(750,520))
    
    def ui_filepath(self):

        #no Ui file is being used as of now
        return(None)
    
    def load_data(self):

        #this is responsible for opening the database and adding the information to self.data
        #https://slaclab.github.io/pydm-tutorial/action/python.html

        pass
    
    def setup_ui(self):
        #create layout
        self._layout = QVBoxLayout()
        self.setLayout(self._layout)

        #give it a title
        lbl_title = QLabel("Infrastructure Monitoring System\n Building View")
        lbl_title.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Maximum)
        lbl_title.setMaximumHeight(35)

        lbl_title.setStyleSheet("\
            QLabel {\
                qproperty-alignment: AlignCenter;\
                border: 1px solid #FF17365D;\
                border-top-left-radius: 15px;\
                border-top-right-radius: 15px;\
                background-color: #FF17365D;\
                padding: 5px 0px;\
                color: rgb(255, 255, 255);\
                max-height: 35px;\
                font-size: 14px;\
            }")

        self._layout.addWidget(lbl_title)
        self._layout.addStretch(1)
        
        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Minimum)
        self.frame.setMinimumHeight(500)

        self.view = QGraphicsView()
        self.scene = GraphicsScene()
        self.pixmapItem =QGraphicsPixmapItem()
        self.scene.setSceneRect(0, 0, 500, 500)
        self.view.setScene(self.scene)

        self.view.scene().addItem(self.pixmapItem)
        #would eventually make this fit to size of screen, waiting cause it's annoying.
        self.buildingItems = GraphicsItemGroup()
        

        self._layout.addWidget(self.view)
        self.addBuildings()
    
    def addBuildings(self):
        
        filename = os.getcwd() + "\examplebuildings.png"
        img = cv2.imread(filename)
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret,thresh = cv2.threshold(imgray, 250, 255, 0)
        contours , h = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        MinCntArea = 5000.
        MaxCntArea = 100000.

        self.rectparameters = []
        for cnt in contours:
            
            if cv2.contourArea(cnt) > MinCntArea and cv2.contourArea(cnt) < MaxCntArea:
                # how does the find contours function parse the image? 
                # I am thinking of making rectItems which are invisible and added to the scene - they will go
                # directly on top of each rectangle as it is found in the image.
                # Then a room is created based on certain parameters it looks for in epics/databases
                # say it give it a name as for example B950 - hutch 1.1
                # It loads the map for that room with the items drawn on
                
                
                cv2.drawContours(img, cnt, -1, (0, 255, 0), 3) # this is a green rectangle which shows the found contour

                #cv2.circle(img, (min(cnt.T[0][0]), min(cnt.T[1][0])), 4, 4) #makes a circle around the upper left corner

                #np.set_printoptions(threshold=np.inf) #this is to make it so that the whole numpy array prints to the terminal

                self.rectparameters.append([min(cnt.T[0][0]), min(cnt.T[1][0]), max(cnt.T[0][0])-min(cnt.T[0][0]), max(cnt.T[1][0])-min(cnt.T[1][0])]) # x, y, height, width
                #print("height = ", max(cnt.T[0][0])-min(cnt.T[0][0]), "width = ", max(cnt.T[1][0])-min(cnt.T[1][0]), "upper left corner = ", (min(cnt.T[1][0]), min(cnt.T[0][0])), self.rectparameters)

                
        
        #cv2.imshow('img', img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        #cv2.rectangle(img, (self.rectparameters[0][0], self.rectparameters[0][1]), 
        #                   (self.rectparameters[0][0] + self.rectparameters[0][2], self.rectparameters[0][1] + self.rectparameters[0][3]),
        #                   (255, 0, 0), -1) # draws a blue filled in rectangle - did this to make sure I had the indicies correct for x, y, width, and height

        height, width, channel = img.shape
        self.rectparameters += [height, width]
        print(self.rectparameters)
        bytesPerLine = 3*width
        qimg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

        self.image = QPixmap.fromImage(qimg)
        self.image = self.image.scaled(self.scene.width(), self.scene.height())
        self.pixmapItem.setPixmap(self.image)

        for i in range(len(self.rectparameters)-2):
            
            rect = QGraphicsRectItem(QRectF(QPointF(self.rectparameters[i][0]*(self.scene.width()/width),
                                                                self.rectparameters[i][1]*(self.scene.height()/height)),
                                                                QPointF((self.rectparameters[i][0] + self.rectparameters[i][2]) * self.scene.width()/width,
                                                                (self.rectparameters[i][1] + self.rectparameters[i][3]) * self.scene.height()/height)))
            #rect.setFlags(Qt.ItemIsSelectable)
            rect.setAcceptHoverEvents(True)
            rect.setGroup(self.buildingItems)

        self.scene.addItem(self.buildingItems)
            #self.scene.addRect(QRectF(QPointF(self.rectparameters[i][0]*(self.scene.width()/width),
            #                                                    self.rectparameters[i][1]*(self.scene.height()/height)),
            #                                                    QPointF((self.rectparameters[i][0] + self.rectparameters[i][2]) * self.scene.width()/width,
            #                                                    (self.rectparameters[i][1] + self.rectparameters[i][3]) * self.scene.height()/height)), pen=QPen(), brush=QBrush(Qt.blue))
            
            
            
    
    def mousePressEvent(self, event):
        print(event.pos(), 'Hi')
        #print(self.view.mapToItem(event.pos()), 'penis')
        print(self.view.mapFromScene(event.pos()), "boo")
        print(self.pixmapItem.mapToScene(event.pos()))
        '''
        for i in range(len(Map["Buildings"])):#["Buildings"].values():

            rectItem = GraphicsRectItem(i)
            self.scene.addItem(rectItem)

        self.view.setScene(self.scene)
        self._layout.addWidget(self.view)
        '''        
    '''
    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        self.rect = QRectF(0, 0, 100, 100)
        self.pen = QPen(Qt.black, 2, Qt.SolidLine)
        p.setPen(self.pen)
        p.setFont(QFont('Arial', 10))
        
        p.drawText(self.rect, "Hello")
        p.drawRect(self.rect)
        
        p.end()
    '''
    


