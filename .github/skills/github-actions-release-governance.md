---
name: github-actions-release-governance
description: Comprehensive standards and guidelines for GitHub Actions CI/CD workflows in Android/Flutter projects. Standardizes concise top-level workflow titles, strict trigger control (prohibiting auto-build on push to main), prerelease vs release publishing rules, and downstream workflow_run linkages.
---

# GitHub Actions Release & Workflow Governance Skill

This skill defines mandatory rules for writing, maintaining, and refactoring GitHub Actions workflow files (`.github/workflows/*.yml`) across Android and Flutter repositories.

---

## 1. Trigger Control Rules (禁止 Push 自动触发编译)

- **Release Build Workflows** (e.g., `pyromagma_build_release_r8.yml`, `veherego_build_release_r8.yml`):
  - **STRICTLY PROHIBITED**: Do NOT add `push.branches: [ main, master ]`.
  - **MANDATORY**: Release workflows must ONLY trigger on version tags or manual invocation:
    ```yaml
    on:
      push:
        tags:
          - 'v*'
      workflow_dispatch:
    ```
  - **Reason**: Pushing code or documentation commits to `main` must NEVER trigger automatic full-scale compilation or release builds.

---

## 2. Workflow Naming Conventions (标题命名规范)

### Top-Level Title (`name:`)
- **Keep it concise, high-level, and clean**: The top `name:` field is shown in the GitHub Actions UI tab.
- **Forbidden Redundant Words**:
  - Do NOT include `"Android"` (AAB/APK builds are implicitly Android).
  - Do NOT include `"Workflow"` at the end (GitHub UI already categorizes it).
  - Do NOT list file format/architecture details like `"AAB Bundle"`, `"APK Split"`, or `"Universal"` in the top title.
- **Format**: `[ProjectName] Target/Action (Modifiers)`
  - *Correct*: `[VehereGo] Build Release (R8)`
  - *Correct*: `[PyroMagma] Build Release (R8)`
  - *Incorrect*: `[VehereGo] Android Release & AAB Build Workflow (R8 Obfuscated & Universal APK)`

### Job & Step Names
- **Do NOT shorten job or step names**: Technical descriptions (e.g., `Build R8 Obfuscated Release AAB & Universal APK`, `Extract Dynamic Version from pubspec.yaml`) MUST be preserved inside `jobs.<job_id>.name` and `steps[].name` for clear build logs.

---

## 3. Release & Prerelease Publishing Protocol

### GitHub Releases Rules
1. **Test / Debug / Prerelease Builds**:
   - Test builds and Master pipeline builds MUST publish test APKs to **GitHub Releases** marked as `prerelease: true` (using dedicated tags like `*-debug`, `*-master`) so developers and testers can easily download test installation packages directly.
2. **Production Release Builds**:
   - Official release builds publish to **GitHub Releases** as `prerelease: false`.
   - Official release assets MUST contain both **AAB** (for Google Play Store) and **APK** (for direct testing).

---

## 4. Downstream Trigger Linkage (`workflow_run`)

When modifying a workflow's top-level `name:`:
1. Search the entire `.github/workflows/` directory for any downstream workflows referencing `workflow_run.workflows`.
2. Update all matching string references in sync to prevent breaking automated deployment pipelines (e.g., Google Play deployment or Telegram notification workflows).

---

## 5. Execution Safeguards

1. **No Unauthorized File System Actions**:
   - NEVER execute unrequested shell commands, file renames (`git mv`), file deletions, or unauthorized structural changes.
2. **Pre-Task Inspection**:
   - Always inspect all trigger conditions (`on:`), output paths, and downstream dependencies before modifying any workflow file.
