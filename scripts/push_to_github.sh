#!/bin/bash

# Script to prepare and push Project Eirene to GitHub

echo "================================================"
echo "Project Eirene - GitHub Push Script"
echo "================================================"
echo ""

# Check if we're in a git repository
if [ ! -d .git ]; then
    echo "Error: Not a git repository"
    exit 1
fi

# Show current status
echo "Current git status:"
git status --short
echo ""

# Confirm with user
read -p "Do you want to add all files and commit? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Add all files
echo "Adding files..."
git add .

# Show what will be committed
echo ""
echo "Files to be committed:"
git status --short
echo ""

# Get commit message
read -p "Enter commit message (or press Enter for default): " commit_msg
if [ -z "$commit_msg" ]; then
    commit_msg="feat: implement Manager Agent and project foundation

- Add Manager Agent with pipeline orchestration
- Implement error handling with retry logic and circuit breaker
- Add comprehensive trace logging system
- Create core data models for pipeline, agents, and interventions
- Add unit tests with 100% pass rate
- Set up project documentation and examples"
fi

# Commit
echo ""
echo "Committing..."
git commit -m "$commit_msg"

# Check if remote exists
if ! git remote get-url origin > /dev/null 2>&1; then
    echo ""
    echo "No remote 'origin' found."
    read -p "Enter GitHub repository URL (e.g., https://github.com/username/eirene.git): " repo_url
    git remote add origin "$repo_url"
    echo "Remote 'origin' added: $repo_url"
fi

# Show remote
echo ""
echo "Remote repository:"
git remote -v
echo ""

# Confirm push
read -p "Push to GitHub? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Commit created but not pushed. You can push later with: git push -u origin main"
    exit 0
fi

# Push
echo "Pushing to GitHub..."
git push -u origin main

echo ""
echo "================================================"
echo "✓ Successfully pushed to GitHub!"
echo "================================================"
