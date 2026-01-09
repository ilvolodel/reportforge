#!/usr/bin/env python3
"""
Quick migration script to drop old reports tables.
Run this directly on production server or remotely.
"""

import subprocess
import sys

SQL_COMMANDS = """
DROP TABLE IF EXISTS report_versions CASCADE;
DROP TABLE IF EXISTS report_executive_summary CASCADE;
DROP TABLE IF EXISTS report_project_snapshots CASCADE;
DROP TABLE IF EXISTS report_templates CASCADE;
DROP TABLE IF EXISTS reports CASCADE;
"""

def run_migration_local():
    """Run migration on local production server (inside /opt/reportforge)"""
    print("🗄️  Running migration locally...")
    
    # Execute SQL
    proc = subprocess.run(
        ["docker", "exec", "-i", "reportforge-db", "psql", "-U", "reportforge", "-d", "reportforge"],
        input=SQL_COMMANDS,
        text=True,
        capture_output=True
    )
    
    if proc.returncode != 0:
        print(f"❌ Error: {proc.stderr}")
        return False
    
    print("✅ Tables dropped")
    print(proc.stdout)
    
    # Restart backend
    print("\n🔄 Restarting backend...")
    subprocess.run(["docker", "compose", "restart", "backend"])
    
    print("\n✅ Migration complete!")
    return True

def run_migration_remote():
    """Run migration remotely via SSH"""
    print("🗄️  Running migration remotely...")
    
    ssh_cmd = f"""
    cd /opt/reportforge && \\
    docker exec -i reportforge-db psql -U reportforge -d reportforge <<'EOSQL'
{SQL_COMMANDS}
EOSQL
    docker compose restart backend
    """
    
    proc = subprocess.run(
        ["ssh", "root@10.135.215.172", ssh_cmd],
        capture_output=True,
        text=True
    )
    
    if proc.returncode != 0:
        print(f"❌ Error: {proc.stderr}")
        return False
    
    print("✅ Migration complete!")
    print(proc.stdout)
    return True

if __name__ == "__main__":
    import os
    
    # Check if we're on production
    if os.path.exists("/opt/reportforge"):
        success = run_migration_local()
    else:
        print("⚠️  Not on production server, trying remote migration...")
        success = run_migration_remote()
    
    sys.exit(0 if success else 1)
