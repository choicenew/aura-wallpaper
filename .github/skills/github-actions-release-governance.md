---
name: github-actions-release-governance
description: Standardized guidelines for GitHub Actions CI/CD workflows in Android and Flutter projects. Covers concise workflow naming conventions, separation of debug vs release artifacts, prevention of GitHub Release pollution, and downstream trigger synchronization.
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

## 2. Release & Artifact Boundary Rules

### GitHub Releases vs. Internal Artifacts
1. **Official Production Releases**:
   - Only release workflows triggered by version tags (e.g., `v*`) or official release dispatches may publish to **GitHub Releases** (`softprops/action-gh-release@v2`).
   - Official release assets MUST contain both **AAB** (for Google Play) and **APK** (for direct testing/distribution).

2. **CI / Debug / Master Synced Pipelines**:
   - Master branch CI pipelines, debug builds, and dependency governance workflows MUST NEVER publish to GitHub Releases.
   - Debug or test APKs MUST NOT pollute the GitHub Releases page. If temporary binaries are required, store them as CI run artifacts (`actions/upload-artifact@v4`) or keep builds strictly in-memory.

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
