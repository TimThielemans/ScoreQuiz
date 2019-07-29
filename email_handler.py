

import configparser, inspect, os
import math
import csv
import pyqrcode
import base64
import time
#================= GET SETTINGS FROM EMAIL SECTION IN settings.ini FILE ==============
def read_Settings():
    try:
        config = configparser.ConfigParser()
        # config.optionxform=str   #By default config returns keys from Settings file in lower case. This line preserves the case for key
        config.read('settings.ini')

        global EMAILINSCHRIJVING
        global EMAILBETALINGSVRAAG
        global EMAILBETALINGSHERINNERING
        global EMAILLASTINFO
        global EMAILEINDSTAND
        global PLOEGGENERAL
        global UITNODIGINGSCR
        global UITNODIGINGBOW
        global UITNODIGINGKWISTET
        global UITNODIGINGLIEFHEBBER
        global UITNODIGINGFAN
        global UITNODIGINGHERINNERING
        global QRCODES
        global INSCHRIJVINGSGELD
        global DRANKKAART
        global BONUSOVERVIEW
        global BONUSTHEMAS
        global REKENINGNUMMER
        global TABLELAYOUT
        global MOEILIJK
        global MOEILIJKTRESHOLD
        global EMAILWACHTLIJST

        global SCOREBORD
        global SCOREBORDINFO
        global RONDEFILES
        global SCHIFTING
        global FINALPREFIX
        global QUIZFOLDER
        global ANTWOORDEN

        global HEADERLEFT
        global HEADERCENTER
        global DATALEFT
        global DATACENTER
        global SCOREHTMLFULL
        global EMAILVRIJEPLAATS
        global TITEL
        global GEMEENTE
        global DATUM
        global BEDRAGOVERSCHRIJVEN
        

        HEADERLEFT = config.get('LAYOUT', 'HEADERLEFT')
        HEADERCENTER = config.get('LAYOUT', 'HEADERCENTER')
        DATALEFT = config.get('LAYOUT', 'DATALEFT')
        DATACENTER = config.get('LAYOUT', 'DATACENTER')
        TABLELAYOUT = config.get('LAYOUT', 'TABLELAYOUT')

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        FINALPREFIX = config.get('COMMON', 'FINALPREFIX')
        MOEILIJKTRESHOLD = float(config.get('COMMON', 'MOEILIJKTRESHOLD'))
        SCOREHTMLFULL = QUIZFOLDER+config.get('PATHS', 'SCOREHTMLFULL')
        SCOREBORD = QUIZFOLDER + config.get('PATHS', 'SCOREBORD')
        RONDEFILES = QUIZFOLDER +config.get('PATHS', 'RONDEFILES')
        SCOREBORDINFO = QUIZFOLDER + config.get('PATHS', 'SCOREBORDINFO')
        MOEILIJK = QUIZFOLDER + config.get('PATHS', 'MOEILIJK')
        SCHIFTING = float(config.get('COMMON', 'SCHIFTING'))
        TITEL = config.get('COMMON', 'TITEL')
        GEMEENTE = config.get('COMMON', 'GEMEENTE')
        DATUM = config.get('COMMON', 'DATUM')
        BEDRAGOVERSCHRIJVEN = config.get('COMMON', 'DEFAULTOVERSCHRIJVING')

        QRCODES = QUIZFOLDER + config.get('PATHS', 'QRCODES')
        PLOEGGENERAL = config.get('PATHS', 'PLOEGGENERAL')
        BONUSOVERVIEW = QUIZFOLDER + config.get('PATHS', 'BONUSOVERVIEW')
        BONUSTHEMAS = config.get('COMMON', 'BONUSTHEMAS').split(',')
        ANTWOORDEN = QUIZFOLDER + config.get('PATHS', 'ANTWOORDEN')

        UITNODIGINGSCR  = QUIZFOLDER + config.get('EMAIL', 'SCR')
        UITNODIGINGBOW  = QUIZFOLDER + config.get('EMAIL', 'BOW')
        UITNODIGINGKWISTET  = QUIZFOLDER + config.get('EMAIL', 'KWISTET')
        UITNODIGINGLIEFHEBBER  = QUIZFOLDER + config.get('EMAIL', 'LIEFHEBBER')
        UITNODIGINGFAN  = QUIZFOLDER +  config.get('EMAIL', 'FAN')
        UITNODIGINGHERINNERING = QUIZFOLDER + config.get('EMAIL', 'UITNODIGINGREMINDER')
        EMAILINSCHRIJVING = QUIZFOLDER + config.get('EMAIL', 'INSCHRIJVING')
        EMAILBETALINGSVRAAG = QUIZFOLDER + config.get('EMAIL', 'BETALING')
        EMAILBETALINGSHERINNERING = QUIZFOLDER + config.get('EMAIL', 'BETALINGREMINDER')
        EMAILLASTINFO = QUIZFOLDER + config.get('EMAIL', 'LAATSTEINFO')
        EMAILEINDSTAND = QUIZFOLDER + config.get('EMAIL', 'EINDSTAND')
        EMAILWACHTLIJST = QUIZFOLDER + config.get('EMAIL', 'WACHTLIJST')
        EMAILVRIJEPLAATS = QUIZFOLDER + config.get('EMAIL', 'VRIJEPLAATS')

        INSCHRIJVINGSGELD = config.get('COMMON', 'INSCHRIJVINGSGELD')
        DRANKKAART = config.get('COMMON', 'DRANKKAARTGELD')
        REKENINGNUMMER = config.get('COMMON', 'REKENINGNUMMER')

        if SCHIFTING.is_integer():
            SCHIFTING = int(SCHIFTING)
        
    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})
