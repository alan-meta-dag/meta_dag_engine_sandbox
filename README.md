# Meta-DAG: AI Governance Engine

⚡ **Process Over Trust** - Infrastructure layer for safe AI-powered applications

🎬 [1-min Pitch](https://youtu.be/0WZZsNf6wp8) | ⭐ [GitHub](https://github.com/alan-meta-dag/meta_dag_engine_sandbox)

---

## What is Meta-DAG?

**Meta-DAG is an infrastructure layer used inside AI-powered web and mobile applications to enforce output governance.**

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

---

## Why Meta-DAG?

In AI-powered applications, the risk isn't AI malice—it's **over-helpfulness**:

- ❌ Executing requests based on incorrect assumptions
- ❌ Assisting with dangerous operations under pressure
- ❌ Creating emotional dependencies through interactive narratives

**Meta-DAG ensures your AI application outputs only safe, governed responses.**

---

## Core Philosophy: Process Over Trust

We don't trust humans. We don't trust AI.  
**We only trust verifiable processes.**

### Key Features

- 🔒 **HardGate**: Token-level output control - unsafe content can't get out
- 📝 **MemoryCard**: Immutable audit trail (dataclass frozen)
- 🎯 **DecisionToken**: Final safety verification before output
- 💾 **JSONL Storage**: Permanent governance logs

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

---

**⭐ Star this repo if you find it useful!**

[Watch the 1-min pitch](https://youtu.be/0WZZsNf6wp8) | [Read more on Dev.to](your-article-url)