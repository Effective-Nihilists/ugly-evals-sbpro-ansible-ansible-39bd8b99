#!/usr/bin/env python
"""
Script to reproduce the async_wrapper issues mentioned in the ticket.
The ticket states that async_wrapper produces inconsistent information across exit paths.
"""

import os
import sys
import tempfile
import json
import subprocess

# Add the lib directory to path so we can import ansible modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from ansible.modules import async_wrapper

def test_fork_failure():
    """Test what happens when fork fails"""
    print("Testing fork failure scenario...")
    
    # Create a temporary directory for job output
    workdir = tempfile.mkdtemp()
    job_path = os.path.join(workdir, 'test_job')
    
    # Mock a command that will fail
    cmd = "/nonexistent/command"
    jid = "test.12345"
    
    try:
        # This should trigger the fork failure path
        result = async_wrapper._run_module(cmd, jid, job_path)
        print("Result:", result)
        
        # Check if job file was created
        if os.path.exists(job_path):
            with open(job_path, 'r') as f:
                job_content = f.read()
                print("Job file content:", job_content)
                try:
                    job_json = json.loads(job_content)
                    print("Job JSON:", json.dumps(job_json, indent=2))
                except json.JSONDecodeError as e:
                    print("Failed to parse job file as JSON:", e)
        else:
            print("Job file was not created")
            
    except Exception as e:
        print("Exception occurred:", e)
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)

def test_module_execution_failure():
    """Test what happens when module execution fails"""
    print("\nTesting module execution failure...")
    
    # Create a temporary directory
    workdir = tempfile.mkdtemp()
    
    # Create a failing module
    module_lines = [
        '#!/usr/bin/python',
        'import sys',
        'sys.exit(1)'
    ]
    module_data = '\n'.join(module_lines) + '\n'
    
    # Write module to temp file
    fh, fn = tempfile.mkstemp(dir=workdir, suffix='.py')
    with open(fn, 'w') as f:
        f.write(module_data)
    os.close(fh)
    os.chmod(fn, 0o755)
    
    job_path = os.path.join(workdir, 'test_job')
    jid = "test.67890"
    
    try:
        result = async_wrapper._run_module(fn, jid, job_path)
        print("Result:", result)
        
        # Check job file
        if os.path.exists(job_path):
            with open(job_path, 'r') as f:
                job_content = f.read()
                print("Job file content:", job_content)
                try:
                    job_json = json.loads(job_content)
                    print("Job JSON:", json.dumps(job_json, indent=2))
                except json.JSONDecodeError as e:
                    print("Failed to parse job file as JSON:", e)
        else:
            print("Job file was not created")
            
    except Exception as e:
        print("Exception occurred:", e)
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)

if __name__ == '__main__':
    test_fork_failure()
    test_module_execution_failure()