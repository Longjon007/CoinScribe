# CoinScribe Build Guide

This guide provides detailed information about building, testing, and validating the CoinScribe application.

## Build Process Overview

CoinScribe uses [Vite](https://vitejs.dev/) as its build tool, which provides:
- ⚡️ Lightning fast Hot Module Replacement (HMR)
- 📦 Optimized production builds
- 🔧 Easy configuration
- 🎯 TypeScript support out of the box

## System Requirements

- **Node.js**: >= 18.0.0
- **npm**: >= 9.0.0 (comes with Node.js)
- **RAM**: Minimum 2GB available
- **Disk Space**: ~500MB for dependencies

## Build Dependencies

### Production Dependencies
- `react` (^18.3.1) - React library
- `react-dom` (^18.3.1) - React DOM rendering
- `recharts` (^2.15.4) - Charting library
- `@netlify/neon` (^0.1.0) - Netlify database integration

### Development Dependencies
- `vite` (^5.4.21) - Build tool
- `typescript` (~5.9.3) - TypeScript compiler
- `eslint` (^9.15.0) - Linting
- `@vitejs/plugin-react` (^4.3.4) - React plugin for Vite

## Build Commands

### Install Dependencies

```bash
# Clean install (recommended for CI/CD)
npm ci

# Regular install (for development)
npm install
```

**Difference:**
- `npm ci` - Uses exact versions from `package-lock.json`, removes `node_modules` first
- `npm install` - Installs latest compatible versions, updates `package-lock.json`

### Development Build

```bash
npm run dev
```

**What it does:**
- Starts Vite development server on port 5173
- Enables Hot Module Replacement (HMR)
- Provides instant feedback on code changes
- Uses fast refresh for React components
- Serves source maps for easy debugging

**Output:**
```
VITE v5.4.21  ready in X ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### Production Build

```bash
npm run build
```

**What it does:**
1. **Type Checking**: Runs TypeScript compiler to check for type errors
2. **Transpilation**: Converts TypeScript to JavaScript
3. **Bundling**: Combines all modules into optimized bundles
4. **Minification**: Reduces file sizes
5. **Tree Shaking**: Removes unused code
6. **Code Splitting**: Splits code into vendor and app chunks
7. **Asset Optimization**: Optimizes images, CSS, and other assets
8. **Source Maps**: Generates source maps for debugging

**Output:**
```
vite v5.4.21 building for production...
transforming...
✓ 34 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                         1.14 kB │ gzip:  0.56 kB
dist/assets/index-B5PQ3PoQ.css          2.88 kB │ gzip:  1.09 kB
dist/assets/chart-vendor-ap62UwsT.js    0.04 kB │ gzip:  0.06 kB
dist/assets/index-D84AKtTh.js           5.37 kB │ gzip:  2.43 kB
dist/assets/react-vendor-DbiWhUg4.js  141.07 kB │ gzip: 45.29 kB
✓ built in 1.79s
```

**Build Output Structure:**
```
dist/
├── index.html                    # Entry HTML file
├── assets/
│   ├── index-[hash].css         # Application styles
│   ├── index-[hash].js          # Application code
│   ├── react-vendor-[hash].js   # React libraries
│   └── chart-vendor-[hash].js   # Chart libraries
└── [other assets]               # Images, fonts, etc.
```

### Build with Bundle Analysis

```bash
npm run build:analyze
```

This generates a visual representation of bundle sizes to help identify optimization opportunities.

### Preview Production Build

```bash
npm run preview
```

**What it does:**
- Starts a local server to preview the production build
- Serves files from the `dist/` directory
- Useful for testing before deployment

**Output:**
```
  ➜  Local:   http://localhost:4173/
  ➜  Network: use --host to expose
```

## Code Quality Commands

### Linting

```bash
# Check for linting errors
npm run lint

# Auto-fix linting errors
npm run lint:fix
```

**What it checks:**
- Code style consistency
- Potential bugs and errors
- React best practices
- TypeScript usage
- Unused variables and imports
- Accessibility issues

**ESLint Configuration:**
- Extends `@eslint/js` recommended config
- React plugin with hooks rules
- TypeScript ESLint parser
- React Refresh plugin

### Type Checking

```bash
npm run type-check
```

**What it checks:**
- TypeScript type errors
- Type mismatches
- Missing types
- Type inference issues

**TypeScript Configuration:**
- Target: ES2020
- Module: ESNext
- Strict mode enabled
- JSX: react-jsx
- Source maps enabled

## Build Optimization

### Current Optimizations

1. **Code Splitting**
   - Vendor chunks separated from app code
   - Chart library in separate chunk
   - React libraries bundled separately

2. **Minification**
   - JavaScript minified with Terser
   - CSS minified
   - HTML minified

3. **Tree Shaking**
   - Removes unused code
   - Optimizes bundle size

4. **Asset Optimization**
   - Images optimized
   - CSS optimized
   - Fonts optimized

### Build Size Guidelines

| File Type | Target Size | Current Size |
|-----------|-------------|--------------|
| HTML | < 2 KB | 1.14 KB ✅ |
| CSS | < 10 KB | 2.88 KB ✅ |
| App JS | < 20 KB | 5.37 KB ✅ |
| Vendor JS | < 150 KB | 141.07 KB ✅ |
| Total (gzipped) | < 60 KB | ~49 KB ✅ |

### Improving Build Performance

If builds are slow, try:

1. **Clear cache:**
```bash
rm -rf node_modules/.vite
```

2. **Update dependencies:**
```bash
npm update
```

3. **Use more workers:**
```bash
# Modify vite.config.ts
build: {
  rollupOptions: {
    maxParallelFileReads: 20
  }
}
```

## Build Validation

### Pre-Build Checklist

- [ ] All dependencies installed (`npm ci`)
- [ ] No TypeScript errors (`npm run type-check`)
- [ ] No linting errors (`npm run lint`)
- [ ] No security vulnerabilities (`npm audit --production`)
- [ ] All tests passing (if tests exist)

### Post-Build Validation

After running `npm run build`, verify:

1. **Build Success:**
   ```bash
   # Should exit with code 0
   echo $?
   ```

2. **Output Files Exist:**
   ```bash
   ls -lh dist/
   # Should show index.html and assets directory
   ```

3. **File Sizes Reasonable:**
   ```bash
   du -sh dist/
   # Should be < 1 MB total
   ```

4. **Preview Works:**
   ```bash
   npm run preview
   # Open http://localhost:4173 and test functionality
   ```

## Continuous Integration (CI) Build

### GitHub Actions Build Process

The CI/CD pipeline (`.github/workflows/deploy.yml`) runs:

1. **Setup**
   - Checkout code
   - Setup Node.js 18
   - Cache npm dependencies

2. **Install**
   ```bash
   npm ci
   ```

3. **Quality Checks**
   ```bash
   npm run lint
   npm run type-check
   ```

4. **Build**
   ```bash
   npm run build
   ```

5. **Upload Artifacts**
   - Uploads `dist/` directory
   - Retained for 7 days
   - Used for deployment

### Build Time Expectations

| Environment | Expected Time |
|-------------|---------------|
| Local (first build) | ~10s |
| Local (cached) | ~2s |
| CI/CD (with cache) | ~30s |
| CI/CD (no cache) | ~60s |

## Troubleshooting Build Issues

### Issue: "Out of memory"

**Solution:**
```bash
# Increase Node.js memory limit
export NODE_OPTIONS="--max-old-space-size=4096"
npm run build
```

### Issue: "Module not found"

**Solution:**
```bash
# Clear and reinstall dependencies
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Issue: "TypeScript errors"

**Solution:**
```bash
# Check for type errors
npm run type-check

# Fix type errors in code
# Common fixes:
# - Add proper types to variables
# - Import missing type definitions
# - Fix type mismatches
```

### Issue: "Vite config error"

**Solution:**
```bash
# Check vite.config.ts syntax
# Ensure all imports are correct
# Verify plugin configurations
```

### Issue: "Build succeeds but app doesn't work"

**Solution:**
1. Check browser console for errors
2. Verify environment variables are set
3. Check network requests for failed API calls
4. Ensure base path is correct in production

## Build Configuration Files

### vite.config.ts

Key configurations:
```typescript
export default defineConfig({
  plugins: [react()],
  build: {
    target: 'esnext',
    minify: 'terser',
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'chart-vendor': ['recharts']
        }
      }
    }
  }
})
```

### tsconfig.json

Key configurations:
```json
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "strict": true,
    "jsx": "react-jsx"
  }
}
```

### package.json Scripts

```json
{
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx",
    "type-check": "tsc --noEmit"
  }
}
```

## Performance Metrics

### Build Performance

| Metric | Target | Current |
|--------|--------|---------|
| Build Time | < 5s | 1.79s ✅ |
| Modules | < 100 | 34 ✅ |
| Chunks | 3-5 | 5 ✅ |
| Bundle Size | < 200KB | 149KB ✅ |

### Runtime Performance

Target Lighthouse scores:
- Performance: > 90
- Accessibility: > 90
- Best Practices: > 90
- SEO: > 90

## Additional Resources

- [Vite Documentation](https://vitejs.dev/)
- [Vite Build Optimizations](https://vitejs.dev/guide/build.html)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [ESLint Documentation](https://eslint.org/docs/latest/)
- [React Production Build](https://react.dev/learn/start-a-new-react-project#building-for-production)

## Maintenance

### Updating Dependencies

```bash
# Check for updates
npm outdated

# Update all dependencies (carefully)
npm update

# Update specific package
npm update package-name

# After updates, always test:
npm run lint
npm run type-check
npm run build
npm run preview
```

### Keeping Build Fast

1. Regularly clean cache: `rm -rf node_modules/.vite`
2. Keep dependencies updated
3. Monitor bundle sizes
4. Use code splitting appropriately
5. Lazy load large components when possible

---

For deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md).
