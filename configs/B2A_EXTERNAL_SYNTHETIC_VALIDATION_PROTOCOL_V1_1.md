# B2A External-Synthetic Validation Protocol v1.1

**Study:** When Is Causal Structure Enough? Decision Sufficiency of Binary Structural Indicators for Pairwise Intervention Choice in Educational AI
**Estimator:** T2-B2A
**Validation type:** External-Synthetic Validation
**Protocol status:** PROSPECTIVELY AMENDED AND FROZEN BEFORE DATA GENERATION
**Date:** September 2026

> **Amendment/provenance note:** V1.1 supersedes V1 prospectively following a
> pre-generation implementation audit. No validation graph, trajectory, query,
> prediction, or ground-truth effect had been generated before this amendment.
>
> V1 remains the historical pre-audit freeze.
>
> This protocol prospectively defines an independent synthetic validation study
> for the frozen B2A causal-effect estimator.
>
> It is used only if organizer-side held-out Task 2 scoring is unavailable or
> unavailable within the study timeline.
>
> No data from this validation study existed and no validation result had been
> inspected at the time of protocol freeze.

### Scientific Amendment Boundary

This amendment resolves prospective design ambiguity only.

It does not change:

- the B2A estimator;
- alpha = 1.0;
- state-only features;
- action-specific Ridge;
- the X_(t-1), A_t -> X_(t+2) alignment;
- 6 environments;
- 400 training trajectories per environment;
- 120 states per trajectory;
- 40 queries per environment;
- 500 paired Monte Carlo draws per query;
- primary metrics.

---

## 1. Purpose

The purpose of this study is to test whether the frozen B2A estimation
procedure can recover intervention-specific effects under synthetic causal
data-generating processes that are independently specified from the NeurIPS
2022 Causal Education benchmark development cohort.

The validation tests estimator generalization under controlled causal
conditions.

It is not intended to:

- reproduce the hidden NeurIPS simulator;
- optimize B2A;
- create a simulator tailored to B2A;
- establish real-world educational validity.

---

## 2. Validation Classification

This study is reported as:

**EXTERNAL-SYNTHETIC VALIDATION**

provided that:

- the DGP is frozen before generation;
- random seeds are frozen before generation;
- B2A remains unchanged;
- no validation result informs estimator modification.

It is not:

- real-world validation;
- benchmark held-out validation;
- proof of educational causal truth.

---

## 3. Frozen B2A Procedure

The estimator is unchanged from the retained Task 2 B2A procedure.

B2A is:

- action-specific T-learner;
- one model per environment and action;
- multi-output Ridge regression;
- alpha = 1.0;
- state features only;
- no temporal-delta augmentation;
- no nonlinear model substitution;
- no hyperparameter tuning.

Frozen temporal alignment:

X_(t-1), A_t -> X_(t+2)

This alignment must not be changed to use X_t.

For every validation query, condition on:

X_(t-1) = x

The simulator transition is exactly:

X_(s+1) = f(X_s, A_s, epsilon_(s+1))

The ground-truth intervention timeline and its nuisance-action marginalization
are defined in Section 17.

The estimator must be applied without modification across all validation
environments.

No environment-specific model selection is allowed.

## 4. Design Principle

The validation DGP must not be designed to imitate B2A's assumptions exactly.

The study therefore includes multiple causal regimes with controlled variation
in:

- graph density;
- direct and mediated effects;
- intervention strength;
- noise;
- action prevalence;
- degree of nonlinearity.

The objective is to test where the frozen lightweight estimator works and where
its assumptions begin to fail.

Failure in a difficult regime is scientifically informative and must not be
used as justification for post-hoc estimator modification.

---

## 5. Number of Validation Environments

Use exactly:

**6 independent validation environments**

Each environment has:

- 20 state variables / constructs;
- 8 possible intervention actions;
- one dynamic causal graph;
- one frozen DGP specification;
- one training trajectory dataset;
- one held-out intervention-query set.

Environment IDs:

- EXT0
- EXT1
- EXT2
- EXT3
- EXT4
- EXT5

---

## 6. Causal Graph Generation

Each environment uses a directed acyclic graph over 20 constructs.

Node ordering is fixed from:

0 through 19.

Edges may only be generated from lower-order nodes to higher-order nodes.

This guarantees acyclicity.

For every admissible ordered pair i < j, sample the edge independently using:

Bernoulli(p)

