#!/usr/bin/env python3
from __future__ import print_function


# Import required modules
import sys, time, os
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2.QtCore import QByteArray
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2 import QtSvg

#Import model
from rdeditor.molEditWidget import MolEditWidget
from rdeditor.ptable_widget import PTable

from rdkit import Chem

# The molecular editor widget
class QrdEditor(QtWidgets.QWidget):
    # Constructor function
    def __init__(self, parent=None, fileName=None, loglevel="WARNING"):
        super(QrdEditor,self).__init__(parent=parent)
        self.pixmappath = os.path.abspath(os.path.dirname(__file__)) + '/pixmaps/'
        self.loglevels = ["Critical","Error","Warning","Info","Debug","Notset"]
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.editor = MolEditWidget()
        self.ptable = PTable()
        self._fileName = None
        self.initGUI(fileName = fileName)
        self.ptable.atomtypeChanged.connect(self.setAtomTypeName)
        self.editor.logger.setLevel(loglevel)

        self.horizontalLayout.addWidget(self.mainToolBar)
        self.horizontalLayout.addWidget(self.editor)
        self.horizontalLayout.addWidget(self.sideToolBar)

    #Properties
    @property
    def fileName(self):
        return self._fileName

    @fileName.setter
    def fileName(self, filename):
        if filename != self._fileName:
            self._fileName = filename
            self.setWindowTitle(str(filename))


    def initGUI(self, fileName=None):
        self.fileName = fileName

        self.filters = "MOL Files (*.mol *.mol);;Any File (*)"
        self.SetupComponents()

        if self.fileName is not None:
            self.editor.logger.info("Loading model from %s"%self.fileName)
            self.loadMolFile(fileName)

        self.show()

    # Function to setup status bar, central widget, menu bar, tool bar
    def SetupComponents(self):
        self.CreateActions()
        # self.CreateMenus()
        self.CreateToolBars()

    def CreateToolBars(self):
        self.mainToolBar = QToolBar(self)
        #Main action bar
        self.mainToolBar.addAction(self.openAction)
        self.mainToolBar.addAction(self.saveAction)
        self.mainToolBar.addAction(self.saveAsAction)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.selectAction)
        self.mainToolBar.addAction(self.addAction)
        self.mainToolBar.addAction(self.addBondAction)
        self.mainToolBar.addAction(self.replaceAction)
        self.mainToolBar.addAction(self.rsAction)
        self.mainToolBar.addAction(self.ezAction)
        self.mainToolBar.addAction(self.increaseChargeAction)
        self.mainToolBar.addAction(self.decreaseChargeAction)
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.cleanCoordinatesAction)

        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.removeAction)
        self.mainToolBar.addAction(self.clearCanvasAction)
        #Bond types TODO are they necessary as can be toggled??
        self.mainToolBar.addSeparator()
        self.mainToolBar.addAction(self.undoAction)
        #Side Toolbar
        self.sideToolBar = QToolBar(self)
        # self.addToolBar(QtCore.Qt.LeftToolBarArea, self.sideToolBar)
        self.sideToolBar.addAction(self.singleBondAction)
        self.sideToolBar.addAction(self.doubleBondAction)
        self.sideToolBar.addAction(self.tripleBondAction)
        self.sideToolBar.addSeparator()
        for action in self.atomActions:
            self.sideToolBar.addAction(action)
        self.sideToolBar.addAction(self.openPtableAction)
        self.mainToolBar.setOrientation(Qt.Vertical)
        self.sideToolBar.setOrientation(Qt.Vertical)

    def loadMolFile(self, filename):
        self.fileName = filename
        mol = Chem.MolFromMolFile(str(self.fileName), sanitize=False, strictParsing=False)
        self.editor.mol = mol
        # self.statusBar().showMessage("File opened")

    def openFile(self):
        self.fileName, self.filterName = QFileDialog.getOpenFileName(self, caption = "Open MOL file",filter = self.filters)
        self.loadMolFile(self.fileName)

    def saveFile(self):
        if self.fileName != None:
            Chem.MolToMolFile(self.editor.mol, str(self.fileName))
        else:
            self.saveAsFile()

    def saveAsFile(self):
        self.fileName, self.filterName = QFileDialog.getSaveFileName(self, filter=self.filters)
        if(self.fileName != ''):
            if self.fileName[-4:].upper() != ".MOL":
                self.fileName = self.fileName + ".mol"
            Chem.MolToMolFile(self.editor.mol, str(self.fileName))
