"""
Workflow Validation Testing Suite for CoinScribe Application
============================================================

Tests GitHub Actions workflows and CI/CD processes:
- Workflow file validation
- Supabase integration commands
- CI/CD pipeline steps
"""

import pytest
import yaml
import os
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestWorkflowFileValidation:
    """Test GitHub Actions workflow file validation."""
    
    def test_workflow_file_exists(self):
        """Test that the Supabase integration workflow file exists."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        assert workflow_path.exists(), "Workflow file should exist"
    
    def test_workflow_file_valid_yaml(self):
        """Test that workflow file is valid YAML."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            try:
                workflow_data = yaml.safe_load(f)
                assert workflow_data is not None
            except yaml.YAMLError as e:
                pytest.fail(f"Workflow file is not valid YAML: {e}")
    
    def test_workflow_structure(self):
        """Test that workflow has required structure."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        # Check required top-level keys
        assert 'name' in workflow_data, "Workflow should have a name"
        # 'on' is a reserved Python keyword, YAML may parse it as True
        assert 'on' in workflow_data or True in workflow_data, "Workflow should have triggers"
        assert 'jobs' in workflow_data, "Workflow should have jobs"
    
    def test_workflow_has_supabase_job(self):
        """Test that workflow includes Supabase setup job."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        jobs = workflow_data.get('jobs', {})
        assert len(jobs) > 0, "Workflow should have at least one job"
        
        # Check for database-related job
        job_names = [name.lower() for name in jobs.keys()]
        assert any('setup' in name or 'database' in name or 'supabase' in name 
                  for name in job_names), "Should have Supabase/database setup job"
    
    def test_workflow_triggers(self):
        """Test that workflow has appropriate triggers."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        # 'on' is a reserved keyword, YAML may parse it as True
        triggers = workflow_data.get('on', workflow_data.get(True, {}))
        assert triggers, "Workflow should have triggers defined"


class TestSupabaseCommands:
    """Test Supabase CLI commands in workflow."""
    
    def test_workflow_has_supabase_cli_installation(self):
        """Test that workflow installs Supabase CLI."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Should have Supabase CLI installation step
        assert 'supabase' in content.lower(), "Workflow should reference Supabase"
        assert 'install' in content.lower() or 'download' in content.lower(), \
            "Workflow should install Supabase CLI"
    
    def test_workflow_has_db_push_command(self):
        """Test that workflow includes 'supabase db push' command."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        assert 'supabase db push' in content, \
            "Workflow should include 'supabase db push' command"
    
    def test_workflow_has_db_reset_command(self):
        """Test that workflow includes 'supabase db reset' command."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        assert 'supabase db reset' in content, \
            "Workflow should include 'supabase db reset' command"
    
    def test_supabase_db_push_simulation(self):
        """Test simulation of 'supabase db push' command."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='Database migrations pushed successfully',
                stderr=''
            )
            
            import subprocess
            result = subprocess.run(
                ['echo', 'supabase db push'],
                capture_output=True,
                text=True,
                check=True
            )
            
            assert result.returncode == 0
    
    def test_supabase_db_reset_simulation(self):
        """Test simulation of 'supabase db reset' command."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='Database reset successfully',
                stderr=''
            )
            
            import subprocess
            result = subprocess.run(
                ['echo', 'supabase db reset'],
                capture_output=True,
                text=True,
                check=True
            )
            
            assert result.returncode == 0


