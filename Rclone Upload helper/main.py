import json
import subprocess
import os
import datetime as dt
from colorama import Fore


from tqdm import tqdm 
from rclone_python import rclone



drive_path = input("\nEnter the path of the drive \n>> ") 
source_path = input("\nEnter the path of the source \n >> ")

print("=============Program Start=========================")


if rclone.Callable is False:
    print(Fore.RED+"Unable to reach to the Cloud Drive")
    exit()

source_data = []
target_data = []
target_dir = []
source_dir = []

if os.path.isdir(source_path) is False:
    print(Fore.RED+"Source folder is not present in the path.")
    exit()

if os.path.isdir('.rclone_logs') is True:
    os.system('rm -r .rclone_logs')

try:
    print(Fore.GREEN+"Fetching data from the source and the cloud .....\n")

    pbar = tqdm(total=100,ascii=False,colour='green',ncols=100,desc='Fetching the data :: ',unit="data")

    os.system(f"rclone mkdir {drive_path}")

    pbar.update(10)

    os.system(f'mkdir .rclone_logs')

    pbar.update(10)

    os.system(f'rclone mkdir {drive_path}')	

    pbar.update(10)

    os.system(f'rclone lsjson -R {source_path} >> .rclone_logs/source.json && rclone lsjson -R {drive_path}>> .rclone_logs/target.json' )

    pbar.update(40)

    with open(".rclone_logs/source.json", "r")  as file:
        source_data = json.load(file)
        file.close()

    pbar.update(10)

    with open(".rclone_logs/target.json","r") as file:
        target_data = json.load(file)
        file.close()

    pbar.update(20)

    # os.system('rm -r .rclone_logs')

    pbar.close()

    print(Fore.GREEN+"\nDatat is fetch !!")

except Exception as error:
    print(Fore.RED+str(error))
    exit()

print(Fore.WHITE+"===============================================")

if target_data.__len__() == 0 and source_data.__len__() == 0:
    print(Fore.RED+"\n Note :: Source and the Drive both are empty !!!")
    exit()

elif target_data.__len__() == 0:
    print(Fore.RED+"\n Note :: No file is found in the cloud !!!\n")

    print("Total Size of total upload is :: ",os.system(f'du -sh {source_path}'))

    if input(Fore.GREEN+"\nEnter 'y' to confirm and for cancel press any key ::: \n>> ").lower() == 'y':

        rclone.sync(src_path=source_path,dest_path=drive_path,show_progress=True)

        print(Fore.GREEN+"\n Upload Completed ...")

    else:
        print("\n The process is canceled!!")
        exit()

elif source_data.__len__() == 0:
    print(Fore.RED+"\n ote :: No file is found in the source folder(folder on current device) !!!\n")

    size_of_download = 0
    for file in target_data:
        size_of_download = size_of_download + file['Size']
    
    print(Fore.WHITE+"Total Size of total download is :: ",round(size_of_download/(1024*1024),3))
    if input("\nEnter 'y' to confirm and for cancel press any key ::: \n >> ").lower() == 'y':
        rclone.sync(dest_path=source_path,src_path=drive_path,show_progress=True)
        print(Fore.GREEN+"\n Download Completed ...")
    else:
        print(Fore.GREEN+"\n The process is canceled!!")
        exit()




for i in range(0,max(source_data.__len__(),len(target_data))):
    try:
        if (source_data[i])['IsDir'] is True:
            source_dir.append(source_data[i])
            source_data.pop(i)
    except:
        pass
    try:
        if (target_data[i])['IsDir'] is True:
            target_dir.append(target_data[i])
            target_data.pop(i)
    except:
        pass


print("+=================Processing Data==================+")

new_files = []
new_dir = []
diff_extension_files  = []
modified_files = []


size_of_upload = 0

print("\n New Folders are :: \n")


for source in source_dir:
    for target in target_dir:
        if source['Path'] == target['Path']:
            print(f'\t>>>\t{source["Path"]}')
            break
    new_dir.append(source)

