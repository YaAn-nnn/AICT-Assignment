# =====================================================
# ASSUMPTIONS (derived from the real-world problem)
# =====================================================

# The MRT network can only be in ONE mode at a time:
# either the current network (TODAY) or the future network (FUTURE).
# It cannot be both simultaneously.

# Terminal 5 (T5), TEL extension, and CRL extension
# do NOT exist in the current network.
# They only exist in the future MRT network.

# If a route uses a station or segment that does not exist
# or is unavailable, the route is considered INVALID.

# During systems integration works,
# MRT services are adjusted and may restrict routing.

# If a service is SUSPENDED, no routing is allowed through it.
# Suspension overrides all other routing decisions.

# If service advisories contradict each other,
# the system should not make any routing decision.


# =====================================================
# PROPOSITIONAL SYMBOLS (knowledge representation)
# =====================================================

# Network mode
TODAY = "TODAY"        # Current MRT network
FUTURE = "FUTURE"      # Future MRT network with extensions

# Route usage
USE_T5 = "USE_T5"      # Route uses Changi Airport Terminal 5
USE_TM_CA = "USE_TM_CA"  # Route uses Tanah Merah–Changi Airport corridor

# Infrastructure availability
TEL_EXT = "TEL_EXT"    # TEL extension exists
CRL_EXT = "CRL_EXT"    # CRL extension exists

# Service conditions
INT_WORKS = "INT_WORKS"  # Systems integration works ongoing
REDUCED = "REDUCED"      # Reduced MRT service
SUSPENDED = "SUSPENDED"  # Suspended MRT service

# Inference outcomes
VALID_ROUTE = "VALID_ROUTE"         # Route is allowed
INVALID_ROUTE = "INVALID_ROUTE"     # Route is not allowed
CONTRADICTION = "CONTRADICTION"     # Advisory information is inconsistent


# =====================================================
# KNOWLEDGE BASE RULES (written in CNF)
# =====================================================

def get_rules():
    # This function builds the knowledge base.
    # Each rule represents a real MRT operational constraint.
    # All rules are written in Conjunctive Normal Form (CNF)
    # so that resolution-based inference can be applied.

    rules = []

    # R1: If the network is in FUTURE mode,
    # then the TEL extension must exist.
    # FUTURE → TEL_EXT
    rules.append({"~" + FUTURE, TEL_EXT})

    # R2: If the network is in FUTURE mode,
    # then the CRL extension must exist.
    # FUTURE → CRL_EXT
    rules.append({"~" + FUTURE, CRL_EXT})

    # R3: If the network is in TODAY mode,
    # then the TEL extension cannot exist.
    # TODAY → ¬TEL_EXT
    rules.append({"~" + TODAY, "~" + TEL_EXT})

    # R4: If the network is in TODAY mode,
    # then the CRL extension cannot exist.
    # TODAY → ¬CRL_EXT
    rules.append({"~" + TODAY, "~" + CRL_EXT})

    # R5: The network cannot be in TODAY and FUTURE mode at the same time.
    # If both are true, the advisory is contradictory.
    rules.append({"~" + TODAY, "~" + FUTURE, CONTRADICTION})

    # R6: If systems integration works are ongoing,
    # MRT service must be reduced.
    # INT_WORKS → REDUCED
    rules.append({"~" + INT_WORKS, REDUCED})

    # R7: MRT service cannot be both reduced and suspended.
    # If both occur, the advisory is contradictory.
    rules.append({"~" + REDUCED, "~" + SUSPENDED, CONTRADICTION})

    # R8: Terminal 5 cannot be used in TODAY mode.
    # Using T5 today results in an invalid route.
    rules.append({"~" + TODAY, "~" + USE_T5, INVALID_ROUTE})

    # R9: During integration works,
    # routes using the TM–CA corridor are invalid.
    rules.append({"~" + INT_WORKS, "~" + USE_TM_CA, INVALID_ROUTE})

    # R10: If service is suspended,
    # routes using the TM–CA corridor are invalid.
    rules.append({"~" + SUSPENDED, "~" + USE_TM_CA, INVALID_ROUTE})

    # R11: If service is suspended,
    # routes using Terminal 5 are invalid.
    rules.append({"~" + SUSPENDED, "~" + USE_T5, INVALID_ROUTE})

    # R12: A route cannot be both valid and invalid.
    rules.append({"~" + INVALID_ROUTE, "~" + VALID_ROUTE})

    return rules


