"""
This module contains functions for analyzing a grammar, finding
its NULLABLE, FIRST, FOLLOW and SELECT sets, and determining if it is
LL(1).

A grammar is represented as a list of rules of the form (head, body)
where head is the goal non-terminal, and body is a tuple of symbols,
or the empty tuple () for an epsilon rule.

The start symbol is always the head of the first rule in the list.
"""

from symbols import *


grammar_recitation = [
    (S, (ID, ASSIGN, E)),              # S -> id := E
    (S, (IF, LP, E, RP, S, ELSE, S)),  # S -> if (E) S else S
    (E, (T, EP)),                      # E -> T EP
    (T, (ID,)),                        # T -> id
    (T, (LP, E, RP)),                  # T -> (E)
    (EP, ()),                          # EP -> epsilon
    (EP, (PLUS, E)),                   # EP -> + E
]


def calculate_nullable(terminals, nonterminals, grammar):
    """
    Return the set of nullable nonterminals in the given grammar.

    terminals and nonterminals are sets, grammer is a list of rules as
    explained above.

    --- DO NOT MODIFY THIS FUNCTION ---
    """
    nullable = set()
    for head, body in grammar:
        if body == ():
            nullable.add(head)
    changing = True
    while changing:
        changing = False
        for head, body in grammar:
            if set(body) <= nullable and head not in nullable:
                nullable.add(head)
                changing = True
    return nullable


def calculate_first(terminals, nonterminals, grammar, nullable):
    """
    Return a dictionary mapping terminals and nonterminals to their FIRST set
    """
    first = dict()
    for t in terminals:
        first[t] = {t}
    for a in nonterminals:
        first[a] = set()
    changing = True
    while changing:
        changing = False
        for head, body in grammar: # for each rule
            for i in range(0, len(body)): # for each token
                if is_nullable(body[0:i], nullable):
                    for item in first[body[i]]:  # add First(body[i]) to First[head]
                        if item not in first[head]:
                            first[head].add(item)
                            changing = True
    return first


 
def is_nullable(token_stream, nullables):
    """
    Function checks if token_stream is nullable or not
    """
    for token in token_stream:
        if token not in nullables:
            return False
    return True


def calculate_follow(terminals, nonterminals, grammar, nullable, first):
    """
    Return a dictionary mapping terminals and nonterminals to their FOLLOW set
    """
    follow = dict()
    for a in nonterminals:
        follow[a] = set()
    start_nonterminal = grammar[0][0]
    follow[start_nonterminal] = {EOF}

    changing = True
    while changing:
        changing = False
        for head, body in grammar: # for each rule
            for i in range(0, len(body)):
                if body[i] in terminals:  # Follow is not relevant to terminals
                    continue
                if is_nullable(body[i+1:], nullable):
                    for item in follow[head]:  # add Follow(head) to Follow(body[i])
                        if item not in follow[body[i]]:
                            follow[body[i]].add(item)
                            changing = True

            for i in range(0, len(body) - 1):
                if body[i] in terminals:  # Follow is not relevant to terminals
                    continue
                for j in range(i + 1, len(body)):
                    if is_nullable(body[i+1:j], nullable):
                        for item in first[body[j]]:  # add First(body[j]) to Follow(body[i])
                            if item not in follow[body[i]]:
                                follow[body[i]].add(item)
                                changing = True

    return follow


def calculate_select(terminals, nonterminals, grammar, nullable, first, follow):
    """
    Return a dictionary mapping rules to their SELECT (a.k.a. PREDICT) set
    """
    select = dict()

    for head, body in grammar:
        select[head, body] = set()
        if body:  # check that right side of rule is not epsilon
            for item in body:
                for x in first[item]:  # add first of item to select of (head, body)
                    select[head, body].add(x)
                if not is_nullable((item,), nullable):
                    break

        if is_nullable(body, nullable):
            for x in follow[head]:
                select[head, body].add(x)

    return select


def format_rule(r):
    """
    --- DO NOT MODIFY THIS FUNCTION ---
    """
    return "{} -> {}".format(r[0], ' '.join(r[1]))


def find_terminals_and_nonterminals(grammar):
    """
    Find the terminals and nonterminals appearing in the given grammar.

    --- DO NOT MODIFY THIS FUNCTION ---
    """
    symbols = set()
    nonterminals = set()
    for head, body in grammar:
        nonterminals.add(head)
        symbols.update(body)
    terminals = symbols - nonterminals
    return terminals, nonterminals


def analyze_grammar(grammar):
    """
    Use other functions in this module to analyze the grammar and
    check if it is LL(1).

    --- DO NOT MODIFY THIS FUNCTION ---
    """
    print "Analyzing grammar:"
    for r in grammar:
        print "    " + format_rule(r)
    print

    terminals, nonterminals = find_terminals_and_nonterminals(grammar)
    print "terminals = ", terminals
    print "nonterminals = ", nonterminals
    print

    nullable = calculate_nullable(terminals, nonterminals, grammar)
    print "nullable = ", nullable
    print

    first = calculate_first(terminals, nonterminals, grammar, nullable)
    for k in sorted(first.keys()):
        print "first({}) = {}".format(k, first[k])
    print

    follow = calculate_follow(terminals, nonterminals, grammar, nullable, first)
    for k in sorted(follow.keys()):
        print "follow({}) = {}".format(k, follow[k])
    print

    select = calculate_select(terminals, nonterminals, grammar, nullable, first, follow)
    for k in sorted(select.keys()):
        print "select({}) = {}".format(format_rule(k), select[k])
    print

    ll1 = True
    n = len(grammar)
    for i in range(n):
        for j in range(i+1, n):
            r1 = grammar[i]
            r2 = grammar[j]
            if r1[0] == r2[0] and len(select[r1] & select[r2]) > 0:
                ll1 = False
                print "Grammar is not LL(1), as the following rules have intersecting SELECT sets:"
                print "    " + format_rule(r1)
                print "    " + format_rule(r2)
    if ll1:
        print "Grammar is LL(1)."
    print

def is_LL1(grammar):
    terminals, nonterminals = find_terminals_and_nonterminals(grammar)
    nullable = calculate_nullable(terminals, nonterminals, grammar)
    first = calculate_first(terminals, nonterminals, grammar, nullable)
    follow = calculate_follow(terminals, nonterminals, grammar, nullable, first)
    select = calculate_select(terminals, nonterminals, grammar, nullable, first, follow)
    ll1 = True
    n = len(grammar)
    for i in range(n):
        for j in range(i+1, n):
            r1 = grammar[i]
            r2 = grammar[j]
            if r1[0] == r2[0] and len(select[r1] & select[r2]) > 0:
                ll1 = False
    if ll1:
        return True
    return False


grammar_json_4a = [
    #
    # --- FILL IN HERE IN QUESTION 5.a ---
    #
    (obj, (LB, RB)),                        # obj -> { }
    (obj, (LB, members, RB)),               # obj -> { members }
    (members, (keyvalue,)),                 # members -> keyvalue
    (members, (members, COMMA, members)),   # members -> members , members
    (keyvalue, (STRING, COLON, value)),     # keyvalue -> string : value
    (value, (STRING,)),                     # value -> string
    (value, (INT,)),                        # value -> int
    (value, (obj,)),                        # value -> obj
]

grammar_json_4b = [
    #
    # --- FILL IN HERE IN QUESTION 5.b ---
    #
    (obj, (LB, obj_right)),                 # obj -> { obj_right
    (obj_right, (RB,)),                     # obj_right -> }
    (obj_right, (members, RB)),             # obj_right -> members }
    (members, (keyvalue, members_right)),   # members -> keyvalue members_right
    (members_right, (COMMA, members)),      # members_right -> , members
    (members_right, ()),                    # members_right -> epsilon
    (keyvalue, (STRING, COLON, value)),     # keyvalue -> string : value
    (value, (STRING,)),                     # value -> string
    (value, (INT,)),                        # value -> int
    (value, (obj,)),                        # value -> obj
]

grammar_json_4c = [
    #
    # --- FILL IN HERE IN QUESTION 5.c ---
    #

    # NOTE: this is the same grammar from last question, meaning grammar_json_4c == grammar_json_4b
    (obj, (LB, obj_right)),                 # obj -> { obj_right
    (obj_right, (RB,)),                     # obj_right -> }
    (obj_right, (members, RB)),             # obj_right -> members }
    (members, (keyvalue, members_right)),   # members -> keyvalue members_right
    (members_right, (COMMA, members)),      # members_right -> , members
    (members_right, ()),                    # members_right -> epsilon
    (keyvalue, (STRING, COLON, value)),     # keyvalue -> string : value
    (value, (STRING,)),                     # value -> string
    (value, (INT,)),                        # value -> int
    (value, (obj,)),                        # value -> obj
]

grammar_json_6 = [
    #
    # --- FILL IN HERE IN QUESTION 7 ---
    #

    # TODO: this version will include words like {'key':[[]]}
    (obj, (LB, obj_right)),                         # obj -> { obj_right
    (obj_right, (RB,)),                             # obj_right -> }
    (obj_right, (members_set, RB)),                 # obj_right -> members_set }
    (arr, (LS, arr_right)),                         # arr -> { arr_right
    (arr_right, (RS,)),                             # obj_right_arr -> }
    (arr_right, (members_arr, RS)),                 # obj_right_arr -> members_arr }
    (members_set, (keyvalue, members_right_set)),   # members_set -> keyvalue members_right_set
    (members_right_set, (COMMA, members_set)),      # members_right_set -> , members_set
    (members_right_set, ()),                        # members_right_set -> epsilon
    (members_arr, (value, members_right_arr)),      # members_arr -> value members_right_arr
    (members_right_arr, (COMMA, members_arr)),      # members_right_arr -> , members_arr
    (members_right_arr, ()),                        # members_right_arr -> epsilon
    (keyvalue, (STRING, COLON, value)),             # keyvalue -> string : value
    (value, (STRING,)),                             # value -> string
    (value, (INT,)),                                # value -> int
    (value, (arr,)),                                # value -> arr
    (value, (obj,)),                                # value -> obj

    # TODO: this version will NOT include words like {'key':[[]]}
    (obj, (LB, obj_right)),                         # obj -> { obj_right
    (obj_right, (RB,)),                             # obj_right -> }
    (obj_right, (members_set, RB)),                 # obj_right -> members_set }
    (arr, (LS, arr_right)),                         # arr -> [ arr_right
    (arr_right, (RS,)),                             # arr_right -> }
    (arr_right, (members_arr, RS)),                 # arr_right -> members_arr }
    (members_set, (keyvalue, members_right_set)),   # members_set -> keyvalue members_right_set
    (members_right_set, (COMMA, members_set)),      # members_right_set -> , members_set
    (members_right_set, ()),                        # members_right_set -> epsilon
    (members_arr, (value_arr, members_right_arr)),  # members_arr -> value_arr members_right_arr
    (members_right_arr, (COMMA, members_arr)),      # members_right_arr -> , members_arr
    (members_right_arr, ()),                        # members_right_arr -> epsilon
    (keyvalue, (STRING, COLON, value_set)),         # keyvalue -> string : value_set
    (value_set, (STRING,)),                         # value_set -> string
    (value_set, (INT,)),                            # value_set -> int
    (value_set, (arr,)),                            # value_set -> arr
    (value_set, (obj,)),                            # value_set -> obj
    (value_arr, (STRING,)),                         # value_arr -> string
    (value_arr, (INT,)),                            # value_arr -> int
    (value_arr, (obj,)),                            # value_arr -> obj

    # TODO: Keep only one of the versions and delete the other
    # TODO: Edit the parser to fit the grammar
]







var0='VAR0'
var1='VAR1'
var2='VAR2'
var3='VAR3'
var4='VAR4'
var5='VAR5'

term0='TERM0'
term1='TERM1'
term2='TERM2'
term3='TERM3'
term4='TERM4'
term5='TERM5'
term6='TERM6'
term7='TERM7'
term8='TERM8'
term9='TERM9'
term10='TERM10'