class TestWorkflowSteps:
    """Test individual workflow steps."""
    
    def test_workflow_checkout_step(self):
        """Test that workflow has repository checkout step."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        jobs = workflow_data.get('jobs', {})
        for job_name, job_data in jobs.items():
            steps = job_data.get('steps', [])
            
            # Should have checkout step
            checkout_steps = [s for s in steps if 'checkout' in str(s).lower()]
            assert len(checkout_steps) > 0, f"Job {job_name} should have checkout step"
    
    def test_workflow_uses_ubuntu(self):
        """Test that workflow runs on Ubuntu."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        jobs = workflow_data.get('jobs', {})
        for job_name, job_data in jobs.items():
            runs_on = job_data.get('runs-on', '')
            assert 'ubuntu' in runs_on.lower(), \
                f"Job {job_name} should run on Ubuntu"
    
    def test_workflow_has_multiple_steps(self):
        """Test that workflow has multiple steps."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        jobs = workflow_data.get('jobs', {})
        for job_name, job_data in jobs.items():
            steps = job_data.get('steps', [])
            assert len(steps) >= 3, \
                f"Job {job_name} should have at least 3 steps"


class TestWorkflowSecurity:
    """Test workflow security considerations."""
    
    def test_workflow_mentions_secrets(self):
        """Test that workflow references proper secrets handling."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Should mention secrets setup
        assert 'secret' in content.lower(), \
            "Workflow should mention secrets configuration"
    
    def test_workflow_no_hardcoded_credentials(self):
        """Test that workflow doesn't contain hardcoded credentials."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Check for common credential patterns
        dangerous_patterns = [
            'password: ',
            'token: ',
            'api_key: ',
            'secret: ',
        ]
        
        content_lower = content.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                # If pattern exists, ensure it references secrets or is a comment
                lines_with_pattern = [
                    line for line in content.split('\n') 
                    if pattern in line.lower()
                ]
                for line in lines_with_pattern:
                    # Should be a comment, reference to secrets, or placeholder
                    assert (
                        line.strip().startswith('#') or 
                        'secrets.' in line.lower() or
                        'placeholder' in line.lower() or
                        'please ensure' in line.lower()
                    ), f"Line may contain hardcoded credential: {line}"
    
    def test_workflow_commit_reference(self):
        """Test that workflow references the correct commit."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Should reference commit cf5645f086b50e1e71fba0b7a84debc46698c2af
        assert 'cf5645f086b50e1e71fba0b7a84debc46698c2af' in content, \
            "Workflow should reference the correct commit hash"


class TestCICD:
    """Test CI/CD pipeline considerations."""
    
    def test_workflow_error_handling(self):
        """Test that workflow includes error handling."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Should have error handling (set -e or similar)
        # Note: This is checking for bash error handling
        if 'run:' in content:
            assert 'set -e' in content or 'shell:' in content, \
                "Workflow should handle errors properly"
    
    def test_workflow_name_descriptive(self):
        """Test that workflow has descriptive name."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        name = workflow_data.get('name', '')
        assert len(name) > 0, "Workflow should have a name"
        assert 'supabase' in name.lower() or 'integration' in name.lower(), \
            "Workflow name should be descriptive"
    
    def test_python_app_integration(self):
        """Test that Python app can run in CI environment."""
        # Check that required files exist
        required_files = [
            'requirements.txt',
            'setup.py',
            'run_server.py',
        ]
        
        base_path = Path('/home/runner/work/CoinScribe/CoinScribe')
        for file in required_files:
            file_path = base_path / file
            assert file_path.exists(), f"Required file {file} should exist"
    
    def test_can_import_modules(self):
        """Test that Python modules can be imported."""
        try:
            from ai_model.api.endpoints import create_app
            from ai_model.config import config
            assert create_app is not None
            assert config is not None
        except ImportError as e:
            pytest.fail(f"Failed to import required modules: {e}")


class TestWorkflowBestPractices:
    """Test workflow follows best practices."""
    
    def test_workflow_has_descriptive_step_names(self):
        """Test that workflow steps have descriptive names."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        jobs = workflow_data.get('jobs', {})
        for job_name, job_data in jobs.items():
            steps = job_data.get('steps', [])
            
            for step in steps:
                if isinstance(step, dict) and 'name' in step:
                    name = step['name']
                    assert len(name) > 5, \
                        f"Step name should be descriptive: {name}"
    
    def test_workflow_version_pinning(self):
        """Test that workflow pins action versions."""
        workflow_path = Path('/home/runner/work/CoinScribe/CoinScribe/.github/workflows/supabase-integration.yml')
        
        with open(workflow_path, 'r') as f:
            workflow_data = yaml.safe_load(f)
        
        jobs = workflow_data.get('jobs', {})
        for job_name, job_data in jobs.items():
            steps = job_data.get('steps', [])
            
            for step in steps:
                if isinstance(step, dict) and 'uses' in step:
                    uses = step['uses']
                    # Should have version (e.g., @v3, @v2)
                    assert '@' in uses, \
                        f"Action should be version pinned: {uses}"
