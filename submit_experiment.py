#!/usr/bin/python
__author__ = 'qiuqiyuan'
import os
import sys
from subprocess import call
import shutil

dir_list = ["scripts"]
usage = '''
submit_experiment.py
    create: create folders
    clean: delete all files in folders
    slurm input_filename: create submit script with input_filename
'''


def create_folder(folder_name):
    os.mkdir(folder_name)


def remove_folder(folder_name):
    os.rmdir(folder_name)


def create_new_script(file_path, mem_per_core, script, script_args):
    f = open(file_path, "w")
    f.write("#!/bin/bash\n" + \
            "#SBATCH -J para_step4\n" + \
            "#SBATCH -t " + "5-00:00:00" + "\n" + \
            "#SBATCH --mem-per-cpu=" + mem_per_core + "\n" + \
            "#SBATCH -n  1 \n" + \
            "#SBATCH -p standard\n" + \
            "#SBATCH -o out_slurm_abyss_p_%j\n" + \
            "#SBATCH -e out_slurm_abyss_p_%j\n" + \
            "#SBATCH --mail-type fail\n" + \
            "#SBATCH --mail-type begin\n" + \
            "#SBATCH --mail-type end\n" + \
            "#SBATCH --mail-user qiuqiyuan@gmail.com\n")

    f.write("cd ..\n")
    f.write("python " + script +" "+script_args + "\n")
    f.close()


def main():
    if len(sys.argv) < 2:
        print usage
        return

    if sys.argv[1] == "create":
        for dir_name in dir_list:
            if not os.path.exists(dir_name):
                print "Folder " + dir_name + " does not exist. " + "Create."
                create_folder(dir_name)
            else:
                print "folder " + dir_name + " already exists"
        exit(1)

    elif sys.argv[1] == "clean":
        for dir_name in dir_list:
            files = os.listdir(dir_name)
            ##remove all files in the directory
            for f in files:
                path = os.path.join(os.getcwd(), dir_name, f)
                os.remove(path)
                print path + " removed"
        exit(1)

    elif sys.argv[1] == "slurm":
        assert (len(sys.argv) >= 3)
        infiles = sys.argv[2:]
        script = "./step4.py"
        for dir_name in dir_list:
            for infile in infiles:
                file_path = os.path.join(os.getcwd(), dir_name, infile+".sh")
                print "file_path", file_path
                # print "new_script name: " + dir_path
                create_new_script(file_path, "2GB", script, infile)
                print file_path + " created"
        exit(0)

    elif sys.argv[1] == "submit":
        owd = os.getcwd()
        for dir_name in dir_list:
            dir_path = os.path.join(owd, dir_name)
            print dir_path
            os.chdir(dir_path)
            print "submit task"
            os.system("sbatch *.sh")
            os.chdir(owd)
        exit(1)


if __name__ == "__main__":
    main()
