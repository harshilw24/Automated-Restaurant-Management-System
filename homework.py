import time


def parse_input(file):
    with open(file, 'rt') as f:
        input_list = f.readlines()

    query = input_list[0].strip()
    number_of_facts = int(input_list[1].strip())
    facts = []

    for i in range(number_of_facts):
        facts.append(input_list[i + 2])

    facts = [x.replace(" ", "") for x in facts]
    facts = [x.replace("\n", "") for x in facts]

    return query, facts


def write_output(output):
    file = open("output.txt", 'w')
    file.write(str(output).upper())
    file.close()


def to_cnf(kb):
    for i in range(len(kb)):
        if "=>" in kb[i]:
            kb[i] = negate_antecedent(kb[i])

    return kb


def negate_predicate(predicate):
    return predicate[1:] if predicate[0] == "~" else "~" + predicate


def distribute_and_over_or(sentence):
    # Split the sentence into individual clauses
    clauses = sentence.split('|')

    # If there is only one clause, return the original sentence
    if len(clauses) == 1:
        return sentence

    # Initialize a list to store the new clauses
    new_clauses = []

    # Iterate over all possible pairs of clauses and distribute '&'
    for i in range(len(clauses)):
        for j in range(i + 1, len(clauses)):
            new_clause = ''
            for clause1 in clauses[i].split('&'):
                for clause2 in clauses[j].split('&'):
                    new_clause += clause1 + '|' + clause2 + '&'
            new_clauses.append(new_clause[:-1])  # Remove the trailing '&'

    # Concatenate the new clauses with '|' in between
    new_sentence = '|'.join(new_clauses)

    return new_sentence


def negate_antecedent(sentence):
    antecedent = sentence[:sentence.find("=>")]
    premise = []
    operators = {"&": 0, "|": 0}
    operators_count = {"&": 0, "|": 0}

    if "&" in antecedent:
        operators["&"] = 1

    if "|" in antecedent:
        operators["|"] = 1

    if operators["|"] == 0 and operators["&"] == 1:
        for predicate in antecedent.split("&"):
            premise.append(negate_predicate(predicate))
        premise.append(sentence[sentence.find("=>") + 2:])
        return "|".join(premise)
    elif operators["|"] == 1 and operators["&"] == 0:
        for predicate in antecedent.split("|"):
            premise.append(negate_predicate(predicate))
        new_antecedent = "&".join(premise)
        new_sentence = new_antecedent + "|" + sentence[sentence.find("=>") + 2:]
        new_sentence = distribute_and_over_or(new_sentence)
        return new_sentence
    elif operators["|"] == 0 and operators["&"] == 0:
        for predicate in antecedent.split("&"):
            premise.append(negate_predicate(predicate))
        premise.append(sentence[sentence.find("=>") + 2:])
        return "|".join(premise)
    else:
        temp_kb = []
        splitter = ""
        for i in antecedent:
            if i == "&":
                operators_count["&"] += 1
            if i == "|":
                operators_count["|"] += 1
        total_operators = operators_count["&"] + operators_count["|"]
        print(operators_count)
        print(total_operators)
        if total_operators == 3:
            if operators_count["|"] < operators_count["&"]:
                splitter = "|"
            else:
                splitter = "&"
        if operators_count["&"] == 1 and operators_count["|"] == 1:
            # for predicate in antecedent.split("|"):
            #     for x in range(len(predicate)):
            #         predicate[x] = predicate[x] + "=>" + sentence[sentence.find("=>") + 2:]
            #         temp_kb.append(predicate[x])
            predicate = antecedent.split("|")
            for x in range(len(predicate)):
                predicate[x] = predicate[x] + "=>" + sentence[sentence.find("=>") + 2:]
                temp_kb.append(predicate[x])
            temp_kb1 = to_cnf(temp_kb)
            new_sentence = "&".join(temp_kb1)
            return new_sentence
        elif total_operators == 3:
            predicate = antecedent.split(splitter)
            for x in range(len(predicate)):
                predicate[x] = predicate[x] + "=>" + sentence[sentence.find("=>") + 2:]
                temp_kb.append(predicate[x])
            temp_kb1 = to_cnf(temp_kb)
            new_sentence = "&".join(temp_kb1)
            return new_sentence


def check_tautology(kb):
    sentence_counter = -1
    for sentence in kb:
        sentence_counter += 1
        if "&" in sentence:
            taut = sentence.split("&")
            kb.remove(sentence)
            for sent in taut:
                kb.insert(sentence_counter, sent)
    return kb


