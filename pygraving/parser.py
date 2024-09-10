# Reference guide
# https://github.com/pyparsing/pyparsing/wiki/Common-Pitfalls-When-Writing-Parsers

"""
! WARNING !
With pyparsing==2.4.7, the methods and attributes should be in camelCase, NOT IN snake_case
"""

import pyparsing

string_name_note = pyparsing.Combine((pyparsing.Literal("do") | pyparsing.Literal("re") | pyparsing.Literal("mi") | \
    pyparsing.Literal("fa") | pyparsing.Literal("sol") | pyparsing.Literal("la") | \
        pyparsing.Literal("si")) + pyparsing.Optional(pyparsing.OneOrMore("+")) + pyparsing.Optional(pyparsing.OneOrMore("-")))

# Argument parsable into a python string, int, float or bool
# for each one, includes the casting function in the parse action
#* place string last, because of the order of matching evaluation

python_int = pyparsing.Combine(pyparsing.Optional("-") + pyparsing.Word(pyparsing.nums))
python_float = pyparsing.Combine(pyparsing.Word(pyparsing.nums) + "." + pyparsing.Word(pyparsing.nums))
python_bool = pyparsing.Keyword("True") | pyparsing.Keyword("False")
python_list = pyparsing.Literal("[").suppress() + pyparsing.delimitedList(python_float | python_int | python_bool) + pyparsing.Literal("]").suppress()
python_string = pyparsing.Word(pyparsing.alphanums + "_")

python_bool.setParseAction(lambda t: t[0] == "True")
python_int.setParseAction(pyparsing.tokenMap(int))
python_float.setParseAction(pyparsing.tokenMap(float))

python_arg = python_float | python_int | python_bool | python_list | python_string


#---

#i) Simple way to allow the parser to start C from 1 instead of 0
#i) without changing the internal representations
degree_int = pyparsing.Combine(pyparsing.Optional("-") + pyparsing.Word(pyparsing.nums))
degree_int.setParseAction(lambda t: int(t[0])-1)

#---


param_with_numeric_value = pyparsing.Word(pyparsing.alphas + "_")("param") + python_int("value")
param_with_python_value = pyparsing.Word(pyparsing.alphas + "_")("param") + python_arg("value")


flipped = pyparsing.Optional("!")("flipped")

inner_voice_track = pyparsing.Combine(pyparsing.Optional("-") + pyparsing.Word(pyparsing.pyparsing_unicode.Latin1.alphas + ",?! '\""))("word")

voice_track = pyparsing.Optional(
    pyparsing.Literal("[").suppress() + pyparsing.delimitedList(inner_voice_track, delim="|")("tracks") + pyparsing.Literal("]").suppress()
)


alteration = pyparsing.Optional(pyparsing.Or(["#", "b", "n"]))
note = pyparsing.Group(
    alteration("alteration") + (degree_int("degree") | string_name_note("degree")) + pyparsing.Optional(".")("dotted") + flipped + voice_track("voice")
)

# chord = pyparsing.nestedExpr(content=note)
chord = pyparsing.Group(
    pyparsing.Literal("(") + pyparsing.OneOrMore(note("note"))("notes") + pyparsing.Literal(")") + flipped
)
beam = pyparsing.Group(
    pyparsing.Literal("[") + pyparsing.OneOrMore(note("note"))("notes") + pyparsing.Literal("]") + flipped
)
silence = pyparsing.Literal("_")

signature_arg = pyparsing.Group(pyparsing.Word(pyparsing.nums)("digit_1") + pyparsing.Word(pyparsing.nums)("digit_2")) | pyparsing.Keyword("C")
signature = pyparsing.Keyword("SIGNATURE")("command") + signature_arg("value")

_BEGIN = pyparsing.Keyword("BEGIN")
_CONFIG = pyparsing.Keyword("CONFIG")
_SET = pyparsing.Keyword("SET")
_MOVE = pyparsing.Keyword("MOVE")
_END = pyparsing.Keyword("END")

stop_on = _BEGIN | _SET | _MOVE | _END

bar = pyparsing.Literal("||:") | pyparsing.Literal(":||") | pyparsing.Literal("||") | \
    pyparsing.Literal("|:") | pyparsing.Literal(":|") | pyparsing.Literal("|")

commands = [
    _BEGIN("command") + pyparsing.Word(pyparsing.alphas)("object"),
    _SET("command") + param_with_numeric_value,
    _CONFIG("config") + param_with_python_value,
    _MOVE("command") + pyparsing.Or([python_float, python_int])("amount") + pyparsing.Word(pyparsing.alphas)("direction"),
    _END("command") + pyparsing.Word(pyparsing.alphas)("object"),
    bar("bar"),
    chord("chord"),
    beam("beam"),
    note("note"),
    silence("silence"),
    signature("signature"),
    pyparsing.Keyword("PLACE")("command") + pyparsing.Word(pyparsing.alphas)("object") + \
        pyparsing.OneOrMore(param_with_python_value, stopOn=stop_on)("arguments"),
]

# combine all commands into a single command
command = commands.pop(0)
for c in commands:
    command = command | c
phrase = pyparsing.OneOrMore(pyparsing.Group(command)).ignore(pyparsing.cStyleComment)

def parse_input(text: str) -> pyparsing.ParseResults:
    return phrase.parseString(text)
