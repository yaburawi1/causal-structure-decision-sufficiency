# Structure vs Effect — Decision Protocol v1

**Study:** When Is Causal Structure Enough? Decision Sufficiency of Binary Structural Indicators for Pairwise Intervention Choice in Educational AI  
**Study role:** Decision-level structure-versus-effect experiment  
**Protocol status:** FROZEN BEFORE FIRST DECISION-LEVEL EXECUTION  
**Date:** September 2026

> This is a prospectively frozen protocol for the new decision-level experiment, not a formal preregistration. Prior Task 1, Task 2, and structure–effect results had already been inspected before this protocol was created.

---

## 1. Purpose

This protocol defines the decision-level experiment used to examine when
binary structural indicators are sufficient for pairwise choice between
educational interventions, and when intervention-specific causal-effect
evidence changes the resulting decision.

The experiment is motivated by a distinction between three computational
functions:

1. causal structure learning,
2. intervention-specific causal-effect estimation,
3. action selection.

The study does not attempt to show that these functions are theoretically
equivalent or different; those distinctions are already established in the
causal decision-making literature.

Instead, the experiment evaluates their practical relationship within the
NeurIPS 2022 Causal Education synthetic benchmark.

The central question is:

> When is structural causal evidence sufficient for selecting an educational
> intervention, and when does intervention-specific effect information
> materially change the decision?

---

## 2. Scope

The primary experiment uses the synthetic components of the
NeurIPS 2022 Causal Education benchmark:

- Task 1 for structural causal information.
- Task 2 for intervention-specific causal effects.

The primary analysis is restricted to benchmark queries for which Task 2
defines:

- an intervention construct,
- a reference construct,
- a target construct,
- and a ground-truth intervention contrast.

Each query is a pairwise intervention choice between candidate `I` and
reference candidate `R` for target outcome `Y`. Multi-action intervention
choice is outside the current empirical scope; no claim about a new
multi-action experiment is made.

Results are interpreted only within the tested synthetic benchmark and its
data-generating processes.

No result from this experiment is treated as real-world educational causal
truth.

---

## 3. Scientific Boundaries

The following distinctions are maintained throughout the study:

Structure != Effect != Decision

A structural relation such as:

A -> B

means that A is represented as a direct causal parent of B within the relevant
benchmark causal structure.

It does not mean that intervening on A is necessarily the best available action
for improving B under a particular intervention comparison.

An intervention contrast:

tau(I,R -> Y)

compares the expected outcome for target Y under intervention I against
reference intervention R.

It does not by itself establish that I is a direct structural parent of Y.

---

## 4. Research Questions

### RQ1 — Structural–Effect Correspondence

To what extent does structural causal evidence correspond to
intervention-specific causal effects across the benchmark environments?

### RQ2 — Structural Sufficiency

When is structural causal evidence sufficient, ambiguous, or misleading for
selecting between candidate educational interventions?

### RQ3 — Decision Consequence

What decision disagreement and selective regret arise when structural causal
evidence is used in place of intervention-specific effect evidence?

---

## 5. Evidence Layers

The experiment separates four evidence layers.

### 5.1 Ground-Truth Structure

The benchmark ground-truth causal adjacency structure.

This layer answers:

> If the true benchmark structure were known perfectly, would structural
> information alone be sufficient for the intervention decision?

### 5.2 Learned Structure

The retained Task 1 structural method:

**Method D**

Method D is treated as the current lightweight structural-evidence generator.

It is not treated as the definition of a complete causal decision system and
is not interpreted as real-world causal truth.

### 5.3 Ground-Truth Effect

The Task 2 benchmark ground-truth intervention contrast:

tau_GT(I,R -> Y)

This layer defines the oracle preference between intervention and reference.

### 5.4 Estimated Effect

The retained Task 2 estimator:

**T2-B2A**

with estimated contrast:

tau_hat_B2A(I,R -> Y)

This layer represents the currently retained lightweight effect estimator.

Because B2A was developed after Task 2 ground truth had already been inspected,
its current benchmark evaluation is treated as development evidence rather than
a fully blind final evaluation.

Independent validation is required before strong performance claims are made
about B2A.

---

## 6. Oracle Decision

For each Task 2 query:

q = (I,R,Y)

the ground-truth intervention effect defines the oracle decision.

If:

tau_GT > 0

then:

Oracle(q) = I

If:

tau_GT < 0

then:

Oracle(q) = R

If:

tau_GT = 0

the query is classified as:

EFFECT_TIE

and is excluded from binary decision-accuracy calculations but retained in
descriptive reporting.

No practical-effect threshold is used in the primary analysis.

Threshold-based analyses, if performed, are reported only as sensitivity
analyses.

---

## 7. Structural-Indicator Decision Policy

For any candidate `A` and target outcome `Y`, define the binary structural
indicator:

S(A,Y) ∈ {0,1}

