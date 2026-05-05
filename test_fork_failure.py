#!/usr/bin/env python
"""Test script to reproduce fork failure issue"""

import os
import sys
import json
import tempfile
import shutil

# Add the lib directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))

from ansible.modules import async_wrapper

def test_fork_failure():
    """Test that fork failures produce JSON output"""
    
    # Create a temporary module
    module_result = {'rc': 0}
    module_lines = [
        '#!/usr/bin/python',
        'import sys',
        'import json',
        'print("%s")' % json.dumps(module_result)
    ]
    module_data = '\n'.join(module_lines) + '\n'
    module_data = module_data.encode('utf-8')
    
    workdir = tempfile.mkdtemp()
    try:
        # Create module file
        module_path = os.path.join(workdir, 'test_module.py')
        with open(module_path, 'wb') as f:
            f.write(module_data)
        
        # Mock os.fork to simulate fork failure
        original_fork = os.fork
        def mock_fork():
            raise OSError("Fork failed")
        
        os.fork = mock_fork
        
        # Capture stdout and stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        
        stdout_capture = []
        stderr_capture = []
        
        class MockStdout:
            def write(self, text):
                stdout_capture.append(text)
            def flush(self):
                pass
                
        class MockStderr:
            def write(self, text):
                stderr_capture.append(text)
            def flush(self):
                pass
        
        sys.stdout = MockStdout()
        sys.stderr = MockStderr()
        
        try:
            # This should trigger a fork failure in the main function
            # We need to simulate the command line arguments
            old_argv = sys.argv
            sys.argv = ['async_wrapper', '12345', '10', module_path, '_']
            
            try:
                async_wrapper.main()
            except SystemExit:
                pass  # Expected
            
            # Check what was output
            stdout_output = ''.join(stdout_capture)
            stderr_output = ''.join(stderr_capture)
            
            print("=== STDOUT ===")
            print(repr(stdout_output))
            print("=== STDERR ===") 
            print(repr(stderr_output))
            
            # Check if output is valid JSON
            try:
                if stdout_output.strip():
                    json.loads(stdout_output.strip())
                    print("✓ STDOUT is valid JSON")
                else:
                    print("✗ STDOUT is empty")
            except json.JSONDecodeError:
                print("✗ STDOUT is NOT valid JSON")
                
        finally:
            sys.argv = old_argv
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            os.fork = original_fork
            
    finally:
        shutil.rmtree(workdir)

if __name__ == '__main__':
    test_fork_failure()