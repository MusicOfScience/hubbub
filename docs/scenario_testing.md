# Scenario Testing

This guide explains how to create, save, and test election scenarios in MOE.

## What is a Scenario?

A scenario is a set of assumptions about:
- **Primary vote swings** — how much each party's vote has moved since the previous election
- **Preference flows** — what share of minor party votes flows to each TCP candidate
- **Postal lean** — the partisan lean of postal votes
- **Turnout and informal rate** — voter participation and informal ballot rates

## Creating Scenarios

### Via the Swingometer Page

1. Navigate to **Swingometer** (page 3)
2. Adjust the sliders for swings and preference flows
3. Observe the live TCP result update
4. Click **💾 Save Scenario to Session** to store

### Via JSON File

Create a scenario JSON file in `data/sample/`:

```json
{
  "scenario_id": "alp_wave",
  "name": "ALP Wave Scenario",
  "swing_alp": 3.5,
  "swing_lib": -2.0,
  "swing_grn": 0.5,
  "swing_ind": -1.0,
  "grn_to_alp_pref": 78.0,
  "grn_to_lib_pref": 22.0,
  "ind_to_alp_pref": 58.0,
  "ind_to_lib_pref": 42.0,
  "postal_alp_lean": 44.0,
  "postal_lib_lean": 56.0,
  "turnout_pct": 94.5,
  "informal_pct": 2.8
}
```

### Loading a Scenario

```python
from backend.utils.helpers import load_json
scenario = load_json("data/sample/scenario_alp_wave.json")
```

## Testing Scenarios Programmatically

```python
from backend.analysis.swing import apply_swing_scenario
from backend.analysis.preferences import PreferenceModel

# Base votes from previous election
base_votes = {"ALP": 35.5, "LIB": 37.8, "GRN": 13.2, "IND": 10.1, "informal": 3.4}

# Apply swings
swings = {"ALP": 3.5, "LIB": -2.0, "GRN": 0.5, "IND": -1.0}
adjusted = apply_swing_scenario(base_votes, swings)

# Calculate TCP
model = PreferenceModel([])
model.adjust_preference_flow("GRN", "ALP", 78.0)
model.adjust_preference_flow("IND", "ALP", 58.0)

tcp = model.flow_to_tcp(adjusted, model._pref_flows)
print(f"ALP TCP: {tcp['ALP']:.1f}% | LIB TCP: {tcp['LIB']:.1f}%")
```

## Sensitivity Analysis

Run a sweep of scenarios using the Monte Carlo engine:

```python
from backend.analysis.monte_carlo import MonteCarloEngine

# Test across a range of std deviations
for std_dev in [500, 1000, 1500, 2000, 2500]:
    engine = MonteCarloEngine(base_margin=800, std_dev=std_dev)
    results = engine.run_simulation(10000)
    prob = engine.probability_of_victory(results, "ALP")
    ci = engine.confidence_interval(results, 0.95)
    print(f"σ={std_dev:,}: P(ALP)={prob:.1%}, 95% CI: [{ci[0]:+,}, {ci[1]:+,}]")
```

## Predefined Scenario Library

| Scenario | ALP Swing | GRN→ALP | Description |
|---|---|---|---|
| Default | 0.0 | 75% | No change from 2022 |
| ALP Wave | +3.5 | 78% | Strong national ALP swing |
| LIB Recovery | -2.0 | 72% | Liberal recovery from 2022 losses |
| Green Surge | 0.0 | 80% | Higher Greens preferences to ALP |
| Postal Heavy | 0.0 | 75% | Strong postal vote LIB lean |

## Scenario Validation

A valid scenario must satisfy:
- All swings are in range [-20, +20] percentage points
- Preference flows sum to 100% (ALP + LIB = 100 for each minor party)
- Turnout between 80% and 100%
- Informal rate between 0% and 10%

```python
def validate_scenario(scenario: dict) -> bool:
    for party in ["alp", "lib", "grn", "ind"]:
        swing = scenario.get(f"swing_{party}", 0)
        if not (-20 <= swing <= 20):
            return False
    grn_total = scenario.get("grn_to_alp_pref", 75) + scenario.get("grn_to_lib_pref", 25)
    if abs(grn_total - 100) > 0.1:
        return False
    return True
```
