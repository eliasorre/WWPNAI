import sys
import re
from collections import Counter

opcode_names = {
    0: "CACHE",
    1: "POP_TOP",
    2: "PUSH_NULL",
    3: "BINARY_OP_ADAPTIVE",
    4: "BINARY_OP_ADD_FLOAT",
    5: "BINARY_OP_ADD_INT",
    6: "BINARY_OP_ADD_UNICODE",
    7: "BINARY_OP_INPLACE_ADD_UNICODE",
    8: "BINARY_OP_MULTIPLY_FLOAT",
    9: "NOP",
    10: "UNARY_POSITIVE",
    11: "UNARY_NEGATIVE",
    12: "UNARY_NOT",
    13: "BINARY_OP_MULTIPLY_INT",
    14: "BINARY_OP_SUBTRACT_FLOAT",
    15: "UNARY_INVERT",
    16: "BINARY_OP_SUBTRACT_INT",
    17: "BINARY_SUBSCR_ADAPTIVE",
    18: "BINARY_SUBSCR_DICT",
    19: "BINARY_SUBSCR_GETITEM",
    20: "BINARY_SUBSCR_LIST_INT",
    21: "BINARY_SUBSCR_TUPLE_INT",
    22: "CALL_ADAPTIVE",
    23: "CALL_PY_EXACT_ARGS",
    24: "CALL_PY_WITH_DEFAULTS",
    25: "BINARY_SUBSCR",
    26: "COMPARE_OP_ADAPTIVE",
    27: "COMPARE_OP_FLOAT_JUMP",
    28: "COMPARE_OP_INT_JUMP",
    29: "COMPARE_OP_STR_JUMP",
    30: "GET_LEN",
    31: "MATCH_MAPPING",
    32: "MATCH_SEQUENCE",
    33: "MATCH_KEYS",
    34: "EXTENDED_ARG_QUICK",
    35: "PUSH_EXC_INFO",
    36: "CHECK_EXC_MATCH",
    37: "CHECK_EG_MATCH",
    38: "JUMP_BACKWARD_QUICK",
    39: "LOAD_ATTR_ADAPTIVE",
    40: "LOAD_ATTR_INSTANCE_VALUE",
    41: "LOAD_ATTR_MODULE",
    42: "LOAD_ATTR_SLOT",
    43: "LOAD_ATTR_WITH_HINT",
    44: "LOAD_CONST__LOAD_FAST",
    45: "LOAD_FAST__LOAD_CONST",
    46: "LOAD_FAST__LOAD_FAST",
    47: "LOAD_GLOBAL_ADAPTIVE",
    48: "LOAD_GLOBAL_BUILTIN",
    49: "WITH_EXCEPT_START",
    50: "GET_AITER",
    51: "GET_ANEXT",
    52: "BEFORE_ASYNC_WITH",
    53: "BEFORE_WITH",
    54: "END_ASYNC_FOR",
    55: "LOAD_GLOBAL_MODULE",
    56: "LOAD_METHOD_ADAPTIVE",
    57: "LOAD_METHOD_CLASS",
    58: "LOAD_METHOD_MODULE",
    59: "LOAD_METHOD_NO_DICT",
    60: "STORE_SUBSCR",
    61: "DELETE_SUBSCR",
    62: "LOAD_METHOD_WITH_DICT",
    63: "LOAD_METHOD_WITH_VALUES",
    64: "PRECALL_ADAPTIVE",
    65: "PRECALL_BOUND_METHOD",
    66: "PRECALL_BUILTIN_CLASS",
    67: "PRECALL_BUILTIN_FAST_WITH_KEYWORDS",
    68: "GET_ITER",
    69: "GET_YIELD_FROM_ITER",
    70: "PRINT_EXPR",
    71: "LOAD_BUILD_CLASS",
    72: "PRECALL_METHOD_DESCRIPTOR_FAST_WITH_KEYWORDS",
    73: "PRECALL_NO_KW_BUILTIN_FAST",
    74: "LOAD_ASSERTION_ERROR",
    75: "RETURN_GENERATOR",
    76: "PRECALL_NO_KW_BUILTIN_O",
    77: "PRECALL_NO_KW_ISINSTANCE",
    78: "PRECALL_NO_KW_LEN",
    79: "PRECALL_NO_KW_LIST_APPEND",
    80: "PRECALL_NO_KW_METHOD_DESCRIPTOR_FAST",
    81: "PRECALL_NO_KW_METHOD_DESCRIPTOR_NOARGS",
    82: "LIST_TO_TUPLE",
    83: "RETURN_VALUE",
    84: "IMPORT_STAR",
    85: "SETUP_ANNOTATIONS",
    86: "YIELD_VALUE",
    87: "ASYNC_GEN_WRAP",
    88: "PREP_RERAISE_STAR",
    89: "POP_EXCEPT",
    90: "HAVE_ARGUMENT",
    91: "DELETE_NAME",
    92: "UNPACK_SEQUENCE",
    93: "FOR_ITER",
    94: "UNPACK_EX",
    95: "STORE_ATTR",
    96: "DELETE_ATTR",
    97: "STORE_GLOBAL",
    98: "DELETE_GLOBAL",
    99: "SWAP",
    100: "LOAD_CONST",
    101: "LOAD_NAME",
    102: "BUILD_TUPLE",
    103: "BUILD_LIST",
    104: "BUILD_SET",
    105: "BUILD_MAP",
    106: "LOAD_ATTR",
    107: "COMPARE_OP",
    108: "IMPORT_NAME",
    109: "IMPORT_FROM",
    110: "JUMP_FORWARD",
    111: "JUMP_IF_FALSE_OR_POP",
    112: "JUMP_IF_TRUE_OR_POP",
    113: "PRECALL_NO_KW_METHOD_DESCRIPTOR_O",
    114: "POP_JUMP_FORWARD_IF_FALSE",
    115: "POP_JUMP_FORWARD_IF_TRUE",
    116: "LOAD_GLOBAL",
    117: "IS_OP",
    118: "CONTAINS_OP",
    119: "RERAISE",
    120: "COPY",
    121: "PRECALL_NO_KW_STR_1",
    122: "BINARY_OP",
    123: "SEND",
    124: "LOAD_FAST",
    125: "STORE_FAST",
    126: "DELETE_FAST",
    127: "POP_JUMP_FORWARD_IF_NOT_NONE",
    128: "POP_JUMP_FORWARD_IF_NONE",
    129: "RAISE_VARARGS",
    130: "GET_AWAITABLE",
    131: "MAKE_FUNCTION",
    132: "BUILD_SLICE",
    133: "JUMP_BACKWARD_NO_INTERRUPT",
    134: "MAKE_CELL",
    135: "LOAD_CLOSURE",
    136: "LOAD_DEREF",
    137: "STORE_DEREF",
    138: "DELETE_DEREF",
    139: "JUMP_BACKWARD",
    140: "CALL_FUNCTION_EX",
    141: "EXTENDED_ARG",
    142: "LIST_APPEND",
    143: "SET_ADD",
    144: "MAP_ADD",
    145: "LOAD_CLASSDEREF",
    146: "COPY_FREE_VARS",
    147: "RESUME",
    148: "MATCH_CLASS",
    149: "FORMAT_VALUE",
    150: "BUILD_CONST_KEY_MAP",
    151: "BUILD_STRING",
    152: "LOAD_METHOD",
    153: "LIST_EXTEND",
    154: "SET_UPDATE",
    155: "DICT_MERGE",
    156: "DICT_UPDATE",
    157: "PRECALL",
    158: "CALL",
    159: "KW_NAMES",
    160: "POP_JUMP_BACKWARD_IF_NOT_NONE",
    161: "POP_JUMP_BACKWARD_IF_NONE",
    162: "POP_JUMP_BACKWARD_IF_FALSE",
    163: "POP_JUMP_BACKWARD_IF_TRUE",
    164: "STORE_ATTR_ADAPTIVE",
    165: "STORE_ATTR_INSTANCE_VALUE",
    166: "STORE_ATTR_SLOT",
    167: "STORE_ATTR_WITH_HINT",
    168: "STORE_FAST__LOAD_FAST",
    169: "STORE_FAST__STORE_FAST",
    170: "STORE_SUBSCR_ADAPTIVE",
    171: "STORE_SUBSCR_DICT",
    172: "STORE_SUBSCR_LIST_INT",
    173: "UNPACK_SEQUENCE_ADAPTIVE",
    174: "UNPACK_SEQUENCE_LIST",
    175: "UNPACK_SEQUENCE_TUPLE",
    176: "UNPACK_SEQUENCE_TWO_TUPLE",
    177: "DO_TRACING"
}