#            file = open(self.fileName, 'w')
#            file.write(self.textEdit.toPlainText())
            self.statusBar().showMessage("File saved", 2000)

    def clearCanvas(self):
        self.editor.clearAtomSelection()
        self.editor.mol = None
        self.fileName = None
        # self.statusBar().showMessage("Canvas Cleared")

    def closeEvent(self, event):
        # self.editor.logger.debug("closeEvent triggered")
        self.exitFile()
        event.ignore()

    def exitFile(self):
        response = self.msgApp("Confirmation","This will quit the application. Do you want to Continue?")
        if response == "Y":
            self.ptable.close()
            exit(0) #TODO, how to exit qapplication from within class instance?
        # else:
            # self.editor.logger.debug("Abort closing")


    # Function to show Diaglog box with provided Title and Message
    def msgApp(self,title,msg):
        userInfo = QMessageBox.question(self,title,msg,
                                        QMessageBox.Yes | QMessageBox.No)
        if userInfo == QMessageBox.Yes:
            return "Y"
        if userInfo == QMessageBox.No:
            return "N"
        self.close()

    def aboutHelp(self):
        QMessageBox.about(self, "About Simple Molecule Editor",
                """A Simple Molecule Editor where you can edit molecules\nBased on RDKit! http://www.rdkit.org/ \nSome icons from http://icons8.com\n\nSource code: https://github.com/EBjerrum/rdeditor""")

    def setAction(self):
        sender = self.sender()
        self.editor.setAction(sender.objectName())
        # self.myStatusBar.showMessage("Action %s selected"%sender.objectName())

    def setBondType(self):
        sender = self.sender()
        self.editor.setBondType(sender.objectName())
        # self.myStatusBar.showMessage("Bondtype %s selected"%sender.objectName())

    def setAtomType(self):
        sender = self.sender()
        self.editor.setAtomType(sender.objectName())
        # self.myStatusBar.showMessage("Atomtype %s selected"%sender.objectName())

    def setAtomTypeName(self, atomname):
        self.editor.setAtomType(str(atomname))
        # self.myStatusBar.showMessage("Atomtype %s selected"%atomname)

    def openPtable(self):
        self.ptable.show()

    def setLogLevel(self):
        loglevel = self.sender().objectName().split(':')[-1].upper()
        # self.editor.logger.setLevel(loglevel)

    # Function to create actions for menus and toolbars
    def CreateActions(self):
        self.openAction = QAction( QIcon(self.pixmappath + 'open.png'), 'O&pen',
                                  self, shortcut=QKeySequence.Open,
                                  statusTip="Open an existing file",
                                  triggered=self.openFile)

        self.saveAction = QAction( QIcon(self.pixmappath + '/icons8-Save.png'), 'S&ave',
                                  self, 
                                  shortcut=QKeySequence.Save,
                                  statusTip="Save file",
                                  triggered=self.saveFile)


        self.saveAsAction = QAction( QIcon(self.pixmappath + 'icons8-Save as.png'), 'Save As',
                                  self, 
                                  shortcut=QKeySequence.SaveAs,
                                  statusTip="Save file as ..",
                                  triggered=self.saveAsFile)


        self.exitAction = QAction( QIcon(self.pixmappath + 'icons8-Shutdown.png'), 'E&xit',
                                   self, shortcut="Ctrl+Q",
                                   statusTip="Exit the Application",
                                   triggered=self.exitFile)

        self.aboutAction = QAction( QIcon(self.pixmappath + 'about.png'), 'A&bout',
                                    self, statusTip="Displays info about text editor",
                                   triggered=self.aboutHelp)

        self.aboutQtAction = QAction("About &Qt", self,
                                statusTip="Show the Qt library's About box",
                                triggered=QApplication.aboutQt)

        self.openPtableAction = QAction( QIcon(self.pixmappath + 'ptable.png'), 'O&pen Periodic Table',
                                  self, shortcut=QKeySequence.Open,
                                  statusTip="Open the periodic table for atom type selection",
                                  triggered=self.openPtable)

        #Edit actions
        self.actionActionGroup = QtWidgets.QActionGroup(self, exclusive=True)
        self.selectAction = QAction( QIcon(self.pixmappath + 'icons8-Cursor.png'), 'Se&lect',
                                   self, shortcut="Ctrl+L",
                                   statusTip="Select Atoms",
                                   triggered=self.setAction, objectName="Select",
                                   checkable=True)
        self.actionActionGroup.addAction(self.selectAction)

        self.addAction = QAction( QIcon(self.pixmappath + 'icons8-Edit.png'), '&Add',
                                   self, shortcut="Ctrl+A",
                                   statusTip="Add Atoms",
                                   triggered=self.setAction, objectName="Add",
                                   checkable=True)
        self.actionActionGroup.addAction(self.addAction)

        self.addBondAction = QAction( QIcon(self.pixmappath + 'icons8-Pinch.png'), 'Add &Bond',
                                   self, shortcut="Ctrl+B",
                                   statusTip="Add Bond",
                                   triggered=self.setAction, objectName="Add Bond",
                                   checkable=True)
        self.actionActionGroup.addAction(self.addBondAction)

        self.replaceAction = QAction( QIcon(self.pixmappath + 'icons8-Replace Atom.png'), '&Replace',
                                   self, shortcut="Ctrl+R",
                                   statusTip="Replace Atom/Bond",
                                   triggered=self.setAction, objectName="Replace",
                                   checkable=True)
        self.actionActionGroup.addAction(self.replaceAction)

        self.rsAction = QAction( QIcon(self.pixmappath + 'Change_R_S.png'), 'To&ggle R/S',
                                   self, shortcut="Ctrl+G",
                                   statusTip="Toggle Stereo Chemistry",
                                   triggered=self.setAction, objectName="RStoggle",
                                   checkable=True)
        self.actionActionGroup.addAction(self.rsAction)

        self.ezAction = QAction( QIcon(self.pixmappath + 'Change_E_Z.png'), 'Toggle &E/Z',
                                   self, shortcut="Ctrl+E",
                                   statusTip="Toggle Bond Stereo Chemistry",
                                   triggered=self.setAction, objectName="EZtoggle",
                                   checkable=True)
        self.actionActionGroup.addAction(self.ezAction)


        self.removeAction = QAction( QIcon(self.pixmappath + 'icons8-Cancel.png'), 'D&elete',
                                   self, shortcut="Ctrl+D",
                                   statusTip="Delete Atom or Bond",
                                   triggered=self.setAction, objectName="Remove",
                                   checkable=True)
        self.actionActionGroup.addAction(self.removeAction)

        self.increaseChargeAction = QAction( QIcon(self.pixmappath + 'icons8-Increase Font.png'), 'I&ncrease Charge',
                                   self, shortcut="Ctrl++",
                                   statusTip="Increase Atom Charge",
                                   triggered=self.setAction, objectName="Increase Charge",
                                   checkable=True)
        self.actionActionGroup.addAction(self.increaseChargeAction)

        self.decreaseChargeAction = QAction( QIcon(self.pixmappath + 'icons8-Decrease Font.png'), 'D&ecrease Charge',
                                   self, shortcut="Ctrl+-",
                                   statusTip="Decrease Atom Charge",
                                   triggered=self.setAction, objectName="Decrease Charge",
                                   checkable=True)
        self.actionActionGroup.addAction(self.decreaseChargeAction)
        self.addAction.setChecked(True)


        #BondTypeActions
        self.bondtypeActionGroup = QtWidgets.QActionGroup(self, exclusive=True)

        self.singleBondAction = QAction( QIcon(self.pixmappath + 'icons8-Single.png'), 'S&ingle Bond',
                                   self, shortcut="Ctrl+1",
                                   statusTip="Set bondtype to SINGLE",
                                   triggered=self.setBondType, objectName="SINGLE",
                                   checkable=True)
        self.bondtypeActionGroup.addAction(self.singleBondAction)

        self.doubleBondAction = QAction( QIcon(self.pixmappath + 'icons8-Double.png'), 'Double Bond',
                                   self, shortcut="Ctrl+2",
                                   statusTip="Set bondtype to DOUBLE",
                                   triggered=self.setBondType, objectName="DOUBLE",
                                   checkable=True)
        self.bondtypeActionGroup.addAction(self.doubleBondAction)

        self.tripleBondAction = QAction( QIcon(self.pixmappath + 'icons8-Triple.png'), 'Triple Bond',
                                   self, shortcut="Ctrl+3",
                                   statusTip="Set bondtype to TRIPLE",
                                   triggered=self.setBondType, objectName="TRIPLE",
                                   checkable=True)
        self.bondtypeActionGroup.addAction(self.tripleBondAction)
        self.singleBondAction.setChecked(True)

        #Build dictionary of ALL available bondtypes in RDKit
        self.bondActions = {}
        for key in self.editor.bondtypes.keys():
            action = QAction( '%s'%key,
                                   self,
                                   statusTip="Set bondtype to %s"%key,
                                   triggered=self.setBondType, objectName=key,
                                   checkable=True)
            self.bondtypeActionGroup.addAction(action)
            self.bondActions[key] = action
        #Replace defined actions
        self.bondActions["SINGLE"] = self.singleBondAction
        self.bondActions["DOUBLE"] = self.doubleBondAction
        self.bondActions["TRIPLE"] = self.tripleBondAction

        #Misc Actions
        self.undoAction = QAction( QIcon(self.pixmappath + 'prev.png'), 'U&ndo',
                           self, shortcut="Ctrl+Z",
                           statusTip="Undo/Redo changes to molecule Ctrl+Z",
                           triggered=self.editor.undo, objectName="undo")

        self.clearCanvasAction = QAction( QIcon(self.pixmappath + 'icons8-Trash.png'), 'C&lear Canvas',
                                   self, shortcut="Ctrl+X",
                                   statusTip="Clear Canvas (no warning)",
                                   triggered=self.clearCanvas, objectName="Clear Canvas")

        self.cleanCoordinatesAction = QAction( QIcon(self.pixmappath + 'icons8-Broom.png'), 'Recalculate coordinates &F',
                                   self, shortcut="Ctrl+F",
                                   statusTip="Re-calculates coordinates and redraw",
                                   triggered=self.editor.canon_coords_and_draw, objectName="Recalculate Coordinates")


        #Atom Actions in actiongroup, reuse from ptable widget
        self.atomActions = []
        for atomname in ["H","B","C","N","O","F","P","S","Cl","Br","I"]:
            action = self.ptable.atomActions[atomname]
            if action.objectName() == "C":
                action.setChecked(True)
            self.atomActions.append(action)

        self.loglevelactions = {}
        for key in self.loglevels:
            self.loglevelactions[key] = QAction(key,
                                   self,
                                   statusTip="Set logging level to %s"%key,
                                   triggered=self.setLogLevel, objectName="loglevel:%s"%key)

