### ❌ Accidental Direct Push to Main Branch
Tool: Git

**What I Was Trying To Do:**
Push initial setup changes to devops/initial-setup branch for review.

**Error / Symptom:**
Accidentally committed and pushed changes directly to the main branch.

Command used:
git push origin main

This violated the branch protection and production workflow policy.

**Root Cause:**
- I was on the wrong branch (main instead of devops/initial-setup).
- Did not verify current branch using `git branch` before pushing.
- No branch protection rules were configured on remote repository.

**How I Debugged:**
1. Checked current branch:
   git branch

2. Checked commit history:
   git log --oneline --graph --decorate

3. Verified what commit was pushed to main:
   git show <commit-id>

4. Checked remote tracking:
   git branch -vv

**Final Fix:**
Used git revert to safely undo the commit without rewriting history:

   git checkout main
   git revert <commit-id>

Then:
- Switched to correct branch:
   git checkout devops/initial-setup
- Re-applied changes properly
- Created Pull Request for review

**Production Lesson:**
- Never push directly to main.
- Always verify branch before committing.
- Enable branch protection rules in remote repository.
- In shared environments, use `git revert` instead of `git reset --hard` to avoid rewriting history.
- Production safety > convenience.
