# 🌿 QueryShield AI — Git Branching Guide
> For a 3-member team: 1 Backend (Dhinakaran) + 2 Frontend members

---

## 👥 Who Works Where

| Member | Role | Branch Area |
|--------|------|-------------|
| **Dhinakaran** | Backend (FastAPI + DB) | `feature/phaseX-backend-...` |
| **Friend 1** | Frontend (Next.js) | `feature/phaseX-frontend-...` |
| **Friend 2** | Frontend (Next.js) | `feature/phaseX-frontend-...` |

---

## 🗂️ Branch Structure

```
main              ← Final production-ready code (merge only when fully done)
└── develop       ← Integration branch (everyone merges their work here)
    ├── feature/phase2-csv-upload           ← Backend feature branch
    ├── feature/phase3-schema-detection     ← Backend feature branch
    ├── feature/phase2-frontend-upload-ui   ← Frontend feature branch
    └── feature/phase3-frontend-query-ui    ← Frontend feature branch
```

> **Rule:** Never commit directly to `main` or `develop`.
> Always work on a feature branch, then merge into `develop`.

---

## ✅ Step-by-Step Workflow (Do This Every Phase)

### 🔵 BEFORE You Start Coding

```bash
# 1. Switch to develop and pull the latest code
git checkout develop
git pull origin develop

# 2. Create your feature branch FROM develop
git checkout -b feature/phase3-schema-detection

# 3. Push branch to GitHub immediately
git push -u origin feature/phase3-schema-detection
```

> ⚠️ Always pull `develop` first before creating a new branch — so you start with the latest code.

---

### 🟡 WHILE Coding (commit often!)

```bash
# After writing a small chunk of code:
git add .
git commit -m "feat: add schema fetcher from information_schema"

# After fixing something:
git commit -m "fix: handle empty table edge case in schema detector"

# Push your progress to GitHub anytime:
git push
```

#### Commit Message Format
```
feat:     New feature
fix:      Bug fix
db:       Database changes
refactor: Code cleanup
test:     Add tests
docs:     Documentation update
```

**Examples:**
```
feat: add /schema endpoint to return all table columns
fix: encode special chars in DB password
db: add indexes on foreign key columns
```

---

### 🟢 AFTER Coding (Phase Complete)

```bash
# 1. Make sure all changes are committed
git add .
git commit -m "feat: phase 3 complete - schema detection and injection"
git push

# 2. Switch to develop and pull latest
git checkout develop
git pull origin develop

# 3. Merge your feature branch into develop
git merge feature/phase3-schema-detection

# 4. Push develop to GitHub
git push origin develop

# 5. Delete the feature branch (cleanup)
git branch -d feature/phase3-schema-detection
git push origin --delete feature/phase3-schema-detection
```

---

## 🔄 Full Phase Cycle (Summary)

```
git checkout develop
git pull origin develop
git checkout -b feature/phaseX-your-feature
git push -u origin feature/phaseX-your-feature

     ↓ [ code → commit → code → commit ]

git add .
git commit -m "feat: ..."
git push

     ↓ [ phase done ]

git checkout develop
git pull origin develop
git merge feature/phaseX-your-feature
git push origin develop
git branch -d feature/phaseX-your-feature
git push origin --delete feature/phaseX-your-feature
```

---

## 👥 Team Coordination Rules

| Rule | Why |
|------|-----|
| Always branch from `develop` | Ensures you have the latest code |
| Pull `develop` before merging | Avoids conflicts |
| One feature = one branch | Keeps history clean |
| Commit small and often | Easier to review and fix conflicts |
| Never force push to `develop` or `main` | Protects shared code |
| Communicate before merging | Tell teammates before merging to avoid conflicts |

---

## 🚀 Branch Naming Convention

```
feature/phase2-csv-upload             ← backend
feature/phase2-frontend-upload-ui     ← frontend
feature/phase3-schema-detection       ← backend
feature/phase3-frontend-query-ui      ← frontend
hotfix/fix-db-connection              ← urgent bug fix
```

---

## 🔧 The `develop` Branch — Key Points

- `develop` = the **shared integration branch** where all features come together
- **All PRs/merges go into `develop` first**, not `main`
- Before merging your feature → always `git pull origin develop` first
- The frontend and backend teams both merge into `develop`
- `main` only gets updated at the **end of the entire project**

---

## 📋 Quick Command Reference

| Action | Command |
|--------|---------|
| See all branches | `git branch -a` |
| Switch branch | `git checkout branch-name` |
| Create + switch | `git checkout -b new-branch` |
| Pull latest | `git pull origin develop` |
| Push new branch | `git push -u origin branch-name` |
| Push updates | `git push` |
| Merge into develop | `git checkout develop` → `git merge feature/...` |
| Delete local branch | `git branch -d branch-name` |
| Delete remote branch | `git push origin --delete branch-name` |
| Check status | `git status` |
| See commit history | `git log --oneline` |

---

## ⚠️ If You Get a Merge Conflict

```bash
# 1. Git will tell you which file has a conflict
# 2. Open the file — look for conflict markers:

<<<<<<< HEAD (your changes)
your code here
=======
their code here
>>>>>>> feature/other-branch

# 3. Edit the file manually to keep the correct version
# 4. Then:
git add .
git commit -m "fix: resolve merge conflict in schema.py"
git push
```

---

## 📁 Who Owns What Directory

```
QueryShield AI/
├── backend/          ← 🔵 Dhinakaran (Backend)
│   ├── main.py
│   ├── database.py
│   ├── csv_uploader.py
│   └── ...
├── db/               ← 🔵 Dhinakaran (DB Scripts)
│   ├── schema.sql
│   └── seed.sql
├── tests/            ← 🔵 Dhinakaran (Backend Tests)
├── frontend/         ← 🟠 Friend 1 & Friend 2 (Next.js)
│   └── ...
├── requirements.txt  ← 🔵 Dhinakaran
├── .env              ← ⛔ Never commit this! (in .gitignore)
└── .gitignore
```

> Frontend friends: clone the repo, work only inside `frontend/` folder.
> Backend: work only inside `backend/`, `db/`, `tests/`.
