---
name: github-actions-release-governance
description: Standardized guidelines for GitHub Actions CI/CD workflows in Android and Flutter projects. Covers concise workflow naming conventions, prerelease vs production release publishing rules, and downstream trigger synchronization.
---

# GitHub Actions Release & Workflow Governance Skill

This skill defines strict standards for writing, maintaining, and refactoring GitHub Actions workflow files (`.github/workflows/*.yml`) in Android and Flutter repositories.

---

## 1. Workflow Naming Conventions

### Top-Level Workflow Name (`name:`)
- **Keep it concise, high-level, and clean**: The top `name:` field is displayed in the GitHub Actions UI tab. It must avoid redundant descriptors.
- **Forbidden Redundancies**:
  - Do NOT include `"Android"` (AAB/APK builds are implicitly Android).
  - Do NOT include `"Workflow"` at the end (GitHub UI already categorizes it as a workflow).
  - Do NOT list file format details like `"AAB Bundle"`, `"APK Split"`, or `"Universal"` in the top title.
- **Format**: `[ProjectName] Target/Action (Modifiers)`
  - *Good*: `[VehereGo] Build Release (R8)`
  - *Good*: `[PyroMagma] Distribute AAB to Google Play Store`
  - *Bad*: `[VehereGo] Android Release & AAB Build Workflow (R8 Obfuscated & Universal APK)`

### Job & Step Names
- Detailed technical descriptions (e.g. `Build R8 Obfuscated Release AAB & Universal APK`, `Decode keystore and create key.properties`) belong inside `jobs.<job_id>.name` and `steps[].name` for build log clarity.

---

## 2. Release & Prerelease Publishing Rules

### GitHub Releases Strategy
1. **Test / Debug / Prerelease Builds**:
   - Test builds, debug builds, and Master pipeline builds MUST publish test APKs directly to **GitHub Releases** (marked with `prerelease: true` and dedicated test tags like `*-debug`, `*-master`) so that testers and developers can easily download test packages directly from GitHub Releases.

2. **Official Production Releases**:
   - Official release builds triggered by version tags (e.g., `v*`) publish to **GitHub Releases** with `prerelease: false`.
   - Official production releases MUST contain both **AAB** (for Google Play Store) and **APK** (for direct testing).

---

## 3. Downstream Trigger Synchronization (`workflow_run`)

When changing a top-level `name:` in a workflow file:
1. Search the repository for any downstream workflows using `workflow_run.workflows`.
2. Update all references to match the exact new `name:` string.
3. Verify trigger chains (e.g., Build Release -> Play Store Upload -> Telegram Notification).

---

## 4. Pre-Task Inspection Protocol

Before applying any edits to CI/CD workflow files:
1. **Read and analyze ALL related workflow files** in `.github/workflows/`.
2. **Check downstream references** (`workflow_run`, `gh release download`, tags).
3. **Confirm exact user intent** before modifying step/job definitions or moving files.
