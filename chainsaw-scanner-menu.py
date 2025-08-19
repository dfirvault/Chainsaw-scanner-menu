import os
import subprocess
import time
import platform
from datetime import datetime
import sys
import ctypes
import win32con
import re
from tkinter import Tk, filedialog

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if platform.system() != 'Windows':
        print("This script requires Windows.")
        return False
        
    if not is_admin():
        print("Requesting administrator privileges...")
        script = os.path.abspath(sys.argv[0])
        params = ' '.join([script] + sys.argv[1:])
        
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, params, None, 1
            )
        except Exception as e:
            print(f"Failed to elevate privileges: {str(e)}")
            return False
        return True
    return False

def select_file(title, initialdir=None, filetypes=None):
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    file_path = filedialog.askopenfilename(
        title=title,
        initialdir=initialdir,
        filetypes=filetypes
    )
    root.destroy()
    return file_path

def select_folder(title, initialdir=None):
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory(
        title=title,
        initialdir=initialdir
    )
    root.destroy()
    return folder_path

def find_evtx_folder(start_path):
    evtx_folders = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            if file.lower().endswith('.evtx'):
                if root not in evtx_folders:
                    evtx_folders.append(root)
    return evtx_folders

def main():
    print("\nChainsaw Event Log Processing Tool")
    print("Version 1.0 - Sigma Rule Scanning\n")

    # Chainsaw path configuration
    config_file = "chainsaw-config.txt"
    chainsaw_path = ""
    
    if os.path.exists(config_file):
        with open(config_file, 'r') as f:
            chainsaw_path = f.readline().strip()

    if not chainsaw_path:
        chainsaw_path = r"C:\Tools\Chainsaw\chainsaw_x86_64-pc-windows-msvc.exe"
        if not os.path.exists(chainsaw_path):
            if os.path.exists("chainsaw.exe"):
                chainsaw_path = os.path.join(os.getcwd(), "chainsaw.exe")

    while not os.path.exists(chainsaw_path):
        print("\nChainsaw executable not found.")
        try:
            chainsaw_path = select_file(
                "Select Chainsaw executable (chainsaw*.exe)",
                initialdir=os.getcwd(),
                filetypes=[("Chainsaw Executable", "chainsaw*.exe"), ("All files", "*.*")]
            )
            
            if not chainsaw_path:
                print("File selection cancelled. Exiting...")
                sys.exit(1)
                
        except Exception as e:
            print(f"Error showing file dialog: {e}")
            chainsaw_path = input("Enter full path to Chainsaw executable: ").strip()
        
        if chainsaw_path and os.path.isdir(chainsaw_path):
            chainsaw_path = os.path.join(chainsaw_path, "chainsaw.exe")
    
    with open(config_file, 'w') as f:
        f.write(chainsaw_path)

    # Main menu
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n===============================")
        print("    Chainsaw Event Log Scanner")
        print("===============================\n")
        print("[1] Scan a folder or mounted image containing EVTX files")
        print("[0] Exit")
        
        choice = input("\nEnter your choice (1 or 0): ").strip()
        
        if choice == "1":
            scan_folder_with_evtx(chainsaw_path)
        elif choice == "0":
            print("\nExiting...")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(1)

def scan_folder_with_evtx(chainsaw_path):
    print("\nPlease select the folder containing EVTX files:")
    evtx_folder = select_folder("Select folder containing EVTX files")
    
    if not evtx_folder:
        print("Folder selection cancelled.")
        return
    
    evtx_files = [f for f in os.listdir(evtx_folder) if f.lower().endswith('.evtx')]
    if not evtx_files:
        print("\nNo EVTX files found in the selected folder.")
        search_subfolders = input("Search subfolders for EVTX files? (y/n): ").strip().lower()
        
        if search_subfolders == 'y':
            evtx_folders = find_evtx_folder(evtx_folder)
            if not evtx_folders:
                print("No EVTX files found in any subfolders.")
                input("Press Enter to continue...")
                return
            elif len(evtx_folders) == 1:
                evtx_folder = evtx_folders[0]
                print(f"\nUsing EVTX files from: {evtx_folder}")
            else:
                print("\nMultiple folders with EVTX files found:")
                for i, folder in enumerate(evtx_folders, 1):
                    print(f"[{i}] {folder}")
                
                while True:
                    selection = input("\nSelect folder to scan (1-{} or 'a' for all): ".format(len(evtx_folders))).strip().lower()
                    if selection == 'a':
                        for folder in evtx_folders:
                            run_chainsaw_scan(chainsaw_path, folder)
                        return
                    elif selection.isdigit() and 1 <= int(selection) <= len(evtx_folders):
                        evtx_folder = evtx_folders[int(selection)-1]
                        break
                    else:
                        print("Invalid selection.")
        else:
            input("Press Enter to continue...")
            return
    
    run_chainsaw_scan(chainsaw_path, evtx_folder)