def create_data_structure(string):
    string = string.replace(" ", "")
    data_structure = []
    if "|" in string:
        literals = string.split("|")
        for lit in literals:
            name, variables = lit.split("(")
            variables = variables[:-1]  # remove closing bracket
            if name[0] == "~":
                if_negated = True
                name = name[1:]
            else:
                if_negated = False
            variables = variables.split(",")
            data_structure.append({"name": name, "if_negated": if_negated, "list_of_variables": variables})
    else:
        name, variables = string.split("(")
        variables = variables[:-1]  # remove closing bracket
        if name[0] == "~":
            if_negated = True
            name = name[1:]
        else:
            if_negated = False
        variables = variables.split(",")
        data_structure.append({"name": name, "if_negated": if_negated, "list_of_variables": variables})
    return data_structure


def remove_duplicates(strings):
    new_strings = []
    for string in strings:
        if "|" in string:
            literals = string.split("|")
            new_literals = []
            for literal in literals:
                if literal not in new_literals:
                    new_literals.append(literal)
            new_string = "|".join(new_literals)
            new_strings.append(new_string)
        else:
            new_strings.append(string)
    return new_strings


def resolve(query, knowledge_base):
    # Convert the query to CNF and negate it
    negated_query = negate_predicate(query)
    # Append the negated query to the knowledge base
    knowledge_base.append(negated_query)
    dynamic_length = 0
    # Keep resolving until we find an empty set
    resolved_pairs = set()
    while True:
        if time.time() - t1 > 1150:
            return False
        new_clauses = set()
        # Iterate over all pairs of sentences in the KB
        for i in range(dynamic_length, len(knowledge_base)):
            # if i in resolved_indices:
            #     continue
            clause1 = knowledge_base[i]
            for j in range(len(knowledge_base)):
                clause2 = knowledge_base[j]
                if i == j or (i, j) in resolved_pairs or (j, i) in resolved_pairs:
                    # Skip already resolved or identical pairs
                    continue
                # Try to resolve the two clauses
                resolvents = resolve_clauses(clause1, clause2)
                # If the resolvents are None, the two clauses were unresolvable
                if resolvents is None:
                    resolved_pairs.add((i, j))
                    continue
                # If the resolvents are empty, we have found a contradiction
                if resolvents[0] == '':
                    return True
                # Add the new resolvents to the set of new clauses
                new_clauses.update(resolvents)
                # print(new_clauses)
                resolved_pairs.add((i, j))
        # If no new clauses were generated, we can't resolve any further
        if not new_clauses:
            return False
        # Add the new clauses to the knowledge base
        dynamic_length = len(knowledge_base)
        new_clauses = remove_duplicates(new_clauses)
        for clause in new_clauses:
            if clause not in knowledge_base:
                knowledge_base.append(clause)
        # Add the indices of resolved clauses to the set
        # resolved_indices.update(set(range(len(knowledge_base))) - set([knowledge_base.index(c) for c in new_clauses]))


def list_duplicates_of(lst, item):
    return [i for i, x in enumerate(lst) if x == item]


