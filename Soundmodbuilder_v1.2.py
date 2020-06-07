import xml.etree.ElementTree as ET
import xml.dom.minidom as XML
import os
import shutil
from pathlib import Path
from io import BytesIO

CONFIG_XML_FILE = "Soundconfig.xml"
global CONFIG_XML_TREE
global MIXER_XML_TREE
INPUT_WAV = "InputWav"
INPUT_XML = "InputXML"
OUTPUT_MOD = "output"
SILENT_WAV = "silent"
global GAIN
GAIN = "0.8"
global PITCH
PITCH = "1"

global completedUnits
completedUnits = 0
global canceledUnits
canceledUnits = 0

global currentFaction
currentFaction = None
global currentUnit
currentUnit = None
global currentAction
currentAction = None

BASEDIRECTORY_XML = "Data/World/Units"
BASEDIRECTORY_WAV = "Data/Audio/Sounds/Cached/Units/DoWSounds"
DESTINATION_MIXER = "output/Data/Audio/Blueprints"
MIXER_NAME = "Mixer.xml.ext"

global CUSTOM_GAIN_FACTIONS
CUSTOM_GAIN_FACTIONS= ['Tyranids', 'Necrons']

global soundfileMapping
soundfileMapping = {
    "AstraMilitarum" : {},
    "Necrons" : {},
    "Neutral" : {},
    "Artefacts" : {},
    "Orks" : {},
    "SpaceMarines" : {},
    "Tyranids" : {},
    "ChaosSpaceMarines" : {},
    "Tau" : {}
    }

global CUSTOM_GAIN
CUSTOM_GAIN = {
    "soundname" : "gain",
    "soundname2" : "gain",
    }

def addSoundfileMapping(originalSoundname, newSoundname):
    global currentUnit
    global currentAction
    global currentFaction
    global soundfileMapping
    soundfileMapping[currentFaction][newSoundname]=[originalSoundname]

    
def getOldSoundName(faction, newSoundname):
    return soundfileMapping[faction][newSoundname] 


def getGain(soundName):    
    global GAIN
    if soundName[0] in CUSTOM_GAIN:
        return CUSTOM_GAIN[soundName[0]]
    else:
        return GAIN

def requiresCustomGain(faction):
    if faction in CUSTOM_GAIN_FACTIONS:
        return True
    else:
        return False


def createMixerXmlTree():
    global MIXER_XML_TREE
    MIXER_XML_TREE = ET.Element('mixer')
    MIXER_XML_TREE.set("distanceModel","InverseClamped")
    MIXER_XML_TREE.set("maxDistance","1000000")
    MIXER_XML_TREE.set("referenceDistance","1500")
    MIXER_XML_TREE.set("rolloffFactor","4")


def populateMixer(soundNames, faction):
    global MIXER_XML_TREE
    for name in soundNames:
        soundElement = ET.SubElement(MIXER_XML_TREE,"cachedSound")
        soundElement.set("name","Units/DoWSounds/"+faction+"/"+name)

        if requiresCustomGain(faction):
            oldSoundname = getOldSoundName(faction, name)
            soundElement.set("gain",getGain(oldSoundname))
        else:
            soundElement.set("gain",GAIN)
        soundElement.set("pitch",PITCH)
    

def fileExists(pathToFile):
    if not Path(pathToFile).is_file():
        print("Error! %s missing!" %pathToFile)
        return False
    return True


def doSoundsExist(soundList):
    returnvalue = True
    soundList = soundList.split(',')
    for sound in soundList:
        sound = sound.strip()
        value = fileExists(INPUT_WAV+"/"+sound+".wav")
        returnvalue = returnvalue and value
    return returnvalue


def voiceEntrysValid(configEntry):
    entriesValid = True
    for entry in configEntry:
        for attrib in entry.attrib:
            if entry.get(attrib).strip() !="":
                entriesValid = entriesValid and doSoundsExist(entry.get(attrib))
            else:
                entriesValid = entriesValid and True
        return entriesValid


def setupSuccesfull():
    global CONFIG_XML_TREE
    global INPUT_XML
    global OUTPUT_MOD
    setupSuccessfull = True
    if not fileExists(CONFIG_XML_FILE):
        print("Error! Soundconfig not found!")
        setupSuccessfull = False
    else:
        CONFIG_XML_TREE = ET.parse(CONFIG_XML_FILE)
    outputXML = OUTPUT_MOD+"/"+BASEDIRECTORY_XML
    outputWav = OUTPUT_MOD+"/"+BASEDIRECTORY_WAV
    try:
        if not os.path.exists(outputXML):
            os.makedirs(outputXML)
    except:
        print("Error! Failed to set up %s" %outputXML)
        setupSuccessfull = False
    try:
        if not os.path.exists(outputWav):
            os.makedirs(outputWav)
    except:
        print("Error! Failed to set up %s" %outputXML)
        setupSuccessfull = False

    try:
        if not os.path.exists(INPUT_XML):
           os.makedirs(INPUT_XML)
    except:
        print("Error! Failed to set up %s" %INPUT_XML)
        setupSuccessfull = False

    try:
        if not os.path.exists(OUTPUT_MOD):
           os.makedirs(OUTPUT_MOD)
    except:
        print("Error! Failed to set up %s" %OUTPUT_MOD)
        setupSuccessfull = False

    if len(os.listdir(INPUT_WAV)) == 0:
        print("Error! No Files in %s found" %INPUT_WAV)
        setupSuccessfull = False
    if len(os.listdir(INPUT_XML)) == 0:
        print("Error! No Files in %s found" %INPUT_XML)
        setupSuccessfull = False
    if len(os.listdir(OUTPUT_MOD)) != 0:
        print("Warning, %s not empty" %OUTPUT_MOD)          
    createMixerXmlTree()       
    return setupSuccessfull


