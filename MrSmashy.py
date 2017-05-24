import hashlib
import logging
import os
import subprocess

from tinydb import TinyDB, Query


logging.basicConfig(level=logging.INFO, format='%(message)s')
db = TinyDB('db.json')


def getFileExtension(filePath):
    fileName, extension = os.path.splitext(filePath)
    return extension.lower()[1:]


def getFileName(filePath):
    return os.path.split(filePath)[1]


def getHash(filePath):
    fileHash = hashlib.md5(open(filePath, 'rb').read()).hexdigest()
    return fileHash


def getListOfFiles(targetDirectory):
    listOfAllFiles = []
    for path, subdirectories, files in os.walk(targetDirectory):
        for fileName in files:
            filePath = os.path.join(path, fileName)
            listOfAllFiles.append(filePath)
    numberOfFilesFound = len(listOfAllFiles)
    logging.warning("Found a total of {} files".format(numberOfFilesFound))
    return listOfAllFiles


def hasFileChanged(filePath):
    currentHash = getHash(filePath)
    logging.warning("   Current hash of:  {}".format(currentHash))
    fileFingerPrints = Query()
    fileName = getFileName(filePath)
    result = db.get(fileFingerPrints.filePath == filePath)
    if result is None:
        logging.warning("   No previous hash found")
        return True
    logging.warning("   Previous hash of: {}".format(result['hash']))
    if currentHash == result['hash']:
        logging.warning("   File has not changed")
        return False
    else:
        logging.warning("{} has changed".format(fileName))
        return True



def updateFileHash(filePath):
    currentHash = getHash(filePath)
    db.insert({'filePath': filePath, 'hash': currentHash})


def smashFiles(listOfFiles):
    changedFiles = 0
    print(len(listOfFiles))
    for filePath in listOfFiles:
        fileName = getFileName(filePath)
        if fileName.endswith('.gz'):
            continue
        if fileName.endswith('.br'):
            continue
        logging.warning("Looking at {}".format(fileName))
        if hasFileChanged(filePath):
            smashImage(filePath)
            zopfiFile(filePath)
            brotliFile(filePath)
            updateFileHash(filePath)
            changedFiles += 1
            logging.warning("   I have fully smashed {}".format(fileName))
        else:
            logging.warning("   I will not smash {}".format(fileName))
    logging.warning("{} files have been smashed this session".format(changedFiles))


def brotliFile(filePath):
    brFileName = filePath + ".br"
    output = subprocess.check_output(["brotli", "--force", "-i", filePath, "-o", brFileName])
    logging.warning("   File has been Brotli compressed")

def zopfiFile(filePath):
    #output = subprocess.check_output(["zopfli", "--i1000", filePath])
    output = subprocess.check_output(["zopfli", "--i1", filePath])
    logging.warning("   File has been Zopfli compressed")


def smashImage(filePath):
    fileName = getFileName(filePath)
    extension = getFileExtension(filePath)
    JPEG_Extensions = ["jpeg", "jpg"]
    if extension in JPEG_Extensions:
        JPEG_Smash(filePath)
    PNG_Extensions = ["png",]
    if extension in PNG_Extensions:
        PNG_Smash(filePath)

def PNG_Smash(filePath):
    #smashCommand = ['optipng', '-o7', filePath]
    smashCommand = ['optipng', '-o1', filePath]
    output = subprocess.check_output(smashCommand)
    logging.warning("   PNG has been optimized")


def JPEG_Smash(filePath):
        smashCommand = ['jpegoptim', '--strip-all', '--all-progressive', '--max=90', filePath]
        output = subprocess.check_output(smashCommand)
        logging.warning("   JPEG has been optimized")


listOfListFiles = getListOfFiles('/home/jason/orko/www/jasonrigden.com')
smashFiles(listOfListFiles)