def extract_opcodes(filename, top_x):
    # Read the file
    with open(filename, 'r') as file:
        content = file.read()

    # Extract the BYTECODE HDBT ENTRIES section
    pattern = re.compile(r'BYTECODE HDBT ENTRIES:(.*?)\n\n', re.DOTALL)
    match = pattern.search(content)
    if not match:
        print("BYTECODE HDBT ENTRIES section not found.")
        return

    section = match.group(1)

    # Find all opcode hits
    opcode_pattern = re.compile(r'\[(\d+)\] hits: (\d+),')
    opcodes = opcode_pattern.findall(section)

    # Create a Counter for opcode hits
    opcode_counter = Counter()
    total_hits = 0
    for opcode, hits in opcodes:
        hits = int(hits)
        opcode_counter[int(opcode)] += hits
        total_hits += hits

    # Get the most common opcodes
    most_common_opcodes = opcode_counter.most_common(top_x)

    # Print the results with opcode names and percentages
    for opcode, hits in most_common_opcodes:
        opcode_name = opcode_names.get(opcode, "UNKNOWN OPCODE")
        percentage = (hits / total_hits) * 100
        print(f'Opcode [{opcode}] ({opcode_name}) hits: {hits} ({percentage:.2f}%)')
        print(f'&{opcode_name} & {percentage:.2f}\% \\')


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python script.py <filename> <top_x>")
    else:
        filename = sys.argv[1]
        top_x = int(sys.argv[2])
        extract_opcodes(filename, top_x)
