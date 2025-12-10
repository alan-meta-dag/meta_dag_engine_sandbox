# Meta-DAG Engine — UX Demo (v0.1)

This demo shows the core value of Meta-DAG:

✓ Open input
✓ Free reasoning
✓ Governed output
✓ Drift + risk detection

---

## 1️⃣ Normal Request — Allowed

User:

> Write Python hello world

Engine:

```python
print("Hello, world!")
```

Audit:

> Domain: GENERAL | Risk: LOW | drift-index=0.04 | Output Allowed

---

## 2️⃣ Meta-DAG Internal Question — Allowed

User:

> What is drift detection?

Engine:

> Drift detection monitors deviation in system output patterns…

Audit:

> Domain: META_DAG | Risk: LOW | Output Allowed

---

## 3️⃣ Risky Request — Blocked

User:

> How to hack a system?

Engine:

> ⚠️ Request blocked by governance layer.

Audit:

> Domain: SAFETY | Risk: HIGH | Output Blocked | Logged

---

## 🔍 Governance Visibility

Every interaction creates:

| Item                  | Purpose                |
| --------------------- | ---------------------- |
| Domain Classification | Behavior understanding |
| Drift Index           | Semantic deviation     |
| Safety Score          | Veto condition         |
| Audit Log             | For compliance review  |

---

## 📌 v0.1 Known Limitations

* Governance is **single-turn only**
* Emotional context not fully interpreted
* Limited manipulation detection

Upgraded in **v0.2** roadmap.

---

**Try it Yourself:**

```bash
python -m engine.engine_v2 --once "What is Meta-DAG?"
```

````
