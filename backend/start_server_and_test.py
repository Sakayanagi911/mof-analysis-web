#!/usr/bin/env python3
"""
Start backend server and test API
"""

import subprocess
import time
import requests
import threading
import sys

def start_server():
    """Start the FastAPI server"""
    try:
        subprocess.run([sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"], 
                      cwd=".", check=True)
    except KeyboardInterrupt:
        print("Server stopped")

def test_api():
    """Test the API after server starts"""
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Test if server is running
    try:
        response = requests.get("http://127.0.0.1:8000/")
        if response.status_code == 200:
            print("✅ Server is running")
            
            # Run the test
            from test_api_case1 import test_api_case1
            test_api_case1()
        else:
            print("❌ Server not responding properly")
    except Exception as e:
        print(f"❌ Cannot connect to server: {e}")

if __name__ == "__main__":
    print("=== STARTING BACKEND SERVER ===")
    
    # Start server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Test API
    test_api()
    
    print("\nPress Ctrl+C to stop server")