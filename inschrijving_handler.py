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
        config.read('settings.ini')

        global PLOEGINFO
        global STRUCTBETALING
        global INSCHRIJVINGSGELD
        global DRANKKAARTGELD
        global PLOEGGENERAL
        global QUIZFOLDER
        global HEADERSPATH
        global MAXIMAALDEELNEMERS
        global WACHTLIJST
        global FIELDNAMESWACHTLIJST
        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        
        PLOEGINFO = QUIZFOLDER + config.get('PATHS', 'PLOEGINFO')
        WACHTLIJST = QUIZFOLDER + config.get('PATHS', 'PLOEGWACHTLIJST')
        HEADERSPATH = QUIZFOLDER + config.get('PATHS', 'HEADERS')   
        PLOEGGENERAL = config.get('PATHS', 'PLOEGGENERAL')

        STRUCTBETALING = config.get('COMMON', 'STRUCTBETALING')
        INSCHRIJVINGSGELD = float(config.get('COMMON', 'INSCHRIJVINGSGELD'))
        DRANKKAARTGELD = float(config.get('COMMON', 'DRANKKAARTGELD'))
        MAXIMAALDEELNEMERS = int(config.get('COMMON', 'MAXIMAALDEELNEMERS'))

        if DRANKKAARTGELD.is_integer():
            DRANKKAARTGELD = int(DRANKKAARTGELD)
        
        if INSCHRIJVINGSGELD.is_integer():
            INSCHRIJVINGSGELD = int(INSCHRIJVINGSGELD)
            
        global FIELDNAMES
        f = csv.reader(open(PLOEGINFO, 'rt'), delimiter = ',')
        FIELDNAMES = next(f)
        del f

        global FIELDNAMESWACHTLIJST
        f = csv.reader(open(WACHTLIJST, 'rt'), delimiter = ',')
        FIELDNAMESWACHTLIJST = next(f)
        del f

        global DEFHEADERS
        f = csv.reader(open(HEADERSPATH, 'rt'), delimiter = ',')
        DEFHEADERS = next(f)
        del f
        
        

    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})
#=====================================================================================

