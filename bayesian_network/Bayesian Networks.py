"""
AICT Assignment 2025/26 — Basic Requirement 2.3
Crowding Risk Prediction with Bayesian Networks (pgmpy)

This skeleton matches the assignment variables and supports:
- Today vs Future mode (TELe+CRL) via M
- Service adjustments/disruptions during systems integration works via S
- Scenario inference (>=5) with paired Today vs Future comparisons

Install (if needed):
    pip install pgmpy
"""

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination
import math



# ----------------------------
# 1) Define BN structure
# ----------------------------
# Variables:
# W: Weather (Clear/Rainy/Thunderstorms)
# T: Time of Day (Peak/Off-Peak)
# D: Day Type (Weekday/Weekend)
# M: Network Mode (Today/Future)
# S: Service Status (Normal/Reduced/Disrupted)
# P: Demand Proxy (Low/Medium/High)
# C: Crowding Risk (Low/Medium/High)

# Structure chosen to be simple + defensible:
# W,T,D -> P -> C
# M -> S -> C
# M -> C (Future mode can change crowding even with same P and S, e.g., more capacity/alternate routes)
model = DiscreteBayesianNetwork([
    ("Season", "Weather"),    
    ("Weather", "Demand"),
    ("Time", "Demand"),
    ("DayType", "Demand"),
    ("Mode", "Service"),
    ("Demand", "Crowding"),
    ("Service", "Crowding"),
    ("Mode", "Crowding"),
])


# ----------------------------
# 2) State names (important for readable evidence)
# ----------------------------
STATE = {
    "Season": ["Northeast Monsoon", "Southwest Monsoon", "Inter-monsoon"],
    "Weather": ["Clear", "Rainy", "Thunderstorms"],
    "Time": ["Peak", "Off-Peak"],
    "DayType": ["Weekday", "Weekend"],
    "Mode": ["Today", "Future"],
    "Service": ["Normal", "Reduced", "Disrupted"],
    "Demand": ["Low", "Medium", "High"],
    "Crowding": ["Low", "Medium", "High"],
}


# ----------------------------
# 3) Priors for root nodes
# ----------------------------
# You may replace these with real distributions later.
cpd_SEASON = TabularCPD(
    variable="Season",
    variable_card=3,
    values=[
        [0.25],  # Northeast Monsoon (Dec–early Mar)
        [0.33],  # Southwest Monsoon (Jun–Sep)
        [0.42],  # Inter-monsoon (Mar–May, Oct–Nov)
    ],
    state_names={"Season": STATE["Season"]},
)

cpd_WEATHER = TabularCPD(
    variable="Weather",
    variable_card=3,
    values=[
        # Clear
        [0.35, 0.50, 0.40],  # NEM, SWM, IM
        # Rainy
        [0.45, 0.30, 0.25],
        # Thunderstorms
        [0.20, 0.20, 0.35],
    ],
    evidence=["Season"],
    evidence_card=[3],
    state_names={
        "Weather": STATE["Weather"],
        "Season": STATE["Season"],  
    },
)

cpd_TIME = TabularCPD(
    variable="Time",
    variable_card=2,
    values=[[0.25], [0.75]],
    state_names={"Time": STATE["Time"]},
)

cpd_DAYTYPE = TabularCPD(
    variable="DayType",
    variable_card=2,
    values=[[5/7], [2/7]],
    state_names={"DayType": STATE["DayType"]},
)

cpd_MODE = TabularCPD(
    variable="Mode",
    variable_card=2,
    values=[[0.50], [0.50]],
    state_names={"Mode": STATE["Mode"]},
)


# ----------------------------
# 4) CPT: Service Status S | Mode M
# ----------------------------
# Encodes systems integration works as higher chance of Reduced/Disrupted in Future mode.
#
# Columns correspond to M in order: Today, Future
cpd_SERVICE = TabularCPD(
    variable="Service",
    variable_card=3,
    values=[
        # S=Normal
        [0.92, 0.78],
        # S=Reduced
        [0.07, 0.17],
        # S=Disrupted
        [0.01, 0.05],
    ],
    evidence=["Mode"],
    evidence_card=[2],
    state_names={"Service": STATE["Service"], "Mode": STATE["Mode"]},
)


