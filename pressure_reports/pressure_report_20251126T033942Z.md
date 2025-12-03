# Meta-DAG Pressure Test Report

- Generated at (UTC): 2025-11-26T03:39:42.993302Z
- Total tests: 11
- Passed: 0
- Failed: 11

## Summary by Category

### dag_contamination
- Total: 4 | Passed: 0 | Failed: 4
- Severity distribution: high: 2, medium: 2

### semantic_corruption
- Total: 3 | Passed: 0 | Failed: 3
- Severity distribution: high: 2, medium: 1

### pec6_boundary
- Total: 4 | Passed: 0 | Failed: 4
- Severity distribution: medium: 2, high: 2

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

### SEM.POLICY.01 — semantic_conflicting_policies
- Category: `semantic_corruption`
- Attack type: `policy_conflict`
- Severity: `high`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Inject contradictory policy rules inside the memory node.
- Error / Concern: `Engine did not flag contradictory policy / semantic conflict.`

```json
{
  "attack_vector": "conflicting_policies",
  "expected_detector_signals": [
    "policy_conflict",
    "inconsistent_node_rules"
  ],
  "validation": {
    "status": "skipped",
    "reason": "no-engine",
    "checked_by": "pressure_test.EngineAdapter"
  }
}
```

### SEM.ROLE.01 — semantic_role_inversion
- Category: `semantic_corruption`
- Attack type: `role_inversion`
- Severity: `medium`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Swap semantic roles between root and PEC-6 module.
- Error / Concern: `Engine did not report suspicious role inversion.`

```json
{
  "attack_vector": "role_inversion",
  "expected_detector_signals": [
    "root_role_mismatch",
    "external_module_marked_as_root"
  ],
  "validation": {
    "status": "skipped",
    "reason": "no-engine",
    "checked_by": "pressure_test.EngineAdapter"
  }
}
```

### SEM.PROMPT.01 — semantic_prompt_poison
- Category: `semantic_corruption`
- Attack type: `prompt_injection`
- Severity: `high`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Embed a prompt-injection style string into the translation layer payload.
- Error / Concern: `Engine did not react to obvious prompt-injection style content.`

```json
{
  "attack_vector": "prompt_injection_style_text",
  "expected_detector_signals": [
    "prompt_injection_pattern",
    "unsafe_instruction_in_payload"
  ],
  "validation": {
    "status": "skipped",
    "reason": "no-engine",
    "checked_by": "pressure_test.EngineAdapter"
  }
}
```

### PEC.SIZE.01 — pec6_oversized_payload
- Category: `pec6_boundary`
- Attack type: `size`
- Severity: `medium`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Send a PEC-6 packet with a very large payload blob.
- Error / Concern: `PEC-6 handler did not acknowledge oversized payload.`

```json
{
  "attack_vector": "oversized_payload",
  "expected_detector_signals": [
    "payload_size_exceeded"
  ],
  "result": {
    "status": "skipped",
    "reason": "phase4_collab-not-found"
  }
}
```

### PEC.AUTH.01 — pec6_missing_signature
- Category: `pec6_boundary`
- Attack type: `auth`
- Severity: `high`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Drop the signature field from an otherwise valid PEC-6 packet.
- Error / Concern: `PEC-6 handler did not mention missing signature / auth.`

```json
{
  "attack_vector": "missing_signature",
  "expected_detector_signals": [
    "missing_signature",
    "unauthenticated_packet"
  ],
  "result": {
    "status": "skipped",
    "reason": "phase4_collab-not-found"
  }
}
```

### PEC.INTENT.01 — pec6_unknown_intent
- Category: `pec6_boundary`
- Attack type: `intent`
- Severity: `high`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Use a deliberately suspicious / unknown intent string.
- Error / Concern: `PEC-6 handler did not flag unknown / dangerous intent.`

```json
{
  "attack_vector": "unknown_intent",
  "expected_detector_signals": [
    "unknown_intent",
    "dangerous_intent_string"
  ],
  "result": {
    "status": "skipped",
    "reason": "phase4_collab-not-found"
  }
}
```

### PEC.REPLAY.01 — pec6_replay_attack
- Category: `pec6_boundary`
- Attack type: `replay`
- Severity: `medium`
- Engine mode: `no-engine`
- Status: ❌ FAIL
- Description: Send the same PEC-6 packet twice to test replay protection / idempotency.
- Error / Concern: `PEC-6 handler did not show replay / duplicate awareness.`

```json
{
  "attack_vector": "replay_same_packet",
  "expected_detector_signals": [
    "replay_detected",
    "duplicate_packet"
  ]
}
```
