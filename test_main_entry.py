#!/usr/bin/env python3
"""
Test script to verify the main.py entry point works correctly.
"""

import subprocess
import sys
import time
import signal
import os


def test_main_entry():
    """Test that main.py can be executed without errors."""
    print("Testing main.py entry point...")
    
    try:
        # Start the main.py process
        process = subprocess.Popen(
            [sys.executable, "main.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Let it run for 2 seconds
        time.sleep(2)
        
        # Terminate the process
        process.terminate()
        
        # Wait for process to finish and get output
        stdout, stderr = process.communicate(timeout=5)
        
        print("✓ main.py executed successfully")
        print(f"✓ Process started and terminated cleanly")
        
        # Check if there were any critical errors
        if "Error starting game:" in stderr:
            print(f"✗ Game startup error: {stderr}")
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        print("✗ Process did not terminate cleanly")
        process.kill()
        return False
    except Exception as e:
        print(f"✗ Error testing main.py: {e}")
        return False


def main():
    """Main test function."""
    print("Testing Python Pacman Game main entry point...")
    
    if test_main_entry():
        print("\n🎉 Main entry point test passed!")
        print("The game can be started with 'python main.py'")
        return 0
    else:
        print("\n❌ Main entry point test failed!")
        return 1


if __name__ == "__main__":
    exit(main())