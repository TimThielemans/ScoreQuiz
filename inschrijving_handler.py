import configparser, inspect, os
import csv
import time
import unicodedata
import shutil

#================= GET SETTINGS FROM EMAIL SECTION IN settings.ini FILE ==============
def read_Settings():
    try:
        config = configparser.ConfigParser()
        # config.optionxform=str   #By default config returns keys from Settings file in lower case. This line preserves the case for key
        config.read(os.path.dirname(os.path.realpath(__file__)) + '/settings.ini')

        global PLOEGINFO
        global RONDEINFO
        global STRUCTBETALING
        global INSCHRIJVINGSGELD
        global DRANKKAARTGELD
        global PLOEGGENERAL
        global QUIZFOLDER

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        
        PLOEGINFO = QUIZFOLDER + config.get('PATHS', 'PLOEGINFO')
        RONDEINFO = QUIZFOLDER + config.get('PATHS', 'RONDEINFO')        
        PLOEGGENERAL = config.get('PATHS', 'PLOEGGENERAL')

        STRUCTBETALING = config.get('COMMON', 'STRUCTBETALING')
        INSCHRIJVINGSGELD = config.get('COMMON', 'INSCHRIJVINGSGELD')
        DARNKKAARTGELD = config.get('COMMON', 'DRANKKAARTGELD')
        
        global FIELDNAMES
        f = csv.reader(open(PLOEGINFO, 'rt'), delimiter = ',')
        FIELDNAMES = next(f)
        

    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})
#=====================================================================================

class Class_Inschrijvingen():
    
    def nieuwePloeg(self, ploegdata):
        dubbelenaam = self.getRowIndex(ploegdata[0])
        if dubbelenaam == 0:
            #De ploegnaam is uniek dus geldige inschrijving
            if '@' in ploegdata[3]:
                self.addToGlobalDocument('1', ploegdata[1], ploegdata[3])
            numbers = self.aantalPloegen()
            TN = numbers[1]+1
            IN = numbers[2]+1
            struct = STRUCTBETALING + str(IN).zfill(2)
            modulo = int(struct.replace('/', ''))%97
            if modulo == 0:
                modulo = 97
            Mededeling = '+++{}{}+++'.format(struct, str(modulo).zfill(2))
            with open(PLOEGINFO, 'a+') as fw:
                writer = csv.DictWriter(fw, FIELDNAMES)
                writer.writerow({'IN': IN, 'TN': TN, 'Ploegnaam' : ploegdata[0], 'Voornaam': ploegdata[1] , 'Achternaam': ploegdata[2], 'Email': ploegdata[3], 'Datum': time.strftime('%d/%m/%Y'), 'Mededeling': Mededeling})        
            self.autoUpdate()
        else:
            #inschrijving is niet gelukt want de ploegnaam bestaat al!
            raise NameError('Ploegnaam is niet uniek!')
            
    
    def verwijderPloeg(self, ploeg):
        X = self.getRowIndex(ploeg)
        if X>0:
            data = self.getData()
            with open(PLOEGINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data[0:X])
                writer.writerows(data[X+1:])
            self.addToGlobalDocument('x', data[X][FIELDNAMES.index('Voornaam')], ploegdata[X][FIELDNAMES.index('Email')])
            self.autoUpdate()
        else:
            #Deze ploeg is niet gevonden
            raise NameError('Not Found')

    def verwijderAllePloegen(self):
        data = self.getData()
        with open(PLOEGINFO, 'wt') as fw:
            writer = csv.writer(fw)
            writer.writerow(data[0])

    def aanmelden(self, ploeg):
        #Return: Tafelnummer en eventueel het uur waarop er al iemand had aangemeld, indien [] bestaat de ploeg niet
        result = {}
        X = self.getRowIndex(ploeg)
        stringResult = ''
        if X>0:
            #de ploeg bestaat
            Y = FIELDNAMES.index('Aangemeld')
            data = self.getData()
            vorig = int(data[X][Y])
            result['TN'] = data[X][FIELDNAMES.index('TN')]
            result['Uur'] = data[X][FIELDNAMES.index('Uur')]
            result['Email'] = data[X][FIELDNAMES.index('Email')]
            result['Betaald'] = data[X][FIELDNAMES.index('Betaald')]
            result['Bedrag'] = data[X][FIELDNAMES.index('Bedrag')]
            if vorig == 0:
                data[X][Y] = '1'
                data[X][FIELDNAMES.index('Uur')] = time.strftime('%H:%M:%S')
                with open(PLOEGINFO, 'w') as fw:
                    writer = csv.writer(fw)
                    writer.writerows(data)
                stringResult = 'Ploegnaam: {}\n'.format(data[X][FIELDNAMES.index('Ploegnaam')])
            else:
                stringResult = stringResult + 'Er heeft zich al iemand van {} aangemeld om {}.\n \n'.format(str(data[X][FIELDNAMES.index('Ploegnaam')]).upper(), data[X][FIELDNAMES.index('Uur')])

            stringResult = stringResult + 'Tafelnummer: {} \n'.format(result['TN'])

            if not '@' in result['Email']:
                stringResult = stringResult + '\nEMAILADRES TOEVOEGEN!!!'
            
        return stringResult
            

    def resetAanmelding(self, ploeg):
        data = self.getData()
        X = self.getRowIndex(ploeg)
        if X>0:
            Yindex = []
            Yindex.append(FIELDNAMES.index('Aangemeld'))
            Yindex.append(FIELDNAMES.index('Uur'))
            Yindex.append(FIELDNAMES.index('Bonus'))
            Yindex.append(FIELDNAMES.index('Schifting'))
            for X in range(1, len(data)):
                for Y in Yindex:
                    data[X][Y] = '0'
            with open(PLOEGINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)
            return True
        return False


    def resetAlleAanmeldingen(self):
        data = self.getData()
        Yindex = []
        Yindex.append(FIELDNAMES.index('Aangemeld'))
        Yindex.append(FIELDNAMES.index('Uur'))
        Yindex.append(FIELDNAMES.index('Bonus'))
        Yindex.append(FIELDNAMES.index('Schifting'))
        for X in range(1, len(data)):
            for Y in Yindex:
                data[X][Y] = '0'
        with open(PLOEGINFO, 'w') as fw:
            writer = csv.writer(fw)
            writer.writerows(data)

    def veranderPloegnaam(self, oud, nieuw):
        X = self.getRowIndex(oud)
        if X>0:
            Y = FIELDNAMES.index('Ploegnaam')
            data = self.getData()
            data[X][Y] = nieuw
            with open(PLOEGINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)
            return True
        return False

    def veranderEmail(self, ploegnaam, email):
        X = self.getRowIndex(ploegnaam)
        if X>0:
            Y = FIELDNAMES.index('Email')
            data = self.getData()
            data[X][Y] = email
            with open(PLOEGINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)
            voornaam = data[X][FIELDNAMES.index('Voornaam')]
            self.addToGlobalDocument('1', voornaam, email)
            return True
        return False
            
    
    def wisselTafelnummers(self, tafel1, tafel2):
        try:
            X1 = self.getRowIndex(tafel1)
            X2 = self.getRowIndex(tafel2)
            Y = FIELDNAMES.index('TN')
            data = self.getData()
            tmp1 = data[X1][Y]
            tmp2 = data[X2][Y]
            data[X1][Y] = tmp2
            data[X2][Y] = tmp1
            with open(PLOEGINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)
                
            self.autoUpdate()
        except NameError:
            raise
        
    def setSchiftingBonus(self, ploeg, schifting=None, bonus=None):
        try:
            X = self.getRowIndex(ploeg)
            data = self.getData()
            if not schifting is None:
                data[X][FIELDNAMES.index('Schifting')] = schifting
            if not bonus is None:
                data[X][FIELDNAMES.index('Bonus')] = bonus
            with open(PLOEGINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)
        except NameError:
            raise

    def setBetaling(self, ploeg, bedrag):
        try:
            X = self.getRowIndex(ploeg)
            data = self.getData()
            data[X][FIELDNAMES.index('Bedrag')] = bedrag
            if int(bedrag)>=20:
                data[X][FIELDNAMES.index('Betaald')] = 1
            with open(PLOEGINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)
        except NameError:
            raise

