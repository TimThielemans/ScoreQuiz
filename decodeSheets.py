import argparse
import cv2
import math
import numpy as np
import time
from PIL import Image
import pytesseract
import os
import configparser
import csv
import shutil
from ronde_handler import Class_Rondes
from inschrijving_handler import Class_Inschrijvingen

CORNER_FEATS = (
    0.322965313273202,
    0.19188334690998524,
    1.1514327482234812,
    0.998754685666376,
)


#=====================================================================================================================================================

def readSettings():
    
    global NOQ 
    global SUPERRONDE 
    global RONDESETTINGS
    global ANSWERSHEET
    global BOX_SIZE
    global BOX_OFFSETY
    global BOX_SPACINGY
    global BOX_OFFSETX
    global BOX_SPACINGX
    global WIDTH
    global HEIGTH
    global BOX_OFFSETYBONUS
    global BOX_SPACINGYBONUS
    global BOX_OFFSETXBONUS
    global BOX_OFFSETXMISTAKE
    global BOX_OFFSETYMISTAKE
    global HR
    global HP
    global EMPTYSCANRAW

    EMPTYSCANRAW = True
    
    NOQ = 0
    SUPERRONDE = 0
    RONDESETTINGS = 99
    ANSWERSHEET = 99

    BOX_SIZE = 0
    BOX_OFFSETY = 0
    BOX_OFFSETX = 0
    BOX_SPACINGY = 0
    BOX_SPACINGX = 0
    BOX_OFFSETYBONUS = 0
    BOX_OFFSETXBONUS = 0
    BOX_SPACINGYBONUS = 0
    BOX_OFFSETYMISTAKE = 0
    BOX_OFFSETXMISTAKE = 0

    WIDTH = 0
    HEIGTH = 0
    
    HR = Class_Rondes()
    HP = Class_Inschrijvingen()
    
    try:
        config = configparser.ConfigParser()
        config.read('settings.ini')

        global RONDEINFO
        global BOXPERCENT
        global DEFAULT_OUTPUTDIR
        global DEFAULT_INPUTDIR
        global SCANRAW
        global JPGPREFIX
        global PROCESSEDDIR
        global OUTPUTIMAGES
        global MARKED_TRESHOLD
        global SHEETINFO
        global UPSIZING
        global QUIZFOLDER
        global SCHIFTINGDIGITS

        QUIZFOLDER = config.get('PATHS', 'QUIZFOLDER')
        BOXPERCENT = float(config.get('COMMON', 'BOXPERCENT'))
        SCHIFTINGDIGITS = int(config.get('COMMON', 'SCHIFTINGDIGITS'))
        SCANRAW = config.get("COMMON","SCANRAW")
        DEFAULT_OUTPUTDIR = QUIZFOLDER + config.get("PATHS", "RONDEFILES")
        OUTPUTIMAGES = QUIZFOLDER + config.get('PATHS', 'OUTPUTIMAGES')
        DEFAULT_INPUTDIR = config.get("PATHS", "FTP")
        JPGPREFIX = config.get('COMMON', 'JPGPREFIX')
        PROCESSEDDIR = config.get("PATHS", "PROCESSEDFILES")
        MARKED_TRESHOLD = float(config.get('COMMON', 'TRESHOLD'))
        SHEETINFO = QUIZFOLDER + config.get('PATHS', 'SHEETINFO')
        UPSIZING = int(config.get('COMMON', 'UPSIZE'))

    except Exception as error_msg:
        print("Error while trying to read Settings.")
        print({"Error" : str(error_msg)})

#=====================================================================================================================================================

def normalize(im):
    return cv2.normalize(im, np.zeros(im.shape), 0, 255, norm_type=cv2.NORM_MINMAX)

def get_approx_contour(contour, tol=.01):
    """Get rid of 'useless' points in the contour"""
    epsilon = tol * cv2.arcLength(contour, True)
    return cv2.approxPolyDP(contour, epsilon, True)

