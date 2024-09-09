import subprocess
import tempfile
import os
from llm import generate_llm_response
from logger import get_logger
logger = get_logger(__name__)

def run_code(code):
    # Get the current working directory
    current_dir = os.getcwd()
    output = None
    # Create a temporary file in the current directory
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=current_dir) as temp_file:
        temp_file.write(code)
        temp_file_path = temp_file.name
    
    try:
        # Run the code in a separate process in the current directory
        result = subprocess.run(['python3.9', os.path.basename(temp_file_path)],
                                capture_output=True,
                                text=True,
                                timeout=90,  # 30 second timeout
                                cwd=current_dir)  # Set the current working directory
        
        # Check if the code executed successfully
        if result.returncode == 0:
            output = result.stdout
        
    except subprocess.TimeoutExpired:
        logger.error("Code execution timed out.")
    
    except Exception as e:
        logger.error(f"An error occurred while running the code: {e}")
    
    finally:
        # Clean up the temporary file
        os.unlink(temp_file_path)

    return output