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

VALID_ROUTE = "VALID_ROUTE"
INVALID_ROUTE = "INVALID_ROUTE"

CONTRADICTION = "CONTRADICTION"


# =========================
# Knowledge Base Rules (CNF)
# =========================

def get_rules():
    rules = []

    # R1: Future mode implies TEL extension exists
    rules.append({"~" + FUTURE, TEL_EXT})

    # R2: Future mode implies CRL extension exists
    rules.append({"~" + FUTURE, CRL_EXT})

    # R3: Today mode implies TEL extension does not exist
    rules.append({"~" + TODAY, "~" + TEL_EXT})

    # R4: Today mode implies CRL extension does not exist
    rules.append({"~" + TODAY, "~" + CRL_EXT})

    # R5: Systems integration works imply reduced service
    rules.append({"~" + INT_WORKS, REDUCED})

    # R6: Suspended service cannot be reduced service
    rules.append({"~" + SUSPENDED, "~" + REDUCED})

    # R7: Today mode cannot use T5
    rules.append({"~" + TODAY, "~" + USE_T5, INVALID_ROUTE})

    # R8: Integration works invalidate routes using TM–CA
    rules.append({"~" + INT_WORKS, "~" + USE_TM_CA, INVALID_ROUTE})

    # R9: Suspended segments invalidate routes
    rules.append({"~" + SUSPENDED, "~" + USE_TM_CA, INVALID_ROUTE})

    # R10: Invalid route implies not valid route
    rules.append({"~" + INVALID_ROUTE, "~" + VALID_ROUTE})

    # R11: Reduced and suspended together is a contradiction
    rules.append({"~" + REDUCED, "~" + SUSPENDED, CONTRADICTION})

    # R12: Suspended T5 cannot be used
    rules.append({"~" + SUSPENDED, "~" + USE_T5, INVALID_ROUTE})

    return rules


# =========================
# Resolution Utilities
# =========================

def negate(literal):
    return literal[1:] if literal.startswith("~") else "~" + literal


def resolve(c1, c2):
    for lit in c1:
        if negate(lit) in c2:
            return (c1 | c2) - {lit, negate(lit)}
    return None


def resolution_entails(kb, query):
    clauses = [set(c) for c in kb]
    clauses.append({negate(query)})

    while True:
        new = []
        for i in range(len(clauses)):
            for j in range(i + 1, len(clauses)):
                resolvent = resolve(clauses[i], clauses[j])
                if resolvent is not None:
                    if len(resolvent) == 0:
                        return True
                    new.append(resolvent)

        if all(c in clauses for c in new):
            return False

        clauses.extend(new)


# =========================
# Scenario Runner
# =========================

def run_scenario(name, facts):
    print("\n==============================")
    print("Scenario:", name)
    print("Facts:", facts)

    kb = get_rules()
    for f in facts:
        kb.append({f})

    # First: check contradiction
    if resolution_entails(kb, CONTRADICTION):
        print("Inference Result: CONTRADICTORY ADVISORY SET")
        return

    # Then: check invalid route
    if resolution_entails(kb, INVALID_ROUTE):
        print("Inference Result: INVALID ROUTE")
        return

    print("Inference Result: VALID ROUTE")


# =========================
# Test Scenarios
# =========================

if __name__ == "__main__":

    run_scenario(
        "S1 - Today Mode using TM to CA",
        {TODAY, USE_TM_CA}
    )

    run_scenario(
        "S2 - Today Mode using T5",
        {TODAY, USE_T5}
    )

    run_scenario(
        "S3 - Future Mode with Integration Works",
        {FUTURE, USE_TM_CA, INT_WORKS}
    )

    run_scenario(
        "S4 - Future Mode using T5",
        {FUTURE, USE_T5}
    )

    run_scenario(
        "S5 - Reduced and Suspended Service",
        {REDUCED, SUSPENDED}
    )

    run_scenario(
        "S6 - Today Mode with TEL Extension Declared",
        {TODAY, TEL_EXT}
    )

    run_scenario(
        "S7 - Today Mode with CRL Extension Declared",
        {TODAY, CRL_EXT}
    )

    run_scenario(
        "S8 - Future Mode with T5 Suspended",
        {FUTURE, USE_T5, SUSPENDED}
    )
