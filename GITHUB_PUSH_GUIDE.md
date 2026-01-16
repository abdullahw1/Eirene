# GitHub Push Guide

## Quick Start (Automated)

Run the automated script:
```bash
./push_to_github.sh
```

This script will:
1. Show current git status
2. Add all files
3. Create a commit with a descriptive message
4. Push to GitHub

## Manual Steps

If you prefer to do it manually:

### 1. Check Status
```bash
git status
```

### 2. Add Files
```bash
# Add all files
git add .

# Or add specific files
git add README.md LICENSE src/ tests/ docs/
```

### 3. Commit
```bash
git commit -m "feat: implement Manager Agent and project foundation

- Add Manager Agent with pipeline orchestration
- Implement error handling with retry logic and circuit breaker
- Add comprehensive trace logging system
- Create core data models for pipeline, agents, and interventions
- Add unit tests with 100% pass rate
- Set up project documentation and examples"
```

### 4. Set Remote (if not already set)
```bash
# Check current remote
git remote -v

# Add remote if needed
git remote add origin https://github.com/yourusername/eirene.git
```

### 5. Push to GitHub
```bash
# First push
git push -u origin main

# Subsequent pushes
git push
```

## What Gets Pushed

✅ **Included:**
- Source code (`src/`)
- Tests (`tests/`)
- Documentation (`docs/`, `README.md`, etc.)
- Configuration examples (`.env.example`)
- Project files (`requirements.txt`, `pyproject.toml`)
- Examples (`examples/`)

❌ **Excluded (via .gitignore):**
- `.env` (your actual API keys)
- `.venv/` (virtual environment)
- `__pycache__/` (Python cache)
- `traces/` (execution logs)
- `.pytest_cache/` (test cache)
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)

## Verify Before Pushing

Check what will be committed:
```bash
git status
git diff --cached
```

## After Pushing

1. Visit your GitHub repository
2. Verify all files are present
3. Check that README displays correctly
4. Ensure no sensitive data (API keys) was committed

## Troubleshooting

### Remote already exists
```bash
git remote remove origin
git remote add origin https://github.com/yourusername/eirene.git
```

### Authentication issues
Use GitHub CLI or personal access token:
```bash
# Using GitHub CLI
gh auth login

# Or use HTTPS with token
git remote set-url origin https://YOUR_TOKEN@github.com/yourusername/eirene.git
```

### Large files
If you accidentally added large files:
```bash
git rm --cached path/to/large/file
echo "path/to/large/file" >> .gitignore
git commit --amend
```
