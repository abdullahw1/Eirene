# Repository Organization

This document explains how the Eirene repository is organized.

## 📂 Directory Structure

### Root Level (Clean & Essential)
```
Eirene/
├── README.md              # Main project documentation
├── QUICKSTART.md          # 5-minute setup guide
├── LICENSE                # MIT License
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project metadata
├── dashboard.py           # Web dashboard server
├── start_dashboard.sh     # Dashboard launcher script
├── .env.example           # Environment template
└── .gitignore            # Git ignore rules
```

### Core Application (`src/`)
```
src/
├── agents/               # AI agent implementations
│   ├── manager.py        # Orchestration agent
│   ├── monitor.py        # Stress signal detection
│   ├── monitor_enhanced.py  # Live TinyFish integration
│   ├── strategy.py       # Therapeutic mapping
│   └── generation.py     # Video generation
├── models/               # Data models & schemas
│   ├── config.py
│   ├── intervention.py
│   ├── pipeline.py
│   └── stress_signal.py
└── utils/                # Shared utilities
    └── trace_logger.py
```

### Testing (`tests/`)
```
tests/
├── test_manager_agent.py
├── test_monitor_strategy_agents.py
├── test_generation_agent.py
├── test_generation_integration.py
└── test_strategy_enhanced.py
```

### Examples (`examples/`)
```
examples/
├── demo_manager.py
├── demo_monitor_strategy.py
├── demo_generation.py
└── demo_strategy_to_generation.py
```

### Documentation (`docs/`)
Technical documentation for each component:
```
docs/
├── manager_agent.md
├── monitor_strategy_agents.md
├── generation_agent.md
├── strategy_agent_enhancements.md
└── freepik_kling_api.md
```

### Scripts (`scripts/`)
Utility scripts for testing and deployment:
```
scripts/
├── README.md              # Scripts documentation
├── test_yutori.py         # Test Yutori API
├── test_freepik_kling.py  # Test Freepik API
├── test_instant_playback.py  # Test video playback
├── generate_demo_video.py # Generate demo videos
└── push_to_github.sh      # Deployment script
```

### Guides (`.guides/`)
Development guides and status documents:
```
.guides/
├── README.md              # Guides index
├── HOW_TO_USE.md          # Usage guide
├── DASHBOARD_README.md    # Dashboard docs
├── DASHBOARD_GUIDE.md     # Dashboard features
├── DASHBOARD_USAGE.md     # Dashboard walkthrough
├── DEMO_PERFECT.md        # Demo script
├── HACKATHON_READY.md     # Readiness checklist
├── CONTRIBUTING.md        # Contribution guide
├── GITHUB_PUSH_GUIDE.md   # Git workflow
├── PRE_PUSH_CHECKLIST.md  # Pre-deployment checks
├── GENERATION_AGENT_COMPLETE.md  # Implementation notes
├── YUTORI_INTEGRATED.md   # Yutori integration
└── YUTORI_STATUS.md       # Yutori status
```

### Templates (`templates/`)
```
templates/
└── dashboard.html         # Web dashboard UI
```

### Generated Content (Gitignored)
```
generated_content/         # Output directory
├── images/               # Generated images
├── audio/                # Generated audio
└── videos/               # Generated videos

traces/                   # Execution traces
└── cycle_*/              # Trace logs by cycle
```

## 🎯 Design Principles

### 1. **Clean Root**
- Only essential files in root directory
- Easy to navigate for new contributors
- Clear entry points (README, QUICKSTART, dashboard)

### 2. **Logical Grouping**
- Core code in `src/`
- Tests in `tests/`
- Examples in `examples/`
- Docs in `docs/`
- Utilities in `scripts/`
- Guides in `.guides/`

### 3. **Hidden Clutter**
- Development guides in `.guides/` (hidden from main view)
- Generated content gitignored
- Traces gitignored
- Virtual environment gitignored

### 4. **Easy Discovery**
- Each directory has a README
- Clear naming conventions
- Consistent structure

## 🔍 Finding Things

### "I want to..."

**...get started quickly**
→ `QUICKSTART.md`

**...understand the project**
→ `README.md`

**...run a demo**
→ `examples/` or `./start_dashboard.sh`

**...test an API**
→ `scripts/test_*.py`

**...read technical docs**
→ `docs/`

**...see development guides**
→ `.guides/`

**...understand the code**
→ `src/`

**...run tests**
→ `tests/`

## 📝 Maintenance

### Adding New Files

- **Core code** → `src/`
- **Tests** → `tests/`
- **Examples** → `examples/`
- **Technical docs** → `docs/`
- **Utility scripts** → `scripts/`
- **Development guides** → `.guides/`

### Keeping It Clean

1. Don't add files to root unless essential
2. Use appropriate subdirectories
3. Update relevant READMEs
4. Keep .gitignore updated
5. Document new directories

## 🎉 Result

A clean, professional, easy-to-navigate repository that makes a great first impression!
