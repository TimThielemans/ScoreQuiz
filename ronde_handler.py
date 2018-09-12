import configparser, inspect, os
import csv
import time
import unicodedata

#================= GET SETTINGS FROM EMAIL SECTION IN settings.ini FILE ==============
def read_Settings():
    try:
        config = configparser.ConfigParser()
        # config.optionxform=str   #By default config returns keys from Settings file in lower case. This line preserves the case for key
        config.read('settings.ini')

        global RONDEINFO
        global SHEETINFO
        global QUIZFOLDER

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        RONDEINFO = QUIZFOLDER + config.get('PATHS', 'RONDEINFO')
        SHEETINFO = QUIZFOLDER + config.get('PATHS', 'SHEETINFO')
        
        global FIELDNAMES
        f = csv.reader(open(RONDEINFO, 'rt'), delimiter = ',')
        FIELDNAMES = next(f)
        del f
        

    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})
#=====================================================================================



class Class_Rondes():
    
    def nieuweRonde(self, rondeData):
        RN = self.aantalRondes()+1
        AS = 0
        NOQ = int(rondeData[1])*(1+2*int(rondeData[2]))
        AS = self.calculateSheet(NOQ)
        if AS>0:
            with open(RONDEINFO, 'a+') as fw:
                writer = csv.DictWriter(fw, FIELDNAMES)
                writer.writerow({'RN': RN, 'Ronde': rondeData[0], 'Aantal' : rondeData[1], 'Super': rondeData[2] , 'Bonus': rondeData[3], 'Sheet' : AS})
            self.autoUpdate()
        else:
            raise NameError('AnswerSheet niet beschikbaar voor een dergelijke ronde!')
            

    def verwijderRonde(self, ronde):
        try:
            X = self.getRowIndex(ronde)
            data = self.getData()
            with open(RONDEINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data[0:X])
                writer.writerows(data[X+1:])
            self.autoUpdate()
        except NameError:
            raise
        

    def verwijderAlleRondes(self):
        data = self.getData()
        with open(RONDEINFO, 'wt') as fw:
            writer = csv.writer(fw)
            writer.writerow(data[0])

    def veranderRondenaam(self, oud, nieuw):
        try:
            X = self.getRowIndex(oud)
            Y = FIELDNAMES.index('Ronde')
            data = self.getData()
            data[X][Y] = nieuw
            with open(RONDEINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)
        except NameError:
            raise       


    def wisselRondenummers(self, ronde1, ronde2):
        try:
            X1 = self.getRowIndex(ronde1)
            X2 = self.getRowIndex(ronde2)
            Y = FIELDNAMES.index('RN')
            data = self.getData()
            tmp1 = data[X1][Y]
            tmp2 = data[X2][Y]
            data[X1][Y] = tmp2
            data[X2][Y] = tmp1
            with open(RONDEINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)
            self.autoUpdate()
        except NameError:
            raise

    def updateSettings(self, ronde, newSettings):
        try:
            X = self.getRowIndex(ronde)
            Yindexes = []
            Yindexes.append(FIELDNAMES.index('Ronde'))
            Yindexes.append(FIELDNAMES.index('Aantal'))
            Yindexes.append(FIELDNAMES.index('Super'))
            Yindexes.append(FIELDNAMES.index('Bonus'))
            data = self.getData()
            for i, Y in enumerate(Yindexes):
                data[X][Y] = newSettings[i]
            data[X][FIELDNAMES.index('Sheet')] = self.calculateSheet(int(newSettings[1])*(1+2*int(newSettings[2]))) 
            with open(RONDEINFO, 'w') as fw:
                writer = csv.writer(fw)
                writer.writerows(data)
        except NameError:
            raise
        

