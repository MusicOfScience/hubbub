# Modelling Assumptions

## Preference Flows

### Federal Preferential Voting

Australia's federal elections use full preferential voting (compulsory preferences). This means:
- Exhaustion rate = 0%
- All votes eventually flow to one of the two TCP candidates

### Default Preference Flows

These defaults are based on historical AEC preference data from 2016–2022:

| Source Party | → ALP | → LIB |
|---|---|---|
| Greens (GRN) | 75% | 25% |
| Independent (IND) | 55% | 45% |
| One Nation (ONP) | 30% | 70% |
| Other (OTH) | 50% | 50% |

These flows can be adjusted in the **Preference Model** and **Swingometer** pages.

### Preference Flow Uncertainty

Preference flows have historically varied by ±5–10 percentage points depending on:
- Candidate how-to-vote cards
- Local factors
- Candidate ideology (e.g. teal independents may attract more progressive preferences)

## Swing Methodology

### Primary Vote Swing

Swing is calculated as a simple change in vote share (percentage points):
```
swing = current_pct - previous_pct
```

### TCP Swing

TCP swing is the change in two-candidate preferred percentage:
```
tcp_swing = current_tcp_pct - previous_tcp_pct
```

### Weighted Swing

When aggregating booth-level swings, booths are weighted by enrolment to produce an enrolment-weighted average swing.

## Monte Carlo Simulation

### Methodology

The simulation uses a normal distribution centred on the projected margin:
```
outcomes ~ Normal(projected_margin, std_dev)
```

### Default Parameters

| Parameter | Default | Notes |
|---|---|---|
| Standard deviation | 1,500 votes | Based on typical count uncertainty |
| Iterations | 10,000 | Balances accuracy vs performance |
| Win threshold | 0 votes | ALP wins if margin > 0 |

### Probability of Victory

The probability of victory is the fraction of simulation iterations in which the projected margin favours the candidate:
```
P(ALP wins) = count(outcomes > 0) / n_iterations
```

## Vote Type Assumptions

### Outstanding Vote Lean

Different vote types have historically shown different partisan leans:

| Vote Type | ALP Lean | LIB Lean | Notes |
|---|---|---|---|
| Ordinary booth | ~equal | ~equal | Counted on night |
| Pre-poll | ALP +2pp | — | Trend toward ALP since 2016 |
| Postal | LIB +8pp | — | Older demographic skew |
| Absent | ALP +1pp | — | Younger mobile voter skew |
| Provisional | ~equal | — | Smallest category |

### Projection Formula

```
projected_margin = current_margin + sum(outstanding[type] * (alp_lean[type] - 0.5) * 2)
```

## Count Progress Classification

| Status | Counted % |
|---|---|
| Early | < 25% |
| Developing | 25–49% |
| Mature | 50–74% |
| Near-final | ≥ 75% |

## Recount Risk

Under Australian electoral law, a recount may be requested when:
- Federal House of Representatives: margin < 100 votes (automatic recount risk)
- Margin < 500 votes: elevated concern warranting close monitoring
