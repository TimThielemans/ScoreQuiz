

import configparser, inspect, os
from email_handler import Class_eMail
from inschrijving_handler import Class_Inschrijvingen
import csv


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
        global QUIZFOLDER

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        
        EMAILINSCHRIJVING = QUIZFOLDER + config.get('EMAIL', 'INSCHRIJVING')
        EMAILBETALINGSVRAAG = QUIZFOLDER + config.get('EMAIL', 'BETALING')
        EMAILHERINNERING = QUIZFOLDER + config.get('EMAIL', 'HERINNERING')
        EMAILEINDSTAND = QUIZFOLDER + config.get('EMAIL', 'EINDSTAND')
        PLOEGGENERAL = config.get('PATHS', 'PLOEGGENERAL')

        UITNODIGINGSCR  = QUIZFOLDER + config.get('EMAIL', 'SCR')
        UITNODIGINGBOW  = QUIZFOLDER + config.get('EMAIL', 'BOW')
        UITNODIGINGKWISTET  = QUIZFOLDER + config.get('EMAIL', 'KWISTET')
        UITNODIGINGLIEFHEBBER  = QUIZFOLDER + config.get('EMAIL', 'LIEFHEBBER')
        UITNODIGINGFAN  = QUIZFOLDER +  config.get('EMAIL', 'FAN')

        

    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})
#=====================================================================================


def bevestigingInschrijving(ploeginfo):
    template = open(EMAILINSCHRIJVING).read()
    text = template.format(VOORNAAM = ploeginfo[1], PLOEGNAAM = ploeginfo[0])
    to_email = ploeginfo[3].replace('\n', '').replace(' ', '')
    email = Class_eMail()
    email.send_HTML_Mail(to_email, 'Bevestiging Inschrijving 6e Q@C Sinterklaasquiz', text)
    del email


def sendUitnodigingen():
    with open(PLOEGGENERAL, 'rt') as fr:
        reader = csv.reader(fr)
        header = next(reader)
        SCRindex = []
        BOWindex = []
        Kwistetindex = []
        for index, name in enumerate(header):
            if 'SCR' in name:
                SCRindex.append(index)
            elif 'BOW' in name:
                BOWindex.append(index)
            elif 'Kwistet' in name:
                Kwistetindex.append(index)
        minimum = 1000
        minimum = input("Laatste index die al verstuurd is?")
        
        email = Class_eMail()
        try:
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
                    email.send_HTML_Mail(adres, onderwerp, text)
                    print(index, adres)
                else:
                    print(index, row[1], 'is al ingeschreven of kreeg al een mail')
            del email
            print('Alles is verstuurd')
        except:
            del email
            raise
            pass

read_Settings()
sendUitnodigingen()


                
        
    



