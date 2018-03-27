#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import os
import subprocess
from PyQt4 import QtGui, QtCore

class PapoInterface(QtGui.QWidget):
  def __init__(self, parent=None):
    super(PapoInterface, self).__init__(parent)
    inputLabel = QtGui.QLabel("MS Word input file:")
    self.inputLineEdit = QtGui.QLineEdit()
    self.inputBrowseButton = QtGui.QPushButton('Browse', self)
    outputLabel = QtGui.QLabel("XML output file:")
    self.outputLineEdit = QtGui.QLineEdit()
    self.outputBrowseButton = QtGui.QPushButton('Browse', self)
    templateLabel = QtGui.QLabel("XML template file:")
    self.templateLineEdit = QtGui.QLineEdit()
    self.templateBrowseButton = QtGui.QPushButton('Browse', self)
    self.debuggerTextEdit = QtGui.QTextEdit()
    self.runButton = QtGui.QPushButton('Run', self)
    self.doneButton = QtGui.QPushButton('Done', self)

    self.inputLineEdit.setReadOnly(True)
    self.outputLineEdit.setReadOnly(True)
    self.templateLineEdit.setReadOnly(True)
    self.debuggerTextEdit.setReadOnly(True)

    mainLayout = QtGui.QVBoxLayout()
    filesGridLayout = QtGui.QGridLayout()
    bottomButtonsLayout = QtGui.QHBoxLayout()

    filesGridLayout.addWidget(inputLabel, 0, 0)
    filesGridLayout.addWidget(self.inputLineEdit, 0, 1)
    filesGridLayout.addWidget(self.inputBrowseButton, 0, 2)
    filesGridLayout.addWidget(outputLabel, 1, 0)
    filesGridLayout.addWidget(self.outputLineEdit, 1, 1)
    filesGridLayout.addWidget(self.outputBrowseButton, 1, 2)
    filesGridLayout.addWidget(templateLabel, 2, 0)
    filesGridLayout.addWidget(self.templateLineEdit, 2, 1)
    filesGridLayout.addWidget(self.templateBrowseButton, 2, 2)

    bottomButtonsLayout.addStretch(1)
    bottomButtonsLayout.addWidget(self.runButton)
    bottomButtonsLayout.addWidget(self.doneButton)

    mainLayout.addLayout(filesGridLayout)
    mainLayout.addWidget(self.debuggerTextEdit)
    mainLayout.addLayout(bottomButtonsLayout)

    self.setLayout(mainLayout)
    self.setWindowTitle("PaPo Interface")
    self.inputBrowseButton.clicked.connect(self.browseDocxFiles)
    self.outputBrowseButton.clicked.connect(self.browseAndSetOutput)
    self.templateBrowseButton.clicked.connect(self.browseXmlFiles)
    self.runButton.clicked.connect(self.run)
    self.doneButton.clicked.connect(QtCore.QCoreApplication.instance().quit)

  def browseDocxFiles(self, extentions):
    fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.', 'MS Word document (*.docx)')
    self.inputLineEdit.clear()
    self.inputLineEdit.setText(fname)

  def browseXmlFiles(self, extentions):
    fname = QtGui.QFileDialog.getOpenFileName(self, 'Open file', '.', 'XML file (*.xml)')
    self.templateLineEdit.clear()
    self.templateLineEdit.setText(fname)

  def browseAndSetOutput(self, extentions):
    fname = QtGui.QFileDialog.getSaveFileName(self, 'Save file', '.')
    self.outputLineEdit.clear()
    self.outputLineEdit.setText(fname)

  def run(self):
    in_path = self.inputLineEdit.text()
    out_path = self.outputLineEdit.text()
    template_path = self.templateLineEdit.text()

    if(not in_path or not out_path or not template_path):
      QtGui.QMessageBox.warning(self,'Blank fields', 'please, fill all the options before running PaPo.')
    else:
      try:
        std = subprocess.check_output([r'papo_docx2xml', in_path, out_path])
        self.debuggerTextEdit.setTextColor(QtGui.QColor('green'))
        self.debuggerTextEdit.append('Success!')
        self.debuggerTextEdit.setTextColor(QtGui.QColor('black'))
        self.debuggerTextEdit.append('Output file written at {0}'.format(out_path))
      except subprocess.CalledProcessError as e:
        self.debuggerTextEdit.setTextColor(QtGui.QColor('red'))
        self.debuggerTextEdit.append('ERROR!')
        self.debuggerTextEdit.setTextColor(QtGui.QColor('black'))
        self.debuggerTextEdit.append('\tParser found an error after')
        output_list = e.output.split('\n')
        self.debuggerTextEdit.append('\t\t' + output_list[-2])
      try:
        self.debuggerTextEdit.append('Filling template file...')
        std_filling_template = subprocess.check_output([r'papo_fill_template', template_path, out_path])
        self.debuggerTextEdit.setTextColor(QtGui.QColor('green'))
        self.debuggerTextEdit.append('Success!')
        self.debuggerTextEdit.setTextColor(QtGui.QColor('black'))
        self.debuggerTextEdit.append('Your xml file is ready to be used on the Password Policy Software')
      except subprocess.CalledProcessError as e:
        self.debuggerTextEdit.setTextColor(QtGui.QColor('red'))
        self.debuggerTextEdit.append('ERROR!')
        self.debuggerTextEdit.setTextColor(QtGui.QColor('black'))
        self.debuggerTextEdit.append(e.output)

#if __name__ == '__main__':
def main():
  app = QtGui.QApplication(sys.argv)

  papo_gui = PapoInterface()
  papo_gui.show()

  sys.exit(app.exec_())

