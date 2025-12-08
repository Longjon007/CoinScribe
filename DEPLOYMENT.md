# CoinScribe Deployment Guide

This guide provides comprehensive instructions for deploying CoinScribe to Netlify and configuring the CI/CD pipeline.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Build and Testing](#local-build-and-testing)
3. [Netlify Setup](#netlify-setup)
4. [GitHub Actions CI/CD](#github-actions-cicd)
5. [Environment Variables](#environment-variables)
6. [Troubleshooting](#troubleshooting)
7. [Production Checklist](#production-checklist)

## Prerequisites

Before deploying, ensure you have:

- [x] Node.js >= 18.0.0 installed
- [x] npm package manager
- [x] A GitHub account with this repository
- [x] A Netlify account (free tier is sufficient)
- [x] Git installed on your machine

## Local Build and Testing

### 1. Install Dependencies

```bash
npm ci
```

Using `npm ci` (clean install) is recommended for consistent builds as it uses the exact versions from `package-lock.json`.

### 2. Run Quality Checks

```bash
# Lint the code
npm run lint

# Type check
npm run type-check

# Check for security vulnerabilities (production only)
npm audit --production
```

### 3. Build for Production

```bash
npm run build
```

Expected output:
```
✓ 34 modules transformed.
dist/index.html                         1.14 kB │ gzip:  0.56 kB
dist/assets/index-B5PQ3PoQ.css          2.88 kB │ gzip:  1.09 kB
dist/assets/chart-vendor-ap62UwsT.js    0.04 kB │ gzip:  0.06 kB
dist/assets/index-D84AKtTh.js           5.37 kB │ gzip:  2.43 kB
dist/assets/react-vendor-DbiWhUg4.js  141.07 kB │ gzip: 45.29 kB
✓ built in ~2s
```

### 4. Preview Production Build

```bash
npm run preview
```

This starts a local server to preview the production build at `http://localhost:4173`.

## Netlify Setup

### Option 1: Deploy via Netlify CLI (Manual)

#### 1. Install Netlify CLI

```bash
npm install -g netlify-cli
```

#### 2. Login to Netlify

```bash
netlify login
```

This will open a browser window for authentication.

#### 3. Initialize Netlify Site

```bash
netlify init
```

Follow the prompts:
- Create a new site or link to an existing one
- Select your team
- Configure build settings:
  - Build command: `npm run build`
  - Publish directory: `dist`
  - Functions directory: `netlify/functions`

#### 4. Deploy

```bash
# Deploy to production
netlify deploy --prod

# Or deploy to a draft URL first
netlify deploy
```

### Option 2: Deploy via Netlify Web UI

1. **Create a New Site**
   - Log in to [Netlify](https://app.netlify.com/)
   - Click "Add new site" → "Import an existing project"
   - Connect to GitHub and select the CoinScribe repository

2. **Configure Build Settings**
   - Build command: `npm run build`
   - Publish directory: `dist`
   - Functions directory: `netlify/functions`

3. **Deploy**
   - Click "Deploy site"
   - Netlify will automatically build and deploy your site

### Option 3: Continuous Deployment via GitHub Actions

This is the recommended approach for production.

#### 1. Get Netlify Credentials

**Netlify Auth Token:**
1. Go to [Netlify User Settings](https://app.netlify.com/user/applications)
2. Click "New access token"
3. Give it a descriptive name (e.g., "GitHub Actions")
4. Copy the token (you won't see it again!)

**Netlify Site ID:**
1. Go to your site in Netlify
2. Navigate to "Site settings"
3. Find "Site information" section
4. Copy the "API ID" (this is your Site ID)

#### 2. Add GitHub Secrets

1. Go to your GitHub repository
2. Navigate to "Settings" → "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add two secrets:

   **Secret 1:**
   - Name: `NETLIFY_AUTH_TOKEN`
   - Value: Your Netlify access token

   **Secret 2:**
   - Name: `NETLIFY_SITE_ID`
   - Value: Your Netlify site ID

#### 3. Enable GitHub Actions

The workflow is already configured in `.github/workflows/deploy.yml`. It will:

- **On Pull Request:**
  - Install dependencies
  - Run linting
  - Run type checking
  - Build the application
  - Upload build artifacts

- **On Push to Main:**
  - Run all the above checks
  - Deploy to Netlify production

#### 4. Trigger a Deployment

```bash
# Make a change and push to trigger deployment
git add .
git commit -m "Trigger deployment"
git push origin main
```

The deployment status can be monitored in the "Actions" tab of your GitHub repository.

## Environment Variables

### Local Development

Create a `.env` file in the project root (this file is gitignored):

```env
# Example environment variables
# VITE_API_KEY=your_api_key_here
# VITE_API_URL=https://api.example.com
```

**Important:** All environment variables must be prefixed with `VITE_` to be accessible in your React application.

### Netlify Environment Variables

#### Via Netlify UI:
1. Go to your site in Netlify
2. Navigate to "Site settings" → "Environment variables"
3. Click "Add a variable"
4. Add your variables (without the `VITE_` prefix if they're Netlify-specific)

#### Via Netlify CLI:
```bash
netlify env:set VITE_API_KEY "your_api_key_here"
```

#### Via netlify.toml:
```toml
[context.production.environment]
  VITE_API_URL = "https://api.production.com"

[context.deploy-preview.environment]
  VITE_API_URL = "https://api.staging.com"
```

## Netlify Configuration

The `netlify.toml` file includes optimized configurations:

### Build Settings
```toml
[build]
  command = "npm run build"
  publish = "dist"
  functions = "netlify/functions"
```

### Security Headers
- Content Security Policy (CSP)
- X-Frame-Options
- X-Content-Type-Options
- X-XSS-Protection
- Referrer Policy

### Caching Strategy
- **Static Assets** (JS/CSS with hashed filenames): 1 year cache
- **HTML**: No cache, always revalidate
- **Images**: 1 week cache
- **API Functions**: 1 minute cache

### Plugins
The configuration includes the Lighthouse plugin for performance monitoring:
```toml
[[plugins]]
  package = "@netlify/plugin-lighthouse"
```

To enable it:
```bash
npm install @netlify/plugin-lighthouse --save-dev
```

## GitHub Actions Workflow

### Workflow Overview

The `.github/workflows/deploy.yml` file defines two jobs:

#### Job 1: Build and Test
- Checks out code
- Sets up Node.js
- Installs dependencies
- Runs linting
- Runs type checking
- Builds the application
- Uploads build artifacts (for main branch only)

#### Job 2: Deploy
- Runs only on pushes to main
- Downloads build artifacts
- Deploys to Netlify using Netlify CLI

### Workflow Optimization Features

1. **Concurrency Control**: Prevents multiple simultaneous deployments
2. **Dependency Caching**: Uses npm cache for faster builds
3. **Artifact Upload**: Build artifacts are uploaded for deployment
4. **Conditional Deployment**: Only deploys on main branch pushes

### Monitoring Workflow Runs

1. Go to the "Actions" tab in your GitHub repository
2. Click on a workflow run to see details
3. View logs for each step
4. Check deployment status in Netlify dashboard

## Troubleshooting

### Build Failures

#### Issue: "Module not found"
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Issue: "TypeScript errors"
```bash
# Run type check to see errors
npm run type-check

# Fix any type errors in your code
```

#### Issue: "Linting errors"
```bash
# View lint errors
npm run lint

# Auto-fix common issues
npm run lint:fix
```

### Deployment Failures

#### Issue: "Deployment timeout"
- Check Netlify deploy logs
- Ensure build completes in under 15 minutes
- Optimize build if necessary

#### Issue: "Missing environment variables"
- Verify all required variables are set in Netlify
- Check variable names match exactly (case-sensitive)
- Ensure `VITE_` prefix for client-side variables

#### Issue: "404 on routes"
- Ensure `netlify.toml` has proper redirect rules
- For SPA, add:
```toml
[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### GitHub Actions Issues

#### Issue: "NETLIFY_AUTH_TOKEN not found"
- Verify secret is added in GitHub repository settings
- Ensure secret name matches exactly
- Check secret hasn't expired

#### Issue: "Workflow not triggering"
- Verify workflow file is in `.github/workflows/`
- Check branch name matches workflow triggers
- Ensure Actions are enabled for the repository

## Production Checklist

Before deploying to production, ensure:

### Code Quality
- [ ] All tests pass
- [ ] No linting errors (`npm run lint`)
- [ ] No type errors (`npm run type-check`)
- [ ] No security vulnerabilities (`npm audit --production`)
- [ ] Build succeeds (`npm run build`)

### Configuration
- [ ] `package.json` version updated
- [ ] Environment variables configured in Netlify
- [ ] `netlify.toml` reviewed and updated
- [ ] Security headers configured
- [ ] Caching strategy appropriate

### CI/CD
- [ ] GitHub Actions workflow tested
- [ ] Secrets configured in GitHub
- [ ] Deployment triggers configured correctly
- [ ] Rollback strategy understood

### Performance
- [ ] Build output optimized (check bundle sizes)
- [ ] Images optimized
- [ ] Lazy loading implemented where appropriate
- [ ] Lighthouse scores acceptable

### Documentation
- [ ] README.md updated
- [ ] DEPLOYMENT.md reviewed
- [ ] API documentation updated (if applicable)
- [ ] Change log maintained

### Monitoring
- [ ] Error tracking configured
- [ ] Analytics configured (if applicable)
- [ ] Uptime monitoring enabled
- [ ] Performance monitoring enabled

## Deployment Commands Quick Reference

```bash
# Local development
npm run dev                    # Start dev server
npm run build                  # Build for production
npm run preview                # Preview production build
npm run lint                   # Run linting
npm run type-check            # Run type checking

# Netlify CLI
netlify login                  # Login to Netlify
netlify init                   # Initialize site
netlify deploy                 # Deploy to draft URL
netlify deploy --prod          # Deploy to production
netlify open                   # Open site in browser
netlify open:admin             # Open Netlify admin
netlify env:list              # List environment variables
netlify env:set KEY value     # Set environment variable

# GitHub
git push origin main          # Trigger automatic deployment
```

## Additional Resources

- [Netlify Documentation](https://docs.netlify.com/)
- [Vite Deployment Guide](https://vitejs.dev/guide/static-deploy.html)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [React Deployment Documentation](https://react.dev/learn/start-a-new-react-project#deploying-to-production)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Netlify deploy logs
3. Check GitHub Actions workflow logs
4. Create an issue in the GitHub repository
