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

       # QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')

        QUIZFOLDER = '/home/pi/Documents/ScoreQuiz/Test/'

        
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
    from score_handler import Class_Scores

    PH = Class_Inschrijvingen()
    RH = Class_Rondes()
    SH = Class_Scores()
    
    SH.clearScoresDir()
    SH.clearImagesDir()
    PH.verwijderAllePloegen()
    RH.verwijderAlleRondes()
    aantalPloegen = 58
    for i in range(0, aantalPloegen):
        PH.nieuwePloeg(['Ploegske{}'.format(i+1), 'Tim', 'Thielemans', 'hello@timtquiz.com'])
        PH.aanmelden('Ploegske{}'.format(i+1))
        PH.setSchiftingBonus('Ploegske{}'.format(i+1), round(SCHIFTING*random.uniform(0.5, 1.5)), random.randint(1,9))

   # RH.nieuweRonde(['Ronde1', 'R1', 11, 0, 0])
   # RH.nieuweRonde(['Ronde2', 'R2', 11, 0, 0])
   # RH.nieuweRonde(['Tafelronde1', 'Taf1', 20, 0, 0]) 
   # RH.nieuweRonde(['Ronde3', 'R3', 11, 0, 0]) 
   # RH.nieuweRonde(['Ronde4', 'R4', 11, 0, 0]) 
   # RH.nieuweRonde(['Ronde5', 'R5', 11, 0, 0]) 
   # RH.nieuweRonde(['Ronde6', 'R6', 11, 0, 0])
   # RH.nieuweRonde(['Tafelronde2', 'Taf2', 20, 0, 0])
   # RH.nieuweRonde(['Ronde7', 'R7', 11, 0, 0]) 
   # RH.nieuweRonde(['Ronde8', 'R8', 11, 0, 0])
   # RH.nieuweRonde(['Finale', 'Finale', 16, 0, 0])

    RH.nieuweRonde(['Mollen en kruisen', 'Muziek', 15, 0, 0])
    RH.nieuweRonde(['Tour de France', 'Tour', 26, 0, 0])
    RH.nieuweRonde(['Kettingronde', 'Ketting', 16, 0, 0]) 
    RH.nieuweRonde(['Tafelronde 1', 'Tafel1', 20, 0, 0]) 
    RH.nieuweRonde(['Poëzieronde', 'Poëzie', 15, 0, 0]) 
    RH.nieuweRonde(['Scrabbleronde', 'Scrabble', 15, 0, 0]) 
    RH.nieuweRonde(['Fotolinkronde', 'Foto', 16, 0, 0])
    RH.nieuweRonde(['Tafelronde 2', 'Tafel2', 20, 0, 0])
    RH.nieuweRonde(['Superronde', 'Super', 10, 1, 0])
    
    with open(DEFAULT_OUTPUTDIR+SCANRAW, 'w') as fw:               
        writer = csv.writer(fw)
        check = 0
        for i, ronde in enumerate(RH.getRondes()):
            NOQ, SUPER = RH.getVragenSuper(ronde[0])
            for j, ploeg in enumerate(PH.getPloegen()):
                data = [ronde[0], ploeg[1], check]
                for k in range(0, int(NOQ)):
                    if not SUPER:
                        data.append(random.randint(0, 1))
                writer.writerow(data)

if __name__ == '__main__':
    main()