class Class_Inschrijvingen():

    def __init__(self):
        read_Settings()

        from ronde_handler import Class_Rondes
        self.RH = Class_Rondes()
        
    def nieuwePloeg(self, ploegdata):
        dubbelenaam = self.getRowIndex(ploegdata[0])
        if dubbelenaam == 0:
            #De ploegnaam is uniek dus geldige inschrijving
            if '@' in ploegdata[3] and '.' in ploegdata[3]:
                self.addToGlobalDocument('1', ploegdata[1], ploegdata[3])
            else:
                ploegdata[3] = ''
            numbers = self.aantalPloegen()
            TN = numbers[1]+1
            IN = numbers[2]+1
            struct = STRUCTBETALING + str(IN).zfill(3)
            modulo = int(struct.replace('/', ''))%97
            if modulo == 0:
                modulo = 97
            Mededeling = '+++{}{}+++'.format(struct, str(modulo).zfill(2))
            if TN<MAXIMAALDEELNEMERS:
                with open(PLOEGINFO, 'a+') as fw:
                    writer = csv.DictWriter(fw, FIELDNAMES)
                    writer.writerow({'IN': IN, 'TN': TN, 'Ploegnaam' : ploegdata[0], 'Voornaam': ploegdata[1] , 'Achternaam': ploegdata[2], 'Email': ploegdata[3], 'Datum': time.strftime('%d/%m/%Y'), 'Mededeling': Mededeling})
                self.autoUpdate()
            else:
                with open(WACHTLIJST, 'a+') as fw:
                    writer = csv.DictWriter(fw, FIELDNAMESWACHTLIJST)
                    writer.writerow({'IN': IN, 'Ploegnaam' : ploegdata[0], 'Voornaam': ploegdata[1] , 'Achternaam': ploegdata[2], 'Email': ploegdata[3], 'Datum': time.strftime('%d/%m/%Y')})
                raise NameError('Wachtlijst')
        else:
            print('niet uniek')
            #inschrijving is niet gelukt want de ploegnaam bestaat al!
            raise ValueError('Ploegnaam is niet uniek!')
            
    
    def verwijderPloeg(self, ploeg):
        X = self.getRowIndex(ploeg)
        if X>0:
            data = self.getData()
            with open(PLOEGINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data[0:X])
                writer.writerows(data[X+1:])
            if '@' in data[X][FIELDNAMES.index('Email')]:
                self.addToGlobalDocument('x', data[X][FIELDNAMES.index('Voornaam')], data[X][FIELDNAMES.index('Email')])
            self.autoUpdate()
        else:
            #Deze ploeg is niet gevonden
            raise NameError('Not Found')

    def verwijderAllePloegen(self):
        with open(PLOEGINFO, 'wt') as fw:
            writer = csv.writer(fw)
            writer.writerow(DEFHEADERS)

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
            if vorig == 0:
                data[X][Y] = '1'
                data[X][FIELDNAMES.index('Uur')] = time.strftime('%H:%M:%S')
                with open(PLOEGINFO, 'w') as fw:
                    writer = csv.writer(fw)
                    writer.writerows(data)
            result['TN'] = data[X][FIELDNAMES.index('TN')]
            result['Ploegnaam'] = data[X][FIELDNAMES.index('Ploegnaam')]
            result['Uur'] = data[X][FIELDNAMES.index('Uur')]
            result['Betaald'] = int(data[X][FIELDNAMES.index('Betaald')])
            result['Bedrag'] = float(data[X][FIELDNAMES.index('Bedrag')])
            if result['Bedrag'].is_integer():
                result['Bedrag'] = int(result['Bedrag'])

            if result['Betaald'] == 1:
                drankkaarten = (result['Bedrag']-INSCHRIJVINGSGELD)/DRANKKAARTGELD
                if drankkaarten.is_integer():
                    drankkaarten = int(drankkaarten)
            else:
                drankkaarten = 0
            
            result['Email'] = '@' in data[X][FIELDNAMES.index('Email')]
            result['Aanwezig'] = bool(vorig) #was er al iemand aanwezig van die ploeg?
            result['Drankkaarten'] = drankkaarten

        return result
            

    def resetAanmelding(self, ploeg):
        data = self.getData()
        X = self.getRowIndex(ploeg)
        if X>0:
            Yindex = []
            Yindex.append(FIELDNAMES.index('Aangemeld'))
            Yindex.append(FIELDNAMES.index('Uur'))
            Yindex.append(FIELDNAMES.index('Bonus'))
            Yindex.append(FIELDNAMES.index('Schifting'))
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

    def resetBetalingen(self):
        data = self.getData()
        Yindex = []
        Yindex.append(FIELDNAMES.index('Betaald'))
        Yindex.append(FIELDNAMES.index('Bedrag'))
        for X in range(1, len(data)):
            for Y in Yindex:
                data[X][Y] = '0'
        with open(PLOEGINFO, 'w') as fw:
            writer = csv.writer(fw)
            writer.writerows(data)

    def updatePloegInfo(self, oud, ploeginfo):
        X = self.getRowIndex(oud)
        if X>0:
            Y = FIELDNAMES.index('Ploegnaam')
            data = self.getData()
            data[X][FIELDNAMES.index('Ploegnaam')] = ploeginfo[0]
            data[X][FIELDNAMES.index('Voornaam')] = ploeginfo[1]
            data[X][FIELDNAMES.index('Achternaam')] = ploeginfo[2]
            update = False
            if not str(data[X][FIELDNAMES.index('Email')]).lower() == str(ploeginfo[3]).lower():
                update = True
            data[X][FIELDNAMES.index('Email')] = ploeginfo[3]
            
            with open(PLOEGINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)

            if update:
                self.addToGlobalDocument('1', data[X][FIELDNAMES.index('Voornaam')], data[X][FIELDNAMES.index('Email')])
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
   
        X = self.getRowIndex(ploeg)
        if X>0:
            data = self.getData()
            if not schifting is None:
                data[X][FIELDNAMES.index('Schifting')] = schifting
            if not bonus is None:
                data[X][FIELDNAMES.index('Bonus')] = bonus
            with open(PLOEGINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)
            return True
        return False
    
    def setBetaling(self, mededeling, bedrag):
        if len(mededeling)>10 and '/' in mededeling:
            mededeling = mededeling.replace('*', '+')
            X = self.getRowIndexBetaling(mededeling)
            if X>0:
                Y=FIELDNAMES.index('Bedrag')
                data = self.getData()
                saldo = bedrag + float(data[X][Y])
                if saldo.is_integer():
                    data[X][Y] = int(saldo)
                else:
                    data[X][Y] = saldo
                print(mededeling, saldo)
                if  saldo>=INSCHRIJVINGSGELD:
                    data[X][FIELDNAMES.index('Betaald')] = 1
                with open(PLOEGINFO, 'w') as fw:
                    writer = csv.writer(fw)
                    writer.writerows(data)
                return True
        return False

    def setBetalingen(self, file):
        self.resetBetalingen()
        with open(file, 'rt') as fr:
            reader = csv.DictReader(fr, delimiter = ';')
            for index, row in enumerate(reader):
                messageStruct = row['gestructureerde mededeling']
                messageFree = row['Vrije mededeling']
                bedrag = float(row['credit'].replace(',', '.'))
                self.setBetaling(messageStruct, bedrag)

    def setBonusses(self, bonusthemas):
        data = self.getData()
        for X in range(1,len(data)):
            data[X][FIELDNAMES.index('Bonus')] = bonusthemas[X-1]
        with open(PLOEGINFO, 'w') as fw:
            writer =csv.writer(fw)
            writer.writerows(data)

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
        reader = csv.DictReader(open(WACHTLIJST, 'rt'), delimiter = ',')
        for i, row in enumerate(reader):
            aantalInschrijvingen = row['IN']
        result = [aantalAangemeld, aantalHuidigeInschrijvingen, int(aantalInschrijvingen), aantalBetaald]
        return result

    def aantalZonder(self):
        reader = csv.DictReader(open(PLOEGINFO, 'rt'), delimiter=',')
        aantalZonder = 0
        for i, row in enumerate(reader):
            if not '@' in row['Email']:
                aantalZonder = aantalZonder +1
        return aantalZonder

    def aanwezigePloegen(self):
        reader = csv.DictReader(open(PLOEGINFO, 'rt'))
        aangemeldPloeg = []
        afwezigPloeg = []
        for i, row in enumerate(reader):
            if int(row['Aangemeld']) == 1:
                aangemeldPloeg.append([int(row['TN']), row['Ploegnaam']])
            else:
                afwezigPloeg.append([int(row['TN']), row['Ploegnaam']])
        return aangemeldPloeg, afwezigPloeg

    def getBetalingen(self):
        Y = FIELDNAMES.index('Bedrag')
        data = self.getData()
        bedrag = 0
        for X in range(1, len(data)):
            bedrag=bedrag + float(data[X][Y])
        return bedrag
        
    def getSchiftingBonus(self, ploeg):
        try:
            X = self.getRowIndex(ploeg)
            Y1 = FIELDNAMES.index('Schifting')
            Y2 = FIELDNAMES.index('Bonus')
            data = self.getData()
            if int(data[X][FIELDNAMES.index('Aangemeld')])>0:
                return int(data[X][Y1]), int(data[X][Y2])
            return 0, 999
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

    def isAanwezig(self, ploeg):
        reader = csv.DictReader(open(PLOEGINFO, 'rt'))
        data = self.getData()
        X = self.getRowIndex(ploeg)
        if X>0:
            if int(data[X][FIELDNAMES.index('Aangemeld')])>0:
                return True
        return False

    def getPloegInfo(self, ploeg):
        try:
            X = self.getRowIndex(ploeg)
            data = self.getData()
            return data[X]
        except NameError:
            raise

    def getEmail(self, ploeg):
        try:
            X = self.getRowIndex(ploeg)
            Y1 = FIELDNAMES.index('Email')
            data = self.getData()
            return data[X][Y1]
        except NameError:
            raise

    def getPloegen(self):
        data = self.getData()
        aantal = self.aantalPloegen()
        for i in range(0, aantal[1]):
            yield data[i+1]

    def getPloegenDict(self):
        with open(PLOEGINFO, 'rt') as fr:
            reader = csv.DictReader(fr)
            for i, row in enumerate(reader):
                yield row

    def getAanwezigePloegenDict(self):
        with open(PLOEGINFO, 'rt') as fr:
            reader = csv.DictReader(fr)
            for i, row in enumerate(reader):
                if row['Aangemeld'] == '1':
                    yield row

    def getPloegNamen(self):
        data = self.getData()
        aantal = self.aantalPloegen()
        for i in range(0, aantal[1]):
            yield data[i+1][FIELDNAMES.index('Ploegnaam')]
    
