"""
AICT Assignment 2025/26 — Basic Requirement 2.3
Crowding Risk Prediction with Bayesian Networks (pgmpy)

This version aligns the BN structure + weights with your write-ups:
- Monsoon Season -> Weather
- Weather, Time, DayType, PublicHoliday -> Demand
- Mode -> Service
- Demand, Service, Mode -> Crowding

Notes
- PublicHoliday affects Crowding *via* Demand (no direct Holiday -> Crowding edge).
- Demand CPT is constructed from the single-parent calibrations using a simple log-linear
  (multiplicative) combination and then normalized.
- Service|Mode and Crowding|Demand,Service,Mode match the document tables, with a
  Future-mode "buffer" on crowding.
"""

from __future__ import annotations

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination

import glob
import os
import pandas as pd

DATA_GLOB = r"C:\\Users\\Flipp\\OneDrive\\Documents\\Desktop\\AICT-Assignment\\transport_node_train_202512\\transport_node_train_202512.*csv"  # <-- change to your folder
STATIONS = {"CG2"} 

# Demand bin thresholds (percentiles) for Low / Moderate / High
LOW_Q = 0.3
HIGH_Q = 0.8




# ----------------------------
# 2) Load and concatenate all monthly CSVs
# ----------------------------
paths = sorted(glob.glob(DATA_GLOB))
if not paths:
    raise FileNotFoundError(f"No CSVs matched DATA_GLOB={DATA_GLOB!r}")

dfs = []
for p in paths:
    df = pd.read_csv(p)

    # Expected columns (DataMall):
    # YEAR_MONTH, DAY_TYPE, TIME_PER_HOUR, PT_TYPE, PT_CODE,
    # TOTAL_TAP_IN_VOLUME, TOTAL_TAP_OUT_VOLUME
    required = {
        "DAY_TYPE",
        "PT_CODE",
        "TOTAL_TAP_IN_VOLUME",
        "TOTAL_TAP_OUT_VOLUME",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"{os.path.basename(p)} missing columns: {sorted(missing)}")

    dfs.append(df)

print(len(dfs), "files loaded.")

data = pd.concat(dfs, ignore_index=True)

# ----------------------------
# 3) Clean + filter
# ----------------------------
# Standardize DAY_TYPE strings (defensive)
data["DAY_TYPE"] = data["DAY_TYPE"].astype(str).str.strip().str.upper()
data["PT_CODE"] = data["PT_CODE"].astype(str).str.strip().str.upper()

# Filter stations if provided
if STATIONS is not None:
    stations_norm = {s.strip().upper() for s in STATIONS}
    data = data[data["PT_CODE"].isin(stations_norm)].copy()
    if data.empty:
        raise ValueError(
            f"No rows match STATIONS={stations_norm}. "
            f"Check PT_CODE values in your CSV(s)."
        )

# Compute total hourly volume (proxy for demand intensity that hour)
data["VOLUME"] = data["TOTAL_TAP_IN_VOLUME"].fillna(0) + data["TOTAL_TAP_OUT_VOLUME"].fillna(0)

# Keep only the 2 known day types
valid_day_types = {"WEEKDAY", "WEEKENDS/HOLIDAY"}
data = data[data["DAY_TYPE"].isin(valid_day_types)].copy()
if data.empty:
    raise ValueError("After filtering DAY_TYPE, no rows remain. Check DAY_TYPE values.")

# ----------------------------
# 4) Discretise VOLUME into Demand states using global quantiles
# ----------------------------
# Compute thresholds on the chosen station(s) and across both day types.
q_low = data["VOLUME"].quantile(LOW_Q)
q_high = data["VOLUME"].quantile(HIGH_Q)


def volume_to_demand(v: float) -> str:
    if v <= q_low:
        return "Low"
    if v >= q_high:
        return "High"
    return "Moderate"

data["DEMAND_STATE"] = data["VOLUME"].map(volume_to_demand)

# ----------------------------
# 5) Compute P(Demand_state | DAY_TYPE)
# ----------------------------
# Count distribution of demand bins within each day type
counts = (
    data.groupby(["DAY_TYPE", "DEMAND_STATE"])
        .size()
        .unstack(fill_value=0)
)