def run_chainsaw_scan(chainsaw_path, evtx_folder):
    print("\nPlease select the folder to save reports:")
    report_path = select_folder(
        "Select folder to save reports",
        initialdir=os.path.dirname(chainsaw_path) if chainsaw_path else os.path.expanduser("~\\Documents")
    )
    
    if not report_path:
        print("Folder selection cancelled.")
        return
    
    os.makedirs(report_path, exist_ok=True)
    if not os.path.isdir(report_path):
        print("ERROR: Could not create directory")
        return

    # Get folder name for output
    folder_name = os.path.basename(os.path.normpath(evtx_folder))
    folder_name = re.sub(r'[^a-zA-Z0-9_-]', '_', folder_name)
    if not folder_name:
        folder_name = "chainsaw_scan"

    # Get case name from user
    while True:
        case_name = input("\nEnter a case name (e.g., MAL2024-001): ").strip()
        if case_name:
            case_name = re.sub(r'[^a-zA-Z0-9_-]', '_', case_name)
            break
        print("Case name cannot be empty. Please try again.")

    # Generate filenames in YYYYMMDD-FolderName-CaseName format
    now = datetime.now()
    date_prefix = now.strftime("%Y%m%d")
    
    base_filename = f"{date_prefix}-{folder_name}-{case_name}"
    log_file = f"{base_filename}-log.txt"

    # Get the directory where Chainsaw is located
    chainsaw_dir = os.path.dirname(os.path.abspath(chainsaw_path))
    
    # Paths for Sigma rules and mappings (relative to Chainsaw directory)
    sigma_rules_path = os.path.join(chainsaw_dir, "rules")
    sigma_mappings_path = os.path.join(chainsaw_dir, "mappings", "sigma-event-logs-all.yml")
    
    # Check if required files exist
    if not os.path.exists(sigma_rules_path):
        print(f"\nError: Sigma rules directory not found at {sigma_rules_path}")
        print("Please ensure the 'rules' folder exists in the same directory as the Chainsaw executable.")
        input("Press Enter to continue...")
        return
    
    if not os.path.exists(sigma_mappings_path):
        print(f"\nError: Sigma mappings file not found at {sigma_mappings_path}")
        print("Please ensure the 'mappings/sigma-event-logs-all.yml' file exists in the Chainsaw directory.")
        input("Press Enter to continue...")
        return

    # Run Chainsaw with Sigma rules
    cmd = [
        chainsaw_path,
        "hunt",
        evtx_folder,
        "-s", "sigma/",
        "--mapping", sigma_mappings_path,
        "-r", sigma_rules_path,
        "--csv",
        "--output", report_path
    ]
    
    try:
        print(f"\nStarting Chainsaw scan on: {evtx_folder}")
        print(f"Using Sigma rules from: {sigma_rules_path}")
        print(f"Using mappings from: {sigma_mappings_path}")
        print(f"Output will be saved to: {report_path}")
        
        with open(os.path.join(report_path, log_file), 'w') as log:
            process = subprocess.Popen(
                cmd,
                stdout=log,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                cwd=chainsaw_dir  # Run from Chainsaw directory to ensure relative paths work
            )
            
            _, stderr = process.communicate()
            
            if process.returncode != 0:
                print(f"\nError during scan (exit code {process.returncode}):")
                if stderr:
                    print(stderr.strip())
                else:
                    print("No error details available. Check the log file for more information.")
            else:
                print("\nScan completed successfully!")
        
    except Exception as e:
        print(f"\nFailed to start Chainsaw: {str(e)}")
    
    if platform.system() == 'Windows':
        os.startfile(report_path)
    
    input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    main()