#========================================GETTERS====================================================

    def aantalRondes(self):
        reader = csv.DictReader(open(RONDEINFO, 'rt'), delimiter=',')
        aantalRondes = 0
        for i, row in enumerate(reader):
                aantalRondes = i+1
        return aantalRondes

    def calculateSheet(self, NOQ):
        with open(SHEETINFO, 'rt') as fr:
            reader = csv.DictReader(fr)
            for row in reader:
                if int(row['Aantal']) == NOQ:
                    return int(row['SN'])
        return 0

    def getSheet(self, ronde):
        try:
            X = self.getRowIndex(ronde)
            Y = FIELDNAMES.index('Sheet')
            data = self.getData()
            return data[X][Y]
        except NameError:
            raise

    def getRondenaam(self, ronde):
        try:
            X = self.getRowIndex(ronde)
            Y = FIELDNAMES.index('Ronde')
            data = self.getData()
            return data[X][Y]
        except NameError:
            raise

    def isSuperRonde(self, ronde):
        try:
            X = self.getRowIndex(ronde)
            Y = FIELDNAMES.index('Super')
            data = self.getData()
            return int(data[X][Y])
        except NameError:
            raise

    def isBonusRonde(self, ronde):
        try:
            X = self.getRowIndex(ronde)
            Y = FIELDNAMES.index('Bonus')
            data = self.getData()
            return int(data[X][Y])
        except NameError:
            raise

    def numberBonusRondes(self):
        data = self.getData()
        Y = FIELDNAMES.index('Bonus')
        result = 0
        for X in range(1, len(data)):
            result = result + int(data[X][Y])
        return int(result)

    def numberSuperRonde(self):
        data = self.getData()
        Y = FIELDNAMES.index('Super')
        for X in range(1, len(data)):
            if int(data[X][Y]) ==1:
                return int(data[X][FIELDNAMES.index('RN')])
        return 0

    def getVragenSuper(self, ronde):
        try:
            X = self.getRowIndex(ronde)
            Y1 = FIELDNAMES.index('Aantal')
            Y2 = FIELDNAMES.index('Super')
            data = self.getData()
            return int(data[X][Y1]), int(data[X][Y2])
        except NameError:
            raise


    def getRondeInfo(self, ronde):
        try:
            X = self.getRowIndex(ronde)
            data = self.getData()
            return data[X]
        except NameError:
            raise

    def getRondes(self):
        data = self.getData()
        for i in range(0, self.aantalRondes()):
            yield data[i+1]

    
#==============================DIT ZIJN INTERNE FUNCTIES ============================================

    def getData(self):
        with open(RONDEINFO, 'rt') as fr:
            return list(csv.reader(fr))
        
    def getRowIndex(self, searchValue):
        reader = csv.DictReader(open(RONDEINFO, 'rt'))
        for index, row in enumerate(reader):
            if unicodedata.normalize('NFKD', row['Ronde']).encode('ASCII', 'ignore') == unicodedata.normalize('NFKD', str(searchValue)).encode('ASCII', 'ignore'):
                return index+1
            elif row['RN'] == str(searchValue):
                return index+1
        raise NameError('NotFound')

    def sorteerRondenummer(self):
        with open(RONDEINFO, 'rt') as fr, open('tmp.csv', 'w+') as fw:
            writer = csv.writer(fw, delimiter=',')
            reader = csv.reader(fr, delimiter=',')
            writer.writerow(next(reader)) #header
            sorted2 = sorted(reader, key = lambda row: (int(row[0])))
            for count, row in enumerate(sorted2):
                writer.writerow(row)
                
        os.rename('tmp.csv', RONDEINFO)
            
    def autoUpdate(self):
        self.sorteerRondenummer()
        with open(RONDEINFO, 'rt') as fr, open('tmp.csv', 'w+') as fw:
            reader = csv.DictReader(fr, delimiter=',')
            writer = csv.DictWriter(fw, FIELDNAMES)
            writer.writeheader()
            for index, row in enumerate(reader):
                toWrite = {}
                RN = str(index+1)
                for i, name in enumerate(FIELDNAMES):
                    data = row[name]
                    toWrite[name] = row[name]
                toWrite['RN'] = RN
                writer.writerow(toWrite)
                
        os.rename('tmp.csv', RONDEINFO)

    
#=================================================================================================

read_Settings()