# ----------------------------
# 5) CPT: Demand Proxy P | W,T,D
# ----------------------------
# Size: P has 3 states; parents W(3)*T(3)*D(2)=18 columns.
# Skeleton provided with a simple scoring rule to generate a valid CPT.
#
# You should later tune/justify these probabilities.
def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def demand_distribution(w, t, d):
    """
    Returns [P(Demand=Low), P(Demand=Medium), P(Demand=High)] with smooth scaling.

    Rationale:
    - Adverse weather (Rainy/Thunderstorms) increases friction for walking/active modes and changes travel behaviour,
      which can shift demand pressure onto rail nodes/segments. :contentReference[oaicite:1]{index=1}
    - Peak periods and weekdays increase demand relative to off-peak/weekends (documented in national travel surveys). :contentReference[oaicite:2]{index=2}
    """

    # --- 1) Score (same structure as your current model) ---
    # Reply by Acting Minister for Transport Chee Hong Tat:

    # In Q3 2023, average daily ridership on public buses and trains was 7.9 million on weekdays, and 6.4 million on weekends. This is around 95% of pre-pandemic levels.
    score = 0

    # Day type effect
    if d == "Weekday":
        score += 2
    else:  # Weekend
        score += 0
    if d == "Weekday":
        # Weather effect given day type
        if w == "Clear":
            score += 0
        elif w == "Rainy":
            score += 2
        else:  # Thunderstorms
            score += 4
    else:  # Weekend
        if w == "Clear":
            score += 0
        elif w == "Rainy":
            score += 1
        else:  # Thunderstorms
            score += 2

    # Time effect
    if t == "Peak":
        score += 3
    else:  # Off-Peak
        score += 0



    # Score range with your scheme:

    score = max(0, min(score, 9))

    # --- 2) Smooth mapping score -> probabilities ---
    # Set bounds to avoid 0/1 extremes and keep uncertainty realistic.
    HIGH_MIN, HIGH_MAX = 0.05, 0.70
    LOW_MIN,  LOW_MAX  = 0.05, 0.75

    # High demand should rise smoothly as score increases (center around ~4)
    p_high = HIGH_MIN + (HIGH_MAX - HIGH_MIN) * sigmoid((score - 4.0) / 0.9)

    # Low demand should fall smoothly as score increases (center around ~2.2)
    p_low  = LOW_MIN  + (LOW_MAX  - LOW_MIN)  * sigmoid((2.2 - score) / 0.9)

    # Medium is remainder
    p_med = 1.0 - (p_low + p_high)

    # Safety clamp + normalize
    p_low  = max(0.001, p_low)
    p_med  = max(0.001, p_med)
    p_high = max(0.001, p_high)
    total = p_low + p_med + p_high

    return [p_low/total, p_med/total, p_high/total]


# Build P CPT columns in pgmpy evidence order: W, T, D (as listed in evidence=)
p_columns = []
for w in STATE["Weather"]:
    for t in STATE["Time"]:
        for d in STATE["DayType"]:
            p_columns.append(demand_distribution(w, t, d))

# Convert columns -> row-wise values for TabularCPD: rows are P states [Low, Medium, High]
p_low = [col[0] for col in p_columns]
p_med = [col[1] for col in p_columns]
p_high = [col[2] for col in p_columns]

cpd_DEMAND = TabularCPD(
    variable="Demand",
    variable_card=3,
    values=[p_low, p_med, p_high],
    evidence=["Weather", "Time", "DayType"],
    evidence_card=[3, 2, 2],
    state_names={"Demand": STATE["Demand"], "Weather": STATE["Weather"], "Time": STATE["Time"], "DayType": STATE["DayType"]},
)


# ----------------------------
# 6) CPT: Crowding Risk C | P,S,M
# ----------------------------
# Size: C has 3 states; parents P(3)*S(3)*M(2)=18 columns.
# Skeleton uses a rule-based generator:
# - Higher P increases crowding
# - Reduced/Disrupted S increases crowding strongly
# - Future mode reduces crowding slightly (more capacity/alternate routes)
#
# You should later tune these numbers to your narrative.
DEMAND_W = {"Low": 0, "Medium": 3, "High": 6}
SERVICE_W = {"Normal": 0, "Reduced": 4, "Disrupted": 8}
FUTURE_BONUS = -2



def crowding_distribution(p, s, m):
    # 1) Risk score
    risk = DEMAND_W[p] + SERVICE_W[s] + (FUTURE_BONUS if m == "Future" else 0)

    # Keep risk in a stable range for calibration
    # (with the weights above, risk typically spans ~0 to ~14)
    risk = max(0, min(risk, 14))

    # 2) Smooth mapping to probabilities
    # Set min/max to keep uncertainty realistic and avoid 0/1 extremes
    HIGH_MIN, HIGH_MAX = 0.05, 0.90
    LOW_MIN,  LOW_MAX  = 0.05, 0.85

    # High crowding increases with risk (centered around ~7)
    p_high = HIGH_MIN + (HIGH_MAX - HIGH_MIN) * sigmoid((risk - 7.0) / 1.6)

    # Low crowding decreases with risk (centered around ~3)
    p_low  = LOW_MIN  + (LOW_MAX  - LOW_MIN)  * sigmoid((3.0 - risk) / 1.6)

    # Medium is whatever remains; then renormalize safely
    p_med = 1.0 - (p_low + p_high)

    # Clamp + renormalize (prevents negative due to overlap)
    p_low  = max(0.001, p_low)
    p_med  = max(0.001, p_med)
    p_high = max(0.001, p_high)
    total = p_low + p_med + p_high
    return [p_low/total, p_med/total, p_high/total]