# =====================================================
# RESOLUTION UTILITIES (inference engine)
# =====================================================

def negate(literal):
    # This function negates a literal.
    # Example: A → ~A,  ~A → A
    return literal[1:] if literal.startswith("~") else "~" + literal


def resolve(c1, c2):
    # This function performs ONE resolution step
    # between two clauses c1 and c2.

    # It looks for a literal in c1
    # whose negation exists in c2.
    for lit in c1:
        if negate(lit) in c2:
            # Remove the complementary literals
            # and combine the remaining literals.
            return (c1 | c2) - {lit, negate(lit)}

    # If no resolution is possible, return None.
    return None


def resolution_entails(clauses, query):
    # This function checks whether the knowledge base
    # entails a given query using resolution.

    # Step 1: Copy all clauses
    clause_list = [set(c) for c in clauses]

    # Step 2: Add the negation of the query
    # (Inference by contradiction)
    clause_list.append({negate(query)})

    while True:
        new_clauses = []

        # Step 3: Resolve every pair of clauses
        for i in range(len(clause_list)):
            for j in range(i + 1, len(clause_list)):
                resolvent = resolve(clause_list[i], clause_list[j])

                if resolvent is not None:
                    # If an empty clause is derived,
                    # the query is logically entailed.
                    if len(resolvent) == 0:
                        return True
                    new_clauses.append(resolvent)

        # Step 4: If no new clauses are produced,
        # entailment cannot be proven.
        if all(c in clause_list for c in new_clauses):
            return False

        clause_list.extend(new_clauses)


# =====================================================
# SCENARIO RUNNER (decision logic)
# =====================================================

def run_scenario(name, facts):
    print("\n==============================")
    print("Scenario:", name)
    print("Facts:", facts)

    # Combine rules and scenario facts into one knowledge base
    kb = get_rules()
    for fact in facts:
        kb.append({fact})

    # Step 1: Check for contradictory advisories first
    # If contradictory, do not make any routing decision
    if resolution_entails(kb, CONTRADICTION):
        print("Inference Result: CONTRADICTORY ADVISORY SET")
        return

    # Step 2: If no contradiction, check route validity
    if resolution_entails(kb, INVALID_ROUTE):
        print("Inference Result: INVALID ROUTE")
        return

    # Step 3: Otherwise, the route is valid
    print("Inference Result: VALID ROUTE")


# =====================================================
# TEST SCENARIOS (real-world situations)
# =====================================================

if __name__ == "__main__":

    # Scenario 1: Using TM–CA corridor in TODAY mode
    run_scenario(
        "S1 - Today Mode using TM to CA",
        {TODAY, USE_TM_CA}
    )

    # Scenario 2: Using Terminal 5 in TODAY mode
    run_scenario(
        "S2 - Today Mode using T5",
        {TODAY, USE_T5}
    )

    # Scenario 3: Integration works in FUTURE mode
    run_scenario(
        "S3 - Future Mode with Integration Works",
        {FUTURE, USE_TM_CA, INT_WORKS}
    )

    # Scenario 4: Using Terminal 5 in FUTURE mode
    run_scenario(
        "S4 - Future Mode using T5",
        {FUTURE, USE_T5}
    )

    # Scenario 5: Reduced and suspended service together
    run_scenario(
        "S5 - Reduced and Suspended Service",
        {REDUCED, SUSPENDED}
    )

    # Scenario 6: Declaring TEL extension in TODAY mode
    run_scenario(
        "S6 - Today Mode with TEL Extension Declared",
        {TODAY, TEL_EXT}
    )

    # Scenario 7: Declaring CRL extension in TODAY mode
    run_scenario(
        "S7 - Today Mode with CRL Extension Declared",
        {TODAY, CRL_EXT}
    )

    # Scenario 8: Using T5 in FUTURE mode with suspension
    run_scenario(
        "S8 - Future Mode with T5 Suspended",
        {FUTURE, USE_T5, SUSPENDED}
    )
