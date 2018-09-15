

import configparser, inspect, os

import csv
import pyqrcode

#================= GET SETTINGS FROM EMAIL SECTION IN settings.ini FILE ==============
def read_Settings():
    try:
        config = configparser.ConfigParser()
        # config.optionxform=str   #By default config returns keys from Settings file in lower case. This line preserves the case for key
        config.read('settings.ini')

        global EMAILINSCHRIJVING
        global EMAILBETALINGSVRAAG
        global EMAILHERINNERING
        global EMAILEINDSTAND
        global PLOEGGENERAL
        global UITNODIGINGSCR
        global UITNODIGINGBOW
        global UITNODIGINGKWISTET
        global UITNODIGINGLIEFHEBBER
        global UITNODIGINGFAN
        global UITNODIGINGHERINNERING
        global QUIZFOLDER
        global QRCODES
        global INSCHRIJVINGSGELD
        global DRANKKAART
        global REKENINGNUMMER

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        
        EMAILINSCHRIJVING = QUIZFOLDER + config.get('EMAIL', 'INSCHRIJVING')
        EMAILBETALINGSVRAAG = QUIZFOLDER + config.get('EMAIL', 'BETALING')
        EMAILHERINNERING = QUIZFOLDER + config.get('EMAIL', 'HERINNERING')
        EMAILEINDSTAND = QUIZFOLDER + config.get('EMAIL', 'EINDSTAND')
        QRCODES = QUIZFOLDER + config.get('PATHS', 'QRCODES')
        PLOEGGENERAL = config.get('PATHS', 'PLOEGGENERAL')

        UITNODIGINGSCR  = QUIZFOLDER + config.get('EMAIL', 'SCR')
        UITNODIGINGBOW  = QUIZFOLDER + config.get('EMAIL', 'BOW')
        UITNODIGINGKWISTET  = QUIZFOLDER + config.get('EMAIL', 'KWISTET')
        UITNODIGINGLIEFHEBBER  = QUIZFOLDER + config.get('EMAIL', 'LIEFHEBBER')
        UITNODIGINGFAN  = QUIZFOLDER +  config.get('EMAIL', 'FAN')
        UITNODIGINGHERINNERING = QUIZFOLDER + config.get('EMAIL', 'UITNODIGINGREMINDER')

        INSCHRIJVINGSGELD = config.get('COMMON', 'INSCHRIJVINGSGELD')
        DRANKKAART = config.get('COMMON', 'DRANKKAARTGELD')
        REKENINGNUMMER = config.get('COMMON', 'REKENINGNUMMER')

        
    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})
#=====================================================================================

