import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as XML

global xmlTree
xmlTree = ET.Element("config")

def addNode(node):
    xmlTree.getroot()

def traverseRoot(root):
    source = os.listdir(root)
    for file in source:
        if "." not in file:
            traverse(root+'/'+file)


def extractName(path):
    if '/' in path:
        pathList = path.split('/')
        path = path.split('/')[-1]
    return path

def addParams(treeElem):
    responses = ET.SubElement(treeElem, "responses")
    responses.set("move","")
    responses.set("attack","")
    responses.set("select","")
    responses.set("productionCompleted","")

def traverse(baseDir):
    factionName = extractName(baseDir)
    source = os.listdir(baseDir)
    faction = ET.SubElement(xmlTree,factionName)
    for file in source:
        if "." not in file:
            traverse(baseDir+"/"+file)

        else:
            unit = ET.SubElement(faction, file.split('.')[0])
            addParams(unit)

def createConfigTemplate():
    tree = ET.ElementTree(xmlTree).getroot()
    xmlstr = ET.tostring(tree, encoding='utf8', method='xml')
    xml = XML.parseString(xmlstr)
    xml_pretty_str = xml.toprettyxml()
    xmlConfig = open("Soundconfig_template.xml", "w")
    xmlConfig.write(xml_pretty_str)
    xmlConfig.close()

traverseRoot("InputXML")
createConfigTemplate()
input("Done! Press enter to quit")
