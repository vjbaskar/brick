#!/usr/bin/env python3
import yaml  # Read yaml files
# import pandas
import os  # OS related operations
import functools  # Use reduce function. May not be useful
import re  # regex
import datetime
import subprocess
import argparse

# Main inputs
CONFIG_FILE = "conf/programs.yaml"
COMMANDS_DIR = "_commands"

local_history = ".brick/"
if not os.path.exists(local_history):
        os.makedirs(local_history)

# cli inputs
#COMMAND_NAME = "hw"

# COMMAND_NAME = args.program
#print("Your command is " + COMMAND_NAME)


def read_config_yaml(CONFIG_FILE):
    """
    Reading config file
    """
    commands = []
    with open(CONFIG_FILE) as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
        for each_command in conf:
            for k, v in each_command.items():
                # print(k, "->", v)
                pass
            commands.append(Command(each_command))  # An array of objects of class Command
    return (commands)

def helpPlease(commands):
    """
    A constructor for help function for the package
    :param commands: A list of <commands> object. See class Command for details
    :return: argparse object
    """
    commands_help = []
    parser = argparse.ArgumentParser(description="brick")
    parser.add_argument("--mode", help="Four modes: shell, print, slurm",
                        action="store", required=True)
    subparsers = parser.add_subparsers(title='Available commands',
                                       description='You can provide any command next to brick',
                                       help='-----List of commands------', dest='commandName')
    for single_command in commands:
        temp = subparsers.add_parser(name=single_command.name, help=single_command.helptext)
        for i in single_command.single_entry():
            temp.add_argument("--" + i, help="(Var) " + single_command.user_help(i), action="store", required=True)
        commands_help.append(temp)
        for i in single_command.multi_entry():
            temp.add_argument("--" + i, help="(File) " + single_command.user_help(i), action="store", required=True)
        commands_help.append(temp)
    return (parser)

def get_command(commands, COMMAND_NAME):
    """
    Get the command details from command name
    :param commands: A list of <commands> object. See class Command for details
    :param COMMAND_NAME: (string) name of the command
    :return: (<Command Obj>) command details for a given command name
    """
    all_command_names = [i.name for i in commands]
    command_filtered = []
    command_data = ""
    if not COMMAND_NAME in all_command_names:
        print("Command not present")
        # print_command_list(commands)
        # exit(1)
    else:
        command_filtered = []  # relevant command is being filtered
        for i in range(len(commands)):
            # print(i)
            if COMMAND_NAME == commands[i].name:
                # print("Found command")
                command_filtered.append(commands[i].name)
                command_data = commands[i]
    # If the interested COMMAND_NAME matches more than once
    # then there is something wrong with the config yaml file
    if len(command_filtered) > 1:
        print("There is more than one command with the same name")
        print("Please keep them unique")
        print(f"You can change them in {CONFIG_FILE}")
        exit(1)
    return command_data



# Command class

