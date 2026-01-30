"""
AICT Assignment
Logical Inference for Service Rules & Advisory Consistency
Component Owner: [Your Name]
"""

# =========================
# Propositional Symbols
# =========================

TODAY = "TODAY"
FUTURE = "FUTURE"

USE_T5 = "USE_T5"
USE_TM_CA = "USE_TM_CA"

TEL_EXT = "TEL_EXT"
CRL_EXT = "CRL_EXT"

INT_WORKS = "INT_WORKS"
REDUCED = "REDUCED"
SUSPENDED = "SUSPENDED"

INVALID_ROUTE = "INVALID_ROUTE"
VALID_ROUTE = "VALID_ROUTE"


# =========================
# Knowledge Base Rules
# CNF Representation
# Each clause is a set of literals
# Negation is represented using "~"
# =========================

def get_rules():
    rules = []

    # R1: FUTURE -> TEL_EXT
    rules.append({"~" + FUTURE, TEL_EXT})

    # R2: FUTURE -> CRL_EXT
    rules.append({"~" + FUTURE, CRL_EXT})

    # R3: TODAY -> not TEL_EXT
    rules.append({"~" + TODAY, "~" + TEL_EXT})

    # R4: INT_WORKS -> REDUCED
    rules.append({"~" + INT_WORKS, REDUCED})

    # R5: SUSPENDED -> not REDUCED
    rules.append({"~" + SUSPENDED, "~" + REDUCED})

    # R6: TODAY and USE_T5 -> INVALID_ROUTE
    rules.append({"~" + TODAY, "~" + USE_T5, INVALID_ROUTE})

    # R7: INT_WORKS and USE_TM_CA -> INVALID_ROUTE
    rules.append({"~" + INT_WORKS, "~" + USE_TM_CA, INVALID_ROUTE})

    # R8: SUSPENDED and USE_TM_CA -> INVALID_ROUTE
    rules.append({"~" + SUSPENDED, "~" + USE_TM_CA, INVALID_ROUTE})

    # R9: INVALID_ROUTE -> not VALID_ROUTE
    rules.append({"~" + INVALID_ROUTE, "~" + VALID_ROUTE})

    # R10: REDUCED and SUSPENDED is a contradiction
    rules.append({"~" + REDUCED, "~" + SUSPENDED})

    return rules


# =========================
# Utility Functions
# =========================

def negate(literal):
    if literal.startswith("~"):
        return literal[1:]
    return "~" + literal


def resolve(clause1, clause2):
    for literal in clause1:
        if negate(literal) in clause2:
            resolvent = (clause1 | clause2) - {literal, negate(literal)}
            return resolvent
    return None


# =========================
# Resolution Based Inference
# =========================

def resolution(kb, query):
    clauses = [set(c) for c in kb]
    clauses.append({negate(query)})

    while True:
        new_clauses = []

        for i in range(len(clauses)):
            for j in range(i + 1, len(clauses)):
                resolvent = resolve(clauses[i], clauses[j])
                if resolvent is not None:
                    if len(resolvent) == 0:
                        return True
                    new_clauses.append(resolvent)

        if all(c in clauses for c in new_clauses):
            return False

        clauses.extend(new_clauses)


# =========================
# Scenario Runner
# =========================

def run_scenario(name, facts, query):
    print("\n==============================")
    print("Scenario:", name)
    print("Facts:", facts)
    print("Query:", query)

    kb = get_rules()
    for fact in facts:
        kb.append({fact})

    result = resolution(kb, query)

    if result:
        print("Inference Result:", query, "is TRUE")
    else:
        print("Inference Result:", query, "is FALSE")


# =========================
# Test Scenarios
# =========================

if __name__ == "__main__":

    # Scenario 1: Valid route in Today Mode
    run_scenario(
        "S1 - Today Mode using TM to CA",
        {TODAY, USE_TM_CA},
        VALID_ROUTE
    )

    # Scenario 2: Invalid route using T5 in Today Mode
    run_scenario(
        "S2 - Today Mode using T5",
        {TODAY, USE_T5},
        INVALID_ROUTE
    )

    # Scenario 3: Invalid route during integration works
    run_scenario(
        "S3 - Future Mode with Integration Works",
        {FUTURE, USE_TM_CA, INT_WORKS},
        INVALID_ROUTE
    )

    # Scenario 4: Valid route using T5 in Future Mode
    run_scenario(
        "S4 - Future Mode using T5",
        {FUTURE, USE_T5},
        VALID_ROUTE
    )

    # Scenario 5: Contradictory advisories
    run_scenario(
        "S5 - Reduced and Suspended Service",
        {REDUCED, SUSPENDED},
        INVALID_ROUTE
    )

    # Scenario 6: Contradictory advisory - TEL extension in Today Mode
    run_scenario(
        "S6 - Today Mode with TEL Extension Declared",
        {TODAY, TEL_EXT},
        INVALID_ROUTE
    )