def resolve_clauses(clause1, clause2, ):
    """Resolves two clauses in CNF form"""
    # print(clause1 + " ---> " + clause2)
    clause1_data = create_data_structure(clause1)
    clause2_data = create_data_structure(clause2)

    clause1_data, clause2_data = standardize_variables(clause1_data, clause2_data)

    # Check if clauses can be resolved
    for lit1 in clause1_data:
        for lit2 in clause2_data:
            if lit1["name"] == lit2["name"] and lit1["if_negated"] != lit2["if_negated"]:
                can_resolve = True
                has_constant = False
                both_constant = False
                ticker = False
                constant1 = ''
                constant2 = ''
                clause1_index = -1
                clause2_index = -1
                ss_case = False

                l1 = len(lit1["list_of_variables"])
                l2 = len(lit2["list_of_variables"])
                original_var = None
                dup_list = []
                dl = []

                for i in range(l1):
                    dup_list.append(list_duplicates_of(lit1["list_of_variables"], lit1["list_of_variables"][i]))

                for i in dup_list:
                    if i not in dl:
                        dl.append(i)

                dup_list = dl

                for i in range(len(dup_list)):
                    if len(dup_list[i]) > 1:
                        original_var = lit2["list_of_variables"][dup_list[i][0]]
                        for j in range(l2):
                            if original_var != lit2["list_of_variables"][dup_list[i][j]]:
                                return None

                for i in range(len(lit1["list_of_variables"])):
                    if lit1["list_of_variables"][i][0].isupper():
                        constant1 = lit1["list_of_variables"][i]
                        clause1_index = i
                for i in range(len(lit1["list_of_variables"])):
                    if lit2["list_of_variables"][i][0].isupper():
                        constant2 = lit2["list_of_variables"][i]
                        clause2_index = i
                if clause2_index == clause1_index and constant1 == constant2 and constant1 != '' and clause1_index != -1:
                    ss_case = True

                for i, var1 in enumerate(lit1["list_of_variables"]):
                    var2 = lit2["list_of_variables"][i]
                    if var1 == var2 and var1[0].isupper() and var2[0].isupper():
                        if not ticker:
                            both_constant = True
                    else:
                        both_constant = False
                        ticker = True
                    # Check if variables can be unified
                    if var1 != var2:
                        if var1[0].islower() and var2[0].islower():
                            break  # variables cannot be unified
                        elif var1[0].islower() and var2[0].isupper():
                            # var1 is a variable and var2 is a constant
                            can_resolve = True
                            has_constant = True
                        elif var1[0].isupper() and var2[0].islower():
                            # var1 is a constant and var2 is a variable
                            can_resolve = True
                            has_constant = True
                        elif var1 == var2:
                            # both variables are the same constants
                            has_constant = True
                    if not can_resolve:
                        break
                if can_resolve and has_constant:
                    # Unify variables
                    substitution = {}
                    for i, var1 in enumerate(lit1["list_of_variables"]):
                        var2 = lit2["list_of_variables"][i]
                        if var1 != var2:
                            if var1[0].islower() and var2[0].isupper():
                                substitution[var1] = var2
                            else:
                                substitution[var2] = var1

                    # Apply substitution to clause data
                    for lit in clause1_data + clause2_data:
                        for i, var in enumerate(lit["list_of_variables"]):
                            if var in substitution:
                                lit["list_of_variables"][i] = substitution[var]

                    # Remove resolved literals and duplicates
                    new_clause_data = []
                    for lit in clause1_data + clause2_data:
                        if lit != lit1 and lit != lit2 and lit not in new_clause_data:
                            new_clause_data.append(lit)

                    # Construct new clause
                    new_clause = "|".join(
                        [f'{"~" if lit["if_negated"] else ""}{lit["name"]}({",".join(lit["list_of_variables"])})'
                         for lit in new_clause_data])
                    return [new_clause]
                elif can_resolve and both_constant:
                    if both_constant and all(v1 == v2 for v1, v2 in zip(lit1["list_of_variables"],
                                                                        lit2["list_of_variables"])):
                        new_clause_data = [lit for lit in clause1_data + clause2_data if lit != lit1 and lit != lit2]
                        new_clause = "|".join(
                            [f'{"~" if lit["if_negated"] else ""}{lit["name"]}({",".join(lit["list_of_variables"])})'
                             for lit in new_clause_data])
                        return [new_clause]
                elif ss_case:
                    # Resolve special case
                    new_clause_data = []
                    for lit in clause1_data + clause2_data:
                        if lit != lit1 and lit != lit2 and lit not in new_clause_data:
                            new_clause_data.append(lit)
                    for i in range(len(lit1["list_of_variables"])):
                        if lit1["list_of_variables"][i][0] == lit2["list_of_variables"][i][0]:
                            if lit1["list_of_variables"][i][0].isupper():
                                constant = lit1["list_of_variables"][i]
                                break
                    # Construct new clause with required constant
                    for i in range(len(new_clause_data)):
                        for j in range(len(new_clause_data[i]["list_of_variables"])):
                            new_clause_data[i]["list_of_variables"][j] = constant1
                    new_clause = "|".join(
                        [f'{"~" if lit["if_negated"] else ""}{lit["name"]}({",".join(lit["list_of_variables"])})'
                         for lit in new_clause_data])
                    return [new_clause]

    return None


def standardize_variables(clause1_data, clause2_data):
    """
    Standardizes variables in clause2_data such that no variable occurs in more than one literal. The
    variables in clause1_data are not changed.
    """
    variable_set = set()
    standardized_clause2_data = []
    for lit in clause1_data:
        variable_set.update(lit['list_of_variables'])
    for lit in clause2_data:
        standardized_lit = lit.copy()
        for i, var in enumerate(lit['list_of_variables']):
            if var in variable_set and var.islower():
                new_var = f"{var}_1"
                standardized_lit['list_of_variables'][i] = new_var
        standardized_clause2_data.append(standardized_lit)
    return clause1_data, standardized_clause2_data


def main():
    query, kb = parse_input("input.txt")
    cnf_kb = to_cnf(kb)
    cnf_kb = check_tautology(cnf_kb)
    result = resolve(query, cnf_kb)
    write_output(result)


if __name__ == '__main__':
    t1 = time.time()
    main()
    t2 = time.time()
    print(t2 - t1)