The adjacency convention is:

adjacency[i,j] = 1 means i -> j.

Graph regimes are frozen as:

### EXT0 — Sparse Linear

Expected edge density: low.

Edge probability among admissible ordered pairs:

p = 0.08

Mechanisms are linear.

---

### EXT1 — Moderate Linear

Edge probability:

p = 0.15

Mechanisms are linear.

---

### EXT2 — Dense Linear

Edge probability:

p = 0.25

Mechanisms are linear.

---

### EXT3 — Sparse Mildly Nonlinear

Edge probability:

p = 0.08

Mechanisms include a frozen mild nonlinear transformation.

---

### EXT4 — Moderate Mildly Nonlinear

Edge probability:

p = 0.15

Mechanisms include the same nonlinear family as EXT3.

---

### EXT5 — Moderate Linear with Downstream-Mediated Query Emphasis

Edge probability:

p = 0.15

Noise standard deviation:

sigma = 0.15

Mechanisms are linear.

After ordinary Bernoulli(p = 0.15) DAG generation, sample the eight distinct
action-target constructs from nodes that have at least one outgoing child where
possible.

The previous V1 requirement for multiple causal chains of length at least 3 is
removed. Under the frozen transition contract, A_t first changes its targeted
construct in X_(t+1), and by X_(t+2) that effect can propagate through one graph
edge. Longer graph paths are therefore not fully observable at the frozen B2A
horizon.

EXT5 emphasizes action effects that reach queried outcomes through a downstream
structural edge within the frozen t+2 horizon. It does not test arbitrary
long-range mediation.

No graph may be regenerated based on saturation, effect size, estimator
performance, or query feasibility. If EXT5 fails the predefined feasibility
condition in Section 15, generation must stop rather than regenerate the
environment or change its seed.

## 7. Random Seeds

The following seeds are frozen before data generation:

- EXT0: 1101
- EXT1: 2202
- EXT2: 3303
- EXT3: 4404
- EXT4: 5505
- EXT5: 6606

The same environment seed governs:

- graph generation;
- structural coefficients;
- trajectory noise;
- action-policy randomness;
- query generation,

using reproducibly derived sub-seeds if needed.

No seed may be replaced because the resulting environment is inconvenient or
produces poor estimator performance.

---

## 8. Structural Coefficients

For every generated edge, coefficient magnitude is sampled from:

Uniform(0.15, 0.60)

Coefficient sign is sampled independently with equal probability:

+1 or -1

Thus:

beta_ij = sign * magnitude

Coefficients are frozen once generated.

No coefficient is changed after outcome inspection.

---

## 9. Dynamic State Mechanism

The simulator transition is exactly:

X_(s+1) = f(X_s, A_s, epsilon_(s+1))

Each state variable evolves from:

1. its own previous state;
2. its causal parents;
3. action A_s where applicable;
4. random noise epsilon_(s+1).

For linear environments, the pre-activation state is:

z_j(s+1) =
rho * X_j(s)
+ sum_i beta_ij X_i(s)
+ intervention_term_j(A_s)
+ epsilon_j(s+1)

where the parental sum is over generated edges i -> j, and:

rho = 0.50

Noise:

epsilon_j(s+1) ~ Normal(0, sigma^2)

The observed state is bounded using:

X_j(s+1) = tanh(z_j(s+1))

The same bounded output transformation is used across all environments so that
state scales remain comparable.

For every trajectory or query context:

X_j(0) ~ Uniform(-0.5, 0.5)

independently for all 20 constructs.

Noise is independent Gaussian noise across:

- nodes;
- time;
- trajectories;
- Monte Carlo draws,

with the environment-specific sigma frozen in Section 14.

Within each paired intervention/reference Monte Carlo draw, corresponding noise
values are shared between the two counterfactual worlds as common random
numbers.

## 10. Mild Nonlinearity

For EXT3 and EXT4 only, the parental contribution is modified to include:

0.75 * beta_ij * X_i(t)
+
0.25 * beta_ij * X_i(t)^2

before the final tanh transformation.

No higher-order neural or black-box mechanism is used.

The nonlinearity is intentionally mild and transparent.

---

## 11. Intervention Mechanism

There are exactly 8 intervention actions.

Each action targets one pre-selected construct.

The eight target constructs are sampled without replacement, so all eight
actions target distinct constructs. EXT5 additionally applies the target-node
rule in Section 6.