tests=[[
	(var4,(term6, term6, term7)),
	(var1,(term2, term7, term5)),
	(var3,()),
	(var1,(var4, var0)),
	(var2,()),
	(var0,())
],[
	(var1,(term5, )),
	(var2,(var0, var2, var0)),
	(var3,(term1, term9, term2, term5)),
	(var2,(term4, )),
	(var0,(var0, )),
	(var4,(term7, term9, term9)),
	(var1,()),
	(var2,(var4, )),
	(var2,()),
	(var0,(var4, var4, term7))
],[
	(var2,(term3, term3)),
	(var2,(term3, term1, term9)),
	(var1,(term2, )),
	(var3,(term4, term4, term4, term7, term4, term0, term7))
],[
	(var0,()),
	(var1,(var3, term4, term7, term7, term3)),
	(var3,(term2, term6, term1, term8, term9, term1, term2)),
	(var0,(term8, term0, term6)),
	(var1,()),
	(var3,(var0, term0, term8, term9, term2, var4)),
	(var0,()),
	(var2,(term1, term5))
],[
	(var2,(term3, term8)),
	(var1,()),
	(var2,(term1, )),
	(var0,()),
	(var4,(term0, var1)),
	(var3,(term8, term1)),
	(var2,()),
	(var1,()),
	(var2,(term3, ))
],[
	(var0,(var3, term1, term3)),
	(var4,(term3, term9, var2)),
	(var4,(term5, var4, var1, var4))
],[
	(var4,())
],[
	(var2,(term2, term2, term5)),
	(var3,(term5, term3, term2)),
	(var3,(term3, term1, term8, term7, term0, term1, term6, term0, term3)),
	(var2,(var3, )),
	(var3,(var0, term9, term3, var2, term4, var4, term4)),
	(var3,(var0, term1, term3))
],[
	(var2,(var3, var1, var0, var2)),
	(var0,(var4, )),
	(var3,(term9, term2, term1, term6, term3)),
	(var3,(term4, var1)),
	(var4,(term5, term8, term2, term4)),
	(var3,(term5, ))
],[
	(var4,(term1, term1)),
	(var0,()),
	(var1,(var4, )),
	(var1,(term3, term7, term9, term7, term1, term9)),
	(var1,(term4, term7, var4)),
	(var0,(term5, term0, term3))
],[
	(var1,()),
	(var4,(term9, term8)),
	(var3,(term8, term8, term7)),
	(var0,()),
	(var4,(term6, term5)),
	(var4,()),
	(var4,()),
	(var1,(var2, term6, term0))
],[
	(var2,(term8, )),
	(var4,(var3, )),
	(var1,(var3, )),
	(var0,(term4, var3)),
	(var4,(var2, var1, var4, term0, term2, term4, term7))
],[
	(var2,(term8, )),
	(var0,(term1, term6)),
	(var1,(term4, var2, var1, term1, var4)),
	(var0,(term7, term0, term0)),
	(var0,(term5, term3, term5, term0, term6)),
	(var2,(term8, var3)),
	(var2,()),
	(var4,(term9, ))
],[
	(var4,()),
	(var0,(term7, term3, term4)),
	(var0,(term3, term0, term5, term0, term2))
],[
	(var2,(term3, var4)),
	(var4,(term2, term7, term7, term1, term0, term6)),
	(var3,(term1, var0)),
	(var2,(term0, term9)),
	(var0,(var0, )),
	(var1,(var4, term8)),
	(var1,(term2, term6, term5, term5))
],[
	(var0,(term6, term4, term3)),
	(var0,(var0, term1, var3, var0, term3, term2, term6)),
	(var2,(var4, )),
	(var0,(term1, term8, term5)),
	(var1,()),
	(var1,(term6, term8)),
	(var1,()),
	(var1,(term9, term5, term0, term1, term8, term2, term3, term7)),
	(var3,(term8, var2))
],[
	(var4,(term1, term4, term5)),
	(var0,()),
	(var3,(var3, )),
	(var1,(term7, term5, var3, term7, term3, var4, term6, var2, term8, term2)),
	(var3,(term6, var0, var0, term7, term4)),
	(var3,(term4, term6, term5, term7, term3)),
	(var0,()),
	(var2,())
],[
	(var2,()),
	(var0,(var0, term0)),
	(var0,(term6, term9, term4, term9))
],[
	(var1,(term8, term4, term0))
],[
	(var2,(var4, term0, term8)),
	(var4,()),
	(var3,(term2, term4, term0)),
	(var0,(term0, var0, term8, var1, term5)),
	(var2,(term8, ))
],[
	(var3,(var4, )),
	(var3,(var0, term6)),
	(var0,(term1, )),
	(var1,(term5, term4, var2, var3, var0, var4, var4)),
	(var2,(term0, term2, term3))
],[
	(var4,(var2, var4, var4)),
	(var1,(term7, term8)),
	(var0,(var3, term2, term5, term5, term5, var3, term1)),
	(var2,(term7, term1, term2)),
	(var3,(term0, )),
	(var1,(term3, term1, term9, term6, term5, term3, term3)),
	(var1,(term2, term1)),
	(var4,())
],[
	(var1,()),
	(var4,()),
	(var0,(term9, term5, var0)),
	(var4,()),
	(var3,(term4, term3, term2, term5, term6))
],[
	(var0,(term5, term0, term4, term7, term2, term0, term4)),
	(var0,(term5, term6, term6, term5, term1, term8, term0)),
	(var2,(var2, term7, term8, term9, term2, term0))
],[
	(var0,(term6, term7)),
	(var1,(term7, term5, term0, term3)),
	(var3,(term7, term2, term0)),
	(var4,(term7, term2, term8))
],[
	(var1,(term4, term7, term4, term7, term8, term3)),
	(var1,(term3, term6, term9, term8, term6, term9, term3)),
	(var3,(term3, term3, term9, term2, term9))
],[
	(var2,(term3, term2)),
	(var3,(var1, term5, var1, term4, term9, term6)),
	(var0,(term8, term5)),
	(var3,(term5, term2, term3, term3, term2, term4, term2, term4, term6)),
	(var4,()),
	(var1,(term1, term2)),
	(var0,(term1, term7, term8)),
	(var0,()),
	(var2,(term6, term1, term7, term3, term2, term9)),
	(var3,(term9, term5, term0, term2))
],[
	(var3,(term9, )),
	(var3,(var4, ))
],[
	(var2,(term0, term9, term6, term7, term8, term7, term2, term9)),
	(var0,(term1, term0)),
	(var2,(var3, var2)),
	(var3,()),
	(var2,()),
	(var0,(term2, term6, var3)),
	(var3,(term2, )),
	(var0,()),
	(var1,(term7, term9, term5))
],[
	(var4,(var3, )),
	(var1,(term7, term0, term3, term6, term3, term8, term8)),
	(var1,(var4, term9)),
	(var4,(term5, )),
	(var2,(var3, term5))
],[
	(var3,(term2, term7, term6)),
	(var1,(term4, term5, term2, term5, term0)),
	(var0,(term2, term3, term5)),
	(var0,(term5, term4, term5, term2)),
	(var4,(term0, term3)),
	(var0,(term8, term0, term0, term9, term9, term5, term3)),
	(var2,(term6, var3)),
	(var4,())
],[
	(var3,(term6, ))
],[
	(var0,(var0, var2, var4, term7, term5)),
	(var2,(term1, term5)),
	(var2,(term1, var4, term9)),
	(var4,()),
	(var0,(var0, )),
	(var2,(term6, term9)),
	(var2,(term0, term5, term4, term1, term8, term2)),
	(var3,(term7, term3, term1, term8, term1, term7, term1)),
	(var4,(term0, term7))
],[
	(var0,(term4, term3, term0, term1, term8, term4, term6)),
	(var2,(term0, term1, term1)),
	(var2,(term4, term4, term2, term2, term5, term2, term9)),
	(var4,(term2, var2))
],[
	(var3,(var4, )),
	(var1,(term7, term1, var0, term1, term8)),
	(var4,(term8, term7, var0, term0)),
	(var3,()),
	(var2,()),
	(var4,(term4, term2)),
	(var0,(term6, term9, term5, var1))
],[
	(var3,(term5, term3)),
	(var0,()),
	(var1,(var2, term0, var4)),
	(var2,()),
	(var0,(term4, term3, term9, term8)),
	(var2,(term7, term6, term0, term0, term5, term0, term8, term0, term8)),
	(var4,(term2, )),
	(var4,(term0, term1, term2)),
	(var4,(term7, var2)),
	(var0,())
],[
	(var0,(term3, var2, term5)),
	(var0,(term3, var1, term1)),
	(var2,(term5, term0)),
	(var2,(term8, term5)),
	(var2,(var2, )),
	(var1,(term4, term4, term9, term3, term6, term7, term8, term2, term8, term3))
],[
	(var1,(term3, term5, term9)),
	(var0,(term6, term0, var0, var1, term3, var2, var3)),
	(var1,(term3, term4)),
	(var4,()),
	(var2,(term4, term1, term3, term6)),
	(var2,(term5, term4, term0))
],[
	(var2,(term0, term6, term5)),
	(var3,(term5, )),
	(var2,(term5, term0, term9, term1, term4)),
	(var4,(var2, )),
	(var0,()),
	(var2,(var0, )),
	(var2,())
],[
	(var4,()),
	(var0,(term4, var3)),
	(var4,(term9, )),
	(var1,(term6, term8)),
	(var0,()),
	(var4,(term5, term0)),
	(var0,()),
	(var0,())
],[
	(var2,(term2, term6, term8)),
	(var2,()),
	(var3,(term1, term8, term7, term2, term3, term2, term8)),
	(var2,()),
	(var4,()),
	(var2,(term6, term2, term7, term0)),
	(var2,(term6, term4, term6)),
	(var4,(term0, )),
	(var2,()),
	(var2,(var2, term5, term3, term0, term6, term9, var4))
],[
	(var1,(term5, term9, term6, term0, var0)),
	(var3,(term1, term9, term1)),
	(var4,(term1, term2, term8)),
	(var2,(var2, term7, term2, term1, var1, term5, var4, term8)),
	(var0,(term8, term5, term0, term4, term2, term3))
],[
	(var4,(var3, var0, var4, term7, term2)),
	(var3,(term3, )),
	(var4,(var2, term5)),
	(var0,(var1, )),
	(var1,()),
	(var0,()),
	(var0,()),
	(var4,(term8, term0, term8, term5, term1)),
	(var4,(term3, term3, term7, term3, term1, term3, term6))
],[
	(var4,(var4, var0, var2)),
	(var1,()),
	(var3,(term8, var2, term3))
],[
	(var0,(term4, var1, term7, var3, var0, var2, term5)),
	(var0,()),
	(var4,(term3, term4, term4, term3)),
	(var4,(term9, var3, term3, term5, term9)),
	(var1,(var2, var4)),
	(var2,())
],[
	(var2,(term6, term9, term7, term3, term8, term1, term1, term7, term6, term5)),
	(var4,(var0, )),
	(var1,(term4, var4, var0, var2, var0, term9, term1)),
	(var1,(term8, term1, term9, var3)),
	(var3,(var0, term1)),
	(var2,(var4, var4)),
	(var4,(term7, term8, term9)),
	(var3,(term6, term1, term0, term2)),
	(var1,(term9, var4))
],[
	(var4,()),
	(var2,(term9, )),
	(var4,(term0, term9, term3, term0)),
	(var4,(term2, term3, term2, term2, term5, term2, term1))
],[
	(var0,(term7, term5, term3, term7, term1, term2, term7)),
	(var0,(term1, term5, term8, var0, term9, term6, term3, var1)),
	(var3,(var0, )),
	(var0,(term5, ))
],[
	(var3,(term1, term3, term5))
],[
	(var4,())
],[
	(var4,(term5, term2, term0)),
	(var0,(term3, term9, term0, term4, term1, term1, term4)),
	(var4,(term0, term8, term3, term6, term1, term5, term0)),
	(var4,(term7, term2, term0, term8, term1, term7)),
	(var1,(term2, term4, term4)),
	(var2,(var0, term9, var2, term1, term3)),
	(var3,()),
	(var0,(var4, )),
	(var3,(var0, var4)),
	(var3,(term1, term8))
],[
	(var0,(term6, term1, term0, term7, term8)),
	(var3,(term7, )),
	(var3,()),
	(var2,()),
	(var2,(term1, )),
	(var3,(term2, )),
	(var2,(term5, term6, term4, term5)),
	(var2,(term9, var2, term6, term4, var4, var2, term2))
],[
	(var3,(term9, term7, term5)),
	(var2,(term3, var4, var3, term1, term0, var4, term3)),
	(var0,(term9, term6, term6, term1)),
	(var3,(term2, var2, var3, term0)),
	(var3,(term0, term8, term0, term2, term2, term6)),
	(var3,(term3, term7, term0, term0, term5, term5, term7)),
	(var1,(term2, term1)),
	(var4,()),
	(var2,(term1, )),
	(var1,(var0, ))
],[
	(var3,(var0, term3)),
	(var0,(term2, term5)),
	(var4,(term6, )),
	(var0,(var0, term2, term8, term1)),
	(var4,(term7, )),
	(var4,(var2, ))
],[
	(var2,(term0, term1)),
	(var4,(term7, term9, var4, var1, var4, var4)),
	(var2,(term6, var3, var3, term0, term8, term7, term5)),
	(var4,(term6, term3, term9, term9)),
	(var4,()),
	(var1,(term6, ))
],[
	(var4,()),
	(var3,(term6, term7, term3, term3, term1, term7, term1)),
	(var1,(term1, term0, term2, var4, term5, term7, var0)),
	(var4,(term1, term7, term2, term2, term4, term8, term6, term6)),
	(var1,(term0, var4, term4, var0)),
	(var2,()),
	(var2,())
],[
	(var4,(var0, )),
	(var2,()),
	(var0,()),
	(var4,(term5, term9, var4, term0, var4, term3, var2, var1, var4))
],[
	(var2,(var0, term4, var0)),
	(var0,()),
	(var3,(var0, )),
	(var2,(term9, term4, term7, term2)),
	(var0,(term4, term6, term9)),
	(var4,(term3, term4, var0, term9, var3, term0, term3)),
	(var1,(term1, var1, var2)),
	(var4,(term3, term3)),
	(var1,(term7, )),
	(var2,(term2, ))
],[
	(var0,()),
	(var4,()),
	(var2,(term7, )),
	(var4,(var3, var4, term8, term6, term4)),
	(var1,())
],[
	(var2,(term4, )),
	(var4,(term7, var1)),
	(var2,(term4, var2)),
	(var4,(term9, term5, term6, term5)),
	(var2,()),
	(var1,(var2, )),
	(var4,(var4, var0)),
	(var4,()),
	(var0,())
],[
	(var1,(term4, term0, term1))
],[
	(var2,(term1, term1, term9, term1)),
	(var1,(term7, term2, var1, var0, term8, term5, term4, var4, var1)),
	(var2,(term4, term1, term0, term9, term9)),
	(var1,()),
	(var2,(var1, var0)),
	(var3,(term1, term7)),
	(var2,()),
	(var3,(term5, term2, term3, term3, term5, term7, term8)),
	(var0,(term4, term0, term4)),
	(var3,(term8, term5, term6))
],[
	(var1,(term0, term6, term0, term3, term8, term4, term2))
],[
	(var0,()),
	(var4,(var1, var3, term9)),
	(var1,(term6, term3)),
	(var0,()),
	(var0,(term1, var0)),
	(var1,(term8, term6, term4, term8, term7, term4, term4, term8, term4)),
	(var2,(var0, var4)),
	(var2,(var4, term2, var1, var4, var0, var3, var3))
],[
	(var4,(term9, term0, var4)),
	(var3,(term6, )),
	(var2,(var0, )),
	(var4,(term1, term1, term0)),
	(var3,(var4, term7, term9, term5))
],[
	(var1,(term8, var0, term1, term2, var2, term9, var0)),
	(var2,()),
	(var4,(var2, term8, term4, term9))
],[
	(var0,(term9, term0)),
	(var0,(term4, term3, term2, term5, term6)),
	(var3,(term3, term6, term8)),
	(var4,()),
	(var2,(term8, )),
	(var2,(term7, term6, var1, var2, term8, var1)),
	(var3,()),
	(var1,(term5, var4)),
	(var4,(term5, term2))
],[
	(var1,(term1, term6, term7, var3)),
	(var4,(var3, var0, term3)),
	(var4,()),
	(var1,(term5, term3)),
	(var4,(term0, term5, term9, term9, term6)),
	(var3,(term8, var4, term2, var0, var2, var4, term1)),
	(var2,(term3, term5, term5, term0, term1)),
	(var3,(term1, term1, term3, term3, term8, term5)),
	(var0,(term1, term8, term7, term8, term6, term4, term1, term0, term3, term5)),
	(var0,(term7, term9, term0, term6, term1, term4, term6, term7, term7))
],[
	(var0,(term4, ))
],[
	(var2,(var2, term7, var1, term3))
],[
	(var0,(term2, term7, term8)),
	(var1,(term0, term2, term7, term9, term7, term1, term1)),
	(var4,(term5, )),
	(var1,(term6, )),
	(var3,(var3, var3)),
	(var1,(term3, ))
],[
	(var4,(term2, term0, term1, term0)),
	(var3,(var2, var4, term3, term3, var2)),
	(var2,(term2, term2, term5, term2, term1)),
	(var1,(var2, var4, var4, var4, term8, term6, var1)),
	(var2,(var0, )),
	(var2,(var2, var2, var3, var1, var0, var3)),
	(var4,(term0, var1, var3, var2, term7, term0, var3))
],[
	(var4,(term9, term3, term1, term8, term7, term8, term9)),
	(var0,(term7, term7, term2, term1, term1)),
	(var1,(term9, term7, term2, term0, term6, term4)),
	(var3,(term3, term8, term4, term0, term6, term6)),
	(var4,()),
	(var0,(term1, term4, term9, term6, term6, term7))
],[
	(var0,()),
	(var0,(var0, var0, term8)),
	(var2,(term9, term2, term0))
],[
	(var3,(term3, term7, var3)),
	(var0,(term1, term5)),
	(var2,(term8, term9, term4, term9, term8, term5)),
	(var3,(term5, term1, term0))
],[
	(var2,(var4, term5, term7, term0, term7, var1, term0)),
	(var1,(term2, term8, term9, term4, term2))
],[
	(var1,()),
	(var4,()),
	(var1,(term2, term2, term1, term3, term3, term0, term7)),
	(var4,(term0, term9, term0, term7)),
	(var1,(term6, term9, term6)),
	(var2,(term6, var0, var4, var4, var1, term9, var0, term9, term5, term0))
],[
	(var2,(term8, term4, term5, term0, var3)),
	(var2,(term3, var0)),
	(var2,()),
	(var3,(var1, var3, term0, term4, term6, var1))
],[
	(var0,(term4, term7)),
	(var1,(term9, var2, term6, term7, term2, var4)),
	(var3,(var2, var0, var0))
],[
	(var4,(term5, term2, term2, term7, term7, term8, term7, term9)),
	(var1,()),
	(var2,(term5, term2, term3)),
	(var3,(term2, ))
],[
	(var4,(var1, term3)),
	(var4,(term7, term5)),
	(var4,(term9, ))
],[
	(var0,(term8, )),
	(var0,(term0, term4)),
	(var2,(term6, term8, term7)),
	(var0,(var0, term3, term4, term1, term5))
],[
	(var3,()),
	(var4,(term4, term1, term8)),
	(var1,(term0, var2, term6, term6, term2)),
	(var0,(term8, term7, term4, term3, term3, term0)),
	(var1,(var1, term9, var3, var1, term1, term1)),
	(var4,(term3, term7))
],[
	(var0,(term2, term9))
],[
	(var2,(var2, )),
	(var0,(term2, var1, term2))
],[
	(var1,(term0, term1)),
	(var2,(term4, )),
	(var2,()),
	(var4,()),
	(var0,(var0, )),
	(var4,(term2, term0, term0)),
	(var0,(term0, term9))
],[
	(var0,(var1, var0, term0)),
	(var2,(term7, term1)),
	(var1,(term7, var0, var2, term2, var1)),
	(var4,(var1, var1, term2)),
	(var4,(var1, term8, var1)),
	(var3,(term8, term1, term7, term6, term0, term2, term8, term3, term1)),
	(var3,(term1, term9, var3, var3, term1, term3, term1, var1)),
	(var2,(var1, var1)),
	(var1,(term4, term6, term9)),
	(var1,(term2, term6))
],[
	(var1,(var1, var2)),
	(var3,(term3, term3, term9, term3, term2, term9, term0)),
	(var0,(term9, var0)),
	(var0,(var3, term5)),
	(var4,(term9, term7, term3, term5, term5))
],[
	(var3,(term3, )),
	(var4,(term7, term2, term2, term0, term8)),
	(var4,(term1, term6, term7, term9, term5, term4)),
	(var2,(term3, term3, term2, term4, term7, term5)),
	(var3,(term7, term7, term5, term6, term8)),
	(var0,(var2, )),
	(var0,(term9, )),
	(var2,(var1, var3, var4)),
	(var4,(term1, var0, term1)),
	(var2,(term5, term8, var0, term6))
],[
	(var2,(term6, )),
	(var0,(var0, )),
	(var0,(var1, )),
	(var3,(var3, )),
	(var2,(term1, )),
	(var4,(term5, term9, term1, term8, term2))
],[
	(var2,(var3, )),
	(var4,()),
	(var4,(term6, term0, term1, term2, term2, term5, term2, term7, term9, term1)),
	(var1,(term6, term4, term5))
],[
	(var0,(term8, term1)),
	(var0,(var3, )),
	(var2,(term2, term5, term7, term3, term8)),
	(var3,(term1, term7, term5, term9, term3, term4, term0)),
	(var2,(term0, term0)),
	(var4,(term6, term4)),
	(var4,(term2, term0, term8)),
	(var1,(var2, term6, term9, term8))
],[
	(var3,())
],[
	(var1,(term5, var4, var3, term9, term3)),
	(var1,()),
	(var2,(term4, term9))
],[
	(var3,(term2, term9, term4, term9, term7))
],[
	(var4,()),
	(var1,(var1, term9, term9)),
	(var3,(var2, term5, term3, var4, var3))
],[
	(var2,(term2, term6, term1, term5)),
	(var0,(term5, term5, term5)),
	(var3,(term9, term2, term5, var0)),
	(var4,(term3, term1, term1)),
	(var2,(term0, term7, var0, var2, var2)),
	(var4,(var1, term6)),
	(var1,())
],[
	(var3,()),
	(var3,(var3, )),
	(var4,()),
	(var1,(var2, var3)),
	(var1,(term7, term1, term0))
],[
	(var1,(term3, term5, term7, term6, term3, term6, term2, term2, term8, term6)),
	(var3,(term2, term2)),
	(var4,(term5, term5, term8, term8))
],[
	(var2,(term2, term7, term2, term9, term9, term3))
],[
	(var4,()),
	(var2,(term1, term3, term7)),
	(var1,(var1, term4, var4, var1, term3, term9, term1)),
	(var1,()),
	(var1,(term9, term6, term5, term4)),
	(var3,()),
	(var2,(term8, term6)),
	(var1,(var3, )),
	(var3,(term0, term8, term3))
],[
	(var3,(term8, term4)),
	(var1,()),
	(var0,(term7, term8, term0)),
	(var3,(term6, term5, term8, term9, term4)),
	(var2,(var3, term4, var2, var0, var4, term4, term9)),
	(var0,(term1, term6)),
	(var4,(term6, )),
	(var2,(term0, term5, term9)),
	(var4,(term4, var2, var2, var4, term6, term4)),
	(var0,(term4, var0, var3, term0, term3, term8, term3, term8, var1))
],[
	(var1,()),
	(var2,(term9, var3, term3, var3, term3, var2)),
	(var1,(term5, term9, var2, term9, term8, term8, term2, var1, term9)),
	(var1,(var1, )),
	(var0,())
],[
	(var1,(term1, term1, term7)),
	(var2,(term8, term7, term2)),
	(var3,(var2, term5, var1)),
	(var0,(term6, term6, term9)),
	(var0,(var3, var4, term5))
],[
	(var3,(var1, term6)),
	(var0,(var2, )),
	(var0,(term3, )),
	(var3,(var4, var3, term4)),
	(var2,(term0, var4, var3, var2, term1, term9, term4, term5))
],[
	(var1,(term1, )),
	(var0,(term0, term0)),
	(var1,(term8, term0)),
	(var4,(term5, )),
	(var1,(term6, )),
	(var3,(var0, var3)),
	(var4,()),
	(var4,(term0, term4, term7, term0, term1, term9, term6, term3, term6)),
	(var4,(term7, var1, var4, var2, var3, term1))
],[
	(var0,()),
	(var0,(var3, term0)),
	(var1,(term5, term1, term9, term9)),
	(var1,()),
	(var1,(term0, term4, term0, term1, term1, term2)),
	(var0,(term3, )),
	(var4,()),
	(var3,(var1, ))
],[
	(var4,(term1, term9))
],[
	(var4,(term4, ))
],[
	(var0,(term6, term6, term7, term2, term8, term4)),
	(var0,(var0, var1, var4)),
	(var2,(var1, var3, term3, var1, term1, var0, var2)),
	(var2,(term7, term1, term0)),
	(var2,(var4, )),
	(var0,(term2, )),
	(var2,()),
	(var0,(term7, term0, term8, term2, term6, term5, term3)),
	(var0,(term8, term9)),
	(var4,(term3, term0, term6))
],[
	(var2,(term4, )),
	(var3,(var2, term8, term1))
],[
	(var0,()),
	(var4,(term1, term8, term7)),
	(var3,(term6, term2)),
	(var2,(term0, term6, term4, term2, term2, term9, term6)),
	(var2,(term0, term7))
],[
	(var3,(term4, term2))
],[
	(var1,(term1, term3, term2)),
	(var0,(var0, var0, var1, term2)),
	(var3,(var3, )),
	(var0,(term8, term8, term4, term9, term1)),
	(var0,(term3, )),
	(var3,(term5, ))
],[
	(var2,(term6, term2, term6, term7)),
	(var3,(term2, term5, term0, term2, term6, term8, term5, term4)),
	(var0,(term2, term7, term0, term8, term9, term8)),
	(var3,()),
	(var4,(term6, term5)),
	(var0,(var4, term5, var3, term0, var0, term7, var4)),
	(var2,(term9, term7, term0, term3, term6)),
	(var3,(term0, )),
	(var2,())
],[
	(var2,()),
	(var0,(var2, )),
	(var3,(term2, term2, term6, term7, term8)),
	(var3,(term6, term0)),
	(var2,()),
	(var0,(term7, term2, term1, term0, term8, term9, term7, term9)),
	(var4,(term6, term3, term5, term8, term1, term9, term9)),
	(var1,(term0, term1, term5, term4, term6, term1)),
	(var2,(term8, )),
	(var1,(term7, term3, term8))
],[
	(var0,(term5, term3, term5, term9, term4, term0, term4, term7))
],[
	(var0,(term8, term7, term9, term0, term9, term2, term4)),
	(var0,(term1, term3, term6)),
	(var0,(term8, term3, var0, term5, term9)),
	(var0,(var1, var4, term6, var2, term2)),
	(var4,(term1, term4, term0))
],[
	(var4,(var2, term4)),
	(var3,(term5, term2, term2)),
	(var2,(term6, term9, term2, term5, var2, term9, term5, term6)),
	(var0,(var1, var3)),
	(var2,()),
	(var1,(term9, term8, term7, term5, term6, term1, term3)),
	(var2,(term3, term6, term0)),
	(var4,(term2, )),
	(var2,(term5, term5, var1, term2, term4, term5, var2, term3))
],[
	(var0,(term8, term8, term1, term2, term2)),
	(var4,(term0, term4, term1, term9, term4, term4))
],[
	(var1,(term8, term9, term8))
],[
	(var0,(var3, )),
	(var3,(var0, var1, term7, term3)),
	(var3,())
],[
	(var0,(var1, var4, var0, var0, term1, term0, term8, var0, term7, var0))
],[
	(var1,(var4, )),
	(var2,(term0, term4, term1, term6, term7, term9)),
	(var3,(var2, var1, var1, term1)),
	(var2,(term1, term6, term4)),
	(var3,()),
	(var3,(var0, var0, term8, term2, var4, term9, term2, term3))
],[
	(var1,(var3, var0, term0, var2, term9, term3, var4)),
	(var3,(term0, term1, term4)),
	(var2,(term2, term1, term5)),
	(var3,(term8, term7, term7, term8)),
	(var4,(term1, term6, term6, term3, term0, term5, term1, term3)),
	(var2,(term3, term2)),
	(var2,(term2, ))
],[
	(var3,())
],[
	(var4,(term8, term4, term6))
],[
	(var4,()),
	(var0,(term3, term8, term4, term4, term2, term6, term3)),
	(var2,(term6, )),
	(var4,(term9, term4, term8, term8, term9, term4))
],[
	(var3,(term6, var0, var0, term9, term6)),
	(var1,(term4, term4, term2))
],[
	(var3,()),
	(var3,(term3, )),
	(var3,(term9, )),
	(var0,(var4, var0))
],[
	(var2,(term5, term4, term9)),
	(var1,(term8, term4, term2)),
	(var4,(term9, var0, term2, term6, var4, var0, term2)),
	(var4,(term9, term9, term7, term3, term7, term6)),
	(var0,(term5, )),
	(var1,(var2, term1, term6, var3)),
	(var4,(term0, var1, term6, term8, var0)),
	(var2,(term9, term8))
],[
	(var2,()),
	(var0,(var4, ))
],[
	(var4,(term0, )),
	(var1,(var1, term8, term5)),
	(var1,(term0, term8)),
	(var0,()),
	(var1,(term3, ))
],[
	(var3,()),
	(var4,(var4, term5, term0, var2)),
	(var2,(var4, var2, var3)),
	(var3,(term2, term8, term0))
],[
	(var2,(term3, term9))
],[
	(var1,(term8, term3, term5, term7)),
	(var3,(term3, var2, var1, var3, term7)),
	(var0,(var3, var3, term0))
],[
	(var0,(term0, var0, term9)),
	(var2,(term4, term1, term4, term9, term6)),
	(var3,()),
	(var1,(var4, term2, term7))
],[
	(var3,(term7, term9, term1, term3, term4, term6, term8)),
	(var4,(term1, ))
],[
	(var4,(term8, term6, term0, term8, term3, term8, term4)),
	(var2,(term0, term2, term2)),
	(var0,()),
	(var3,(term0, term0, term7, term5, term6, term7, term8, term8, term2, term7)),
	(var4,(term8, term7, term5, term6, var1, var2, term1, var1, var1)),
	(var0,(term1, term2, term8)),
	(var3,(term4, term4, term6, term2, term5)),
	(var3,(term5, term9)),
	(var4,(term2, term8, term5, term8, term9, term3, term2, term0, term4))
],[
	(var3,(term3, term5)),
	(var1,()),
	(var2,(term5, term6)),
	(var3,(term9, term5, term2)),
	(var2,(term4, term8, term8)),
	(var2,(term9, term8)),
	(var3,(term4, term3, term1, term1, term5, term6, term0))
],[
	(var3,(var2, term5, term0)),
	(var3,()),
	(var3,(term8, term1)),
	(var0,(term2, term0, term0)),
	(var1,(term3, term8, term7))
],[
	(var0,(term7, term2))
],[
	(var2,(term6, term8)),
	(var3,(term8, var4, term9))
],[
	(var2,(term4, )),
	(var3,(term1, term4)),
	(var3,(term7, term2, term8, term5)),
	(var1,(var0, var2, var3)),
	(var2,(term2, term1, term1, term9, term0, term2, term9, term1, term6, term0))
],[
	(var1,(term0, var0, var0)),
	(var0,(term2, term7)),
	(var3,(term2, term4)),
	(var1,(var0, term7, term2, term7, term2)),
	(var3,(term3, var3, term2)),
	(var4,(term7, term8)),
	(var3,()),
	(var4,(term8, term2, term6)),
	(var1,(term3, ))
],[
	(var0,(term8, term5))
],[
	(var3,(var0, var3)),
	(var3,(term8, term0, term3, term7, term7))
],[
	(var0,(term1, term3)),
	(var1,()),
	(var1,(term8, term2, term1)),
	(var3,(term2, term8, term8, term2, term6, term6, term0, term0, term3, term8)),
	(var3,(term3, term8, term1))
],[
	(var3,(var1, )),
	(var4,(var3, term9, var1)),
	(var0,(term5, term6, term8, term3, term3, term7, term7, term0)),
	(var3,(var2, term5)),
	(var2,(term0, term4, term3)),
	(var1,(term9, term9, term8, term5, term8, term9, term8)),
	(var3,(term5, term5)),
	(var3,(term4, term9)),
	(var3,(var3, ))
],[
	(var1,(term3, term5, term4)),
	(var0,(term2, var3)),
	(var0,(var1, term2, var2)),
	(var2,(term2, term4)),
	(var2,(var1, )),
	(var0,(term4, term1, term1))
],[
	(var3,(term8, term2)),
	(var1,(term2, ))
],[
	(var1,(term4, term6, term2, term8, term9, term2, term6, term5)),
	(var0,(term6, term6, term9, term1, term1, term1, term1)),
	(var4,(term1, )),
	(var3,()),
	(var4,()),
	(var3,(term7, term3, term8)),
	(var1,(term7, term5, term0, term4)),
	(var3,(var4, term5)),
	(var3,(term0, term1, term2, term6, term7, term2, term8)),
	(var4,(term5, term1, term6, term9, term3, term6, term0, term6, term6, term6))
],[
	(var0,(term0, term2, term7, term7, term4, term6)),
	(var4,(term6, term8, term4, term8, term6)),
	(var0,(var0, var4, var0, term7, var2)),
	(var0,(term6, term1, term9, term3, term8, term0, term4, term2, term1, term9)),
	(var4,(term6, term7, term3, term5, term8)),
	(var0,(term1, term6, term0, term4, term5, term9, term5)),
	(var4,(var0, term4, term1, term7, term2)),
	(var3,(term5, term2)),
	(var0,(var1, term0, var0, term4, term8, var2, term5, term9))
],[
	(var2,(term9, term7)),
	(var4,()),
	(var0,(var0, term0, var1))
],[
	(var2,(var0, )),
	(var1,(var0, var0)),
	(var0,(term4, term9, term9)),
	(var0,(term7, )),
	(var3,(term7, )),
	(var4,()),
	(var4,(term4, term5, var0, term3, var3, term7, var4, term5))
],[
	(var3,(term9, )),
	(var1,(term1, term9, term5, term0)),
	(var2,(term8, var1, term9, var0, var3, var1)),
	(var2,()),
	(var4,(term6, term7, term6))
],[
	(var0,()),
	(var1,(term5, term6)),
	(var4,(term4, term0)),
	(var3,(term4, term1, term5)),
	(var2,(term5, )),
	(var4,(term0, term9, term8)),
	(var3,()),
	(var4,())
],[
	(var0,(term3, term3, term2)),
	(var3,(term9, term1, term4)),
	(var4,(var4, var0, term0, term6)),
	(var0,(term3, term4, term6, term9, term3, term3, term8)),
	(var1,(term4, var2)),
	(var0,(var1, )),
	(var0,(term4, )),
	(var1,(term7, )),
	(var0,(var0, ))
],[
	(var2,(term2, term1, term4, term1, term9, term6, term7)),
	(var0,(term6, )),
	(var4,(term7, )),
	(var0,(term8, term7, term8, term3, term9, term5, term3)),
	(var0,(var1, ))
],[
	(var2,()),
	(var4,(term1, term7)),
	(var3,(term6, term4)),
	(var3,(var0, )),
	(var1,(term1, var4)),
	(var4,(var0, )),
	(var3,(term8, term2, term4, term0))
],[
	(var2,()),
	(var4,(term6, term3)),
	(var0,(var3, var3)),
	(var2,(var0, var3, term1, var1, term5, term6, var1)),
	(var2,(var1, )),
	(var4,(var0, var1, var4))
],[
	(var4,(term6, )),
	(var1,(term1, term7)),
	(var1,(term5, term3)),
	(var4,(term9, var0, var2, term9)),
	(var2,(var4, ))
],[
	(var0,(var4, )),
	(var1,(term1, term8, term2, term8, term7, term9)),
	(var0,(term3, term1))
],[
	(var4,(term0, )),
	(var0,(var3, )),
	(var2,(term8, term0, term1, term5, term3, term5)),
	(var1,(term2, term0, term0)),
	(var3,(term7, term1, term8, term8, term0, term3))
],[
	(var3,(term0, var1, term4))
],[
	(var3,(term9, term5, term3, term2, term1, term6, term1, term6)),
	(var2,(term0, var3, var4)),
	(var2,(term8, term8, term2, term3, term6, term9, term7)),
	(var4,(term1, term3, term0, term4)),
	(var2,(var4, )),
	(var1,(term2, term5, term5, term1, term6)),
	(var2,(term4, term6, term2))
],[
	(var3,(term6, term2, term4)),
	(var3,(term5, term4, term0)),
	(var3,(term3, term4)),
	(var4,()),
	(var2,()),
	(var0,()),
	(var4,(term0, term8)),
	(var0,(term7, term6, var2))
],[
	(var3,(term3, term7, term6)),
	(var4,(term9, term2)),
	(var0,(term7, term6)),
	(var1,(term1, term6, term0, term9, term0, term9, term5, term3))
],[
	(var3,(term0, term6, term2)),
	(var4,(term6, term8, term5, term2, term3, term0, term8, term6)),
	(var3,(var0, term6)),
	(var2,(term6, term7, term6, term8, term2, term5, term5)),
	(var2,(var2, term5, var4, var3, var0)),
	(var1,()),
	(var0,(term2, ))
],[
	(var0,()),
	(var1,(term6, )),
	(var0,()),
	(var1,(term4, term2, term0, term5)),
	(var4,(term8, term9, term7, term7, term7, term6))
],[
	(var2,(term3, term2)),
	(var1,(var1, term0, term3, term0)),
	(var4,()),
	(var4,()),
	(var0,(term1, term1)),
	(var0,(term7, term1, term8, term0, term7)),
	(var1,())
],[
	(var2,(term7, term8)),
	(var0,(term3, term4, term4)),
	(var3,(term8, )),
	(var2,(term6, var2, var2, term8, term1, term3, term8))
],[
	(var4,(term1, term3, term8, term8, term9, term6, term8)),
	(var4,(term4, term9)),
	(var3,(term9, )),
	(var2,(term8, term8)),
	(var2,(var4, var0, var4, var0)),
	(var0,(term7, term5, var2)),
	(var0,(term7, term3, term0)),
	(var1,(term6, )),
	(var3,()),
	(var1,(var3, term0, var0, term0, term1, var4, term8, term3))
],[
	(var0,()),
	(var3,(term1, term9, term1, term7)),
	(var1,(var4, term3, var3, term2, var3)),
	(var4,(var4, var3)),
	(var4,(term4, term2)),
	(var2,(term2, term3, term8, term6)),
	(var2,(term1, term1)),
	(var1,(term4, )),
	(var3,(term2, )),
	(var4,())
],[
	(var4,(var1, term3, term4)),
	(var2,(var3, var1, term4, term4, var4)),
	(var2,()),
	(var4,(term0, term9, term8, term1))
],[
	(var0,(term0, term6, term0, term4, term4, term1, term4)),
	(var1,(term5, term4, term0)),
	(var1,(term6, term9, term7, term7, term3)),
	(var2,(term7, term7, term9, term5, term1)),
	(var0,(term7, var4)),
	(var0,(var3, ))
],[
	(var1,(term5, var3, var4, term8, term0, var2, term7)),
	(var4,(term9, term5)),
	(var2,(var2, )),
	(var3,(var0, term0, var1, term7, term1)),
	(var0,(term6, term4, term3)),
	(var4,()),
	(var3,(term0, term2, term1)),
	(var4,()),
	(var2,()),
	(var3,(var4, ))
],[
	(var4,(term7, term8, term7, term3, term5, term3, term0)),
	(var4,(var1, )),
	(var0,(term7, ))
],[
	(var1,(var4, term6)),
	(var1,()),
	(var3,(var3, )),
	(var3,(term6, term9, term0, term8, term3, term6)),
	(var0,(term3, )),
	(var0,(term8, term8, term9, term1, term9, term0, term0, term9, term4)),
	(var1,(term1, term3, term4)),
	(var2,()),
	(var4,(term2, term0, term7))
],[
	(var3,(term7, term9, term3, term4, term4, term6, term3)),
	(var3,(term0, )),
	(var3,(term0, term7, term2, term2)),
	(var1,(var1, term2, term2)),
	(var3,(term4, term3)),
	(var3,(var0, term9, var2, var0, var2, term2, term1)),
	(var3,(term0, term6, var2, var3, term8)),
	(var0,(term7, var1, term8))
],[
	(var0,(term0, var3, term8, term8)),
	(var3,(term2, term7, term1))
],[
	(var0,(term1, var4)),
	(var1,()),
	(var2,(term4, term1, term9)),
	(var3,(term3, term8, term5)),
	(var0,(term2, term3, term3)),
	(var0,(term4, ))
],[
	(var4,(term0, var0, var4)),
	(var1,(term0, term9, term5, term0, term6, term8, term0)),
	(var0,(term9, var1, var0, var0, term6, term1, var1, var0, term3, var1)),
	(var1,(term5, term7, var2, term5, var4, var3, var0)),
	(var3,(term2, term8, term0, term0, term3, term2)),
	(var2,(term7, )),
	(var2,(term3, )),
	(var3,()),
	(var1,(term5, term8))
],[
	(var3,(var1, var1, term3, term9, var0, term2))
],[
	(var1,(var2, var4, var0, var0, var2)),
	(var4,(var4, var3)),
	(var0,(term7, term3, term1, term4)),
	(var4,(term2, term4, term0)),
	(var0,(term3, term8, term7, term6)),
	(var2,(term9, term7))
],[
	(var2,(var0, term5, var4)),
	(var2,(term2, term3, term4)),
	(var2,(term4, term2, term5, term5, term0, term5)),
	(var0,(var1, var0)),
	(var3,(term9, term2, term4)),
	(var3,(term8, term4, term3, term2, term5, term8))
],[
	(var2,(term6, term2, term8))
],[
	(var0,(term9, term4, term2)),
	(var2,(term3, term0))
],[
	(var4,(term9, term1, term6)),
	(var2,(var0, var1, term5, term6, term3, var0, term5)),
	(var0,()),
	(var1,(term4, )),
	(var0,(term9, term7, term4, term6, term2, term8, term7)),
	(var4,(term3, term7)),
	(var4,(term2, )),
	(var2,(term6, term5, term5)),
	(var0,(term9, )),
	(var3,(term9, ))
],[
	(var2,(var1, var2)),
	(var2,(term5, )),
	(var1,(term4, term8, term0)),
	(var2,(term0, ))
],[
	(var3,()),
	(var1,(term5, term7, term8, term3, term9, term1)),
	(var2,(term8, term4, term9, term1, term6, term1, term7)),
	(var4,(var2, var4)),
	(var3,(term1, ))
],[
	(var2,(term4, term6, term5)),
	(var0,(term4, var1, term6, var3)),
	(var1,(var3, term1, term6)),
	(var3,()),
	(var0,(var2, )),
	(var3,(var1, var2, term5, term9, var4, var3, term8)),
	(var3,(var0, term3, term1))
],[
	(var2,(term9, )),
	(var1,(term1, term8, term0, term2, term5, term2)),
	(var2,(term5, term7, term1)),
	(var2,(var4, term7, term7, term3)),
	(var3,(term3, var1)),
	(var2,(term0, term1))
],[
	(var0,(term9, ))
],[
	(var3,(term8, term2, term3)),
	(var0,(term5, term6, term3, term0, term2)),
	(var4,(term9, var3)),
	(var4,(term5, term5, term5, term7, term2)),
	(var0,()),
	(var1,()),
	(var1,(var0, var0, var0, term1, term5, var1, var3, term6, term8, term0)),
	(var4,(term7, term8, var3, var0)),
	(var4,())
],[
	(var3,(term0, var0, var0, term3, var4, var1)),
	(var3,()),
	(var1,(var4, var1, var0, var1, term8, term7, term2, term6)),
	(var2,())
],[
	(var3,(var4, var4)),
	(var3,(term8, ))
],[
	(var0,(term8, term9, term8))
],[
	(var3,(term9, term2, term2)),
	(var4,(term1, term4, term2, term3, term8, term6, term5, term3, term0)),
	(var2,(term1, term9)),
	(var1,(term5, term0, term4, term4, term1, term8, term5)),
	(var1,(term9, term8, term0, term0, term7, term1, term8)),
	(var0,(var3, var2, term8)),
	(var2,(term2, term4, term0, term2, term8, term0))
],[
	(var4,()),
	(var2,(term9, term4, term0)),
	(var0,(var4, )),
	(var3,(term4, )),
	(var3,(term4, term2)),
	(var4,(term1, term0, term6)),
	(var4,(term2, ))
],[
	(var0,(term5, term5)),
	(var4,(term2, )),
	(var4,(term2, term5, var1, term7, var1)),
	(var2,(var0, )),
	(var1,(var1, var0)),
	(var0,(term6, term8, term9, term4))
],[
	(var2,(term1, term1)),
	(var3,(var0, term4)),
	(var4,(var4, var2)),
	(var1,(term1, term5)),
	(var1,()),
	(var2,(term9, term1, term1, term4)),
	(var4,()),
	(var1,(term5, term2, term1)),
	(var0,(term7, )),
	(var1,(term9, term7, term7, term5, term7, term2))
],[
	(var4,(term9, )),
	(var0,(term1, term1)),
	(var0,()),
	(var0,(var1, term7, term3)),
	(var3,(term2, term1)),
	(var4,(term5, term3, term3, term7, term1, term0, term9)),
	(var4,(var0, )),
	(var3,(var0, term6)),
	(var3,(term7, ))
],[
	(var4,(var0, var3, term9, var0, var3))
],[
	(var0,(term5, term7, term0)),
	(var3,(term5, term9, term9, term7, term4, term8, term3)),
	(var4,(term8, var2, var2)),
	(var3,(var2, var2)),
	(var0,(var2, term3)),
	(var1,(term7, term6)),
	(var0,(term3, )),
	(var4,(var2, )),
	(var4,(var0, ))
],[
	(var0,(term7, term7)),
	(var2,(var3, var0)),
	(var0,(term4, var4, var4, term6, term3, term1, var4)),
	(var3,(var1, var4)),
	(var1,(term4, term7, term6, term1)),
	(var4,(term6, term9, term7)),
	(var0,(term0, var0, var3, var4, var3, term4, var3)),
	(var1,(var1, term6, var3)),
	(var3,(term4, term0, term6))
],[
	(var2,(term0, term4, term8, term6)),
	(var2,(term3, term9, var4, term5))
],[
	(var4,(term2, term2)),
	(var0,(term2, term3, term2, term5)),
	(var4,(term1, term7)),
	(var0,(var1, term1, var0, var3, var2, term6, var4)),
	(var3,(term2, term0, term8))
],[
	(var3,(var0, )),
	(var2,(term4, term5)),
	(var1,()),
	(var4,(term9, )),
	(var4,(var4, )),
	(var1,()),
	(var2,(term6, term5, term4, var3, var2, term3, var2))
],[
	(var4,(term4, )),
	(var3,(term8, term8, term2)),
	(var3,(term8, term4, term2)),
	(var1,(term2, term0)),
	(var2,(var4, )),
	(var1,(term5, var2, var4, var1, var3, term4, term1)),
	(var0,(term7, ))
],[
	(var3,(term3, term0, var3)),
	(var0,(var1, var0)),
	(var1,(term5, term7, term2)),
	(var4,(term5, term9, term6, term6, term1, term6, term2)),
	(var1,(term0, term4, term5, term2, term4, term0, term5, term0, term0)),
	(var1,())
],[
	(var0,()),
	(var3,(term1, term3, term2)),
	(var2,(term6, )),
	(var3,(term2, term3, term0, term6, term6, term4, term8)),
	(var4,(term4, term7, term2)),
	(var0,(var2, term0)),
	(var3,(term9, var3, var1)),
	(var2,(term5, term5, term4, term7, var3, term7)),
	(var2,(var3, term7, var4))
],[
	(var2,(var2, var0)),
	(var2,(term0, )),
	(var0,(term1, term6, term8)),
	(var2,(var2, term1, term5, var4, var1, var2, var0, term1)),
	(var2,()),
	(var3,()),
	(var1,(term5, term2)),
	(var0,()),
	(var0,(term0, term5, term5, term2)),
	(var4,())
],[
	(var1,(term2, term6)),
	(var1,()),
	(var4,(term3, )),
	(var3,(term6, term7, term3)),
	(var1,(term1, term4, term7)),
	(var2,(var4, var1, term6, var0, term7, var4, var1)),
	(var2,())
],[
	(var2,(term2, term8, term2, term6, term5, term1, term2)),
	(var4,(term3, term0, term2)),
	(var2,(term5, )),
	(var4,(var4, term6, term0, term4, term4, term2, term5, term1, var0, term9)),
	(var2,(term9, term5)),
	(var3,(var3, )),
	(var3,(var4, var3, term2, term9, var1, term7, term5, var3, term2, term2))
],[
	(var0,(var2, var3, term4, term0, term1, term7, var2, term2, var3)),
	(var3,(term1, term2, term4, term2, term2, term9, term8))
],[
	(var2,(var2, term5, term2)),
	(var4,(term2, )),
	(var4,(term3, var4, var4, var3, var1, var0)),
	(var1,(term5, )),
	(var3,(term2, term8, term6))
],[
	(var0,(term3, term9, term5, term3, term8, term1, term0, term1, term1, term2)),
	(var4,(term6, ))
],[
	(var1,(term0, term4, term9, term9, term2, term4, term4)),
	(var0,(var1, ))
],[
	(var4,(term1, var4)),
	(var3,(term4, term4, term4, var2, term0)),
	(var1,(term5, term3, term3, term8, term8, term0)),
	(var0,(term3, term4, term9, term1, var4, term9, var0))
],[
	(var2,(term6, )),
	(var1,(term8, term6)),
	(var1,()),
	(var4,(var1, term2, term8)),
	(var1,(var2, ))
],[
	(var2,(term2, term1, term6, term8)),
	(var2,(term8, term3, term7, term6, term7, term5, term9)),
	(var3,(term7, term5, term7)),
	(var2,(term8, term1, term3, term1, term5)),
	(var4,(var2, term9)),
	(var0,(term3, term3, term4, term6, term2)),
	(var2,(var3, var0, term6, term9, var1, var3, var0))
],[
	(var3,(var4, )),
	(var4,(term5, term7, term2)),
	(var3,(term2, term8, term0, term5, term5, term5, term6, term9)),
	(var4,(term9, term3, term5, term3, term9, term5)),
	(var1,(var1, )),
	(var4,(var1, term6, var4, term6, term7, term0, var4)),
	(var1,(term8, term5, term9, term2, term2, term0, term3)),
	(var3,()),
	(var1,(var3, )),
	(var3,(term4, term5, var1, var1))
],[
	(var2,(term3, var0)),
	(var0,(var3, term5)),
	(var4,(var4, var2))
],[
	(var1,()),
	(var1,(term2, )),
	(var0,(term1, term0, var2)),
	(var0,(term3, term5, term8))
],[
	(var2,(term6, term3, term7, term0, term8)),
	(var2,(term2, term2, var1, var0)),
	(var2,(term5, term2)),
	(var3,(term2, term2)),
	(var4,(term8, term0, term1)),
	(var0,(var0, term9, var2))
],[
	(var1,())
],[
	(var2,(term7, var0, term4, var3, term5)),
	(var4,(term6, term9, term4, term4, term2, term3, term7)),
	(var3,(term6, )),
	(var1,())
],[
	(var3,(term3, )),
	(var1,(var3, var1, var4, term7)),
	(var1,(term8, term9, term4, term0, term2, var3, term4)),
	(var2,(term8, term8, term0)),
	(var3,(var2, )),
	(var0,())
],[
	(var4,(var4, var4))
],[
	(var3,()),
	(var3,(term0, )),
	(var2,(var1, term3, var3, term9)),
	(var2,(term8, term3, term4))
],[
	(var4,()),
	(var2,(term3, term0, term8, term4, term5, term3)),
	(var1,(term6, )),
	(var2,(term4, var3)),
	(var2,(term6, var4, var0, var1, term9, term5, term0, term0, term7)),
	(var3,(var2, )),
	(var3,()),
	(var0,()),
	(var3,()),
	(var4,(term9, ))
],[
	(var0,(term2, var4, var4, term8, term5, term7, var4)),
	(var2,()),
	(var0,(var2, term6, term5, term9, term4, term3, var3)),
	(var4,(term1, )),
	(var0,(term6, term6, term1, term0, term8, term8, term6, term7, term8, term7))
],[
	(var3,(var4, var3, term3, term5)),
	(var2,(term1, term7, term6)),
	(var0,(var1, term2)),
	(var3,()),
	(var2,()),
	(var3,(var1, )),
	(var3,(term5, term6, term8, term1, term7))
],[
	(var2,()),
	(var0,(term6, term0, term5, term6)),
	(var4,(term3, term6)),
	(var2,())
],[
	(var2,()),
	(var1,()),
	(var3,(term4, term1, term5, term3, term8)),
	(var3,(term1, )),
	(var1,(term4, term1, term2, var4, var3, var4, var3)),
	(var4,())
],[
	(var1,(term4, var4, term0, term4, var0, var4, var3, term5, var0)),
	(var4,(term3, term1, term6)),
	(var1,(term2, var3, var0, var0, term6)),
	(var0,(var2, term0)),
	(var4,(var3, )),
	(var0,(term3, var0))
],[
	(var2,(term1, term5)),
	(var0,(term2, var1, var3, var4)),
	(var1,(term0, term7, term7, var0, var4, var0, term8, term8)),
	(var3,(term4, ))
],[
	(var4,(term6, term1, term5, var4)),
	(var4,(term7, term8, term7))
],[
	(var0,()),
	(var2,(term8, term9)),
	(var3,(term7, term3, term4)),
	(var3,(term6, term1, var2, term6, term8)),
	(var2,(var3, var4, var0, term8, term9, var1, var2)),
	(var4,(term9, )),
	(var2,()),
	(var2,(term3, var4, var4, term6, term6, term1))
],[
	(var4,(term2, term4)),
	(var4,())
],[
	(var1,(term8, term1, term7, term9, term9, term8, term2, term2, term6, term8)),
	(var2,(term1, term5)),
	(var4,(term3, term7, term3, term0, term0, term6)),
	(var4,(var4, term6, var2, term3, var1, term5, var3)),
	(var0,()),
	(var3,(term8, term9, term7, term9, term0, term6)),
	(var2,(term3, term5, term1)),
	(var3,()),
	(var4,()),
	(var2,(term9, var2))
],[
	(var2,(term5, term8, term5, term5, term8))
],[
	(var1,(term4, term4, term4, term6, term5))
],[
	(var1,()),
	(var3,(term4, )),
	(var1,(var2, var0, term3, term5, term4)),
	(var3,(term0, term3)),
	(var3,(term9, term8))
],[
	(var4,(var0, )),
	(var0,(var2, )),
	(var3,(var2, term6))
],[
	(var4,()),
	(var4,(term6, term9, term3, term9, term8)),
	(var0,(term3, term9, term6)),
	(var0,(var3, var0, term6, term0, var3, var3, var2, term4, term9, term9))
],[
	(var0,(term6, term2, term8, term8, term1, term3))
],[
	(var4,(var3, term0, var4)),
	(var3,(term4, term2, term7)),
	(var2,(var1, )),
	(var4,(var4, )),
	(var1,(term6, term1, term4, term3, term1, term7, term9, term5, term7, term8))
],[
	(var4,(var1, var0)),
	(var0,(term4, term4)),
	(var2,()),
	(var1,(var2, )),
	(var1,(term8, term0, term4, term8, term4, term5, term6)),
	(var2,(var3, term8, var3, term1, term3, var0, var0)),
	(var4,(term4, )),
	(var3,(var0, )),
	(var1,(term4, )),
	(var4,(var1, var1, term6, term8, term0, term9, var2))
],[
	(var1,(term9, term6))
],[
	(var0,(var0, var3, var1, term7)),
	(var0,()),
	(var0,(term0, term4, var2)),
	(var3,(term2, term4, term4, term3, term3)),
	(var3,(term0, term4, term2, term5, term6, term8, term4)),
	(var4,(var2, term2, var1)),
	(var4,(term1, term9, term6))
],[
	(var4,()),
	(var4,(var2, term7, term2, term9, var3, var4, term9)),
	(var3,(term4, term9)),
	(var1,())
],[
	(var0,(term1, )),
	(var2,(term5, term2, term7)),
	(var0,(var3, )),
	(var2,(var2, term6, term3)),
	(var4,(term0, )),
	(var2,(term2, term9, term8))
],[
	(var3,(var0, term7, term1, var3)),
	(var4,(term6, var3)),
	(var2,(term0, term2, term4, term3)),
	(var0,(term0, )),
	(var2,()),
	(var4,(var1, var2)),
	(var1,(var0, ))
],[
	(var0,()),
	(var2,(term9, )),
	(var2,(term5, term8, term6)),
	(var1,(var3, )),
	(var1,()),
	(var3,())
],[
	(var2,()),
	(var4,(term9, var3, var2, term3, term9)),
	(var1,(term5, term0))
],[
	(var3,(var0, term8, var1, var0, var2, term3)),
	(var2,()),
	(var1,(var1, term8)),
	(var3,(term9, )),
	(var3,()),
	(var1,(term5, term5, term5, term4, term3, term8, term8, term1)),
	(var2,(var3, term9)),
	(var4,(term1, term4, term7)),
	(var4,(var2, term7, term1, term2, term1, term0, var1, var0)),
	(var0,(term1, ))
],[
	(var3,(term1, term7)),
	(var0,()),
	(var0,(term6, term7, term2)),
	(var3,(term2, term7, term5, term7)),
	(var2,(term7, term9, term0, term1)),
	(var2,()),
	(var0,(term9, )),
	(var4,(var3, )),
	(var4,(term7, term0)),
	(var4,(var2, term8, var3, term9, term4, var2, var0, var2, var1, var0))
],[
	(var1,(term7, term9, term3))
],[
	(var2,()),
	(var1,()),
	(var4,(var0, var2)),
	(var4,(term8, term1, var2))
],[
	(var0,()),
	(var4,(term0, term4, term5, term0, term3, term5, term4)),
	(var3,()),
	(var1,(term7, term5, term2, term0)),
	(var1,(var2, term7, term8, term0, var0)),
	(var0,()),
	(var0,(term5, term4)),
	(var0,(term4, term6)),
	(var1,(var0, var3, term3, term8, term7, var3, term7)),
	(var2,(var4, term1, term7, term1, var3, term2, var2, term6, var3, var4))
],[
	(var3,(term4, term7)),
	(var3,(var1, term4, term9, var1, term4, var1, term0)),
	(var0,(term6, term4, term9)),
	(var4,(term5, term0, term2, term7, term2)),
	(var0,(term9, term9, term5)),
	(var0,(term1, term6, term8, term9, term8, term2)),
	(var2,()),
	(var3,()),
	(var0,(term0, term2, term6, term4, term3, term8, term7)),
	(var1,())
],[
	(var3,(term5, term0, term8, term0)),
	(var4,(var0, var4, term5)),
	(var2,(term1, term7, term0, term7)),
	(var1,()),
	(var2,(term2, term6, term4))
],[
	(var1,(var4, )),
	(var0,(term8, )),
	(var1,(term7, term3)),
	(var0,()),
	(var0,(var0, term9, var4)),
	(var0,()),
	(var0,(var4, term1, var3)),
	(var2,()),
	(var1,(term6, var2, term2)),
	(var3,(term5, var1, var4))
],[
	(var0,(term9, term8)),
	(var2,(var0, term9, term5)),
	(var1,(term6, )),
	(var2,(term2, term9)),
	(var1,(term3, ))
],[
	(var3,(var1, term9, term9, term2, term7, term5, var0)),
	(var4,(term2, term8))
],[
	(var2,(term9, )),
	(var3,(term2, term9, term7, term1, term6, term2, term1, term5)),
	(var2,(term7, term5)),
	(var4,(var3, var0, term2, term2, term5, var0)),
	(var0,(term9, )),
	(var1,(term8, term2, term6, term2, term0, term4, term8, term3)),
	(var2,(term1, term1, term2, term3, var1, term1, var4, term9, term5, term3)),
	(var3,(term4, )),
	(var2,(term7, term1, term3)),
	(var0,(term2, term9, term9, term9))
],[
	(var3,(var3, var1, var4)),
	(var4,()),
	(var2,())
],[
	(var1,()),
	(var4,(var3, term7, var1)),
	(var0,(term1, term5)),
	(var2,(term3, term6, term6)),
	(var4,(term4, term9, term2, term4)),
	(var1,()),
	(var3,(var3, term1, var1, term5, term8, term1, var4))
],[
	(var0,(var4, )),
	(var0,()),
	(var0,(term2, term4, term4, term9, term9, term5)),
	(var4,(term0, term5)),
	(var3,(term4, term4, term5)),
	(var0,(var1, )),
	(var3,(var0, var0, term0, term9, var1, var3, term2)),
	(var3,(term2, term3, term1)),
	(var4,()),
	(var2,(var2, ))
],[
	(var0,(term1, term8, term5)),
	(var0,(var3, term0)),
	(var1,(term5, term0, term3, term2, term6, term0, term8)),
	(var2,()),
	(var3,()),
	(var3,(term2, var1)),
	(var3,(term5, )),
	(var2,()),
	(var2,(var3, var3, term2, term6, term0, term6, var4, term3, term1)),
	(var2,(term4, term2, term8, term9, term4))
],[
	(var2,(term0, var4, var1, term1, term8, term4, term6)),
	(var1,()),
	(var3,()),
	(var2,(term4, var0)),
	(var0,(term4, )),
	(var1,(term3, term0, term9)),
	(var4,(var1, var2, term0)),
	(var4,(term9, term9))
],[
	(var4,(term7, term2))
],[
	(var0,(term4, term4, term5)),
	(var2,()),
	(var1,(term0, term6, term4)),
	(var3,(term5, term7, term7)),
	(var1,(term8, var1)),
	(var0,(term7, term3, term7)),
	(var1,(term5, )),
	(var4,(term7, term8)),
	(var0,(term2, term4, var2))
],[
	(var2,(term1, )),
	(var3,(term1, var2, var0, var1, term4)),
	(var1,(var2, term4, term3)),
	(var2,()),
	(var4,(term6, )),
	(var0,()),
	(var2,(term5, term3)),
	(var2,(term8, term5, term3))
],[
	(var0,(term3, term1, term7, term0, term3, term3, term3)),
	(var0,()),
	(var1,(term4, term9, term7, term5))
],[
	(var3,(term5, term2)),
	(var3,(var3, )),
	(var2,()),
	(var2,(term5, term4)),
	(var2,(var0, term5, term0, var3)),
	(var1,(var3, var0)),
	(var2,(term6, term8, var0)),
	(var0,()),
	(var2,(term2, term4, term8, term5))
],[
	(var3,(term6, term1, term9)),
	(var2,(term9, term1)),
	(var4,(term1, term7)),
	(var3,()),
	(var0,(var3, )),
	(var2,(term8, )),
	(var3,(term5, )),
	(var0,(term3, )),
	(var1,(var2, term5))
],[
	(var1,(var4, var1)),
	(var2,(term4, term0, term2, term1, term9)),
	(var4,(term5, )),
	(var3,(term5, term9)),
	(var1,()),
	(var1,(var2, var0)),
	(var1,(term2, term9, term4, term0, term8, term2, term3, term8, term1)),
	(var3,())
],[
	(var0,(term0, term8)),
	(var1,(term3, term8, term5, term2)),
	(var2,(term5, )),
	(var1,(term7, term0, term1, term0, var3, term7, term3, var4, term5, term5)),
	(var1,(term2, )),
	(var4,(var0, ))
],[
	(var4,(term4, ))
],[
	(var1,(var0, term9, var4)),
	(var4,()),
	(var2,(term4, term3, term5, term7, term0, term5, term1, term5, term0)),
	(var1,(var0, term4, term0))
],[
	(var4,(term7, term0, term5, term3, term2, term9, term4)),
	(var2,(var1, term4, var2, term9, term5, term7, term0)),
	(var1,()),
	(var4,()),
	(var4,(term7, term1)),
	(var4,(term8, term0, term5)),
	(var3,()),
	(var3,(var0, )),
	(var1,(var4, term1, term8, term5)),
	(var2,(var2, var3, term9))
],[
	(var3,(term2, term6, term8, term5, term1, term8, term1)),
	(var4,(term9, term1, term4, term9, term1, term2, term4)),
	(var0,(var3, var1, term2, var0)),
	(var2,(term9, term1, term0, term6, term9, term0, term3, term8)),
	(var3,(term3, term9, term5)),
	(var1,(var0, term2, term4, term6, term2, var1, var1)),
	(var0,(term8, term0, term3)),
	(var2,(term6, term7, var0, term9, term1, term1, term7, var3, term1, term4))
],[
	(var4,(var3, ))
],[
	(var1,()),
	(var0,(term8, term5, term2)),
	(var2,(term0, var1, var4, var2, term1, term3)),
	(var3,(term4, term5)),
	(var4,(term3, term9, term7, term3, term2)),
	(var0,(term9, var1)),
	(var1,(term8, term3)),
	(var1,(term7, term0)),
	(var2,(term1, term2, term9))
],[
	(var2,()),
	(var2,(term5, term2, term4)),
	(var3,(term1, term8))
],[
	(var2,(term3, term5))
],[
	(var4,(term3, term4, term8)),
	(var3,(term8, term0)),
	(var3,(term2, term2)),
	(var3,()),
	(var4,()),
	(var4,(term1, term4, term5, term7, term9, term7))
],[
	(var0,(term8, var3, var1, term0, term0, var2, term2)),
	(var4,(term8, term6, var3, var1, term4, var4, term8, term8, var0, var2)),
	(var2,(term1, var0, term8, term7, term9)),
	(var0,(term0, term0, term5)),
	(var0,(var4, var2)),
	(var3,()),
	(var3,(term6, term9, term3))
],[
	(var4,()),
	(var2,(term1, ))
],[
	(var2,(var4, term1, var0)),
	(var2,(term2, term5)),
	(var3,(term1, term3, term8, term0, term8, term8)),
	(var3,(var2, var1, term3, var1, term4)),
	(var4,(term7, term0, term4)),
	(var1,(var0, term3, var3, var0, term9)),
	(var3,(term2, term8)),
	(var0,(term2, term5, term5)),
	(var0,(var1, term4, var4, term5, var0)),
	(var1,(var0, ))
],[
	(var4,(term3, term2, term5)),
	(var1,(var4, term7, var0)),
	(var3,(term1, var4, term0)),
	(var2,(term9, var2, var3)),
	(var2,(var2, var1, var0, term8)),
	(var4,(term3, term4, term6, term3, term4, term7, term3, term2, term4)),
	(var2,())
],[
	(var2,(term8, term7, term7, term4)),
	(var3,(var1, var0)),
	(var3,(term2, term3, term7, term9, term9, term1, term4)),
	(var3,(var2, term5)),
	(var4,(var2, var4, var4)),
	(var1,(term4, term4))
],[
	(var2,(term0, var4, var3)),
	(var2,(term3, term7, term6, term2, term3)),
	(var0,(term7, term7))
],[
	(var0,(term3, term0, term4, term0)),
	(var4,(var0, var0, term6, var2, term8, term1, var3, term7)),
	(var1,(term4, term0, term5, term4, term6, term1)),
	(var0,())
],[
	(var4,()),
	(var4,(var2, term6, term2, term2)),
	(var3,(term1, term8, term8))
],[
	(var3,(term3, term1, term6, term4, term2)),
	(var4,(term2, var4, var0)),
	(var3,(term6, var3, term8, var3, var4, term1, term6, var0, var0)),
	(var2,(term1, term8, var1, var0, term1, var0, term5)),
	(var0,(term9, term4)),
	(var3,(term1, term6, term5)),
	(var4,()),
	(var1,(var2, term3, term5, term9, var2)),
	(var4,(term3, term5, term6, term9, term8, term3))
],[
	(var1,(term2, )),
	(var2,(var3, )),
	(var4,(term4, term8)),
	(var4,()),
	(var2,(var0, )),
	(var2,(var1, var2)),
	(var0,(term0, term4, term3))
],[
	(var3,()),
	(var0,()),
	(var0,(term6, var2, term0, term3, term1, var3, term4, var0, term1, term9)),
	(var2,(term8, term9, var1, term5)),
	(var1,()),
	(var1,(term7, )),
	(var3,(term0, term7)),
	(var0,(term9, term0, term8, term5, term8, term1, term5, term8)),
	(var1,()),
	(var1,(term0, term7, term6))
],[
	(var1,(term9, var1)),
	(var2,()),
	(var0,(var0, )),
	(var3,(var1, )),
	(var3,(term2, term3, term6, term6, term8, term7, term1)),
	(var2,(term7, term8, term2, term1, term8, term7, term9)),
	(var2,(term5, ))
],[
	(var4,(term4, term8, term4, term5, term5, term5, term8))
],[
	(var0,(term0, var1, term5, var1)),
	(var2,(var1, )),
	(var1,()),
	(var0,()),
	(var3,(term5, term3, term0, term3, term1)),
	(var0,(var0, var3, term2)),
	(var1,(var3, )),
	(var1,(term0, var2)),
	(var3,(term0, )),
	(var4,(term8, ))
],[
	(var2,(term8, term0, term5))
],[
	(var2,(term8, term6)),
	(var2,(term7, term5, term0, term1, var3, term8, var2)),
	(var4,(term9, term1, term8, term8, term6)),
	(var2,()),
	(var1,())
],[
	(var4,()),
	(var0,(term8, term6, term5, term0, term5, term4, term4)),
	(var1,()),
	(var0,(term3, term0, term7, term3, term3)),
	(var1,(term8, var4)),
	(var1,(term9, term6, term1, term8, term4, term2, term8, term4)),
	(var0,(var1, )),
	(var4,(var0, term3, var1, var1, var4, term6, term3, term6, term6, var2))
],[
	(var1,(term9, term1, term2)),
	(var3,(term4, )),
	(var1,()),
	(var3,(term1, term6, term3)),
	(var0,(term5, term0)),
	(var0,(term6, term5))
],[
	(var4,(var2, var3)),
	(var1,())
],[
	(var3,(term5, term2, term2, term9)),
	(var0,(var1, term2, var2, term1, term4, term5, var0, var2, term1, term8)),
	(var0,(term3, term5, term9)),
	(var3,(var4, var1, term4, var2, term0, term0)),
	(var2,(term7, term1)),
	(var0,(term4, term5))
],[
	(var2,(var2, term8, var4)),
	(var0,(term2, term1, term5)),
	(var1,(term5, term7, term4, term5, term1)),
	(var0,(var3, var2, var4)),
	(var2,(term1, var1, term4, term0)),
	(var1,(var3, ))
],[
	(var1,()),
	(var0,(term2, term3)),
	(var0,(term2, term7, var0)),
	(var1,())
],[
	(var1,(term1, term5, term9)),
	(var4,(term8, term5, term3)),
	(var3,(term9, var4)),
	(var0,(var1, term0)),
	(var4,(term4, var1)),
	(var1,(term0, term9)),
	(var1,(term8, term6, term4)),
	(var0,(term4, term4, term5, term7, term6, term3, term1))
],[
	(var0,(term7, term1, term2, term7))
],[
	(var0,(term1, term9, term7)),
	(var1,()),
	(var2,(term4, term8))
],[
	(var2,(term9, term8, term2)),
	(var4,()),
	(var4,(var3, term1, term2)),
	(var1,(term5, term5, var1)),
	(var2,(term2, var2))
],[
	(var3,(term6, var0, term4, var1)),
	(var3,(term6, term6, term8, term9, term4, term9, term3)),
	(var2,(term0, var4, term0, var2, var3, term6)),
	(var4,(term0, term6, term2)),
	(var1,(term5, ))
],[
	(var0,(term4, term5, term5)),
	(var0,(term9, )),
	(var3,()),
	(var2,(term6, term7, term3, term3)),
	(var1,()),
	(var1,(term5, ))
],[
	(var2,(term1, var4, term6, term9, term4)),
	(var2,(term9, var4, var0))
],[
	(var0,(term6, var1)),
	(var4,(term8, term5, term7, term5, term5)),
	(var4,(term9, term8, term1, term6, term0, term7, term4)),
	(var3,(term5, )),
	(var0,(term2, term8, term6, term7, term5, term1, term4)),
	(var1,(term4, term6)),
	(var0,(term2, var3, term4, term5, var1, term5, var0))
],[
	(var0,(var1, var1, var3)),
	(var3,(term6, term8)),
	(var4,(term5, term9, term5, term8, term9, term3, term1, term0)),
	(var2,(var4, )),
	(var2,(term3, term3, term9, term0, term5, term8, term5)),
	(var3,(var3, term7))
],[
	(var4,(term7, )),
	(var1,(term8, term4, term7, term2, term5)),
	(var0,(term4, )),
	(var1,(term4, )),
	(var0,(term3, term8)),
	(var4,(term1, term9)),
	(var4,(term7, term7, term5, term4, term1, term9, term7, term7)),
	(var1,(term3, term3, term2, term3, term5, term3, term3)),
	(var0,(term1, term1, term0, term1, term4))
],[
	(var1,())
],[
	(var0,(term6, var3, term6, term5, term4, term0, var2)),
	(var2,(var1, var3, term3)),
	(var3,()),
	(var4,()),
	(var4,(var3, term7)),
	(var1,(term8, term1, term4, term0, term8, term7)),
	(var3,(term1, )),
	(var0,(term8, var0, term4, var0)),
	(var0,(var2, var0))
],[
	(var3,(term5, var4, term5, term9)),
	(var2,(term4, term6, term8, term9, term0, term7)),
	(var0,(term2, var3, var4, term8, var3, term0))
],[
	(var0,())
],[
	(var3,())
],[
	(var1,(term3, term1, term1, term0, term6, term0)),
	(var0,(term3, term3)),
	(var1,(term8, term9, term7, term8, term0, term4, term8)),
	(var2,(term4, term1, term4, var4, var4, var0)),
	(var1,(term8, var4)),
	(var2,()),
	(var1,(term5, term8, term3)),
	(var4,()),
	(var4,(term5, term3, term9, term0, term3, term0))
],[
	(var0,()),
	(var3,(term6, var1, var4, term3, term9)),
	(var3,(term1, )),
	(var0,(term7, var1)),
	(var0,(term1, term3, term0, term4, term4, term1, term2, term5, term8, term8))
],[
	(var1,(term7, term6)),
	(var0,(term2, term5))
],[
	(var4,()),
	(var4,(term6, term1, term4)),
	(var1,(term7, term0)),
	(var1,(term8, term4, term9, term2, term9)),
	(var3,(term5, term5, term3, var2, term0)),
	(var1,(var4, var2, term8)),
	(var0,(term2, term6, term5, term5, term2, term7, term8))
],[
	(var4,(term0, )),
	(var2,(term3, term2)),
	(var0,()),
	(var4,(term4, term4, term5, term0)),
	(var2,(term5, )),
	(var4,(term7, term6, term4, term7, term3, term9, term1))
],[
	(var3,()),
	(var1,(term9, )),
	(var1,(term1, term2)),
	(var4,(var0, term6, term0, term8, var0))
],[
	(var4,(var2, var1, var2, term7, term3)),
	(var4,(term7, )),
	(var1,(var0, var2, var4, term9, var2, term9)),
	(var3,(term3, term5)),
	(var4,(var2, )),
	(var3,(term4, term3, term4, term9, term6)),
	(var1,(var2, )),
	(var2,()),
	(var1,(term4, term8)),
	(var2,())
],[
	(var1,(term5, term2, term3, term7)),
	(var4,()),
	(var2,(term8, )),
	(var3,(var0, var2))
],[
	(var2,(term7, ))
],[
	(var3,()),
	(var3,(term2, term4, term3, term5, term0)),
	(var1,(term6, term1, term9, term0, term7, term5, term4, term5, term9)),
	(var3,(term6, term6)),
	(var4,(term3, term8, term8, term5)),
	(var4,(var0, )),
	(var3,(term6, term0, term3)),
	(var2,(var1, term6, term2, var4, term9, term2)),
	(var3,())
],[
	(var1,(term6, term4, term1)),
	(var1,(var4, term5, term4, term3, var3, var2))
],[
	(var4,()),
	(var3,(var2, term1, term7)),
	(var1,(term3, term0, term4, term0, term8, term2)),
	(var0,(term9, )),
	(var1,()),
	(var1,(term7, )),
	(var4,(term0, term7)),
	(var0,(term6, )),
	(var1,(term1, term3, term0, term2, term2, term0, term5))
],[
	(var2,()),
	(var2,(term3, ))
],[
	(var4,()),
	(var0,(term3, term2)),
	(var1,(var3, )),
	(var1,(term0, term4, term1)),
	(var1,(term5, term2)),
	(var3,(term1, )),
	(var1,()),
	(var0,(term3, term8, var4))
],[
	(var2,(term2, term1))
],[
	(var1,(term8, term8)),
	(var0,(term1, term2, term3))
],[
	(var0,(term9, term5, term6, term4)),
	(var0,(term1, term1, term9, term2)),
	(var0,(term3, var1)),
	(var1,(term0, term4, term3, term7, term1, term8, term3)),
	(var1,()),
	(var4,(term6, term3, term1, term1, term2, term0)),
	(var1,(var4, var0)),
	(var4,())
],[
	(var0,(term3, term5, term3, var2, term6, term2, term7)),
	(var0,(term9, term2, term1, term2)),
	(var4,())
],[
	(var1,()),
	(var0,(term2, term6, term0)),
	(var3,(term8, )),
	(var4,(term8, term1, term2, term7, term7, term2, term2, term1, term6)),
	(var0,(term8, var1, var2))
],[
	(var1,(term4, term5))
],[
	(var1,(term1, term4, term5)),
	(var3,(var4, )),
	(var3,(term2, term6)),
	(var2,(term2, )),
	(var3,(term5, term8, term3, term6, term3, term4)),
	(var3,(var4, term2))
],[
	(var2,()),
	(var4,(term2, term5, term6, term0)),
	(var1,(var1, )),
	(var4,(term8, term8)),
	(var1,(var2, )),
	(var1,(var4, var2)),
	(var1,(term8, term3))
],[
	(var1,(term6, term5, term9, term3, term4)),
	(var0,(term7, term6))
],[
	(var0,()),
	(var3,(term7, term3, term8, var4, var1)),
	(var4,(term2, term9, term2, term6))
],[
	(var2,(var0, )),
	(var3,()),
	(var2,(term2, term0, term4)),
	(var0,(var2, var0, term1, var4, term5, var2, var3)),
	(var0,())
],[
	(var3,(term9, var0, var3, var2, term0, term3, term8, var0, term7, var4)),
	(var0,(term3, )),
	(var4,(term0, )),
	(var2,(term8, var4, term2)),
	(var4,()),
	(var2,(var4, var1, term3, term4, term1, var4)),
	(var2,()),
	(var4,(term0, term0, term4, term4, term7, term8)),
	(var4,(var3, var0)),
	(var1,(term8, term9, term0, term5, term7, term2, term2))
],[
	(var4,(var3, )),
	(var2,(term9, var2, term0, term0))
],[
	(var4,())
],[
	(var0,()),
	(var0,(term6, term1, term3, term6, term0, term6)),
	(var1,(var1, )),
	(var4,(term2, term6, term8))
],[
	(var3,()),
	(var3,(term1, term2, term4)),
	(var1,(term7, term9, term3)),
	(var4,(term1, term6, term6)),
	(var4,(term8, term7, term0, term6, term0)),
	(var1,())
],[
	(var3,(term1, )),
	(var1,()),
	(var2,(term2, var0)),
	(var4,()),
	(var4,(term3, )),
	(var1,(term7, term6, term9)),
	(var0,(term6, var4)),
	(var0,(term9, term4, term3, term2, term7, term6, term4))
],[
	(var1,(term0, )),
	(var4,(term0, term4, term2, term3, term3, term3)),
	(var3,(term2, term5, term9))
],[
	(var0,()),
	(var4,(term2, term6, term9, term6, term2, term4)),
	(var0,())
],[
	(var4,(var4, term6)),
	(var1,(term3, term8, term9, term1, term8, term6, term6, term5, term3)),
	(var3,(term1, term6, var2))
],[
	(var4,()),
	(var4,(var2, var3, var0, var1)),
	(var2,(term0, term8, term3, term5, term6)),
	(var1,(term5, term0, term8, term2, term8, term9, term1)),
	(var4,(var0, var4)),
	(var3,()),
	(var1,(var4, term2, var4, term7, term8)),
	(var4,()),
	(var0,(term3, )),
	(var4,(term3, term8, term2, term4, term1, term8, term8))
],[
	(var0,(term1, )),
	(var1,(term1, term4, term6, term5)),
	(var0,()),
	(var4,()),
	(var4,(term4, term0, term8, term1, term4)),
	(var4,(var3, )),
	(var0,(term8, term4, term5, term6, term6, term1)),
	(var4,(term3, term6, term3)),
	(var0,(term1, ))
],[
	(var4,(term3, term9, term6, term5, term3, term5, term1)),
	(var1,(var0, )),
	(var4,(term8, term9, term0, term8, term3, term1)),
	(var1,(term0, term6, term2, term1, term9, term8, term3)),
	(var4,()),
	(var1,(var2, var4, term0))
],[
	(var1,()),
	(var0,(term4, )),
	(var3,(term5, )),
	(var3,(term3, term2)),
	(var3,(var2, var2, term4)),
	(var0,(term9, )),
	(var3,(term4, term1, term2, term4, term4, term7, term8, term7, term7, term9))
],[
	(var3,(term9, )),
	(var0,()),
	(var3,())
],[
	(var0,(term7, term5, var2, var1, term2, var3, term3)),
	(var4,(var4, var3, var2, term0))
],[
	(var1,(term9, term6, term9, term9, term1, term9, term4, term9))
],[
	(var3,(var1, )),
	(var1,(term0, term4, var1, var3)),
	(var3,(var2, ))
],[
	(var4,(term5, term7, term6, term2, term5, term9, term6)),
	(var2,(var3, var2, term3)),
	(var0,(term4, )),
	(var3,(term8, term3)),
	(var3,(term6, term6, term9, term4, term3, term0, term6)),
	(var4,(term5, term2, term0)),
	(var4,()),
	(var2,())
],[
	(var2,(var3, var2)),
	(var1,()),
	(var3,(term6, term9, term7, term8, term4, term0, term8)),
	(var3,(term0, term5)),
	(var3,(term5, term3, term5, term5, term2, term7, term8)),
	(var3,(term7, )),
	(var1,(var1, )),
	(var1,(var1, )),
	(var1,(var3, term6)),
	(var4,(term5, ))
],[
	(var2,(term9, term4, term6, term9)),
	(var4,(term3, term1, term5, var0, var3)),
	(var1,(var0, )),
	(var1,()),
	(var4,(var2, term2))
],[
	(var2,(term7, var0, term9, var4, term8)),
	(var3,()),
	(var0,(term6, term8, term5, var1, term9, term1, term3, var0)),
	(var4,(term4, term1, term5)),
	(var1,(term1, term8, term5, term4, term0, term7, term2)),
	(var0,(term1, var2)),
	(var1,(term6, var1, term0)),
	(var4,(term9, term3)),
	(var1,(var4, ))
],[
	(var3,(var2, var2)),
	(var0,(term7, term0, term5, term0, term4, term2, term4, term9)),
	(var1,(term9, )),
	(var0,(term4, term2, term0)),
	(var3,(term4, term5, var2, term2, term6, term1)),
	(var0,(term0, term9, term6, term6, term9, term9)),
	(var0,(term2, term5))
],[
	(var4,(term1, term6)),
	(var0,(var1, )),
	(var2,(term0, term7, term7, term8, term8)),
	(var2,()),
	(var0,(term4, term7, term9, term5)),
	(var0,(term3, term2)),
	(var0,(term9, term9, term6))
],[
	(var2,(term8, term3)),
	(var0,(term6, term3, term7, term9, term9, term4, term4)),
	(var0,(term1, term4, var4))
],[
	(var4,(var2, var4)),
	(var3,(var4, var0, term9)),
	(var0,(term4, var3))
],[
	(var4,()),
	(var2,(var4, var1, term0)),
	(var4,(term7, term2, term9, term5, term7)),
	(var0,(term3, ))
],[
	(var1,(term5, term3, term5)),
	(var3,(term0, term3, term2)),
	(var1,()),
	(var2,(var4, term3, term6, var4)),
	(var2,(term7, ))
],[
	(var1,(term3, term3)),
	(var4,(term7, var2, var2, term0, var3, var3)),
	(var4,(term9, term2, term2)),
	(var0,(var3, )),
	(var0,()),
	(var1,(term6, term9, term4)),
	(var2,())
],[
	(var4,(var0, )),
	(var1,(term1, term1))
],[
	(var0,(var1, var1, term4))
],[
	(var3,()),
	(var3,(var1, var0)),
	(var4,(term7, term3, term8, term4, term5, term0, term5)),
	(var2,(term9, term3, term9)),
	(var4,(var3, )),
	(var0,(var3, term0, var4, var3, term3, var1, var0)),
	(var4,()),
	(var1,(var4, var0, var0)),
	(var0,(term4, term2))
],[
	(var4,(term3, term2, term1, term0)),
	(var0,(term0, term6, term1, term6, term1, term5)),
	(var0,(term9, var2, var1, term9, term8)),
	(var1,(term9, term4, term3)),
	(var0,(var3, term6, term0)),
	(var0,()),
	(var4,(term7, term1, term4, term2)),
	(var4,(term2, term9, term4)),
	(var0,(term4, ))
],[
	(var2,(term1, term2, term4, var4, var2)),
	(var0,(var0, var0)),
	(var0,())
],[
	(var3,()),
	(var4,(term2, )),
	(var1,(term2, term0, term3, var3, var3, term8)),
	(var3,(term1, var2, var1)),
	(var3,()),
	(var1,(term8, term3)),
	(var3,(term0, )),
	(var2,(term8, term9, term1, term6, term1, term2, term2)),
	(var1,(var4, )),
	(var4,(var2, ))
],[
	(var3,(term4, )),
	(var0,(term6, term6, term5)),
	(var2,()),
	(var0,(term1, term1, term4))
],[
	(var2,(term4, term1)),
	(var0,(var4, term3, term1, term5, var0, var0, term1)),
	(var2,(var1, )),
	(var2,(term4, term5, term0, term2, term1)),
	(var0,(var1, )),
	(var2,(term3, )),
	(var2,(var3, var3, var0))
],[
	(var0,()),
	(var1,(term9, term6, term8, term1, term3, term2, term1))
],[
	(var0,(term5, term7, term4, term3, term8, term7)),
	(var0,(var4, )),
	(var4,(term8, term0, term7, term1, term3, term8, term3, term6, term4, term5)),
	(var0,())
],[
	(var0,(term0, )),
	(var3,(term2, term7, term0, term7))
],[
	(var3,(term6, term1, term6)),
	(var4,(term0, var3)),
	(var2,(var3, term7)),
	(var3,(term8, )),
	(var0,(var1, term7)),
	(var4,(term4, term9, term6, term8, term1, term7))
],[
	(var0,(term3, )),
	(var2,(term4, term5, term9)),
	(var4,(var2, term5)),
	(var0,()),
	(var0,()),
	(var0,(term6, term4, term7, term1, term0, term1, term7)),
	(var3,(term8, term9)),
	(var2,(term7, )),
	(var2,(term0, term6, term2))
],[
	(var2,(term8, )),
	(var1,(term3, term3)),
	(var2,(term2, )),
	(var4,()),
	(var3,(term8, term5)),
	(var2,(term4, term2, term8, term8, term1)),
	(var3,(term4, term3, term0)),
	(var3,(term1, term5, term8)),
	(var3,(var2, )),
	(var1,(var4, term0, var4, term2, term2, term5))
],[
	(var4,()),
	(var2,(term8, term3, term4)),
	(var4,(term0, term3, term1)),
	(var1,()),
	(var2,()),
	(var0,(term3, term8, term5)),
	(var3,(term1, var4, var0)),
	(var3,(term8, term4, var2, var2, var4))
],[
	(var2,(term5, )),
	(var2,(term5, term6)),
	(var4,(term2, term5, term3, term1))
],[
	(var3,()),
	(var2,(var2, term6, term6, term9)),
	(var2,()),
	(var2,(term3, term7, term5, term8, term0, term5)),
	(var2,(term1, term5))
],[
	(var4,(term1, term7, term3))
],[
	(var4,(var0, ))
],[
	(var0,(term4, term1, term0, term3, term3)),
	(var2,(term8, term0, term3, term0, term0)),
	(var2,(var0, term1)),
	(var3,(term9, term7)),
	(var4,(term0, term7)),
	(var3,(var3, term2, var2, term7)),
	(var2,()),
	(var4,(term1, term8, term1, term8, term8, term8, var3, term4)),
	(var1,(var4, term4, term0, var3, term7, var1, term9, term8, term7, var4)),
	(var4,(var0, ))
],[
	(var2,(var4, term2, var2)),
	(var0,(term9, term4, var4)),
	(var2,(term1, term3)),
	(var0,(var3, term6, term0, term2, term0, term0, term9)),
	(var2,()),
	(var3,(term2, term5, term5)),
	(var0,(term3, var0)),
	(var3,(term2, term8, term0, term1, term5)),
	(var2,(var0, term6, var4, var3, term1, term7, var3, term3, term0))
],[
	(var4,(term2, term9, term7, term4, term1, term3)),
	(var3,(term0, term4, term9, term8, term8, term7, term1)),
	(var3,(term2, term3, term8)),
	(var3,(var4, )),
	(var3,(term0, )),
	(var3,()),
	(var2,(term4, ))
],[
	(var4,(term3, var1, var2, var2, term2)),
	(var4,(term1, term3, term2)),
	(var2,()),
	(var3,(term0, var0)),
	(var3,(term1, term1, term8, term5, term0, term3, term8, term0, term8, term6)),
	(var4,(var3, )),
	(var4,(term0, )),
	(var0,(term2, term7, term2))
],[
	(var1,(var4, term0, term0, var1, term1, term7)),
	(var4,(term4, term1, term7, term8, var0, term7, term1, term0)),
	(var0,()),
	(var0,(term4, term3, term7, term2, term4, term3, term5)),
	(var1,(term5, term8, var4)),
	(var3,()),
	(var4,(term0, var4))
],[
	(var0,(term0, )),
	(var0,(var3, term2, var1)),
	(var1,(term7, )),
	(var3,(term3, term9))
],[
	(var0,(term0, term6, term1, term0, term7, term0, term5)),
	(var0,(var0, term2, var0, term0, term8, term9))
],[
	(var4,()),
	(var4,(term2, term9, term3)),
	(var3,(term5, term5)),
	(var2,(term5, term5, term3, term5, term4, term7))
],[
	(var2,()),
	(var2,(term3, term1, term9, term3, term0)),
	(var0,(term7, term8, term4)),
	(var2,(term7, term2)),
	(var4,(var2, term7, term0, term8)),
	(var1,()),
	(var2,(term7, term5, term8)),
	(var2,(term8, term1, term7)),
	(var4,(term8, var4, term8, var4, var1)),
	(var2,(var4, var1, var1, var4, term9, term8))
],[
	(var2,())
],[
	(var0,(var3, term4)),
	(var4,(term5, term0, term2, term7, term6, term4)),
	(var1,()),
	(var1,()),
	(var0,(var1, term6, term6, term4))
],[
	(var0,(var1, var2, term4, term5))
],[
	(var1,(term6, var2)),
	(var4,()),
	(var4,(term3, )),
	(var2,(term4, term8)),
	(var2,(term3, term6)),
	(var1,(var3, var1, term0, var4)),
	(var0,(var3, term1, term5, term9, var2, var2, var0)),
	(var0,(term4, var3)),
	(var2,(term3, term9, term6, term4, term1, term5, term8, term9, term7)),
	(var0,(var2, var1, term1, term7, var4, term2, var2))
],[
	(var1,(term5, term3)),
	(var3,(term4, term7)),
	(var4,(term7, var4, var2, term1)),
	(var3,(term9, var4)),
	(var4,()),
	(var4,(var4, )),
	(var2,(term8, term9, term6, term8, term1, term8))
],[
	(var0,(term6, )),
	(var3,()),
	(var1,(term7, term1, term3, term9, term9, term0, term1)),
	(var0,(term7, var1, term9, var3)),
	(var0,(term1, term3, term8)),
	(var4,(term9, term1, term9)),
	(var2,(term6, var0, term2)),
	(var3,(term9, term0, term4)),
	(var4,(term0, term3, term9)),
	(var4,(var2, term3, term6, var0, var2, var3, term4, term1, var2, term4))
],[
	(var3,()),
	(var0,(term1, term0, term6)),
	(var1,(term6, term7, term7)),
	(var4,(term4, term3)),
	(var4,()),
	(var1,(var0, term8)),
	(var2,(var2, term9, term1, term7, term9, term5))
],[
	(var0,())
],[
	(var4,(var2, )),
	(var3,(term7, term2)),
	(var2,(var0, term9)),
	(var2,(term4, term9, var1)),
	(var3,(term3, )),
	(var3,(var2, term1, term4)),
	(var0,(term5, var1)),
	(var2,(term0, term6, term3, term7, term3, term6)),
	(var4,(term5, var3, term0, term3, var0, term5, var3)),
	(var4,(term6, term6, term4, term4, term9, term3, var1))
],[
	(var0,(var1, var3)),
	(var2,(var0, ))
],[
	(var0,(term1, )),
	(var0,(var1, var4))
],[
	(var0,()),
	(var4,(term1, term5, term8, term4, term7, term5, term0)),
	(var3,(var0, )),
	(var0,(term3, term0, term7)),
	(var1,()),
	(var3,(term6, term0, term7)),
	(var1,(var0, )),
	(var0,(term2, )),
	(var1,())
],[
	(var1,(term6, term5, term9, term4, term0, term9)),
	(var4,(var4, var4, term3)),
	(var1,(var0, )),
	(var1,()),
	(var0,(term4, term0, term1, term7)),
	(var3,(term6, term9, var3, term1, var3, term4, term5, term9, term1)),
	(var0,(term3, ))
],[
	(var1,(term8, term0)),
	(var0,(term5, term3, term1, term4)),
	(var0,(term5, term4, term0)),
	(var1,(var1, var3, term5, term0)),
	(var3,())
],[
	(var3,(var4, var0, term6))
],[
	(var4,(var1, var3, var1, term1, term2, var3, var3)),
	(var1,(term4, term0, term8, term6, term8)),
	(var0,(term5, term6, term2, term4, term0, term9, term0)),
	(var1,()),
	(var0,()),
	(var4,(term3, term0, term1)),
	(var3,(term5, term5, term4)),
	(var3,(term5, term0, term1, term8, term5))
],[
	(var3,(var3, var0)),
	(var4,(term6, var3, var2, term0, term7))
],[
	(var4,(var3, term9, term9, term7, var2, term4, var4, term1, term3, var1))
],[
	(var1,(term0, term2))
],[
	(var1,(var2, var0, term1, term1, term6, var4, var0)),
	(var0,(var1, var4)),
	(var2,(var3, term6))
],[
	(var1,(term7, term9, term4, term9, term6, term8, term6, term8, term1)),
	(var1,(term9, term9, term5)),
	(var1,(term7, term6, term5)),
	(var2,(term7, var1, term1, term6, var2, var4)),
	(var0,(var4, )),
	(var3,(term2, term1, term6))
],[
	(var2,(term7, term6, term5, term6, term6, term4, term5, term7)),
	(var2,()),
	(var2,(var3, )),
	(var3,(term8, )),
	(var2,()),
	(var2,(term0, term7, term2, var3, var4, term0)),
	(var2,(var4, var1, term4, var4)),
	(var0,(term0, term8, term6, term7))
],[
	(var2,(term8, term8, term8, term3, term0)),
	(var3,(var2, )),
	(var3,(var0, )),
	(var0,(term4, term2, term9))
],[
	(var2,(term1, var2)),
	(var0,(term1, term1, term8, term5, term7, term4, term8)),
	(var2,(var3, var3))
],[
	(var1,(term7, term9))
],[
	(var3,(var3, ))
],[
	(var1,()),
	(var0,()),
	(var3,(term7, term4, term7, term5, term7, term3, term2)),
	(var2,(term8, term2)),
	(var4,(var4, var3, var1)),
	(var1,(term5, term9)),
	(var2,(term6, )),
	(var3,(term5, term7, term9, term3, term2, term8, term0)),
	(var1,(var4, ))
],[
	(var4,(term0, term8, term0, term6, term1, term2, term4)),
	(var2,(var3, var1)),
	(var4,(term2, term0, term3, term2)),
	(var4,(var2, )),
	(var1,(var3, term2, term1, term9, term6, var2, term6)),
	(var3,(var2, term0, var4))
],[
	(var4,(term4, var1, var0)),
	(var2,()),
	(var1,(term3, term9, term7, term6, term5, term8, term6, term7, term5, term6)),
	(var4,(term4, var4))
],[
	(var3,(term3, term0)),
	(var2,(var0, term2, var2, term2, term8, var4)),
	(var3,(term0, ))
],[
	(var1,(var3, term0, term3)),
	(var4,(term1, term3, term3, term8, term0, term0, term9)),
	(var3,(term7, )),
	(var3,(term4, term8, term5, term0, term9, term0, term1)),
	(var0,()),
	(var3,(term3, term8, term9, term2)),
	(var0,(term6, term6, var0, term0, var1, var3))
],[
	(var3,(var0, var0, var0)),
	(var1,(var4, term9, var2)),
	(var4,()),
	(var2,(term9, )),
	(var3,(term4, term9)),
	(var1,(term7, )),
	(var1,(var3, var0))
],[
	(var1,(term8, term7, term5)),
	(var2,(var4, term7, var0, var2, var2, term0, term3)),
	(var2,(var2, term7, var1))
],[
	(var4,()),
	(var1,(term3, term0, term0)),
	(var2,()),
	(var4,()),
	(var3,()),
	(var2,(term3, term5, term1)),
	(var0,(term4, term3)),
	(var3,())
],[
	(var3,(term0, term2, term7, term6, term1, term3)),
	(var2,(var1, term8)),
	(var4,(var4, var0)),
	(var0,(term6, term0))
],[
	(var4,(term9, term7, term2, term8)),
	(var4,(var0, term4, term1, var3, var0, var0))
],[
	(var0,(term1, term8, term4, term4, term4, term6, term5, term2, term8, term1)),
	(var3,(var0, )),
	(var3,(term0, term5, term5)),
	(var1,()),
	(var3,(var4, )),
	(var2,(term8, term4, term3, term6)),
	(var2,(term3, term8, term5)),
	(var4,(var1, )),
	(var0,(term4, term2)),
	(var3,(term1, var1, term1))
],[
	(var4,(term9, term3, term4, term7, var2, var1)),
	(var2,(term2, )),
	(var2,(term0, term6)),
	(var1,(var0, )),
	(var0,()),
	(var2,(term3, var1, term8)),
	(var3,(term5, term5, var4)),
	(var0,()),
	(var4,(term9, term4, term9)),
	(var4,(term8, var0))
],[
	(var3,(var4, var1)),
	(var3,(term7, ))
],[
	(var1,(term0, var2, term1, term1, term8, term7)),
	(var4,(term6, term3)),
	(var2,(term0, )),
	(var2,(term7, )),
	(var4,(var1, term4, var4)),
	(var2,(term3, ))
],[
	(var0,()),
	(var1,()),
	(var2,()),
	(var3,()),
	(var4,(term7, term3, term9)),
	(var0,()),
	(var3,(term8, term8)),
	(var4,(var4, var0))
],[
	(var0,(term6, term6, term3)),
	(var4,(term5, term1, term6, term9, term9, term1, term3)),
	(var2,(term9, term5, term3))
],[
	(var0,(term7, term5, term9))
],[
	(var0,(term2, var3, term8, var0, term4)),
	(var0,(term8, term8, term5, var0, var0, term5)),
	(var1,(term6, var1, term1, term3, term4, var3, var2, term8, var2))
],[
	(var0,(term4, term6, term5, term7, term3, term8)),
	(var2,()),
	(var4,(term7, term6, var4, term2, var0, var0, term8)),
	(var0,(var4, )),
	(var2,(term6, term8, term5)),
	(var2,(term4, var2, var3, var1, var0))
],[
	(var1,()),
	(var3,(term1, term1, term3, term3, term7)),
	(var4,(var4, var4, var0)),
	(var3,(var1, term0))
],[
	(var1,(term4, term5, term3, term2))
],[
	(var4,(var0, var1))
],[
	(var4,(term2, term8, term7, term0, term0, term4, term8, term5, term9, term8)),
	(var2,(term2, term3, term0, term0, term2, term0, term3, term0))
],[
	(var1,(var0, var2, term8, term7)),
	(var0,(term6, term6, term8, term5, term1, term4, term7, term4)),
	(var1,()),
	(var4,(term6, term0)),
	(var1,(var3, term7)),
	(var2,(term4, term7, term0, term3, term3)),
	(var0,(term8, var1))
],[
	(var0,()),
	(var0,(term1, term9, term3)),
	(var0,(term7, term2)),
	(var3,(var4, )),
	(var3,(var3, term2))
],[
	(var2,(term2, term5)),
	(var3,(term1, term5, term1)),
	(var0,(term2, var1, var2, var1)),
	(var1,(term1, term6, term0, term0, term6)),
	(var4,()),
	(var4,(var3, var1, term7, var4, var2)),
	(var3,(term8, var4, var1))
],[
	(var4,(term5, )),
	(var4,(term4, term7, term3, term8, term6)),
	(var3,(term3, term4, term5))
],[
	(var3,(var4, var1)),
	(var1,(term8, term3, var4, term6, var4, term3, var0)),
	(var3,(term7, var2, term6, var2, term6)),
	(var1,(term5, )),
	(var3,(var4, term7, term2)),
	(var1,(var2, term9))
],[
	(var3,(term8, term9)),
	(var0,()),
	(var0,(term6, term9, var1)),
	(var3,(term8, term0)),
	(var1,(var0, term7, term0, term4, var4)),
	(var4,(var3, var1, term1)),
	(var0,()),
	(var0,(term9, term6, term5))
],[
	(var1,(term6, term9)),
	(var3,(var0, term1, term4, var1, term1)),
	(var2,()),
	(var1,()),
	(var3,(term4, term7, term2, term4, term4)),
	(var0,()),
	(var4,(var3, term3))
],[
	(var1,(var1, var4, term0, var0, var4)),
	(var2,(term9, term3, term5, term4)),
	(var2,(term6, term1)),
	(var1,()),
	(var3,(var1, term4, var3))
],[
	(var4,(term7, var0)),
	(var3,(term3, var3, var2)),
	(var3,(term8, term6, term6)),
	(var0,(term3, term9, term9, term3))
],[
	(var3,(term8, term1, var0, var2, term1, term2, term2)),
	(var0,(term5, term1)),
	(var1,(var0, term1, var1, var3, var0, var4)),
	(var4,(var4, )),
	(var0,(var0, term0)),
	(var1,()),
	(var4,(term9, term2, term4, term7, term7, term5, term1)),
	(var2,(term5, term1, term4, term8, term2))
],[
	(var4,(var4, )),
	(var4,(var0, term5, var1)),
	(var0,(term7, term0, term1, term8, term0))
],[
	(var3,(term9, term6, term4)),
	(var3,(term5, var0, var1)),
	(var2,(term6, term3, term8, term1, term1, term3, term4)),
	(var3,()),
	(var1,(term4, term8, term2)),
	(var0,()),
	(var3,(term4, term0, term8, term1, term1, term1, var2)),
	(var0,()),
	(var1,(var3, var1, term0, term7, term0, term3, term3, term1)),
	(var0,())
],[
	(var2,(term8, var2)),
	(var0,(term9, )),
	(var0,(term4, term8, term5, term1)),
	(var1,(term6, term4, term2, term6, term7, term9, term4)),
	(var4,(term4, term1, term4, term3, term1, term6)),
	(var1,(term4, term6)),
	(var3,(term1, term6, var2)),
	(var2,()),
	(var0,(var3, term4)),
	(var2,(term9, term1, term6, var2, term7, term9))
],[
	(var2,()),
	(var4,(term8, term2)),
	(var3,()),
	(var0,(term7, term6, term7, var3, term9)),
	(var4,(term2, term6, term3)),
	(var1,(term7, term3, term6, term5, term0)),
	(var2,(term5, term1))
],[
	(var4,(term0, term8, term7, term5, term9, term9)),
	(var0,(term8, term2, term3)),
	(var3,(term7, term4)),
	(var0,(term7, )),
	(var4,()),
	(var3,(term5, )),
	(var4,(term4, term6, term3, term6))
],[
	(var2,()),
	(var3,()),
	(var1,(term2, term7, term3, term9, term6, term9, term7, term4, term1, term7)),
	(var3,(var0, term1)),
	(var4,(term3, term9, term5)),
	(var1,(var1, var2))
],[
	(var1,(term0, term9, term3, term2, term0, term7)),
	(var4,(term7, term1, term7)),
	(var1,()),
	(var3,(term1, term1, term3, term2, term2)),
	(var2,()),
	(var1,(term9, )),
	(var3,(term5, term2))
],[
	(var3,(var0, var2, var2, term1, var1))
],[
	(var3,(term6, )),
	(var0,(term4, term3, term2, term5, term2, term7, term7, term6)),
	(var3,(term9, term1, term4, term8, term1))
],[
	(var2,(var3, term0)),
	(var3,(var2, term3, term8)),
	(var0,()),
	(var2,(term7, term1)),
	(var2,(var1, )),
	(var1,(term2, term8)),
	(var4,(var3, term1, term6, term2, var2, term6, term6, term5)),
	(var1,(var1, ))
],[
	(var0,(term9, var0)),
	(var3,())
],[
	(var4,(term5, term4, term5, term7, term5, term2, term8, term1)),
	(var4,(term5, term9, term6)),
	(var4,(term4, )),
	(var1,(term3, term5, term8, term6, term3, term2, term5, term6)),
	(var1,(var1, )),
	(var4,()),
	(var4,(term6, term0, term4, term4, term5, term6, term3)),
	(var1,(var2, ))
],[
	(var4,())
],[
	(var2,(term5, )),
	(var4,(term4, term1, term4, term2, term9, var3, var0, term5, term1, var3)),
	(var2,(term0, var3, term1)),
	(var2,(term1, term8, var1, var0)),
	(var3,(var0, )),
	(var3,(var3, var1, term0, term1, var0)),
	(var2,(term8, var3))
],[
	(var4,(term8, term6)),
	(var1,(var1, term1, var2)),
	(var0,()),
	(var0,(term4, var2)),
	(var4,(term4, term4)),
	(var2,()),
	(var3,(var2, term7, term4, var0, term1, term3)),
	(var4,(var4, )),
	(var2,(term9, term5, term8, term1)),
	(var1,(var3, term6, var1, term8, term6, var0, var4))
],[
	(var1,(term4, term3, term2, term7, term6)),
	(var0,(var0, term8, var2)),
	(var0,(term9, term7)),
	(var2,(term7, term0, term0, var4)),
	(var3,(var2, var3)),
	(var4,()),
	(var0,(var2, term9)),
	(var3,(term5, term4))
],[
	(var0,(term1, term0, term8)),
	(var4,(term5, term6, term3)),
	(var2,(term0, var3)),
	(var3,(term6, term2, term9)),
	(var2,())
],[
	(var1,(term4, term4, term6)),
	(var2,()),
	(var2,(term7, term7, term3, term6)),
	(var3,(var1, )),
	(var0,(term3, )),
	(var2,(term2, term2, term7))
],[
	(var4,(term1, term0))
],[
	(var4,(var2, term9, var3)),
	(var0,(var2, )),
	(var3,(term8, term1, term5, term5, term5)),
	(var2,(term4, term8, term3)),
	(var3,(term9, )),
	(var4,(var2, )),
	(var3,()),
	(var2,(var1, var1))
],[
	(var2,()),
	(var4,(term1, term6, term2)),
	(var2,(term4, term3, term4))
],[
	(var2,(term2, term0, term5, term1, term1)),
	(var1,(var3, )),
	(var4,()),
	(var3,()),
	(var1,()),
	(var1,(var0, term7, var2, term5, term6)),
	(var0,(term1, ))
],[
	(var1,(term1, )),
	(var2,(term2, term0, term3)),
	(var2,(term8, term7, term8, term0, term8, term1, term9)),
	(var0,(term2, var0)),
	(var4,(term5, term1)),
	(var4,(term4, term5)),
	(var0,(term7, term5)),
	(var0,(term5, term7)),
	(var2,(term2, term0))
],[
	(var4,(term3, term4, term9, term5, term5, term9, term6)),
	(var3,(term0, term7, term3, term8, term4, term6, term5, term2, term4, term8)),
	(var0,(term4, term5, term7, term3, term2, term5, term1, term8)),
	(var4,(var3, var4)),
	(var1,(term9, term9)),
	(var3,(term4, term9, term1, term7, term2)),
	(var0,()),
	(var2,(term7, )),
	(var3,(term6, term1, term3, term7, term1, term9)),
	(var3,(var0, var3, term4, var2, term4, var2, term4))
],[
	(var0,(var3, var1)),
	(var4,(var1, )),
	(var3,(term1, )),
	(var4,(term1, term7, var2, var3, var1, term2)),
	(var3,(term1, term3, term6)),
	(var4,(term0, term7, var1, term0, var1, var2, var2))
],[
	(var3,(term3, )),
	(var1,(term6, term1)),
	(var0,(term6, term7, var1, var1, term4)),
	(var2,()),
	(var3,(term2, term9, term0, term8, term2, term9, term8))
],[
	(var3,(var1, term0, term6, term9, term7, term3, term6, term8, term3, term9)),
	(var3,()),
	(var0,(term6, term5, term0)),
	(var4,(term6, term2, term1)),
	(var2,(term2, var4)),
	(var2,(term2, term6, term4, term7, term5, term6)),
	(var1,(term8, term0, term4)),
	(var4,(var3, var2, term1, var2, term9)),
	(var0,(var2, var2, term5))
],[
	(var2,()),
	(var3,(var2, var4, var3, term7)),
	(var3,(term6, term4, term3, term1, term9, term3, term9, term8, term6, term8)),
	(var1,(var1, )),
	(var2,(term6, term5, term4)),
	(var2,(var2, var4, var0)),
	(var0,(term1, term1, term0, term3, term5, term9, term3))
],[
	(var1,(term8, )),
	(var0,()),
	(var0,(term0, term2)),
	(var2,(term1, term1, term7, term6, term4, term6, term2, term1, term6)),
	(var2,(term5, term6, term7, term7, term2, term7, term1, term7, term7, term4)),
	(var0,(term4, )),
	(var1,(var1, )),
	(var1,(var3, ))
],[
	(var1,(var1, var1, term9, term4, term2)),
	(var0,(term6, var4, var3, var0, var0)),
	(var2,(var2, var3, var0)),
	(var3,(term8, var4, term5, var4, term8, var2)),
	(var1,())
],[
	(var3,(term1, term3, term1)),
	(var3,(var1, )),
	(var4,(term4, )),
	(var4,()),
	(var4,(var4, )),
	(var2,(term9, term0)),
	(var0,(var2, term7, var4, term3, term9)),
	(var4,(term9, term4, term9))
],[
	(var1,(term1, term6)),
	(var0,(term9, var3)),
	(var4,(var1, var3)),
	(var2,(term8, term8, var3, term5, var3, term4, term5)),
	(var2,(term4, term5, var0, var3, term1, term0, term1)),
	(var1,(term3, term5, term4)),
	(var4,(term8, term1, term2)),
	(var3,(var4, term6, var2))
],[
	(var2,(var2, )),
	(var2,(term8, )),
	(var2,(var3, term5, term2, var4)),
	(var4,(term0, term6, var3)),
	(var3,(term9, term6, term7, term7, term8))
]]






def main():
    analyze_grammar(grammar_recitation)
    print

    #
    # --- UNCOMMENT THE FOLLOWING LINES AS YOU PROCEED ---
    #
    analyze_grammar(grammar_json_4a)
    print
    analyze_grammar(grammar_json_4b)
    print
    analyze_grammar(grammar_json_4c)
    print
    analyze_grammar(grammar_json_6)
    print

    #
    # --- ADD MORE TEST CASES HERE ---
    #

    arr = []
    for i in range(0, len(tests)):
        temp = is_LL1(tests[i])
        arr.append(temp)
        print 

    print arr


if __name__ == '__main__':
    main()