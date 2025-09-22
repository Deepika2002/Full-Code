#!/usr/bin/env python3
"""
Start all ImpactAnalyzer microservices
"""

import os
import sys
import subprocess
import time
import signal
from multiprocessing import Process

def start_service(service_name, port):
    """Start a single microservice"""
    print(f"Starting {service_name} on port {port}...")
    
    service_dir = f"ms_{service_name.lower().replace('-', '_')}"
    app_file = os.path.join(service_dir, "app.py")
    
    if not os.path.exists(app_file):
        print(f"❌ Service file not found: {app_file}")
        return
    
    try:
        # Change to service directory and start
        os.chdir(service_dir)
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", str(port),
            "--reload"
        ])
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping {service_name}...")
    except Exception as e:
        print(f"❌ Error starting {service_name}: {e}")
    finally:
        os.chdir("..")

def main():
    """Main function to start all services"""
    print("🚀 Starting ImpactAnalyzer Backend Services")
    print("=" * 50)
    
    # Change to backend directory
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(backend_dir)
    
    # Service configuration
    services = [
        ("index", 8001),
        ("mr", 8002), 
        ("common", 8003),
        ("ai", 8004)
    ]
    
    processes = []
    
    try:
        # Start each service in a separate process
        for service_name, port in services:
            process = Process(target=start_service, args=(service_name, port))
            process.start()
            processes.append(process)
            time.sleep(2)  # Stagger startup
        
        print("\n✅ All services started successfully!")
        print("\nService URLs:")
        for service_name, port in services:
            print(f"  MS-{service_name.upper()}: http://localhost:{port}")
        
        print("\nPress Ctrl+C to stop all services...")
        
        # Wait for all processes
        for process in processes:
            process.join()
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping all services...")
        
        # Terminate all processes
        for process in processes:
            if process.is_alive():
                process.terminate()
                process.join(timeout=5)
                if process.is_alive():
                    process.kill()
        
        print("✅ All services stopped")

if __name__ == "__main__":
    main()