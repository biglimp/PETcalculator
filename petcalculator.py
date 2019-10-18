
from PyQt5 import uic, QtWidgets
import sys
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox
import numpy as np
import Solweig_v2015_metdata_noload as metload
import clearnessindex_2013b as ci
import diffusefraction as df
import Solweig1D_2019a_calc as so
import PET_calculations as p
import UTCI_calculations as utci


class Ui(QtWidgets.QDialog):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('PETCalculator.ui', self)
        self.show()

        self.runButton.clicked.connect(self.start_calculation)
        self.pushButtonSave.clicked.connect(self.folder_path_out)
        self.fileDialog = QFileDialog()
        self.fileDialog.setFileMode(QFileDialog.Directory)
        self.fileDialog.setOption(QFileDialog.ShowDirsOnly, True)

        self.pushButtonImportMetData.clicked.connect(self.met_file)
        self.fileDialogMet = QFileDialog()
        self.fileDialogMet.setNameFilter("(*.txt)")

        self.CheckBoxHumanDefault.clicked.connect(self.set_Default_human)
        self.CheckBoxEnvironDefault.clicked.connect(self.set_Default_environ)
        self.comboBoxSky.currentIndexChanged.connect(self.setRadiation)
        self.CheckBoxBoxSkyCondition.clicked.connect(self.set_clear)
        self.outputfile = None

    def folder_path_out(self):
        self.outputfile = self.fileDialog.getSaveFileName(None, "Save File As:", None, "Text Files (*.txt)")

        if not self.outputfile[0]:
            QMessageBox.critical(None, "Error", "An output text file (.txt) must be specified")
            return
        else:
            self.textOutput.setText(self.outputfile[0])

    def met_file(self):
        self.fileDialogMet.open()
        result = self.fileDialogMet.exec_()
        if result == 1:
            self.folderPathMet = self.fileDialogMet.selectedFiles()
            self.textInputMetdata.setText(self.folderPathMet[0])

    def set_clear(self):
        self.comboBoxSky.setCurrentIndex(1)
        self.setRadiation()

    def setRadiation(self):
        Ta = self.doubleSpinBoxTa.value()
        RH = self.doubleSpinBoxRH.value()
        date = self.calendarWidget.selectedDate()
        year = date.year()
        month = date.month()
        day = date.day()
        time = self.spinBoxTimeEdit.time()
        hour = time.hour()
        minu = time.minute()
        doy = self.day_of_year(year, month, day)
        lat = self.doubleSpinBoxLatitude.value()
        lon = self.doubleSpinBoxLongitude.value()
        if lon > 180.:
            lon = lon - 180.

        metdata = np.zeros((1, 24)) - 999.
        metdata[0, 0] = year
        metdata[0, 1] = doy
        metdata[0, 2] = hour
        metdata[0, 3] = minu
        metdata[0, 11] = Ta
        metdata[0, 10] = RH

        UTC = self.spinBoxUTC.value()
        location = {'longitude': lon, 'latitude': lat, 'altitude': 3.}
        P = -999.
        radG = 40.
        
        YYYY, altitude, azimuth, zen, jday, leafon, dectime, altmax = metload.Solweig_2015a_metdata_noload(metdata, location, UTC)
        if altitude > 0.:
            I0, _, Kt, _, _ = ci.clearnessindex_2013b(zen, jday, Ta, RH / 100., radG, location, P)
        
            if self.comboBoxSky.currentIndex() == 1:
                radG = I0 
            elif self.comboBoxSky.currentIndex() == 2:
                radG = I0 * 0.8
            elif self.comboBoxSky.currentIndex() == 3:
                radG = I0 * 0.6
            else:
                radG = I0 * 0.4

            I0, _, Kt, _, _ = ci.clearnessindex_2013b(zen, jday, Ta, RH / 100., radG, location, P)
            radI, radD = df.diffusefraction(radG, altitude, Kt, Ta, RH)
        
        else:
            radG = 0.
            radD = 0.
            radI = 0.
        
        self.doubleSpinBoxradG.setValue(radG)
        self.doubleSpinBoxradD.setValue(radD)
        self.doubleSpinBoxradI.setValue(radI)

    def day_of_year(self, yyyy, month, day):
        if (yyyy % 4) == 0:
            if (yyyy % 100) == 0:
                if (yyyy % 400) == 0:
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

        doy = np.sum(dayspermonth[0:month - 1]) + day

        return doy

    def set_Default_human(self):
        self.doubleSpinBoxShortwaveHuman.setValue(0.70)
        self.doubleSpinBoxLongwaveHuman.setValue(0.95)
        self.comboBox_posture.setCurrentIndex(0)
        self.doubleSpinBoxWeight.setValue(75)
        self.doubleSpinBoxHeight.setValue(180)
        self.doubleSpinBoxClo.setValue(0.9)
        self.doubleSpinBoxAge.setValue(35)
        self.doubleSpinBoxActivity.setValue(80)
        self.comboBoxGender.setCurrentIndex(0)
        self.CheckBoxBox.setChecked(True)

    def set_Default_environ(self):
        self.doubleSpinBoxAlbedo_w.setValue(0.2)
        self.doubleSpinBoxAlbedo_g.setValue(0.15)
        self.doubleSpinBoxEmis_w.setValue(0.9)
        self.doubleSpinBoxEmis_g.setValue(0.95)
        self.doubleSpinBoxSVF.setValue(0.6)

    def read_metdata(self):
        headernum = 1
        delim = ' '
        try:
            self.metdata = np.loadtxt(self.folderPathMet[0], skiprows=headernum, delimiter=delim)
        except:
            QMessageBox.critical(self, "Import Error",
                                 "Make sure format of meteorological file is correct. You can "
                                 "prepare your data by using 'Prepare Existing Data' in "
                                 "the Pre-processor")
            return

        if self.metdata.shape[1] == 24:
            test = 4
        else:
            QMessageBox.critical(self, "Import Error",
                                 "Wrong number of columns in meteorological data. You can "
                                 "prepare your data by using 'Prepare Existing Data'")
            return

    def start_calculation(self):
        
        sh = 1.  # 0 if shadowed by building
        vegsh = 1.  # 0 if shadowed by tree
        svfveg = 1.
        svfaveg = 1.
        trans = 1.
        elvis = 0

        # Location and time settings
        UTC = self.spinBoxUTC.value()
        lat = self.doubleSpinBoxLatitude.value()
        lon = self.doubleSpinBoxLongitude.value()

        if lon > 180.:
            lon = lon - 180.
     
        # Human parameter data
        if self.CheckBoxHumanDefault.isChecked():
            absK = 0.70
            absL = 0.95
            pos = 0
            mbody = 75.
            ht = 180 / 100.
            clo = 0.9
            age = 35
            activity = 80.
            sex = 1
        else:
            absK = self.doubleSpinBoxShortwaveHuman.value()
            absL = self.doubleSpinBoxLongwaveHuman.value()
            pos = self.comboBox_posture.currentIndex()
            mbody = self.doubleSpinBoxWeight.value()
            ht = self.doubleSpinBoxHeight.value() / 100
            clo = self.doubleSpinBoxClo.value()
            age = self.doubleSpinBoxAge.value()
            activity = self.doubleSpinBoxActivity.value()
            sex = self.comboBoxGender.currentIndex() + 1
            
        if pos == 0:
            Fside = 0.22
            Fup = 0.06
            height = 1.1
            Fcyl = 0.28
        else:
            Fside = 0.166666
            Fup = 0.166666
            height = 0.75
            Fcyl = 0.2

        if self.CheckBoxBox.isChecked():
            cyl = 1
        else:
            cyl = 0

        ani = 1
          
        # Environmental data
        albedo_b = self.doubleSpinBoxAlbedo_w.value()
        albedo_g = self.doubleSpinBoxAlbedo_g.value()
        ewall = self.doubleSpinBoxEmis_w.value()
        eground = self.doubleSpinBoxEmis_g.value()
        svf = self.doubleSpinBoxSVF.value()
        
        # Meteorological data
        sensorheight = self.doubleSpinBoxWsHt.value() 
        onlyglobal = 0
        if self.CheckBoxMetData.isChecked():
            self.read_metdata()
            metfileexist = 1
            PathMet = self.folderPathMet[0]
            if self.checkBoxUseOnlyGlobal.isChecked():
                onlyglobal = 1
            else:
                onlyglobal = 0
        else:
            metfileexist = 0
            PathMet = None
            self.metdata = np.zeros((1, 24)) - 999.

            date = self.calendarWidget.selectedDate()
            year = date.year()
            month = date.month()
            day = date.day()
            time = self.spinBoxTimeEdit.time()
            hour = time.hour()
            minu = time.minute()
            doy = self.day_of_year(year, month, day)

            Ta = self.doubleSpinBoxTa.value()
            RH = self.doubleSpinBoxRH.value()
            radG = self.doubleSpinBoxradG.value()
            radD = self.doubleSpinBoxradD.value()
            radI = self.doubleSpinBoxradI.value()
            Ws = self.doubleSpinBoxWs.value()

            self.metdata[0, 0] = year
            self.metdata[0, 1] = doy
            self.metdata[0, 2] = hour
            self.metdata[0, 3] = minu
            self.metdata[0, 11] = Ta
            self.metdata[0, 10] = RH
            self.metdata[0, 14] = radG
            self.metdata[0, 21] = radD
            self.metdata[0, 22] = radI
            self.metdata[0, 9] = Ws

        location = {'longitude': lon, 'latitude': lat, 'altitude': 3.}
        YYYY, altitude, azimuth, zen, jday, leafon, dectime, altmax = metload.Solweig_2015a_metdata_noload(self.metdata, location, UTC)

        svfalfa = np.arcsin(np.exp((np.log((1.-svf))/2.)))

        # %Creating vectors from meteorological input
        DOY = self.metdata[:, 1]
        hours = self.metdata[:, 2]
        minu = self.metdata[:, 3]
        Ta = self.metdata[:, 11]
        RH = self.metdata[:, 10]
        radG = self.metdata[:, 14]
        radD = self.metdata[:, 21]
        radI = self.metdata[:, 22]
        P = self.metdata[:, 12]
        Ws = self.metdata[:, 9]

        TgK = 0.37
        Tstart = -3.41
        TmaxLST = 15
        TgK_wall = 0.58
        Tstart_wall = -3.41
        TmaxLST_wall = 15
        
        # Check if diffuse and direct radiation exist
        if metfileexist == 1:
            if onlyglobal == 0:
                if np.min(radD) == -999:
                    QMessageBox.critical(self, "Diffuse radiation include NoData values",
                                            'Tick in the box "Estimate diffuse and direct shortwave..." or aqcuire '
                                            'observed values from external data sources.')
                    return
                if np.min(radI) == -999:
                    QMessageBox.critical(self, "Direct radiation include NoData values",
                                            'Tick in the box "Estimate diffuse and direct shortwave..." or aqcuire '
                                            'observed values from external data sources.')
                    return

        self.progressBar.setRange(0, Ta.__len__())

        # If metfile starts at night
        CI = 1.

        if ani == 1:
            skyvaultalt = np.atleast_2d([])
            skyvaultazi = np.atleast_2d([])
            skyvaultaltint = [6, 18, 30, 42, 54, 66, 78]
            skyvaultaziint = [12, 12, 15, 15, 20, 30, 60]
            for j in range(7):
                for k in range(1, int(360/skyvaultaziint[j]) + 1):
                    skyvaultalt = np.append(skyvaultalt, skyvaultaltint[j])

            skyvaultalt = np.append(skyvaultalt, 90)

            diffsh = np.zeros((145))
            svfalfadeg = svfalfa / (np.pi / 180.)
            for k in range(0, 145):
                if skyvaultalt[k] > svfalfadeg:
                    diffsh[k] = 1
        else:
            diffsh = []

        numformat = '%3d %2d %3d %2d %6.5f ' + '%6.2f ' * 29
        poi_save = np.zeros((1, 34))

        if self.CheckBoxMetData.isChecked():
            header = 'yyyy id   it imin dectime altitude azimuth kdir kdiff kglobal kdown   kup    keast ksouth ' \
                                'kwest knorth ldown   lup    least lsouth lwest  lnorth   Ta      Tg     RH    Esky   Tmrt    ' \
                                'I0     CI   Shadow  SVF_b KsideI PET  UTCI'
        
            if not self.outputfile:
                QMessageBox.critical(None, "No specified output information", "An output text file (.txt) must be specified")
                return
            else:
                data_out = self.outputfile[0]
        
            np.savetxt(data_out, [],  delimiter=' ', header=header, comments='')  # fmt=numformat,

        for i in np.arange(0, Ta.__len__()):
            #print(i)
            # Daily water body temperature
            if (dectime[i] - np.floor(dectime[i])) == 0 or (i == 0):
                Twater = np.mean(Ta[jday[0] == np.floor(dectime[i])])

            # Nocturnal cloudfraction from Offerle et al. 2003
            if (dectime[i] - np.floor(dectime[i])) == 0:
                daylines = np.where(np.floor(dectime) == dectime[i])
                alt = altitude[0][daylines]
                alt2 = np.where(alt > 1)
                rise = alt2[0][0]
                [_, CI, _, _, _] = ci.clearnessindex_2013b(zen[0, i + rise + 1], jday[0, i + rise + 1],
                                                        Ta[i + rise + 1],
                                                        RH[i + rise + 1] / 100., radG[i + rise + 1], location,
                                                        P[i + rise + 1])
                if (CI > 1) or (CI == np.inf):
                    CI = 1

            Tmrt, Kdown, Kup, Ldown, Lup, Tg, ea, esky, I0, CI, Keast, Ksouth, Kwest, Knorth, Least, Lsouth, Lwest, \
            Lnorth, KsideI, radIo, radDo, shadow = so.Solweig1D_2019a_calc(svf, svfveg, svfaveg, sh, vegsh,  albedo_b, absK, absL, ewall,
                                                                Fside, Fup, Fcyl,
                                                                altitude[0][i], azimuth[0][i], zen[0][i], jday[0][i],
                                                                onlyglobal, location, dectime[i], altmax[0][i], cyl, elvis,
                                                                Ta[i], RH[i], radG[i], radD[i], radI[i], P[i],
                                                                Twater, TgK, Tstart, albedo_g, eground, TgK_wall, Tstart_wall,
                                                                TmaxLST, TmaxLST_wall, svfalfa, CI, ani, diffsh, trans)

            self.progressBar.setValue(i + 1)


            # Write to array
            poi_save[0, 0] = YYYY[0][i]
            poi_save[0, 1] = jday[0][i]
            poi_save[0, 2] = hours[i]
            poi_save[0, 3] = minu[i]
            poi_save[0, 4] = dectime[i]
            poi_save[0, 5] = altitude[0][i]
            poi_save[0, 6] = azimuth[0][i]
            poi_save[0, 7] = radIo
            poi_save[0, 8] = radDo
            poi_save[0, 9] = radG[i]
            poi_save[0, 10] = Kdown
            poi_save[0, 11] = Kup
            poi_save[0, 12] = Keast
            poi_save[0, 13] = Ksouth
            poi_save[0, 14] = Kwest
            poi_save[0, 15] = Knorth
            poi_save[0, 16] = Ldown
            poi_save[0, 17] = Lup
            poi_save[0, 18] = Least
            poi_save[0, 19] = Lsouth
            poi_save[0, 20] = Lwest
            poi_save[0, 21] = Lnorth
            poi_save[0, 22] = Ta[i]
            poi_save[0, 23] = Tg + Ta[i]
            poi_save[0, 24] = RH[i]
            poi_save[0, 25] = esky
            poi_save[0, 26] = Tmrt
            poi_save[0, 27] = I0
            poi_save[0, 28] = CI
            poi_save[0, 29] = shadow
            poi_save[0, 30] = svf
            poi_save[0, 31] = KsideI


            # Recalculating wind speed based on pwerlaw
            WsPET = (1.1 / sensorheight) ** 0.2 * Ws[i]
            WsUTCI = (10. / sensorheight) ** 0.2 * Ws[i]
            resultPET = p._PET(Ta[i], RH[i], Tmrt, WsPET, mbody, age, ht, activity, clo, sex)
            poi_save[0, 32] = resultPET
            resultUTCI = utci.utci_calculator(Ta[i], RH[i], Tmrt, WsUTCI)
            poi_save[0, 33] = resultUTCI

            if self.CheckBoxMetData.isChecked():
                self.lineEditTmrt.setText('See textfile')
                self.lineEditPET.setText('See textfile')
                self.lineEditUTCI.setText('See textfile')
                f_handle = open(data_out, 'ab')
                np.savetxt(f_handle, poi_save, fmt=numformat)
                f_handle.close()
            else:
                self.lineEditTmrt.setText('%3.1f' % (Tmrt))
                self.lineEditPET.setText('%3.1f' % (resultPET))
                self.lineEditUTCI.setText('%3.1f' % (resultUTCI))

app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()