# Ensure all states exist as columns
for col in ["Low", "Moderate", "High"]:
    if col not in counts.columns:
        counts[col] = 0

probs = counts.div(counts.sum(axis=1), axis=0)

# Map into your BN naming convention:
# - "Weekday" from WEEKDAY
# - "Weekend" from WEEKENDS/HOLIDAY (dataset merges weekends + holidays)
cal_daytype = {
    "Weekday": [
        float(probs.loc["WEEKDAY", "Low"]),
        float(probs.loc["WEEKDAY", "Moderate"]),
        float(probs.loc["WEEKDAY", "High"]),
    ],
    "Weekend": [
        float(probs.loc["WEEKENDS/HOLIDAY", "Low"]),
        float(probs.loc["WEEKENDS/HOLIDAY", "Moderate"]),
        float(probs.loc["WEEKENDS/HOLIDAY", "High"]),
    ],
}


# ----------------------------
# 6) Print results + diagnostics
# ----------------------------
print("Files loaded:", len(paths))
print("Rows used:", len(data))
print("Station filter:", STATIONS)
print(f"Demand bin thresholds: q{int(LOW_Q*100)}={q_low:.2f}, q{int(HIGH_Q*100)}={q_high:.2f}")
print("\nP(Demand | DAY_TYPE) based on hourly volumes:")
print(probs[["Low", "Moderate", "High"]])

print("\nCAL_DAYTYPE (use this in your model):")
print(cal_daytype)

print("\nNOTE:")
print("- 'Weekend' above corresponds to LTA DAY_TYPE='WEEKENDS/HOLIDAY'.")
print("- You cannot compute CAL_HOLIDAY (Yes/No) from this dataset alone without a holiday calendar + daily-level linkage.")

import glob
import pandas as pd

# ----------------------------
# CONFIG
# ----------------------------
DATA_GLOB = r"C:\\Users\\Flipp\\OneDrive\\Documents\\Desktop\\AICT-Assignment\\transport_node_train_202512\\transport_node_train_202512.*csv"  # <-- change to your folder
STATIONS = {"CG2"}   # Change if needed

PEAK_HOURS = set(range(7, 10)) | set(range(17, 20))  # 7–9, 17–19


# ----------------------------
# LOAD DATA
# ----------------------------
dfs = [pd.read_csv(p) for p in glob.glob(DATA_GLOB)]
data = pd.concat(dfs, ignore_index=True)

data["PT_CODE"] = data["PT_CODE"].str.upper()
data["DAY_TYPE"] = data["DAY_TYPE"].str.upper()

if STATIONS:
    data = data[data["PT_CODE"].isin(STATIONS)]

# Demand proxy
data["VOLUME"] = data["TOTAL_TAP_IN_VOLUME"] + data["TOTAL_TAP_OUT_VOLUME"]

# Time bucket
def time_bucket(h):
    return "Peak" if h in PEAK_HOURS else "Off-Peak"

data["TIME_BUCKET"] = data["TIME_PER_HOUR"].apply(time_bucket)

# ----------------------------
# DEMAND DISCRETISATION
# ----------------------------
q30 = data["VOLUME"].quantile(LOW_Q)
q70 = data["VOLUME"].quantile(HIGH_Q)

def volume_to_demand(v):
    if v <= q30:
        return "Low"
    if v >= q70:
        return "High"
    return "Moderate"

data["DEMAND"] = data["VOLUME"].apply(volume_to_demand)

# ----------------------------
# CAL_TIME
# ----------------------------
counts = (
    data.groupby(["TIME_BUCKET", "DEMAND"])
        .size()
        .unstack(fill_value=0)
)

probs = counts.div(counts.sum(axis=1), axis=0)







# ----------------------------
# 1) State names
# ----------------------------
STATE = {
    "Season": ["Northeast Monsoon", "Southwest Monsoon", "Inter-monsoon"],
    "Weather": ["Clear", "Rainy", "Thunderstorms"],
    "Time": ["Peak", "Off-Peak"],
    "DayType": ["Weekday", "Weekend"],
    "Holiday": ["Yes", "No"],
    "Mode": ["Today", "Future"],
    "Service": ["Normal", "Reduced", "Disrupted"],
    "Demand": ["Low", "Moderate", "High"],
    "Crowding": ["Low", "Moderate", "High"],
}


