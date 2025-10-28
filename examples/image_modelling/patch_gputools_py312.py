"""
Patch gputools to work with Python 3.12+

SafeConfigParser was removed in Python 3.12, but it's just an alias for ConfigParser.
This script patches the gputools package to use ConfigParser instead.

Run this on Google Colab BEFORE importing biobeam:
    !python patch_gputools_py312.py
"""

import os
import sys

def find_gputools_config_file():
    """Find the myconfigparser.py file in the installed gputools package."""
    try:
        import gputools
        gputools_path = os.path.dirname(gputools.__file__)
        config_file = os.path.join(gputools_path, 'config', 'myconfigparser.py')
        
        if os.path.exists(config_file):
            return config_file
        else:
            print(f"Error: Could not find {config_file}")
            return None
    except ImportError:
        print("Error: gputools is not installed")
        return None

def patch_configparser(config_file):
    """Patch the file to use ConfigParser instead of SafeConfigParser."""
    
    print(f"Patching {config_file}...")
    
    # Read the file
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Check if already patched
    if 'ConfigParser as SafeConfigParser' in content:
        print("✓ Already patched!")
        return True
    
    # Make the replacement
    old_import = 'from configparser import SafeConfigParser'
    new_import = 'from configparser import ConfigParser as SafeConfigParser'
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        
        # Write back
        with open(config_file, 'w') as f:
            f.write(content)
        
        print("✓ Successfully patched!")
        print(f"  Changed: {old_import}")
        print(f"  To:      {new_import}")
        return True
    else:
        print("✗ Could not find the import statement to patch")
        return False

def main():
    print("=" * 60)
    print("Patching gputools for Python 3.12+ compatibility")
    print("=" * 60)
    print(f"Python version: {sys.version}")
    print()
    
    config_file = find_gputools_config_file()
    
    if config_file:
        success = patch_configparser(config_file)
        if success:
            print()
            print("You can now import biobeam without errors!")
            print()
            print("Test with:")
            print("  from biobeam import SimLSM_Cylindrical")
        else:
            print()
            print("Patching failed. You may need to do it manually.")
            print(f"Edit: {config_file}")
            print("Change line 13 from:")
            print("  from configparser import SafeConfigParser")
            print("To:")
            print("  from configparser import ConfigParser as SafeConfigParser")
    else:
        print("Could not locate gputools installation")

if __name__ == "__main__":
    main()
