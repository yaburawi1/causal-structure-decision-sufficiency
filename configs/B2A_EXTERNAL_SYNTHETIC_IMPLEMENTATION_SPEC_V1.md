# B2A External-Synthetic Implementation Specification v1

**Study:** When Is Causal Structure Enough? Decision Sufficiency of Binary Structural Indicators for Pairwise Intervention Choice in Educational AI
**Scientific protocol:** B2A External-Synthetic Validation Protocol v1.1
**Specification status:** FROZEN BEFORE ANY RNG OR DATA GENERATION
**Date:** September 2026

> This non-scientific implementation specification operationalizes the frozen
> V1.1 scientific protocol without changing its scientific design. No validation
> graph, trajectory, query, prediction, or ground-truth effect had been
> generated at the time of this freeze.

---

## 1. Runtime and PRNG

Use:
- Python 3.11
- NumPy Generator
- PRNG: numpy.random.PCG64

Each environment has the frozen base seed from V1.1.

Derive deterministic component seeds from the base seed using NumPy SeedSequence:

base = SeedSequence(environment_seed)

spawn exactly these child streams in this fixed order:
1. graph
2. coefficients
3. intervention_targets
4. intervention_strengths
5. action_probabilities
6. training_initial_states
7. training_actions
8. training_noise
9. query_initial_states
10. query_context_actions
11. query_context_noise
12. query_sampling
13. monte_carlo
14. diagnostics

Do not derive seeds using Python hash(), wall-clock time, process IDs, or machine-dependent state.

Store the entropy/spawn keys required to reproduce each stream.

## 2. Graph generation

For every admissible ordered pair i<j:
- draw exactly one Bernoulli(p) sample in lexicographic order:
  (0,1), (0,2), ..., (18,19)

Adjacency convention:
adjacency[i,j] = 1 means i -> j

Coefficient magnitudes/signs are sampled only for realized edges, in the same lexicographic edge order.

No extra RNG draw is allowed for absent edges.

## 3. EXT5 target eligibility

For EXT5:
- after graph generation, define eligible intervention-target nodes as nodes with out-degree >=1;
- sample 8 distinct targets without replacement from this eligible set.

If fewer than 8 eligible nodes exist:
- stop with PROTOCOL_FEASIBILITY_ERROR;
- do not regenerate graph;
- do not change seed.

For EXT0-EXT4:
- sample 8 distinct targets without replacement from all 20 nodes.

## 4. Action probability floor

Start from:
raw ~ Dirichlet([2,2,2,2,2,2,2,2])

Project deterministically onto the probability simplex with lower bound 0.03.

Implement this as:

floor = 0.03
remaining = 1 - 8*floor

q_i = max(raw_i - floor, 0)

If sum(q) > 0:
    p_i = floor + remaining * q_i / sum(q)
Else:
    p_i = 1/8

After construction:
- assert abs(sum(p)-1) <= 1e-12
- assert min(p) >= 0.03 - 1e-12

Store full float64 values.

## 5. State update order

Use synchronous updates.

For every transition s -> s+1:
1. compute all pre-activation z_j using only X_s;
2. add self-persistence;
3. add all parent contributions;
4. add intervention shift for the current action target;
5. add epsilon_(s+1);
6. apply tanh;
7. write the complete X_(s+1) simultaneously.

No in-place node update may affect another node in the same time step.

## 6. Training trajectory generation

For each environment:
- 400 trajectories;
- each trajectory has states shape (120,20);
- actions shape (119,).

Initial states:
Uniform(-0.5,0.5)

Actions:
sample independently over time from frozen environment action probabilities.

Noise:
iid Normal(0,sigma^2), shape (119,20).

Store trajectories in a deterministic order by trajectory_id 0..399.

## 7. B2A-aligned training rows

Eligible t:
11..117 inclusive

For each trajectory and each eligible t:
features = X[t-1]
action = A[t]
target = X[t+2]

Generate rows in deterministic order:
trajectory_id first,
then t ascending.

Expected total rows:
400 * 107 = 42,800 per environment.

Support counts are computed from these rows only.

## 8. Query-context generation

Generate exactly 40 query contexts/environment.

For each query_id 0..39:
- sample independent X_0;
- simulate exactly 10 transitions;
- generate exactly 10 context actions and 10 context noise vectors;
- X_10 is the query conditioning state.

Query-context data must never be included in B2A training.

## 9. Query sampling EXT0-EXT4

Supported action set:
actions with aligned training count >=100.

For each query_id:
- sample I uniformly from supported actions;
- sample R uniformly from supported actions excluding I;
- sample Y uniformly from integers 0..19.

Use query_sampling RNG only.

Repeated (I,R,Y) combinations are allowed.

## 10. Query sampling EXT5

Mediation-eligible supported actions:
supported actions whose target construct has at least one outgoing child.

Require at least two such actions.

If fewer than two:
PROTOCOL_FEASIBILITY_ERROR.

