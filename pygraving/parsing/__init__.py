import pyparsing

from .parser import commands


def make(commands):
    command = commands.pop(0)
    for c in commands:
        command = command | c
    phrase = pyparsing.OneOrMore(pyparsing.Group(command)).ignore(pyparsing.cStyleComment)
    return phrase

phrase = make(commands)

def parse_input(text: str) -> pyparsing.ParseResults:
    return phrase.parseString(text)