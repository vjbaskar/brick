import yaml
#import pandas
import os
import functools


# Main inputs
CONFIG_FILE="conf/programs.yaml"
COMMANDS_DIR="_commands"

#cli inputs
COMMAND_NAME="test"

# Command class

class Command:
    
    def __init__(self, each_command):
        self.name=each_command["name"]
        self.exec=each_command["exec"]

    
    def gettime():
        t = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%s")
        return(t)

    def create_command_file(self):
        if not os.path.exists(COMMANDS_DIR):
            os.mkdir(COMMANDS_DIR)
        t = gettime()
        exec_file = COMMANDS_DIR + "/" + self.name + "." + t + ".sh"
        with open(exec_file,"w") as f:
            f.write('#!/usr/bin/env bash'+"\n")
            f.write('set -euo pipefail'+"\n")
            f.write(self.exec+"\n")
        os.chmod(exec_file, 0o755)
        self.exec_file = exec_file
        return(exec_file)

    def shell(self):
        outpt = subprocess.run(["bash",self.exec_file])
        return(outpt)





# Print list of commands present
def print_command_list(commands):
    pass

def command_exec(command_data_exec):
    """
    Given an object of class Command
    this will exec this on linux shell
    Uses subprocess.run
    """
    exec_list = [i.strip().split() for i in command_data_exec.split('"')]
    command_array =  functools.reduce(lambda x,y: x+y, temp)
    return(command_array)

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

"""
Check if COMMAND_NAME is present in the command list.
"""

all_command_names = [ i.name for i in commands ]
if not COMMAND_NAME in all_command_names:
    print("Command not present")
    print_command_list(commands)
    #exit(1)
else:
    command_filtered=[]
    for i in range(len(commands)):
        print(i)
        if COMMAND_NAME == commands[i].name:
            print("Found command")
            command_filtered.append(commands[i].name)
            command_data = commands[i]

if len(command_filtered) > 1:
    print("There is more than one command with the same name")
    print("Please keep them unique")
    print(f"You can change them in {CONFIG_FILE}")
    #exit(0)
# command_exec(command_data.exec)
command_data.create_command_file()

