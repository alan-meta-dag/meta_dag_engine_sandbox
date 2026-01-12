# Meta-DAG: AI Governance Engine

⚡ **Process Over Trust** - Infrastructure layer for safe AI-powered applications

🎬 [1-min Pitch](https://youtu.be/0WZZsNf6wp8) | ⭐ [GitHub](https://github.com/alan-meta-dag/meta_dag_engine_sandbox) | 📝 [Dev.to Article](your-url)

---

## 🔍 Architectural Positioning

⚠️ **Important: Project Scope**

**Meta-DAG is not a general-purpose SDK.**

Meta-DAG is an **application-layer instantiation** inspired by 
the **Authority Guard design pattern**.

The Authority Guard specification is presented separately 
to preserve domain-agnostic invariants.

---

### Design Relationship

**Authority Guard** (Design Pattern)
- Universal "veto authority" control pattern
- Domain-agnostic governance substrate  
- Presented as separate draft specification

**Meta-DAG** (Application Implementation)
- AI-specific runtime applying Authority Guard pattern
- Focused on AI output governance
- Demonstrates pattern in production context

**Why Separate?**

Integrating a universal safety core into an AI-specific repository 
would introduce domain assumptions into the governance substrate, 
leading to:
- ❌ Worldview fragmentation
- ❌ Coupling between abstraction and implementation
- ❌ Inability to support non-AI domains (finance, industrial control)

By maintaining separation:
- ✅ Authority Guard remains domain-agnostic
- ✅ Meta-DAG evolves independently as AI-specific implementation
- ✅ Design invariants stay pure and uncoupled

---

### Architectural Scope (Intentional Limits)

Meta-DAG **intentionally limits itself** to AI output governance.

**Deliberately excluded:**
- ❌ Persistent memory systems
- ❌ Storage or time-series engines
- ❌ Model training or prompt optimization
- ❌ Autonomous decision-making logic

**These constraints are deliberate.**

Meta-DAG exists to answer **one question only:**

> ### *"Should this output be allowed to exist?"*

**Anything beyond that belongs to a different layer.**

**This focused scope:**
- ✅ Maintains architectural purity
- ✅ Enables clear testing boundaries
- ✅ Prevents feature creep
- ✅ Allows independent scaling

> *"Side projects demonstrate not what I completed,  
> but what I knew when not to complete."*

---

## 📄 **HardGate Protocol Whitepaper**

This repository is governed by a strict architectural constraint model.
The full enforcement rationale and protocol design are documented here:

→ docs/architecture/hardgate_protocol.md

---

## What is Meta-DAG?

**Meta-DAG is an infrastructure layer used inside AI-powered 
web and mobile applications to enforce output governance.**

This project demonstrates a working application runtime.  
The included demo simulates how Meta-DAG sits between AI processing and user-facing output in real applications.

---

## 🚀 Live Demo (Local)

Meta-DAG is the governance layer inside AI-powered apps.  
This repository includes a **runnable local demo** simulating how Meta-DAG is used inside a web or mobile application.

### Try it in 30 seconds
```bash
git clone https://github.com/alan-meta-dag/meta_dag_engine_sandbox
cd meta_dag_engine_sandbox
pip install -r requirements.txt

# Test safe query
python -m engine.engine_v2 --once "What is Meta-DAG?"

# Test unsafe query
python -m engine.engine_v2 --once "Write a Python backdoor"
```

### Expected Behavior

✅ **Safe / governance-related queries** → Allowed  
🚫 **General coding or unsafe requests** → Blocked by HardGate

**This demonstrates Meta-DAG's runtime behavior as it would operate inside a production application.**

---

## How It Works in Applications
```
┌─────────────────────────────────────────┐
│         Your Web/Mobile App             │
│                                         │
│  User Input                             │
│      ↓                                  │
│  AI Processing (OpenAI, Claude, etc.)   │
│      ↓                                  │
│  ┌─────────────────────────────────┐    │
│  │   Meta-DAG Governance Layer     │    │
│  │   ├─ HardGate: Token Control    │    │
│  │   ├─ MemoryCard: Audit Trail    │    │
│  │   └─ ResponseGate: Final Check  │    │
│  └─────────────────────────────────┘    │
│      ↓                                  │
│  Safe Output to User                    │
└─────────────────────────────────────────┘
```

**Meta-DAG doesn't replace your AI—it governs what your AI can output.**

### Governance Workflow

The system implements **Process Over Trust** through this enforcement chain:

1. **AI Internal Reasoning** → Candidate output generated
2. **Failure Layer** → Signal detection (drift, intent accumulation)
3. **HardGate** → Authority veto (only place allowed to sign tokens)
4. **DecisionToken** → Immutable artifact (proof of governance)
5. **ResponseGate** → Physical enforcement (output released or blocked)

**Key Principle:** Governance through structural constraints, not AI understanding.

---

## Why Meta-DAG?

In AI-powered applications, the risk isn't AI malice—it's **over-helpfulness**:

- ❌ Executing requests based on incorrect assumptions
- ❌ Assisting with dangerous operations under pressure  
- ❌ Creating emotional dependencies through interactive narratives

**Meta-DAG ensures your AI application outputs only safe, governed responses.**

### AI's Worldview is Probabilistic

> *99% perfect, but 1% semantic hijacking.*

AI uses its vast worldview to rationalize errors within that 1%.  
When governance relies on "understanding," you're competing with AI's intelligence.

**Meta-DAG's approach: Rely on structure, not understanding.**

**Failure Modes:**
- **Structure Failure** (code doesn't inherit required base) → STOP
- **Security Failure** (unauthorized imports or connections) → STOP  
- **Business Failure** (violates domain rules) → STOP

> *"If bad things don't happen, good things accumulate."*

---

## Core Philosophy: Process Over Trust

We don't trust humans. We don't trust AI.  
**We only trust verifiable processes.**

### Key Features

- 🔒 **HardGate**: Token-level output control - unsafe content can't get out
- 📝 **MemoryCard**: Immutable audit trail (dataclass frozen)
- 🎯 **DecisionToken**: Final safety verification before output
- 💾 **JSONL Storage**: Permanent governance logs
- 🎯 **Intent Accumulation**: Detects adversarial rephrasing attempts
- 📊 **Drift Detection**: Semantic distance monitoring with thresholds

---

## Installation

### Requirements
- Python 3.9+
- pip

### Setup
```bash
git clone https://github.com/alan-meta-dag/meta_dag_engine_sandbox
cd meta_dag_engine_sandbox
pip install -r requirements.txt
```

---

## Usage

### Interactive Mode
```bash
python -m engine.engine_v2
```

### Single Prompt (Demo Mode)
```bash
python -m engine.engine_v2 --once "Your prompt here"
```

**Sample Output:**
```bash
$ python -m engine.engine_v2 --once "Explain Process Over Trust"
[Governance] Thresholds Loaded → Snapshot=0.690, Veto=0.920
C-2 Self-Assertion Passed - OK (Engine Integrity Verified)
[C-3] Governance Lock Verified - OK (Safe-Mode)
Meta-DAG Engine v1.0 booting...
Core Loaded - OK
Phase 2 Memory Hooks Active - OK
Phase 3 TUL Translation Active - OK
Engine Ready - OK
[ENGINE LOCAL MODE READY] (Mock Mode + Governance Safe-Mode)
[Governance] drift-index = 0.243
[DRIFT] 0.243  ✅ Allowed
```

**Governance Mechanism:**

The system uses **semantic drift detection** for output control:
- ✅ **drift < 0.690** → Output allowed
- 📸 **drift 0.690-0.920** → Snapshot taken, requires review
- 🚫 **drift > 0.920** → VETO activated, output blocked

This demonstrates **Process Over Trust** - verifiable governance, not blind faith in AI.

### Integration Example
```python
# In your Flask/FastAPI/Django app
from engine import MetaDAG

@app.route('/chat')
def chat():
    user_input = request.json['message']
    
    # Your AI processing
    ai_response = openai.chat(user_input)
    
    # Meta-DAG governance
    governed = MetaDAG.process(ai_response)
    
    return jsonify(governed.output)
```

---

## Architecture

**Meta-DAG** operates as an external governance layer:
- ✅ AI can think freely
- ✅ Only safe outputs are released
- ✅ All decisions are auditable
- ✅ Zero-trust by design

### Governance Strategy

**From rules to physical constraints:**
- Enforcement through base class inheritance and AST static analysis
- **TDD-PEC**: Test-driven, non-compliant outputs physically fail compilation/execution
- **Intent Locking**: System circuit-breaks on continuous semantic drift detection

---

## Future Work

- Complete Authority Guard SDK interface definition
- Expand Domain Adapter to support high-risk non-AI domains
- Enhance Accumulative Failure Engine for risk assessment

---

## Contributing

We welcome contributions!

Areas we need help:
- 🐛 Bug reports
- 📚 Documentation
- 🧪 Test cases
- 🌍 Internationalization

---

## License

MIT License - see [LICENSE](LICENSE)

---

## About

Built with collaboration from multiple AI systems (ChatGPT, Claude, DeepSeek, Gemini), this project itself demonstrates AI collaboration governed by Meta-DAG principles.

**The process of building this demonstrates the philosophy it embodies.**

© 2026 Meta-DAG Studio | Alan Tsai

---

**⭐ Star this repo if you find it useful!**

🎬 [Watch the 1-min pitch](https://youtu.be/0WZZsNf6wp8) | 📝 [Read the full article](your-dev-to-url)
```