For each query:
- sample I uniformly from eligible actions;
- sample R uniformly from remaining eligible actions;
- candidate_Y = sorted union of immediate children of target(I) and target(R);
- remove target(I) and target(R) if present;
- sample Y uniformly from candidate_Y.

If candidate_Y is empty:
PROTOCOL_FEASIBILITY_ERROR for that environment;
do not regenerate graph or seed.

## 11. Monte Carlo seed derivation

For each environment/query:
derive the query-specific Monte Carlo RNG deterministically from:
- environment monte_carlo SeedSequence child stream
- query_id

Use SeedSequence.spawn(40) once in query_id order.

Each query uses exactly 500 paired draws.

For each draw:
- sample nuisance A_(t-1);
- sample nuisance A_(t+1);
- sample required Gaussian noise for all three transitions;
- reuse the exact same nuisance actions/noise in I and R worlds.

The only difference between paired worlds is A_t.

## 12. Prediction blind boundary

B2A prediction code may read only:
- generated training trajectories / aligned training table;
- query conditioning states;
- I;
- R;
- Y.

It must not read:
- adjacency matrices;
- coefficients;
- intervention strengths;
- simulator seeds;
- Monte Carlo streams;
- ground-truth files.

Prediction generation and ground-truth generation must be separate functions/modules.

## 13. Serialization

Use:
- CSV for query/prediction/GT/summary tables;
- JSON for DGP specification;
- NPY for adjacency matrices and coefficient matrices if needed.

CSV:
- UTF-8
- comma separator
- header included
- index=False
- float serialization using repr-compatible float64 precision.

JSON:
- UTF-8
- sorted keys
- indent=2

Do not round scientific values before saving.

## 14. Canonical IDs

Environment:
EXT0..EXT5

Training trajectories:
trajectory_id 0..399

Queries:
query_id 0..39

Canonical query key:
(environment_id, query_id)

## 15. Exact-zero handling

Use native float64 comparison:
value > 0
value < 0
value == 0

Do not apply epsilon threshold in primary analysis.

## 16. Metrics

Pooled:
MAE = mean(abs(error))
RMSE = sqrt(mean(error^2))

Pearson and Spearman:
- use all defined query pairs;
- if mathematically undefined because one vector is constant, record NaN and document the reason;
- do not replace undefined correlations with zero.

Sign agreement:
exact sign-category equality, including zero.

## 17. Bootstrap

Use:
- 10,000 replicates
- bootstrap seed = 20260909
- NumPy Generator(PCG64)

Environment-stratified bootstrap:
for each replicate and each environment:
- sample 40 query indices with replacement from that environment;
- concatenate all six sampled strata;
- compute pooled metric.

Confidence interval:
2.5th and 97.5th empirical percentiles.

Apply to:
- MAE
- RMSE
- sign agreement

## 18. Ground-truth diagnostics

For each query store:
- tau_gt
- paired_diff_sd
- mc_se
- running_tau_100
- running_tau_250
- running_tau_500
- split_half_tau_first_250
- split_half_tau_second_250

No diagnostic can trigger regeneration or additional Monte Carlo draws.

## 19. Saturation diagnostics

For each environment report descriptively:
- fraction of stored training state values with abs(X)>0.95
- mean state variance across constructs
- minimum construct variance
- maximum construct variance

These are diagnostics only.

They must not trigger regeneration, seed changes, graph changes, or estimator changes.

## 20. Scientific-payload hashing

Use SHA-256 over deterministically serialized scientific content. Exclude
wall-clock time, repository history, absolute paths, and other packaging-only
provenance from scientific hashes.

Create a manifest:
results/b2a_external_synthetic_manifest_v1.json

For every canonical artifact record:
- relative path
- scientific-payload SHA-256
- byte size

For the DGP specification, hash the canonical JSON serialization of the six
environment definitions. For the query table, hash its deterministic CSV
bytes. For the training archive, hash each array's key, dtype, shape, and
C-order bytes in sorted-key order.

## 21. Generation-stage separation

Implementation must support these explicit stages:

Stage A:
generate DGP specifications and training/query inputs only.

Stage B:
fit frozen B2A and generate all predictions.

Stage C:
freeze and hash predictions.

Stage D:
generate Monte Carlo ground truth.

Stage E:
evaluate and summarize.

Ground truth must not be generated before Stage C is complete.

## 22. Failure behavior

Any protocol feasibility failure must:
- stop the pipeline;
- write no replacement environment;
- not consume a new seed;
- clearly report environment and reason.

Implementation bugs may be corrected only under the amendment rules of V1.1.

## 23. Scientific boundary

This specification operationalizes V1.1 only.

It must not change any scientific choice in:
B2A_EXTERNAL_SYNTHETIC_VALIDATION_PROTOCOL_V1_1.md

If implementation requires a scientific choice not already frozen in V1.1:
STOP and report it rather than silently choosing one.
