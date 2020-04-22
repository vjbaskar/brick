#!/usr/bin/env python3
##################
"""
Example input config file
-   name: "hw"
    exec: echo "Hello world %name% {num}"
    help: "Just prints hello world"
    vars:
        name: "Your name"
        num: "File of numbers"



"""
##################


import yaml
import os # OS related operations
import re # regex
import datetime
import subprocess

class Command:
    """
    core command class
    contains information of a given command tool
    """
    def __init__(self, each_command):
        self.name=each_command["name"]
        self.exec=each_command["exec"]

    
    def gettime(none): # Get time in a file creation friendly way
        t = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%s")
        return(t)

    def create_command_file(self): 
        """
        Creates a sh file for each command
        """
        if not os.path.exists(COMMANDS_DIR):
            os.mkdir(COMMANDS_DIR)
        t = self.gettime()
        exec_file = COMMANDS_DIR + "/" + self.name + "." + t + ".sh"
        with open(exec_file,"w") as f:
            f.write('#!/usr/bin/env bash'+"\n")
            f.write('set -euo pipefail'+"\n")
            f.write(self.exec+"\n")
        os.chmod(exec_file, 0o755)
        self.exec_file = exec_file
        return(exec_file)

    def shell(self):
        """
        Runs the sh file created by create_command_file function
        """
        outpt = subprocess.run(["bash",self.exec_file])
        return(outpt)


    def single_var(self):
        e = self.exec
        pattern = r'(%[a-z]*[A-Z]*%)'
        vars = re.findall(pattern,e)
        vars = [i.strip("%") for i in vars]
        return(vars)

    def multi_var(self):
        e = self.exec
        pattern = r'(\{[a-z]*[A-Z]*\})'
        vars = re.findall(pattern,e)
        vars = [i.strip("{").strip("}") for i in vars]
        return(vars)


    def get_vars(self):
        """
        Get the vars for the commands.
        There can be two types of vars.
        1. single entry input. eg. %name%
        2. multiple entry inpu. eg. {all_fastq_files}
        """
        singles = self.single_entry(self)
        return(singles)

def read_config_yaml(CONFIG_FILE):
    """
    Reading config file
    """
    commands=[]
    with open(CONFIG_FILE) as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
        for each_command in conf:
            for k,v in each_command.items():
                #print(k, "->", v)
                pass
            commands.append(Command(each_command)) # An array of objects of class Command
    return(commands)


if __name__ == "__main__":
    print("This is a function")
    CONFIG_FILE = "conf/programs.yaml"
    commands = read_config_yaml(CONFIG_FILE)
    command_data = commands[0]
