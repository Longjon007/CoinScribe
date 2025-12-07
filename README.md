# CoinScribe

CoinScribe is an all-in-one crypto tracker that shows you not just what the market is doing, but why. It goes beyond simple price charts by integrating a powerful AI engine that instantly reads, understands, and summarizes the latest news for any coin.

## Repository Contents

This repository currently contains the setup utility for the CoinScribe project's development workflow.

### Auto-Tagging Setup Script (`Cli`)

The `Cli` file is a shell script designed to initialize the Continuous Integration (CI) environment by generating a GitHub Actions workflow file.

**Purpose:**
The script creates `.github/workflows/auto-tag.yml`. This workflow automates semantic versioning for the repository. When a Pull Request is merged into the `main` branch, the workflow:
1.  Analyzes the commit messages.
2.  Determines the appropriate version bump (Major, Minor, or Patch).
3.  Creates a new git tag.
4.  Publishes a GitHub Release with release notes.

**Usage:**

To set up the auto-tagging workflow, run the `Cli` script from the root of the repository:

```bash
bash Cli
```

Or, make it executable and run it directly:

```bash
chmod +x Cli
./Cli
```

**Version Bump Logic:**
The generated workflow looks for specific keywords in the commit messages to decide the version bump:
*   `[bump:major]` - Triggers a Major version update.
*   `[bump:minor]` - Triggers a Minor version update.
*   `[skip-bump]` - Skips tagging for this commit.
*   Default - Triggers a Patch version update.

## Getting Started with Development

1.  Clone the repository.
2.  Run the `Cli` script to ensure the CI/CD workflows are set up.
3.  (Future steps would go here as the application source code is added).
