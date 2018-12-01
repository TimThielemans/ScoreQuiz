import csv
import time
import math
import random
import shutil
import itertools
import configparser, inspect, os
import statistics
import ftplib


#================= GET SETTINGS FROM EMAIL SECTION IN settings.ini FILE ==============
def read_Settings():
    try:
        config = configparser.ConfigParser()
        config.read('settings.ini')

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
        global BONUSOVERVIEW
        global BONUSTHEMAS
        global SCHIFTING
        global SCORETEMPLATEHTML
        global SCOREHTMLFULL
        global SCOREHTMLLAST
        global CSSFINAL
        global CSSTEMPLATE
        global JSFINAL
        global JSTEMPLATE
        global AANTALTUSSENSTAND
        global FTPSERVER
        global FTPUSER
        global FTPPASSWORD

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        SCOREBORD = QUIZFOLDER+config.get('PATHS', 'SCOREBORD')
        SCOREBORDINFO = QUIZFOLDER+config.get('PATHS', 'SCOREBORDINFO')
        RONDEFILES = QUIZFOLDER+config.get('PATHS', 'RONDEFILES')
        IMAGESDIR = QUIZFOLDER+config.get('PATHS', 'OUTPUTIMAGES')
        BONUSOVERVIEW = QUIZFOLDER + config.get('PATHS', 'BONUSOVERVIEW')
        BONUSTHEMAS = config.get('COMMON', 'BONUSTHEMAS').split(',')
        AANTALTUSSENSTAND = int(config.get('COMMON', 'AANTALTUSSENSTANDRONDES'))

        SCORETEMPLATEHTML = config.get('PATHS', 'SCORETEMPLATE')
        SCOREHTMLFULL = QUIZFOLDER+config.get('PATHS', 'SCOREHTMLFULL')
        SCOREHTMLLAST = QUIZFOLDER+config.get('PATHS', 'SCOREHTMLLAST')
        CSSFINAL = QUIZFOLDER+config.get('PATHS', 'SCORECSS')
        CSSTEMPLATE = config.get('PATHS', 'CSSTEMPLATESCORE')
        JSFINAL = QUIZFOLDER+config.get('PATHS', 'SCOREJS')
        JSTEMPLATE= config.get('PATHS', 'JSTEMPLATESCORE')
        
        SCHIFTING = float(config.get('COMMON', 'SCHIFTING'))
        SCANRAW = config.get('COMMON', 'SCANRAW')
        SCANCONTROL = config.get("COMMON","SCANCONTROL")
        USERPREFIX = config.get("COMMON","USERPREFIX")
        FINALPREFIX = config.get("COMMON","FINALPREFIX")
        JPGPREFIX = config.get('COMMON', 'JPGPREFIX')

        FTPSERVER = config.get('COMMON', 'FTPSERVER')
        FTPUSER = config.get('COMMON', 'FTPUSER')
        FTPPASSWORD = config.get('COMMON', 'FTPPASSWORD')
        
    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})
#=====================================================================================

