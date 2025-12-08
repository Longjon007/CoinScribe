# GitHub Secrets Setup Guide

This guide walks you through setting up the required secrets for automatic deployment of CoinScribe to Netlify.

## Overview

For automated deployment to work, you need to configure two secrets in GitHub:
1. `NETLIFY_AUTH_TOKEN` - Authenticates with Netlify
2. `NETLIFY_SITE_ID` - Identifies which site to deploy to

## Prerequisites

- ✅ GitHub account with access to this repository
- ✅ Netlify account (free tier works)
- ✅ Repository admin access (required to add secrets)

## Step-by-Step Setup

### Step 1: Create Netlify Account

If you don't have a Netlify account:

1. Go to https://www.netlify.com/
2. Click "Sign up"
3. Choose "Sign up with GitHub" for easy integration
4. Authorize Netlify to access your GitHub account

### Step 2: Create a Netlify Site

#### Option A: Manual Setup (Recommended for first-time)

1. Log in to https://app.netlify.com/
2. Click "Add new site" → "Import an existing project"
3. Choose "GitHub"
4. Find and select the "CoinScribe" repository
5. Configure build settings:
   - **Build command:** `npm run build`
   - **Publish directory:** `dist`
   - **Functions directory:** `netlify/functions`
6. Click "Deploy site"

The site will deploy with a random name like `random-name-123456.netlify.app`.

#### Option B: Using Netlify CLI

```bash
# Install Netlify CLI globally
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize site
netlify init
```

Follow the prompts to create a new site or link to an existing one.

### Step 3: Get Netlify Auth Token

1. Go to https://app.netlify.com/user/applications
2. Scroll to "Personal access tokens" section
3. Click "New access token"
4. Give it a descriptive name:
   - Example: "GitHub Actions - CoinScribe Deployment"
5. Click "Generate token"
6. **IMPORTANT:** Copy the token immediately
   - ⚠️ You won't be able to see it again!
   - Save it temporarily in a secure location

**Example token format:**
```
nfp_aBc123DeF456GhI789JkL012MnO345PqR678
```

### Step 4: Get Netlify Site ID

1. Go to https://app.netlify.com/
2. Click on your CoinScribe site
3. Go to "Site settings"
4. Find the "Site information" section
5. Copy the **API ID**
   - This is your Site ID
   - It looks like: `abcd1234-ef56-7890-abcd-ef1234567890`

**Example Site ID format:**
```
12345678-90ab-cdef-1234-567890abcdef
```

### Step 5: Add Secrets to GitHub

#### Navigate to Secrets Page

1. Go to your GitHub repository: https://github.com/Longjon007/CoinScribe
2. Click "Settings" (top menu)
3. In the left sidebar, expand "Secrets and variables"
4. Click "Actions"

#### Add NETLIFY_AUTH_TOKEN

1. Click "New repository secret" button
2. Fill in the form:
   - **Name:** `NETLIFY_AUTH_TOKEN` (exactly as written)
   - **Value:** Paste your Netlify token from Step 3
3. Click "Add secret"

#### Add NETLIFY_SITE_ID

1. Click "New repository secret" button again
2. Fill in the form:
   - **Name:** `NETLIFY_SITE_ID` (exactly as written)
   - **Value:** Paste your Site ID from Step 4
3. Click "Add secret"

### Step 6: Verify Secrets

After adding both secrets, you should see them listed:

```
NETLIFY_AUTH_TOKEN    Updated now
NETLIFY_SITE_ID       Updated now
```

**Security Note:** The values are hidden and cannot be viewed after creation.

### Step 7: Test the Deployment

1. Make a small change to the repository
2. Commit and push to main:
   ```bash
   git add .
   git commit -m "Test automated deployment"
   git push origin main
   ```
3. Go to "Actions" tab in GitHub
4. Watch the workflow run
5. After ~3 minutes, your site should be deployed!

## Verification Checklist

- [ ] Netlify account created
- [ ] Netlify site created for CoinScribe
- [ ] `NETLIFY_AUTH_TOKEN` added to GitHub secrets
- [ ] `NETLIFY_SITE_ID` added to GitHub secrets
- [ ] Test deployment triggered
- [ ] Deployment successful
- [ ] Site accessible at Netlify URL

## Troubleshooting

### Secret Names Don't Match

**Problem:** Workflow fails with "NETLIFY_AUTH_TOKEN not found"

**Solution:** Secret names are case-sensitive. Verify exact names:
- ✅ `NETLIFY_AUTH_TOKEN` (correct)
- ❌ `netlify_auth_token` (incorrect)
- ❌ `NETLIFY_TOKEN` (incorrect)

