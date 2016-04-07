#!/usr/bin/env python

##############
###
### Qt is licensed under a commercial and open source license (GNU Lesser General Public License version 2.1)
### This programs is licensed under a commercial and open source license (GNU Lesser General Public License version 2.1)
###
### latest coding - Konstantin Glazyrin for the needs of P02.2 beamline PETRAIII - DESY (coded under Python 2.7, PyQt version 4.10, Qt version 4.8.4)
#############
#import sip
#sip.setapi('QVariant', 1)

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import os
import sys
import time

from random import gauss
from itertools import cycle


DISCLAMER = """-- gui for markers - overlay - beam position, etc --
-- GPL licence applies - as we use QT library for free --

version 0.5
0.5 improvement - correction for Python 3 style of code
0.4 improvement - update of calibration tab
0.3 improvement - full coordination between gui and marker window
0.2 improvement - basic gui
0.1 improvement - basic marker functionality + key strokes
coding by Konstantin Glazyrin
contact lorcat@gmail.com for questions, comments and suggestions 
"""


# marker window opacity settings
OPAMOVE = 0.5
OPASTILL = 1.0
OPAMINIMUM = 0.3
OPAMAXIMUM = 1.0
OPASTEP = 0.1

# Icons for combobox
QICONW = 100
QICONH = 20

# QSettings initial values - organization name and program name
ORGNAME = "PETRA-III"
ORGDOMAIN = "desy.de"
PROGNAME = "P02.2-Marker"

# constants to operate with QSettings keys
# general - different groups
(SETMWGROUP, SETMARGROUP) = ("mainWindow", "markerWindow")
# main window
(SETPOS, SETSIZE, SETMARSHAPE, SETMARCOLOR, SETMARMCCOLOR, 
    SETMARMCPOS, SETMARMCDISPLAY,
    SETDISPLAY, SETCURSORDISPLAY, SETOPACITY,
    SETMOVESTEP, SETMOVESTEPSMALL, SETRESIZESTEP, SETRESIZESTEPSMALL,
    SETMARMCMOVESTEP, SETMARMCMOVESTEPSMALL,
    SETGRIDUNIT, SETSCRDISTANCE, SETOBJDISTANCE) = ("pos", "size", "marker-shape", "marker-color", "move-cursor-color",
                    "move-cursor-pos", "move-cursor-visibility",
                    "frame-visibility", "frame-cursor-visibility", "marker-opacity",
                    "marker-move-step", "marker-move-step-small", "marker-resize-step", "marker-resize-step-small",
                    "move-cursor-move-step", "move-cursor-move-step-small", 
                    "marker-grid-unit", "calibr-screen-dist", "calibr-object-dist")

# constants for shape designition
(SHAPESQR, SHAPECIRCLE, SHAPERECT, SHAPEELLIPSE, SHAPEGRID, SHAPEBOUNDS)= (0, 1, 2, 3, 4, 5)

# line lenght parameters
# for cross shape
CROSSLENGTH = 5
CROSSSPACE = 5
# for bounds shape
BOUNDSLENGTH = 20


# color macros
COLORGRN = QColor(200, 200, 0)
COLORBRN = QColor(0, 200, 200)
COLORPRPL = QColor(200, 0, 200)
COLORORG = QColor(255, 255, 0)
COLORBLUE = QColor(0, 0, 255)
COLORLIGHTBLUE = QColor(150, 150, 255)
COLORGREEN = QColor(0, 255, 0)
COLORLIGHTGREEN = QColor(150, 255, 150)
COLORRED = QColor(255, 0, 0)
COLORLIGHTRED = QColor(255, 150, 150)
COLORGREY = QColor(150, 150, 150)
COLORWHITE = QColor(255, 255, 255)
COLORBLACK = QColor(0, 0, 0)
MOVECURSORCOLORLIST = (COLORLIGHTRED, COLORGRN, COLORBRN, COLORPRPL, COLORORG, COLORBLUE, COLORLIGHTBLUE, COLORGREEN, COLORLIGHTGREEN, COLORRED, COLORGREY, COLORWHITE, COLORBLACK)
FRAMECOLORLIST = (COLORGRN, COLORBRN, COLORPRPL, COLORORG, COLORBLUE, COLORLIGHTBLUE, COLORGREEN, COLORLIGHTGREEN, COLORRED, COLORGREY, COLORWHITE, COLORBLACK)
# overlay colors
(COLOROVERLAYBKG, COLOROVERLAYBKGLINE, COLOROVERLAYLINE, COLOROVERLAYTEXT) = (QColor(100, 100, 100, 100), QColor(100, 100, 100, 0), QColor(255, 255, 100, 255), QColor(255, 0, 0, 150))

# shade color - if no element is visible
SHADECOLOR = QColor(100, 0, 0, 100)
SHADEPEN = 0

# grid settings
GRID10 = 60
GRID1 = 6
GRIDTHICK = 1
GRIDUNITMIN = 2
GRIDUNITMAX = 30

# thickness macros
(THICK, THIN) = (3, 2)

# sets of parameters used to draw a shape and a cursor
# (shape, penwidth, cursor pen width)
SQRTHICK = (SHAPESQR, THICK, THICK)
SQRTHIN = (SHAPESQR, THIN, THIN)
RECTTHICK = (SHAPERECT, THICK, THICK)
RECTTHIN = (SHAPERECT, THIN, THIN)
CIRCLETHICK = (SHAPECIRCLE, THICK, THICK)
CIRCLETHIN = (SHAPECIRCLE, THIN, THIN)
ELLIPSETHICK = (SHAPEELLIPSE, THICK, THICK)
ELLIPSETHIN = (SHAPEELLIPSE, THIN, THIN)
BOUNDSTHICK = (SHAPEBOUNDS, THICK, THICK)
BOUNDSTHIN = (SHAPEBOUNDS, THIN, THIN)
GRID = (SHAPEGRID, GRIDTHICK, THICK)
FRAMESHAPELIST = (SQRTHICK, SQRTHIN, CIRCLETHICK, CIRCLETHIN, RECTTHICK, RECTTHIN, ELLIPSETHICK, ELLIPSETHIN, BOUNDSTHICK, BOUNDSTHIN, GRID)

# minimal dimension for window
MINDIMENSION = 70

# buttons types
(BTNLARGEUP, BTNLARGEDOWN, BTNLARGELEFT, BTNLARGERIGHT,
    BTNSMALLUP,BTNSMALLDOWN,BTNSMALLLEFT,BTNSMALLRIGHT
    ) = (1,3,5,7,2,4,6,8)

# basic Marker and gui signals
SIGNALMOVERESIZE = "moveOrResize"
SIGNALMOVECURSOR = "moveCursorEvent"
SIGNALSTYLE = "styleChange"
SIGNALCALIBRATION = "calibrationSuccess"
SIGNALCALIBRATIONCANCELED = "calibrationCanceled"
SIGNALREPORT = "reportChange"

# overlay modes for operation
(OVERLAYCALIBRATION) = (0)


# basic buttons gui clicked() operation flags/signal - type of operation with marker
(BTNSMARKERMOVE, BTNSMARKERRESIZE, BTNSMOVECURSOR) = (0, 1, 2)
    # subflags - discriminate large or small buttons
(BTNSMALLSTEP, BTNLARGESTEP) = (0, 1)

