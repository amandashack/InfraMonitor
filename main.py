import os
import json
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
Map = {'Buildings': {"B750": [Qt.red, QRectF(10, 10, 100, 100)], "B950": [Qt.green, QRectF(10, 100, 100, 100)], "B208": [Qt.blue, QRectF(200, 50, 100, 100)]}}

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
        


class InfrastructureDisplay(Display):

    def __init__(self, parent=None, args=[], macros=None):

        super(InfrastructureDisplay, self).__init__(parent=parent,args=args, macros=None)

        #reference to PyDMApplication - this line is what makes it so that you can avoid 
        #having to define main() and instead pydm handles that for you
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
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 500, 500)
        self.addBuildings()
    
    def addBuildings(self):
        
        for i in range(len(Map["Buildings"])):#["Buildings"].values():

            rectItem = GraphicsRectItem(i)
            self.scene.addItem(rectItem)

        self.view.setScene(self.scene)
        self._layout.addWidget(self.view)
        
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
    