#=====================================================================================

class Class_Emails():

    def __init__(self):
        read_Settings()
        from email_sender import Class_EmailSender
        from inschrijving_handler import Class_Inschrijvingen
        from score_handler import Class_Scores
        from ronde_handler import Class_Rondes
        self.EH = Class_EmailSender()
        self.PH = Class_Inschrijvingen()
        self.RH = Class_Rondes()
        self.SH = Class_Scores()

    def bevestigingInschrijving(self, ploeginfo):
        template = open(EMAILINSCHRIJVING).read()
        text = template.format(VOORNAAM = ploeginfo[1], PLOEGNAAM = ploeginfo[0])
        to_email = ploeginfo[3].replace('\n', '').replace(' ', '')
        self.EH.send_HTML_Mail(to_email, 'Bevestiging Inschrijving ' + TITEL, text)
        
    def wachtlijst(self, ploeginfo):
        template = open(EMAILWACHTLIJST).read()
        text = template.format(VOORNAAM = ploeginfo[1], PLOEGNAAM = ploeginfo[0])
        to_email = ploeginfo[3].replace('\n', '').replace(' ', '')
        self.EH.send_HTML_Mail(to_email, 'Inschrijving ' + TITEL + ': Wachtlijst', text)


    def sendBetalingQR(self, ploeginfo):
        ploegnaam = ploeginfo['Ploegnaam']
        mededeling = ploeginfo['Mededeling']
        email = ploeginfo['Email']
        onderwerp = 'Betaling ' + TITEL
        filename = 'Betaling_{}.png'.format(ploegnaam.replace('ë', 'e').replace('é','e').replace('ç','c'))
        betalingqr = 'BCD\n001\n1\nSCT\nKREDBEBB\nTimTquiz\nBE15735054557030\nEUR' + BEDRAGOVERSCHRIJVEN + '\n\n{}'.format(mededeling)
        pyqrcode.create(betalingqr, error='M', version=6).png(QRCODES + filename, scale=10, quiet_zone = 4)
        template = open(EMAILBETALINGSVRAAG).read()
        tekst = template.format(VOORNAAM = ploeginfo['Voornaam'], PLOEGNAAM = ploegnaam, MEDEDELING = mededeling, INSCHRIJVINGSGELD = INSCHRIJVINGSGELD, DRANKKAART = DRANKKAART , REKENINGNUMMER = REKENINGNUMMER)
        self.EH.send_HTML_Attachment_Mail(email, onderwerp, tekst, QRCODES+filename, filename)
        print(email)
        time.sleep(1)

    def sendBetalingQRSimpel(self, ploeginfo):
        ploegnaam = ploeginfo[2]
        mededeling = ploeginfo[11]
        email = ploeginfo[5]
        onderwerp = 'Betaling ' + TITEL
        filename = 'Betaling_{}.png'.format(ploegnaam.replace('ë', 'e').replace('é','e').replace('ç','c'))
        betalingqr = 'BCD\n001\n1\nSCT\nKREDBEBB\nTimTQuiz\nBE15735054557030\nEUR' + BEDRAGOVERSCHRIJVEN + '\n\n{}'.format(mededeling)
        pyqrcode.create(betalingqr, error='M', version=6).png(QRCODES + filename, scale=10, quiet_zone = 4)
        template = open(EMAILBETALINGSVRAAG).read()
        tekst = template.format(VOORNAAM = ploeginfo[3], PLOEGNAAM = ploegnaam, MEDEDELING = mededeling, INSCHRIJVINGSGELD = INSCHRIJVINGSGELD, DRANKKAART = DRANKKAART , REKENINGNUMMER = REKENINGNUMMER)
        self.EH.send_HTML_Attachment_Mail(email, onderwerp, tekst, QRCODES+filename, filename)
        print(email)

    def sendBetalingReminder(self, ploeginfo):
        ploegnaam = ploeginfo['Ploegnaam']
        mededeling = ploeginfo['Mededeling']
        email = ploeginfo['Email']
        onderwerp = 'Herinnering betaling ' + TITEL
        filename = 'Betaling_{}.png'.format(ploegnaam.replace('ë', 'e').replace('é','e').replace('ç','c'))
        betalingqr = 'BCD\n001\n1\nSCT\nKREDBEBB\nTimTQuiz\nBE15735054557030\nEUR' + BEDRAGOVERSCHRIJVEN + '\n\n{}'.format(mededeling)
        pyqrcode.create(betalingqr, error='M', version=6).png(QRCODES + filename, scale=10, quiet_zone = 4)
        template = open(EMAILBETALINGSHERINNERING).read()
        tekst = template.format(VOORNAAM = ploeginfo['Voornaam'], PLOEGNAAM = ploegnaam, MEDEDELING = mededeling, INSCHRIJVINGSGELD = INSCHRIJVINGSGELD, DRANKKAART = DRANKKAART , REKENINGNUMMER = REKENINGNUMMER )
        self.EH.send_HTML_Attachment_Mail(email, onderwerp, tekst, QRCODES+filename, filename)
        print(email)

    def sendWachtlijstUitnogiding(self, ploeginfo):
        ploegnaam = ploeginfo[1]
        email = ploeginfo[4]
        onderwerp = 'Plaats vrijgekomen ' + TITEL
        template = open(EMAILVRIJEPLAATS).read()
        tekst = template.format(VOORNAAM = ploeginfo[2], PLOEGNAAM = ploegnaam )
        self.EH.send_HTML_Mail(email, onderwerp, tekst)
        print(email)

    def sendWrapUp(self, ploeginfo):
        ploegnaam = ploeginfo['Ploegnaam']
        email = ploeginfo['Email']
        onderwerp = 'Laatste informatie ' + TITEL
        filename = 'NeemMijMee_{}.png'.format(ploegnaam.replace('ë', 'e').replace('é','e').replace('ç','c'))
        pyqrcode.create(ploegnaam, error='M', version=5).png(QRCODES + filename, scale=10, quiet_zone = 4)

        if bool(int(ploeginfo['Betaald'])):
            mededeling = 'We hebben uw betaling van €{} goed ontvangen'.format(ploeginfo['Bedrag'])
        else:
            mededeling = 'We hebben nog geen overschrijving ontvangen van jullie. Geen probleem, maar hou dan alvast €' + INSCHRIJVINGSGELD + ' klaar bij het aanmelden samen met je QR-code. Enkel cash.'

        template = open(EMAILLASTINFO).read()
        tekst = template.format(VOORNAAM = ploeginfo['Voornaam'], PLOEGNAAM = ploegnaam, BETALINGTEKST = mededeling)
        self.EH.send_HTML_Attachment_Mail(email, onderwerp, tekst, QRCODES+filename, filename)
        print(email)
        
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
                noMail = False
                genre = "KWISTET"
                ##Dit aanpassen afhankelijk welke quiz het is, de volgorde aanpassen. 
                if not int(row[Kwistetindex[len(Kwistetindex)-1]]) == 1 and index>int(minimum) and index<int(minimum)+80:  #de quizindex van huidige quiz zetten en maximaal 80 per 'batch'
                    #nog niet ingeschreven
                    if SCRsum+Kwistetsum+BOWsum>6:
                        template = open(UITNODIGINGFAN).read()
                        
                        genre = "FAN"
                    # Eerste elif moet van huidige quiz zijn!
                    elif Kwistetsum > 0:
                        template = open(UITNODIGINGKWISTET).read()
                    elif SCRsum>0:
                        genre = "SCR"
                        template = open(UITNODIGINGSCR).read()
                    elif BOWsum>0:
                        genre = "BOW"
                        noMail = True
                        template = open(UITNODIGINGBOW).read()
                    else:
                        #quizliefhebber, ooit ingeschreven maar terug uitgeschreven ook
                        template = open(UITNODIGINGLIEFHEBBER).read()

                        genre = "liefhebber"
                    try:
                        text = template.format(VOORNAAM=row[0])
                    except KeyError:
                        text = template.format(VOORNAAM=row[0], DEELNAMES = SCRsum+Kwistetsum+BOWsum)
                        pass
                    if noMail:
                        print(index, row[1], genre, 'Hoeft geen mail te ontvangen')
                    else:
                        onderwerp = 'Uitnodiging ' + TITEL + ' ' + GEMEENTE + ' ' + DATUM
                        adres = row[1]
                        self.EH.send_HTML_Mail(adres, onderwerp, text)
                        print(index, adres, genre)
                        time.sleep(5)
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
                        
                ##Dit aanpassen afhankelijk welke quiz het is, de volgorde aanpassen. Dit is voor Kwistet. Stuurt uitnodiging naar Fans, en de laatste 2 huidige en laatste andere deelnemers
                if not int(row[Kwistetindex[len(Kwistetindex)-1]]) == 1 and index>int(minimum) and index<int(minimum)+80:
                    if SCRsum+Kwistetsum+BOWsum>5 or row[Kwistetindex[len(Kwistetindex)-2]]=='1' or row[Kwistetindex[len(Kwistetindex)-3]]=='1' or row[SCRindex[len(SCRindex)-1]]=='1':
                        template = open(UITNODIGINGHERINNERING).read()
                        text = template.format(VOORNAAM=row[0])
                        onderwerp = 'Herinnering ' + TITEL + ' ' + GEMEENTE + ' ' + DATUM
                        adres = row[1]
                        self.EH.send_HTML_Mail(adres, onderwerp, text)
                        time.sleep(5)
                        print(index, adres)
                    else:
                        print(index, row[1], 'Is niet recent naar een quiz geweest')
                else:
                    print(index, row[1], 'is al ingeschreven of kreeg al een mail')
            print('Alles is verstuurd')

    def sendEindstand(self):
        
        aantalDeelnemers,_,_,_ = self.PH.aantalPloegen()
        self.worstAnsweredQuestions(aantalDeelnemers)
        for i in range(0, aantalDeelnemers):
            pos = i+1
            eindstandPloeg = self.SH.getFinalScore(pos)
            ploegnaam = eindstandPloeg['Ploegnaam']
            tafelnummer = eindstandPloeg['TN']
            email = self.PH.getEmail(ploegnaam)
            onderwerp = 'Evaluatie ' + TITEL
            #AANPASSEN naar gelang wat de schiftingsvraag was
            schifting = str(SCHIFTING) + ' km'
            positie = str(pos) + 'e'

            bonusTekst = self.generateBonusTekst(ploegnaam)
            rondescores = self.generateEigenOverzicht(tafelnummer)
            eindstand = self.generateNabijeOverzicht(pos, aantalDeelnemers, len(bonusTekst)>1)
            winnaars = self.generateNabijeOverzicht(1,1,len(bonusTekst)>1)
            
            template = open(EMAILEINDSTAND).read()
            tekst = template.format(PLOEGNAAM = ploegnaam, EINDPOSITIE = positie, AANTALDEELNEMERS = aantalDeelnemers, MOEILIJK = MOEILIJKTRESHOLD*100, BONUSTEKST = bonusTekst, SCHIFTINGSANTWOORD = schifting, EIGENOVERZICHT = rondescores, EINDSTANDNABIJ = eindstand, SCOREWINNAARS = winnaars)
            #self.EH.send_HTML_Attachment_Mail(email, onderwerp, tekst, MOEILIJK, 'Moeilijk.txt')
            tmp = MOEILIJK.split('/')
            filename1 = tmp[len(tmp)-1]
            tmp = SCOREHTMLFULL.split('/')
            filename2 = tmp[len(tmp)-1]
            #if email == 'hello@timtquiz.com':
            print(pos, email)
            self.EH.send_HTML_Double_Attachment_Mail(email, onderwerp, tekst, MOEILIJK, filename1, SCOREHTMLFULL, filename2)
            #else:
             #   print(pos, email)
              #  self.EH.send_HTML_Double_Attachment_Mail(email, onderwerp, tekst, MOEILIJK, filename1, SCOREHTMLFULL, filename2)

            time.sleep(2)
                

    def sendTussenstandToTim(self):
        email = 'timtquiz@gmail.com'
        onderwerp = 'Score: Projectie'
        tekst = 'Goedenavond mezelf, hierbij de tussen- of eindstand. Groetjes van de jury'
        tmp = SCOREHTMLFULL.split('/')
        filename2 = tmp[len(tmp)-1]
        self.EH.send_HTML_Attachment_Mail(email, onderwerp, tekst, SCOREHTMLFULL, filename2)
        
    def generateBonusTekst(self, ploegnaam):
        with open(BONUSOVERVIEW, 'rt') as fr:
            reader = csv.DictReader(fr)
            for row in reader:
                if row['Ploegnaam'] == ploegnaam:
                    tekst = 'Jullie kozen {} als bonusthema ({}/{})'.format(BONUSTHEMAS[int(row['Origineel'])-1], row['OrigineelScore'], row['Maximum'])
                    if int(row['BesteScore'])>int(row['OrigineelScore']):
                        tekst = tekst + ', dat is niet slecht maar op {} heb je beter gescoord ({}/{})! '.format(BONUSTHEMAS[int(row['Beste'])-1], row['BesteScore'], row['Maximum'])
                    else:
                        tekst = tekst + ', goed ingeschat dus want het was jullie beste thema! '

                    return tekst
        return ''

    def getBonusScore(self, ploegnaam):
        with open(BONUSOVERVIEW, 'rt') as fr:
            reader = csv.DictReader(fr)
            for row in reader:
                if row['Ploegnaam'] == ploegnaam:
                    tekst = BONUSTHEMAS[int(row['Origineel'])-1] + ' ({}/{})'.format(row['OrigineelScore'], row['Maximum'])
                    return tekst
        return ''

    def generateEigenOverzicht(self, tafelnummer):

        tekst = TABLELAYOUT + '<tr>' + HEADERLEFT.format(HEADER = 'Ronde') + HEADERCENTER.format(HEADER = 'Eigen Score') + HEADERCENTER.format(HEADER = 'Maximum Score') + HEADERCENTER.format(HEADER = 'Gemiddelde score') + '</tr>'

        totaalScore = 0
        maximumScore = 0
        gemiddeldeScore = 0

        with open(SCOREBORDINFO, 'rt') as fr1:
            reader = csv.DictReader(fr1)
            for usedRound in reader:
                rondeNaam= usedRound['Ronde']
                maximumRondeScore = 0
                gemiddeldeRondeScore = 0
                eigenRondeScore = 0
                with open(RONDEFILES + FINALPREFIX + rondeNaam + '.csv', 'rt') as fr:
                    reader = csv.reader(fr)    
                    for row in reader:
                        if row[1] == str(tafelnummer):
                            eigenRondeScore = sum(map(int, row[2:]))
                        elif 'Max/Gem' in row:
                            maximumRondeScore = row[0]
                            gemiddeldeRondeScore = round(float(row[1]),1)

                maximumScore = int(maximumRondeScore)+ maximumScore
                totaalScore = eigenRondeScore + totaalScore
                gemiddeldeScore = float(gemiddeldeRondeScore) + gemiddeldeScore

                tekst = tekst + '<tr>' + DATALEFT.format(DATA = rondeNaam) + DATACENTER.format(DATA = eigenRondeScore) + DATACENTER.format(DATA = maximumRondeScore) + DATACENTER.format(DATA = gemiddeldeRondeScore) + '</tr>'
               
        tekst = tekst + '<tr>' + DATALEFT.format(DATA = 'Totaal') + DATACENTER.format(DATA = str(totaalScore) + ' ({}%)'.format(round(totaalScore/maximumScore*100,2))) + DATACENTER.format(DATA = maximumScore) + DATACENTER.format(DATA = str(round(float(gemiddeldeScore),2)) + ' ({}%)'.format(round(gemiddeldeScore/maximumScore*100,2))) + '</tr>'
        tekst = tekst + '</table></div>'
        return tekst

    def generateNabijeOverzicht(self, positie, aantalPloegen, bonus):
        aantalPlusMin = 5
        aantalRondes = 0

        tekst = TABLELAYOUT + '<tr>' + HEADERLEFT.format(HEADER = 'Nr.') + HEADERLEFT.format(HEADER = 'Ploegnaam') + HEADERCENTER.format(HEADER = 'Totaal')
        with open(SCOREBORDINFO, 'rt') as fr:
            reader = csv.DictReader(fr)
            for row in reader:
                tekst = tekst + HEADERCENTER.format(HEADER = row['Afkorting'])
                aantalRondes = aantalRondes +1
        if bool(bonus):
            tekst = tekst + HEADERCENTER.format(HEADER = 'Bonus')
        tekst = tekst + HEADERCENTER.format(HEADER='Schiting') + '</tr>'

        nabijescores = self.SH.getFinalScores(positie, aantalPloegen, aantalPlusMin)
        for scores in nabijescores:
            ploegnaamOrig = scores[2]
            if len(ploegnaamOrig) > 25:
                ploegnaam = (ploegnaamOrig[:25] + '..')
            else:
                ploegnaam = ploegnaamOrig;
            tekst = tekst + '<tr>' + DATALEFT.format(DATA = scores[0]) + DATACENTER.format(DATA = ploegnaam) + DATACENTER.format(DATA = scores[3])
            for i in range(0, aantalRondes):
                tekst = tekst + DATACENTER.format(DATA = scores[5+i])
            if bool(bonus):
                tekst = tekst + DATACENTER.format(DATA = self.getBonusScore(ploegnaamOrig))
            schifting = float(scores[len(scores)-2])
            if schifting.is_integer():
                schifting = int(schifting)
            tekst = tekst + DATACENTER.format(DATA = round(float(scores[len(scores)-2]),2)) +  '</tr>'
        
        return tekst

    def worstAnsweredQuestions(self, aantalDeelnemers):
        filenames = []
        rondenaam = []
        rondenummer = []
        with open(SCOREBORDINFO, 'rt') as fr:
            reader = csv.DictReader(fr)
            for row in reader:
                filenames.append(RONDEFILES + FINALPREFIX + row['Ronde'] + '.csv')
                rondenaam.append(row['Afkorting'])
                rondenummer.append(int(row['RN']))

        antwoordLimiet = int(math.ceil(aantalDeelnemers*MOEILIJKTRESHOLD))
        moeilijkeVragen = []
        antwoorden = self.getAntwoorden()
        for index, file in enumerate(filenames):
            try:
                RNaam =rondenaam[index]
                RN = rondenummer[index]
                with open(file, 'rt') as fr:
                    reader =csv.reader(fr)
                    if 'Bonus' in next(reader):
                        compensatieBonus = 1
                    else:
                        compensatieBonus = 0
                    if self.RH.isSuperRonde(RN) == 1:
                        superronde = True
                    else:
                        superronde = False
                    for row in reader:
                        if 'Max/Gem' in row:
                            aantalJuist = row[2:len(row)-1]
                            aantalJuist = list(map(int, aantalJuist))
                            for i in range(0, len(aantalJuist)-compensatieBonus):
                                if aantalJuist[i]<=antwoordLimiet:
                                    if not superronde:
                                        VN = i+1
                                        moeilijkeVragen.append([RNaam, VN, aantalJuist[i], antwoorden[RN-1][VN]])
                                    elif i%3 == 2:
                                        VN = int((i+1)/3)
                                        moeilijkeVragen.append([RNaam, str(VN)+'c', aantalJuist[i], antwoorden[RN-1][i+1]])
            except:
                print('Fout!')
                print(index, rondenaam, rondenummer)
                print(RNaam, RN, VN)
                pass                                        
        
        moeilijkeVragen = sorted(moeilijkeVragen,key=lambda x: (x[2], x[0]))
        
        with open(MOEILIJK, "w") as fw:
            fw.write('#Juist' + '\t' + 'Ronde'+ '\t' + 'Vraag' + '\t' +'Antwoord' + '\n')
            for i in range(len(moeilijkeVragen)):
                fw.write(str(moeilijkeVragen[i][2]) + '\t' + str(moeilijkeVragen[i][0]) + '\t' + str(moeilijkeVragen[i][1]) + '\t' + str(moeilijkeVragen[i][3])+ '\n')
                         
    def getAntwoorden(self):
        with open(ANTWOORDEN, 'rt')as fr:
            reader = csv.reader(fr)
            return list(reader)
        


    