###
### class MarkerCanvas - transparent marker window implementation
### does not use python @properties to simplify operation
### but uses '_' for variables intended for inner use
###
class MarkerCanvas(QWidget):
    def __init__(self, app=None, parent=None):
        super(MarkerCanvas, self).__init__(parent)
        self._app = app

        self.title = "Marker"
        self.setWindowTitle(self.title)

        # variables
        self.initVars()

        # events handling
        self.initCanvasEvents()

        # init window params
        self.initSelf()

        # init signals and slots
        self.initSignals()

        # show widget
        self.show()
        return

    # initialization
    # variables
    def initVars(self):
        # track mouse position
        self._oldMousePos = None

        # track window position
        self._oldwdgtPos = None
        self.movestep = 30         # controls movement by keyboard
        self.movestepsmall = int(self.movestep/10)

        # size - values here and below are used for initialization only
        # they are changed on read/write settings procedure
        self._h = 300               # just for the initialization
        self._w = 300               # just for the initialization
        self.sizestep = 30          # controls resize events
        self.sizestepsmall = int(self.sizestep/10)

        #center
        self._cenx = 0
        self._ceny = 0

        # visual switches
        # center cross
        self.bcross = True                  #visibility

        # frame visibility
        self.bframe = True                  #visibility

        # movable cross
        self.bcrossmove = False             #visibility
        self.cursormovepos = None
        self.cursormovestep = 10
        self.cursormovestepsmall = 1

        # shapes
        self._shapeslist = FRAMESHAPELIST
        self.shapes = cycle(self._shapeslist)
        self.shape = None
        self.setShape()

        # colors move cursor
        self._cursorcolorslist = MOVECURSORCOLORLIST
        self.movecursorcolors = cycle(self._cursorcolorslist)
        self.movecursorcolor = None
        self.setMoveCursorColor()

        # colors frame
        self._colorslist = FRAMECOLORLIST
        self.colors = cycle(self._colorslist)
        self.color = None
        self.setColor()

        # opacity
        self.opacity = OPASTILL
        self.OPAMOVE = OPAMOVE

        # grid unit
        self.gridunit = GRID1

        # to process close event
        self._bclose = False

        # antialiasing hint
        self._antialiasing = QPainter.HighQualityAntialiasing
        return

    # style of the widget
    def initSelf(self):
        # size
        self.resize(self._h, self._w)

        # style 
        # translucient, window on top
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_NativeWindow , True)
        self.setWindowOpacity(self.opacity)
        self.setFocusPolicy(Qt.TabFocus|Qt.ClickFocus)
        self.setBackgroundRole(QPalette.Window)
        

        #background - color
        pal = QPalette()
        self.setAutoFillBackground(True)
        pal.setColor(QPalette.Window, QColor(100,100,100, 100))
        self.setPalette(pal)
        return

    # initialize signals and slots
    def initSignals(self):
        return

    def initCanvasEvents(self):
        return

    # event processing related
    def report(self, msg):
        self.emit(SIGNAL(SIGNALREPORT), "Action: %s"%msg)

    # mouse events processing
    def mousePressEvent(self, event):
        # track only left clicks
        if(event.button()==Qt.LeftButton):
            self._oldMousePos = event.globalPos()
            self._oldwdgtPos = self.pos()
            self.grabMouse()

            self.setWindowOpacity(self.OPAMOVE)
        return

    def mouseMoveEvent(self, event):
        # track if we have oldMousePos setup - move window position
        if(self._oldMousePos):
            newpos = event.globalPos() - self._oldMousePos
            self.move(self._oldwdgtPos+newpos)

            # notify MArkerControl that the position has changed
            self.emit(SIGNAL(SIGNALMOVERESIZE))
        return

    def mouseReleaseEvent(self, event):
        # if we track the position - release mouse
        if(event.button()==Qt.LeftButton):
            self.releaseMouse()
            # clean up
            self._oldMousePos = None
            self._oldwdgtPos = None

            self.setWindowOpacity(self.opacity)
        return

    # simple getters // setters avoiding properties this time - just stupid using properties for this
    # return shapes in use or set them // don't think I will use it often
    def getSetShapes(self, value = None):
        if(value!=None):
            self.shapes = value
        return self.shapes

    # returns current shape in use
    def getSetShape(self, value=None):
        if(value is not None):
            # QSettings provide QVariant value, parse it, convert to list of ints
            if(type(value) is QVariant):
                value = self.listQvarToInts(value)
            # select specific shape
            self.selectSpecificShape(value)
        return self.shape

    # return colors in use or set them // don't think I will use it often
    def getSetColors(self, value = None):
        if(value!=None):
            self.colors = value
        return self.colors

    # returns current shape in use or sets it
    def getSetColor(self, value = None):
        if(value!=None):
            if(type(value) is QColor): # 
                value = QColor(value)
            self.selectSpecificColor(value)
        return self.color

    # return colors in use or set them // don't think I will use it often
    def moveCursorGetSetColors(self, value = None):
        if(value!=None):
            self.movecursorcolors = value
        return self.movecursorcolors

    # returns current shape in use or sets it
    def moveCursorGetSetColor(self, value = None):
        if(value!=None):
            if(type(value) is QColor): # 
                value = QColor(value)
            self.selectMoveCursorSpecificColor(value)
        return self.movecursorcolor

    # movable cursor position
    def moveCursorGetSetPos(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toPoint()
            self.cursormovepos = value
            self.emit(SIGNAL(SIGNALMOVECURSOR))
            self.report("change of movable cursor position")
        return self.cursormovepos

    # movable cursor position
    def moveCursorGetSetVisibility(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toBool()
            self.bcrossmove = value
            self.report("change of movable cursor visibility")
            self.update()
        return self.bcrossmove

    # frame visibility
    def getSetVisibility(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toBool()
            self.bframe = value
            self.update()
        return self.bframe

    # static cursor visibility
    def getSetCursorVisibility(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toBool()
            self.bcross = value
            self.report("change of marker frame visibility")
            self.update()
        return self.bcross

    # returns current opacity or sets it
    def getSetOpacity(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toFloat()[0]
            elif(type(value)==type(list()) or  type(value)==type(tuple())): # for a case when I forget to transorm some values
                value = float(value[0])
            if(type(value)==type(float()) and value>=OPAMINIMUM and value<=OPAMAXIMUM+OPASTEP/2):
                self.opacity = value
                self.report("change of marker window opacity")
                self.setWindowOpacity(self.opacity)
        return self.opacity

    # returns frame moving step - large
    def getSetMoveStep(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toInt()[0]
            elif(type(value)==type(list()) or  type(value)==type(tuple())): # for a case when I forget to transorm some values
                value = int(value[0])
            if(type(value)==type(int())):
                self.report("change of marker window move step (large)")
                self.movestep = value
        return self.movestep

    # returns frame moving step - small
    def getSetMoveStepSmall(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toInt()[0]
            elif(type(value)==type(list()) or  type(value)==type(tuple())): # for a case when I forget to transorm some values
                value = int(value[0])
            if(type(value)==type(int())):
                self.report("change of marker window move step (small)")
                self.movestepsmall = value
        return self.movestepsmall

    # returns marker resize step - large
    def getSetResizeStep(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toInt()[0]
            elif(type(value)==type(list()) or  type(value)==type(tuple())): # for a case when I forget to transorm some values
                value = int(value[0])
            if(type(value)==type(int())):
                self.report("change of marker window resize step (large)")
                self.sizestep = value
        return self.sizestep

    # returns marker resize step - small
    def getSetResizeStepSmall(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toInt()[0]
            elif(type(value)==type(list()) or  type(value)==type(tuple())): # for a case when I forget to transorm some values
                value = int(value[0])
            if(type(value)==type(int())):
                self.report("change of marker window resize step (small)")
                self.sizestepsmall = value
        return self.sizestepsmall

    # returns cursor moving step - large
    def moveCursorGetSetMoveStep(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toInt()[0]
            elif(type(value)==type(list()) or  type(value)==type(tuple())): # for a case when I forget to transorm some values
                value = int(value[0])
            if(type(value)==type(int())):
                self.report("change of movable cursor move step (large)")
                self.cursormovestep = value
        return self.cursormovestep

    # returns cursor moving step - small - small is always used for movements with keyboard keypress events
    def moveCursorGetSetMoveStepSmall(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toInt()[0]
            elif(type(value)==type(list()) or  type(value)==type(tuple())): # for a case when I forget to transorm some values
                value = int(value[0])
            if(type(value)==type(int())):
                self.report("change of movable cursor move step (small)")
                self.cursormovestepsmall = value
        return self.cursormovestepsmall

    # returns grid unit step in px
    def getSetGridUnit(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toInt()[0]
            elif(type(value)==type(list()) or  type(value)==type(tuple())): # for a case when I forget to transorm some values
                value = int(value[0])
            if(type(value)==type(int())):
                self.report("change of the smallest grid unit size (px)")
                self.gridunit = value
        return self.gridunit

    # list of QVariants to list of ints
    # should throw exception if cannot transform QVariant to a list, but fine
    def listQvarToInts(self, tlist):
        tlist = tlist.toList()
        value = []
        for v in tlist:
            value.append(v.toInt()[0])
        return value

    # painting 
    def paintEvent(self, event):
        # settings for shape, thickness
        (shape, pen, pencursor) = self.shape

        # flag to control if something is really drawn
        bpaint = False

        # main painter object
        painter = QPainter(self)
        painter.setRenderHint(self._antialiasing)
        
        # pen for the outer rim
        mypen = painter.pen()
        mypencolor = self.color
        #mypencolor.setAlpha(int(self.opacity*255))
        mypen.setColor(mypencolor)
        
        mybrush = QBrush(QColor(255, 255, 255, 0)) # int(self.opacity*255)
        painter.setBrush(mybrush)

        (x, y, width, height) = (int(pen/2),int(pen/2),self.width()-pen, self.height()-pen)
        (cenx, ceny) = (int((x+width)/2), int((y+height)/2))
        (self._cenx, self._ceny) = (cenx, ceny)

        # paint cross if required for better centering
        if(self.bcross):
            mypen.setWidth(pencursor)
            painter.setPen(mypen)

            (crossx, crossy) = (self._cenx, self._ceny)
            self.drawCross(painter, crossx, crossy, width, height)

            bpaint = True or bpaint

        # initialize cursormovepos once
        if(self.cursormovepos is None):
                self.moveCursorGetSetPos(QPoint(10, -10))

        # painting movable cross
        if(self.bcrossmove):
            bpaint = True or bpaint

        # draw frame settings
        mypen.setWidth(pen)
        mypen.setColor(self.color)
        #mypencolor.setAlpha(int(self.opacity*255))
        painter.setPen(mypen)

        # draw frame depending on settings
        if(self.bframe):
            bpaint = True or bpaint

        # if there should be nothing drawn - draw a shade - set it now
        # penwidfth is used to discriminate between different SHADE and normal modes
        if(not bpaint):
            mypen.setWidth(SHADEPEN)
            mypen.setColor(SHADECOLOR)
            painter.setPen(mypen)
            mybrush = QBrush(SHADECOLOR)
            painter.setBrush(mybrush)
            pen = SHADEPEN

        # draw a shade or a normal marker
        if(self.bframe or not bpaint):
            if(shape==SHAPESQR):
                self.drawSQR(painter, x, y, width, height, pen)
            elif(shape==SHAPECIRCLE):
                self.drawCircle(painter, x, y, width, height, pen)
            elif(shape==SHAPERECT):
                self.drawRect(painter, x, y, width, height, pen)
            elif(shape==SHAPEELLIPSE):
                self.drawEllipse(painter, x, y, width, height, pen)
            elif(shape==SHAPEBOUNDS):
                self.drawRectBounds(painter, x, y, width, height, pen)
            elif(shape==SHAPEGRID):
                self.drawGrid(painter, x, y, width, height, pen)

        # painting movable cross
        if(self.bcrossmove):
            mypen.setWidth(pencursor)
            mypen.setColor(self.movecursorcolor)
            painter.setPen(mypen)

            # make a certain shift to compensate for
            (crossx, crossy) = (self.cursormovepos.x()+self._cenx, self.cursormovepos.y()+self._ceny)
            self.drawCross(painter, crossx, crossy, width, height)

        # finish painting
        painter.end()
        return

    # draws a cross
    def drawCross(self, painter, cenx, ceny, width, height):
        crosslength = CROSSLENGTH
        crossspace = CROSSSPACE

        painter.drawLine(cenx-(crossspace+crosslength), ceny, cenx-crossspace, ceny)     # left
        painter.drawLine(cenx+(crossspace+crosslength), ceny, cenx+crossspace, ceny)     # right

        painter.drawLine(cenx, ceny-(crossspace+crosslength), cenx, ceny-crossspace)     # bottom
        painter.drawLine(cenx, ceny+(crossspace+crosslength), cenx, ceny+crossspace)     # top
        return

    # draw grid
    def drawGrid(self, painter, x, y, width, height, pen):
        (cenx, ceny) = (self._cenx, self._ceny)

        (grid1, grid10) = (int(self.gridunit), int(self.gridunit*10))

        # y direction - up
        numlines = int(round(ceny/grid10))+1
        ystart = ceny
        for i in range(numlines):
            self.cycleGrid(painter, i)
            painter.drawLine(x, ystart-i*grid10, width, ystart-i*grid10)
            painter.drawLine(x, ystart+i*grid10, width, ystart+i*grid10)

        # units up + down
        numunits = int(round(ystart/grid1))+1
        for j in range(numunits):
            painter.drawLine(cenx, ystart-j*grid1, cenx+5, ystart-j*grid1)
            painter.drawLine(cenx, ystart+j*grid1, cenx+5, ystart+j*grid1)

        # x direction - left
        numlines = int(round(cenx/grid10))+1
        xstart = cenx
        for i in range(numlines):
            self.cycleGrid(painter, i)
            painter.drawLine(xstart-i*grid10, y, xstart-i*grid10, height) 
            painter.drawLine(xstart+i*grid10, y, xstart+i*grid10, height) 

        numunits = int(round(xstart/grid1))+1
        xstart = cenx
        for j in range(numunits):
            painter.drawLine(xstart-j*grid1, ceny, xstart-j*grid1, ceny+5)
            painter.drawLine(xstart+j*grid1, ceny, xstart+j*grid1, ceny+5)


        # prepare normal pen for frame - solid
        mypen = painter.pen()
        mypen.setStyle(Qt.SolidLine)
        painter.setPen(mypen)
        painter.drawRect(QRect(x, y, width, height))


        # prepare for a case - nothing seen
        temppen = int(pen/2)
        if(temppen==0):
            temppen = 1
        # entity for moving - only if not a shade form
        if(pen>0):
            color = QColor(self.color)
            color.setAlpha(90)
            mybrush = QBrush(color) # int(self.opacity*255)
            painter.setBrush(mybrush)
            painter.drawRect(QRect(width-20+temppen, height-20+temppen, 20, 20))

        # units
        return

    # cycle different paint styles
    def cycleGrid(self, painter, i):
        if(i%2):
            mypen = painter.pen()
            mypen.setStyle(Qt.DashLine)
            mypen.setDashPattern([5,5])
            painter.setPen(mypen)
        else:
            mypen = painter.pen()
            mypen.setStyle(Qt.SolidLine)
            painter.setPen(mypen)

    # draw square
    def drawSQR(self, painter, x, y, width, height, pen):

        painter.drawRect(QRect(x, y, width, height))

        temppen = int(pen/2)
        if(temppen==0):
            temppen = 1

        # entity for moving - only if not a shade form
        if(pen>0):
            color = QColor(self.color)
            color.setAlpha(90)
            mybrush = QBrush(color) # int(self.opacity*255)
            painter.setBrush(mybrush)
            painter.drawRect(QRect(width-20+temppen, height-20+temppen, 20, 20))
        return

    # draw rect
    def drawRect(self, painter, x, y, width, height, pen):
        painter.drawRect(QRect(x, y, width, height))

        temppen = int(pen/2)
        if(temppen==0):
            temppen = 1

        # entity for moving - only if not a shade form
        if(pen>0):
            color = QColor(self.color)
            color.setAlpha(90)
            mybrush = QBrush(color) # int(self.opacity*255)
            painter.setBrush(mybrush)
            painter.drawRect(QRect(width-20+temppen, height-20+temppen, 20, 20))
        return

    # draw Rect bounds
    def drawRectBounds(self, painter, x, y, width, height, pen):
        boundslength = BOUNDSLENGTH

        painter.drawLine(x+int((width-boundslength)/2), y, x+int((width+boundslength)/2), y)               # top
        painter.drawLine(x+int((width-boundslength)/2), height, x+int((width+boundslength)/2), height)     # bottom

        painter.drawLine(x, int((height-boundslength)/2), x, int((height+boundslength)/2))             # left
        painter.drawLine(width, int((height-boundslength)/2), width, int((height+boundslength)/2))     # right

        temppen = int(pen/2)
        if(temppen==0):
            temppen = 1

        # entity for moving - only if not a shade form
        if(pen>0):
            color = QColor(self.color)
            color.setAlpha(90)
            mybrush = QBrush(color) # int(self.opacity*255)
            painter.setBrush(mybrush)
            painter.drawRect(QRect(width-20+temppen, height-20+temppen, 20, 20))
        else:
            painter.drawEllipse(QRect(x, y, width, height))    
        return

    # draw circle
    def drawCircle(self, painter, x, y, width, height, pen):
        painter.drawEllipse(QRect(x, y, width, height))

        # entity for moving - only if not a shade form
        if(pen>0):
            color = QColor(self.color)
            color.setAlpha(90)
            mybrush = QBrush(color) # int(self.opacity*255)
            painter.setBrush(mybrush)
            painter.drawEllipse(QRect(width-20, height-20, 20, 20))
        return

    # draw ellipse
    def drawEllipse(self, painter, x, y, width, height, pen):
        painter.drawEllipse(QRect(x, y, width, height))

        # entity for moving - only if not a shade form
        if(pen>0):
            color = QColor(self.color)
            color.setAlpha(90)
            mybrush = QBrush(color) # int(self.opacity*255)
            painter.setBrush(mybrush)
            painter.drawEllipse(QRect(width-20, height-20, 20, 20))
        return

    # sets a shape for drawing - adjust dimensions if necessary
    def setShape(self):
        self.shape = next(self.shapes)

        # adjust for square like form - center should be the same
        tempmin = min(self.width(), self.height())
        (shape, pen, pencursor) = self.shape
        if(shape==SHAPECIRCLE or shape==SHAPESQR):
            (xshift, yshift) = (int((self.width()-tempmin)/2), int((self.height()-tempmin)/2))
            self.setGeometry(self.x()+xshift, self.y()+yshift, tempmin, tempmin)

            # notify MarkerControl of the possible pos or size change
            self.emit(SIGNAL(SIGNALMOVERESIZE))
        
        # notify MarkerControl of the possible pos or size change
        self.emit(SIGNAL(SIGNALSTYLE))
        self.report("change of frame shape")
        self.update()

    # sets a shape for drawing
    def setColor(self):
        self.color = next(self.colors)
        self.report("change of frame color")
        self.update()

    # returns list of colors
    def getColorList(self):
        return self._colorslist

    # returns list of shapes
    def getShapeList(self):
        return self._shapeslist

    # returns list of movable cursor colors
    def getMoveCursorColorList(self):
        return self._cursorcolorslist

    # sets movable cursor color
    def setMoveCursorColor(self):
        self.movecursorcolor = next(self.movecursorcolors)
        self.report("change of movable cursor color")

    # processing key events
    def keyPressEvent(self, event):
        # check special keys - CTRL, ALT, SHIFT
        # fine discrimination is done in the each procedure
        key = event.key()
        modifier = event.modifiers()

        # repaint flag - collect repaint events to update only once
        brepaint = False
        
        # processing movement with large step or small step - save previous repaint event
        brepaint = self.processMovement(key, modifier) or brepaint

        # processing resize with large step or small step - save previous repaint event
        brepaint = self.processResize(key, modifier) or brepaint

        # process change of styles // color // cross - save previous repaint event
        brepaint = self.processStyle(key, modifier) or brepaint

        # collect repaint events to update only once
        if(brepaint):
            self.update()

        return QWidget().keyPressEvent(event)

    # key events - process movement
    def processMovement(self, key, modifier):
        # flag controls repaint
        brepaint = False

        # flags controlling MarkerControl gui backfeed
        bmove = False
        bmovecursor = False

        ###
        ### NO CTRL - NO SHIFT, could be ALT for small movements
        ###
        if(not (modifier & Qt.ControlModifier) and not (modifier & Qt.ShiftModifier)):
            tempstep = self.movestep
            if(modifier & Qt.AltModifier):
                tempstep = self.movestepsmall

            # setup direction
            (xdir, ydir) = (0, 0)
            if(key==Qt.Key_Up or key==Qt.Key_8):
                ydir = -tempstep
            elif(key==Qt.Key_Down or key==Qt.Key_2):
                ydir = tempstep
            elif(key==Qt.Key_Left or key==Qt.Key_4):
                xdir = -tempstep
            elif(key==Qt.Key_Right or key==Qt.Key_6):
                xdir = tempstep
            elif(key==Qt.Key_End or key==Qt.Key_1):
                (xdir, ydir) = (-tempstep, tempstep)
            elif(key==Qt.Key_PageDown or key==Qt.Key_3):
                (xdir, ydir) = (tempstep, tempstep)
            elif(key==Qt.Key_Home or key==Qt.Key_7):
                (xdir, ydir) = (-tempstep, -tempstep)
            elif(key==Qt.Key_PageUp or key==Qt.Key_9):
                (xdir, ydir) = (tempstep, -tempstep)
            # actual movement - does not require repaint event
            self.moveSelf(xdir, ydir)
            self.report("change of frame position")
            bmove = True

        # moving special movable cross - only if it is visible
        ###
        ### CTRL - NO SHIFT, possible ALT, but another requirenment - visibility
        ###
        if((modifier & Qt.ControlModifier) and not (modifier & Qt.ShiftModifier) and self.bcrossmove):
            tempstep = self.cursormovestepsmall
            if(modifier & Qt.AltModifier):
                tempstep = self.cursormovestep

            (xdir, ydir) = (0,0)
            if(key==Qt.Key_Up or key==Qt.Key_8):
                ydir = -tempstep
            elif(key==Qt.Key_Down or key==Qt.Key_2):
                ydir = tempstep
            elif(key==Qt.Key_Left or key==Qt.Key_4):
                xdir = -tempstep
            elif(key==Qt.Key_Right or key==Qt.Key_6):
                xdir = tempstep
            elif(key==Qt.Key_End or key==Qt.Key_1):
                (xdir, ydir) = (-tempstep, tempstep)
            elif(key==Qt.Key_PageDown or key==Qt.Key_3):
                (xdir, ydir) = (tempstep, tempstep)
            elif(key==Qt.Key_Home or key==Qt.Key_7):
                (xdir, ydir) = (-tempstep, -tempstep)
            elif(key==Qt.Key_PageUp or key==Qt.Key_9):
                (xdir, ydir) = (tempstep, -tempstep)

            # requires repaint
            if(xdir!=0 or ydir!=0):
                temppos = self.cursormovepos + QPoint(xdir, ydir)
                self.moveCursorGetSetPos(temppos)
                brepaint = True
                bmovecursor = True

        # flags controlling MarkerControl gui backfeed
        if(bmove):
            self.emit(SIGNAL(SIGNALMOVERESIZE))
        if(bmovecursor):
            self.emit(SIGNAL(SIGNALMOVECURSOR))
    
        return brepaint

    # key events - process movement
    def processResize(self, key, modifier):
        # flag control repaint
        brepaint = False

        # flags controlling MarkerControl gui backfeed
        bresize = False

        # ALT allows movement with small step
        if(not (modifier & Qt.ControlModifier) and (modifier & Qt.ShiftModifier)):
            tempstep = self.movestep
            if(modifier & Qt.AltModifier):
                tempstep = self.sizestepsmall
                if(tempstep==0):
                    tempstep = 1

            # setup direction - left or right
            (xdir, ydir) = (0, 0)
            # setup resize - left or right
            # right - increase width, left - decrease width
            # up - increase height, down - decrease height
            (xsiz, ysiz) = (0, 0)

            if(key==Qt.Key_Up or key==Qt.Key_8):
                ydir = self.checkDefaultInt(int(-tempstep/2), 0, -1)
                ysiz = tempstep
            elif(key==Qt.Key_Down or key==Qt.Key_2):
                ydir = self.checkDefaultInt(int(tempstep/2), 0, 1)
                ysiz = -tempstep
                # return if min size has been reached
                if(self.height()+ysiz<MINDIMENSION):
                    return
            elif(key==Qt.Key_Left or key==Qt.Key_4):
                xdir = self.checkDefaultInt(int(tempstep/2), 0, 1)
                xsiz = -tempstep
                # return if min size has been reached
                if(self.width()+xsiz<MINDIMENSION):
                    return
            elif(key==Qt.Key_Right or key==Qt.Key_6):
                xdir = self.checkDefaultInt(int(-tempstep/2), 0, -1)
                xsiz = tempstep

            # make homogenoues resize and move if needed
            (shape, pen, pencursor) = self.shape
            if(shape==SHAPESQR or shape==SHAPECIRCLE):
                tempmin = min(xsiz, ysiz)
                tempmax = max(xsiz, ysiz)
                if(tempmin == 0):               # means we move the positive way
                    ysiz = xsiz = tempmax
                    ydir = xdir = min(xdir, ydir)
                else:                           # we should move the negative way
                    ysiz = xsiz = tempmin
                    ydir =xdir = max(xdir,ydir)

            # actual movement
            # resize implies movement relative the widget center - xdir or ydir are good indicators
            if(xdir!=0 or ydir!=0):
                # use set Geometry - still flickering
                self.setGeometry(self.x()+xdir, self.y()+ydir, self.width()+xsiz, self.height()+ysiz)
                self.report("change of frame size")
                brepaint = True
                bresize = True

        # flags controlling MarkerControl gui backfeed
        if(bresize):
            self.emit(SIGNAL(SIGNALMOVERESIZE))

            # update image on resize
        return brepaint

    # check default value
    def checkDefaultInt(self, value, check, default):
        res = value
        if(value==check):
            res = default
        return res


    # external events - resize - adjust everything, size, position, update visual and gui in turn
    def processExternalResize(self, newsize):
        oldsize = self.size()
        tdir = (oldsize-newsize)/2
        (xdir, ydir) = (tdir.width(), tdir.height())

        # make homogenoues resize and move if needed
        (shape, pen, pencursor) = self.shape
        (xsiz, ysiz) = (newsize.width(), newsize.height())
        if(shape==SHAPESQR or shape==SHAPECIRCLE):
            tempmin = min(xsiz, ysiz)
            tempmax = max(xsiz, ysiz)
            if(xdir<0 or ydir<0):               # means we move the positive way
                newsize = QSize(tempmax, tempmax)
                ydir = xdir = min(xdir, ydir)
            else:                           # we should move the negative way
                newsize = QSize(tempmin, tempmin)
                ydir =xdir = max(xdir,ydir)

        if(xdir!=0 or ydir!=0):
                # move and resize for simplicity, also recommended practice
                self.report("change of frame size")
                self.move(self.x()+xdir, self.y()+ydir)
                self.resize(newsize)
                self.selectSpecificShape(self.getSetShape())
                self.emit(SIGNAL(SIGNALMOVERESIZE))
                self.update()
        return

    # key events - process change of styles // color // cross
    def processStyle(self, key, modifier):
        # flag control repaint
        brepaint = False

        # flags controlling MarkerControl gui backfeed
        bmove = False
        bmovecursor = False
        brestyle = False

        # switch between styles 
        ###
        ### NO CTRL - NO ALT - NO SHIFT
        ###
        if(not (modifier & Qt.ControlModifier) and not (modifier & Qt.ShiftModifier) and not (modifier & Qt.AltModifier)):
            # switch between frame visibility - F without CTRL - requires repaint
            if(key==Qt.Key_F):
                self.getSetVisibility(not self.bframe)
                brepaint = True
                bmove = True

            # switch between frame styles - TAB without CTRL - requires repaint
            if(key==Qt.Key_Tab):
                self.setShape()
                brepaint = True

            # adjust certain shapes - SQR
            if(key==Qt.Key_F2):
                self.selectCertainShape(SHAPESQR)
                brepaint = True

            # adjust certain shapes - Circle
            if(key==Qt.Key_F3):
                self.selectCertainShape(SHAPECIRCLE)
                brepaint = True

            # adjust certain shapes - Rect
            if(key==Qt.Key_F4):
                self.selectCertainShape(SHAPERECT)
                brepaint = True

            # adjust certain shapes - Ellipse
            if(key==Qt.Key_F5):
                self.selectCertainShape(SHAPEELLIPSE)
                brepaint = True

            # adjust certain shapes - Bounds
            if(key==Qt.Key_F6):
                self.selectCertainShape(SHAPEBOUNDS)
                brepaint = True

            # adjust certain shapes - Grid
            if(key==Qt.Key_F7):
                self.selectCertainShape(SHAPEGRID)
                brepaint = True

            # central cross visibility - requires repaint
            if(key==Qt.Key_5 or key==Qt.Key_C):
                self.getSetCursorVisibility(not self.bcross)
                brepaint = True
                bmovecursor = True

            # switch between opacity window settings - does not require repaint
            if(key==Qt.Key_Plus):
                    temp = self.opacity+OPASTEP
                    self.getSetOpacity(temp)
                    brestyle = True
            if(key==Qt.Key_Minus):
                    temp = self.opacity-OPASTEP
                    self.getSetOpacity(temp)
                    brestyle = True
        ###
        ### CTRL - NO ALT - NO SHIFT
        ###
        elif((modifier & Qt.ControlModifier) and not (modifier & Qt.ShiftModifier) and not (modifier & Qt.AltModifier)):
            # switch between frame colors with CTRL TAB- requires repaint
            if(key==Qt.Key_Tab):
                self.setColor()
                brepaint = True
                brestyle = True

            # set movable cross - requires repaint
            if(key==Qt.Key_5 or key==Qt.Key_C):
                self.moveCursorGetSetVisibility(not self.bcrossmove)
                brepaint = True
                bmovecursor = True
        ###
        ### NO CTRL - NO ALT - SHIFT
        ###
        elif(not (modifier & Qt.ControlModifier) and (modifier & Qt.ShiftModifier) and not (modifier & Qt.AltModifier)):  # switch between colors with CTRL - requires repaint
            # switch between movable cursor colors with SHIFT TAB - requires repaint
            if(key==Qt.Key_C and self.bcrossmove):
                self.setMoveCursorColor()
                brepaint = True
                brestyle = True

        # flags controlling MarkerControl gui backfeed
        if(bmove):
            self.emit(SIGNAL(SIGNALMOVERESIZE))
        if(bmovecursor):
            self.emit(SIGNAL(SIGNALMOVECURSOR))
        if(brestyle):
            self.emit(SIGNAL(SIGNALSTYLE))

        return brepaint

    # move window by a small increment
    def moveSelf(self, xdir, ydir):
        curpos = self.pos()
        movepos = QPoint(xdir, ydir)
        self.move(curpos+movepos)

    # resize window by a small increment
    def resizeSelf(self, xsize, ysize):
        size =  QSize(self.width(), self.height())+QSize(xsize, ysize)
        self.resize(size)

    # select certain shape so, that the shape class is the same
    def selectCertainShape(self, shape):
        while(self.shape[0]!=shape):
            self.setShape()

    # select specific shape so, that all parameters are the same
    def selectSpecificShape(self, shape):
        while(tuple(self.shape)!=tuple(shape)):
            self.setShape()

    # select specific marker frame color
    # pay attention to passing values in python by ref or by value
    # part with changing color's alpha could be affected
    def selectSpecificColor(self, color):
        while(self.color!=color):
            #print("current %i:%i:%i:%i, set: %i:%i:%i:%i"%(self.color.red(), self.color.blue(), self.color.green(),self.color.alpha(), color.red(), color.blue(), color.green(), color.alpha()))
            #print(self.color == color)
            self.setColor()

    #
    def selectMoveCursorSpecificColor(self, color):
        while(self.movecursorcolor!=color):
            #print("current %i:%i:%i:%i, set: %i:%i:%i:%i"%(self.color.red(), self.color.blue(), self.color.green(),self.color.alpha(), color.red(), color.blue(), color.green(), color.alpha()))
            #print(self.color == color)
            self.setMoveCursorColor()

    # closing window event
    def closeEvent(self, event):
        if(not self._bclose):
            event.ignore()
        else:
            event.accept()
        return

    # closing marker window
    def setClose(self):
        self._bclose = True
        self.close()

###
##  Marker end
###

###
### Widget for gui control of the markers
###

class MarkerControl(QMainWindow):
    def __init__(self, app, parent=None):
        super(MarkerControl, self).__init__(parent)

        # init variables
        self.initVariables(app)

        # init gui
        self.initSelf()

        # init gui special events, not part of the Tab processing
        self.initEvents()

        self.show()
        self.marker.setFocus()
        return

    # init gui
    def initSelf(self):
        # set window title
        self.title = "Marker Control"
        self.setWindowTitle(self.title)

        # set status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        #main widget - tabulated widget
        self.tab = QTabWidget()
        self.tab.setTabPosition(QTabWidget.South)

        self.createMarkerTab(self.tab)
        self.updateMarkerTab()
        self.createMarkerResizeTab(self.tab)
        self.updateMarkerResizeTab()
        self.createCursorTab(self.tab)
        self.updateCursorTab()
        self.createStyleTab(self.tab)
        self.updateStyleTab()
        self.createGridTab(self.tab)
        self.updateGridTab()
        self.createCalibrationTab(self.tab)
        self.updateCalibrationTab()

        self.setCentralWidget(self.tab)

        # window on top
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        return

    # init variables
    def initVariables(self, app):
        # save application
        self._app = app

        # initialize organization name and program name
        self._app.setOrganizationName(ORGNAME)
        self._app.setOrganizationDomain(ORGDOMAIN)
        self._app.setApplicationName(PROGNAME)

        # initialize settings
        self.settings = QSettings()

        # create marker window
        self.marker = MarkerCanvas(self._app)

        # variable to store overlay
        self.overlay = None

        # screen distance used in calibration
        self.scrdistance = 1
        self.objdistance = 1

        # use QSettings mechanism to initialize certain values
        self.readSettings()

        # used for detection of gui input fields changes
        self.resetInputchange()

        return

    # marker tab
    def createMarkerTab(self, tab):
        title = "Marker Position"

        # general elements
        wdgt = QWidget()
        grid = QGridLayout()

        # create general layout
        tgroup = QGroupBox("Position and size")
        bgroup = QGroupBox("Movement step size")
        rgroup = QGroupBox("Marker movement control")
        grid.addWidget(tgroup, 0, 0)
        grid.addWidget(bgroup, 1, 0)
        grid.addWidget(rgroup, 0, 1, 0, 1)
        grid.setColumnStretch(1, 50)
        #grid.setRowStretch(2, 50)

        # position group - top
        tgrid = QGridLayout()
        tgrid.addWidget(QLabel("x:"), 0, 0)
        tgrid.addWidget(QLabel("y:"), 1, 0)
        tgrid.addWidget(QLabel("width:"), 2, 0)
        tgrid.addWidget(QLabel("height:"), 3, 0)

        self.lexmarker = QLineEdit("")
        self.leymarker = QLineEdit("")
        self.lewidthmarker = QLineEdit("")
        self.leheightmarker = QLineEdit("")
        tgrid.addWidget(self.lexmarker, 0, 1)
        tgrid.addWidget(self.leymarker, 1, 1)
        tgrid.addWidget(self.lewidthmarker, 2, 1)
        tgrid.addWidget(self.leheightmarker, 3, 1)
        self.cbvframe = QCheckBox("frame visibility")
        self.setCheckedFromBool(self.cbvframe, self.marker.getSetVisibility())
        tgrid.addWidget(self.cbvframe, 4, 1, 1, 1, Qt.AlignLeft)
        tgrid.setRowStretch(5, 50)
        tgroup.setLayout(tgrid)

        # position group - bottom
        bgrid = QGridLayout()
        bgrid.addWidget(QLabel("large step:"), 0, 0)
        bgrid.addWidget(QLabel("small step:"), 1, 0)
        self.lelstepmarker = QLineEdit("")
        self.lesstepmarker = QLineEdit("")
        self.cmblstepmarker = self.createSpecComboBox("step", 5, 10, 20, 30, 40, 50, 100)
        self.cmbsstepmarker = self.createSpecComboBox("step", 1,2,4,5,10)
        bgrid.addWidget(self.lelstepmarker, 0, 1)
        bgrid.addWidget(self.lesstepmarker, 1, 1)
        bgrid.addWidget(self.cmblstepmarker, 0, 2)
        bgrid.addWidget(self.cmbsstepmarker, 1, 2)
        bgrid.setColumnStretch(1, 50)
        bgroup.setLayout(bgrid)

        # movement group - right
        rgrid = QGridLayout()
        self.btnmarktoplarge = MPushButton(BTNLARGEUP)
        self.btnmarkbottomlarge = MPushButton(BTNLARGEDOWN)
        self.btnmarkleftlarge = MPushButton(BTNLARGELEFT)
        self.btnmarkrightlarge = MPushButton(BTNLARGERIGHT)
        self.btnmarktopsmall = MPushButton(BTNSMALLUP)
        self.btnmarkbottomsmall = MPushButton(BTNSMALLDOWN)
        self.btnmarkleftsmall = MPushButton(BTNSMALLLEFT)
        self.btnmarkrightsmall = MPushButton(BTNSMALLRIGHT)
        rgrid.addWidget(self.btnmarktoplarge, 0, 2)
        rgrid.addWidget(self.btnmarktopsmall, 1, 2, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btnmarkleftlarge, 2, 0)
        rgrid.addWidget(self.btnmarkleftsmall, 2, 1, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btnmarkrightsmall, 2, 4, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btnmarkrightlarge, 2, 5)
        rgrid.addWidget(self.btnmarkbottomsmall, 3, 2, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btnmarkbottomlarge, 4, 2)
        self.resizeWidgetsSeq(QSize(40,40), self.btnmarktoplarge, self.btnmarkleftlarge, self.btnmarkrightlarge, self.btnmarkbottomlarge)
        self.resizeWidgetsSeq(QSize(35,35), self.btnmarktopsmall, self.btnmarkbottomsmall)
        self.resizeWidgetsSeq(QSize(35,35), self.btnmarkleftsmall, self.btnmarkrightsmall)
        rgroup.setLayout(rgrid)

        # adjusting the input parameters for text fields
        # make ajustemnt of QLineEdit input values
        self.setIntValidator((self.lexmarker, self.leymarker))
        self.setIntValidator((self.lelstepmarker, self.lesstepmarker), 1)
        self.setIntValidator((self.lewidthmarker, self.leheightmarker), 0)

        # assigning signals and slots in sequence
        self.connectSeq((self.lexmarker, self.leymarker, self.lewidthmarker, self.leheightmarker, self.lelstepmarker, self.lesstepmarker), SIGNAL("textEdited(const QString&)"), self.setInputChange)
        self.connectSeq((self.lexmarker, self.leymarker, self.lewidthmarker, self.leheightmarker, self.lelstepmarker, self.lesstepmarker), SIGNAL("editingFinished()"), self.updateMarker)
        self.connectSeq((self.lexmarker, self.leymarker, self.lewidthmarker, self.leheightmarker, self.lelstepmarker, self.lesstepmarker), SIGNAL("returnPressed()"), self.updateMarker)
        self.connectSeq((self.cbvframe), SIGNAL("stateChanged(int)"), self.setInputChange)
        self.connectSeq((self.cbvframe), SIGNAL("stateChanged(int)"), self.updateMarker)
        self.connectSeq((self.cmblstepmarker, self.cmbsstepmarker), SIGNAL("currentIndexChanged(int)"), self.setInputChange)
        self.connectSeq((self.cmblstepmarker, self.cmbsstepmarker), SIGNAL("currentIndexChanged(int)"), self.updateMarker)

        # assigning button actions - the idea just to forward key actions to the marker window
            # large step - in principle I pass small step flag for redundance and future possible actions, so far it is modifier which matters
            # wdgt, operation and step flag are passed for redundancy, not needed now
            # marker operates different from cursor. for general purpose we use large step instead of small
        self.createBtnAction(self.btnmarktoplarge, BTNSMARKERMOVE, BTNLARGESTEP, Qt.Key_Up, Qt.NoModifier)
        self.createBtnAction(self.btnmarkbottomlarge, BTNSMARKERMOVE, BTNLARGESTEP, Qt.Key_Down, Qt.NoModifier)
        self.createBtnAction(self.btnmarkleftlarge, BTNSMARKERMOVE, BTNLARGESTEP, Qt.Key_Left, Qt.NoModifier)
        self.createBtnAction(self.btnmarkrightlarge, BTNSMARKERMOVE, BTNLARGESTEP, Qt.Key_Right, Qt.NoModifier)
            # small step
            # wdgt, operation and step flag are passed for redundancy, not needed now
        self.createBtnAction(self.btnmarktopsmall, BTNSMARKERMOVE, BTNSMALLSTEP, Qt.Key_Up, Qt.AltModifier)
        self.createBtnAction(self.btnmarkbottomsmall, BTNSMARKERMOVE, BTNSMALLSTEP, Qt.Key_Down, Qt.AltModifier)
        self.createBtnAction(self.btnmarkleftsmall, BTNSMARKERMOVE, BTNSMALLSTEP, Qt.Key_Left, Qt.AltModifier)
        self.createBtnAction(self.btnmarkrightsmall, BTNSMARKERMOVE, BTNSMALLSTEP, Qt.Key_Right, Qt.AltModifier)

        # adding tab
        wdgt.setLayout(grid)
        tab.addTab(wdgt, title)
        return

    # marker resize tab
    def createMarkerResizeTab(self, tab):
        title = "Marker Size"

        # general elements
        wdgt = QWidget()
        grid = QGridLayout()

        # create general layout
        tgroup = QGroupBox("Resize step")
        rgroup = QGroupBox("Marker resize control")
        grid.addWidget(tgroup, 0, 0)
        grid.addWidget(rgroup, 0, 1, 0, 1)
        grid.setColumnStretch(1, 50)
        #grid.setRowStretch(1, 50)

        # position group - top
        tgrid = QGridLayout()
        tgrid.addWidget(QLabel("large step:"), 0, 0)
        tgrid.addWidget(QLabel("small step:"), 1, 0)
        self.lelsresizemarker = QLineEdit("")
        self.lessresizemarker = QLineEdit("")
        self.cmblstepmarkerresize = self.createSpecComboBox("step", 5, 10, 20, 30, 40, 50, 100)
        self.cmbsstepmarkerresize = self.createSpecComboBox("step", 2,3,4,5,10)
        tgrid.addWidget(self.lelsresizemarker, 0, 1)
        tgrid.addWidget(self.lessresizemarker, 1, 1)
        tgrid.addWidget(self.cmblstepmarkerresize, 0, 2)
        tgrid.addWidget(self.cmbsstepmarkerresize, 1, 2)
        tgrid.setRowStretch(2, 50)
        tgroup.setLayout(tgrid)

        # resize group - right
        rgrid = QGridLayout()
        self.btnmarktoplargeresize = MPushButton(BTNLARGEUP)
        self.btnmarkbottomlargeresize = MPushButton(BTNLARGEDOWN)
        self.btnmarkleftlargeresize = MPushButton(BTNLARGELEFT)
        self.btnmarkrightlargeresize = MPushButton(BTNLARGERIGHT)
        self.btnmarktopsmallresize = MPushButton(BTNSMALLUP)
        self.btnmarkbottomsmallresize = MPushButton(BTNSMALLDOWN)
        self.btnmarkleftsmallresize = MPushButton(BTNSMALLLEFT)
        self.btnmarkrightsmallresize = MPushButton(BTNSMALLRIGHT)
        rgrid.addWidget(self.btnmarktoplargeresize, 0, 2)
        rgrid.addWidget(self.btnmarktopsmallresize, 1, 2, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btnmarkleftlargeresize, 2, 0)
        rgrid.addWidget(self.btnmarkleftsmallresize, 2, 1, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btnmarkrightsmallresize, 2, 4, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btnmarkrightlargeresize, 2, 5)
        rgrid.addWidget(self.btnmarkbottomsmallresize, 3, 2, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btnmarkbottomlargeresize, 4, 2)
        self.resizeWidgetsSeq(QSize(40,40), self.btnmarktoplargeresize, self.btnmarkleftlargeresize, self.btnmarkrightlargeresize, self.btnmarkbottomlargeresize)
        self.resizeWidgetsSeq(QSize(35,35), self.btnmarktopsmallresize, self.btnmarkbottomsmallresize)
        self.resizeWidgetsSeq(QSize(35,35), self.btnmarkleftsmallresize, self.btnmarkrightsmallresize)
        rgroup.setLayout(rgrid)

        # adjusting the input parameters for text fields
        # make ajustemnt of QLineEdit input values
        self.setIntValidator((self.lelsresizemarker, self.lessresizemarker), 0)

        # assigning signals and slots in sequence
        self.connectSeq((self.lelsresizemarker, self.lessresizemarker), SIGNAL("textEdited(const QString&)"), self.setInputChange)
        self.connectSeq((self.lelsresizemarker, self.lessresizemarker), SIGNAL("editingFinished()"), self.updateMarkerResize)
        self.connectSeq((self.lelsresizemarker, self.lessresizemarker), SIGNAL("returnPressed()"), self.updateMarkerResize)
        self.connectSeq((self.cmblstepmarkerresize, self.cmbsstepmarkerresize), SIGNAL("currentIndexChanged(int)"), self.setInputChange)
        self.connectSeq((self.cmblstepmarkerresize, self.cmbsstepmarkerresize), SIGNAL("currentIndexChanged(int)"), self.updateMarkerResize)

        # assigning button actions - the idea just to forward key actions to the marker window
            # large step - in principle I pass small step flag for redundance and future possible actions, so far it is modifier which matters
            # wdgt, operation and step flag are passed for redundancy, not needed now
            # marker operates different from cursor. for general purpose we use large step instead of small
        self.createBtnAction(self.btnmarktoplargeresize, BTNSMARKERRESIZE, BTNLARGESTEP, Qt.Key_Up, Qt.ShiftModifier)
        self.createBtnAction(self.btnmarkbottomlargeresize, BTNSMARKERRESIZE, BTNLARGESTEP, Qt.Key_Down, Qt.ShiftModifier)
        self.createBtnAction(self.btnmarkleftlargeresize, BTNSMARKERRESIZE, BTNLARGESTEP, Qt.Key_Left, Qt.ShiftModifier)
        self.createBtnAction(self.btnmarkrightlargeresize, BTNSMARKERRESIZE, BTNLARGESTEP, Qt.Key_Right, Qt.ShiftModifier)
            # small step
            # wdgt, operation and step flag are passed for redundancy, not needed now
        self.createBtnAction(self.btnmarktopsmallresize, BTNSMARKERRESIZE, BTNSMALLSTEP, Qt.Key_Up, Qt.AltModifier|Qt.ShiftModifier)
        self.createBtnAction(self.btnmarkbottomsmallresize, BTNSMARKERRESIZE, BTNSMALLSTEP, Qt.Key_Down, Qt.AltModifier|Qt.ShiftModifier)
        self.createBtnAction(self.btnmarkleftsmallresize, BTNSMARKERRESIZE, BTNSMALLSTEP, Qt.Key_Left, Qt.AltModifier|Qt.ShiftModifier)
        self.createBtnAction(self.btnmarkrightsmallresize, BTNSMARKERRESIZE, BTNSMALLSTEP, Qt.Key_Right, Qt.AltModifier|Qt.ShiftModifier)

        # adding tab
        wdgt.setLayout(grid)
        tab.addTab(wdgt, title)
        return

    # create tab with controls for cross
    def createCursorTab(self, tab):
        title = "Cursor Position"

        # general elements
        wdgt = QWidget()
        grid = QGridLayout()

        # main groups for arrangement
        tgroup = QGroupBox("Position and visibility")
        bgroup = QGroupBox("Movement step size")
        rgroup = QGroupBox("Cursor movement control")

        grid.addWidget(tgroup, 0, 0)
        grid.addWidget(bgroup, 1, 0)
        grid.addWidget(rgroup, 0, 1, 0, 1)
        grid.setColumnStretch(1, 50)
        #grid.setRowStretch(2, 50)


        # top group - position (relative to the center of Marker) and visibility
        tgrid = QGridLayout()
        tgrid.addWidget(QLabel("x:"), 0,0)
        tgrid.addWidget(QLabel("y:"), 1,0)
        self.lexcursor = QLineEdit("")
        self.leycursor = QLineEdit("")
        tgrid.addWidget(self.lexcursor, 0, 1)
        tgrid.addWidget(self.leycursor, 1, 1)
        self.cbvcursormove = QCheckBox("movable cursor visibility")
        self.cbvcursor = QCheckBox("main cursor visibility")
        self.setCheckedFromBool(self.cbvcursormove, self.marker.moveCursorGetSetVisibility())
        self.setCheckedFromBool(self.cbvcursor, self.marker.getSetCursorVisibility())
        tgrid.addWidget(self.cbvcursormove, 2, 1, 1, 1, Qt.AlignLeft)
        tgrid.addWidget(self.cbvcursor, 3, 1, 1, 1, Qt.AlignLeft)
        tgrid.setRowStretch(4, 50)
        tgroup.setLayout(tgrid)

        # position group - bottom
        bgrid = QGridLayout()
        bgrid.addWidget(QLabel("large step:"), 0, 0)
        bgrid.addWidget(QLabel("small step:"), 1, 0)
        self.lelstepcursor = QLineEdit("")
        self.lesstepcursor = QLineEdit("")
        self.cmblstepcursor = self.createSpecComboBox("step", 5, 10, 20, 30, 40, 50, 100)
        self.cmbsstepcursor = self.createSpecComboBox("step", 1,2,4,5,10)
        bgrid.addWidget(self.lelstepcursor, 0, 1)
        bgrid.addWidget(self.lesstepcursor, 1, 1)
        bgrid.addWidget(self.cmblstepcursor, 0, 2)
        bgrid.addWidget(self.cmbsstepcursor, 1, 2)
        bgrid.setColumnStretch(1, 50)
        bgroup.setLayout(bgrid)

         # movement group - right
        rgrid = QGridLayout()
        self.btncurstoplarge = MPushButton(BTNLARGEUP)
        self.btncursbottomlarge = MPushButton(BTNLARGEDOWN)
        self.btncursleftlarge = MPushButton(BTNLARGELEFT)
        self.btncursrightlarge = MPushButton(BTNLARGERIGHT)
        self.btncurstopsmall = MPushButton(BTNSMALLUP)
        self.btncursbottomsmall = MPushButton(BTNSMALLDOWN)
        self.btncursleftsmall = MPushButton(BTNSMALLLEFT)
        self.btncursrightsmall = MPushButton(BTNSMALLRIGHT)
        rgrid.addWidget(self.btncurstoplarge, 0, 2)
        rgrid.addWidget(self.btncurstopsmall, 1, 2, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btncursleftlarge, 2, 0)
        rgrid.addWidget(self.btncursleftsmall, 2, 1, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btncursrightsmall, 2, 4, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btncursrightlarge, 2, 5)
        rgrid.addWidget(self.btncursbottomsmall, 3, 2, 1, 1, Qt.AlignCenter)
        rgrid.addWidget(self.btncursbottomlarge, 4, 2)
        self.resizeWidgetsSeq(QSize(40,40), self.btncurstoplarge, self.btncursleftlarge, self.btncursrightlarge, self.btncursbottomlarge)
        self.resizeWidgetsSeq(QSize(35,35), self.btncurstopsmall, self.btncursbottomsmall)
        self.resizeWidgetsSeq(QSize(35,35), self.btncursleftsmall, self.btncursrightsmall)
        rgroup.setLayout(rgrid)

        # set validators
        self.setIntValidator((self.lexcursor, self.leycursor))
        self.setIntValidator((self.lelstepcursor, self.lesstepcursor), 1)

        # assigning signals and slots in sequence
        self.connectSeq((self.lexcursor, self.leycursor, self.lelstepcursor, self.lesstepcursor), SIGNAL("textEdited(const QString&)"), self.setInputChange)
        self.connectSeq((self.lexcursor, self.leycursor, self.lelstepcursor, self.lesstepcursor), SIGNAL("editingFinished()"), self.updateCursor)
        self.connectSeq((self.lexcursor, self.leycursor, self.lelstepcursor, self.lesstepcursor), SIGNAL("returnPressed()"), self.updateCursor)
        self.connectSeq((self.cbvcursormove, self.cbvcursor), SIGNAL("stateChanged(int)"), self.setInputChange)
        self.connectSeq((self.cbvcursormove, self.cbvcursor), SIGNAL("stateChanged(int)"), self.updateCursor)
        self.connectSeq((self.cmblstepcursor, self.cmbsstepcursor), SIGNAL("currentIndexChanged(int)"), self.setInputChange)
        self.connectSeq((self.cmblstepcursor, self.cmbsstepcursor), SIGNAL("currentIndexChanged(int)"), self.updateCursor)

        # assigning button actions - the idea just to forward key actions to the marker window
            # large step - in principle I pass small step flag for redundance and future possible actions, so far it is modifier which matters
            # wdgt, operation and step flag are passed for redundancy, not needed now
            # cursor operates different from marker resize and move. for general purpose we use small step instead of large
        self.createBtnAction(self.btncurstoplarge, BTNSMOVECURSOR, BTNLARGESTEP, Qt.Key_Up, Qt.AltModifier|Qt.ControlModifier)
        self.createBtnAction(self.btncursbottomlarge, BTNSMOVECURSOR, BTNLARGESTEP, Qt.Key_Down, Qt.AltModifier|Qt.ControlModifier)
        self.createBtnAction(self.btncursleftlarge, BTNSMOVECURSOR, BTNLARGESTEP, Qt.Key_Left, Qt.AltModifier|Qt.ControlModifier)
        self.createBtnAction(self.btncursrightlarge, BTNSMOVECURSOR, BTNLARGESTEP, Qt.Key_Right, Qt.AltModifier|Qt.ControlModifier)
            # small step
            # wdgt, operation and step flag are passed for redundancy, not needed now
        self.createBtnAction(self.btncurstopsmall, BTNSMOVECURSOR, BTNSMALLSTEP, Qt.Key_Up, Qt.ControlModifier)
        self.createBtnAction(self.btncursbottomsmall, BTNSMOVECURSOR, BTNSMALLSTEP, Qt.Key_Down, Qt.ControlModifier)
        self.createBtnAction(self.btncursleftsmall, BTNSMOVECURSOR, BTNSMALLSTEP, Qt.Key_Left, Qt.ControlModifier)
        self.createBtnAction(self.btncursrightsmall, BTNSMOVECURSOR, BTNSMALLSTEP, Qt.Key_Right, Qt.ControlModifier)

        wdgt.setLayout(grid)
        tab.addTab(wdgt, title)
        return

    # create tab with controls for style - cross and frame
    def createStyleTab(self, tab):
        title = "Style"

        # general elements
        wdgt = QWidget()
        grid = QGridLayout()

        # main grouping objects
        lgroup = QGroupBox("Frame style")
        rgroup = QGroupBox("Movable cursor style")
        grid.addWidget(lgroup, 0, 0)
        grid.addWidget(rgroup, 0, 1)

        # left group - frame style
        lgrid = QGridLayout()
        self.cmbframeshape = QComboBox()
        self.createCMBFrameShapes()
        self.cmbframecolor = QComboBox()
        self.createCMBFrameColors()
        self.cmbframecolor.setIconSize(QSize(QICONW,QICONH))
        self.sbframeopacity = QDoubleSpinBox()
        self.sbframeopacity.setMinimum(OPAMINIMUM)
        self.sbframeopacity.setMaximum(OPAMAXIMUM)
        self.sbframeopacity.setSingleStep(0.1)
        self.sbframeopacity.setSuffix(QString(""))
        lgrid.addWidget(QLabel("frame shape:"), 0, 0)
        lgrid.addWidget(self.cmbframeshape, 0, 1)
        lgrid.addWidget(QLabel("frame color:"), 1, 0)
        lgrid.addWidget(self.cmbframecolor, 1, 1)
        lgrid.addWidget(QLabel("marker opacity:"), 2, 0)
        lgrid.addWidget(self.sbframeopacity, 2, 1)
        lgrid.setRowStretch(3, 50)
        lgroup.setLayout(lgrid)

        # right group - frame style
        rgrid = QGridLayout()
        self.cmbcursorshape = QComboBox()
        self.cmbcursorcolor = QComboBox()
        self.createCMBMovableCursorColors()
        self.cmbcursorcolor.setIconSize(QSize(QICONW,QICONH))
        #rgrid.addWidget(QLabel("Cursor shape"), 0, 0)
        #rgrid.addWidget(self.cmbcursorshape, 0, 1)
        rgrid.addWidget(QLabel("Cursor color:"), 1, 0)
        rgrid.addWidget(self.cmbcursorcolor, 1, 1)
        rgrid.setRowStretch(2, 50)
        rgroup.setLayout(rgrid)

            # assign signal and slots
            # here I have to stick to a different approach - through lambda functions
        # frame color
        func_callback = lambda what="", who=self.cmbframecolor : self.updateStyle(what, who)
        self.connect(self.cmbframecolor, SIGNAL("currentIndexChanged(int)"), func_callback)
        # frame shape
        func_callback = lambda what="", who=self.cmbframeshape : self.updateStyle(what, who)
        self.connect(self.cmbframeshape, SIGNAL("currentIndexChanged(int)"), func_callback)
        # cursor color
        func_callback = lambda what="", who=self.cmbcursorcolor : self.updateStyle(what, who)
        self.connect(self.cmbcursorcolor, SIGNAL("currentIndexChanged(int)"), func_callback)
        # marker window opacity change
        func_callback = lambda what="", who=self.sbframeopacity : self.updateStyle(what, who)
        self.connect(self.sbframeopacity, SIGNAL("valueChanged(double)"), func_callback)

        wdgt.setLayout(grid)
        tab.addTab(wdgt, title)
        return

    # grid control Tab
    def createGridTab(self, tab):
        title = "Grid"

        # general elements
        wdgt = QWidget()
        grid = QGridLayout()

        # main grouping objects
        lgroup = QGroupBox("Grid parameters")
        grid.addWidget(lgroup, 0, 0)

        # left group - grid parameters
        lgrid = QGridLayout()
        self.sbgridunit = QSpinBox()
        self.sbgridunit.setSuffix(" px")
        self.sbgridunit.setMinimum(GRIDUNITMIN)
        self.sbgridunit.setMaximum(GRIDUNITMAX)
        lgrid.addWidget(QLabel("small unit step:"), 0, 0)
        lgrid.addWidget(self.sbgridunit, 0, 1)
        lgrid.setRowStretch(1, 50)
        lgroup.setLayout(lgrid)

        # update grid unit - the only thing to change is the spin box now
        self.connect(self.sbgridunit, SIGNAL("valueChanged(const QString&)"), self.setInputChange)
        self.connect(self.sbgridunit, SIGNAL("valueChanged(const QString&)"), self.updateGrid)

        wdgt.setLayout(grid)
        tab.addTab(wdgt, title)
        return

    # calibration tab
    def createCalibrationTab(self, tab):
        title = "Calibration"

        # general elements
        wdgt = QWidget()
        grid = QGridLayout()

        # main grouping objects
        tgroup = QGroupBox("Calibration control")
        bgroup = QGroupBox("Calibration parameters")
        rgroup = QGroupBox("Calibrated distances")
        rbgroup = QGroupBox("Cursor to cursor (raw distances in px)")

        grid.addWidget(tgroup, 0, 0)
        grid.addWidget(bgroup, 1, 0)
        grid.addWidget(rbgroup, 1, 1)
        grid.setRowStretch(1, 50)
        grid.addWidget(rgroup, 0, 1, 1, 2)

        # top group - calibration start
        tgrid = QGridLayout()
        self.btncalibration = QPushButton("Measure screen distance (px)")
        tgrid.addWidget(self.btncalibration, 0, 0)
        tgrid.setRowStretch(1, 50)
        tgroup.setLayout(tgrid)

        # bottom group - calibration parameters
        bgrid = QGridLayout()
        self.ledistscreen = QLineEdit()
        self.ledistscreen.setText(self.floatStringSeq(self.scrdistance))
        self.ledistobj = QLineEdit()
        self.ledistobj.setText(self.floatStringSeq(self.objdistance))
        bgrid.addWidget(QLabel("screen distance:"), 0, 0)
        bgrid.addWidget(self.ledistscreen, 0, 1)
        bgrid.addWidget(QLabel("real (object) distance:"), 1, 0)
        bgrid.addWidget(self.ledistobj, 1, 1)
        bgrid.setRowStretch(2, 50)
        bgroup.setLayout(bgrid)

        # right group - measured distances
        rgrid = QGridLayout()
        self.lecwidth = QLineEdit()
        self.lecheight = QLineEdit()
        self.leccursorcursor = QLineEdit()
        self.leccursorx = QLineEdit()
        self.leccursory = QLineEdit()
        self.setWidgetsDisable(True, self.lecwidth, self.lecheight, self.leccursorcursor, self.leccursorx, self.leccursory)
        rgrid.addWidget(QLabel("marker width:"), 0, 0)
        rgrid.addWidget(self.lecwidth, 0, 1)
        rgrid.addWidget(QLabel("marker height:"), 1, 0)
        rgrid.addWidget(self.lecheight, 1, 1)
        rgrid.addWidget(QLabel("curs.-curs. distance:"), 2, 0)
        rgrid.addWidget(self.leccursorcursor, 2, 1)
        rgrid.addWidget(QLabel("curs.-curs. along x:"), 3, 0)
        rgrid.addWidget(self.leccursorx, 3, 1)
        rgrid.addWidget(QLabel("curs.-curs. along y:"), 4, 0)
        rgrid.addWidget(self.leccursory, 4, 1)

        # right bottom group - raw, not calibrated distanced
        rbgrid = QGridLayout()
        self.lecursorcursor = QLineEdit()
        self.lecursorx = QLineEdit()
        self.lecursory = QLineEdit()
        self.setWidgetsDisable(True, self.lecursorcursor, self.lecursorx, self.lecursory)
        rbgrid.addWidget(QLabel("curs.-curs. distance:"), 0, 0)
        rbgrid.addWidget(self.lecursorcursor, 0, 1)
        rbgrid.addWidget(QLabel("curs.-curs. along x:"), 1, 0)
        rbgrid.addWidget(self.lecursorx, 1, 1)
        rbgrid.addWidget(QLabel("curs.-curs. along y:"), 2, 0)
        rbgrid.addWidget(self.lecursory, 2, 1)
        rbgroup.setLayout(rbgrid)

        rgrid.setRowStretch(3, 50)
        rgroup.setLayout(rgrid)

        # make constraints on calibration
        self.setFloatValidator((self.ledistscreen, self.ledistobj))

        # assign signals and slots
        self.connectSeq((self.ledistscreen, self.ledistobj), SIGNAL("textChanged(const QString&)"), self.updateCalibrationTab)
        self.connectSeq((self.ledistscreen, self.ledistobj), SIGNAL("returnPressed()"), self.updateCalibrationTab)

        # assign bnt click event
        self.connect(self.btncalibration, SIGNAL("clicked()"), self.btnStartCalibration)

        wdgt.setLayout(grid)
        tab.addTab(wdgt, title)

    # track btn action centralized - for all tabs
    # wdgt, operation and step flag are passed for redundancy, not needed now
    def trackBtnAction(self, wdgt, operation, stepflag, key, modifier):
        kevent = QKeyEvent(QEvent.KeyPress, key, modifier)
        self.marker.keyPressEvent(kevent)

        # touble shooting
        if(operation==BTNSMOVECURSOR and not self.marker.moveCursorGetSetVisibility()):
            self.showShortMsg("Attention: movable cursor is not visible - there will be no movement")
        return

    # create btn action for clicked() signal - one type
    # wdgt, operation and step flag are passed for redundancy, not needed now
    def createBtnAction(self, wdgt, operation, stepflag, key, modifier):
        func_callback = lambda w=wdgt, o=operation, s=stepflag, k=key, m=modifier, : self.trackBtnAction(w, o, s, k, m)
        self.connect(wdgt, SIGNAL("clicked()"), func_callback)

    # create large step combobox - default movement settings
    def createSpecComboBox(self, *tlist):
        # widget created
        wdgt = QComboBox()
         # check if we submit list or tuple 
        if(type(tlist[0])==type(tuple()) or type(tlist[0])==type(list())):
            tlist = tlist[0]
        
        # walk through the values, adjust type if needed 
        for v in tlist:
            format = "%s"
            val = QVariant("")
            if(type(v)==type(int())):
                format = "%s"
                val = QVariant(int(v))
            wdgt.addItem(format%v, val)
        return wdgt

    # resize widgets by list to certain size
    def resizeWidgetsSeq(self, size, *tlist):
        # check if we submit list or tuple 
        if(type(tlist[0])==type(tuple()) or type(tlist[0])==type(list())):
            tlist = tlist[0]
        for wdgt in tlist:
            wdgt.setMinimumWidth(size.width())
            wdgt.setMinimumHeight(size.height())
            wdgt.setMaximumWidth(size.width())
            wdgt.setMaximumHeight(size.height())

    # disable/enable widgets in a sequence - for simplicity 
    def setWidgetsDisable(self, flag, *tlist):
        if(type(tlist[0])==type(tuple()) or type(tlist[0])==type(list())):
            tlist = tlist[0]

        for wdgt in tlist:
            wdgt.setDisabled(flag)

    # initialize specific events
    def initEvents(self):
        # events driven from marker side - make the tabs update by themselves
        # marker - move resize event - affects MArker tab and Calibration tab
        self.connect(self.marker, SIGNAL(SIGNALMOVERESIZE), self.updateMarkerTab)
        self.connect(self.marker, SIGNAL(SIGNALMOVERESIZE), self.updateCalibrationTab)

        # movable cursor - move event - affects Cursor tab and Calibration tab
        self.connect(self.marker, SIGNAL(SIGNALMOVECURSOR), self.updateCursorTab)
        self.connect(self.marker, SIGNAL(SIGNALMOVECURSOR), self.updateCalibrationTab)

        # style change event - affects Style tab
        self.connect(self.marker, SIGNAL(SIGNALSTYLE), self.updateStyleTab)

        # report changes 
        self.connect(self.marker, SIGNAL(SIGNALREPORT), self.showShortMsg)
        self.connect(self, SIGNAL(SIGNALREPORT), self.showShortMsg)

    # event happening on close
    def closeEvent(self, event):
        # close marker window
        self.marker.setClose()

        # save settings using QSettings mechanism
        self.writeSettings()
        return

    # settings on start - read
    def readSettings(self):
        #self.settings.clear()
        # main window properties - position, size
        self.settings.beginGroup(SETMWGROUP)
        value = self.settings.value(SETPOS, QPoint(200, 200))
        if(type(value)!=type(QPoint())):
            value = value.toPoint()
        self.move(value)

        value = self.settings.value(SETSIZE, QSize(400, 300))
        if(type(value)!=type(QSize())):
            value = value.toSize()
        self.resize(value)
        self.settings.endGroup()

        # settings - marker window
        self.settings.beginGroup(SETMARGROUP)
            # position and size - should be set before we change shape, shape will take additional care for the round and square dimensions

        value = self.settings.value(SETPOS, QPoint(200, 0))
        if(type(value)!=type(QPoint())):
            value = value.toPoint()
        self.marker.move(value)
        value = self.settings.value(SETSIZE, QSize(300, 300))
        if(type(value)!=type(QSize())):
            value = value.toSize()
        self.marker.resize(value)
            # shape and color
            # shape
        value = self.settings.value(SETMARSHAPE, self.marker.getSetShape(), type(list()))
        self.marker.getSetShape(value)
            # color
        value = QColor(self.settings.value(SETMARCOLOR, self.marker.getSetColor()))
        self.marker.getSetColor(value)
            # movable cursor color
        value = QColor(self.settings.value(SETMARMCCOLOR, self.marker.moveCursorGetSetColor()))
        self.marker.moveCursorGetSetColor(value)
            # movable cross position
        value = self.settings.value(SETMARMCPOS, self.marker.moveCursorGetSetPos()).toPoint()
        self.marker.moveCursorGetSetPos(value)
            # movable cross visibility
        value = self.settings.value(SETMARMCDISPLAY, self.marker.moveCursorGetSetVisibility()).toBool()
        self.marker.moveCursorGetSetVisibility(value)
            # frame visibility
        value = self.settings.value(SETDISPLAY, self.marker.getSetVisibility()).toBool()
        self.marker.getSetVisibility(value)
            # frame cursor visibility
        value = self.settings.value(SETCURSORDISPLAY, self.marker.getSetCursorVisibility()).toBool()
        self.marker.getSetCursorVisibility(value)
            # marker opacity
        value = self.settings.value(SETOPACITY, self.marker.getSetOpacity()).toFloat()
        self.marker.getSetOpacity(value)
            # marker move step
        value = self.settings.value(SETMOVESTEP, self.marker.getSetMoveStep()).toInt()
        self.marker.getSetMoveStep(value)
            # marker move step small
        value = self.settings.value(SETMOVESTEPSMALL, self.marker.getSetMoveStepSmall()).toInt()
        self.marker.getSetMoveStepSmall(value)
            # marker resize step
        value = self.settings.value(SETRESIZESTEP, self.marker.getSetResizeStep()).toInt()
        self.marker.getSetResizeStep(value)
            # marker resize step small
        value = self.settings.value(SETRESIZESTEPSMALL, self.marker.getSetResizeStepSmall()).toInt()
        self.marker.getSetResizeStepSmall(value)
            # marker move cursor move step - large
        value = self.settings.value(SETMARMCMOVESTEP, self.marker.moveCursorGetSetMoveStep())
        self.marker.moveCursorGetSetMoveStep(value)
            # marker move cursor move step - small
        value = self.settings.value(SETMARMCMOVESTEPSMALL, self.marker.moveCursorGetSetMoveStepSmall())
        self.marker.moveCursorGetSetMoveStepSmall(value)
            # small grid unit
        value = self.settings.value(SETGRIDUNIT, self.marker.getSetGridUnit())
        self.marker.getSetGridUnit(value)

        # calibration
            # screen distance
        value = self.settings.value(SETSCRDISTANCE, self.getSetScreenDistance()).toFloat()
        self.getSetScreenDistance(value)
            # object  distance
        value = self.settings.value(SETOBJDISTANCE, self.getSetObjectDistance()).toFloat()
        self.getSetObjectDistance(value)

        self.settings.endGroup()
        return

    # settings on exit - write
    def writeSettings(self):
        # settings - main window
        self.settings.beginGroup(SETMWGROUP)
        self.settings.setValue(SETPOS, self.pos())
        self.settings.setValue(SETSIZE, self.size())
        self.settings.endGroup()

        # settings - marker window
        self.settings.beginGroup(SETMARGROUP)
        self.settings.setValue(SETPOS, self.marker.pos())   # position
        self.settings.setValue(SETSIZE, self.marker.size()) # size
            # shape and color
            # shape
        self.settings.setValue(SETMARSHAPE, self.marker.getSetShape())
            # color
        self.settings.setValue(SETMARCOLOR, self.marker.getSetColor())
            # movable cursor color
        self.settings.setValue(SETMARMCCOLOR, self.marker.moveCursorGetSetColor())
            # movable cross position
        self.settings.setValue(SETMARMCPOS, self.marker.moveCursorGetSetPos())
            # movable cross visibility
        self.settings.setValue(SETMARMCDISPLAY, self.marker.moveCursorGetSetVisibility())
            # frame visibility
        self.settings.setValue(SETDISPLAY, self.marker.getSetVisibility())
            # frame cursor visibility
        self.settings.setValue(SETCURSORDISPLAY, self.marker.getSetCursorVisibility())
            # marker opacity
        self.settings.setValue(SETOPACITY, self.marker.getSetOpacity())
            # marker move step
        self.settings.setValue(SETMOVESTEP, self.marker.getSetMoveStep())
            # marker move step small
        self.settings.setValue(SETMOVESTEPSMALL, self.marker.getSetMoveStepSmall())
            # marker resize step
        self.settings.setValue(SETRESIZESTEP, self.marker.getSetResizeStep())
            # marker resize step small
        self.settings.setValue(SETRESIZESTEPSMALL, self.marker.getSetResizeStepSmall())
            # marker move cursor move step - large
        self.settings.setValue(SETMARMCMOVESTEP, self.marker.moveCursorGetSetMoveStep())
            # marker move cursor move step - small
        self.settings.setValue(SETMARMCMOVESTEPSMALL, self.marker.moveCursorGetSetMoveStepSmall())
            # small grid unit
        self.settings.setValue(SETGRIDUNIT, self.marker.getSetGridUnit())

        # calibration
            # screen distance
        self.settings.setValue(SETSCRDISTANCE, self.getSetScreenDistance())
            # object  distance
        self.settings.setValue(SETOBJDISTANCE, self.getSetObjectDistance())
        self.settings.endGroup()

        # final saving settings
        self.settings.sync()
        return

    # functions to initialize and update gui
    # update marker tab
    def updateMarkerTab(self):
        # update marker tab - pos, dimentions
        (x, y, width, height) = self.intStringSeq(self.marker.x(), self.marker.y(), self.marker.width(), self.marker.height())
        self.lexmarker.setText(x)
        self.leymarker.setText(y)
        self.lewidthmarker.setText(width)
        self.leheightmarker.setText(height)

        # update marker step size
        (step, stepsmall) = self.intStringSeq(self.marker.getSetMoveStep(), self.marker.getSetMoveStepSmall())
        self.lelstepmarker.setText(step)
        self.lesstepmarker.setText(stepsmall)

        # frame visibility
        bframe = self.marker.getSetVisibility() 
        self.setCheckBoxOnBool(self.cbvframe, bframe)
        return

    # update marker resize tab
    def updateMarkerResizeTab(self):
        # update marker tab - pos, dimentions
        (step, stepsmall) = self.intStringSeq(self.marker.getSetResizeStep(), self.marker.getSetResizeStepSmall())
        self.lelsresizemarker.setText(step)
        self.lessresizemarker.setText(stepsmall)
        return

    # update cursor tab
    def updateCursorTab(self):
        # update marker tab - pos, dimentions
        (x, y, step, stepsmall) = self.intStringSeq(self.marker.moveCursorGetSetPos().x(), self.marker.moveCursorGetSetPos().y(), self.marker.moveCursorGetSetMoveStep(), self.marker.moveCursorGetSetMoveStepSmall())
        self.lexcursor.setText(x)
        self.leycursor.setText(y)
        self.lelstepcursor.setText(step)
        self.lesstepcursor.setText(stepsmall)

        # movable cursor visibility
        bcursor = self.marker.moveCursorGetSetVisibility()
        self.setCheckBoxOnBool(self.cbvcursormove, bcursor)

        # main, fixed cursor visibility
        bcursor = self.marker.getSetCursorVisibility()
        self.setCheckBoxOnBool(self.cbvcursor, bcursor)
        return

    # update grid tab
    def updateGridTab(self):
        gridunit = self.marker.getSetGridUnit()
        self.sbgridunit.setValue(gridunit)
        return

    # updade calibration tab - values used for calibration and distances
    def updateCalibrationTab(self):
        # width and height of the marker (outer rim) // correction by the pen size is required
        (width, height) = (float(self.marker.width()), float(self.marker.height()))


        # movable cursor distance to marker center
        cursorpos = self.marker.moveCursorGetSetPos()
        (x, y) = (cursorpos.x(), cursorpos.y())
        cursdist = pow(pow(x, 2) + pow(y, 2), 0.5)
        self.lecursorcursor.setText(self.floatStringSeq(cursdist))
        self.lecursorx.setText(self.intStringSeq(x))
        self.lecursory.setText(self.intStringSeq(y))

        # distances - read from the tab
        try:
            (self.scrdistance, self.objdistance) = (float(self.ledistscreen.text()), float(self.ledistobj.text()))
        except ValueError:
            self.showShortMsg(" wrong value submitted for calibration", True)
            return

        # calibration should be done realdist/screendist*otherdist
        (width, height, cursdist, x, y) = self.floatStringSeq(self.massMultiply(self.objdistance/self.scrdistance, width, height, cursdist, x, y))

        # setting corresponding gui fields
        self.lecwidth.setText(width)
        self.lecheight.setText(height)
        self.leccursorcursor.setText(cursdist)
        self.leccursorx.setText(x)
        self.leccursory.setText(y)
        return

    # update style tab - colors, shapes, etc.
    def updateStyleTab(self):
        # marker opacity
        opacity = self.marker.getSetOpacity()
        self.sbframeopacity.setValue(opacity)

        # update frame shapes combo
        self.updateFrameShapes()

        # update frame colors
        self.updateFrameColors()

        # update cursor colors
        self.updateMovableCursorColors()

        # create colors // fill comboboxes // create QPixmaps, create QIcons // create combobox items
        framecolors = self.marker.getColorList()
        return

    # update Frame shapes combo
    def updateFrameShapes(self):
        # shapes - fill the combobox once
        frameshapes = self.marker.getShapeList()

        # check selected frame shape
        shape = self.marker.getSetShape()
        index = frameshapes.index(shape)
        self.cmbframeshape.setCurrentIndex(index)

        # update window title
        self.updateWindowTitle(shape)
        return

    # create Frame shapes combo box
    def createCMBFrameShapes(self):
        # shapes - fill the combobox once
        frameshapes = self.marker.getShapeList()

        # fill frame shapes box once
        if(self.cmbframeshape.count()==0):
            for shape in frameshapes:
                temp = shape[0]

                strshape = ""
                strthick = "THICK"
                if(shape[1]==THIN):
                    strthick = "THIN"

                if(temp==SHAPESQR):
                    strshape = "Square"
                elif(temp==SHAPECIRCLE):
                    strshape = "Circle"
                elif(temp==SHAPERECT):
                    strshape = "Rectangle"
                elif(temp==SHAPEELLIPSE):
                    strshape = "Ellipse"
                elif(temp==SHAPEBOUNDS):
                    strshape = "Bounds"
                elif(temp==SHAPEGRID):
                    strshape = "Grid"
                
                strshape = "%s - %s"%(strshape, strthick)

                # ca only pass shapes as a list of QVariants
                temp = []
                for v in shape:
                    temp.append(QVariant(v))
                self.cmbframeshape.addItem(strshape, QVariant().fromList(temp))
        return

    # update window title using shape name
    def updateWindowTitle(self, shape):
        # shape
        temp = shape[0]

        # pen width
        strthick = ""
        if(shape[1]==THIN):
            strthick = "- Thin"
        elif(shape[1]==THICK):
            strthick = "- Thick"

        string = ""
        if(temp==SHAPESQR):
            string = "Square"
        elif(temp==SHAPECIRCLE):
            string = "Circle"
        elif(temp==SHAPERECT):
            string = "Rectangle"
        elif(temp==SHAPEELLIPSE):
            string = "Ellipse"
        elif(temp==SHAPEBOUNDS):
            string = "Bounds"
        elif(temp==SHAPEGRID):
            string = "Grid"

        string = "%s - %s %s"%(self.title, string, strthick)
        self.setWindowTitle(string)

    # update frame colors combobox
    def updateFrameColors(self):
        framecolors = self.marker.getColorList()
        index = framecolors.index(self.marker.getSetColor())
        self.cmbframecolor.setCurrentIndex(index)
        return

    # create frame colors combobox
    def createCMBFrameColors(self):
        framecolors = self.marker.getColorList()
        if(self.cmbframecolor.count()==0):
            for color in framecolors:
                pixmap = QPixmap(QICONW, QICONH)
                pixmap.fill(color)
                icon = QIcon(pixmap)
                self.cmbframecolor.addItem(icon, "", QVariant(color))
        return

    # update movable cursor colors
    def updateMovableCursorColors(self):
        cursorcolors = self.marker.getMoveCursorColorList()
        index = cursorcolors.index(self.marker.moveCursorGetSetColor())
        self.cmbcursorcolor.setCurrentIndex(index)
        return

    # create movable cursor colors combobox
    def createCMBMovableCursorColors(self):
        cursorcolors = self.marker.getMoveCursorColorList()
        if(self.cmbcursorcolor.count()==0):
            for color in cursorcolors:
                pixmap = QPixmap(QICONW, QICONH)
                pixmap.fill(color)
                icon = QIcon(pixmap)
                self.cmbcursorcolor.addItem(icon, "", QVariant(color))
        return

    # process calibration button click
    def btnStartCalibration(self):
        self.overlay = MOverlay()
        self.overlay.showFullScreen()

        # create calibration signal
        self.connect(self.overlay, SIGNAL(SIGNALCALIBRATIONCANCELED), self.cleanupCalibration)
        self.connect(self.overlay, SIGNAL(SIGNALCALIBRATION), self.applyCalibration)

        # hide marker to improve visuals
        self.marker.hide()

    # procces calibration
    def applyCalibration(self, number):
        self.ledistscreen.setText("%.2f"%number)
        self.cleanupCalibration("Action: screen distance measurement success")

    # cleanup after screen distance measurement
    def cleanupCalibration(self, msg):
        # show marker after distance calibration
        self.marker.show()
        self.showShortMsg(msg)

    # mass convertion to strings - ints
    def intStringSeq(self, *tlist):
        if(type(tlist[0])==type(tuple()) or type(tlist[0])==type(list())):
            tlist = tlist[0]

        res = []
        for v in tlist:
            res.append("%i"%v)

        if(len(res)==1):            # check if we have only one value
            res = res[0] 
        return res

    # mass convertion to strings - floats
    def floatStringSeq(self, *tlist):
        if(type(tlist[0])==type(tuple()) or type(tlist[0])==type(list())):
            tlist = tlist[0]

        res = []
        for v in tlist:
            format = "%.2f" 
            if(v<1 and v>-1):       # check if units are stupid - very small - we need move digits as an answer
                format = "%.4f"
            res.append(format%v)

        if(len(res)==1):            # check if we have only one value
            res = res[0]
        return res

    # mass division
    def massMultiply(self, div, *tlist):
        if(type(tlist[0])==type(tuple()) or type(tlist[0])==type(list())):
            tlist = tlist[0]

        res = []
        for v in tlist:
            res.append(float(v)*float(div))
        return res

    # set checked state of QCheckBox on bool
    def setCheckBoxOnBool(self, wdgt, state):
        bchecked = Qt.Unchecked
        if(state):
            bchecked = Qt.Checked

        wdgt.setChecked(bchecked)
        return bchecked

    # returns current screen distance for calibration - used a lot in read/write of the settings
    def getSetScreenDistance(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toFloat()[0]
            elif(type(value)==type(list()) or  type(value)==type(tuple())): # for a case when I forget to transorm some values
                value = float(value[0])
            self.scrdistance = float(value)
        return self.scrdistance

    # returns object real distance for calibration - used a lot in read/write of the settings
    def getSetObjectDistance(self, value = None):
        if(value!=None):
            if(type(value)==type(QVariant())): # 
                value = value.toFloat()[0]
            elif(type(value)==type(list()) or  type(value)==type(tuple())): # for a case when I forget to transorm some values
                value = float(value[0])
            self.objdistance = float(value)
        return self.objdistance

    # implement integer fields validation procedure for text fields - QLineEdit
    def setIntValidator(self, tlist, vmin=None, vmax=None):
        for wdgt in tlist:
            v = QIntValidator()
            if(vmin is not None):
                v.setBottom(vmin)
            if(vmax is not None):
                v.setTop(vmax)
            wdgt.setValidator(v)

    # implement integer fields validation procedure for text fields - QLineEdit
    def setFloatValidator(self, tlist, vmin=None, vmax=None):
        for wdgt in tlist:
            v = QDoubleValidator()
            if(vmin is not None):
                v.setBottom(vmin)
            if(vmax is not None):
                v.setTop(vmax)
            wdgt.setValidator(v)

    # assigning signals and slots in sequence
    def connectSeq(self, tlist, signal, slot):
        temp = []
        # connection of item by item or items in sequence 
        if(type(tlist)==type(tuple()) or type(tlist)==type(list())):
            temp = tlist
        else:
            temp.append(tlist)

        # connect specific signal and slot in sequence
        for wdgt in temp:
            self.connect(wdgt, signal, slot)

    # updating marker from MarkerPositionTab input - one change in Tab, look for all values approach for simplicity
    def updateMarker(self):
        # detect if there is really a change - first check if there is a change in comboboxes for steps
        # all other changes are attributed to changes by keytyping into the text fields
        if(self.getInputChange()):
            # check large marker step - check if it is the same or not, update it
            if(self.cmblstepmarker.currentIndex()!=0):
                cmb =  self.cmblstepmarker
                le =  self.lelstepmarker

                i = cmb.currentIndex()
                v = cmb.itemData(i).toInt()[0]

                if(v!= self.marker.getSetMoveStep()):
                    le.setText(cmb.currentText())
                    self.marker.getSetMoveStep(v)
                    cmb.setCurrentIndex(0)
            # check small marker step - check if it is the same or not, update it
            elif(self.cmbsstepmarker.currentIndex()!=0):
                cmb =  self.cmbsstepmarker
                le =  self.lesstepmarker

                i = cmb.currentIndex()
                v = cmb.itemData(i).toInt()[0]

                if(v!= self.marker.getSetMoveStepSmall()):
                    le.setText(cmb.currentText())
                    self.marker.getSetMoveStepSmall(v)
                cmb.setCurrentIndex(0)
            else:
                ## here we check text fields and check boxes

                # check change of position of the marker - move if there is a change
                vpos = QPoint(self.getIntWdgtText(self.lexmarker), self.getIntWdgtText(self.leymarker))
                if(vpos != self.marker.pos()):
                    self.marker.move(vpos)

                # check size of the marker - change size if there is a change, check for minimum marker dimension
                vsize = QSize(self.getIntWdgtText(self.lewidthmarker), self.getIntWdgtText(self.leheightmarker))
                if(vsize.width()<MINDIMENSION or vsize.height()<MINDIMENSION):
                    self.updateMarkerTab()
                    self.showShortMsg("one of the desired marker dimensions is too small", True)
                    return
                if(vsize!= self.marker.size()):
                    self.marker.processExternalResize(vsize)

                # check steps for marker steps - large
                v = self.getIntWdgtText(self.lelstepmarker)
                if(v!= self.marker.getSetMoveStep()):
                    self.marker.getSetMoveStep(v)

                # check steps for marker steps - small
                v = self.getIntWdgtText(self.lesstepmarker)
                if(v!= self.marker.getSetMoveStepSmall()):
                    self.marker.getSetMoveStepSmall(v)

                # change of checkbox states

                v = self.cbvframe.checkState() == Qt.Checked
                if(v != self.marker.getSetVisibility()):
                    self.marker.getSetVisibility(v)
                    self.marker.update()

            self.resetInputchange()
        return

    # updating marker from MarkerResizeTab input - one change in Tab, look for all values approach for simplicity
    def updateMarkerResize(self):
        # detect if there is really a change - first check if there is a change in comboboxes for steps
        # all other changes are attributed to changes by keytyping into the text fields
        if(self.getInputChange()):
            # check large marker step - check if it is the same or not, update it
            if(self.cmblstepmarkerresize.currentIndex()!=0):
                cmb =  self.cmblstepmarkerresize
                le =  self.lelsresizemarker

                i = cmb.currentIndex()
                v = cmb.itemData(i).toInt()[0]

                if(v!= self.marker.getSetResizeStep()):
                    le.setText(cmb.currentText())
                    self.marker.getSetResizeStep(v)
                    cmb.setCurrentIndex(0)
            # check small marker step - check if it is the same or not, update it
            elif(self.cmbsstepmarkerresize.currentIndex()!=0):
                cmb =  self.cmbsstepmarkerresize
                le =  self.lessresizemarker

                i = cmb.currentIndex()
                v = cmb.itemData(i).toInt()[0]

                if(v!= self.marker.getSetResizeStepSmall()):
                    le.setText(cmb.currentText())
                    self.marker.getSetResizeStepSmall(v)
                cmb.setCurrentIndex(0)
            else:
                ## here we check text fields and check boxes

                # check steps for marker steps - large
                v = self.getIntWdgtText(self.lelsresizemarker)
                if(v!= self.marker.getSetResizeStep()):
                    self.marker.getSetResizeStep(v)

                # check steps for marker steps - small
                v = self.getIntWdgtText(self.lessresizemarker)
                if(v!= self.marker.getSetResizeStepSmall()):
                    self.marker.getSetResizeStepSmall(v)

            self.resetInputchange()
        return

    # updating marker from CursorTab input - one change in Tab, look for all values approach for simplicity
    def updateCursor(self):
        # detect if there is really a change - first check if there is a change in comboboxes for steps
        # all other changes are attributed to changes by keytyping into the text fields
        if(self.getInputChange()):
            # check large marker step - check if it is the same or not, update it
            if(self.cmblstepcursor.currentIndex()!=0):
                cmb =  self.cmblstepcursor
                le =  self.lelstepcursor

                i = cmb.currentIndex()
                v = cmb.itemData(i).toInt()[0]

                if(v!= self.marker.moveCursorGetSetMoveStep()):
                    le.setText(cmb.currentText())
                    self.marker.moveCursorGetSetMoveStep(v)
                cmb.setCurrentIndex(0)
            # check small marker step - check if it is the same or not, update it
            elif(self.cmbsstepcursor.currentIndex()!=0):
                cmb =  self.cmbsstepcursor
                le =  self.lesstepcursor

                i = cmb.currentIndex()
                v = cmb.itemData(i).toInt()[0]

                if(v!= self.marker.moveCursorGetSetMoveStepSmall()):
                    le.setText(cmb.currentText())
                    self.marker.moveCursorGetSetMoveStepSmall(v)
                cmb.setCurrentIndex(0)
            else:
                ## here we check text fields and check boxes

                # check change of position of the movable cursor - move if there is a change
                vpos = QPoint(self.getIntWdgtText(self.lexcursor), self.getIntWdgtText(self.leycursor))
                if(vpos != self.marker.moveCursorGetSetPos()):
                    self.marker.moveCursorGetSetPos(vpos)
                    self.marker.update()

                # check steps for marker steps - large
                v = self.getIntWdgtText(self.lelstepcursor)
                if(v!= self.marker.moveCursorGetSetMoveStep()):
                    self.marker.moveCursorGetSetMoveStepSmall(v)

                # check steps for marker steps - small
                v = self.getIntWdgtText(self.lesstepcursor)
                if(v!= self.marker.moveCursorGetSetMoveStepSmall()):
                    self.marker.moveCursorGetSetMoveStepSmall(v)

                # change of checkbox states
                # static cursor visibility - center of the marker
                v = self.cbvcursor.checkState() == Qt.Checked
                if(v != self.marker.getSetCursorVisibility()):
                    self.marker.getSetCursorVisibility(v)
                    self.marker.update()

                # movable cursor visibility 
                v = self.cbvcursormove.checkState() == Qt.Checked
                if(v != self.marker.moveCursorGetSetVisibility()):
                    self.marker.moveCursorGetSetVisibility(v)
                    self.marker.update()

            self.resetInputchange()
        return

    # updating marker from GridTab input - one change in Tab, look for all values approach for simplicity
    def updateGrid(self):
        if(self.getInputChange()):
            v = self.sbgridunit.value()
            if(v!=self.marker.getSetGridUnit()):
                self.marker.getSetGridUnit(v)
                self.marker.update()
            self.resetInputchange()
        return

    # update marker style
    def updateStyle(self, *tlist):
        (i, wdgt) = tlist
        if(wdgt == self.cmbframecolor):     # update marker frame color
            v = QColor(wdgt.itemData(i))
            self.marker.getSetColor(v)
        elif(wdgt == self.cmbcursorcolor):
            v = QColor(wdgt.itemData(i))
            self.marker.moveCursorGetSetColor(v)
            self.marker.update()
        elif(wdgt == self.cmbframeshape):
            v = wdgt.itemData(i)
            self.marker.getSetShape(v)
        elif(wdgt == self.sbframeopacity):  # update marker frame opacity
            self.marker.getSetOpacity(i)
        return


    # flag to detect input change - for instance that the text has been edited - will simplify bulk processing of input events in gui
    def setInputChange(self):
        self._binputchange = True

    def getInputChange(self):
        return self._binputchange

    def resetInputchange(self):
        self._binputchange = False

    # get certain conversion of widget text - int value
    def getIntWdgtText(self, wdgt):
        v = 0
        try:
            v = int(wdgt.text())
        except ValueError:
            self.showLongMsg(" widget text type coversion error (int)", True)
        return v

    # get certain conversion of widget text - float value
    def getFloatWdgtText(self, wdgt):
        v = 0
        try:
            v = float(wdgt.text())
        except ValueError:
            self.showLongMsg(" widget text type coversion error (float) ", True)
        return v

    # status bar messages - 10s
    def showLongMsg(self, msg, error=False):
        duration = 10000
        format = "%s"
        if(error is not None):
            format = "Error: %s"
        self.showMessage(format%msg, duration)

    # status bar messages - 3s
    def showShortMsg(self, msg, error=False):
        duration = 2000
        format = "%s"
        if(error):
            format = "Error: %s"
        self.showMessage(format%msg, duration)

    # show message
    def showMessage(self, msg, duration):
        # cleanup overlay if needed
        if(self.overlay is not None):
            self.overlay = None
        # show message
        self.status.showMessage(msg, duration)

    # test
    def trackBtnPress(self):
        k = QKeyEvent(QEvent.KeyPress, Qt.Key_Up, Qt.NoModifier)
        self.marker.keyPressEvent(k)

    # set check state from boo;
    def setCheckedFromBool(self, wdgt, value):
        state = Qt.Unchecked
        if(value):
            state = Qt.Checked
        wdgt.setCheckState(state)
###
## MarkerControl class END
###

###
### MPushButton class = override pushbutton to draw arrows on the buttons
###
class MPushButton(QPushButton):
    def __init__(self, type=BTNLARGEUP, parent=None):
        super(MPushButton, self).__init__(parent)

        # type discriminates arrow direction
        self.type = type

    # draw first superclass, then arrows on top of it
    def paintEvent(self, event):
        # draw superclass
        super(MPushButton, self).paintEvent(event)

        # take painter, switch on antialiasing
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # setup pen
        mypen = painter.pen()
        mypen.setColor(QColor(100,100,100))
        mypen.setWidth(3)
        painter.setPen(mypen)

        # width, height
        (x, y, width, height) = (0,0, self.width(), self.height())
        (draww, drawh) = (20, 20)

        # positions of the rectangle to draw
        (drawx, drawy) = (int((width-draww)/2), int((height-drawh)/2))

        # position of the center
        (cenx, ceny) = (int((width)/2), int((height)/2))

        # large buttons up and down, left and right - we use the fact of symmetric buttons for simplicity
        if(self.type %2 ==1): # and (self.type==BTNLARGEUP or self.type==BTNLARGEDOWN)
            (liney1, liney2) = (int(drawh*1.0/4), int(drawh*0.0/4))
            (liney3, liney4) = (int(drawh*3.0/4), int(drawh*2.0/4))
            shift = 1
            spany = int(abs(liney1-liney2))
            spanx = int(draww/2)
            if(self.type == BTNLARGEUP):
                painter.drawLine(drawx, ceny-shift, drawx+spanx, ceny-spany-shift)
                painter.drawLine(drawx+spanx, ceny-spany-shift, drawx+draww, ceny-shift)
                painter.drawLine(drawx, ceny+spany+shift, drawx+spanx, ceny+shift)
                painter.drawLine(drawx+spanx, ceny+shift, drawx+draww, ceny+spany+shift)
            elif(self.type == BTNLARGEDOWN):
                painter.drawLine(drawx, ceny+shift, drawx+spanx, ceny+spany+shift)
                painter.drawLine(drawx+spanx, ceny+spany+shift, drawx+draww, ceny+shift)
                painter.drawLine(drawx, ceny-spany-shift, drawx+spanx, ceny-shift)
                painter.drawLine(drawx+spanx, ceny-shift, drawx+draww, ceny-spany-shift)
            elif(self.type == BTNLARGELEFT):
                painter.drawLine( ceny-shift, drawx,  ceny-spany-shift, drawx+spanx)
                painter.drawLine( ceny-spany-shift, drawx+spanx, ceny-shift, drawx+draww)
                painter.drawLine( ceny+spany+shift, drawx,  ceny+shift, drawx+spanx,)
                painter.drawLine( ceny+shift, drawx+spanx,  ceny+spany+shift, drawx+draww)
            elif(self.type == BTNLARGERIGHT):
                painter.drawLine( ceny+shift, drawx,  ceny+spany+shift, drawx+spanx)
                painter.drawLine( ceny+spany+shift, drawx+spanx, ceny+shift, drawx+draww)
                painter.drawLine( ceny-spany-shift, drawx,  ceny-shift, drawx+spanx,)
                painter.drawLine( ceny-shift, drawx+spanx,  ceny-spany-shift, drawx+draww)
        # small buttons up and down, left and right, we use symmetric buttons for simplicity
        elif(self.type %2 ==0 ):
            (liney1, liney2) = (int(drawh*2.0/4), int(drawh*1.0/4))
            spany = int(abs(liney1-liney2)/2)
            spanx = int(draww/2)
            if(self.type == BTNSMALLUP):
                painter.drawLine(drawx, ceny+spany, drawx+spanx, ceny-spany)
                painter.drawLine(drawx+spanx, ceny-spany, drawx+draww, ceny+spany)
            elif(self.type ==BTNSMALLDOWN):
                painter.drawLine(drawx, ceny-spany, drawx+spanx, ceny+spany)
                painter.drawLine(drawx+spanx, ceny+spany, drawx+draww, ceny-spany)
            if(self.type == BTNSMALLLEFT):
                painter.drawLine(ceny+spany, drawx, ceny-spany, drawx+spanx)
                painter.drawLine(ceny-spany, drawx+spanx, ceny+spany, drawx+draww)
            elif(self.type ==BTNSMALLRIGHT):
                painter.drawLine(ceny-spany, drawx, ceny+spany, drawx+spanx)
                painter.drawLine(ceny+spany, drawx+spanx, ceny-spany, drawx+draww)

        painter.end()
###
## MPushButton class END
###


###
## MOverlay class - transparent class for calibration and other tasks
## user clicks on the canvas and draws a distance of interest
###
class MOverlay(QMainWindow):
    def __init__(self, parent=None):
        super(MOverlay, self).__init__(parent)

        self.initVariables()

        self.initSelf()
        return

    def initSelf(self):
        # set title
        self.setWindowTitle("MarkerOverlay")
        self.resize(400, 400)

        # translucient, window on top
        self.setWindowFlags(Qt.FramelessWindowHint|Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_NoSystemBackground, False)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        # prepare message
        self.prepMessage()

        return

    def initVariables(self):
        # mode for work - for calibration or anything else
        self._mode = OVERLAYCALIBRATION

        # self first click position
        self._firstpos = None
        # second position - second click or while mouse move
        self._secondpos = None

        # store old cursor, set new cursor
        self._oldcursor = self.cursor()

        # message to tell user
        self._message = ""

        # check readiness to close window
        self._bcloseready = False

        # check if we do draw line - prevent keys from being accepted
        self._bdraw = False
        
        # change cursor to a point
        pixmap = QPixmap(QSize(3,3))
        pixmap.fill(QColor(255, 255, 100, 255))
        self.setCursor(QCursor(pixmap))

        return

    def prepMessage(self):
        if(self._mode==OVERLAYCALIBRATION):
            if(self._firstpos is None):
                self._message = """
Step 1: Click on the canvas at the begining of the object used for calibration.
Step 2: Drag the calibration line across the object with known size.
Step 3: Finish calibration by releasing mouse button and pressing ENTER

Cancel calibration completely by pressing ESC. 
Reset calibration and clean the drawn line by pressing the right mouse button."""
            else:
                self._message = ""

    def paintEvent(self, event):
        # fill with gray transparent background
        (width, height) = (self.width(), self.height())

        color = COLOROVERLAYBKG

        painter = QPainter(self)
        mybrush = QBrush(color)
        painter.setBrush(mybrush)

        color = COLOROVERLAYBKGLINE
        pen = QPen(color)
        painter.setPen(pen)

        painter.drawRect(QRect(0,0,width, height))

        # draw a guiding message - telling user what to do
        if(len(self._message)>0):
            color = COLOROVERLAYTEXT
            (pen, brush, font) = (QPen(color), QBrush(color), QFont("Arial", 22))
            painter. setPen(pen)
            painter.setBrush(brush)
            painter.setFont(font)

            # show text in the center
            rtext = painter.boundingRect(QRectF(0,0, width, height), Qt.AlignLeft, QString(self._message)).toRect()
            rwdgt = self.rect()
            (wd, ht) = (rtext.width(), rtext.height())
            rtext.setRect(rwdgt.x()+(rwdgt.width()-rtext.width())/2, rwdgt.y()+(rwdgt.height()-rtext.height())/2, wd, ht)
            painter.drawText(rtext, Qt.AlignLeft, QString(self._message))


        # first position is an indicator for additional graphic work
        # discriminate different modes
        if(self._firstpos):
            if(self._mode==OVERLAYCALIBRATION):
                endw = 10

                # line between points
                color = COLOROVERLAYLINE
                pen = QPen(color)
                pen.setWidth(2)
                painter.setPen(pen)
                painter.drawLine(self._firstpos, self._secondpos)

                # draw markers at the end of the lines, calculate normal and its length
                (dx, dy) = (self._secondpos.x()-self._firstpos.x(), self._secondpos.y()-self._firstpos.y())
                length = pow(dx**2+dy**2, 0.5)
                if(length==0.0):
                    length = 1.0

                # draw normal lines at the end points
                point = QPoint(float(-dy)/length*endw, float(dx)/length*endw)
                painter.drawLine(self._firstpos, self._firstpos+point)
                painter.drawLine(self._firstpos, self._firstpos-point)
                painter.drawLine(self._secondpos, self._secondpos-point)
                painter.drawLine(self._secondpos, self._secondpos+point)

        painter.end()

    # process mouse press event - left click to calibrate, right click to stop calibration
    def mousePressEvent(self, event):
        if(event.button()==Qt.LeftButton):
            if(self._firstpos is None):      # start of calibration
                event.accept()
                self._firstpos = event.globalPos()
                self._secondpos = self._firstpos

                # prepare guiding message
                self.prepMessage()

                # confirm - we are drawing
                self._bdraw = True

                self.grabMouse()
                self.update()
        elif(event.button()==Qt.RightButton):
            event.accept()
            # reset - cleanup - no calibration is done
            self.resetTemporary()
            self.update()
        return QWidget().mousePressEvent(event)

    # process key events - Escape closes window and resets calibration, Enter - confirms the choice
    def keyPressEvent(self, event):
        k = event.key()
        m = event.modifiers()

        # only accept keypress while not drawing calibration line
        if(not self._bdraw):
            if(k==Qt.Key_Escape):
                # reset - cleanup - no calibration is done
                event.accept()
                self.reset()
            elif(k==Qt.Key_Enter or k==Qt.Key_Return):
                event.accept()
                self.prepClose()
        else:
            event.ignore()

    # prepare of the close event
    def prepClose(self):
        self._bcloseready = True
        self.releaseMouse()
        self.update()
        self.close()
        return

    # on mouse release event - prepare for
    def mouseReleaseEvent(self, event):
        # save last point
        if(self._firstpos):
            self._secondpos = event.globalPos()
            self._bdraw = False

        return

    # control mouse movement - report position if needed
    def mouseMoveEvent(self, event):
        if(self._firstpos is not None):
            self._secondpos = event.globalPos()
            self.update()
        return

    def reset(self):
        self.resetTemporary()
        self._bcloseready = True
        self.prepClose()

    def resetTemporary(self):
        self._firstpos = self._secondpos = None
        self._bdraw = False
        self.prepMessage()

    # on window close event
    def closeEvent(self, event):
        if(self._bcloseready):
            # restoring cursor
            self.setCursor(self._oldcursor)
            # accept close event
            event.accept()

            # report distance for calibration
            if(self._firstpos):
                (x, y) = ((self._firstpos-self._secondpos).x(), (self._firstpos-self._secondpos).y())
                (x, y) = (float(x), float(y))
                length = pow(x**2+y**2, 0.5)

                # avoid reporting 0 as an answer
                if(length==0):
                    length = 1.
                
                # report length for calibration
                self.emit(SIGNAL(SIGNALCALIBRATION), length)
            else:
                self.emit(SIGNAL(SIGNALCALIBRATIONCANCELED), "Action: screen distance measurement canceled.")
        else:
            event.ignore() 
        return

###
## MOverlay class END
###

###
### Main program loop
###
if __name__ == '__main__':
    print(DISCLAMER)
    app = QApplication(sys.argv)
    form = MarkerControl(app)
    app.exec_()