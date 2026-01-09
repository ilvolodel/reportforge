#!/usr/bin/env python3
"""
Remote Database Migration Script for ReportForge
Executes migration on production server via SSH using Paramiko
"""

import paramiko
import time
import sys

# Production server details
HOST = "10.135.215.172"
USERNAME = "root"
PASSWORD = "Fr3qu3nc1."
PROJECT_DIR = "/opt/reportforge"

# Migration SQL
MIGRATION_SQL = """
DROP TABLE IF EXISTS report_versions CASCADE;
DROP TABLE IF EXISTS report_executive_summary CASCADE;
DROP TABLE IF EXISTS report_project_snapshots CASCADE;
DROP TABLE IF EXISTS report_templates CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
"""

def execute_ssh_command(ssh, command, description):
    """Execute a command via SSH and print output"""
    print(f"\n{description}")
    stdin, stdout, stderr = ssh.exec_command(command)
    
    # Wait for command to complete
    exit_status = stdout.channel.recv_exit_status()
    
    # Print output
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    
    if output:
        print(output)
    if error and exit_status != 0:
        print(f"⚠️  Error: {error}", file=sys.stderr)
        
    return exit_status == 0

def main():
    print("🗄️  ReportForge Remote Database Migration")
    print("=" * 50)
    print(f"\n📍 Target: {USERNAME}@{HOST}")
    print(f"📁 Project: {PROJECT_DIR}\n")
    
    try:
        # Create SSH client
        print("🔐 Connecting to production server...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=10)
        print("✅ Connected!\n")
        
        # Step 1: Pull latest code
        if not execute_ssh_command(
            ssh,
            f"cd {PROJECT_DIR} && git pull",
            "📥 Pulling latest code..."
        ):
            print("⚠️  Warning: Git pull failed, continuing anyway...")
        
        # Step 2: Drop old tables
        drop_command = f"cd {PROJECT_DIR} && echo '{MIGRATION_SQL}' | docker exec -i reportforge-db psql -U reportforge -d reportforge"
        if execute_ssh_command(
            ssh,
            drop_command,
            "🗑️  Dropping old reports tables..."
        ):
            print("✅ Old tables dropped successfully")
        else:
            print("❌ Failed to drop tables")
            return False
        
        # Step 3: Restart backend
        if execute_ssh_command(
            ssh,
            f"cd {PROJECT_DIR} && docker compose restart backend",
            "🔄 Restarting backend to recreate tables..."
        ):
            print("✅ Backend restarted")
        else:
            print("❌ Failed to restart backend")
            return False
        
        # Step 4: Wait for backend to start
        print("\n⏳ Waiting 5 seconds for backend to initialize...")
        time.sleep(5)
        
        # Step 5: Verify new tables
        verify_command = "docker exec reportforge-db psql -U reportforge -d reportforge -c '\\dt report*'"
        print("\n🔍 Verifying new tables were created...")
        if execute_ssh_command(
            ssh,
            verify_command,
            "📊 Current reports tables:"
        ):
            print("✅ Tables verified!")
        else:
            print("⚠️  Warning: Could not verify tables")
        
        # Step 6: Check backend logs
        print("\n📋 Recent backend logs:")
        execute_ssh_command(
            ssh,
            "docker logs reportforge-backend --tail 20",
            ""
        )
        
        # Close connection
        ssh.close()
        
        print("\n" + "=" * 50)
        print("🎉 Migration completed successfully!")
        print("\n🧪 Test the API:")
        print("   curl https://reportforge.brainaihub.tech/api/reports/templates")
        print("\n")
        
        return True
        
    except paramiko.AuthenticationException:
        print("❌ Authentication failed. Check credentials.")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
