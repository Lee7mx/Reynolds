#!/usr/bin/env python
#Created by Mike Lee 2020-01-06
#Tar up files based on file size. This will be used primarily for IDMt to Kodata projects. This will probably only work if you run msb2kod.sh.

import os, sys, shutil, subprocess

output = sys.argv[1]

####################USER DEFINED METHODS####################
#Method that will convert bytes to human-readable format
def convert_bytes(bytes):
    bytes = float(bytes)
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return "%3.1f %s" % (bytes, x)
        bytes /= 1024.0
#Method that will get the file size
def get_fileSize(filepath):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(filepath):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size

def main():

    #Assigning path to the folder containing items to be compressed.
    path = os.getcwd()+'/'+output
    #Lists each item in the folder.
    check_stores = os.listdir(path)

    #Parsing through
    for store in check_stores:
        check_branches = os.listdir(path+'/'+store)
        for branch in check_branches:
            check_applications = os.listdir(path+'/'+store+'/'+branch)
            for application in check_applications:
                archive_path = path+'/'+store+'/'+branch+'/'+application
                check_doctypes = os.listdir(archive_path)
                for doctype in check_doctypes:
                    temp_path = archive_path+'/'+doctype
                    #Grabbing the size of the file
                    size = convert_bytes(get_fileSize(temp_path))
                    size_list = size.split(' ')
                    #If the file is greater than 6.5 GB, then it will walk into the next directory and compress the items in there.
                    if (float(size_list[0]) > 6.5) and (size_list[1] == 'GB'):
                        new_path = os.listdir(temp_path)
                        for month in new_path:
                            subprocess.call(['tar', '-czvf', archive_path+'/'+doctype+'~'+month+'.tar.gz', new_path])
                    else:
                        subprocess.call(['tar', '-czvf', archive_path+'/'+doctype+'.tar.gz', temp_path])

if __name__=="__main__":
    main()