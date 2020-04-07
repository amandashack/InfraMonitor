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

'''

Having the window pop up for the correct building thoughts:
this may be a signals and slots solution or maybe parent and child widget thing
when mouse press event happens for the Item it could either
send a signal to the correct building class based on location
or it could access a function in the parent (QGraphicsView)
which would then handle the pointing to the correct building

'''

class GraphicsRectItem(QGraphicsRectItem):

    def __init__(self, parent=None):
        super(GraphicsRectItem, self).__init__(parent)

        self.brush = QBrush(Qt.lightGray)
        self.brush.setStyle(Qt.NoBrush)
        self.setBrush(self.brush)

    def hoverEnterEvent(self, e):
        self.setOpacity(.7)
        self.brush.setStyle(Qt.SolidPattern)
        self.setBrush(self.brush)
        self.update()
    
    def hoverLeaveEvent(self, e):
        self.setOpacity(1.)
        self.brush.setStyle(Qt.NoBrush)
        self.setBrush(self.brush)
        self.update()

    def mousePressEvent(self, e):
        print("hi")
    
    def mouseReleaseEvent(self, e):
        print("bye")
        

class GraphicsScene(QGraphicsScene):

    def __init__(self, parent = None):
        super(GraphicsScene, self).__init__(parent)


class GraphicsView(QGraphicsView):

    def __init__(self, parent=None):

        super(GraphicsView, self).__init__(parent)

        self.scene = QGraphicsScene()
        self.pixmapItem = QGraphicsPixmapItem()
        self.scene.setSceneRect(0, 0, 500, 500)
        self.setScene(self.scene)
        self.scene.addItem(self.pixmapItem)
        #would eventually make this fit to size of screen, waiting cause it's annoying.

        self.buildingParams = []
        self.scalef = [1, 1]

        self.Buildings()
    
    def Buildings(self):
        
        filename = os.getcwd() + "\examplebuildings.png"
        img = cv2.imread(filename)
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        ret,thresh = cv2.threshold(imgray, 250, 255, 0)
        contours , h = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        MinCntArea = 5000.
        MaxCntArea = 100000.

        for cnt in contours:
            
            if cv2.contourArea(cnt) > MinCntArea and cv2.contourArea(cnt) < MaxCntArea:
                
                cv2.drawContours(img, cnt, -1, (0, 255, 0), 3) # this is a green rectangle which shows the found contour

                #cv2.circle(img, (min(cnt.T[0][0]), min(cnt.T[1][0])), 4, 4) #makes a circle around the upper left corner

                #np.set_printoptions(threshold=np.inf) #this is to make it so that the whole numpy array prints to the terminal

                self.buildingParams.append([min(cnt.T[0][0]), min(cnt.T[1][0]), max(cnt.T[0][0])-min(cnt.T[0][0]), max(cnt.T[1][0])-min(cnt.T[1][0])]) # x, y, height, width
                
        # copy and paste these three lines if you would like to see what an opencv images looks like anywhere in the program
        #cv2.imshow('img', img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()

        #cv2.rectangle(img, (self.buildingParams[0][0], self.buildingParams[0][1]), 
        #                   (self.buildingParams[0][0] + self.buildingParams[0][2], self.buildingParams[0][1] + self.buildingParams[0][3]),
        #                   (255, 0, 0), -1) # draws a blue filled in rectangle - did this to make sure I had the indicies correct for x, y, width, and height

        height, width, channel = img.shape
        bytesPerLine = 3*width
        qimg = QImage(img.data, width, height, bytesPerLine, QImage.Format_RGB888).rgbSwapped()

        ##### need to add not null checks here

        self.ogimage = QPixmap.fromImage(qimg)
        self.image = self.ogimage.scaled(self.scene.width(), self.scene.height())
        self.pixmapItem.setPixmap(self.image)

        self.updateScalef()
        self.buildingParams += self.scalef

        for i in range(len(self.buildingParams)-2):

            parameters = self.buildingParams
            rect = GraphicsRectItem(QRectF(QPointF(parameters[i][0] * parameters[4],
                                                                parameters[i][1] * parameters[5]),
                                                                QPointF((parameters[i][0] + parameters[i][2]) * parameters[4],
                                                                (parameters[i][1] + parameters[i][3]) * parameters[5])))
            
            rect.setAcceptHoverEvents(True)
            self.scene.addItem(rect)

        

    def updateScalef(self):

        self.scalef[0] = self.image.width()/self.ogimage.width()
        self.scalef[1] = self.image.height()/self.ogimage.height()

    def mousePressEvent(self, e):
        print(e.pos())
        #print(self.scene.itemAt(e.pos()))



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

        self.view = GraphicsView()
        self.view.setMouseTracking(True)

        self._layout.addWidget(self.view)


