# CoinScribe

[![Build and Deploy](https://github.com/Longjon007/CoinScribe/actions/workflows/deploy.yml/badge.svg)](https://github.com/Longjon007/CoinScribe/actions/workflows/deploy.yml)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Node](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.9.3-blue.svg)](https://www.typescriptlang.org/)
[![React](https://img.shields.io/badge/React-18.3.1-blue.svg)](https://react.dev/)

CoinScribe is an all-in-one crypto tracker that shows you not just what the market is doing, but why. It goes beyond simple price charts by integrating a powerful AI engine that instantly reads, understands, and summarizes the latest news for any coin.

## 🚀 Quick Start

### Prerequisites

- Node.js >= 18.0.0
- npm (comes with Node.js)

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/Longjon007/CoinScribe.git
cd CoinScribe

# Run the quickstart script
./scripts/quickstart.sh
```

The quickstart script will:
- ✅ Check all prerequisites
- ✅ Install dependencies
- ✅ Run quality checks (linting, type-checking)
- ✅ Build the application
- ✅ Run security audit

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/Longjon007/CoinScribe.git
cd CoinScribe

# Install dependencies
npm install

# Start development server
npm run dev
```

## 📦 Building the Project

### Development Build

```bash
npm run dev
```

This starts the Vite development server with hot module replacement.

### Production Build

```bash
npm run build
```

The production build artifacts will be generated in the `dist/` directory. The build process:
- Transpiles TypeScript to JavaScript
- Bundles all dependencies
- Minifies and optimizes code
- Generates source maps
- Optimizes assets for production

Build output typically takes ~2 seconds and produces:
- `dist/index.html` - Entry HTML file
- `dist/assets/` - Bundled JavaScript, CSS, and other assets

### Build Verification

Before deploying, verify your build:

```bash
# Run linting
npm run lint

# Run type checking
npm run type-check

# Build the project
npm run build

# Preview production build locally
npm run preview
```

## 🔍 Code Quality

### Linting

```bash
# Check for linting errors
npm run lint

# Auto-fix linting errors
npm run lint:fix
```

### Type Checking

```bash
npm run type-check
```

### Security Audit

```bash
# Check for production vulnerabilities
npm audit --production

# Check all vulnerabilities
npm audit
```

## 🌐 Deployment

### Deploy to Netlify

CoinScribe is configured to deploy to Netlify automatically via GitHub Actions.

#### Prerequisites

1. A Netlify account
2. A Netlify site created for this project
3. GitHub repository secrets configured:
   - `NETLIFY_AUTH_TOKEN` - Your Netlify personal access token
   - `NETLIFY_SITE_ID` - Your Netlify site ID

**Need help?** See [SECRETS_SETUP.md](./SECRETS_SETUP.md) for a detailed step-by-step guide on obtaining and configuring these secrets.

#### Automatic Deployment

The project uses GitHub Actions for CI/CD:

- **On Pull Request**: Runs linting, type-checking, and builds the project
- **On Push to Main**: Runs all checks, builds, and deploys to Netlify

The workflow is defined in `.github/workflows/deploy.yml`.

#### Manual Deployment

If you want to deploy manually:

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy to production
netlify deploy --prod --dir=dist
```

### Environment Variables

Create a `.env` file for local development (do not commit this file):

```env
# Add your environment variables here
# VITE_API_KEY=your_api_key
```

Environment variables must be prefixed with `VITE_` to be accessible in the application.

## 📁 Project Structure

```
CoinScribe/
├── .github/
│   └── workflows/
│       └── deploy.yml          # CI/CD workflow
├── netlify/
│   └── functions/              # Netlify serverless functions
├── src/
│   ├── components/             # React components
│   ├── App.tsx                 # Main application component
│   ├── main.tsx                # Application entry point
│   └── index.css               # Global styles
├── dist/                       # Build output (generated)
├── index.html                  # HTML template
├── netlify.toml                # Netlify configuration
├── package.json                # Dependencies and scripts
├── tsconfig.json               # TypeScript configuration
├── vite.config.ts              # Vite configuration
└── README.md                   # This file
```

## 🛠️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run build:analyze` - Build with bundle analyzer
- `npm run preview` - Preview production build locally
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint errors automatically
- `npm run type-check` - Run TypeScript type checking

## 🔧 Configuration Files

### Netlify Configuration (`netlify.toml`)

The project includes optimized Netlify configuration with:
- Security headers (CSP, X-Frame-Options, etc.)
- Caching strategies for optimal performance
- Build commands and output directory
- Serverless functions configuration

### TypeScript Configuration (`tsconfig.json`)

Configured for React with strict type checking and modern JavaScript features.

### Vite Configuration (`vite.config.ts`)

Optimized build settings with:
- React Fast Refresh
- Chunk splitting for better caching
- Production optimizations

## 📝 Documentation

For more detailed information, see:

### Getting Started
- [README.md](./README.md) - This file (quick start and overview)
- [scripts/quickstart.sh](./scripts/quickstart.sh) - Automated setup script

### Build & Deploy
- [BUILD_GUIDE.md](./BUILD_GUIDE.md) - Detailed build instructions and optimization
- [DEPLOYMENT.md](./DEPLOYMENT.md) - Comprehensive deployment guide
- [SECRETS_SETUP.md](./SECRETS_SETUP.md) - Step-by-step guide for GitHub secrets
- [PUBLISH_SUMMARY.md](./PUBLISH_SUMMARY.md) - Complete build and publish overview

### Development
- [.github/CICD.md](./.github/CICD.md) - CI/CD pipeline documentation
- [.env.example](./.env.example) - Environment variables example
- [IMPROVEMENTS_SUMMARY.md](./IMPROVEMENTS_SUMMARY.md) - Performance improvements
- [PERFORMANCE_ANALYSIS.md](./PERFORMANCE_ANALYSIS.md) - Performance analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [GitHub Repository](https://github.com/Longjon007/CoinScribe)
- [Netlify Documentation](https://docs.netlify.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
