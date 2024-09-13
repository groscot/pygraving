import pyparsing

# Argument parsable into a python string, int, float or bool
# for each one, includes the casting function in the parse action
#* place string last, because of the order of matching evaluation

python_int = pyparsing.Combine(pyparsing.Optional("-") + pyparsing.Word(pyparsing.nums))
python_float = pyparsing.Combine(pyparsing.Optional("-") + pyparsing.Word(pyparsing.nums) + "." + pyparsing.Word(pyparsing.nums))
python_bool = pyparsing.Keyword("True") | pyparsing.Keyword("False")
python_list = pyparsing.Literal("[").suppress() + pyparsing.delimitedList(python_float | python_int | python_bool) + pyparsing.Literal("]").suppress()
python_string = pyparsing.Word(pyparsing.alphanums + "_")

python_bool.setParseAction(lambda t: t[0] == "True")
python_int.setParseAction(pyparsing.tokenMap(int))
python_float.setParseAction(pyparsing.tokenMap(float))

python_number = python_float | python_int
python_arg = python_float | python_int | python_bool | python_list | python_string

param_with_int_value = pyparsing.Word(pyparsing.alphas + "_")("param") + python_int("value")
param_with_numeric_value = pyparsing.Word(pyparsing.alphas + "_")("param") + (python_float | python_int)("value")
param_with_python_value = pyparsing.Word(pyparsing.alphas + "_")("param") + python_arg("value")