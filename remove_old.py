import os
import time
import shutil

def deleteOldFolders(path, diff_in_seconds):
    now = time.time()
    old = now - diff_in_seconds #5184000 -> 60 days

    for root, dirs, files, in os.walk(path, topdown=False):
        for _dir in dirs:
            if os.path.getmtime(os.path.join(root,_dir)) < old:
                fpath = os.path.join(root,_dir)
                shutil.rmtree(fpath)

def deleteOldFile(path, diff_in_seconds):
    now = time.time()
    old = now - diff_in_seconds #5184000 -> 60 days

    for root, dirs, files, in os.walk(path, topdown=False):
        for _file in files:
            if os.path.getmtime(os.path.join(root,_file)) < old and _file!='.gitkeep':
                fpath = os.path.join(root,_file)
                os.remove(fpath)