def createFactionXmlDirectory(faction):
    if not os.path.exists(outputXML):
        os.makedirs(outputXML)


def generatePath(basePath, faction):
    path = basePath
    if faction == "Artefacts":
        path = path + "/Neutral/Artefacts"
    else:
        path = path+"/"+faction
    return path


def processNode(node):
    for unit in node:
        processUnit(node, unit)

        
def getVoiceEntrys(configResponseEntry):
    responseEntrys = {}
    for entry in configResponseEntry:
        for attrib in entry.attrib:
            if entry.get(attrib).strip() != "":
                responseEntrys[attrib] = entry.get(attrib)
                if attrib == "select":
                    responseEntrys[attrib] = responseEntrys[attrib]+","+SILENT_WAV
    return responseEntrys


def generateSoundName(baseName, soundNr):
    parts = baseName
    newSoundName = baseName+str(soundNr)
    return newSoundName


def generateVoiceFilenames(voiceList):
    global currentUnit
    global currentAction
    global soundfileMapping
    newVoiceFilenames = list()
    baseName = currentUnit + "_" + currentAction
    if len(voiceList) > 1:
        for i in range(0,len(voiceList)):
            newSoundName = generateSoundName(baseName, i)
            newVoiceFilenames.append(newSoundName)
            addSoundfileMapping(voiceList[i],newSoundName)           
    else:
        newVoiceFilenames.append(baseName)
    return newVoiceFilenames


def copySoundFiles(nameListOrig, nameListNew, faction):
    targetPath = "output"+"/"+generatePath(BASEDIRECTORY_WAV, faction)
    if not os.path.exists(targetPath):
            os.makedirs(targetPath)

    for i in range(0, len(nameListOrig)):
        shutil.copy(INPUT_WAV+"/"+nameListOrig[i].strip()+".wav", targetPath+"/"+nameListNew[i]+".wav")

        
def addToResponse(nodeResponses, attribute, sound, soundCount):
    newElem = ET.Element(attribute, sound=sound, soundCount = soundCount)
    nodeResponse.set(nodeResponses+sound, sound)
    nodeResponse.set(nodeResponses+sound, soundCount)    


def processDescriptionEntrys(descriptionEntrys, faction):
    global currentAction
    global currentFaction
    currentFaction = faction
    nodeResponses = None
    if descriptionEntrys:
        nodeResponses = ET.Element("responses")
        for entry in descriptionEntrys:
            currentAction = entry
            voiceList = descriptionEntrys[entry].split(",")
            soundCount = len(voiceList)
            newVoiceNames = generateVoiceFilenames(voiceList)
            copySoundFiles(voiceList, newVoiceNames, faction)
            populateMixer(newVoiceNames, faction)

            if soundCount > 1:
                newElem = ET.Element(entry, sound = "Units/DoWSounds/"+faction+"/"+newVoiceNames[0][:-1], soundCount = str(soundCount))
            else:
                newElem = ET.Element(entry, sound="Units/DoWSounds/"+faction+"/"+newVoiceNames[0])
            nodeResponses.append(newElem)
    return nodeResponses

        
def processUnit(faction, unit):
    global completedUnits
    global canceledUnits
    global currentUnit
    currentUnit = unit.tag
    print("Processing %s" %unit.tag)
    pathForWav = generatePath(BASEDIRECTORY_WAV, faction.tag)+"/"+unit.tag
    pathForXML = generatePath(BASEDIRECTORY_XML, faction.tag)+"/"+unit.tag

    if(fileExists(generatePath(INPUT_XML, faction.tag)+"/"+unit.tag+".xml") and voiceEntrysValid(unit)):
        try:
            origXML = ET.parse(generatePath(INPUT_XML, faction.tag)+"/"+unit.tag+".xml")
        except:
            canceledUnits = canceledUnits+1
            print("Something went wrong while processing \"%s\" and the file got skipped. Try validating the XML (www.xmlvalidation.com)"%(generatePath(INPUT_XML, faction.tag)+"/"+unit.tag+".xml"))

        descriptionEntrys = getVoiceEntrys(unit)
        responsesNode = processDescriptionEntrys(descriptionEntrys, faction.tag)
        if responsesNode:
            path = "output"+"/"+generatePath(BASEDIRECTORY_XML, faction.tag)
            if not os.path.exists(path):
                os.makedirs(path)

            origXML = ET.ElementTree()
            origXML._setroot(ET.Element('unit'))
            origXML.getroot().append(responsesNode)
            origXML.write("output/"+pathForXML+".xml.ext",encoding='utf-8', xml_declaration=True)

            completedUnits=completedUnits+1
    else:
        canceledUnits = canceledUnits+1
        print("-->Skipped unit \"%s\" because of missing file(s)"%unit.tag)


def processSoundConfig():
    root = CONFIG_XML_TREE.getroot()
    for faction in root:
        processNode(faction)

        
def createMixer_XML():
    tree = ET.ElementTree(MIXER_XML_TREE).getroot()
    xmlstr = ET.tostring(tree, encoding='utf8', method='xml')
    xml = XML.parseString(xmlstr)
    xml_pretty_str = xml.toprettyxml()
    if not os.path.exists(DESTINATION_MIXER):
        os.makedirs(DESTINATION_MIXER)
    xmlConfig = open(DESTINATION_MIXER+"/"+MIXER_NAME, "w")
    xmlConfig.write(xml_pretty_str)
    xmlConfig.close()

print("### Executing Soundmodbuilder v1.2 ###")
if setupSuccesfull():
    processSoundConfig()
    createMixer_XML()
    completed = completedUnits
    total = completedUnits +canceledUnits
    print("Completed " + str(completedUnits)+"/"+str(total)+" Units")
input("Press enter to quit")
