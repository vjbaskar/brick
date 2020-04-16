#!/usr/bin/env python3
import yaml # Read yaml files
#import pandas
import os # OS related operations
import functools # Use reduce function. May not be useful
import re # regex

# Main inputs
CONFIG_FILE="conf/programs.yaml"
COMMANDS_DIR="_commands"

#cli inputs
COMMAND_NAME="hw"

# Command class

class Command:
    """
    core command class
    contains information of a given command tool
    """
    def __init__(self, each_command):
        self.name=each_command["name"]
        self.exec=each_command["exec"]

    
    def gettime(): # Get time in a file creation friendly way
        t = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%s")
        return(t)

    def create_command_file(self): 
        """
        Creates a sh file for each command
        """
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
        """
        Runs the sh file created by create_command_file function
        """
        outpt = subprocess.run(["bash",self.exec_file])
        return(outpt)


    def single_entry(self):
        #e = self.exec
        pattern = r'(%[a-z]*[A-Z]*%)'
        vars = re.findall(pattern,e)
        vars = [i.strip("%") for i in vars]
        return(vars)


    def get_vars(self):
        """
        Get the vars for the commands.
        There can be two types of vars.
        1. single entry input. eg. %name%
        2. multiple entry inpu. eg. {all_fastq_files}
        """
        singles = single_entry()
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

commands = read_config_yaml(CONFIG_FILE)

"""
Check if COMMAND_NAME is present in the command list.
"""
# Get command names in a list
all_command_names = [ i.name for i in commands ]

if not COMMAND_NAME in all_command_names:
    print("Command not present")
    print_command_list(commands)
    #exit(1)
else:
    command_filtered=[] # relevant command is being filtered
    for i in range(len(commands)):
        print(i)
        if COMMAND_NAME == commands[i].name:
            print("Found command")
            command_filtered.append(commands[i].name)
            command_data = commands[i]

# If the interested COMMAND_NAME matches more than once
# then there is something wrong with the config yaml file
if len(command_filtered) > 1:
    print("There is more than one command with the same name")
    print("Please keep them unique")
    print(f"You can change them in {CONFIG_FILE}")
    #exit(0)

command_data.create_command_file()
command_data.shell()




#### ---- END ----


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



