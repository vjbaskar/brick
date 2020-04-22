#!/usr/bin/env python3
import argparse
import Command
import argparse


CONFIG_FILE="conf/programs.yaml"
commands = Command.read_config_yaml(CONFIG_FILE)
print("--"+commands[0].name)


parser = argparse.ArgumentParser("Brick commands")
subparsers = parser.add_subparsers(help = "Progs")


sparsers = []
sp = subparsers.add_parser(commands[0].name, help= "command1")
sparsers.append(sp)

args = parser.parse_args()


