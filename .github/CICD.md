# CI/CD Pipeline Documentation

This document explains the Continuous Integration and Continuous Deployment (CI/CD) pipeline for CoinScribe.

## Overview

CoinScribe uses GitHub Actions for automated building, testing, and deploying. The workflow is triggered on:
- Pull requests to `main` branch
- Pushes to `main` branch

## Workflow File

Location: `.github/workflows/deploy.yml`

## Workflow Jobs

### Job 1: Build and Test

**Triggers:** Pull requests and pushes to main

**Purpose:** Validate code quality and build the application

**Steps:**

1. **Checkout code**
   - Uses: `actions/checkout@v4`
   - Fetches the repository code

2. **Setup Node.js**
   - Uses: `actions/setup-node@v4`
   - Version: Node.js 18
   - Enables npm caching for faster builds

3. **Install dependencies**
   ```bash
   npm ci
   ```
   - Clean install using package-lock.json
   - Ensures consistent dependency versions

4. **Run ESLint**
   ```bash
   npm run lint
   ```
   - Checks code style and quality
   - Fails if any linting errors found
   - Maximum warnings: 0

5. **Run TypeScript type check**
   ```bash
   npm run type-check
   ```
   - Validates TypeScript types
   - Catches type errors before runtime

6. **Build application**
   ```bash
   npm run build
   ```
   - Environment: `NODE_ENV=production`
   - Generates optimized production build
   - Output: `dist/` directory

7. **Upload build artifacts** (main branch only)
   - Uses: `actions/upload-artifact@v4`
   - Artifact name: `dist`
   - Path: `dist/`
   - Retention: 7 days
   - Only runs on pushes to main

### Job 2: Deploy

**Triggers:** Only on pushes to main (after successful build)

**Dependencies:** Requires `build-and-test` job to succeed

**Purpose:** Deploy the built application to Netlify

**Steps:**

1. **Checkout code**
   - Uses: `actions/checkout@v4`
   - Needed for deployment context

2. **Download build artifacts**
   - Uses: `actions/download-artifact@v4.1.3`
   - Downloads the `dist` artifact from build job
   - Version v4.1.3 fixes CVE security vulnerability

3. **Deploy to Netlify**
   - Uses: `netlify/actions/cli@master`
   - Command: `deploy --prod --dir=dist`
   - Requires secrets:
     - `NETLIFY_AUTH_TOKEN`
     - `NETLIFY_SITE_ID`

4. **Comment deployment URL on PR** (PR only)
   - Uses: `actions/github-script@v7`
   - Comments on pull request with deployment info
   - Note: Currently only runs on PR events (not main pushes)

## Workflow Features

### Concurrency Control

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true
```

**Purpose:**
- Prevents multiple simultaneous deployments
- Cancels old deployments when new one starts
- Saves CI/CD minutes

### Permissions

#### Build Job
```yaml
permissions:
  contents: read
```
- Minimal permissions for security
- Only reads repository contents

#### Deploy Job
```yaml
permissions:
  contents: read
  pull-requests: write
