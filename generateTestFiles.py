import csv
import numpy as np
import random
import time
import csv
import time
import math
import random
import itertools
import configparser, inspect, os


 
#================= GET SETTINGS FROM EMAIL SECTION IN settings.ini FILE ==============
def read_Settings():
    try:
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.realpath(__file__)) + '/settings.ini')

        global PLOEGINFO
        global RONDEINFO
        global RONDEFILES
        global SCHIFTING
        global HEADERSglobal QUIZFOLDER

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        PLOEGINFO = QUIZFOLDER + config.get('PATHS', 'PLOEGINFOTEST')
        RONDEFILES = QUIZFOLDER + config.get('PATHS', 'RONDEFILES')
        RONDEINFO = QUIZFOLDER+ config.get('PATHS', 'RONDEINFOTEST')
        SCHIFTING = float(config.get('COMMON', 'SCHIFTING'))
        HEADERS = QUIZFOLDER + config.get('PATHS', 'HEADERS')

    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})
    except:
        raise
        
#=====================================================================================



def main():
   
    read_Settings()

    with open(HEADERS, 'rt') as fr, open(PLOEGINFO, 'w') as fw1, open(RONDEINFO, 'w') as fw2: 
        reader= csv.reader(fr)
        writer1 = csv.writer(fw1)
        writer2 = csv.writer(fw2)
        writer1.writerow(next(reader))
        writer2.writerow(next(reader))

    from ronde_handler import Class_Rondes
    from inschrijving_handler import Class_Inschrijvingen
    global RH
    global PH
    RH = Class_Rondes()
    PH = Class_Inschrijvingen()

    aantalPloegen = 60
    aantalGewoneRondes = 8

    
    for i in range(0, aantalGewoneRondes):
        RH.nieuweRonde(['Ronde{}'.format(i+1), 11, 0, 1])

    RH.nieuweRonde(['Ronde{}'.format(aantalGewoneRondes+1), 15, 0, 0])
    RH.nieuweRonde(['RondeSuper',10, 1, 0])

    for i in range(0, aantalPloegen):
        PH.nieuwePloeg(['Ploegske{}'.format(i+1), 'Tim', 'Thielemans', 'tim.thielemans@gmail.com'])
        PH.setSchiftingBonus('Ploegske{}'.format(i+1), SCHIFTING*random.uniform(0.5, 1.5), 2)

    for i, ronde in enumerate(RH.getRondes()):
        with open(RONDEFILES+ronde[1]+'.csv', 'w') as fw:
            writer = csv.writer(fw)
            NOQ, SUPER = RH.getVragenSuper(ronde[0])
            header = ['RN', 'TN']
            for j, ploeg in enumerate(PH.getPloegen()):
                data = [ronde[0], ploeg[1]]
                for k in range(0, int(NOQ)):
                    header.append(k+1)
                    data.append(random.randint(0, 1))
                if j == 0:
                    writer.writerow(header)
                writer.writerow(data)
    
if __name__ == '__main__':
    main()
