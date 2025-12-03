# Meta-DAG Pressure Test Report

- Generated at (UTC): 2025-11-26T03:27:16.070192Z
- Total tests: 4
- Passed: 0
- Failed: 4

## Summary by Category

### dag_contamination
- Total: 4 | Passed: 0 | Failed: 4
- Severity distribution: high: 2, medium: 2

## Detailed Results (truncated details)

### DAG.CYCLE.01 — dag_cycle_back_edge
- Category: `dag_contamination`
- Attack type: `cycle`
- Severity: `high`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Inject a back-edge from pec6 to root to create an explicit cycle.
- Error / Concern: `Engine did not clearly flag cycle / loop / invalid graph.`

```json
{
  "attack_vector": "cycle_back_edge",
  "expected_detector_signals": [
    "cycle_detected",
    "root_reachable_loop"
  ],
  "validation": {
    "status": "skipped",
    "reason": "no-engine",
    "checked_by": "pressure_test.EngineAdapter"
  }
}
```

### DAG.ORPHAN.01 — dag_orphan_component
- Category: `dag_contamination`
- Attack type: `orphan`
- Severity: `medium`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Add a disconnected orphan subgraph not reachable from root.
- Error / Concern: `Engine did not mention orphan / disconnected components.`

```json
{
  "attack_vector": "orphan_subgraph",
  "expected_detector_signals": [
    "unreachable_nodes",
    "orphan_component"
  ],
  "validation": {
    "status": "skipped",
    "reason": "no-engine",
    "checked_by": "pressure_test.EngineAdapter"
  }
}
```

### DAG.LABEL.01 — dag_mass_semantic_duplication
- Category: `dag_contamination`
- Attack type: `label_collision`
- Severity: `medium`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Inject many nodes with the same semantic_role as the core memory engine.
- Error / Concern: `Engine did not comment on duplicate semantic roles / label collisions.`

```json
{
  "attack_vector": "mass_semantic_duplication",
  "expected_detector_signals": [
    "semantic_role_collision",
    "suspicious_fanout_from_root"
  ],
  "validation": {
    "status": "skipped",
    "reason": "no-engine",
    "checked_by": "pressure_test.EngineAdapter"
  }
}
```

### DAG.PAYLOAD.01 — dag_suspicious_payload_string
- Category: `dag_contamination`
- Attack type: `payload`
- Severity: `high`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Replace a node payload with a code-like string to test payload sanitization.
- Error / Concern: `Engine did not flag suspicious / code-like payload content.`

```json
{
  "attack_vector": "payload_suspicious_string",
  "expected_detector_signals": [
    "suspicious_payload",
    "code_like_string"
  ],
  "validation": {
    "status": "skipped",
    "reason": "no-engine",
    "checked_by": "pressure_test.EngineAdapter"
  }
}
```