class Class_Scores():

    def __init__(self):
        read_Settings()

        from ronde_handler import Class_Rondes
        from inschrijving_handler import Class_Inschrijvingen
        self.RH = Class_Rondes()
        self.PH = Class_Inschrijvingen()

        global SUPERNR
        SUPERNR = self.RH.numberSuperRonde()

    
    def getImagesDir(self):
        return IMAGESDIR
    
    def getScanResults(self):
        try:
            with open(RONDEFILES+SCANRAW, 'rt') as fr:
                reader = csv.reader(fr)
                for row in reader:
                    yield row, IMAGESDIR + '{}_{}.jpg'.format(row[0], row[1])
        except:
            yield []

    def getAllScanResults(self):
        data = []
        for X, a in enumerate(self.getScanResults()):
            data.append(a)
        return data
    
    def validateScanResult(self, row):
        writer = csv.writer(open(RONDEFILES + SCANCONTROL, 'a+'))
        writer.writerow(row)
        del writer

    def clearImagesDir(self):
        files = os.listdir(IMAGESDIR)
        for filename in files:
            os.remove(IMAGESDIR + '/' + filename)

    def clearScoresDir(self):
        files = os.listdir(RONDEFILES)
        for filename in files:
            os.remove(RONDEFILES + '/' + filename)

    def cleanScanRaw(self):
        tmp = RONDEFILES + 'tmp.csv'
        with open(RONDEFILES+SCANCONTROL, 'rt') as fr, open(RONDEFILES+SCANRAW, 'rt') as fr2, open(tmp, 'w') as fw:
            reader1 = csv.reader(fr)
            reader2 = csv.reader(fr2)
            writer = csv.writer(fw)
            checkcombo = []
            for row in reader1:
                if '999' in row[1]:
                    row[1] = '999'
                checkcombo.append('{}_{}'.format(row[0], row[1]))
                
            for row in reader2:
                combo = '{}_{}'.format(row[0], row[1])
                if not combo in checkcombo:
                    writer.writerow(row)
                else:
                    checkcombo.remove(combo)
        shutil.move(tmp, RONDEFILES+SCANRAW)

    def getUserRondes(self):
        files = os.listdir(RONDEFILES)
        result = []
        for RN, ronde in enumerate(self.RH.getRondeNames()):
            for file in files:
                if USERPREFIX in file and ronde in file:
                    result.append(str(RN+1) + '_' + file.replace('.csv','').replace(USERPREFIX, ''))
                    break;
        return result
        
    def getScore(self, ronde, ploeg, scanner=0):
        if scanner==1:
            filename = RONDEFILES + SCANRAW
        else:
            filename = RONDEFILES + USERPREFIX + self.RH.getRondenaam(ronde) + '.csv'
        with open(filename, 'rt') as fr:
            reader = csv.reader(fr)
            next(reader)
            for i, row in enumerate(reader):
                if int(row[1]) == int(ploeg) and int(row[0]) == int(ronde):
                    return row[2:]
        return []
                
    def setScore(self, ronde, ploeg, nieuweScore, scanner=0):
        if '999' in str(ploeg):
            ploeg = int(str(ploeg).replace('999', ''))
        if ronde>0:
            tmp = RONDEFILES + 'tmp.csv'
            weggeschreven = False
            if scanner==1:
                filename = RONDEFILES + SCANRAW
            else:
                filename = RONDEFILES + USERPREFIX + self.RH.getRondenaam(ronde) + '.csv'
            with open(filename, 'rt') as fr, open(tmp, 'w') as fw:
                writer = csv.writer(fw)
                reader = csv.reader(fr)
                writer.writerow(next(reader))
                for i, row in enumerate(reader):
                    if int(row[1]) == int(ploeg) and int(row[0]) == int(ronde):
                        writer.writerow(row[0:2] + nieuweScore)
                        weggeschreven = True
                    else:
                        writer.writerow(row)
            if not weggeschreven:
                self.insertScore(ronde, ploeg, nieuweScore, USERPREFIX)
            else:      
                shutil.move(tmp, filename)
        else:
            if len(nieuweScore)>1: 
                self.PH.setSchiftingBonus(ploeg, nieuweScore[0], nieuweScore[1])
            else:
                self.PH.setSchiftingBonus(ploeg, nieuweScore[0])

    def insertScore(self, ronde, ploeg, score, prefix):
        tmp = RONDEFILES + 'tmp.csv'
        filename = RONDEFILES + prefix + self.RH.getRondenaam(ronde) + '.csv'
        with open(filename, 'rt') as fr, open(tmp, 'w') as fw:
            writer = csv.writer(fw)
            reader = csv.reader(fr)
            writer.writerow(next(reader))
            ingevoegd = 0
            for i, row in enumerate(reader):
                if not 'Max/Gem' in row:
                    if ingevoegd==0 and int(row[1]) > int(ploeg):
                        writer.writerow([ronde] + [ploeg] + score)
                        ingevoegd = 1
                elif ingevoegd == 0:
                    writer.writerow([ronde] + [ploeg] + score)
                    ingevoegd = 1
                
                writer.writerow(row)
        shutil.move(tmp, filename)

    def deleteScore(self, ronde, ploeg, prefix):
        tmp = RONDEFILES + 'tmp.csv'
        filename = RONDEFILES + prefix + self.RH.getRondenaam(ronde) + '.csv'
        with open(filename, 'rt') as fr, open(tmp, 'w') as fw:
            writer = csv.writer(fw)
            reader = csv.reader(fr)
            writer.writerow(next(reader))
            for i, row in enumerate(reader):
                if not 'Max/Gem' in row:
                    if not int(row[1]) == int(ploeg):
                        writer.writerow(row)
                else:
                    writer.writerow(row)
        shutil.move(tmp, filename)

    def getFinalScore(self, ploegnaamPositie):
        with open(SCOREBORD, 'rt') as fr:
            reader = csv.DictReader(fr)
            next(reader)
            for row in reader:
                if row['Ploegnaam'] == ploegnaamPositie or row['Pos'] == str(ploegnaamPositie):
                    return row
        return ''

    def getFinalScores(self, positie, aantaldeelnemers, plusmin):
        result = []
        posities = list(map(str, range(max(1, int(positie)-int(plusmin)), min(aantaldeelnemers, int(positie)+int(plusmin))+1)))
        with open(SCOREBORD, 'rt') as fr:
            reader = csv.reader(fr)
            for row in reader:
                if row[0] in posities:
                    result.append(row)
        return result
    
    def generateBonusOverview(self):
        #Bereken Score met originele thema
        #Bereken score voor al de andere thema's zet hiervoor al de thema's steeds eens op het zelfde voor alle ploegen en bereken opnieuw de score
        #Bekijk wat het beste resultaat was en schrijf dat in BONUSOVERVIEW
        #Zet de origineleBonusThemas terug in PLOEGINFO en maak opnieuw Final bestanden aan alsof er niets gebeurd is
        
        headers = ['TN', 'Ploegnaam', 'Origineel', 'OrigineelScore', 'Beste', 'BesteScore', 'Maximum']
        origineleBonusThemas = []
        aantalPloegen = 0
        for ploeginfo in self.PH.getPloegenDict():
            origineleBonusThemas.append(ploeginfo['Bonus'])
            aantalPloegen = aantalPloegen + 1 

        bonusScore = []
        for i in range(0, len(BONUSTHEMAS)):
            self.PH.setBonusses([i+1]*len(origineleBonusThemas))
            self.makeFinal()
            score, maximum = self.calculateBonusScore(aantalPloegen)
            bonusScore.append(score)

        self.PH.setBonusses(origineleBonusThemas)
        self.makeFinal()
        eigenScore, maximum = self.calculateBonusScore(aantalPloegen)
        with open(BONUSOVERVIEW, 'w') as fw:
            writer = csv.writer(fw)
            writer.writerow(headers)
            for i, ploeginfo in enumerate(self.PH.getPloegenDict()):
                if ploeginfo['Aangemeld'] == '1':
                    start = [ploeginfo['TN'], ploeginfo['Ploegnaam'], ploeginfo['Bonus'], eigenScore[i]]
                    besteScore = eigenScore[i]
                    beste = ploeginfo['Bonus']
                    for index in range(0, len(BONUSTHEMAS)):
                        if bonusScore[index][i]>besteScore:
                            besteScore = bonusScore[index][i]
                            beste = index
                else:
                    start = [ploeginfo['TN'], ploeginfo['Ploegnaam'], ploeginfo['Bonus'], 0]
                    besteScore = 0
                    beste = 0
                writer.writerow(start + [beste] + [besteScore] +[maximum])
                
    def calculateBonusScore(self, aantalPloegen):
        bonusscore=[0]*aantalPloegen
        maximum = 0
        filenames = os.listdir(RONDEFILES)
        with open(SCOREBORDINFO, 'rt') as fr:
            readerInfo = csv.DictReader(fr)
            for row in readerInfo:
                filename = FINALPREFIX + row['Ronde'] + '.csv'
                if filename in filenames and bool(self.RH.isBonusRonde(row['Ronde'])):
                    with open(RONDEFILES+ filename) as fr2:
                        reader = csv.DictReader(fr2)
                        for index, row in enumerate(reader):
                            if not '.' in row['TN']:
                                bonusscore[int(row['TN'])-1] = bonusscore[int(row['TN'])-1] + int(row['Bonus'])
                    maximum = maximum + 1

        return bonusscore, maximum
    
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
                    if '999' in str(ploeg):
                        ploeg = int(str(ploeg).replace('999', ''))
                        row = [ronde] + [ploeg] + score 
                    if not ronde == currentRound and ronde>0:
                        #nieuweronde dus nieuwe file opendoen!
                        del writer
                        self.sorteerVerwijderDubbels(filename)
                        rondeNaam = self.RH.getRondenaam(ronde)
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
                            self.PH.setSchiftingBonus(ploeg, score[0], score[1])
                        else:
                            self.PH.setSchiftingBonus(ploeg, score[0])
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
        aanwezig, afwezig = self.PH.aanwezigePloegen()
        nummers = []
        for ploeg in aanwezig:
            nummers.append(ploeg[0])
        originalNumbers = nummers
        ontbrekendeBestanden = []
        nietAanwezigeInvoer = []
        filenames = os.listdir(RONDEFILES)
        for count, filename in enumerate(filenames):
            if FINALPREFIX in filename:
                with open(RONDEFILES + filename, 'r') as fr:
                    data = list(csv.reader(fr))
                    ronde = data[1][0]
                    for X in range(1, len(data)-1):
                        try:
                            index = nummers.index(int(data[X][1]))
                            del nummers[index]
                        except:
                            nietAanwezigeInvoer.append('{}_{}'.format(ronde,data[X][1]))
                            pass
                    for i in nummers:
                        ontbrekendeBestanden.append('{}_{}'.format(ronde,i))
                       
            aanwezig, afwezig = self.PH.aanwezigePloegen()
            nummers = []
            for ploeg in aanwezig:
                nummers.append(ploeg[0])

        
        #Verwijder de (foutieve) entry van ploegen die niet aanwezig zijn!
        for bestand in nietAanwezigeInvoer:
            ronde = list(map(int,bestand.split('_')))
            self.deleteScore(ronde[0], ronde[1], FINALPREFIX)
        #Voeg 0 toe bij de ontbrekende bestanden!
        for bestand in ontbrekendeBestanden:
            ronde = list(map(int,bestand.split('_')))
            NOQ, SUPER = self.RH.getVragenSuper(ronde[0])
            bonus = self.RH.isBonusRonde(ronde[0])
            self.insertScore(ronde[0], ronde[1], [0]*(NOQ*(1+2*SUPER)+bonus), FINALPREFIX)
            
        return ontbrekendeBestanden, nietAanwezigeInvoer

    def makeFinal(self):
        #remove all files with FINALPREFIX
        #Check op aanwezigheden
        #voeg de bonusthema's toe!
        #Analyse van elke ronde op het einde (gemiddelde, aantalJuist per vraag)

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
                    superRonde = 0
                    totaalScore = []
                    JuisteAntwoorden = [0]*(len(header)-2)
                    for index, row in enumerate(reader):
                        ronde = int(row[0])
                        if not currentRound == ronde:
                            bonusRonde = self.RH.isBonusRonde(ronde)
                            superRonde = self.RH.isSuperRonde(ronde)
                            if bonusRonde == 1:
                                header.append('Bonus')
                                JuisteAntwoorden.append(0)
                            writer.writerow(header)
                        if bonusRonde == 1:
                            schifting, bonus = self.PH.getSchiftingBonus(int(row[1]))
                            if not bonus == 999:
                                if bonus>0:
                                    row.append(row[bonus+1])
                                else:
                                    if not int(row[1]) in geenBonus:
                                        geenBonus.append(int(row[1]))
                                    row.append(0)
                            else:
                                row.append(0) #de ploeg is niet aanwezig maar die wordt pas in checkAanwezigheden verwijderd
                        for i, score in enumerate(row[2:]):
                            JuisteAntwoorden[i] = JuisteAntwoorden[i]+int(score)
                        writer.writerow(row)
                        if superRonde == 1:
                            tmpscore = list(map(int, row[2:]))
                            totaalScore.append(sum(tmpscore[0:len(tmpscore):3])+2*sum(tmpscore[1:len(tmpscore):3])+3*sum(tmpscore[2:len(tmpscore):3]))
                        else:
                            totaalScore.append(sum(map(int, row[2:])))
                        currentRound = ronde
                        
                    writer.writerow([len(JuisteAntwoorden)] + [round(statistics.mean(totaalScore),2)] + JuisteAntwoorden + ['Max/Gem'])
                        
                shutil.move(tmp, RONDEFILES+ filename.replace(USERPREFIX, FINALPREFIX))
        aanwezig, _ = self.PH.aanwezigePloegen()
        geenSchifting = []
        for ploeg in aanwezig:
            schifting, bonus = self.PH.getSchiftingBonus(ploeg[0])
            if float(schifting) == 0:
                geenSchifting.append(ploeg[0])
        ontbreekt, fout = self.checkAanwezigheden()
        geenBonus = sorted(geenBonus)
        ontbreekt = sorted(ontbreekt)
        fout = sorted(fout)
        return geenBonus, geenSchifting, ontbreekt, fout

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


    def collectAllInfo(self):
    #Zet de verschillende csv files per ronde samen in een groot bestand en sorteert dit dan zodat alles per ploeg en dan per ronde staat gerangschikt
        tmp = 'tmp.csv'
        with open(tmp , 'w') as fw:
            writer = csv.writer(fw)
            filenames = os.listdir(RONDEFILES)
            for file in filenames:
                if file.endswith('.csv') and file.startswith(FINALPREFIX):
                    with open(RONDEFILES + file, mode='rt') as fr:
                        reader = csv.reader(fr)
                        next(reader)
                        for row in reader:
                            if not 'Max/Gem' in row:
                                row = list(map(int, row))
                                if row[0]==SUPERNR :
                                    score = sum(row[2:len(row):3])+2*sum(row[3:len(row):3])+3*sum(row[4:len(row):3])
                                else:
                                    score = sum(row[2::])
                                writer.writerow([row[1], row[0], score])

        #sorteer volgens tafelnummer en dan volgens rondenummer
        with open(tmp, mode='rt') as fr, open(SCOREBORD, 'w') as fw:
            writer = csv.writer(fw)
            reader = csv.reader(fr)
            writer.writerow(['TN', 'RN', 'Score'])
            sorted2 = sorted(reader, key = lambda row: (int(row[0]), int(row[1])))
            for row in sorted2:
                writer.writerow(row)

        
    def makeScorebordInfo(self):
        #Dit werkt enkel op basis van CollectAllInfo
        with open(SCOREBORD, mode ='rt') as fr, open(SCOREBORDINFO, 'w') as fw:
            fields = ['RN', 'Ronde', 'Afkorting', 'Maximum']
            writer = csv.DictWriter(fw, fields )
            reader = csv.DictReader(fr)
            writer.writeheader()
            vorigePloeg = 0
            for i, row in enumerate(reader):
                if i>0 and not int(row['TN']) == vorigePloeg:
                    break
                else:
                    rn = row['RN']
                    try:
                        info = self.RH.getRondeInfoDict(rn) #Rondenr, rondenaam, Afkorting, NOQ, superronde, bonusronde, sheet
                    except NameError:
                        print(rn)
                        raise
                    maximum = int(info['Aantal'])*(1+2*int(info['Super']))+int(info['Bonus']) #bonusronde + 1, superronde * 3
                    writer.writerow({'RN': rn, 'Ronde': info['Ronde'], 'Afkorting': info['Afkorting'] , 'Maximum': maximum})
                    vorigePloeg = int(row['TN'])

    def setHeaders(self):
        global FIELDNAMES
        global ROW1
        
        FIELDNAMES = ['Pos', 'TN', 'Ploegnaam', 'Score', '%']
        ROW1 = ['0', '0', 'Maximum','', '100']

        with open(SCOREBORDINFO, 'rt') as fr:
            readerInfo = csv.DictReader(fr)
            for row in readerInfo:
                FIELDNAMES.append(row['Afkorting'])
                ROW1.append(int(row['Maximum']))
        ROW1[3] = sum(ROW1[5:])
        FIELDNAMES.append('Schifting')
        ROW1.append(SCHIFTING)
        FIELDNAMES.append('NormSchifting')
        ROW1.append('')
        
    def generateScorebord(self, bonusGeneration):
        a = time.time()
        geenBonus, geenSchifting, ontbreekt, fout = self.makeFinal()
        print('makeFinal:', time.time()-a)
        self.collectAllInfo()
        self.makeScorebordInfo()
        self.setHeaders()
        
        geenScoresBeschikbaar = True
        
        tmp = 'tmp.csv'
        with open(SCOREBORD, mode='rt') as fr,  open(tmp, 'w') as fw:
            writer = csv.writer(fw)
            reader = csv.DictReader(fr)
            writer.writerow(FIELDNAMES)
            writer.writerow(ROW1)
            
            vorigePloeg = 0
            ploegdata = ['']
            for i, row in enumerate(reader):
                if not int(row['TN']) == vorigePloeg and not 'Max/Gem' in row:
                    #nieuwe ploeg
                    if i>0:
                        ploegdata[3] = sum(map(int,ploegdata[5:]))
                        ploegdata[4]= round(ploegdata[3]/ROW1[FIELDNAMES.index('Score')]*100, 2)
                        schiftingantwoord, Bonus = self.PH.getSchiftingBonus(vorigePloeg)
                        schiftingnorm = round(SCHIFTING/(abs(float(schiftingantwoord)-SCHIFTING)+0.0001), 3)
                        ploegdata.append(schiftingantwoord)
                        ploegdata.append(schiftingnorm)               
                        writer.writerow(ploegdata)
                    try:
                        ploegnaam = self.PH.getPloegnaam(row['TN'])
                        ploegdata = ['', row['TN'], ploegnaam, '', '']
                        ploegdata.append(row['Score'])
                    except NameError:
                        print(row['TN'])
                else:
                    #zelfde ploeg
                    ploegdata.append(row['Score'])

                vorigePloeg = int(row['TN'])

            #moet dat hier staan?
            if len(ploegdata)>1:
                ploegdata[3] = sum(map(int,ploegdata[5:]))
                ploegdata[4]= round(ploegdata[3]/ROW1[FIELDNAMES.index('Score')]*100, 2)
                schiftingantwoord, Bonus = self.PH.getSchiftingBonus(vorigePloeg)
                schiftingnorm = round(SCHIFTING/(abs(float(schiftingantwoord)-SCHIFTING)+0.0001), 3)
                ploegdata.append(schiftingantwoord)
                ploegdata.append(schiftingnorm)               
                writer.writerow(ploegdata)
                geenScoresBeschikbaar = False
                
                
        maximumScore = 0
        gemiddeldeScore = 0
        gemiddeldes = []

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
                        if 'Max/Gem' in row:
                            maximumRondeScore = row[0]
                            gemiddeldeRondeScore = round(float(row[1]),1)
                            gemiddeldes.append(gemiddeldeRondeScore)

                maximumScore = int(maximumRondeScore)+ maximumScore
                gemiddeldeScore = float(gemiddeldeRondeScore) + gemiddeldeScore

        newRow = ['0', '0', 'Gemiddelde', round(float(gemiddeldeScore), 2), round(float(gemiddeldeScore/maximumScore*100), 2)]
        newRow = newRow + gemiddeldes
        newRow.append('') #schifting
        newRow.append('') #normschifting
        
        
        #sorteren
        if not geenScoresBeschikbaar:
            with open(tmp, mode='rt') as fr, open(SCOREBORD, 'w') as fw:
                writer = csv.writer(fw)
                reader = csv.reader(fr)
                writer.writerow(FIELDNAMES)
                writer.writerow(newRow)
                writer.writerow(ROW1)
                next(reader)
                next(reader) 
                sorted2 = sorted(reader, key = lambda row: (float(row[FIELDNAMES.index('Score')]), float(row[FIELDNAMES.index('NormSchifting')])), reverse=True)
                for positie, row in enumerate(sorted2):
                    writer.writerow([positie+1] + row[1:])


        print('makeScorebord:',time.time()-a)
        if bonusGeneration:
            self.generateBonusOverview()
        print('generate BonusOverview:',time.time()-a)
            
        try:
            os.remove(tmp)
        except OSError:
            pass
        
        self.visualizeScorebord()
        return geenBonus, geenSchifting, ontbreekt, fout, SCOREHTMLFULL

    def visualizeScorebord(self):
        headers = ''
        body = ''
                
        with open(SCOREBORD, mode='rt') as fr: 
            reader = csv.reader(fr)
            row1 = next(reader)
            headers = headers + '"Pos"'
            headers = headers + ', "Ploegnaam"'
            headers = headers + ', "Tot"'
            for i in range(4, len(row1)-1):
                headers = headers + ', "{}"'.format(row1[i])

            for i, row in enumerate(reader):
                body = body + '["{}"'.format(row[0])                
                ploegnaam = row[2]
               # if len(ploegnaam)>25:
               #     ploegnaam= ploegnaam[:24]+'..'
                body = body + ', "{}"'.format(ploegnaam)
                body = body + ', "{}"'.format(row[3])
                body = body + ', "{}"'.format(row[4])
                for j in range(5, len(row)-1):#norm schifting moet er niet in
                    body = body + ', "{}"'.format(row[j])
                body = body + '],'

        
        
        template = open(SCORETEMPLATEHTML).read()
        fullHTML = open(SCOREHTMLFULL,"w")
        template = template.replace('{BODY}', body)
        template = template.replace('{HEADERS}', headers)
        fullHTML.write(template)
        fullHTML.close()

        self.uploadScorebordLive()


    def uploadScorebordPublic(self):
        ftp = ftplib.FTP(FTPSERVER)
        ftp.login(FTPUSER, FTPPASSWORD)  
        remote_path = "/htdocs/ScorebordFiles"
        ftp.cwd(remote_path)
        fh = open(SCOREHTMLFULL, 'rb')
        ftp.storbinary('STOR Sinterklaasquiz2018.html', fh)
        fh.close()

    def uploadScorebordLive(self):
        ftp = ftplib.FTP(FTPSERVER)
        ftp.login(FTPUSER, FTPPASSWORD)  
        remote_path = "/htdocs/ScorebordFiles"
        ftp.cwd(remote_path)
        fh = open(SCOREHTMLFULL, 'rb')
        ftp.storbinary('STOR goLiveTim.html', fh)
        fh.close()

            

            
                

        
        