c_columns = []
for p in STATE["Demand"]:
    for s in STATE["Service"]:
        for m in STATE["Mode"]:
            c_columns.append(crowding_distribution(p, s, m))

c_low = [col[0] for col in c_columns]
c_med = [col[1] for col in c_columns]
c_high = [col[2] for col in c_columns]

cpd_CROWDING = TabularCPD(
    variable="Crowding",
    variable_card=3,
    values=[c_low, c_med, c_high],
    evidence=["Demand", "Service", "Mode"],
    evidence_card=[3, 3, 2],
    state_names={"Crowding": STATE["Crowding"], "Demand": STATE["Demand"], "Service": STATE["Service"], "Mode": STATE["Mode"]},
)


# ----------------------------
# 7) Add CPDs and validate model
# ----------------------------
model.add_cpds(cpd_SEASON, cpd_WEATHER, cpd_TIME, cpd_DAYTYPE, cpd_MODE, cpd_SERVICE, cpd_DEMAND, cpd_CROWDING)

assert model.check_model(), "Model is invalid. Check CPT dimensions / sums."


# ----------------------------
# 8) Inference helper + required scenarios
# ----------------------------
infer = VariableElimination(model)


def run_scenario(name, evidence):
    q = infer.query(variables=["Crowding"], evidence=evidence, show_progress=False)

    # Newer/changed pgmpy returns a DiscreteFactor directly for single-variable queries
    dist = q  # instead of q["Crowding"]

    print(f"\nScenario: {name}")
    print("Evidence:", evidence)

    for state, prob in zip(dist.state_names["Crowding"], dist.values):
        print(f"  P(Crowding={state}) = {prob:.4f}")

    return dist


if __name__ == "__main__":
    # (a) Rainy, Peak + reduced service (Today)
    run_scenario(
        "Rainy Peak + reduced service (Today)",
        {"Weather": "Rainy", "Time": "Peak", "DayType": "Weekday", "Mode": "Today", "Service": "Reduced"},
    )

    # Paired Today vs Future (same evidence except Mode) — counts toward the >=3 paired requirement
    # (e) Today Mode: Clear Peak + normal service (baseline)
    run_scenario(
        "Clear Peak + normal service (Today baseline)",
        {"Weather": "Clear", "Time": "Peak", "DayType": "Weekday", "Mode": "Today", "Service": "Normal"},
    )
    # (f) Future Mode: Clear Peak + normal service
    run_scenario(
        "Clear Peak + normal service (Future TELe+CRL)",
        {"Weather": "Clear", "Time": "Peak", "DayType": "Weekday", "Mode": "Future", "Service": "Normal"},
    )

    # (g) Today Mode: Rainy Peak + reduced service (baseline)
    run_scenario(
        "Rainy Peak + reduced service (Today baseline)",
        {"Weather": "Rainy", "Time": "Peak", "DayType": "Weekday", "Mode": "Today", "Service": "Reduced"},
    )
    # (h) Future Mode: Rainy Peak + reduced service
    run_scenario(
        "Rainy Peak + reduced service (Future TELe+CRL)",
        {"Weather": "Rainy", "Time": "Peak", "DayType": "Weekday", "Mode": "Future", "Service": "Reduced"},
    )

    # (c) Weekend Off-Peak + normal service (single scenario)
    run_scenario(
        "Weekend Off-Peak + normal service",
        {"Weather": "Clear", "Time": "Off-Peak", "DayType": "Weekend", "Mode": "Today", "Service": "Normal"},
    )

    # (d) Disrupted service near the airport corridor (single scenario)
    run_scenario(
        "Disrupted service near airport corridor",
        {"Weather": "Clear", "Time": "Peak", "DayType": "Weekday", "Mode": "Today", "Service": "Disrupted"},
    )

        # (d) Disrupted service near the airport corridor (single scenario)
    run_scenario(
        "Disrupted service near airport corridor",
        {"Weather": "Clear", "Time": "Peak", "DayType": "Weekday", "Mode": "Future", "Service": "Disrupted"},
    )

    # Optional: show how Mode influences Service Status if S is NOT observed:
    # Uncomment to test S inferred from M (useful for discussion)
    # run_scenario(
    #     "Clear Peak weekday (Today) — S unobserved",
    #     {"Weather": "Clear", "Time": "Peak", "DayType": "Weekday", "Mode": "Today"},
    # )
    # run_scenario(
    #     "Clear Peak weekday (Future) — S unobserved",
    #     {"Weather": "Clear", "Time": "Peak", "DayType": "Weekday", "Mode": "Future"},
    # )