Binary refers to presence or absence of the specified structural relation for
that candidate–outcome pair; it does not mean that causal decision problems
are generally restricted to two available interventions.

For direct adjacency, `S(A,Y)=1` if and only if the required direct structural
relation exists. For the post-hoc directed-ancestry analysis, `S(A,Y)=1` if and
only if the required directed reachability relation exists.

For the pairwise intervention query:

q = (I,R,Y)

the structural-indicator pair is:

(S(I,Y), S(R,Y))

with four possible states:

(1,0), (0,1), (1,1), (0,0)

The frozen primary policy uses direct adjacency and considers whether the
intervention and reference constructs have direct structural relations to the
target.

For query:

q = (I,R,Y)

define:

S_I = 1

if:

I -> Y

is present in the structural graph, otherwise:

S_I = 0

and:

S_R = 1

if:

R -> Y

is present, otherwise:

S_R = 0

The decision rule is frozen as follows.

### Case A

If:

S_I = 1 and S_R = 0

then:

StructureDecision(q) = I

### Case B

If:

S_I = 0 and S_R = 1

then:

StructureDecision(q) = R

### Case C

If:

S_I = S_R

then:

StructureDecision(q) = ABSTAIN

This includes:

- both structural edges present,
- neither structural edge present.

No post-hoc tie-breaking rule is permitted in the primary experiment.

---

## 8. Two Structural Conditions

The structural-indicator policy is evaluated twice.

### Condition S-GT

Use ground-truth benchmark structure.

Purpose:

> Is causal structure itself sufficient for the decision when structural
> estimation error is removed?

### Condition S-D

Use Method D learned structure.

Purpose:

> What happens when the same decision rule operates on realistically estimated
> structural evidence?

This separation distinguishes:

structural insufficiency

from:

structural estimation error

---

## 9. Effect-Aware Decision Policy

For the retained B2A estimator:

If:

tau_hat_B2A > 0

then:

EffectDecision(q) = I

If:

tau_hat_B2A < 0

then:

EffectDecision(q) = R

Exact estimated zero is classified as:

ABSTAIN

The B2A policy is compared against the ground-truth oracle.

Its results are interpreted as development-stage effect-estimation evidence
until an independent validation set is available.

---

## 10. Decision-State Classification

For each structural condition, every non-tied oracle query is assigned to
exactly one of three states.

### STRUCTURE_SUFFICIENT

The structural policy makes a decision and that decision agrees with the
ground-truth effect oracle.

### STRUCTURE_MISLEADING

The structural policy makes a decision but selects the opposite action from the
ground-truth effect oracle.

### STRUCTURE_AMBIGUOUS

The structural policy returns ABSTAIN.

These labels describe decision sufficiency within the benchmark query.

They do not imply that the causal structure itself is scientifically incorrect.

---

## 11. Primary Metrics

### 11.1 Coverage

Coverage = N_decided / N_eligible

Coverage measures how often structural information alone provides an
unambiguous intervention preference.

### 11.2 Ambiguity Rate

AmbiguityRate = N_abstain / N_eligible

and therefore:

AmbiguityRate = 1 - Coverage

for the binary primary analysis.

### 11.3 Conditional Decision Accuracy

Among queries for which the policy makes a decision:

DecisionAccuracy = N_correct / N_decided

This metric is not reported without Coverage.

A high conditional accuracy with very low coverage must not be presented as
high overall decision performance.

### 11.4 Misleading Rate

Among all eligible queries:

MisleadingRate = N_STRUCTURE_MISLEADING / N_eligible

A conditional version among decided queries may additionally be reported.

### 11.5 Decision Disagreement

For policies that both produce a decision:

Disagreement = N_different_decisions / N_jointly_decided

Disagreement is reported for:

- Ground-Truth Structure vs Oracle Effect.
- Method D Structure vs Oracle Effect.
- Method D Structure vs B2A Effect.

The last comparison is descriptive and does not define causal correctness.

---

## 12. Selective Decision Regret

Regret is defined only for queries on which a policy makes a decision.

For a binary intervention-reference query:

If the selected action agrees with the oracle:

Regret(q) = 0

If the selected action disagrees with the oracle:

Regret(q) = |tau_GT(q)|

The primary regret statistic is:

MeanSelectiveRegret =
(1 / N_decided) * sum(Regret(q) for decided queries)

Median and distributional summaries are also reported.

Abstentions are not assigned zero regret.

No arbitrary cost of abstention is introduced in the primary analysis.

Therefore, regret must always be interpreted jointly with Coverage.

This avoids equating:

ABSTAIN

with:

Correct Decision

---

## 13. Primary Comparisons

The following comparisons are frozen.

### C1 — Oracle Structure Sufficiency

Ground-truth structure policy vs ground-truth effect oracle.

This is the primary conceptual comparison.

It isolates whether perfect structural information is sufficient for the
intervention query.

### C2 — Learned Structure Sufficiency

Method D structure policy vs ground-truth effect oracle.