### Invalid Token Error

**Problem:** "Error: Invalid Netlify token"

**Solutions:**
1. Verify token was copied completely (no spaces)
2. Generate a new token from Netlify
3. Update the GitHub secret with new token

### Site ID Not Found

**Problem:** "Error: Site not found"

**Solutions:**
1. Verify you copied the API ID (not the site name)
2. Ensure the site exists in your Netlify account
3. Check you're using the correct Netlify account

### Deployment Fails After Adding Secrets

**Problem:** Workflow runs but deployment fails

**Checklist:**
1. Check GitHub Actions logs for specific error
2. Verify secrets are added (they should be listed)
3. Check Netlify deploy logs
4. Ensure site exists and is active on Netlify

## Security Best Practices

### Token Security

✅ **DO:**
- Store tokens only in GitHub Secrets
- Use descriptive token names in Netlify
- Rotate tokens every 6-12 months
- Delete old tokens after rotation

❌ **DON'T:**
- Commit tokens to code
- Share tokens in chat or email
- Use same token across multiple projects
- Leave tokens in clipboard history

### Access Control

- Limit repository access to trusted collaborators
- Review who has admin access regularly
- Use branch protection on main branch
- Require PR reviews for main branch

## Rotating Secrets

To rotate your secrets (recommended every 6-12 months):

1. **Generate New Netlify Token:**
   - Go to https://app.netlify.com/user/applications
   - Create new access token
   - Copy new token

2. **Update GitHub Secret:**
   - Go to repository Settings → Secrets → Actions
   - Click on `NETLIFY_AUTH_TOKEN`
   - Click "Update secret"
   - Paste new token
   - Click "Update secret"

3. **Delete Old Token:**
   - Go back to Netlify applications page
   - Find old token
   - Click "Revoke" or "Delete"

4. **Test Deployment:**
   - Trigger a deployment
   - Verify it succeeds with new token

## Alternative Deployment Methods

### Using Netlify CLI Locally

If you prefer manual deployment without GitHub Actions:

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login
netlify login

# Deploy to production
netlify deploy --prod

# Or deploy to draft URL first
netlify deploy
```

### Using Netlify Git Integration

You can skip GitHub Actions and use Netlify's built-in GitHub integration:

1. Connect repository in Netlify
2. Configure build settings in Netlify UI
3. Netlify automatically deploys on push to main

**Note:** GitHub Actions provides more control and can run additional checks.

## Environment Variables for Your Site

If your application needs environment variables:

### In Netlify UI:
1. Go to your site in Netlify
2. Site settings → Environment variables
3. Add variables (don't need `VITE_` prefix in Netlify)

### In netlify.toml:
```toml
[context.production.environment]
  VITE_API_URL = "https://api.production.com"

[context.deploy-preview.environment]
  VITE_API_URL = "https://api.staging.com"
```

## Getting Help

If you encounter issues:

1. **Check Documentation:**
   - [DEPLOYMENT.md](./DEPLOYMENT.md) - Full deployment guide
   - [.github/CICD.md](./.github/CICD.md) - CI/CD details

2. **Review Logs:**
   - GitHub Actions logs (Actions tab)
   - Netlify deploy logs (Netlify dashboard)

3. **Common Issues:**
   - Verify secret names are exact
   - Check tokens haven't expired
   - Ensure Netlify site exists

4. **Create Issue:**
   - Provide error messages
   - Include workflow run link
   - Describe steps taken

## Additional Resources

- [Netlify Documentation](https://docs.netlify.com/)
- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Netlify CLI Documentation](https://docs.netlify.com/cli/get-started/)

## Quick Reference

### Required Secrets

| Secret Name | Where to Get It | Format |
|-------------|----------------|--------|
| NETLIFY_AUTH_TOKEN | Netlify → User Settings → Applications → Personal access tokens | `nfp_xxxxxx...` |
| NETLIFY_SITE_ID | Netlify → Site Settings → Site information → API ID | UUID format |

### Important URLs

- Netlify Dashboard: https://app.netlify.com/
- Netlify Tokens: https://app.netlify.com/user/applications
- GitHub Secrets: https://github.com/Longjon007/CoinScribe/settings/secrets/actions

### Commands

```bash
# Create new token (Netlify CLI)
netlify login

# View site info
netlify status

# Manual deploy
netlify deploy --prod

# View deploy logs
netlify logs:deploy
```

---

**Setup Complete?** ✅ Once secrets are added, push to main to deploy automatically!
