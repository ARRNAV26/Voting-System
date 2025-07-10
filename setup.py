#!/usr/bin/env python3
"""
Setup script for the Voting System
This script helps you set up the development environment quickly.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, cwd=None):
    """Run a command and return the result"""
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, capture_output=True, text=True)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_node_version():
    """Check if Node.js is installed"""
    success, output = run_command("node --version")
    if success:
        print(f"✅ Node.js {output.strip()} detected")
        return True
    else:
        print("❌ Node.js is not installed. Please install Node.js 16+")
        return False

def setup_backend():
    """Set up the backend"""
    print("\n🔧 Setting up backend...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    # Create virtual environment
    print("Creating virtual environment...")
    success, output = run_command("python -m venv venv", cwd=backend_dir)
    if not success:
        print(f"❌ Failed to create virtual environment: {output}")
        return False
    
    # Determine activation command based on OS
    if os.name == 'nt':  # Windows
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
    else:  # Unix/Linux/Mac
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
    
    # Install dependencies
    print("Installing Python dependencies...")
    success, output = run_command(f"{pip_cmd} install -r requirements.txt", cwd=backend_dir)
    if not success:
        print(f"❌ Failed to install dependencies: {output}")
        return False
    
    # Create .env file if it doesn't exist
    env_file = backend_dir / ".env"
    env_example = backend_dir / "env.example"
    
    if not env_file.exists() and env_example.exists():
        print("Creating .env file...")
        shutil.copy(env_example, env_file)
        print("✅ Backend setup complete!")
    else:
        print("✅ Backend setup complete!")
    
    return True

def setup_frontend():
    """Set up the frontend"""
    print("\n🔧 Setting up frontend...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Install dependencies
    print("Installing Node.js dependencies...")
    success, output = run_command("npm install", cwd=frontend_dir)
    if not success:
        print(f"❌ Failed to install dependencies: {output}")
        return False
    
    print("✅ Frontend setup complete!")
    return True

def main():
    """Main setup function"""
    print("🚀 Setting up Voting System...")
    
    # Check prerequisites
    if not check_python_version():
        return
    
    if not check_node_version():
        return
    
    # Set up backend
    if not setup_backend():
        return
    
    # Set up frontend
    if not setup_frontend():
        return
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Start the backend:")
    print("   cd backend")
    print("   # On Windows:")
    print("   venv\\Scripts\\activate")
    print("   # On Unix/Linux/Mac:")
    print("   source venv/bin/activate")
    print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("\n2. Start the frontend (in a new terminal):")
    print("   cd frontend")
    print("   npm run dev")
    print("\n3. Open your browser to http://localhost:3000")
    print("\n4. Register a new account and start voting!")

if __name__ == "__main__":
    main() 