class Command:
    """
    core command class
    contains information of a given command tool
    """

    def __init__(self, each_command):
        self.name = each_command["name"]
        self.exec = each_command["exec"]
        self.helptext = each_command["help"]
        self.vars = each_command["vars"]
        self.command_list = []

    def user_help(self, var):
        return (self.vars[var])

    def gettime(none):  # Get time in a file creation friendly way
        t = datetime.datetime.now().strftime("%Y-%m-%d-%H_%M_%s")
        return (t)

    def single_entry(self):
        e = self.exec
        pattern = r'(%[a-z]*[A-Z]*%)'
        vars = re.findall(pattern, e)
        vars = [i.strip("%") for i in vars]
        return (vars)

    def multi_entry(self):
        e = self.exec
        pattern = r'({[a-z]*[A-Z]*})'
        vars = re.findall(pattern, e)
        vars = [i.strip("\{").strip("\}") for i in vars]
        return (vars)

    def get_vars(self):
        """
        Get the vars for the commands.
        There can be two types of vars.
        1. single entry input. eg. %name%
        2. multiple entry inpu. eg. {all_fastq_files}
        """
        singles = self.single_entry()
        multi = self.multi_entry()
        return (multi)


    def create_command_file(self):
        """
        Creates a sh file for each command
        """
        if not os.path.exists(COMMANDS_DIR):
            os.mkdir(COMMANDS_DIR)
        t = self.gettime()
        exec_file = COMMANDS_DIR + "/" + self.name + "." + t + ".sh"
        with open(exec_file, "w") as f:
            f.write('#!/usr/bin/env bash' + "\n")
            f.write('set -euo pipefail' + "\n")
            f.write(self.exec + "\n")
        os.chmod(exec_file, 0o755)
        self.exec_file = exec_file
        return (exec_file)

    def create_command(self, cl_args):
        command_list = []
        command_to_single = self.exec
        single_entries = self.single_entry()
        multi_entries = self.multi_entry()

        for i in single_entries:
            word_to_replace = "%" + i + "%"
            #print(f"{i} == {word_to_replace} == {cl_args[i]}")
            command_to_single = command_to_single.replace(word_to_replace, cl_args[i])
        command_from_single = command_to_single
        for i in multi_entries:
            word_to_replace = "{" + i + "}"
            with open(cl_args[i], "r") as f:
                for line in f:
                    command_to_exec = command_from_single
                    #print(command_to_exec)
                    line = line.strip()
                    #print(line)
                    command_to_exec = command_to_exec.replace(word_to_replace, line)
                    command_list.append(command_to_exec)
                    self.command_list = command_list
        # If there are no multi entries then make single command as a list
        if len(multi_entries) == 0:
            #print("*****@*@*@*")
            #print(command_from_single)
            self.command_list = [command_from_single]
            command_list = [command_from_single]
        return(command_list)

    # Command modes
    def shell(self):
        """
        Runs the sh file created by create_command_file function
        """
        f = open(local_history + "/cmds", mode = "+a")
        outpt = []
        #cli_parse = self.create_command(cl_args)
        #print(cli_parse)
        for cmd in self.command_list:
            cmd = ["bash", "-o", "pipefail", "-c"] + [cmd]
            time_of_cmd = self.gettime()
            t = subprocess.run(cmd, stderr = True)
            print(f"{time_of_cmd}:\t{cmd}\t{t}", file = f)
            outpt.append(t)
        f.close()
        return (outpt)

    def print_command(self):
        print("Hello")
        print("Here we print command")

    def slurm_command(self):
        print("Here we run command using slurm")

    def runner(mode):
        print(f"***{mode}")
        mode_run = {
            "print": self.print_command,
            "shell": self.shell,
            "slurm": self.slurm_command
        }
        return mode_run.get(mode, "get help!")


# Read config file and add in all commands into Command object list
commands = read_config_yaml(CONFIG_FILE)
# Create cli help
parser = helpPlease(commands)
# Get args list
args = parser.parse_args()
#args = parser.parse_args("hw --name Vijay --num test/numbers.txt".split())
# Convert arg list as dictionary
cl_args = vars(args)
#print(cl_args)

if cl_args['commandName'] == None:
    parser.print_help()
    exit(0)

COMMAND_NAME = args.commandName
command_data = get_command(commands, COMMAND_NAME)
# Delete the command name from the args list.
del cl_args['commandName']
# Send the args so that we can create a shell executable command list
cli_parse = command_data.create_command(cl_args)
#command_data.shell(cl_args)

print("hello")
def runner(mode, command_data):
    print(f"***{mode}")
    mode_run = {
        "print": command_data.print_command,
        "shell": command_data.shell,
        "slurm": command_data.slurm_command
    }
    return mode_run.get(mode, "get help!")

#print(cl_args["mode"])
#runner(cl_args["mode"], command_data)()




#print(cl_args['mode'])
# temp = mode_run[cl_args["mode"]]
# temp
#if cl_args['slurm'] == True:
#    print("We have to run this in slurm")

# exit(0)


