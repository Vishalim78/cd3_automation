import subprocess
import os

# === Correct Windows Paths ===
toolkit_dir = r"I:\cd3_automation\cd3-automation-toolkit"
tenancy_prefix = "vishal"
properties_path = fr"I:\cd3_automation\cd3-automation-toolkit\tenancies\{tenancy_prefix}\{tenancy_prefix}_setUpOCI.properties"
terraform_dir = fr"I:\cd3_automation\cd3-automation-toolkit\tenancies\{tenancy_prefix}\terraform_files"

def run_export():
    os.chdir(toolkit_dir)
    print("🔄 Exporting resources from OCI using CD3 Toolkit...")
    subprocess.run(["python", "setUpOCI.py", properties_path], check=True)
    print("✅ Export complete! Check:", terraform_dir)

if __name__ == "__main__":
    run_export()