This evaluates the practical combination of structural insufficiency and
structural estimation error.

### C3 — Structural Estimation Consequence

Compare C1 and C2 in:

- coverage,
- ambiguity,
- decision accuracy,
- misleading rate,
- selective regret.

### C4 — Estimated Effect Decision

B2A effect-aware decision vs ground-truth effect oracle.

This comparison evaluates the currently retained lightweight effect estimator.

Because the estimator was developed after ground-truth exposure, this
comparison is reported as development-stage evidence until independent
validation is completed.

---

## 14. Statistical Reporting

Primary results are reported:

1. pooled across all benchmark queries;
2. separately by benchmark environment.

For proportions such as:

- coverage,
- accuracy,
- misleading rate,

95% confidence intervals are reported.

For mean selective regret:

- bootstrap 95% confidence intervals are reported.

Bootstrap resampling must preserve the benchmark's relevant query/environment
structure where possible.

The paper will emphasize:

estimate + uncertainty

rather than relying primarily on null-hypothesis significance tests.

---

## 15. Sensitivity Analysis

The primary oracle uses the raw sign of:

tau_GT

A secondary sensitivity analysis may define a practical indifference region:

|tau_GT| <= epsilon

where such queries are classified as practically tied.

The value or values of epsilon must be justified from the benchmark outcome
scale and documented before the sensitivity results are inspected.

Sensitivity analysis does not replace the primary zero-threshold analysis.

---

## 16. Exploratory Analyses

The following analyses may be conducted after the primary analysis and must be
labelled exploratory:

- ancestor/path-based structural policies;
- structural ranking rather than direct-edge presence;
- path length;
- indirect structural relationships;
- structural score or stability;
- effect magnitude strata;
- query-level uncertainty;
- alternative abstention policies.

No exploratory rule may retroactively replace the frozen primary policy.

---

## 17. Expected Patterns

The following are research expectations rather than strict preregistered
hypotheses, because prior Task 1, Task 2, and structure-effect analyses have
already been inspected.

### E1

Structural indicators will not provide unambiguous decisions for all Task 2
queries.

### E2

Even under ground-truth structure, structural decisions will not perfectly
agree with intervention-effect oracle decisions.

### E3

Some structurally supported decisions will incur non-zero selective regret.

### E4

Structural estimation error may alter the coverage and error pattern relative
to ground-truth structure.

These expectations must not be rewritten after the new decision-level results
are observed.

---

## 18. Claim Boundaries

The experiment may support claims about:

- decision sufficiency of structural indicators within the tested benchmark;
- disagreement between structural and intervention-specific evidence;
- decision consequences of using one evidence type as a proxy for another;
- architectural implications for causal-aware AI systems.

The experiment does not establish:

- causal truth in real educational systems;
- that causal structure is unnecessary;
- that intervention effects are universally more informative than structure;
- that causal discovery is inferior to effect estimation;
- that the retained methods are universally optimal;
- that benchmark constructs correspond directly to real curriculum concepts;
- that the findings automatically generalize to curriculum sequencing in
  universities;
- that B2A has independently validated state-of-the-art performance.

---

## 19. Architectural Interpretation

If the primary results show that structural indicators can be sufficient in some
queries but ambiguous or misleading in others, the appropriate architectural
interpretation is:

Structure != Effect != Decision

and therefore causal-aware systems should preserve these evidence types
explicitly rather than automatically collapsing them into a single signal.

Such a finding would support a causal-aware architecture in which:

Structural Indicators

and:

Intervention-Specific Evidence

remain separately represented before symbolic decision logic is applied.

This is an architectural implication, not proof that a specific system
architecture is universally optimal.

---

## 20. Freeze Rule

This protocol must be versioned and frozen before the first execution of the
new decision-level experiment.

After the first result is produced:

- RQs must not be changed in response to the result.
- The primary structural-indicator policy must not be changed.
- The oracle definition must not be changed.
- The regret definition must not be changed.
- Abstention must not be replaced by a post-hoc tie-breaking rule.
- Primary and exploratory analyses must remain clearly separated.

Corrections are permitted only for:

- implementation bugs,
- incorrect benchmark interpretation,
- data integrity problems,
- or errors that make the frozen analysis scientifically invalid.

Every such correction must be documented in the Research Log with:

1. what changed,
2. why it changed,
3. whether any results had already been inspected.

---

## 21. Next Step After Freeze

After this protocol is frozen, implement one dedicated decision-level notebook
or experiment that reconstructs its inputs from canonical Task 1 and Task 2
artifacts and produces:

1. query-level decision table;
2. ground-truth structure results;
3. Method D structure results;
4. B2A effect-aware results;
5. coverage and ambiguity;
6. decision accuracy and misleading rate;
7. selective regret;
8. uncertainty intervals;
9. per-environment summaries;
10. one canonical machine-readable result file.

No manuscript claim should be finalized until this experiment has been
completed and independently reviewed.