Target constructs are selected reproducibly from the 20 nodes using the frozen
environment seed and are frozen once generated.

An intervention adds an action-specific shift to the targeted construct's
pre-activation value.

Intervention strength is sampled once per action from:

Uniform(0.20, 0.50)

and then frozen.

Interventions may propagate through downstream causal pathways naturally.

## 12. Action Assignment Policy

Training trajectories must not use uniform action assignment only.

Each environment uses a stochastic, state-independent action policy with
unequal action probabilities.

Action probabilities are sampled once from:

Dirichlet(alpha = 2 for each of the 8 actions)

and frozen.

A minimum action probability of 0.03 must be enforced through a deterministic
simplex projection / redistribution procedure that guarantees:

- probabilities sum exactly to 1 within numerical tolerance;
- every probability remains >= 0.03.

The exact algorithm must be specified in the later non-scientific
implementation specification and tested before validation generation.

The purpose is to create realistic differences in action prevalence without
introducing hidden confounding.

The action assignment policy depends only on frozen action probabilities and
not on state or future outcomes.

## 13. Training Data Size

For each environment generate:

- 400 independent trajectories;
- exactly 120 states per trajectory.

Each training trajectory contains:

X_0 ... X_119

and exactly 119 actions:

A_0 ... A_118

where A_s governs the transition X_s -> X_(s+1).

The first 10 states, X_0 ... X_9, are burn-in and excluded from estimator
fitting.

Frozen B2A aligned rows use:

t = 11 ... 117 inclusive

with:

- feature: X_(t-1);
- action: A_t;
- target: X_(t+2).

Therefore each complete trajectory contributes exactly 107 eligible aligned
rows before any action-specific grouping.

Training data are generated before validation queries.

No validation query or query-context trajectory is included in the training
trajectories.

## 14. Noise Regimes

Noise standard deviation is fixed by environment:

- EXT0: sigma = 0.10
- EXT1: sigma = 0.15
- EXT2: sigma = 0.20
- EXT3: sigma = 0.10
- EXT4: sigma = 0.20
- EXT5: sigma = 0.15

These values are frozen before generation.

---

## 15. Validation Queries

Generate exactly:

**40 intervention queries per environment**

Total:

6 x 40 = 240 queries.

Generate exactly 40 independent query-context trajectories per environment,
separate from all B2A training trajectories.

For each query context:

- sample an independent initial state from the frozen initial-state
  distribution;
- simulate exactly 10 transitions using the frozen observational action policy;
- use X_10 as that query's conditioning state X_(t-1).

Query-context trajectories are never used for B2A fitting.

Each query contains:

- conditioning state;
- intervention action I;
- reference action R;
- target construct Y.

For EXT0 through EXT4, for each of the 40 queries:

- sample I uniformly from supported actions;
- sample R uniformly from the remaining supported actions, so I != R;
- sample Y uniformly from construct indices 0 through 19.

Sampling is independent of:

- B2A predictions;
- ground-truth effects;
- coefficient magnitudes;
- path existence.

Queries are sampled independently across query IDs. Repeated I/R/Y combinations
are permitted; conditioning states remain independently generated.

No query is removed or regenerated because its causal effect is zero, small,
large, unexpected, or difficult.

For EXT5 only:

- use only supported actions whose target construct has at least one outgoing
  child;
- sample I and R uniformly without replacement from that eligible action set;
- sample Y uniformly from the union of the immediate children of the target
  constructs of I and R;
- exclude the intervention-target constructs themselves from Y.

If fewer than two supported mediation-eligible actions exist, generation must
stop with a protocol-feasibility error. Do not regenerate the environment or
change the seed.

## 16. Query-Support Rule

Support counts use only the frozen B2A-eligible aligned training rows defined
in Section 13.

An action is supported if its total eligible-row count within the relevant
environment is:

n >= 100

The supported-action set is computed once per environment after training-data
generation and before query sampling.

For EXT0 through EXT4, query actions are sampled only from this supported set.
For EXT5, the additional mediation-eligibility rule in Section 15 applies.

No query-regeneration rule is used to repair action support.

## 17. Ground-Truth Intervention Effect

Ground-truth effect is computed using paired Monte Carlo intervention
simulation from the known DGP.

For every validation query, condition on:

X_(t-1) = x

Each paired Monte Carlo draw evaluates:

