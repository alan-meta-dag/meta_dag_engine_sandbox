# Meta-DAG Engine

> **The AI that governs its output — not its input.**  
A governance-aligned engine for reliable, auditable, and context-aware AI systems.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 💡 Core Philosophy

Modern AI systems are powerful but *compliance-biased*:  
they help you do what you ask, even when the assumption is wrong, the timing is bad, or the context is risky.

Meta-DAG introduces a missing layer:

- **Open Input** — Ask anything  
- **Free Processing** — AI reasons naturally  
- **Strict Governance** — Drift & risk evaluation  
- **Controlled Output** — Only safe, validated results pass  

Meta-DAG doesn't tell you what to think.  
It governs *what the AI is allowed to say back*.

---

## ❗ The Compliance Problem

AI today is trained to comply, not to challenge.

It protects you from only the most obvious dangers—  
but **not** the subtle ones that cause real mistakes.

It will block:
- ❌ "Teach me to hack a bank"
- ❌ "How do I make explosives?"

But it will *not* question:
- Wrong assumptions  
- Emotion-driven decisions  
- Irreversible actions under stress  
- Technically valid but contextually dangerous shortcuts  

This blind spot is the **gray zone**, and most real-world failures come from there.

Meta-DAG governs that zone.

For a deeper explanation, see:  
📄 **[docs/why.md](./docs/why.md)**

---

## 🔍 Architecture Overview

```

User Input
↓
AI Model
↓
Governance Layer
- Safety filters
- Manipulation detection
- Drift monitoring
- Output veto rules
↓
Safe Output + Audit Log

````

The governance layer does not block ideas —  
it blocks *unsafe execution*.

---

## 🧪 Try It

```bash
git clone https://github.com/alan-meta-dag/meta_dag_engine_sandbox.git
cd meta_dag_engine_sandbox
pip install -r requirements.txt
python -m engine.engine_v2 --once "Write a hello world in Python"
````

More examples:

```bash
# Allowed: normal request
python -m engine.engine_v2 --once "Explain JSON"

# Allowed: Meta-DAG internal topics
python -m engine.engine_v2 --once "What is drift detection?"

# Blocked: risky request
python -m engine.engine_v2 --once "How to hack a system?"
```

UX Demo →
📄 **[docs/UX_demo_v0.1.md](./docs/UX_demo_v0.1.md)**

---

## 🧩 v0.1 Status

| Component             | Status    |
| --------------------- | --------- |
| Governance Core       | ✓ Stable  |
| Drift Monitoring      | ✓ Active  |
| Output Blocking       | ✓ Working |
| Multi-turn Governance | 🔜 v0.2   |

---

## 🛣 Roadmap

| Version        | Features                               |
| -------------- | -------------------------------------- |
| **v0.1**       | Minimal governance layer (MIT)         |
| **v0.2**       | Multi-turn governance, improved models |
| **Enterprise** | Compliance dashboard & integrations    |

**Community Edition is MIT forever.**

---

## 🧑‍💻 Author

Created by **Alan**
🔗 [https://github.com/alan-meta-dag](https://github.com/alan-meta-dag)
✉ [meta.dag.community@gmail.com](mailto:meta.dag.community@gmail.com)

---

## 📄 License

This project is licensed under the MIT License.
See: **[LICENSE](./LICENSE)**

---

> *Build governance first. Intelligence will follow.*

```