def get_contours(image_gray):
    img, contours, hierarchy = cv2.findContours(image_gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    return map(get_approx_contour, contours)

def get_corners(contours):
    return sorted(
        contours,
        key=lambda c: features_distance(CORNER_FEATS, get_features(c)))[:4]

def get_bounding_rect(contour):
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    return np.int0(box)

def get_convex_hull(contour):
    return cv2.convexHull(contour)

def get_contour_area_by_hull_area(contour):
    return (cv2.contourArea(contour) /
            cv2.contourArea(get_convex_hull(contour)))

def get_contour_area_by_bounding_box_area(contour):
    return (cv2.contourArea(contour) /
            cv2.contourArea(get_bounding_rect(contour)))

def get_contour_perim_by_hull_perim(contour):
    return (cv2.arcLength(contour, True) /
            cv2.arcLength(get_convex_hull(contour), True))

def get_contour_perim_by_bounding_box_perim(contour):
    return (cv2.arcLength(contour, True) /
            cv2.arcLength(get_bounding_rect(contour), True))

def get_features(contour):
    try:
        return (
            get_contour_area_by_hull_area(contour),
            get_contour_area_by_bounding_box_area(contour),
            get_contour_perim_by_hull_perim(contour),
            get_contour_perim_by_bounding_box_perim(contour),
        )
    except ZeroDivisionError:
        return 4*[np.inf]

def features_distance(f1, f2):
    return np.linalg.norm(np.array(f1) - np.array(f2))

# Default mutable arguments should be harmless here
def draw_point(point, img, radius=5, color=(0, 0, 255)):
    cv2.circle(img, tuple(point), radius, color, -1)
    #cv2.rectangle(img, (0,0), (int(BOX_SIZE), int(BOX_SIZE)), 120, -1)


def get_centroid(contour):
    m = cv2.moments(contour)
    x = int(m["m10"] / m["m00"])
    y = int(m["m01"] / m["m00"])
    return (x, y)

def order_points(points):
    """Order points counter-clockwise-ly."""
    origin = np.mean(points, axis=0)

    def positive_angle(p):
        x, y = p - origin
        ang = np.arctan2(y, x)
        return 2 * np.pi + ang if ang < 0 else ang

    return sorted(points, key=positive_angle)

def get_outmost_points(contours):
    all_points = np.concatenate(contours)
    return get_bounding_rect(all_points)

def perspective_transform(img, points):
    """Transform img so that points are the new corners"""

    source = np.array(
        points,
        dtype="float32")

    dest = np.array([
        [WIDTH, HEIGTH],
        [0, HEIGTH],
        [0, 0],
        [WIDTH, 0]],
        dtype="float32")

    img_dest = img.copy()
    transf = cv2.getPerspectiveTransform(source, dest)
    warped = cv2.warpPerspective(img, transf, (WIDTH, HEIGTH))
    return warped


#=====================================================================================================================================================

def get_processedImage(source_file):
    """Run the full pipeline:
        - Load image
        - Convert to grayscale
        - Filter out high frequencies with a Gaussian kernel
        - Apply threshold
        - Find contours
        - Find corners among all contours
        - Find 'outmost' points of all corners
        - Apply perpsective transform to get a bird's eye view
    """
    b = time.time()
    im_orig = cv2.imread(source_file)
    #print('reading' + str(time.time()-b))
    heigth, width = im_orig.shape[0:2]


################################# DIT AANPASSEN AAN DE HAND VAN DE RONDE FILES #########################################################################

    
    if not JPGPREFIX + '0_' in source_file:
        im_orig = im_orig[0.07*heigth:0.93*heigth, 0.6*width:0.98*width]
        #print('cut' + str(time.time()-b))
    else:
        #schiftingsformulier heeft andere marges
        im_orig = im_orig[0.3*heigth:0.92*heigth, 0.3*width:0.93*width]

######################################################## EINDE AANPASSEN #####################################################################
        
        
  #  blurred = cv2.GaussianBlur(im_orig, (11, 11), 10)    
    #print('blur' + str(time.time()-b))
    im = normalize(cv2.cvtColor(im_orig, cv2.COLOR_BGR2GRAY))
    #print('norm' + str(time.time()-b))

    ret, im = cv2.threshold(im, 127, 255, cv2.THRESH_BINARY)
    #print('treshold' + str(time.time()-b))
    contours = get_contours(im)
    #print('contours' + str(time.time()-b))
    corners = get_corners(contours)
    #print('corners' + str(time.time()-b))
    outmost = order_points(get_outmost_points(corners))
    #print('orderpoints' + str(time.time()-b))
    transf = perspective_transform(im_orig, outmost)
    #print('transform' + str(time.time()-b))
    #cv2.imwrite(QUIZFOLDER + 'debug/2blurred.jpg', im_orig)
    #cv2.imwrite('debug/4treshold.jpg', im)
    #cv2.drawContours(im_orig, corners, -1, (0, 255, 0), 3)
    #cv2.imwrite('debug/1original.jpg', im_orig)
    #cv2.imwrite('debug/5.jpg', im_orig)
    #cv2.imwrite('debug/6.jpg', transf)

    return transf

def get_question_patch(transf, q_number, super_index):
    percentage = BOXPERCENT
    # Top left
    tl = [BOX_OFFSETX-BOX_SIZE/2*percentage+BOX_SPACINGX*super_index, BOX_OFFSETY-BOX_SIZE/2*percentage+BOX_SPACINGY*q_number]
    # Bottom right
    br = [BOX_OFFSETX+BOX_SIZE/2*percentage+BOX_SPACINGX*super_index, BOX_OFFSETY+BOX_SIZE/2*percentage+BOX_SPACINGY*q_number]
    return transf[tl[1]:br[1], tl[0]:br[0]]

def get_bonus_patch(transf, q_number):
    percentage = BOXPERCENT
    # Top left
    tl = [BOX_OFFSETXBONUS-BOX_SIZE/2*percentage, BOX_OFFSETYBONUS-BOX_SIZE/2*percentage+BOX_SPACINGYBONUS*q_number]
    # Bottom right
    br = [BOX_OFFSETXBONUS+BOX_SIZE/2*percentage, BOX_OFFSETYBONUS+BOX_SIZE/2*percentage+BOX_SPACINGYBONUS*q_number]
    return transf[tl[1]:br[1], tl[0]:br[0]]

def getMistakePatch(transf):
    percentage = BOXPERCENT
    tl = [BOX_OFFSETXMISTAKE-BOX_SIZE/2*percentage, BOX_OFFSETYMISTAKE-BOX_SIZE/2*percentage]
    # Bottom right
    br = [BOX_OFFSETXMISTAKE+BOX_SIZE/2*percentage, BOX_OFFSETYMISTAKE+BOX_SIZE/2*percentage]
    return transf[tl[1]:br[1], tl[0]:br[0]]

def get_question_patches(transf):
    Question = 0
    for i in range(0, NOQ):
        if SUPERRONDE ==1:
            if i%3 == 0 and i>0:
                Question = Question + 1
            yield get_question_patch(transf, Question, i%3)
        else:
            yield get_question_patch(transf, i, i%3)

def get_schifting_patches(transf, digit):
    for i in range(0,10):
        yield get_question_patch(transf, i, digit)

def get_bonus_patches(transf):
    for i in range(0,9):
        yield get_bonus_patch(transf, i)

##def draw_marked(question_patch):
##    cx = int(BOX_SIZE/2)
##    cy = int(BOX_SIZE/2)
##    draw_point((cx, cy), question_patch, radius=3, color=(0, 255, 0))

def draw_marked(question_patch, color=(0, 100, 255), alpha = 0.2):
    overlay = question_patch.copy()
    cv2.rectangle(overlay, (0,0), (int(BOX_SIZE), int(BOX_SIZE)), color, -1)
    cv2.addWeighted(overlay, alpha, question_patch, 1 - alpha, 0, question_patch)
    if color == (0, 100, 255):
        global MISTAKEMADE
        MISTAKEMADE = 1

def is_marked(question_patch):
    means = np.mean(question_patch)
    # Simple heuristic
    if means > MARKED_TRESHOLD:
       # print('0: ' + str(means))
        return 0
    else:
       # print('1: ' + str(means))
        return 1

def checkMistakeField(image):   
    checkpatch = getMistakePatch(image)
    mistake = is_marked(checkpatch)
    if mistake:
        draw_marked(checkpatch,  alpha = 0.5, color = (0, 20, 255))
        global MISTAKEMADE
        MISTAKEMADE = 1
    return mistake
    
def get_answers(transf):
    answers = []
    superpatches = []
    superanswers = []
    for i, q_patch in enumerate(get_question_patches(transf)):
        checked = is_marked(q_patch)

        if checked is 1 and SUPERRONDE ==0:
            draw_marked(q_patch, color = (0, 255, 0))

        if SUPERRONDE == 1:
            superpatches.append(q_patch)
            superanswers.append(checked)
            if i%3 == 2:
                if (sum(superanswers)>1):
                    for j in range(0,3):
                        if superanswers[j] == 1:
                            draw_marked(superpatches[j])
                else:
                    for j in range(0,3):
                        if superanswers[j] == 1:
                            draw_marked(superpatches[j],  color=(0, 255, 0))
                superpatches = []
                superanswers = []
            
            
        answers.append(checked)
       # cv2.imwrite('debug/patch{}.jpg'.format(i+1), q_patch)
    
    return answers, transf

def decodeShifting(transf):
    schifting = ''
    for j in range(0, SCHIFTINGDIGITS):
        answers = []
        patches = []
        newdigit = '0' 
        for i, q_patch in enumerate(get_schifting_patches(transf, j)):
            checked = is_marked(q_patch)

            if checked is 1 and sum(answers)==0:
                draw_marked(q_patch, color = (0, 255, 0))
                newdigit  = str(i)
            patches.append(q_patch)
            answers.append(checked)
            
        if sum(answers)>1:
            for k in range(0, len(answers)):
                if answers[k] == 1:
                    draw_marked(patches[k])
        elif sum(answers) == 0:
            for k in range(0, len(answers)):
                draw_marked(patches[k])
        schifting+=newdigit
    return schifting, transf
                    

def decodeBonus(transf):
    answers = []
    patches = []
    bonus = 0
    for i, q_patch in enumerate(get_bonus_patches(transf)):
        checked = is_marked(q_patch)

        if checked is 1 and sum(answers)==0:
            draw_marked(q_patch, color = (0, 255, 0))
            bonus = i+1
        patches.append(q_patch)
        answers.append(checked)
        
    if sum(answers)>1:
        for k in range(0, len(answers)):
            if answers[k] == 1:
                draw_marked(patches[k])
    elif sum(answers) == 0:
        for k in range(0, len(answers)):
            draw_marked(patches[k])

    return bonus, transf

def setSheetSettings(sheetNumber, bonusRondes=0):
    global BOX_SIZE
    global BOX_OFFSETY
    global BOX_SPACINGY
    global BOX_OFFSETX
    global BOX_SPACINGX
    global HEIGTH
    global WIDTH
    global NOQ
    global SUPERRONDE
    global ANSWERSHEE    
    global BOX_OFFSETYBONUS
    global BOX_SPACINGYBONUS
    global BOX_OFFSETXBONUS
    global BOX_OFFSETXMISTAKE
    global BOX_OFFSETYMISTAKE
    with open(SHEETINFO, mode='rt') as fr:
        reader = csv.DictReader(fr)
        for row in reader:
            if int(row['SN']) == sheetNumber:
                HEIGTH = int(row['Heigth'])*UPSIZING
                WIDTH = int(row['Width'])*UPSIZING
                BOX_SIZE = float(row['BoxSize'])*UPSIZING
                BOX_SPACINGY = float(row['BoxSpacingY'])*UPSIZING
                BOX_SPACINGX = float(row['BoxSpacingX'])*UPSIZING
                BOX_OFFSETY = float(row['BoxOffsetY'])*UPSIZING
                BOX_OFFSETX = float(row['BoxOffsetX'])*UPSIZING
                BOX_OFFSETXMISTAKE = float(row['BoxOffsetXMistake'])*UPSIZING
                BOX_OFFSETYMISTAKE = float(row['BoxOffsetYMistake'])*UPSIZING
                NOQ = int(row['Aantal'])

                if bonusRondes>0:
                    BOX_SPACINGYBONUS = float(row['BoxSpacingYBonus'])*UPSIZING
                    BOX_OFFSETYBONUS = float(row['BoxOffsetYBonus'])*UPSIZING
                    BOX_OFFSETXBONUS = float(row['BoxOffsetXBonus'])*UPSIZING
                break
    ANSWERSHEET = sheetNumber

def decodeSheet(filename, outputDir, rondeCheck):
    
    tmp = filename.split('/')
    filenew = tmp[len(tmp)-1]
    ronde,ploeg= filenew.replace('.jpg', '').replace(JPGPREFIX, '').split('_')
    #print('R' + ronde + '_' + ploeg)
    ronde = int(ronde)
    ploeg = int(ploeg)
     
    global RONDESETTINGS
    global SUPERRONDE
    global MISTAKEMADE
    MISTAKEMADE = 0

    if ronde>0:
        #decoding van een ronde
        if not ronde == RONDESETTINGS:
            RONDESETTINGS = ronde
            newAnswerSheet = int(HR.getSheet(ronde))
            SUPERRONDE = int(HR.isSuperRonde(ronde))
            if not ANSWERSHEET == newAnswerSheet:
                setSheetSettings(newAnswerSheet)

        #a = time.time()
        image = get_processedImage(filename)
       # print(time.time()-a)
        answers, im = get_answers(image)
    else:
        #decoding van shiftingsvraag en eventueel bonusthema
        if not ronde == RONDESETTINGS:
            RONDESETTINGS = ronde
            if not ANSWERSHEET < 3:
                if HR.numberBonusRondes()>0:
                    setSheetSettings(2, 1)
                else:
                    setSheetSettings(1, 0)      
        answers = []
        #a = time.time()
        image = get_processedImage(filename)
        #print(time.time()-a)
        schifting, im = decodeShifting(image)
        answers.append(schifting)
        if HR.numberBonusRondes()>0:
            bonus, im = decodeBonus(im)
            answers.append(bonus)

    checkMistakeField(image)
    check = MISTAKEMADE
    cv2.imwrite(OUTPUTIMAGES + '{}_{}.jpg'.format(ronde,ploeg), im)

    
    return answers, ronde, ploeg, check

def deleteIfPresent(ronde, ploeg):
    tmp = 'tmp.csv'
    with open(DEFAULT_OUTPUTDIR + SCANRAW, 'r') as fr,open(tmp, 'w') as fw:
        reader = csv.reader(fr)
        writer = csv.writer(fw)
        for row in reader:
            if not (row[0] == str(ronde) and row[1] == str(ploeg)):
                writer.writerow(row)
    shutil.move(tmp, DEFAULT_OUTPUTDIR + SCANRAW)

def isScanRawEmpty():
    global EMPTYSCANRAW
    try:
        with open(DEFAULT_OUTPUTDIR + SCANRAW, 'r') as fr:
            reader = csv.reader(fr)
            if len(list(reader))>0:
                EMPTYSCANRAW = False
            else:
                EMPTYSCANRAW = True
    except:
        EMPTYSCANRAW = True

def decodeAndSave(inputDir, outputDir, doAll, rondeCheck):
    isScanRawEmpty()
    timeID = time.strftime('%Hu%M')
    intermediate = outputDir + 'Intermediate_{}.csv'.format(timeID)
    with open(intermediate, 'w') as csvfile:
        filewriter = csv.writer(csvfile)
        filenames = os.listdir(inputDir)
        for count, filename in enumerate(filenames):
            if filename.endswith('.jpg') and filename.startswith(JPGPREFIX):
                result, ronde, ploeg, check = decodeSheet(inputDir + filename, outputDir, rondeCheck)
                if not EMPTYSCANRAW:
                    deleteIfPresent(ronde, ploeg)
                if int(ploeg) == 999:
                    check = 1
                resultnew = [ronde] + [ploeg] + [check] + result
                filewriter.writerow(resultnew)
                try:
                    os.remove(PROCESSEDDIR +'/' + filename)
                except:
                    pass
                shutil.move(inputDir + filename, PROCESSEDDIR)
                print('R{}_{}'.format(ronde, ploeg))
                if doAll < 1:
                    break

    finalFilename = outputDir + SCANRAW    
    with open(intermediate, mode='rt') as f, open(finalFilename, 'a+') as final:
        writer = csv.writer(final, delimiter=',')
        reader = csv.reader(f, delimiter=',')
        sorted2 = sorted(reader, key = lambda row: (int(row[0]), int(row[1])))
        for count, row in enumerate(sorted2):
            writer.writerow(row)

    count = count+1

    try:
        os.remove(intermediate)
    except OSError:
        print('missed')
        pass

    return count, timeID
            
        
def main(inputDirA, doAllA, rondeCheckA, outputDirA):

    readSettings()
    inputDir = inputDirA or DEFAULT_INPUTDIR
    doAll = doAllA or 1
    rondeCheck = rondeCheckA or 0
    outputDir = outputDirA or DEFAULT_OUTPUTDIR

    starttime = time.time()

    items,timeID = decodeAndSave(inputDir, outputDir, doAll, rondeCheck)

    processtime = time.time()-starttime;

    if items == 0:
        items = 1
    
    print('Process time: {}s with an average of {}s/sheet'.format(round(processtime,3), round(processtime/items,3)))
    return items, processtime


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    readSettings()

    parser.add_argument("--inputDir", help="Input directory", default = DEFAULT_INPUTDIR, type=str)
    parser.add_argument("--outputDir", help="Output directory", default = DEFAULT_OUTPUTDIR, type=str)
    parser.add_argument("--all", type=int, default=1, help="Convert all documents")
    parser.add_argument("--rondeCheck", type=int, default=0, help="OCR on ronde")
 
    args = parser.parse_args()
    main(args.inputDir, args.all, args.rondeCheck, args.outputDir)
