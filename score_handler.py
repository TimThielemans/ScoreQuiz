import csv
import time
import math
import random
import shutil
import itertools
import configparser, inspect, os
from ronde_handler import Class_Rondes
from inschrijving_handler import Class_Inschrijvingen

#================= GET SETTINGS FROM EMAIL SECTION IN settings.ini FILE ==============
def read_Settings():

    global RH
    global PH
    

    RH = Class_Rondes()
    PH = Class_Inschrijvingen()
    SUPERNR = RH.numberSuperRonde()
    
    try:
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.realpath(__file__)) + '/settings.ini')

        global SCOREBORD
        global SCOREBORDINFO
        global RONDEFILES
        global SCANCONTROL
        global SCANRAW
        global USERPREFIX
        global FINALPREFIX
        global JPGPREFIX
        global IMAGESDIR
        global QUIZFOLDER

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        SCOREBORD = QUIZFOLDER+config.get('PATHS', 'SCOREBORD')
        SCOREBORDINFO = QUIZFOLDER+config.get('PATHS', 'SCOREBORDINFO')
        RONDEFILES = QUIZFOLDER+config.get('PATHS', 'RONDEFILES')
        IMAGESDIR = QUIZFOLDER+config.get('PATHS', 'OUTPUTIMAGES')
        
        SCANRAW = config.get('COMMON', 'SCANRAW')
        SCANCONTROL = config.get("COMMON","SCANCONTROL")
        USERPREFIX = config.get("COMMON","USERPREFIX")
        FINALPREFIX = config.get("COMMON","FINALPREFIX")
        JPGPREFIX = config.get('COMMON', 'JPGPREFIX')
        
    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})
#=====================================================================================

