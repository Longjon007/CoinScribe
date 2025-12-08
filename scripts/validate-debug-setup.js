#!/usr/bin/env node

/**
 * Validation script to check if the debugging setup is correctly configured.
 * Run this script with: node scripts/validate-debug-setup.js
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Validating CoinScribe Debug Setup...\n');

let hasErrors = false;

// Check for required files
const requiredFiles = [
  { path: '.vscode/launch.json', description: 'VS Code debug configurations' },
  { path: '.vscode/tasks.json', description: 'VS Code tasks' },
  { path: '.vscode/extensions.json', description: 'VS Code extension recommendations' },
  { path: 'DEBUG.md', description: 'Debug documentation' },
  { path: '.gitignore', description: 'Git ignore file' }
];

console.log('📁 Checking for required files:');
requiredFiles.forEach(({ path: filePath, description }) => {
  if (fs.existsSync(filePath)) {
    console.log(`  ✓ ${filePath} - ${description}`);
  } else {
    console.log(`  ✗ ${filePath} - ${description} (MISSING)`);
    hasErrors = true;
  }
});

// Validate JSON files
console.log('\n📝 Validating JSON configuration files:');
const jsonFiles = ['.vscode/launch.json', '.vscode/tasks.json', '.vscode/extensions.json'];

jsonFiles.forEach(filePath => {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    JSON.parse(content);
    console.log(`  ✓ ${filePath} - Valid JSON`);
  } catch (error) {
    console.log(`  ✗ ${filePath} - Invalid JSON: ${error.message}`);
    hasErrors = true;
  }
});

// Check launch configurations
console.log('\n🚀 Checking debug configurations:');
try {
  const launchConfig = JSON.parse(fs.readFileSync('.vscode/launch.json', 'utf8'));
  
  if (launchConfig.configurations && Array.isArray(launchConfig.configurations)) {
    const configNames = launchConfig.configurations.map(c => c.name);
    console.log(`  ✓ Found ${configNames.length} debug configuration(s):`);
    configNames.forEach(name => console.log(`    - ${name}`));
  } else {
    console.log('  ✗ No debug configurations found');
    hasErrors = true;
  }
} catch (error) {
  console.log(`  ✗ Error reading launch.json: ${error.message}`);
  hasErrors = true;
}

// Check for package.json (optional - will exist when app code is added)
console.log('\n📦 Checking for application files:');
if (fs.existsSync('package.json')) {
  console.log('  ✓ package.json found - Application is set up');
  
  try {
    const packageJson = JSON.parse(fs.readFileSync('package.json', 'utf8'));
    if (packageJson.scripts && packageJson.scripts.dev) {
      console.log('  ✓ "dev" script found in package.json');
    } else {
      console.log('  ⚠ "dev" script not found in package.json (needed for debugging)');
    }
  } catch (error) {
    console.log(`  ⚠ Error reading package.json: ${error.message}`);
  }
} else {
  console.log('  ℹ package.json not found - Application code not yet merged');
  console.log('    Debug setup will be ready once app code is added');
}

// Final summary
console.log('\n' + '='.repeat(50));
if (hasErrors) {
  console.log('❌ Validation FAILED - Please fix the errors above');
  process.exit(1);
} else {
  console.log('✅ Debug setup validation PASSED!');
  console.log('\nYou can now:');
  console.log('  1. Open the project in VS Code');
  console.log('  2. Press F5 to start debugging');
  console.log('  3. Read DEBUG.md for detailed instructions');
  process.exit(0);
}
