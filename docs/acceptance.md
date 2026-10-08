# Qualification Gates And Scoring

The executable gate catalog is `src/frankenstein/acceptance.py`. Its score is an evidence-completeness score, not a substitute for the official judging rubric.

| Gate | Points | Pass criterion |
| --- | ---: | --- |
| DOD-01 | 8 | Registry searched and a real capability gap recorded |
| DOD-02 | 10 | Persistent reusable implementation artifact generated |
| DOD-03 | 8 | A failing verification is observed and promotion is denied |
| DOD-04 | 10 | Generated capability independently verified and registered |
| DOD-05 | 10 | Original task completes using the generated capability |
| DOD-06 | 10 | Capability-management infrastructure is itself generated |
| DOD-07 | 10 | Management extension is verified, registered, and subsequently used |
| DOD-08 | 8 | Registry reload after process restart discovers installed versions |
| DOD-09 | 8 | A genuinely fresh session rediscovers generated capabilities |
| DOD-10 | 10 | A different task composes at least two generated capabilities with no rebuild |
| DOD-11 | 8 | Permission escalation is denied while ordinary execution succeeds |

Total: 100 points. **Qualification requires all eleven gates**, not merely a score threshold. A 92/100 result that misses the security gate is a failure. Events must be backed by retained local traces; names alone are not proof.

## Official Judging Alignment

- End-to-end working result, 35%: DOD-01 through DOD-10.
- Value and track relevance, 25%: generated task capabilities and management evolution.
- Technical execution, 20%: persistence, typed contracts, dependency checks, independent verification, and permission enforcement.
- Originality, 10%: persistent self-extension and management-layer evolution.
- Validation and limitations, 10%: DOD-03, DOD-11, retained failures, honest unknown costs, and explicit limitations.

## Evidence Rules

- Fixture-backed runs must be labelled fixtures; live integrations must be labelled live.
- `qualified=true` is forbidden until the evaluator sees every required event and integration tests link those events to actual artifacts.
- Fresh-session composition must contain `fresh_session_started`, registry lookups, a composition graph, task completion, and `no_rebuild_confirmed`; manually injecting tool descriptions does not count.
- Management evolution requires a generated manifest with `domain=capability_management` and its own independent verification record.
- No cost improvement passes unless workload identity, success criteria, pricing source, and regression result are comparable.
