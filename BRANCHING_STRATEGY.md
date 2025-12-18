# Branching Strategy

## Overview

This project follows a milestone-based branching strategy where each milestone has its own feature branch that merges back to `main` upon completion.

## Branch Structure

```
main (protected)
├── milestone-1-rtsp-setup
├── milestone-2-motion-detection
├── milestone-3-fall-detection
├── milestone-4-line-alerts
├── milestone-5-line-webhook
├── milestone-6-ota-updates
├── milestone-7-voice-alert
├── milestone-8-pan-tilt
└── milestone-9-final-delivery
```

## Branch Naming Convention

- **Main Branch**: `main` - Production-ready code
- **Milestone Branches**: `milestone-{number}-{description}`
- **Hotfix Branches**: `hotfix/{issue-description}`
- **Feature Branches** (if needed): `feature/{milestone-number}-{feature-name}`

## Workflow

### 1. Starting a New Milestone

```bash
# Ensure main is up to date
git checkout main
git pull origin main

# Create milestone branch
git checkout -b milestone-1-rtsp-setup

# Push to remote
git push -u origin milestone-1-rtsp-setup
```

### 2. Development Process

```bash
# Make changes
git add .
git commit -m "feat: implement RTSP stream handler"

# Push changes
git push origin milestone-1-rtsp-setup
```

### 3. Commit Message Convention

Follow conventional commits:

- `feat:` - New feature
- `fix:` - Bug fix
- `test:` - Adding or updating tests
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes

Examples:
```
feat: add motion detection background subtraction
fix: resolve RTSP connection timeout issue
test: add unit tests for fall detection algorithm
docs: update setup manual with LINE API configuration
```

### 4. Testing Before Merge

```bash
# Run all tests
pytest tests/ -v --cov=src

# Run linting
flake8 src/
black src/ --check

# Run type checking
mypy src/
```

### 5. Merging to Main

```bash
# Ensure all tests pass
pytest tests/ -v

# Switch to main
git checkout main
git pull origin main

# Merge milestone branch
git merge --no-ff milestone-1-rtsp-setup

# Tag the milestone
git tag -a milestone-1 -m "Milestone 1: RTSP & Environment Setup"

# Push to remote
git push origin main
git push origin milestone-1
```

### 6. Creating Pull Request (Optional)

If using GitHub PR workflow:

1. Push milestone branch to remote
2. Create Pull Request on GitHub
3. Wait for CI/CD checks to pass
4. Request code review (if applicable)
5. Merge PR using "Squash and merge" or "Create merge commit"
6. Delete milestone branch after merge

## Branch Protection Rules

### Main Branch Protection

- Require pull request reviews before merging
- Require status checks to pass before merging
- Require branches to be up to date before merging
- Include administrators in restrictions

## Milestone Completion Checklist

Before merging a milestone branch to main:

- [ ] All unit tests pass
- [ ] Code coverage meets minimum threshold (80%)
- [ ] Linting passes (flake8, black)
- [ ] Type checking passes (mypy)
- [ ] Documentation updated
- [ ] Manual testing completed
- [ ] Client deliverable prepared (if applicable)
- [ ] CHANGELOG.md updated

## Hotfix Process

For urgent fixes:

```bash
# Create hotfix branch from main
git checkout main
git checkout -b hotfix/rtsp-connection-fix

# Make fix
git add .
git commit -m "fix: resolve RTSP reconnection issue"

# Merge back to main
git checkout main
git merge --no-ff hotfix/rtsp-connection-fix

# Tag hotfix
git tag -a v1.0.1 -m "Hotfix: RTSP connection stability"

# Push
git push origin main
git push origin v1.0.1

# Delete hotfix branch
git branch -d hotfix/rtsp-connection-fix
```

## Release Tags

- Milestone releases: `milestone-{number}` (e.g., `milestone-1`, `milestone-2`)
- Version releases: `v{major}.{minor}.{patch}` (e.g., `v1.0.0`, `v1.0.1`)
- Final release: `v1.0.0-final`

## Best Practices

1. **Commit Often**: Make small, focused commits
2. **Write Clear Messages**: Use conventional commit format
3. **Test Before Push**: Run tests locally before pushing
4. **Keep Branches Updated**: Regularly merge main into milestone branches
5. **Delete Merged Branches**: Clean up after successful merges
6. **Use Tags**: Tag important milestones and releases

