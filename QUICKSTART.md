# Quick Start Guide

Get Project Eirene running in 5 minutes!

## 🚀 Installation

```bash
# 1. Clone and enter directory
git clone https://github.com/yourusername/eirene.git
cd eirene

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env with your API keys
```

## 🎨 Launch Dashboard (Easiest!)

```bash
./start_dashboard.sh
```

Then open: **http://localhost:5001**

## 🧪 Run Demos

```bash
# Test Monitor + Strategy agents
PYTHONPATH=. python examples/demo_monitor_strategy.py

# Test Generation agent (creates videos!)
PYTHONPATH=. python examples/demo_generation.py

# Full pipeline demo
PYTHONPATH=. python examples/demo_strategy_to_generation.py
```

## 🔑 Required API Keys

Get free API keys from:
- **TinyFish/Mino**: https://mino.ai
- **Yutori**: https://yutori.com
- **Freepik**: https://freepik.com/api
- **ElevenLabs**: https://elevenlabs.io
- **OpenAI**: https://platform.openai.com

## 📚 Need More Help?

- **[Full README](README.md)** - Complete documentation
- **[How to Use Guide](.guides/HOW_TO_USE.md)** - Detailed usage instructions
- **[Demo Guide](.guides/DEMO_PERFECT.md)** - Perfect demo script
- **[Dashboard Guide](.guides/DASHBOARD_README.md)** - Dashboard features

## 🎯 What to Try First

1. **Start the dashboard**: `./start_dashboard.sh`
2. **Click a stress signal scenario** (e.g., "Work Burnout Crisis")
3. **Watch the agents work** - Monitor → Strategy → Generation
4. **View the generated video** in the results panel

That's it! You're running an autonomous AI mental health intervention system! 🌿