X_(t-1)
-> X_t using nuisance action A_(t-1)
-> X_(t+1) using do(A_t = I) or do(A_t = R)
-> X_(t+2) using nuisance action A_(t+1).

A_(t-1) and A_(t+1) are sampled from the frozen environment action policy.

For every paired Monte Carlo draw, intervention and reference worlds use:

- the same X_(t-1);
- the same A_(t-1);
- the same A_(t+1);
- identical exogenous noise draws;

and differ only in A_t = I versus A_t = R.

The action policy is state-independent, so the same nuisance-action draws can
be coupled across both worlds without post-intervention policy differences.

Thus the estimand marginalizes over nuisance actions and noise not included in
the frozen B2A feature set.

Use exactly:

500 Monte Carlo paired draws per query.

The ground-truth estimand is:

tau_GT =
E[Y_(t+2) | do(A_t = I), X_(t-1) = x]
-
E[Y_(t+2) | do(A_t = R), X_(t-1) = x]

Monte Carlo seeds must be reproducibly derived from:

environment seed + query ID.

Alongside tau_GT, report:

- paired-difference standard deviation;
- Monte Carlo standard error;
- running estimate at n = 100;
- running estimate at n = 250;
- final estimate at n = 500;
- split-half estimates using draws 1 ... 250 and 251 ... 500.

These diagnostics must never cause:

- extra draws;
- query deletion;
- query regeneration;
- DGP modification.

Ground-truth simulation code must not use B2A predictions.

## 18. B2A Validation Prediction

For each environment:

1. fit the frozen B2A procedure using only that environment's generated
   training trajectories;
2. fit one action-specific multi-output Ridge model per action;
3. alpha remains 1.0;
4. use state features only;
5. apply the frozen temporal alignment;
6. evaluate each validation query once.

For query q:

tau_hat(q) =
predicted target under intervention
-
predicted target under reference

No validation ground truth may be opened or used before all B2A predictions are
generated and frozen.

---

## 19. Blind Generation Sequence

The implementation must enforce:

1. generate and save DGP specifications;
2. generate and save training trajectories;
3. generate and save query definitions;
4. fit B2A;
5. generate all 240 predictions;
6. save predictions;
7. hash prediction file;
8. freeze the prediction artifact and implementation;
9. only then compute or reveal ground-truth intervention effects;
10. evaluate.

If practical implementation requires ground-truth simulator code to exist
before prediction generation, its outputs must remain unopened and unused until
predictions are frozen.

---

## 20. Primary Performance Metrics

Report:

- MAE;
- RMSE;
- Pearson correlation;
- Spearman correlation;
- sign agreement.

Report:

- pooled over 240 queries;
- separately for each environment.

Pooled RMSE is defined exactly as:

sqrt(mean over all 240 queries of squared prediction error)

It is not the arithmetic mean of six environment RMSE values.

For sign agreement:

- positive means value > 0;
- negative means value < 0;
- zero means value == 0 at full stored floating-point precision.

Report zero-effect queries separately.

A prediction counts as sign-agreeing only if its sign category exactly matches
the ground-truth sign category.

No epsilon practical-tie threshold is used in the primary validation.

No single metric defines validation success.

## 21. Additional Diagnostic Metrics

Also report:

- prediction range;
- ground-truth effect range;
- mean predicted effect;
- mean ground-truth effect;
- per-query absolute error;
- effect-sign confusion counts.

These are diagnostic rather than primary ranking criteria.

---

## 22. Uncertainty

Use environment-stratified bootstrap with:

10,000 replicates

for pooled:

- MAE;
- RMSE;
- sign agreement.

Report 95% bootstrap confidence intervals.

The environment-stratified bootstrap quantifies query-level uncertainty
conditional on the six realized environments.

Per-environment metrics are reported descriptively with appropriate uncertainty
where feasible.

## 23. Predefined Regime Comparison

The following comparisons are frozen before validation:

- sparse vs moderate vs dense linear;
- linear vs mildly nonlinear;
- lower-noise vs higher-noise environments;
- direct/ordinary graphs vs the downstream-mediated query-emphasis
  environment.

The six environments are six realized DGPs, not six independent replications
of each regime.

Regime comparisons are descriptive and partially confounded. They do not
isolate causal effects of graph density, noise, or nonlinearity.

The study must not be redesigned into a factorial experiment.

The purpose is diagnostic characterization, not post-hoc model selection.

