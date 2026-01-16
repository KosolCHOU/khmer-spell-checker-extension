#!/bin/bash
# GitHub Setup Script
# Replace YOUR_USERNAME with your actual GitHub username

GITHUB_USERNAME="YOUR_USERNAME"
REPO_NAME="AstroAI"

echo "Setting up GitHub remote..."
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo "✅ Done! Your code is now on GitHub"
echo "🚀 Next: Go to railway.app to deploy"
