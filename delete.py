import os
import shutil
import sys

component = sys.argv[1]
foldername = sys.argv[2]
#generate the path to which the required keys/logs will be downloaded

def get_download_path(component):
  component_path_map = { 
        "middleware": "/data/mwlogs", 
        "upi": "/data/upilogs",
        "fastag": "/data/fastaglogs",
        "cbs": "/data/cbslogs",
        "kyc": "/data/kyclogs",
        "coms": "/data/comslogs"
    }
  return component_path_map.get(component,None) 

dir_path = get_download_path(component)
dir_path = dir_path + "/" + foldername

def deletedir(dir_path):
    dirpath = os.path.join(dir_path)
    if os.path.exists(dirpath) and os.path.isdir(dirpath):
        shutil.rmtree(dirpath)
        print ("Directory Deleted")
    else:
        print ("Log Directory does not exist")
print(dir_path)
deletedir(dir_path) 