## 24. No Success Threshold

No arbitrary threshold such as:

"RMSE must be below X"

is defined as a pass/fail criterion.

The validation is interpreted by:

- absolute performance;
- uncertainty;
- consistency across environments;
- degradation under known assumption violations;
- comparison with the already documented development performance.

The study must report unfavorable results.

---

## 25. Comparison With Development Results

The local-development Task 2 B2A results may be shown as historical reference:

- MAE approximately 0.0657;
- RMSE approximately 0.0938;
- Spearman approximately 0.787;
- sign agreement 0.86.

These are not treated as target thresholds.

The external-synthetic validation is not expected to reproduce identical
values because the DGP is intentionally different.

---

## 26. Claim Boundaries

The validation may support claims about:

- generalization of the frozen B2A procedure across independently specified
  synthetic causal environments;
- descriptive performance patterns across the realized environments, which
  vary in graph density, noise, downstream mediation, and mild nonlinearity;
- robustness or limitations of a lightweight transparent causal-effect
  estimator.

The validation does not establish:

- causal effects of graph density, noise, mediation, or nonlinearity on
  estimator performance;
- real-world educational effectiveness;
- external validity to universities or classrooms;
- causal truth outside the generated DGPs;
- superiority over state-of-the-art causal estimators;
- equivalence with the hidden NeurIPS simulator.

## 27. Failure Interpretation

Poor performance in one or more environments is not grounds to modify B2A
within this validation.

Such results must instead be interpreted as evidence about the estimator's
operating boundaries.

Any future improved estimator must be treated as a separate method and cannot
replace B2A retrospectively in this frozen validation.

---

## 28. Reproducibility Requirements

Save and hash:

- protocol file;
- DGP specification;
- environment seeds and derived sub-seeds;
- graph adjacency matrices;
- coefficients;
- intervention definitions;
- action probabilities;
- generated training datasets;
- query definitions and conditioning states;
- frozen B2A predictions;
- Monte Carlo ground truth and convergence diagnostics;
- evaluation summaries.

Record stable publication metadata:

- Python version;
- package versions;
- protocol version;
- implementation-specification version;
- scientific-payload hashes.

The exact PRNG library, sub-seed arithmetic, serialization schemas, bootstrap
seed, and file schemas must be fixed in the subsequent non-scientific
implementation specification before validation generation. They are not
specified in this scientific protocol amendment.

## 29. Required Canonical Outputs

The validation study must eventually produce:

- `results/b2a_external_synthetic_dgp_spec_v1.json`
- `results/b2a_external_synthetic_queries_v1.csv`
- `results/b2a_external_synthetic_predictions_v1.csv`
- `results/b2a_external_synthetic_ground_truth_v1.csv`
- `results/b2a_external_synthetic_summary_v1.csv`
- `results/b2a_external_synthetic_environment_summary_v1.csv`

A dedicated notebook may be created after freeze:

`notebooks/b2a_external_synthetic_validation.ipynb`

---

## 30. Organizer Evaluation Priority

If the NeurIPS 2022 organizers provide an official one-shot held-out Task 2
evaluation before this external-synthetic validation is executed, the official
held-out evaluation remains the preferred independent-validation evidence.

The external-synthetic study may still be retained as a robustness and
generalization analysis.

---

## 31. Freeze Rule

V1.1 prospectively supersedes V1. V1 must remain unchanged as the historical
pre-audit freeze.

This V1.1 protocol must be versioned and frozen before:

- any external-synthetic RNG call;
- generating any external-synthetic graph;
- generating any external-synthetic trajectory;
- generating any validation query;
- running B2A on the validation environments;
- generating any prediction;
- generating any ground-truth effect or validation result.

After generation begins:

- DGP definitions must not change;
- seeds must not change;
- B2A must not change;
- primary metrics must not change;
- primary regime comparisons must not change.

Corrections are permitted only for implementation errors that invalidate the
frozen intended design.

Every correction must be documented with:

- error;
- correction;
- whether predictions had been generated;
- whether ground-truth effects had been inspected.

## 32. Immediate Next Step

After this V1.1 protocol is frozen:

1. create the subsequent non-scientific implementation specification;
2. specify and test the deterministic action-probability lower-bound algorithm
   before any validation generation;
3. verify implementation fidelity and leakage boundaries without generating
   validation artifacts;
4. only then implement the blind external-synthetic validation sequence.