# ----------------------------
# 2) Define BN structure
# ----------------------------
model = DiscreteBayesianNetwork(
    [
        ("Season", "Weather"),
        ("Weather", "Demand"),
        ("Time", "Demand"),
        ("DayType", "Demand"),
        ("Holiday", "Demand"),
        ("Mode", "Service"),
        ("Demand", "Crowding"),
        ("Service", "Crowding"),
        ("Mode", "Crowding"),
    ]
)


# ----------------------------
# 3) Priors (roots) + Weather|Season
# ----------------------------
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

# Example seasonal weather mix (keep or tune if you have better priors)
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
    state_names={"Weather": STATE["Weather"], "Season": STATE["Season"]},
)

cpd_TIME = TabularCPD(
    variable="Time",
    variable_card=2,
    values=[[0.16], [0.84]],  # Peak, Off-Peak 530am-1230am 
    state_names={"Time": STATE["Time"]},
)

cpd_DAYTYPE = TabularCPD(
    variable="DayType",
    variable_card=2,
    values=[[5 / 7], [2 / 7]],
    state_names={"DayType": STATE["DayType"]},
)

# If you have the actual holiday rate for your study period, replace this.
cpd_HOLIDAY = TabularCPD(
    variable="Holiday",
    variable_card=2,
    values=[[11/365], [354/365]],  # Yes, No
    state_names={"Holiday": STATE["Holiday"]},
)

cpd_MODE = TabularCPD(
    variable="Mode",
    variable_card=2,
    values=[[0.50], [0.50]],
    state_names={"Mode": STATE["Mode"]},
)


# ----------------------------
# 4) CPT: Service | Mode  (document values)
# ----------------------------
# Columns correspond to Mode in order: Today, Future
cpd_SERVICE = TabularCPD(
    variable="Service",
    variable_card=3,
    values=[
        # Normal
        [0.9962, 0.991422],
        # Reduced
        [0.0037, 0.008578],
        # Disrupted
        [0.0001, 0.000000000001],
    ],
    evidence=["Mode"],
    evidence_card=[2],
    state_names={"Service": STATE["Service"], "Mode": STATE["Mode"]},
)


# ----------------------------
# 5) CPT: Demand | Weather, Time, DayType, Holiday
# ----------------------------
# Single-parent calibration tables from your write-ups:
CAL_TIME = {
    "Peak": [
        probs.loc["Peak", "Low"],
        probs.loc["Peak", "Moderate"],
        probs.loc["Peak", "High"],
    ],
    "Off-Peak": [
        probs.loc["Off-Peak", "Low"],
        probs.loc["Off-Peak", "Moderate"],
        probs.loc["Off-Peak", "High"],
    ],
}
print("\nCAL_TIME (use this in your model):")
print(CAL_TIME)

CAL_DAYTYPE = {
    "Weekday": cal_daytype["Weekday"],
    "Weekend": cal_daytype["Weekend"],
}

#Source: LTA DataMall (Passenger Volume by Train Station).
#How to use: Download the "Monthly Passenger Volume" dataset. Compare CG2 (Changi Airport) against Raffles Place or Jurong East. You will notice that while Raffles Place drops ~80% on weekends, Changi often stays within 70–85% of its weekday volume due to leisure traffic.

CAL_HOLIDAY = {
    "Yes":        [0.15, 0.45, 0.40],
    "No":         [0.3, 0.50, 0.2],
}
# Weather is 3-state in the model; the doc provides a 2-state effect.
# This is a consistent split that preserves "worse weather -> higher demand".
CAL_WEATHER = {
    "Clear":          [0.30, 0.50, 0.20],
    "Rainy":          [0.12, 0.46, 0.42],
    "Thunderstorms":  [0.08, 0.44, 0.48],
}

BASE_DEMAND = [0.3, 0.50, 0.2]  # neutral prior

def _safe_normalize(p):
    s = sum(p)
    if s <= 0:
        # Fallback to uniform
        return [1/3, 1/3, 1/3]
    return [x / s for x in p]

