# =====================================================
# Assumptions (derived from problem statement)
# =====================================================
# 1. TODAY and FUTURE represent mutually exclusive network modes.
# 2. T5, TEL extension, and CRL extension exist only in Future Mode.
# 3. Routes using unavailable stations or segments are invalid.
# 4. Systems integration works require service adjustments.
# 5. Suspended service overrides all routing decisions.
# 6. Contradictory advisories invalidate decision-making.

# =====================================================
# Propositional Symbols
# =====================================================

TODAY = "TODAY"
FUTURE = "FUTURE"

USE_T5 = "USE_T5"              # Route uses Terminal 5
USE_TM_CA = "USE_TM_CA"        # Route uses Tanah Merah – Changi Airport corridor

TEL_EXT = "TEL_EXT"            # TEL extension exists
CRL_EXT = "CRL_EXT"            # CRL extension exists

INT_WORKS = "INT_WORKS"        # Systems integration works ongoing
REDUCED = "REDUCED"            # Reduced service
SUSPENDED = "SUSPENDED"        # Suspended service

VALID_ROUTE = "VALID_ROUTE"
INVALID_ROUTE = "INVALID_ROUTE"
CONTRADICTION = "CONTRADICTION"


# =====================================================
# Knowledge Base Rules (CNF)
# Each rule is grounded in the real-world problem text
# =====================================================

def get_rules():
    rules = []

    # R1: Future Mode implies TEL extension exists
    rules.append({"~" + FUTURE, TEL_EXT})

    # R2: Future Mode implies CRL extension exists
    rules.append({"~" + FUTURE, CRL_EXT})

    # R3: Today Mode implies TEL extension does not exist
    rules.append({"~" + TODAY, "~" + TEL_EXT})

    # R4: Today Mode implies CRL extension does not exist
    rules.append({"~" + TODAY, "~" + CRL_EXT})

    # R5: Today and Future modes cannot both be true
    rules.append({"~" + TODAY, "~" + FUTURE, CONTRADICTION})

    # R6: Systems integration works imply reduced service
    rules.append({"~" + INT_WORKS, REDUCED})

    # R7: Reduced and suspended service cannot coexist
    rules.append({"~" + REDUCED, "~" + SUSPENDED, CONTRADICTION})

    # R8: Today Mode cannot use Terminal 5
    rules.append({"~" + TODAY, "~" + USE_T5, INVALID_ROUTE})

    # R9: Integration works invalidate routes using TM–CA corridor
    rules.append({"~" + INT_WORKS, "~" + USE_TM_CA, INVALID_ROUTE})

    # R10: Suspended service invalidates TM–CA routes
    rules.append({"~" + SUSPENDED, "~" + USE_TM_CA, INVALID_ROUTE})

    # R11: Suspended service invalidates T5 routes
    rules.append({"~" + SUSPENDED, "~" + USE_T5, INVALID_ROUTE})

    # R12: Invalid route cannot be valid
    rules.append({"~" + INVALID_ROUTE, "~" + VALID_ROUTE})

    return rules


# =====================================================
# Resolution Utilities
# =====================================================

def negate(literal):
    return literal[1:] if literal.startswith("~") else "~" + literal


def resolve(c1, c2):
    for lit in c1:
        if negate(lit) in c2:
            return (c1 | c2) - {lit, negate(lit)}
    return None


def resolution_entails(clauses, query):
    clause_list = [set(c) for c in clauses]
    clause_list.append({negate(query)})

    while True:
        new_clauses = []

        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvent = resolve(clause_list[i], clause_list[j])
                if resolvent is not None:
                    if len(resolvent) == 0:
                        return True
                    new_clauses.append(resolvent)

        if all(c in clause_list for c in new_clauses):
            return False

        clause_list.extend(new_clauses)


# =====================================================
# Scenario Runner
# =====================================================

def run_scenario(name, facts):
    print("\n==============================")
    print("Scenario:", name)
    print("Facts:", facts)

    kb = get_rules()
    for fact in facts:
        kb.append({fact})

    # Step 1: Advisory consistency check
    if resolution_entails(kb, CONTRADICTION):
        print("Inference Result: CONTRADICTORY ADVISORY SET")
        return

    # Step 2: Route validity check
    if resolution_entails(kb, INVALID_ROUTE):
        print("Inference Result: INVALID ROUTE")
        return

    print("Inference Result: VALID ROUTE")


# =====================================================
# Test Scenarios (aligned with real-world brief)
# =====================================================

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