class Class_Emails():

    def __init__(self):
        read_Settings()
        from email_sender import Class_EmailSender
        from inschrijving_handler import Class_Inschrijvingen

        self.EH = Class_EmailSender()
        self.PH = Class_Inschrijvingen()

    def bevestigingInschrijving(self, ploeginfo):
        template = open(EMAILINSCHRIJVING).read()
        text = template.format(VOORNAAM = ploeginfo[1], PLOEGNAAM = ploeginfo[0])
        to_email = ploeginfo[3].replace('\n', '').replace(' ', '')
        self.EH.send_HTML_Mail(to_email, 'Bevestiging Inschrijving 6e Q@C Sinterklaasquiz', text)

    def sendBetalingQR(self, ploeginfo):
        ploegnaam = ploeginfo['Ploegnaam']
        mededeling = ploeginfo['Mededeling']
        email = 'tim.thielemans@gmail.com' #ploeginfo['Email']
        onderwerp = 'Betaling en QRcode 6e Q@C Sinterklaasquiz'
        filename = 'NeemMijMee_{}.png'.format(ploegnaam.replace('ë', 'e').replace('é','e').replace('ç','c'))
        pyqrcode.create(ploegnaam, error='M', version=5).png(QRCODES + filename, scale=10, quiet_zone = 4)
        template = open(EMAILBETALINGSVRAAG).read()
        tekst = template.format(VOORNAAM = ploeginfo['Voornaam'], PLOEGNAAM = ploegnaam, MEDEDELING = mededeling, INSCHRIJVINGSGELD = INSCHRIJVINGSGELD, DRANKKAART = DRANKKAART , REKENINGNUMMER = REKENINGNUMMER )
        self.EH.send_HTML_Attachment_Mail(email, onderwerp, tekst, QRCODES+filename, filename)
        
    def sendUitnodigingen(self, minimum):
        SCRindex = []
        BOWindex = []
        Kwistetindex = []
        with open(PLOEGGENERAL, 'rt') as fr:
            reader = csv.reader(fr)
            header = next(reader)
            for index, name in enumerate(header):
                if 'SCR' in name:
                    SCRindex.append(index)
                elif 'BOW' in name:
                    BOWindex.append(index)
                elif 'Kwistet' in name:
                    Kwistetindex.append(index)
            
            for index, row in enumerate(reader):
                SCRsum = 0
                BOWsum = 0
                Kwistetsum = 0
                for i in SCRindex:
                    if not row[i] == 'x':
                        SCRsum = SCRsum + int(row[i])
                for i in BOWindex:
                    if not row[i] == 'x':
                        BOWsum = BOWsum + int(row[i])
                for i in Kwistetindex:
                    if not row[i] == 'x':
                        Kwistetsum = Kwistetsum + int(row[i])

                ##Dit aanpassen afhankelijk welke quiz het is, de volgorde aanpassen. Dit is voor SCR
                if not int(row[SCRindex[len(SCRindex)-1]]) == 1 and index>int(minimum):
                    if SCRsum+Kwistetsum+BOWsum>6:
                        template = open(UITNODIGINGFAN).read()
                    elif SCRsum>0:
                        template = open(UITNODIGINGSCR).read()
                    elif Kwistetsum > 0:
                        template = open(UITNODIGINGKWISTET).read()
                    elif BOWsum>0:
                        template = open(UITNODIGINGBOW).read()
                    else:
                        #quizliefhebber, ooit ingeschreven maar terug uitgeschreven ook
                        template = open(UITNODIGINGLIEFHEBBER).read()

                    try:
                        text = template.format(VOORNAAM=row[0])
                    except KeyError:
                        text = template.format(VOORNAAM=row[0], DEELNAMES = SCRsum+Kwistetsum+BOWsum)
                        pass

                        onderwerp = 'Uitnodiging 6e Q@C Sinterklaasquiz Rotselaar 07/12/2018'
                        adres = row[1]
                       # self.EH.send_HTML_Mail(adres, onderwerp, text)
                        print(index, adres)
                    else:
                        print(index, row[1], 'is al ingeschreven of kreeg al een mail')
                print('Alles is verstuurd')

    def sendUitnodigingenReminder(self, minimum):
        SCRindex = []
        BOWindex = []
        Kwistetindex = []
        with open(PLOEGGENERAL, 'rt') as fr:
            reader = csv.reader(fr)
            header = next(reader)
            for index, name in enumerate(header):
                if 'SCR' in name:
                    SCRindex.append(index)
                elif 'BOW' in name:
                    BOWindex.append(index)
                elif 'Kwistet' in name:
                    Kwistetindex.append(index)
            
            for index, row in enumerate(reader):
                SCRsum = 0
                BOWsum = 0
                Kwistetsum = 0
                for i in SCRindex:
                    if not row[i] == 'x':
                        SCRsum = SCRsum + int(row[i])
                for i in BOWindex:
                    if not row[i] == 'x':
                        BOWsum = BOWsum + int(row[i])
                for i in Kwistetindex:
                    if not row[i] == 'x':
                        Kwistetsum = Kwistetsum + int(row[i])
                        
                ##Dit aanpassen afhankelijk welke quiz het is, de volgorde aanpassen. Dit is voor SCR. Stuurt uitnodiging naar Fans, en de laatste 2 SCR en laatste Kwistet deelnemers
                if not int(row[SCRindex[len(SCRindex)-1]]) == 1 and index>int(minimum):
                    if SCRsum+Kwistetsum+BOWsum>6 or int(row[SCRindex[len(SCRindex)-2]])==1 or int(row[SCRindex[len(SCRindex)-3]])==1 or int(row[Kwistetindex[len(Kwistetindex)-1]])==1:
                        template = open(UITNODIGINGHERINNERING).read()
                        text = template.format(VOORNAAM=row[0])
                        onderwerp = 'Herinnering 6e Q@C Sinterklaasquiz Rotselaar 07/12/2018'
                        adres = row[1]
                       # self.EH.send_HTML_Mail(adres, onderwerp, text)
                        print(index, adres)
                    else:
                        print(index, row[1], 'Is niet recent naar een quiz geweest')
                else:
                    print(index, row[1], 'is al ingeschreven of kreeg al een mail')
            print('Alles is verstuurd')

     