```
- Reads repository contents
- Writes comments to pull requests

## Required Secrets

### NETLIFY_AUTH_TOKEN

**What it is:** Personal access token from Netlify

**How to get it:**
1. Go to https://app.netlify.com/user/applications
2. Click "New access token"
3. Give it a name (e.g., "GitHub Actions CoinScribe")
4. Copy the token immediately (you won't see it again)

**How to add it:**
1. Go to GitHub repository settings
2. Navigate to "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `NETLIFY_AUTH_TOKEN`
5. Value: Your token
6. Click "Add secret"

### NETLIFY_SITE_ID

**What it is:** Unique identifier for your Netlify site

**How to get it:**
1. Go to https://app.netlify.com/
2. Select your site
3. Go to "Site settings"
4. Find "Site information" section
5. Copy the "API ID" (this is your Site ID)

**How to add it:**
1. Go to GitHub repository settings
2. Navigate to "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `NETLIFY_SITE_ID`
5. Value: Your site ID
6. Click "Add secret"

## Workflow Execution

### On Pull Request

```
┌─────────────────────────────────┐
│  Pull Request Created/Updated   │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│      Checkout Repository        │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│       Setup Node.js 18          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│      Install Dependencies       │
│        (npm ci)                 │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│         Run Linting             │
│      (npm run lint)             │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│      Run Type Checking          │
│    (npm run type-check)         │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│      Build Application          │
│     (npm run build)             │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│      ✅ PR Checks Pass          │
└─────────────────────────────────┘
```

### On Push to Main

```
┌─────────────────────────────────┐
│      Push to Main Branch        │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│    Run All Build Steps          │
│  (Same as PR workflow)          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│    Upload Build Artifacts       │
│      (dist directory)           │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│   Download Build Artifacts      │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│     Deploy to Netlify           │
│    (Production)                 │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│  ✅ Deployment Complete         │
│  🌐 Site Live on Netlify        │
└─────────────────────────────────┘
```

## Monitoring Workflows

### GitHub Actions UI

1. **View all runs:**
   - Go to repository → "Actions" tab
   - See list of all workflow runs

2. **View specific run:**
   - Click on a workflow run
   - See job details and logs

3. **Re-run failed workflows:**
   - Click "Re-run jobs" button
   - Option to re-run all or failed jobs only

### Status Checks

On pull requests, you'll see:
- ✅ Build and Test - Passed
- ⏳ Build and Test - Running
- ❌ Build and Test - Failed

### Logs

Each step produces logs that can be viewed:
- Click on a job
- Click on a step to expand logs
- Download logs for offline viewing

## Workflow Optimization

### Current Optimizations

1. **Dependency Caching**
   - Node.js setup includes npm caching
   - Reduces installation time by ~50%

2. **Conditional Steps**
   - Artifact upload only on main
   - Deploy only on main
   - PR comments only on PRs

3. **Concurrency Control**
   - Cancels old deployments
   - Saves CI/CD minutes

4. **Minimal Permissions**
   - Each job has only needed permissions
   - Improves security

### Performance Metrics

| Stage | Expected Time |
|-------|---------------|
| Checkout | < 10s |
| Setup Node.js | < 30s (with cache) |
| Install Dependencies | < 30s (with cache) |
| Linting | < 10s |
| Type Checking | < 10s |
| Build | < 30s |
| Upload Artifacts | < 10s |
| Deploy | < 60s |
| **Total** | **< 3 minutes** |

## Troubleshooting

### Common Issues

#### 1. Workflow Not Triggering

**Problem:** Push to main but no workflow runs

**Solutions:**
- Check workflow file is in `.github/workflows/`
- Verify branch name matches workflow triggers
- Ensure Actions are enabled in repository settings

#### 2. Linting Failures

**Problem:** `npm run lint` fails

**Solutions:**
```bash
# Locally test and fix
npm run lint:fix
git add .
git commit -m "Fix linting errors"
git push
```

#### 3. Type Check Failures

**Problem:** `npm run type-check` fails

**Solutions:**
```bash
# Locally test
npm run type-check

# Fix type errors in code
# Push changes
```

#### 4. Build Failures

**Problem:** `npm run build` fails

**Solutions:**
- Check build logs for specific error
- Test build locally
- Verify all dependencies are in package.json
- Check for environment-specific issues

#### 5. Deployment Failures

**Problem:** Deploy step fails

**Possible Causes:**
- Missing `NETLIFY_AUTH_TOKEN` secret
- Missing `NETLIFY_SITE_ID` secret
- Invalid tokens
- Netlify site doesn't exist
- Network issues

**Solutions:**
1. Verify secrets are set correctly
2. Check token hasn't expired
3. Verify site ID is correct
4. Check Netlify status page

#### 6. Artifact Upload/Download Fails

**Problem:** Artifact steps fail

**Solutions:**
- Check artifact size (< 10 GB)
- Verify artifact name matches
- Check retention days setting
- Ensure proper permissions

### Debug Tips

1. **Enable debug logging:**
   Add to repository secrets:
   - `ACTIONS_RUNNER_DEBUG`: `true`
   - `ACTIONS_STEP_DEBUG`: `true`

2. **Add debug steps:**
   ```yaml
   - name: Debug Info
     run: |
       echo "Node version: $(node --version)"
       echo "npm version: $(npm --version)"
       ls -la
       pwd
   ```

3. **Test locally:**
   - Run all commands locally first
   - Use `act` to test GitHub Actions locally

## Security Best Practices

1. **Secrets Management**
   - Never commit secrets to code
   - Use GitHub Secrets for sensitive data
   - Rotate tokens regularly

2. **Permissions**
   - Use minimal permissions required
   - Review permissions regularly

3. **Dependencies**
   - Keep actions updated
   - Use specific versions (not `@latest`)
   - Review dependency updates

4. **Artifacts**
   - Don't include sensitive data
   - Set appropriate retention periods
   - Clean up old artifacts

## Maintenance

### Regular Tasks

1. **Update Actions** (Monthly)
   ```yaml
   # Current versions:
   actions/checkout@v4
   actions/setup-node@v4
   actions/upload-artifact@v4
   actions/download-artifact@v4.1.3
   netlify/actions/cli@master
   ```

2. **Review Logs** (Weekly)
   - Check for warnings
   - Monitor build times
   - Identify optimization opportunities

3. **Rotate Secrets** (Quarterly)
   - Generate new Netlify token
   - Update GitHub secrets
   - Test deployment

### Updating the Workflow

1. Make changes to `.github/workflows/deploy.yml`
2. Test changes on a feature branch
3. Create PR to main
4. Review workflow run
5. Merge if successful

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Netlify CLI Documentation](https://docs.netlify.com/cli/get-started/)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)

## Support

For CI/CD issues:
1. Check this documentation
2. Review workflow logs
3. Check Netlify deploy logs
4. Create an issue with:
   - Workflow run link
   - Error messages
   - Steps to reproduce
