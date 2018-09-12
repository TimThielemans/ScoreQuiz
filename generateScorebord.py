import csv
import time
import math
import random
import itertools
import configparser, inspect, os
from ronde_handler import Class_Rondes
from inschrijving_handler import Class_Inschrijvingen
from score_handler import Class_Scores

#================= GET SETTINGS FROM EMAIL SECTION IN settings.ini FILE ==============
def read_Settings():

    global RH
    global PH
    global SUPERNR
    global SH
    RH = Class_Rondes()
    PH = Class_Inschrijvingen()
    SH = Class_Scores()
    SUPERNR = RH.numberSuperRonde()
    
    try:
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.realpath(__file__)) + '/settings.ini')

        global SCOREBORD
        global SCOREBORDINFO
        global RONDEFILES
        global SCHIFTING
        global FINALPREFIX
        global QUIZFOLDER

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        FINALPREFIX = config.get('COMMON', 'FINALPREFIX')
        SCOREBORD = QUIZFOLDER + config.get('PATHS', 'SCOREBORD')
        RONDEFILES = QUIZFOLDER +config.get('PATHS', 'RONDEFILES')
        SCOREBORDINFO = QUIZFOLDER + config.get('PATHS', 'SCOREBORDINFO')
        SCHIFTING = float(config.get('COMMON', 'SCHIFTING'))

    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})
#=====================================================================================

def collectAllInfo():
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

    ##try:
    #    os.remove(tmp)
    #except OSError:
    #    pass
    
def makeScorebordInfo():
    with open(SCOREBORD, mode ='rt') as fr, open(SCOREBORDINFO, 'w') as fw:
        fields = ['RN', 'Ronde', 'Maximum']
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
                    info = RH.getRondeInfo(rn) #Rondenr, rondenaam, NOQ, superronde, bonusronde, sheet
                except NameError:
                    print(rn)
                    raise
                maximum = int(info[2])*(1+2*int(info[3]))+int(info[4]) #bonusronde + 1, superronde * 3
                writer.writerow({'RN': rn, 'Ronde': info[1], 'Maximum': maximum})
                vorigePloeg = int(row['TN'])

def setHeaders():
    global FIELDNAMES
    global ROW1
    
    FIELDNAMES = ['Positie', 'TN', 'Ploegnaam', 'Totaal', 'Percent']
    ROW1 = ['', '', '','', '100']

    with open(SCOREBORDINFO, 'rt') as fr:
        readerInfo = csv.DictReader(fr)
        for row in readerInfo:
            FIELDNAMES.append(row['Ronde'])
            ROW1.append(int(row['Maximum']))
    ROW1[3] = sum(ROW1[5:])
    FIELDNAMES.append('Schifting')
    ROW1.append('')
    FIELDNAMES.append('NormSchifting')
    ROW1.append('')
        
def makeScorebord():
    tmp = 'tmp.csv'
    with open(SCOREBORD, mode='rt') as fr,  open(tmp, 'w') as fw:
        writer = csv.writer(fw)
        reader = csv.DictReader(fr)
        writer.writerow(FIELDNAMES)
        writer.writerow(ROW1)
        
        vorigePloeg = 0
        ploegdata = ['']
        for i, row in enumerate(reader):
            if not int(row['TN']) == vorigePloeg:
                #nieuwe ploeg
                if i>0:
                    ploegdata[3] = sum(map(int,ploegdata[5:]))
                    ploegdata[4]= round(ploegdata[3]/ROW1[FIELDNAMES.index('Totaal')]*100, 2)
                    schiftingantwoord, Bonus = PH.getSchiftingBonus(vorigePloeg)
                    schiftingnorm = round(SCHIFTING/(abs(float(schiftingantwoord)-SCHIFTING)+0.0001), 3)
                    ploegdata.append(schiftingantwoord)
                    ploegdata.append(schiftingnorm)               
                    writer.writerow(ploegdata)
                try:
                    ploegdata = ['', row['TN'], PH.getPloegnaam(row['TN']), '', '']
                    ploegdata.append(row['Score'])
                except NameError:
                    print(row['TN'])
            else:
                #zelfde ploeg
                ploegdata.append(row['Score'])

            vorigePloeg = int(row['TN'])

        ploegdata[3] = sum(map(int,ploegdata[5:]))
        ploegdata[4]= round(ploegdata[3]/ROW1[FIELDNAMES.index('Totaal')]*100, 2)
        schiftingantwoord, Bonus = PH.getSchiftingBonus(vorigePloeg)
        schiftingnorm = round(SCHIFTING/(abs(float(schiftingantwoord)-SCHIFTING)+0.0001), 3)
        ploegdata.append(schiftingantwoord)
        ploegdata.append(schiftingnorm)               
        writer.writerow(ploegdata)

    #sorteren
    with open(tmp, mode='rt') as fr, open(SCOREBORD, 'w') as fw:
        writer = csv.writer(fw)
        reader = csv.reader(fr)
        writer.writerow(FIELDNAMES)
        writer.writerow(ROW1)
        next(reader)
        next(reader)
        sorted2 = sorted(reader, key = lambda row: (row[FIELDNAMES.index('Totaal')], row[FIELDNAMES.index('NormSchifting')]), reverse=True)
        positie = 1
        for positie, row in enumerate(sorted2):
            writer.writerow([positie+1] + row[1:])
    try:
        os.remove(tmp)
    except OSError:
        pass

def main():
    read_Settings()

    a = time.time()

    geenBonus, ontbreekt, fout = SH.makeFinal()
    collectAllInfo()
    makeScorebordInfo()
    setHeaders()
    makeScorebord()

    return geenBonus, ontbreekt, fout

    print(time.time()-a)
    
if __name__ == '__main__':
    main()
