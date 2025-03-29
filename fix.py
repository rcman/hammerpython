import sys
import os

def validate_vmf(filename):
    """
    Validates a VMF file for common syntax errors
    """
    print(f"Validating VMF file: {filename}")
    
    try:
        if not os.path.exists(filename):
            print(f"Error: File {filename} does not exist.")
            return False
            
        with open(filename, 'r') as f:
            content = f.read()
            
        # Check file size
        file_size = os.path.getsize(filename)
        print(f"File size: {file_size} bytes")
        
        if file_size < 100:
            print("Warning: File size is suspiciously small!")
            
        # Check for balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        print(f"Open braces: {open_braces}, Close braces: {close_braces}")
        
        if open_braces != close_braces:
            print(f"ERROR: Unbalanced braces! Open: {open_braces}, Close: {close_braces}")
            return False
            
        # Check for essential VMF sections
        required_sections = ["versioninfo", "world", "cameras", "cordon"]
        missing_sections = []
        
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)
                
        if missing_sections:
            print(f"ERROR: Missing required sections: {', '.join(missing_sections)}")
            return False
            
        # Check for worldspawn entity
        if '"classname" "worldspawn"' not in content:
            print("ERROR: No worldspawn entity found!")
            return False
            
        # Check file ending
        if not content.strip().endswith('}'):
            print("ERROR: File does not end with a closing brace!")
            return False
            
        print("VMF file validation PASSED!")
        return True
        
    except Exception as e:
        print(f"Error validating VMF file: {e}")
        return False
        
def fix_common_issues(input_file, output_file):
    """
    Attempts to fix common VMF syntax issues
    """
    print(f"Attempting to fix issues in {input_file}")
    
    try:
        with open(input_file, 'r') as f:
            content = f.read()
            
        # Ensure all sections are properly closed
        open_braces = content.count('{')
        close_braces = content.count('}')
        
        if open_braces > close_braces:
            # Add missing closing braces
            content += '\n' + ('}' * (open_braces - close_braces))
            print(f"Added {open_braces - close_braces} missing closing braces")
            
        # Ensure file ends with proper structure
        if not content.strip().endswith('}'):
            content += '\n}'
            print("Added missing final brace")
            
        # Write fixed content
        with open(output_file, 'w') as f:
            f.write(content)
            
        print(f"Fixes applied and saved to {output_file}")
        return True
        
    except Exception as e:
        print(f"Error fixing VMF file: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python vmf_debug.py <vmf_file> [output_file]")
        sys.exit(1)
        
    input_file = sys.argv[1]
    
    if not validate_vmf(input_file):
        if len(sys.argv) >= 3:
            output_file = sys.argv[2]
            fix_common_issues(input_file, output_file)
            validate_vmf(output_file)
        else:
            print("Specify an output file to attempt fixing issues.")
    else:
        print("No fixes needed.")