#========================================GETTERS====================================================

    def aantalPloegen(self):
        reader = csv.DictReader(open(PLOEGINFO, 'rt'), delimiter=',')
        aantalInschrijvingen = 0
        aantalAangemeld = 0
        aantalHuidigeInschrijvingen = 0
        aantalBetaald = 0
        for i, row in enumerate(reader):
                aantalAangemeld = aantalAangemeld + int(row['Aangemeld'])
                aantalHuidigeInschrijvingen = i+1
                aantalInschrijvingen = row['IN']
                aantalBetaald = aantalBetaald + int(row['Betaald'])
        result = [aantalAangemeld, aantalHuidigeInschrijvingen, int(aantalInschrijvingen), aantalBetaald]
        return result

    def aanwezigePloegen(self):
        reader = csv.DictReader(open(PLOEGINFO, 'rt'), delimiter=',')
        aangemeldNummer = []
        aangemeldPloeg = []
        afwezigPloeg = []
        for i, row in enumerate(reader):
            if int(row['Aangemeld']) == 1:
                aangemeldNummer.append(int(row['TN']))
                aangemeldPloeg.append(row['Ploegnaam'])
            else:
                afwezigPloeg.append(row['Ploegnaam'])
        return aangemeldNummer, aangemeldPloeg, afwezigPloeg

    def getSchiftingBonus(self, ploeg):
        try:
            X = self.getRowIndex(ploeg)
            Y1 = FIELDNAMES.index('Schifting')
            Y2 = FIELDNAMES.index('Bonus')
            data = self.getData()
            return float(data[X][Y1]), int(data[X][Y2])
        except NameError:
            raise

    def getPloegnaam(self, ploeg):
        try:
            X = self.getRowIndex(ploeg)
            Y1 = FIELDNAMES.index('Ploegnaam')
            data = self.getData()
            return data[X][Y1]
        except NameError:
            raise

    def getPloegen(self):
        data = self.getData()
        aantal = self.aantalPloegen()
        for i in range(0, aantal[1]):
            yield data[i+1]

    def getPloegNamen(self):
        data = self.getData()
        aantal = self.aantalPloegen()
        for i in range(0, aantal[1]):
            yield data[i+1][FIELDNAMES.index('Ploegnaam')]
    
