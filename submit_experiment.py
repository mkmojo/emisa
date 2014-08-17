#!/usr/bin/python
__author__ = 'qiuqiyuan'
import os
import sys
from subprocess import call
import shutil


def CreateFolder(folder_name):
    os.mkdir(folder_name)


def RemoveFolder(folder_name):
    os.rmdir(folder_name)


def CreateNewScript(dir_name, dir_path, abyss_path, mem_per_core, k, name, in_file):
    list = dir_name.split("_")
    np = list[0]
    #nm == number of machens
    nm = list[1]
    f = open(dir_path, "w")
    f.write("#!/bin/bash\n" + \
            "#SBATCH -J " + dir_name + "\n" + \
            "#SBATCH -t " + "5-00:00:00" + "\n" + \
            "#SBATCH --mem-per-cpu=" + mem_per_core + "\n" + \
            "#SBATCH -n " + np + "\n" + \
            "#SBATCH -p standard\n" + \
            "#SBATCH -o out_slurm_abyss_p_%j\n" + \
            "#SBATCH -e out_slurm_abyss_p_%j\n" + \
            "#SBATCH --mail-type fail\n" + \
            "#SBATCH --mail-type begin\n" + \
            "#SBATCH --mail-type end\n" + \
            "#SBATCH --mail-user qiuqiyuan@gmail.com\n")

    if (int(np) / int(nm) <= 24):
        f.write("#SBATCH --ntasks-per-node=" + str(int(np) / int(nm)) + "\n")
    else:
        f.write("#SBATCH --ntasks-per-node=24\n")

    f.write(abyss_path + " np=" + np + " k=" + k + " name=" + \
            "test_" + dir_name + " in='" + in_file + "'" + "\n")
    f.close()

#dir_list = ["1_1", "2_1", "4_1", "8_1", "12_1", "16_1", "24_1","24_6", "48_2", "64_3", "120_5"]
dir_list = ["1_1", "2_1", "4_1", "8_1"]
usage = '''
submit_experiment.py
    create: create folders
    clean: delete all files in folders
    slurm abyss-pe_path mem_per_core k name in_file
'''


def main():
    if (len(sys.argv) < 2):
        print usage
        return
    if (sys.argv[1] == "create"):
        for dir_name in dir_list:
            if not os.path.exists(dir_name):
                print "file " + dir_name + " does not exist. " + "ready to create"
                CreateFolder(dir_name)
            else:
                print "folder " + dir_name + " already exists"
        exit(1)
    elif (sys.argv[1] == "clean"):
        for dir_name in dir_list:
            files = os.listdir(dir_name)
            ##remove all files in the directory
            for f in files:
                path = os.path.join(os.getcwd(), dir_name, f)
                os.remove(path)
                print path + " removed"
        exit(1)
    elif (sys.argv[1] == "slurm"):
        assert (len(sys.argv) == 7)
        for dir_name in dir_list:
            dir_path = os.path.join(os.getcwd(), dir_name, "run.bash")
            # print "new_script name: " + dir_path
            abyss_path = sys.argv[2]
            mem_per_core = sys.argv[3]
            k = sys.argv[4]
            name = sys.argv[5]
            in_file = sys.argv[6]
            CreateNewScript(dir_name, dir_path, abyss_path, mem_per_core, k, name, in_file)
            print dir_path + " created"
        exit(1)
    elif (sys.argv[1] == "submit"):
        owd = os.getcwd()
        for dir_name in dir_list:
            dir_path = os.path.join(owd, dir_name)
            print dir_path
            os.chdir(dir_path)
            print "submit task"
            os.system("sbatch run.bash")
            os.chdir(owd)
        exit(1)


if __name__ == "__main__":
    main()
