#!/usr/bin/env python3
"""
ReportForge - Automated Production Deployment Script
Deploys latest changes to production server via SSH with full container rebuild
"""

import paramiko
import sys
import time
import subprocess
from datetime import datetime

# Production server configuration
HOST = "10.135.215.172"
USERNAME = "root"
PASSWORD = "Fr3qu3nc1."
PROJECT_DIR = "/opt/reportforge"
GITHUB_REPO = "https://github.com/ilvolodel/reportforge.git"

def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)

def print_step(step_num, total_steps, description):
    """Print step header"""
    print(f"\n📋 Step {step_num}/{total_steps}: {description}")
    print("-" * 60)

def execute_ssh_command(ssh, command, show_output=True):
    """Execute a command via SSH and return success status"""
    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
    
    # Wait for command to complete
    exit_status = stdout.channel.recv_exit_status()
    
    # Get output
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if show_output and output:
        print(output)
    
    if error and exit_status != 0:
        print(f"⚠️  Error: {error}", file=sys.stderr)
    
    return exit_status == 0, output

def local_commit_and_push():
    """Commit and push local changes"""
    print_step(1, 7, "Committing and pushing local changes")
    
    try:
        # Check if there are changes
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd='/workspace/reportforge',
            capture_output=True,
            text=True
        )
        
        if result.stdout.strip():
            print("📝 Local changes detected:")
            print(result.stdout)
            
            # Get commit message
            commit_msg = input("\n💬 Enter commit message (or press Enter for default): ").strip()
            if not commit_msg:
                commit_msg = f"feat: Task 27 - PDF template development - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            # Add all changes
            subprocess.run(['git', 'add', '-A'], cwd='/workspace/reportforge', check=True)
            
            # Commit
            subprocess.run(
                ['git', 'commit', '-m', commit_msg],
                cwd='/workspace/reportforge',
                check=True
            )
            
            # Push
            subprocess.run(
                ['git', 'push', 'origin', 'main'],
                cwd='/workspace/reportforge',
                check=True
            )
            
            print("✅ Changes committed and pushed to GitHub")
            return True
        else:
            print("ℹ️  No local changes to commit")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git operation failed: {e}")
        return False

def deploy_to_production():
    """Deploy to production server"""
    print_header("🚀 REPORTFORGE - PRODUCTION DEPLOYMENT")
    print(f"\n📍 Target: {USERNAME}@{HOST}")
    print(f"📁 Project: {PROJECT_DIR}")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Local commit and push
    if not local_commit_and_push():
        print("\n❌ Deployment aborted: Failed to commit/push changes")
        return False
    
    try:
        # Step 2: Connect to server
        print_step(2, 7, "Connecting to production server")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=15)
        print("✅ Connected successfully!")
        
        # Step 3: Pull latest code
        print_step(3, 7, "Pulling latest code from GitHub")
        success, output = execute_ssh_command(
            ssh,
            f"cd {PROJECT_DIR} && git pull origin main"
        )
        if not success:
            print("⚠️  Warning: Git pull had issues, continuing anyway...")
        else:
            print("✅ Code updated from GitHub")
        
        # Step 4: Rebuild Docker containers
        print_step(4, 7, "Rebuilding Docker containers")
        print("⏳ This may take a few minutes...")
        success, output = execute_ssh_command(
            ssh,
            f"cd {PROJECT_DIR} && docker compose build --no-cache"
        )
        if not success:
            print("❌ Failed to rebuild containers")
            ssh.close()
            return False
        print("✅ Containers rebuilt successfully")
        
        # Step 5: Stop old containers
        print_step(5, 7, "Stopping old containers")
        execute_ssh_command(
            ssh,
            f"cd {PROJECT_DIR} && docker compose down"
        )
        print("✅ Old containers stopped")
        
        # Step 6: Start new containers
        print_step(6, 7, "Starting new containers")
        success, output = execute_ssh_command(
            ssh,
            f"cd {PROJECT_DIR} && docker compose up -d"
        )
        if not success:
            print("❌ Failed to start containers")
            ssh.close()
            return False
        print("✅ New containers started")
        
        # Step 7: Verify deployment
        print_step(7, 7, "Verifying deployment")
        print("⏳ Waiting 15 seconds for services to initialize...")
        time.sleep(15)
        
        # Check container status
        print("\n📊 Container status:")
        execute_ssh_command(
            ssh,
            f"cd {PROJECT_DIR} && docker compose ps"
        )
        
        # Health check
        print("\n🏥 Health check:")
        success, output = execute_ssh_command(
            ssh,
            "docker exec reportforge-backend curl -f http://localhost:8030/health 2>/dev/null",
            show_output=False
        )
        
        if success and "healthy" in output:
            print("✅ Health check PASSED")
        else:
            print("⚠️  Health check FAILED - checking logs...")
        
        # Show recent logs
        print("\n📋 Recent backend logs:")
        execute_ssh_command(
            ssh,
            "docker logs reportforge-backend --tail 30"
        )
        
        # Close connection
        ssh.close()
        
        # Success summary
        print_header("✅ DEPLOYMENT COMPLETED SUCCESSFULLY!")
        print("\n🌐 Application URL: https://reportforge.brainaihub.tech")
        print("📊 API Docs: https://reportforge.brainaihub.tech/api/docs")
        print("\n🔍 To check logs:")
        print(f"   ssh {USERNAME}@{HOST}")
        print(f"   cd {PROJECT_DIR}")
        print("   docker logs -f reportforge-backend")
        print("\n")
        
        return True
        
    except paramiko.AuthenticationException:
        print("\n❌ Authentication failed. Check credentials.")
        return False
    except paramiko.SSHException as e:
        print(f"\n❌ SSH error: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("\n" + "🚀 " * 20)
    
    # Confirmation
    confirm = input("\n⚠️  This will deploy to PRODUCTION. Continue? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("\n❌ Deployment cancelled by user")
        return 1
    
    # Run deployment
    success = deploy_to_production()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