#==============================DIT ZIJN INTERNE FUNCTIES ============================================

    def addToGlobalDocument(self,number, voornaam, email):
        if not 'Test' in QUIZFOLDER:
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
        else:
            print('Testmodus dus niets toevoegd aan {}'.format(PLOEGGENERAL))   
                                
    def sorteerPloegGeneral(self):
        #SORTEER HET MAAR EEN KEER VLAK NA DE QUIZ ANDERS IS HET OVERZICHT VOLLEDIG WEG VOOR TESTFILES E.d
        tmp = 'tmp.csv'
        with open(PLOEGGENERAL, 'rt') as fr, open(tmp, 'w+') as fw:
            writer = csv.writer(fw)
            reader = csv.reader(fr)
            writer.writerow(next(reader)) #header
            sorted2 = sorted(reader, key = lambda row: (int(row[1]))) #'sorteer op emailadres
            for count, row in enumerate(sorted2):
                writer.writerow(row)

        shutil.move(tmp, PLOEGGENERAL)
    
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

    def getRowIndexBetaling(self, mededeling):
        reader = csv.DictReader(open(PLOEGINFO, 'rt'))
        for index, row in enumerate(reader):
            if row['Mededeling'] == mededeling:
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
        global FIELDNAMES
        if not (len(DEFHEADERS) + self.RH.aantalRondes() + 1) == len(FIELDNAMES):
            FIELDNAMES = DEFHEADERS
            if not 'O' in FIELDNAMES:
                FIELDNAMES.append('O')
            for index, row in enumerate(self.RH.getRondes()):
                if not row[0] in FIELDNAMES:
                    FIELDNAMES.append(row[0])

        self.sorteerTafelnummer()

        tmp = 'tmp.csv'
        with open(PLOEGINFO, 'rt') as fr, open(tmp, 'w+') as fw:
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
                
        os.rename(tmp, PLOEGINFO)

    
#=================================================================================================

#read_Settings()

