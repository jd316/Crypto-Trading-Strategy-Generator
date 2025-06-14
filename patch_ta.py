import os
import re

def patch_squeeze_pro():
    """
    Patch the pandas_ta squeeze_pro.py file to fix the NaN import issue
    """
    try:
        # Path to the problematic file
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "venv", "Lib", "site-packages", 
                                "pandas_ta", "momentum", "squeeze_pro.py")
        
        print(f"Attempting to patch file at: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return False
            
        print(f"File found. Reading content...")
        
        # Read the file
        with open(file_path, 'r') as file:
            content = file.read()
        
        print(f"File content read ({len(content)} characters)")
        
        # Check if the problematic line exists
        if 'from numpy import NaN as npNaN' in content:
            print(f"Found problematic import 'from numpy import NaN as npNaN'")
            
            # Replace 'from numpy import NaN as npNaN' with 'from numpy import nan as npNaN'
            patched_content = content.replace('from numpy import NaN as npNaN', 'from numpy import nan as npNaN')
            
            # Write the patched content back
            with open(file_path, 'w') as file:
                file.write(patched_content)
            
            print(f"Successfully patched {file_path}")
            return True
        else:
            print(f"Problematic import not found in file. File content (first 100 chars): {content[:100]}")
            return False
            
    except Exception as e:
        print(f"Error patching file: {e}")
        return False

if __name__ == "__main__":
    successful = patch_squeeze_pro()
    print(f"Patch completed: {'Successfully' if successful else 'Failed'}") 