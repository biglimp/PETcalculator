# -*- coding: utf-8 -*-

from PyQt5 import uic, QtWidgets
import sys
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox
import numpy as np
import os.path
import webbrowser

#from __future__ import absolute_import
#from builtins import str
#from builtins import range
#from builtins import object
#from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
#from qgis.PyQt.QtWidgets import QFileDialog, QMessageBox, QAction
#from qgis.PyQt.QtGui import QIcon
#from .metdata_processor_dialog import MetdataProcessorDialog
#import numpy as np
#import webbrowser

class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('metdata_processor_dialog_base.ui', self)
        self.show()

        self.pushButtonImport.clicked.connect(self.import_file)
        self.pushButtonExport.clicked.connect(self.start_progress)
        self.helpButton.clicked.connect(self.help)
        self.fileDialog = QFileDialog()

    def import_file(self):
        if self.checkBoxEPW.isChecked():
            result = self.fileDialog.exec_()
            self.pushButtonExport.setEnabled(True)
            self.folderPath = self.fileDialog.selectedFiles()
            self.textInput.setText(self.folderPath[0])
            if result == 1:
                try:
                    self.data = np.genfromtxt(self.folderPath[0], skip_header=8, delimiter=',', filling_values=99999)
                    QMessageBox.information(self, "EPW file imported",
                                            "No time or meteorological variables need to be specified. "
                                            "Press 'Export data' to continue to generate a formatted text-file.")
                except Exception as e:
                    QMessageBox.critical(self, "Error: Check the number of columns in each line", str(e))
                    return
        else:
            self.comboBox_yyyy.clear()
            self.comboBox_doy.clear()
            self.comboBox_month.clear()
            self.comboBox_dom.clear()
            self.comboBox_dectime.clear()
            self.comboBox_hour.clear()
            self.comboBox_minute.clear()
            self.comboBox_RH.clear()
            self.comboBox_Tair.clear()
            self.comboBox_Wd.clear()
            self.comboBox_Wuh.clear()
            self.comboBox_fcld.clear()
            self.comboBox_kdiff.clear()
            self.comboBox_kdir.clear()
            self.comboBox_kdown.clear()
            self.comboBox_lai.clear()
            self.comboBox_ldown.clear()
            self.comboBox_pres.clear()
            self.comboBox_qe.clear()
            self.comboBox_qf.clear()
            self.comboBox_qh.clear()
            self.comboBox_qn.clear()
            self.comboBox_qs.clear()
            self.comboBox_rain.clear()
            self.comboBox_snow.clear()
            self.comboBox_ws.clear()
            self.comboBox_xsmd.clear()
            self.fileDialog.open()
            result = self.fileDialog.exec_()
            if result == 1:
                self.pushButtonExport.setEnabled(True)
                self.folderPath = self.fileDialog.selectedFiles()
                self.textInput.setText(self.folderPath[0])
                headernum = self.spinBoxHeader.value()
                delimnum = self.comboBox_sep.currentIndex()
                delim = None
                if delimnum == 0:
                    delim = ','
                elif delimnum == 1:
                    delim = None  # space
                elif delimnum == 2:
                    delim = None  # '\t'
                elif delimnum == 3:
                    delim = ';'
                elif delimnum == 4:
                    delim = ':'

                f = open(self.folderPath[0])
                header = f.readline().split(delim)

                for i in range(0, header.__len__()):
                    self.comboBox_yyyy.addItem(header[i])
                    self.comboBox_doy.addItem(header[i])
                    self.comboBox_month.addItem(header[i])
                    self.comboBox_dom.addItem(header[i])
                    self.comboBox_dectime.addItem(header[i])
                    self.comboBox_hour.addItem(header[i])
                    self.comboBox_minute.addItem(header[i])
                    self.comboBox_RH.addItem(header[i])
                    self.comboBox_Tair.addItem(header[i])
                    self.comboBox_Wd.addItem(header[i])
                    self.comboBox_Wuh.addItem(header[i])
                    self.comboBox_fcld.addItem(header[i])
                    self.comboBox_kdiff.addItem(header[i])
                    self.comboBox_kdir.addItem(header[i])
                    self.comboBox_kdown.addItem(header[i])
                    self.comboBox_lai.addItem(header[i])
                    self.comboBox_ldown.addItem(header[i])
                    self.comboBox_pres.addItem(header[i])
                    self.comboBox_qe.addItem(header[i])
                    self.comboBox_qf.addItem(header[i])
                    self.comboBox_qh.addItem(header[i])
                    self.comboBox_qn.addItem(header[i])
                    self.comboBox_qs.addItem(header[i])
                    self.comboBox_rain.addItem(header[i])
                    self.comboBox_snow.addItem(header[i])
                    self.comboBox_ws.addItem(header[i])
                    self.comboBox_xsmd.addItem(header[i])

                try:
                    self.data = np.genfromtxt(self.folderPath[0], skip_header=headernum, delimiter=delim,
                                              filling_values=99999)
                    QMessageBox.information(self, "File imported", "If invalid data was detected such as strings or "
                                                                   "other non-numrical characters, these data points could "
                                                                   "result in that the MetdataProcessor "
                                                                   "will fail to create your formatted inputdata.") #, 'Continue'
                except Exception as e:
                    QMessageBox.critical(self, "Error: Check the number of columns in each line", str(e))
                    return

    def epw2umep(self, met_old):
        met_new = np.zeros((met_old.shape[0], 24)) - 999

        # yyyy
        met_new[:, 0] = 1985
        met_new[met_old.shape[0] - 1, 0] = 1986

        # hour
        met_new[:, 2] = met_old[:, 3]
        test = met_new[:, 2] == 24
        met_new[test, 2] = 0

        # day of year
        mm = met_old[:, 1]
        dd = met_old[:, 2]
        rownum = met_old.shape[0]
        for i in range(0, rownum):
            yy = int(met_new[i, 0])
            if (yy % 4) == 0:
                if (yy % 100) == 0:
                    if (yy % 400) == 0:
                        leapyear = 1
                    else:
                        leapyear = 0
                else:
                    leapyear = 1
            else:
                leapyear = 0
            if leapyear == 1:
                dayspermonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            else:
                dayspermonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            met_new[i, 1] = sum(dayspermonth[0:int(mm[i] - 1)]) + dd[i]

        test2 = np.where(met_new[:, 2] == 0)
        met_new[np.where(met_new[:, 2] == 0), 1] = met_new[np.where(met_new[:, 2] == 0), 1] + 1
        met_new[met_old.shape[0] - 1, 1] = 1

        # minute
        met_new[:, 3] = 0

        # met variables
        met_new[:, 11] = met_old[:, 6]  # Ta
        met_new[:, 10] = met_old[:, 8]  # Rh
        met_new[:, 12] = met_old[:, 9] / 1000.  # P
        met_new[:, 16] = met_old[:, 12]  # Ldown
        met_new[:, 14] = met_old[:, 13]  # Kdown
        met_new[:, 22] = met_old[:, 14]  # Kdir
        met_new[:, 21] = met_old[:, 15]  # Kdiff
        met_new[:, 23] = met_old[:, 20]  # Wdir
        met_new[:, 9] = met_old[:, 21]  # Ws
        met_new[:, 13] = met_old[:, 33]  # Rain
        met_new[np.where(met_new[:, 13] == 999), 13] = 0

        return met_new

    def start_progress(self):

        outputfile = self.fileDialog.getSaveFileName(None, "Save File As:", None, "Text Files (*.txt)")

        if not outputfile[0]:
            QMessageBox.critical(None, "Error", "An output text file (.txt) must be specified")
            return

        met_old = self.data
        met_new = np.zeros((met_old.shape[0], 24)) - 999

        if self.checkBoxEPW.isChecked():
            self.progressBar.setRange(0, 23)
            met_new = self.epw2umep(met_old)
            norain = np.sum(met_new[:, 13])
            if norain == 0:
                QMessageBox.critical(None, "Value error", "No precipitation found in EPW-file. Find alternative "
                                                          "data source if rain is required (e.g. SUEWS).")
            # if np.min(met_new[:, 9]) == 0.0:
            #     QMessageBox.critical(None, "Wind speed = 0.0", "The SUEWS model cannot found in EPW-file. Find alternative "
            #                                               "data source if rain is required (e.g. SUEWS).")


            self.progressBar.setValue(23)
        else:
            self.progressBar.setRange(0, 23)

            rownum = self.data.shape[0]

            if self.checkBoxYear.isChecked():
                yyyy_col = self.comboBox_yyyy.currentIndex()
                met_new[:, 0] = met_old[:, yyyy_col]
            else:
                met_new[:, 0] = self.spinBoxYear.value()

            self.progressBar.setValue(1)

            if self.checkBoxDOY.isChecked():
                doy_col = self.comboBox_doy.currentIndex()
                met_new[:, 1] = met_old[:, doy_col]
            else:
                mm = met_old[:, self.comboBox_month.currentIndex()]
                dd = met_old[:, self.comboBox_dom.currentIndex()]
                for i in range(0, rownum):
                    yy = int(met_new[i, 0])
                    if (yy % 4) == 0:
                        if (yy % 100) == 0:
                            if (yy % 400) == 0:
                                leapyear = 1
                            else:
                                leapyear = 0
                        else:
                            leapyear = 1
                    else:
                        leapyear = 0
                    if leapyear == 1:
                        dayspermonth = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    else:
                        dayspermonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                    met_new[i, 1] = sum(dayspermonth[0:int(mm[i] - 1)]) + dd[i]

            self.progressBar.setValue(2)

            if self.checkBoxDectime.isChecked():
                dectime_col = self.comboBox_dectime.currentIndex()
                timeres_old = np.round((met_old[1, dectime_col] - met_old[0, dectime_col]) * (60. * 24.))
                nsh = int(timeres_old / 5)
                # QMessageBox.information(None, "Metdata pre-processor", str(timeres_old))

                first_hour = (met_old[0, dectime_col] - np.floor(met_old[0, dectime_col])) * 24
                met_new[0, 2] = first_hour
                first_min = np.round((met_new[0, 2] - np.floor(met_new[0, 2])) * 60)
                met_new[0, 3] = first_min

                for t in range(1, rownum):
                    # min_now = first_hour + timeres_old
                    met_new[t, 3] = met_new[(t - 1), 3] + timeres_old
                    met_new[t, 2] = met_new[(t - 1), 2]
                    if (met_new[t, 3] >= 60) and (met_new[t, 3] < 120):
                        met_new[t, 3] = int(met_new[t, 3] - 60)
                        met_new[t, 2] = met_new[t, 2] + 1
                    if (met_new[t, 3] >= 120) and (met_new[t, 3] < 180):
                        met_new[t, 3] = int(met_new[t, 3] - 120)
                        met_new[t, 2] = met_new[t, 2] + 2
                    if met_new[t, 3] >= 180:
                        met_new[t, 3] = int(met_new[t, 3] - 180)
                        met_new[t, 2] = met_new[t, 2] + 3
                    if met_new[t, 2] >= 24:
                        met_new[t, 2] = 0
                    # else:
                    #     met_new[t, 2] = met_new[(t - 1), 2]

                # dechour = (met_old[:, dectime_col] - np.floor(met_old[:, dectime_col])) * 24
                # met_new[:, 2] = dechour
                # minute = np.round((dechour - np.floor(dechour)) * 60)
                # minute[(minute == 60)] = 0
                # changehour = np.where(minute == 60)
                # dechour[changehour] = dechour + 1
                # met_new[:, 3] = minute
            else:
                met_new[:, 2] = met_old[:, self.comboBox_hour.currentIndex()]
                met_new[:, 3] = met_old[:, self.comboBox_minute.currentIndex()]
                nshhh= int(abs((met_new[1, 2] - met_new[0, 2])) * 12)
                nshmin = int(abs((met_new[1, 3] - met_new[0, 3])) / 5)
                nsh = nshhh + nshmin

            # Check if time gap exists
            #for i in range(0, met_new.shape[0] - 1):
            #    dectime0 = met_new[i, 0] + met_new[i, 1] + met_new[i, 2] / 24. + met_new[i, 3] / (60. * 24.)
            #    dectime1 = met_new[i + 1, 0] + met_new[i + 1, 1] + met_new[i + 1, 2] / 24. + met_new[i + 1, 3] / (60. * 24.)
            #    timeres_old = np.round((dectime1 - dectime0) * (60. * 24.))
            #    nshtest = int(timeres_old / 5)
            #    if nshtest > nsh:
            #        QMessageBox.critical(None, "Input data is not continuous", "There seems to be a time gap at line:"
            #                                                  " \n" + str(i + 1))
            #        return

            self.progressBar.setValue(3)

            # Met variables
            if self.checkBox_kdown.isChecked():
                met_new[:, 14] = met_old[:, self.comboBox_kdown.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 14] < 0.0) | (met_new[:, 14] > 1200.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Kdown - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 14] = -999.0

            self.progressBar.setValue(4)

            if self.checkBox_ws.isChecked():
                met_new[:, 9] = met_old[:, self.comboBox_ws.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 9] <= 0) | (met_new[:, 9] > 60.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Wind speed - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 9] = -999.0

            self.progressBar.setValue(5)

            if self.checkBox_Tair.isChecked():
                met_new[:, 11] = met_old[:, self.comboBox_Tair.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 11] < -30.0) | (met_new[:, 11] > 55.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Air temperature - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 11] = -999.0

            self.progressBar.setValue(6)

            if self.checkBox_RH.isChecked():
                met_new[:, 10] = met_old[:, self.comboBox_RH.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 10] < 0.00) | (met_new[:, 10] > 100.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Relative humidity - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 10] = -999.0

            self.progressBar.setValue(7)

            if self.checkBox_pres.isChecked():
                met_new[:, 12] = met_old[:, self.comboBox_pres.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 12] < 70.0) | (met_new[:, 12] > 107.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Pressure - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 12] = -999.0

            self.progressBar.setValue(8)

            if self.checkBox_rain.isChecked():
                met_new[:, 13] = met_old[:, self.comboBox_rain.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where(((met_new[:, 13] / nsh) < 0.0) | ((met_new[:, 13] / nsh) > 30.0))
                    #QMessageBox.critical(None, "Test", met_new[0, 13] / nsh)
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Rain - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 13] = -999.0

            self.progressBar.setValue(9)

            if self.checkBox_snow.isChecked():
                met_new[:, 15] = met_old[:, self.comboBox_snow.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where(((met_new[:, 15] / nsh) < 0.0) | ((met_new[:, 15] / nsh) > 300.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Snow - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 15] = -999.0

            self.progressBar.setValue(10)

            if self.checkBox_ldown.isChecked():
                met_new[:, 16] = met_old[:, self.comboBox_ldown.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 16] < 100.0) | (met_new[:, 16] > 600.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Ldown - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 16] = -999.0

            self.progressBar.setValue(11)

            if self.checkBox_fcld.isChecked():
                met_new[:, 17] = met_old[:, self.comboBox_fcld.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 17] < 0.0) | (met_new[:, 17] > 1.01))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Fraction of cloud - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 17] = -999.0

            self.progressBar.setValue(12)

            if self.checkBox_Wuh.isChecked():
                met_new[:, 18] = met_old[:, self.comboBox_Wuh.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where(((met_new[:, 18] / nsh) < 0.0) | ((met_new[:, 18] / nsh) > 10.01))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "External water use - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 18] = -999.0

            self.progressBar.setValue(13)

            if self.checkBox_xcmd.isChecked():
                met_new[:, 19] = met_old[:, self.comboBox_xcmd.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 19] < 0.01) | (met_new[:, 19] > 0.5))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Soil moisture - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 19] = -999.0

            self.progressBar.setValue(14)

            if self.checkBox_lai.isChecked():
                met_new[:, 20] = met_old[:, self.comboBox_lai.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 20] < 0.0) | (met_new[:, 20] > 15.01))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Leaf area index - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 20] = -999.0

            self.progressBar.setValue(15)

            if self.checkBox_kdiff.isChecked():
                met_new[:, 21] = met_old[:, self.comboBox_kdiff.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 21] < 0.0) | (met_new[:, 21] > 600.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Diffuse shortwave radiation - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 21] = -999.0

            self.progressBar.setValue(16)

            if self.checkBox_kdir.isChecked():
                met_new[:, 22] = met_old[:, self.comboBox_kdir.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 22] < 0.0) | (met_new[:, 22] > 1200.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Direct shortwave radiation - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 22] = -999.0

            self.progressBar.setValue(17)

            if self.checkBox_Wd.isChecked():
                met_new[:, 23] = met_old[:, self.comboBox_Wd.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 23] < 0.0) | (met_new[:, 23] > 360.01))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Wind directions - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 23] = -999.0

            self.progressBar.setValue(18)

            if self.checkBox_qn.isChecked():
                met_new[:, 4] = met_old[:, self.comboBox_qn.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 4] < -200.0) | (met_new[:, 4] > 800.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Net radiation - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 4] = -999.0

            self.progressBar.setValue(19)

            if self.checkBox_qh.isChecked():
                met_new[:, 5] = met_old[:, self.comboBox_qh.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 5] < -200.0) | (met_new[:, 5] > 750.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Sensible heat flux - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 5] = -999.0

            self.progressBar.setValue(20)

            if self.checkBox_qe.isChecked():
                met_new[:, 6] = met_old[:, self.comboBox_qe.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 6] < -100.0) | (met_new[:, 6] > 650.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Latent heat flux - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 6] = -999.0

            self.progressBar.setValue(21)

            if self.checkBox_qs.isChecked():
                met_new[:, 7] = met_old[:, self.comboBox_qs.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 7] < -200.0) | (met_new[:, 7] > 650.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Storage heat flux - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 7] = -999.0

            self.progressBar.setValue(22)

            if self.checkBox_qf.isChecked():
                met_new[:, 8] = met_old[:, self.comboBox_qf.currentIndex()]
                if self.checkBoxQuality.isChecked():
                    testwhere = np.where((met_new[:, 8] < 0.0) | (met_new[:, 8] > 1500.0))
                    if testwhere[0].__len__() > 0:
                        QMessageBox.critical(None, "Value error", "Anthropogenic heat flux - beyond what is expected at line:"
                                                                  " \n" + str(testwhere[0] + 1))
                        return
            else:
                met_new[:, 8] = -999.0

                self.progressBar.setValue(23)

        # Quality control


        # if self.checkBoxSOLWEIG.isChecked(): #NOT READY
        #     # Moving one hour
        #     Ta[1:np.size(Ta)] = Ta[0:np.size(Ta) - 1]
        #     Ta[0] = Ta[1]
        #     RH[1:np.size(RH)] = RH[0:np.size(RH) - 1]
        #     RH[0] = RH[1]
        #     G[1:np.size(G)] = G[0:np.size(G) - 1]
        #     G[0] = G[1]
        #     D[1:np.size(D)] = D[0:np.size(D) - 1]
        #     D[0] = D[1]
        #     I[1:np.size(I)] = I[0:np.size(I) - 1]
        #     I[0] = I[1]
        #     Ws[1:np.size(Ws)] = Ws[0:np.size(Ws) - 1]
        #     Ws[0] = Ws[1]
                                                                  #
        header = '%iy  id  it imin   Q*      QH      QE      Qs      Qf    Wind    RH     Td     press   rain ' \
                 '   Kdn    snow    ldown   fcld    wuh     xsmd    lai_hr  Kdiff   Kdir    Wd'
        # #Save as text files
        # numformat = '%3d %2d %3d %2d %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f ' \
        #             '%6.2f %6.2f %6.2f %6.2f %6.2f %6.2f %6.2f'
        numformat = '%d %d %d %d %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f %.2f ' \
                    '%.2f %.2f %.2f %.2f %.2f %.2f %.2f'
        np.savetxt(outputfile[0], met_new, fmt=numformat, header=header, comments='')

        self.progressBar.setValue(23)

        QMessageBox.information(None, "Metdata pre-processor", "Input data to PET-calculator generated")

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.show()
        self.exec_()

    def help(self):
        url = 'https://umep-docs.readthedocs.io/en/latest/pre-processor/Meteorological%20Data%20MetPreprocessor.html'
        webbrowser.open_new_tab(url)

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()