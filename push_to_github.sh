#!/bin/bash
# Quick GitHub Push Script
# Edit the GITHUB_USERNAME below with your actual username

GITHUB_USERNAME="YOUR_USERNAME_HERE"
REPO_NAME="AstroAI"

echo "📦 Pushing to GitHub..."
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git 2>/dev/null || echo "Remote already exists"
git branch -M main
git push -u origin main

echo ""
echo "✅ Code pushed to GitHub!"
echo "🔗 Repository: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "🚀 Next step: Deploy on Render"
echo "   Go to: https://dashboard.render.com/select-repo?type=web"
