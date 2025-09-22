#!/usr/bin/env python3
"""
Setup script for ImpactAnalyzer Backend Services
"""

import os
import sys
import subprocess
import mysql.connector
from mysql.connector import Error

def install_requirements():
    """Install requirements for all microservices"""
    services = ['ms_index', 'ms_mr', 'ms_common', 'ms_ai']
    
    for service in services:
        print(f"\n=== Installing requirements for {service} ===")
        req_file = os.path.join(service, 'requirements.txt')
        if os.path.exists(req_file):
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', req_file])
                print(f"✅ Requirements installed for {service}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install requirements for {service}: {e}")
        else:
            print(f"⚠️  Requirements file not found for {service}")

def setup_database():
    """Setup MySQL database"""
    print("\n=== Setting up MySQL Database ===")
    
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'password'  # Change this to your MySQL root password
    }
    
    try:
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS impact_analyzer")
        print("✅ Database 'impact_analyzer' created successfully")
        
        # Create user (optional)
        try:
            cursor.execute("CREATE USER IF NOT EXISTS 'impact_user'@'localhost' IDENTIFIED BY 'impact_pass'")
            cursor.execute("GRANT ALL PRIVILEGES ON impact_analyzer.* TO 'impact_user'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            print("✅ Database user created successfully")
        except Error as e:
            print(f"⚠️  User creation skipped: {e}")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"❌ Error setting up database: {e}")
        print("Please ensure MySQL is running and credentials are correct")

def create_directories():
    """Create necessary directories"""
    print("\n=== Creating directories ===")
    
    directories = [
        'vector_store',
        'temp_repos',
        'logs'
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Directory '{directory}' created")

def create_env_file():
    """Create environment file template"""
    print("\n=== Creating environment file ===")
    
    env_content = """# ImpactAnalyzer Environment Configuration

# Database
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/impact_analyzer

# API Keys
OPENAI_API_KEY=your_openai_api_key_here
IMPACT_ANALYZER_API_KEY=dev-key-123

# Vector Store
VECTOR_STORE_PATH=./vector_store
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Services URLs
MS_INDEX_URL=http://localhost:8001
MS_MR_URL=http://localhost:8002
MS_COMMON_URL=http://localhost:8003
MS_AI_URL=http://localhost:8004

# Git
TEMP_REPO_PATH=./temp_repos

# Logging
LOG_LEVEL=INFO
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Environment file '.env' created")
    print("⚠️  Please update the environment variables as needed")

def main():
    """Main setup function"""
    print("🚀 ImpactAnalyzer Backend Setup")
    print("=" * 50)
    
    # Change to backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Install requirements
    install_requirements()
    
    # Setup database
    setup_database()
    
    # Create directories
    create_directories()
    
    # Create environment file
    create_env_file()
    
    print("\n" + "=" * 50)
    print("✅ Setup completed successfully!")
    print("\nNext steps:")
    print("1. Update the .env file with your actual API keys and database credentials")
    print("2. Start the services using the start scripts:")
    print("   - python ms_index/app.py")
    print("   - python ms_mr/app.py") 
    print("   - python ms_common/app.py")
    print("   - python ms_ai/app.py")
    print("3. Test the services using the provided test scripts")

if __name__ == "__main__":
    main()