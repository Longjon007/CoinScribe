# Debugging CoinScribe

This document explains how to debug the CoinScribe application during development.

> **Note**: This debug configuration is ready for use once the application source code is merged from the development branches. The configuration supports React + TypeScript + Vite applications.

## Prerequisites

- Node.js 18.0.0 or higher
- VS Code (recommended) or another IDE with debugging support
- Chrome or Edge browser (for frontend debugging)
- The application source code (merge from `copilot/build-and-publish-coinscribe` or similar branches)

## Quick Start

### Option 1: Using VS Code (Recommended)

1. Open the project in VS Code
2. Press `F5` or go to Run > Start Debugging
3. Select "Debug CoinScribe in Chrome" or "Debug CoinScribe in Edge"
4. VS Code will automatically start the development server and open your browser
5. Set breakpoints in your code and they will be hit when the code executes

### Option 2: Manual Debugging

1. Start the development server:
   ```bash
   npm run dev
   ```

2. Open your browser's developer tools (F12)
3. Navigate to http://localhost:5173
4. Use the browser's built-in debugging tools

## Available Debug Configurations

### Debug CoinScribe in Chrome
Launches the React application in Chrome with full debugging support. This is the recommended configuration for frontend development.

### Debug CoinScribe in Edge
Same as Chrome but uses Microsoft Edge browser.

### Debug Netlify Functions (requires netlify-cli)
Launches Netlify Functions in debug mode using the Netlify CLI, allowing you to debug serverless function code. 

**Prerequisites**: Install Netlify CLI if you plan to debug Netlify Functions:
```bash
npm install -g netlify-cli
```

### Debug Full Stack (requires netlify-cli)
A compound configuration that launches both the frontend and Netlify Functions simultaneously, perfect for full-stack debugging. Requires Netlify CLI to be installed.

## Development Scripts

- `npm run dev` - Start the Vite development server (default port: 5173)
- `npm run preview` - Preview the production build locally
- `npm run lint` - Run ESLint to check code quality
- `npm run lint:fix` - Automatically fix ESLint issues
- `npm run type-check` - Run TypeScript type checking without emitting files

## Debugging Tips

### Frontend Debugging

1. **Source Maps**: Source maps are automatically enabled in development mode, allowing you to debug TypeScript code directly in the browser.

2. **React DevTools**: Install the React Developer Tools browser extension for enhanced React component debugging.

3. **Hot Module Replacement (HMR)**: Vite's HMR allows you to see changes instantly without full page reloads. This preserves your application state during development.

4. **Console Logging**: Use `console.log()`, `console.error()`, and `console.warn()` for quick debugging. Remember to remove or comment them out before committing.

### Backend Debugging

1. **Netlify Functions**: When debugging serverless functions, use the "Debug Netlify Functions" configuration which runs `netlify dev`. Make sure you have the Netlify CLI installed:
   ```bash
   npm install -g netlify-cli
   ```

2. **Environment Variables**: Check that all required environment variables are set in your `.env` file or in the Netlify dashboard.

### Common Issues

#### Port Already in Use
If port 5173 is already in use, Vite will automatically try the next available port. Check the terminal output for the actual port.

#### Source Maps Not Working
Make sure:
- You're running in development mode (`npm run dev`)
- Your browser's developer tools are set to enable source maps
- You're using a recent version of your browser

#### Breakpoints Not Hitting
- Verify that the source path in your launch configuration matches your project structure
- Make sure you're setting breakpoints in TypeScript files, not compiled JavaScript
- Try restarting the debug session

## Advanced Debugging

### Performance Profiling
Use your browser's Performance tab to record and analyze application performance.

### Network Analysis
Monitor API calls and responses in the Network tab of your browser's developer tools.

### Memory Leaks
Use the Memory tab to take heap snapshots and identify memory leaks.

## Additional Resources

- [Vite Documentation](https://vitejs.dev/)
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [VS Code Debugging](https://code.visualstudio.com/docs/editor/debugging)
- [Chrome DevTools](https://developer.chrome.com/docs/devtools/)