if new_dir.__len__() == 0:
    print("\t\tNo New Folder is Found\n")
else:
    print(f"\n Total Number of New folders are : {new_dir.__len__()}")

print("===============================================")

print("\n New Files are (excluding those whose are in new folders):: \n")
print("\t\tSize(MB)\tName")

for source in source_data:
    
    is_done = False
    in_new_dir = False

    for dir in new_dir:
        if dir['Path'] in source['Path']:
            in_new_dir = True
            source_data.remove(source)
            break
    
    if in_new_dir is False:
        for target in target_data:
            if source['Path'] == target['Path']:
                if source['Size'] == target['Size'] :
                    if source['ModTime'].split("T")[0] == target['ModTime'].split("T")[0] or source['IsDir'] is True:
                        if(source['MimeType'] == target['MimeType'] or source['MimeType'].split(";")[0] == target['MimeType']):
                            is_done = True
                            target_data.remove(target)
                            break
                        else:
                            is_done = True
                            temp = [source,target]
                            diff_extension_files.append(temp)
                            target_data.remove(target)
                            break
                    else:
                        modified_files.append(source)
                        is_done = True
                        target_data.remove(target)
                        break
                else:
                    modified_files.append(source)
                    is_done = True
                    target_data.remove(target)
                    break

    if is_done is False:
        new_files.append(source)
        print(f">>> {source['Size']/(1024*1024)}\t{source['Path']}")
        size_of_upload = int(source['Size']) + size_of_upload

if (new_files.__len__()) == 0:
    print("\t\tNo New File")
else:
    print(f'\n Total Number of new files are :: {new_files.__len__()}')

print("===============================================")

if modified_files.__len__ !=0:

    print("\n Modified Files are :: \n")
    print("\t\tSize(MB)\tName")

    for source in modified_files:
        print(f">>> {source['Size']/(1024*1024)}\t{source['Path']}")
        size_of_upload = int(source['Size']) + size_of_upload

    print("===============================================")

if new_files.__len__() + modified_files.__len__() + new_dir.__len__() == 0:
    print(Fore.GREEN+"\tAll files are already in the cloud and all they are up to date")
    exit()

print(Fore.WHITE+f"\nTotal Size of upload is :: {size_of_upload/(1024*1024)}")

print(Fore.WHITE+"===============================================")

if input(Fore.GREEN+"Enter y to confirm to upload \n for cancel press any key :: \n >>>  ").lower() == 'y':

    print("\n Uploading the New Folders")

    print(Fore.WHITE+"\n")
    try:
        for dir in new_dir:
            rclone.copyto(in_path=dir['Path']+'/',out_path=drive_path,show_progress=True)
        
        print(Fore.GREEN+"\nUploading the folders is complete\n")
        print(Fore.WHITE+"===============================================")

        print(Fore.GREEN+"\n Uploading the New Files and Modified Files")
        print(Fore.WHITE+"\n")

        for file in new_files:
            rclone.copy(in_path=file['Path'],out_path=drive_path,show_progress=True,ignore_existing=True)
        print(Fore.GREEN+"\n New Files are uploaded ")
        print(Fore.WHITE+"\n")

        time = str(dt.datetime.now())
        for file in modified_files:
            rclone.copy(in_path=source_path+file['Path'],out_path=drive_path+file['Path']+f"({time})",show_progress=True,ignore_existing=True)
        print(Fore.GREEN+"\n New Files are uploaded \n")

        print(Fore.GREEN+"Uploaded complete\n")

        print(Fore.WHITE+"===============================================")

        print(f' Note::  Number of Conficted files are :: {diff_extension_files.__len__()}')
        if diff_extension_files.__len__() != 0:
            with open("./Confict.json",'r') as file:
                writer = json.dumps(diff_extension_files) 
                file.write(writer)
            print("All confict are save in json files with there copy in the drive")

        print(Fore.WHITE+"===============================================")

        print(Fore.GREEN+"\nAll operation completed...")
        print(Fore.WHITE+"\n")

    except Exception as error:
        print(Fore.RED+str(error))