# Git Branching Model

## Rules

- Never push directly to main
- All changes go through Pull Request
- Each failure simulation gets its own branch
- Each production incident gets incident/* branch

---

## Branch Types

main
develop
feature/*
devops/*
bugfix/*
incident/*

---

## Merge Flow

feature → develop
devops → develop
develop → main (only stable state)