class Class_Scores():

    def getScore(self, ronde, ploeg, scanner=0):
        if scanner==1:
            filename = RONDEFILES + SCANRAW
        else:
            filename = RONDEFILES + USERPREFIX + RH.getRondenaam(ronde) + '.csv'
        with open(filename, 'rt') as fr:
            reader = csv.reader(fr)
            for i, row in enumerate(reader):
                if int(row[1]) == int(ploeg) and int(row[0]) == int(ronde):
                    return row[2:]

    def getScanResults(self):
         with open(RONDEFILES+SCANRAW, 'rt') as fr:
            reader = csv.reader(fr)
            for row in reader:
                yield row, IMAGESDIR + '{}_{}.jpg'.format(row[0], row[1])

    def getAllScanResults(self):
        data = []
        for X, a in enumerate(self.getScanResults()):
            data.append(a)
        return data
    
    def validateScanResult(self, row):
        writer = csv.writer(open(RONDEFILES + SCANCONTROL, 'a+'))
        writer.writerow(row)
        del writer

    def cleanScanRaw(self):
        tmp = RONDEFILES + 'tmp.csv'
        with open(RONDEFILES+SCANCONTROL, 'rt') as fr, open(RONDEFILES+SCANRAW, 'rt') as fr2, open(tmp, 'w') as fw:
            reader1 = csv.reader(fr)
            reader2 = csv.reader(fr2)
            writer = csv.writer(fw)
            checkcombo = []
            for row in reader1:
                checkcombo.append('{}_{}'.format(row[0], row[1]))

            for row in reader2:
                combo = '{}_{}'.format(row[0], row[1])
                if not combo in checkcombo:
                    writer.writerow(row)
                else:
                    checkcombo.remove(combo)
        shutil.move(tmp, RONDEFILES+SCANRAW)
        
        
    def setScore(self, ronde, ploeg, nieuweScore, scanner=0):
        tmp = RONDEFILES + 'tmp.csv'
        if scanner==1:
            filename = RONDEFILES + SCANRAW
        else:
            filename = RONDEFILES + USERPREFIX + RH.getRondenaam(ronde) + '.csv'
        with open(filename, 'rt') as fr, open(tmp, 'w') as fw:
            writer = csv.writer(fw)
            reader = csv.reader(fr)
            writer.writerow(next(reader))
            for i, row in enumerate(reader):
                if int(row[1]) == int(ploeg) and int(row[0]) == int(ronde):
                    writer.writerow(row[0:1] + nieuweScore)
                else:
                    writer.writerow(row)
        shutil.move(tmp, filename)

    def insertScore(self, ronde, ploeg, score, prefix):
        tmp = RONDEFILES + 'tmp.csv'
        filename = RONDEFILES + prefix + RH.getRondenaam(ronde) + '.csv'
        with open(filename, 'rt') as fr, open(tmp, 'w') as fw:
            writer = csv.writer(fw)
            reader = csv.reader(fr)
            writer.writerow(next(reader))
            ingevoegd = 0
            for i, row in enumerate(reader):
                if ingevoegd==0 and int(row[1]) > int(ploeg):
                    writer.writerow([ronde] + [ploeg] + score)
                    ingevoegd = 1
                writer.writerow(row)
        shutil.move(tmp, filename)

    def deleteScore(self, ronde, ploeg, prefix):
        tmp = RONDEFILES + 'tmp.csv'
        filename = RONDEFILES + prefix + RH.getRondenaam(ronde) + '.csv'
        with open(filename, 'rt') as fr, open(tmp, 'w') as fw:
            writer = csv.writer(fw)
            reader = csv.reader(fr)
            writer.writerow(next(reader))
            for i, row in enumerate(reader):
                if not int(row[1]) == int(ploeg):
                    writer.writerow(row)
        shutil.move(tmp, filename)
        
    def fromScannerToUser(self):
        #De SCANCONTROL sorteren volgens rondenummer
        #alles in SCANCONTORL omvromen naar rondefiles met userprefix
        #goed controleren op dubbele entries en ook toevoegen aan de rondefiles, niet overschrijven stel bijvoorbeeld dat een ronde in drie scanverwerkings wordt gedaan!
        #Scan CSV file wordt gewoon verwijderd!!!
       
        if SCANCONTROL in os.listdir(RONDEFILES):
            file = RONDEFILES+SCANCONTROL
            self.sorteer(file)
            
            with open(file, 'rt') as fr:
                reader = csv.reader(fr)
                currentRound = 9999
                mode = 'a'
                writer = None
                filename = ''
                for index, row in enumerate(reader):
                    row = list(map(int, row))
                    ronde = row[0]
                    ploeg = row[1]
                    score = row[2:]
                    if not ronde == currentRound and ronde>0:
                        #nieuweronde dus nieuwe file opendoen!
                        del writer
                        self.sorteerVerwijderDubbels(filename)
                        rondeNaam = RH.getRondenaam(ronde)
                        nieuw = not any(fname.endswith(rondeNaam + '.csv') for fname in os.listdir(RONDEFILES))
                        filename = RONDEFILES + USERPREFIX + rondeNaam + '.csv'
                        writer = csv.writer(open(filename, 'a'))
                        if nieuw:
                            header = ['RN', 'TN']
                            for i in range(0, len(score)):
                                header.append(i+1)
                            writer.writerow(header)
                    if ronde > 0:
                        #rondefile verder aanvullen
                        writer.writerow(row)
                    else:
                        #schifting en bonus
                        if len(score)>1:
                            PH.setSchiftingBonus(ploeg, score[0], score[1])
                        else:
                            PH.setSchiftingBonus(ploeg, score[0])
                    currentRound = ronde
                del writer
                self.sorteerVerwijderDubbels(filename)

            self.cleanScanRaw()
            try:
                os.remove(file)
            except:
                print('{} , niet kunnen verwijderen'.format(file))

    def sorteerVerwijderDubbels(self, filename):
        if filename.endswith('.csv'):
            tmp = RONDEFILES + 'tmp.csv'
            with open(filename, mode='rt') as fr, open(tmp, 'w') as fw:
                writer = csv.writer(fw)
                reader = csv.reader(fr)
                writer.writerow(next(reader))
                sorted2 = sorted(reader, key = lambda row: (int(row[1])))
                for count, row in enumerate(sorted2):
                    writer.writerow(row)
            shutil.move(tmp, filename)

            with open(filename, mode='rt') as fr, open(tmp, 'w') as fw:
                writer = csv.writer(fw)
                data = list(csv.reader(fr))
                writer.writerow(data[0])
                for X in range(1, len(data)-1):
                    if not data[X][1] == data[X+1][1]:
                        #geen dubbele entry voor deze ploeg in deze ronde
                        writer.writerow(data[X])
                writer.writerow(data[len(data)-1])
            shutil.move(tmp, filename)


    def checkAanwezigheden(self):
        nummers, _, _ = PH.aanwezigePloegen()
        ontbrekendeBestanden = []
        nietAanwezigeInvoer = []
        filenames = os.listdir(RONDEFILES)
        for count, filename in enumerate(filenames):
            if FINALPREFIX in filename:
                with open(RONDEFILES + filename, 'r') as fr:
                    data = list(csv.reader(fr))
                    if not len(data)-1 == len(nummers):
                        #miserie...
                        ronde = data[1][0]
                        for X in range(1, len(data)):
                            try:
                                index = nummers.index(int(data[X][1]))
                                del nummers[index]
                            except:
                                nietAanwezigeInvoer.append('{}_{}'.format(ronde,data[X][1]))
                                pass
                        for i in nummers:
                            ontbrekendeBestanden.append('{}_{}'.format(ronde,i))
                        nummers, _, _ = PH.aanwezigePloegen()

        
        #Verwijder de (foutieve) entry van ploegen die niet aanwezig zijn!
        for bestand in nietAanwezigeInvoer:
            ronde = list(map(int,bestand.split('_')))
            self.deleteScore(ronde[0], ronde[1], FINALPREFIX)
        #Voeg 0 toe bij de ontbrekende bestanden!
        for bestand in ontbrekendeBestanden:
            ronde = list(map(int,bestand.split('_')))
            NOQ, SUPER = RH.getVragenSuper(ronde[0])
            self.insertScore(ronde[0], ronde[1], [0]*NOQ*(1+2*SUPER), FINALPREFIX)
            
        return ontbrekendeBestanden, nietAanwezigeInvoer

    def makeFinal(self):
        #remove all files with FINALPREFIX
        #Check op aanwezigheden
        #voeg de bonusthema's toe!

        filenames = os.listdir(RONDEFILES)
        tmp = RONDEFILES +  'tmp.csv'
        for count, filename in enumerate(filenames):
            if FINALPREFIX in filename:
                os.remove(RONDEFILES + filename)

        geenBonus = []
        filenames = os.listdir(RONDEFILES)
        for count, filename in enumerate(filenames):
            if USERPREFIX in filename:
                with open(RONDEFILES + filename, 'r') as fr, open(tmp, 'w') as fw:
                    writer = csv.writer(fw)
                    reader = csv.reader(fr)
                    header = next(reader)
                    currentRound = 0
                    bonusRonde = 0
                    for row in reader:
                        ronde = int(row[0])
                        if not currentRound == ronde:
                            bonusRonde = RH.isBonusRonde(ronde)
                            if bonusRonde == 1:
                                header.append('Bonus')
                            writer.writerow(header)
                        if bonusRonde == 1:
                            schifting, bonus = PH.getSchiftingBonus(int(row[1]))
                            if bonus>0:
                                row.append(row[bonus+3])
                            else:
                                if not row[1] in geenBonus:
                                    geenBonus.append(row[1])
                        writer.writerow(row)
                        currentRound = ronde
                shutil.move(tmp, RONDEFILES+ filename.replace(USERPREFIX, FINALPREFIX))
        ontbreekt, fout = self.checkAanwezigheden()
        geenBonus = sorted(geenBonus)
        ontbreekt = sorted(ontbreekt)
        fout = sorted(fout)
        return geenBonus, ontbreekt, fout

    def sorteer(self, filename):
        tmp = 'tmp.csv'
        with open(filename, 'rt') as fr, open(tmp, 'w+') as fw:
            writer = csv.writer(fw)
            reader = csv.reader(fr)
            writer.writerow(next(reader)) #header
            sorted2 = sorted(reader, key = lambda row: (int(row[0]), int(row[1])))
            for count, row in enumerate(sorted2):
                writer.writerow(row)
        os.rename(tmp, filename)
        
   
read_Settings()
##for i, a in enumerate(getScanResults()):
##    if not i == 3:
##       validateScanResult(a[0])
##fromScannerToUser()
##makeFinal()