#==============================DIT ZIJN INTERNE FUNCTIES ============================================

    def addToGlobalDocument(self,number, voornaam, email):
        tmp = 'tmp.csv'
        with open(PLOEGGENERAL, 'rt') as fr, open(tmp, 'w') as fw:
            reader = csv.reader(fr)
            writer = csv.writer(fw)
            headers = next(reader)
            writer.writerow(headers)
            new = True
            for index, row in enumerate(reader):
                if str(row[1]).lower() == str(email).lower():
                    newRow = []
                    if len(row)==len(headers):
                        newRow = [voornaam] + row[1:(len(row)-1)] + [number]
                    else:
                        extra = [0]*(len(headers)-len(row)-1)
                        newRow = [voornaam] + row[1:] + extra + [number]
                    writer.writerow(newRow)
                    new = False
                    print('GEVONDEN:', index, row[1])
                else:
                    if len(row)<len(headers):
                        row = row + [0]*(len(headers)-len(row))
                    writer.writerow(row)
            if new:
                extra = [0]*(len(headers)-3)
                nieuweRij = [voornaam] +  [email] + extra + [number]
                writer.writerow(nieuweRij)
                print('Nieuwe ploeg:', voornaam, email)

        #SORTEER HET MAAR EEN KEER VLAK NA DE QUIZ ANDERS IS HET OVERZICHT VOLLEDIG WEG VOOR TESTFILES E.d
        shutil.move(tmp, PLOEGGENERAL)
                                
    def sorteerPLOEGGENERAL(self):
        #SORTEER HET MAAR EEN KEER VLAK NA DE QUIZ ANDERS IS HET OVERZICHT VOLLEDIG WEG VOOR TESTFILES E.d
        with open(tmp, 'rt') as fr, open(PLOEGGENERAL, 'w+') as fw:
            writer = csv.writer(fw)
            reader = csv.reader(fr)
            writer.writerow(next(reader)) #header
            sorted2 = sorted(reader, key = lambda row: (int(row[1]))) #'sorteer op emailadres
            for count, row in enumerate(sorted2):
                writer.writerow(row)
    
    def getData(self):
        with open(PLOEGINFO, 'rt') as fr:
            return list(csv.reader(fr))
        
    def getRowIndex(self, searchValue):
        reader = csv.DictReader(open(PLOEGINFO, 'rt'))
        for index, row in enumerate(reader):
            if unicodedata.normalize('NFKD', row['Ploegnaam']).encode('ASCII', 'ignore') == unicodedata.normalize('NFKD', str(searchValue)).encode('ASCII', 'ignore'):
                return index+1
            elif row['TN'] == str(searchValue):
                return index+1
        return 0

    def sorteerTafelnummer(self):
        with open(PLOEGINFO, 'rt') as fr, open('tmp.csv', 'w+') as fw:
            writer = csv.writer(fw, delimiter=',')
            reader = csv.reader(fr, delimiter=',')
            writer.writerow(next(reader)) #header
            sorted2 = sorted(reader, key = lambda row: (int(row[1])))
            for count, row in enumerate(sorted2):
                writer.writerow(row)
                
        os.rename('tmp.csv', PLOEGINFO)
            
    def autoUpdate(self):
        if not '0' in FIELDNAMES:
            FIELDNAMES.append('0')
            with open(RONDEINFO, 'rt') as f:
                rondes = csv.DictReader(f, delimiter=',')
                for index, row in enumerate(rondes):
                    if not row['RN'] in FIELDNAMES:
                        FIELDNAMES.append(row['RN'])

        self.sorteerTafelnummer()

        with open(PLOEGINFO, 'rt') as fr, open('tmp.csv', 'w+') as fw:
            reader = csv.DictReader(fr, delimiter=',')
            writer = csv.DictWriter(fw, FIELDNAMES)
            writer.writeheader()
            for index, row in enumerate(reader):
                toWrite = {}
                TN = str(index+1)
                for i, name in enumerate(FIELDNAMES):
                    try:
                        data = row[name]
                        if name.replace(' ', '').isdigit():
                            toWrite[name] = name.replace(' ', '') + '_' + TN
                        elif not data is '':
                            toWrite[name] = row[name]
                        else:
                            toWrite[name] = '0'
                    except KeyError:
                        toWrite[name] = name + '_' + TN
                toWrite['TN'] = TN
                writer.writerow(toWrite)
                
        os.rename('tmp.csv', PLOEGINFO)

    
#=================================================================================================

read_Settings()

