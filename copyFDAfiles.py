import os
import fnmatch
import shutil

destination = "output.folder/"

def copy(path, file):
    source = path+"/"+file
    destination = "output.folder/" +createNewFileName(path, file)
    shutil.copyfile(source, destination)

def isTarget(file):
    if file.endswith(".fda"):
        return True
    else:
        return False

def createNewFileName(path, file):
    paths = path.split("/")
    newFilename=""
    for part in paths:
        newFilename = newFilename + part.capitalize()
    newFilename = newFilename[1::] + file
    return(newFilename)

def copyFile(path, file):
    if isTarget(file):
        copy(path, file)
    return 0


def traverseRoot(root):
    source = os.listdir(root)
    for file in source:
        if "." not in file:
            traverse(root+"/"+file)

        else:
            copyFile(root, file)
            
def traverse(baseDir):
    print("traverse(%s)"%baseDir)
    source = os.listdir(baseDir)
    for file in source:
        if "." not in file:
            traverse(baseDir+"/"+file)

        else:
            copyFile(baseDir, file)

if not os.path.exists(destination):
            os.makedirs(destination)
traverseRoot("./")
input("Done! Press enter to quit")