def combine_calibrations(weather: str, time: str, daytype: str, holiday: str, alpha: float = 0.15):
    """Log-linear (multiplicative) combination of single-parent calibrations.

    alpha is a small smoothing term to avoid zero-probabilities.
    """
    w = CAL_WEATHER[weather]
    t = CAL_TIME[time]
    d = CAL_DAYTYPE[daytype]
    h = CAL_HOLIDAY[holiday]

    # Multiply component-wise with a base prior, then normalize.
    raw = [
        (BASE_DEMAND[i] + alpha) * (w[i] + alpha) * (t[i] + alpha) * (d[i] + alpha) * (h[i] + alpha)
        for i in range(3)
    ]
    return _safe_normalize(raw)

# Build CPT columns in pgmpy evidence order: Weather, Time, DayType, Holiday
cols = []
for w in STATE["Weather"]:
    for t in STATE["Time"]:
        for d in STATE["DayType"]:
            for h in STATE["Holiday"]:
                cols.append(combine_calibrations(w, t, d, h))

dem_low  = [c[0] for c in cols]
dem_med  = [c[1] for c in cols]
dem_high = [c[2] for c in cols]

cpd_DEMAND = TabularCPD(
    variable="Demand",
    variable_card=3,
    values=[dem_low, dem_med, dem_high],
    evidence=["Weather", "Time", "DayType", "Holiday"],
    evidence_card=[3, 2, 2, 2],
    state_names={
        "Demand": STATE["Demand"],
        "Weather": STATE["Weather"],
        "Time": STATE["Time"],
        "DayType": STATE["DayType"],
        "Holiday": STATE["Holiday"],
    },
)


# ----------------------------
# 6) CPT: Crowding | Demand, Service, Mode
# ----------------------------
# Evidence order here is: Demand, Service, Mode
TODAY = {
    ("Low", "Normal"):      [0.90, 0.08, 0.02],
    ("Low", "Reduced"):     [0.40, 0.50, 0.10],
    ("Low", "Disrupted"):   [0.10, 0.30, 0.60],
    ("Moderate", "Normal"): [0.15, 0.75, 0.10],
    ("Moderate", "Reduced"):[0.05, 0.55, 0.40],
    ("Moderate", "Disrupted"):[0.01, 0.29, 0.70],
    ("High", "Normal"):     [0.05, 0.25, 0.70],
    ("High", "Reduced"):    [0.01, 0.09, 0.90],
    ("High", "Disrupted"):  [0.01, 0.01, 0.98],
}

FUTURE = {
    ("Low", "Normal"):      [0.93, 0.06, 0.01],
    ("Low", "Reduced"):     [0.55, 0.40, 0.05],
    ("Low", "Disrupted"):   [0.15, 0.35, 0.50],
    ("Moderate", "Normal"): [0.25, 0.65, 0.10],
    ("Moderate", "Reduced"):[0.12, 0.68, 0.20],
    ("Moderate", "Disrupted"):[0.03, 0.47, 0.50],
    ("High", "Normal"):     [0.20, 0.55, 0.25],
    ("High", "Reduced"):    [0.05, 0.60, 0.35],
    ("High", "Disrupted"):  [0.01, 0.09, 0.90],
}

crowd_cols = []
for dem in STATE["Demand"]:
    for srv in STATE["Service"]:
        for mode in STATE["Mode"]:
            table = TODAY if mode == "Today" else FUTURE
            crowd_cols.append(table[(dem, srv)])

crowd_low  = [c[0] for c in crowd_cols]
crowd_med  = [c[1] for c in crowd_cols]
crowd_high = [c[2] for c in crowd_cols]

cpd_CROWDING = TabularCPD(
    variable="Crowding",
    variable_card=3,
    values=[crowd_low, crowd_med, crowd_high],
    evidence=["Demand", "Service", "Mode"],
    evidence_card=[3, 3, 2],
    state_names={
        "Crowding": STATE["Crowding"],
        "Demand": STATE["Demand"],
        "Service": STATE["Service"],
        "Mode": STATE["Mode"],
    },
)


# ----------------------------
# 7) Add CPDs + validate
# ----------------------------
model.add_cpds(
    cpd_SEASON,
    cpd_WEATHER,
    cpd_TIME,
    cpd_DAYTYPE,
    cpd_HOLIDAY,
    cpd_MODE,
    cpd_SERVICE,
    cpd_DEMAND,
    cpd_CROWDING,
)

