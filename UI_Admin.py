from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt
import configparser
import os, parser
import sys
sys.path.append('code/')


class Admin(QtWidgets.QDialog):   
    def __init__(self, parent=None):
        super(Admin, self).__init__(parent)
        uic.loadUi('code/ui/Admin.ui', self)
        self.setup()
        self.show()

    def setup(self):
        from inschrijving_handler import Class_Inschrijvingen
        from ronde_handler import Class_Rondes
        from score_handler import Class_Scores
        import email_sender

        self.email = email_sender
        self.PH = Class_Inschrijvingen()
        self.RH = Class_Rondes()
        self.SH = Class_Scores()

        self.fillComboBoxes()
        self.fillInfoFields()
        
        self.origineelPBox.currentIndexChanged.connect(self.fillInfoFields)
        self.origineelRBox.currentIndexChanged.connect(self.fillInfoFields)
        
        self.PAanpassenBtn.clicked.connect(self.updatePloeg)
        self.UitschrijvenBtn.clicked.connect(self.verwijderPloeg)
        self.updatenPBtn.clicked.connect(self.updateAllPloegen)

        self.RNieuwBtn.clicked.connect(self.nieuweRonde)
        self.RAanpassenBtn.clicked.connect(self.updateRonde)
        self.VerwijderRBtn.clicked.connect(self.verwijderRonde)

        self.RAanmeldenBtn.clicked.connect(self.resetAanmelden)
        self.RPloegenBtn.clicked.connect(self.resetPloegen)
        self.RRondesBtn.clicked.connect(self.resetRondes)
        self.RAllBtn.clicked.connect(self.totalReset)

    def fillComboBoxes(self):
        self.origineelPBox.clear()
        self.tafelnummerBox.clear()
        self.rondeNummerBox.clear()
        self.origineelRBox.clear()
        for index, ploegnaam in enumerate(self.PH.getPloegNamen()):
            self.origineelPBox.addItem(ploegnaam)
            self.tafelnummerBox.addItem(str(index+1) +': ' +  ploegnaam)
        for index, rondenaam in enumerate(self.RH.getRondeNames()):
            self.origineelRBox.addItem(rondenaam)
            self.rondeNummerBox.addItem(str(index+1) +': ' +  rondenaam)
            
        self.origineelPBox.setCurrentIndex(-1)
        self.tafelnummerBox.setCurrentIndex(-1)
        self.origineelRBox.setCurrentIndex(-1)
        self.rondeNummerBox.setCurrentIndex(-1)

    def fillInfoFields(self):
        Pindex = self.origineelPBox.currentIndex()
        Ptext = self.origineelPBox.currentText()
        Rindex = self.origineelRBox.currentIndex()
        Rtext = self.origineelRBox.currentText()
        if Rindex>-1 and len(Rtext)>1:
            info = self.RH.getRondeInfo(Rtext)
            self.RondenaamTxt.setText(info[1])
            self.AfkortingTxt.setText(info[2])
            self.superCheck.setChecked(int(info[4]))
            self.bonusCheck.setChecked(int(info[5]))
            self.NOQBOX.setValue(int(info[3]))
            self.rondeNummerBox.setCurrentIndex(Rindex)

        else:
            self.RondenaamTxt.setText('')
            self.AfkortingTxt.setText('')
            self.superCheck.setChecked(int(0))
            self.bonusCheck.setChecked(int(0))
            self.NOQBOX.setValue(int('0'))

        if Pindex>-1 and len(Ptext)>1:
            info = self.PH.getPloegInfo(Ptext)
            self.PloegnaamTxt.setText(info[2])
            self.VoornaamTxt.setText(info[3])
            self.AchternaamTxt.setText(info[4])
            self.EmailTxt.setText(info[5])
            self.tafelnummerBox.setCurrentIndex(Pindex)
        else:
            self.PloegnaamTxt.setText('')
            self.VoornaamTxt.setText('')
            self.AchternaamTxt.setText('')
            self.EmailTxt.setText('')


    def betalingToevoegen(self):
        

    def resetAanmelden(self):
        if self.questionBox('Zeker?', 'Zeker dat je al de aanmeldingen, en dus ook de scores, wilt resetten?'):
            self.PH.resetAlleAanmeldingen()
            self.SH.clearScoresDir()
            self.SH.clearImagesDir()
    def resetPloegen(self):
        if self.questionBox('Zeker?', 'Zeker dat je al de aanmeldingen, en dus ook de scores, wilt verwijderen?'):
            self.PH.verwijderAllePloegen()
            self.SH.clearScoresDir()
            self.SH.clearImagesDir()
    def resetRondes(self):
        if self.questionBox('Zeker?', 'Zeker dat je al de rondes wilt verwijderen?'):
            self.RH.verwijderAlleRondes()
            self.SH.clearScoresDir()
            self.SH.clearImagesDir()
    def totalReset(self):
        if self.questionBox('Zeker?', 'Zeker dat je alles van deze quiz wil verwijderen?'):
            self.RH.verwijderAlleRondes()
            self.PH.verwijderAllePloegen()
            self.SH.clearScoresDir()
            self.SH.clearImagesDir()

    def nieuweRonde(self):
        index1 = self.origineelRBox.currentIndex()
        index2 = self.rondeNummerBox.currentIndex()
        Ronde1 = self.origineelRBox.currentText()
        rondeInfo = self.getRondeSettings()
        self.RH.nieuweRonde(rondeInfo)

        if not index1 == index2 and index2 >-1:
            if self.questionBox('Ronde invoegen?', 'Zeker dat je {} als ronde {} wilt plaatsen?'.format(rondeInfo[0], index2+1)):
                self.RH.insertRondeBefore(rondeInfo[0], index2+1)
        self.fillComboBoxes()
        
    def updateRonde(self):
        index1 = self.origineelRBox.currentIndex()
        index2 = self.rondeNummerBox.currentIndex()
        Ronde1 = self.origineelRBox.currentText()
        rondeInfo = self.getRondeSettings()
        self.RH.updateRondeInfo(Ronde1, rondeInfo)

        if not index1 == index2 and index2 >-1:
            if self.questionBox('Ronde invoegen?', 'Zeker dat je {} als ronde {} wilt plaatsen?'.format(rondeInfo[0], index2+1)):
                self.RH.insertRondeBefore(rondeInfo[0], index2+1)

        self.fillComboBoxes()

    def getRondeSettings(self):
        rondeInfo = []
        rondeInfo.append(self.RondenaamTxt.text())
        rondeInfo.append(self.AfkortingTxt.text())
        rondeInfo.append(self.NOQBOX.value())
        rondeInfo.append(int(self.superCheck.isChecked()))
        rondeInfo.append(int(self.bonusCheck.isChecked()))
        return rondeInfo

    def verwijderRonde(self):
        index1 = self.origineelRBox.currentIndex()
        Ronde1 = self.origineelRBox.currentText()
        self.RH.verwijderRonde(Ronde1)
            
    def updatePloeg(self):
        index1 = self.origineelPBox.currentIndex()
        index2 = self.tafelnummerBox.currentIndex()
        ploeg1 = self.origineelPBox.currentText()
        
        ploegInfo = []
        ploegInfo.append(self.PloegnaamTxt.text())
        ploegInfo.append(self.VoornaamTxt.text())
        ploegInfo.append(self.AchternaamTxt.text())
        ploegInfo.append(self.EmailTxt.text())
        self.PH.updatePloegInfo(ploeg1, ploegInfo)

        if not index1 == index2 and index2 >-1:
            if self.questionBox('Tafelnummers wisselen?', 'Zeker dat je {} wilt wisselen met tafelnummer {} wilt wisselen?'.format(ploeg1, index2+1)):
                self.PH.wisselTafelnummers(ploeg1, index2+1)

        self.fillComboBoxes()
                

    def verwijderPloeg(self):
        Pindex = self.origineelPBox.currentIndex()
        Ptext = self.origineelPBox.currentText()
        if Pindex>-1 and len(Ptext)>1:
            if self.questionBox('Ploeg verwijderen?', 'Zeker dat je {} wilt uitschrijven?'.format(Ptext)):
                self.PH.verwijderPloeg(Ptext)
                self.fillComboBoxes()

    def updateAllPloegen(self):
        self.PH.autoUpdate()
        #self.PH.sorteerPloegGeneral()
        print('DEBUG mode: Ploeg General is niet gesorteerd om overzicht te behouden, enkel uncomment na de quiz best')
        
    def msgBox(self, text, titel):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle(titel)
        msg.exec()

    def questionBox(self, titel, message):
        qm = QtWidgets.QMessageBox()
        answer = qm.question(QtWidgets.QDialog(), titel, message, qm.Yes | qm.No)
        if answer == qm.Yes:
            return True
        return False

        
       

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Admin()
    sys.exit(app.exec_())

