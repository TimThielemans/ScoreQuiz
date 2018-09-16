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
        config.read('settings.ini')

        global PLOEGINFO
        global RONDEINFO
        global RONDEFILES
        global SCHIFTING
        global HEADERS
        global QUIZFOLDER
        global SCANRAW
        global DEFAULT_OUTPUTDIR

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        SCANRAW = config.get("COMMON","SCANRAW")
        DEFAULT_OUTPUTDIR = QUIZFOLDER + config.get("PATHS", "RONDEFILES")

       
        PLOEGINFO = QUIZFOLDER + config.get('PATHS', 'PLOEGINFO')
        RONDEFILES = QUIZFOLDER + config.get('PATHS', 'RONDEFILES')
        RONDEINFO = QUIZFOLDER+ config.get('PATHS', 'RONDEINFO')
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
    from inschrijving_handler import Class_Inschrijvingen
    from ronde_handler import Class_Rondes

    PH = Class_Inschrijvingen()
    RH = Class_Rondes()
    
    PH.verwijderAllePloegen()
    RH.verwijderAlleRondes()
    aantalPloegen = 60
    for i in range(0, aantalPloegen):
        PH.nieuwePloeg(['Ploegske{}'.format(i+1), 'Tim', 'Thielemans', 'tim.thielemans@gmail.com'])
        PH.aanmelden('Ploegske{}'.format(i+1))
        PH.setSchiftingBonus('Ploegske{}'.format(i+1), SCHIFTING*random.uniform(0.5, 1.5), random.randint(1,9))

    RH.nieuweRonde(['Ronde1', 'R1', 11, 0, 1])
    RH.nieuweRonde(['Ronde2', 'R2', 11, 0, 1])
    RH.nieuweRonde(['Tafelronde1', 'Taf1', 20, 0, 0]) 
    RH.nieuweRonde(['Ronde3', 'R3', 11, 0, 1]) 
    RH.nieuweRonde(['Ronde4', 'R4', 11, 0, 1]) 
    RH.nieuweRonde(['Ronde5', 'R5', 11, 0, 1]) 
    RH.nieuweRonde(['Ronde6', 'R6', 11, 0, 1])
    RH.nieuweRonde(['Tafelronde2', 'Taf2', 20, 0, 0])
    RH.nieuweRonde(['Ronde7', 'R7', 11, 0, 1]) 
    RH.nieuweRonde(['Ronde8', 'R8', 11, 0, 1])
    RH.nieuweRonde(['Finale', 'Finale', 15, 0, 0])

    with open(DEFAULT_OUTPUTDIR+SCANRAW, 'w') as fw:               
        writer = csv.writer(fw)
        for i, ronde in enumerate(RH.getRondes()):
            NOQ, SUPER = RH.getVragenSuper(ronde[0])
            for j, ploeg in enumerate(PH.getPloegen()):
                data = [ronde[0], ploeg[1]]
                for k in range(0, int(NOQ)):
                    if not SUPER:
                        data.append(random.randint(0, 1))
                writer.writerow(data)

if __name__ == '__main__':
    main()
