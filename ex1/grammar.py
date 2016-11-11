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
        for head, body in grammar:
            for i in range(0, len(body)):  # TODO: check for out of range bugs
                if does_set_contain_tuple(body[0:i], nullable):
                    for item in first[body[i]]:
                        if item not in first[head]:
                            first[head].add(item)
                            changing = True
    return first


def does_set_contain_tuple(tuple, set):
    for item in tuple:
        if item not in set:
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
        for head, body in grammar:
            for i in range(0, len(body)):  # TODO: check for out of range bugs
                if body[i] in terminals:  # TODO: check if needed
                    continue
                if does_set_contain_tuple(body[i+1:], nullable):
                    for item in follow[head]:
                        if item not in follow[body[i]]:
                            follow[body[i]].add(item)
                            changing = True

            for i in range(0, len(body) - 1):  # TODO: check for out of range bugs
                if body[i] in terminals:  # TODO: check if needed
                    continue
                for j in range(i + 1, len(body)):  # TODO: check for out of range bugs
                    if does_set_contain_tuple(body[i+1:j], nullable):
                        for item in first[body[j]]:
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
        # TODO: ask Oded if only need to get first of left-most token in right side of rule
        if body:
            item = body[0]
            for x in first[item]:
                select[head, body].add(x)
        if does_set_contain_tuple(body, nullable):
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


grammar_json_4a = [
    #
    # --- FILL IN HERE IN QUESTION 5.a ---
    #
]

grammar_json_4b = [
    #
    # --- FILL IN HERE IN QUESTION 5.b ---
    #
]

grammar_json_4c = [
    #
    # --- FILL IN HERE IN QUESTION 5.c ---
    #
]

grammar_json__6 = [
    #
    # --- FILL IN HERE IN QUESTION 7 ---
    #
]



def main():
    analyze_grammar(grammar_recitation)
    print

    #
    # --- UNCOMMENT THE FOLLOWING LINES AS YOU PROCEED ---
    #
    # analyze_grammar(grammar_json_4a)
    # print
    # analyze_grammar(grammar_json_4b)
    # print
    # analyze_grammar(grammar_json_4c)
    # print
    # analyze_grammar(grammar_json_6)
    # print

    #
    # --- ADD MORE TEST CASES HERE ---
    #


if __name__ == '__main__':
    main()
