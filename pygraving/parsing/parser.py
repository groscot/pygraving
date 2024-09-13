# Reference guide
# https://github.com/pyparsing/pyparsing/wiki/Common-Pitfalls-When-Writing-Parsers

"""
! WARNING !
With pyparsing==2.4.7, the methods and attributes should be in camelCase, NOT IN snake_case
"""

import pyparsing

from .primitives import *

string_name_note = pyparsing.Combine((pyparsing.Literal("do") | pyparsing.Literal("re") | pyparsing.Literal("mi") | \
    pyparsing.Literal("fa") | pyparsing.Literal("sol") | pyparsing.Literal("la") | \
        pyparsing.Literal("si")) + pyparsing.Optional(pyparsing.OneOrMore("+")) + pyparsing.Optional(pyparsing.OneOrMore("-")))




#---

#i) Simple way to allow the parser to start C from 1 instead of 0
#i) without changing the internal representations
degree_int = pyparsing.Combine(pyparsing.Optional("-") + pyparsing.Word(pyparsing.nums))
degree_int.setParseAction(lambda t: int(t[0])-1)

#---




flipped = pyparsing.Optional("!")("flipped")

inner_voice_track = pyparsing.Combine(pyparsing.Optional("-") + pyparsing.Word(pyparsing.pyparsing_unicode.Latin1.alphas + ",?! '\""))("word")

voice_track = pyparsing.Optional(
    pyparsing.Literal("[").suppress() + pyparsing.delimitedList(inner_voice_track, delim="|")("tracks") + pyparsing.Literal("]").suppress()
)

fingering_string = pyparsing.Optional(
    pyparsing.Literal("((").suppress() + pyparsing.Word(pyparsing.nums)("number") + pyparsing.Literal("))").suppress()
)
fingering_finger = pyparsing.Optional(
    pyparsing.Literal("(").suppress() + pyparsing.Word(pyparsing.nums)("number") + pyparsing.Literal(")").suppress()
)

newvoicetrack = pyparsing.QuotedString(quote_char='"')
newvoicetrack.setParseAction(lambda t: t[0].strip())
newvoice = pyparsing.Optional(pyparsing.OneOrMore(newvoicetrack))("voice")


alteration = pyparsing.Optional(pyparsing.Or(["#", "b", "n"]))
note = pyparsing.Group(
    alteration("alteration") + (degree_int("degree") | string_name_note("degree")) + \
        pyparsing.Optional(".")("dotted") + flipped + newvoice("voice") + \
        fingering_string("fingering_string") + fingering_finger("fingering_finger")
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

_SELECT = pyparsing.Keyword("SELECT")
_TRANSLATE = pyparsing.Keyword("TRANSLATE")

stop_on = _BEGIN | _SET | _MOVE | _END | _CONFIG | _SELECT | _TRANSLATE

select = _SELECT("command") + pyparsing.QuotedString(quote_char="'")("object")
translate = _TRANSLATE("command") + python_number("x") + python_number("y")

bar = pyparsing.Literal("||:") | pyparsing.Literal(":||") | pyparsing.Literal("||") | \
    pyparsing.Literal("[|:") | pyparsing.Literal(":|]") | pyparsing.Literal("[|") | pyparsing.Literal("|]") | \
    pyparsing.Literal("|:") | pyparsing.Literal(":|") | pyparsing.Literal("|")

commands = [
    _BEGIN("command") + pyparsing.Word(pyparsing.alphas)("object"),
    _SET("command") + param_with_int_value,
    _CONFIG("config") + param_with_numeric_value,
    _MOVE("command") + pyparsing.Or([python_float, python_int])("amount") + pyparsing.Word(pyparsing.alphas)("direction"),
    _END("command") + pyparsing.Word(pyparsing.alphas)("object"),
    select,
    translate,
    bar("bar"),
    chord("chord"),
    beam("beam"),
    note("note"),
    silence("silence"),
    signature("signature"),
    pyparsing.Keyword("PLACE")("command") + pyparsing.Word(pyparsing.alphas)("object") + \
        pyparsing.OneOrMore(param_with_python_value, stopOn=stop_on)("arguments"),
]