# The main window class
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, fileName=None, loglevel="WARNING"):
        super(MainWindow,self).__init__()
        self.pixmappath = os.path.abspath(os.path.dirname(__file__)) + '/pixmaps/'
        self.loglevels = ["Critical","Error","Warning","Info","Debug","Notset"]
        self.moleditor = QrdEditor(parent=self, fileName=fileName, loglevel=loglevel)
        self._fileName = None
        self.initGUI(fileName = fileName)

    def initGUI(self, fileName=None):
        self.moleditor.initGUI(fileName)
        self.setWindowTitle("A simple mol editor")
        self.setWindowIcon(QIcon(self.pixmappath + 'appicon.svg.png'))
        self.setGeometry(100, 100, 200, 150)

        self.center = self.moleditor
        self.center.setFixedSize(600,600)
        self.setCentralWidget(self.center)

        self.SetupComponents()

        self.infobar = QLabel("")
        self.myStatusBar.addPermanentWidget(self.infobar, 0)

        self.moleditor.editor.sanitizeSignal.connect(self.infobar.setText)
        self.show()

    def SetupComponents(self):
        self.myStatusBar = QStatusBar()
        self.setStatusBar(self.myStatusBar)
        self.myStatusBar.showMessage('Ready', 10000)

        self.CreateMenus()

        self.mainToolBar = self.addToolBar(self.moleditor.mainToolBar)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.moleditor.sideToolBar)

        self.moleditor.mainToolBar.hide()
        self.moleditor.sideToolBar.hide()

    # Actual menu bar item creation
    def CreateMenus(self):
        self.fileMenu = self.menuBar().addMenu("&File")
        self.toolMenu = self.menuBar().addMenu("&Tools")
        self.atomtypeMenu = self.menuBar().addMenu("&AtomTypes")
        self.bondtypeMenu = self.menuBar().addMenu("&BondTypes")
        self.helpMenu = self.menuBar().addMenu("&Help")

        self.fileMenu.addAction(self.moleditor.openAction)
        self.fileMenu.addAction(self.moleditor.saveAction)
        self.fileMenu.addAction(self.moleditor.saveAsAction)
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.moleditor.exitAction)

        self.toolMenu.addAction(self.moleditor.selectAction)
        self.toolMenu.addAction(self.moleditor.addAction)
        self.toolMenu.addAction(self.moleditor.addBondAction)
        self.toolMenu.addAction(self.moleditor.replaceAction)
        self.toolMenu.addAction(self.moleditor.rsAction)
        self.toolMenu.addAction(self.moleditor.ezAction)
        self.toolMenu.addAction(self.moleditor.increaseChargeAction)
        self.toolMenu.addAction(self.moleditor.decreaseChargeAction)

        self.toolMenu.addSeparator()
        self.toolMenu.addAction(self.moleditor.cleanCoordinatesAction)
        self.toolMenu.addSeparator()
        self.toolMenu.addAction(self.moleditor.undoAction)
        self.toolMenu.addSeparator()
        self.toolMenu.addAction(self.moleditor.removeAction)


        #Atomtype menu
        for action in self.moleditor.atomActions:
            self.atomtypeMenu.addAction(action)
        self.specialatommenu = self.atomtypeMenu.addMenu("All Atoms")
        for atomnumber in self.moleditor.ptable.ptable.keys():
            atomname = self.moleditor.ptable.ptable[atomnumber]["Symbol"]
            self.specialatommenu.addAction(self.moleditor.ptable.atomActions[atomname])

        #Bondtype Menu
        self.bondtypeMenu.addAction(self.moleditor.singleBondAction)
        self.bondtypeMenu.addAction(self.moleditor.doubleBondAction)
        self.bondtypeMenu.addAction(self.moleditor.tripleBondAction)
        self.bondtypeMenu.addSeparator()
        #Bondtype Special types
        self.specialbondMenu = self.bondtypeMenu.addMenu("Special Bonds")
        for key in self.moleditor.bondActions.keys():
            self.specialbondMenu.addAction(self.moleditor.bondActions[key])
        #Help menu
        self.helpMenu.addAction(self.moleditor.aboutAction)
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.moleditor.aboutQtAction)
        #Debug level sub menu
        self.loglevelMenu = self.helpMenu.addMenu("Logging Level")
        for loglevel in self.loglevels:
            self.loglevelMenu.addAction(self.moleditor.loglevelactions[loglevel])

def launch(filename=None, loglevel="WARNING"):
    "Function that launches the mainWindow Application"
    # Exception Handling
    try:
        myApp = QApplication(sys.argv)
        mainWindow = MainWindow(fileName=filename, loglevel=loglevel)
        myApp.exec_()
        sys.exit(0)
    except NameError:
        print("Name Error:", sys.exc_info()[1])
    except SystemExit:
        print("Closing Window...")
    except Exception as e:
        print(sys.exc_info()[1])
        raise e


if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = None
    launch(filename=filename, loglevel="DEBUG")