assert model.check_model(), "Model is invalid. Check CPT dimensions / sums."


# ----------------------------
# 8) Inference helper + sample scenarios
# ----------------------------
infer = VariableElimination(model)

def run_scenario(name: str, evidence: dict):
    dist = infer.query(variables=["Crowding"], evidence=evidence, show_progress=False)
    # pgmpy returns a DiscreteFactor for single-variable queries
    factor = dist
    print(f"\nScenario: {name}")
    print("Evidence:", evidence)
    for state, prob in zip(factor.state_names["Crowding"], factor.values):
        print(f"  P(Crowding={state}) = {float(prob):.4f}")
    return factor

# ----------------------------
# 9) Ten test scenarios (add below your existing ones)
# ----------------------------
TEST_SCENARIOS = [
    # 1) Worst-case operational stress (Today)
    (
        "Thunderstorms + Peak + Weekday + Holiday=Yes + Disrupted (Today)",
        {"Weather": "Thunderstorms", "Time": "Peak", "DayType": "Weekday", "Holiday": "Yes", "Mode": "Today", "Service": "Disrupted"},
    ),
    # 2) Same, Future mode
    (
        "Thunderstorms + Peak + Weekday + Holiday=Yes + Disrupted (Future)",
        {"Weather": "Thunderstorms", "Time": "Peak", "DayType": "Weekday", "Holiday": "Yes", "Mode": "Future", "Service": "Disrupted"},
    ),

    # 3) Heavy rain, reduced service, weekday peak (Today)
    (
        "Rainy + Peak + Weekday + Holiday=No + Reduced (Today)",
        {"Weather": "Rainy", "Time": "Peak", "DayType": "Weekday", "Holiday": "No", "Mode": "Today", "Service": "Reduced"},
    ),
    # 4) Same, Future mode
    (
        "Rainy + Peak + Weekday + Holiday=No + Reduced (Future)",
        {"Weather": "Rainy", "Time": "Peak", "DayType": "Weekday", "Holiday": "No", "Mode": "Future", "Service": "Reduced"},
    ),

    # 5) Clear off-peak weekday normal service (Today) — “quiet baseline”
    (
        "Clear + Off-Peak + Weekday + Holiday=No + Normal (Today)",
        {"Weather": "Clear", "Time": "Off-Peak", "DayType": "Weekday", "Holiday": "No", "Mode": "Today", "Service": "Normal"},
    ),
    # 6) Same, Future mode
    (
        "Clear + Off-Peak + Weekday + Holiday=No + Normal (Future)",
        {"Weather": "Clear", "Time": "Off-Peak", "DayType": "Weekday", "Holiday": "No", "Mode": "Future", "Service": "Normal"},
    ),

    # 7) Weekend holiday peak travel, normal service (Today)
    (
        "Clear + Peak + Weekend + Holiday=Yes + Normal (Today)",
        {"Weather": "Clear", "Time": "Peak", "DayType": "Weekend", "Holiday": "Yes", "Mode": "Today", "Service": "Normal"},
    ),
    # 8) Same, Future mode
    (
        "Clear + Peak + Weekend + Holiday=Yes + Normal (Future)",
        {"Weather": "Clear", "Time": "Peak", "DayType": "Weekend", "Holiday": "Yes", "Mode": "Future", "Service": "Normal"},
    ),

    # 9) Rainy off-peak weekend, reduced service (Today) — “messy but not peak”
    (
        "Rainy + Off-Peak + Weekend + Holiday=No + Reduced (Today)",
        {"Weather": "Rainy", "Time": "Off-Peak", "DayType": "Weekend", "Holiday": "No", "Mode": "Today", "Service": "Reduced"},
    ),
    # 10) Same, Future mode
    (
        "Rainy + Off-Peak + Weekend + Holiday=No + Reduced (Future)",
        {"Weather": "Rainy", "Time": "Off-Peak", "DayType": "Weekend", "Holiday": "No", "Mode": "Future", "Service": "Reduced"},
    ),
]

if __name__ == "__main__":
    for name, evidence in TEST_SCENARIOS:
        run_scenario(name, evidence)
