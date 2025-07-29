import locale
import os
import enum
import re
import sys

# folder path input 
folders = []

component = sys.argv[1]
#generate the path to which the required keys/logs will be downloaded

def get_download_path(component):
    component_path_map = { 
        "middleware": "/data/mwlogs/", 
        "upi": "/data/upilogs/",
        "fastag": "/data/fastaglogs/",
        "cbs": "/data/cbslogs/",
    }
    return component_path_map.get(component,None) 
dir_path = get_download_path(component)

# Funtion to print in Mb/Gb/Kb
class SIZE_UNIT(enum.Enum):
   BYTES = 1 
   KB = 2
   MB = 3
   GB = 4
def convert_unit(size_in_bytes, unit):
   if unit == SIZE_UNIT.KB:
       return size_in_bytes/1024
   elif unit == SIZE_UNIT.MB:
       return size_in_bytes/(1024*1024)
   elif unit == SIZE_UNIT.GB:
       return size_in_bytes/(1024*1024*1024)
   else:
       return size_in_bytes

# locale.setlocale(locale.LC_ALL, "")
def get_size(path):
    """Calculate total size of directory using os.walk()"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            # handles dangling symlinks
            if os.path.exists(filepath):
                total_size += os.stat(filepath).st_size
    return total_size

def print_sizes(root):
    total = 0
    paths = []
    n_ind = s_ind = 0
    output_foldername = []
    output_foldersize = []
    for name in sorted(os.listdir(root)):
        path = os.path.join(root, name)
        if not os.path.isdir(path):
            continue
        size = get_size(path)
        total += size
        s_size = locale.format('%8.0f', size, 3)
        n_ind = max(n_ind, len(name), 5)
        s_ind = max(s_ind, len(s_size))
        paths.append((name, s_size))
       
    for name, size in paths:        
        size=float(size.replace(',', ''))
        size= round(convert_unit(size,SIZE_UNIT.MB))
        print(name.ljust(n_ind), '~', size, 'MB')

# def get_folder_location_with_data(): 
#     try:
#         folders = next(os.walk(dir_path))[1]
#     except Exception as e:
#         print('Missing Folder: ' + str(e))
#     if component == "middleware":
#         for folder in folders:
#             if folder == "mwlogs":
#                 print_sizes(dir_path+"/"+folder)
#     elif component == "upi":
#         for folder in folders:
#             if folder == "upilogs":
#                 print_sizes(dir_path+"/"+folder)
#     elif component == "fastag":
#         for folder in folders:
#             if folder == "fastaglogs":
#                 print_sizes(dir_path+"/"+folder)
#     elif component == "cbs":
#         for folder in folders:
#             if folder == "cbslogs":
#                 print_sizes(dir_path+"/"+folder)
#     elif component == "acquirer":
#         for folder in folders:
#             if folder == "acquirerlogs":
#                 print_sizes(dir_path+"/"+folder)
#     else:
#         print ("No Log folder Found -- Error")


def get_folder_location_with_data(): 
    try:
        folders = next(os.walk(dir_path))[1]
    except Exception as e:
        print('Missing Folder: ' + str(e))
    print_sizes(dir_path)
#calling the  the folder location function

get_folder_location_with_data()
