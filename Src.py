#!/bin/python3


import os
import subprocess
from colorama import Fore, Style 
from pathlib import Path
from subprocess import call
import datetime
import platform
import psutil
import shutil
import sys



# func


def cp(source, destination):
  
    try:
        if os.path.exists(source):
            if os.path.isfile(source):
                shutil.copy(source, destination)
                print(f"Copied {source} to {destination}") # Give feedback
            else:
                print(Fore.RED + "Source is not a valid file." + Fore.RESET)
                return False
        else:
            print(Fore.RED + "Source file not found" + Fore.RESET)
            return False
        return True
    except FileNotFoundError:
        print(Fore.RED + f"Error: '{source}' not found." + Fore.RESET)
    except PermissionError:
        print(
            Fore.RED
            + f"Error: Permission denied for '{source}' or '{destination}'"
            + Fore.RESET
        )


def mv(source, destination):

    try:
        shutil.move(source, destination)
        print(f"Moved {source} → {destination} ") 
    except FileNotFoundError:
        print(Fore.RED + f"Error: '{source}' not found." + Fore.RESET)
    except PermissionError:
        print(
            Fore.RED
            + f"Error: Permission denied for '{source}' or '{destination}'"
            + Fore.RESET
        )


def rmdir(directory):
    try:
        if os.path.isdir(directory):
            # Only empty directories
            if len(os.listdir(directory)) > 0:
                print(Fore.YELLOW + "Directory not empty! Use 'delete' instead." + Fore.RESET)
                return
            os.rmdir(directory)
            print(f"Removed empty directory: {directory}")
        else:
            print(Fore.RED + "Source is not a directory" + Fore.RESET)
    except FileNotFoundError:
        print(Fore.RED + f"Error: '{directory}' not found." + Fore.RESET)
    except PermissionError:
        print(Fore.RED + f"Error: Permission denied for '{directory}'" + Fore.RESET)

def rm(file_or_directory):
    # rm - warns first for directories
    try:
        if os.path.isfile(file_or_directory):
            os.remove(file_or_directory)
            print(f"Removed file: {file_or_directory}")
        elif os.path.isdir(file_or_directory):
            # Added extra safety check here
            file_count = sum(len(files) for _, _, files in os.walk(file_or_directory))
            if file_count > 5:
                confirm = input(f"Directory has {file_count} files. Type 'YES' to confirm: ")
                if confirm != "YES":
                    print("Operation canceled.")
                    return
            shutil.rmtree(file_or_directory)
            print(f"Removed directory tree: {file_or_directory}")
        else:
            print(
                Fore.RED
                + f"Error: '{file_or_directory}' is not a file or directory."
                + Fore.RESET
            )
    except FileNotFoundError:
        print(Fore.RED + f"Error: '{file_or_directory}' not found." + Fore.RESET)
    except PermissionError:
        print(Fore.RED + f"Error: Permission denied for '{file_or_directory}'" + Fore.RESET)


def get_system_info():
    # system info grabber - pretty basic but works
    MY_MULTIPLIER = 1024 * 1024 
    
    comp_info = {}
    comp_info["OS"] = platform.system()
    comp_info["OS Version"] = platform.version()
    comp_info["Machine"] = platform.machine()
    
    ram = psutil.virtual_memory()
    comp_info["Total RAM"] = f"{ram.total / MY_MULTIPLIER:.0f} MB"
    comp_info["Available RAM"] = f"{ram.available / MY_MULTIPLIER:.0f} MB"

    
    
    comp_info["CPU Cores"] = os.cpu_count()
    comp_info["Username"] = os.getenv("USER") or os.getenv("USERNAME")
    
    return comp_info


def view(directory):
    # ls command, shows only normal files

    normal_contents = []
    try:
        all_items = os.listdir(directory)
        
        # Sort them with folders first (my preference)
        folders = []
        files = []
        
        for item in all_items:
         
            item_path = os.path.join(directory, item)
            if os.path.isdir(item_path):
                folders.append(f"[{item}]")  # Mark folders with brackets
            else:
                files.append(item)
                
        normal_contents = folders + files
    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found.")
    
    return normal_contents


def view_all(directory):
    # Show absolutely everything 
    try:
        all_items = sorted(os.listdir(directory))
        return all_items
    except:
        print(Fore.RED + "Can't access that directory!" + Fore.RESET)
        return []


def create_file(name):
    # Don't let users do silly things
    rm_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    
    for char in rm_chars:
        if char in str(name):
            print(Fore.RED + f"Can't include '{char}' in file names" + Fore.RESET)
            return
            
    try:
        print(f"Created file: {name}")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {str(e)}" + Fore.RESET)


def create_folder(folder_name):
    # folder maker 
    folder_name = str(folder_name)
    try:
        Path(folder_name).mkdir()
        print(f"Created folder: {folder_name}")
    except Exception as e:
        print(Fore.RED + f"An error occurred: {str(e)}" + Fore.RESET)


def display(file_path):
    # Quick cat replacement
    MAX_LINES = 500  
    
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
            if len(lines) > MAX_LINES:
                print(f"File is too large ({len(lines)} lines). Showing first {MAX_LINES} lines:")
                print("".join(lines[:MAX_LINES]))
                print(f"...and {len(lines) - MAX_LINES} more lines (truncated)")
            else:
                print("".join(lines))
    except FileNotFoundError:
        print(Fore.RED + "File not found: " + file_path + Fore.RESET)
    except UnicodeDecodeError:
        print(Fore.YELLOW + "Cannot display binary file: " + file_path + Fore.RESET)


def parse_cmd(input_str):
    # custom command parser - handles quotes and escapes
    # E.g. copy "my file.txt" "new file.txt"
    parts = []
    current_part = ""
    in_quotes = False
    escape_next = False
    
    for char in input_str:
        if escape_next:
            current_part += char
            escape_next = False
        elif char == '\\':
            escape_next = True
        elif char == '"' and not in_quotes:
            in_quotes = True
        elif char == '"' and in_quotes:
            in_quotes = False
        elif char.isspace() and not in_quotes:
            if current_part:
                parts.append(current_part)
                current_part = ""
        else:
            current_part += char
            
    if current_part:
        parts.append(current_part)
        
    return parts

def main():
    
    help_text = """
    SHELL COMMANDS 
    
    File operations:
      view                - Show non-hidden files in current dir
      view_all            - Show ALL files (including hidden)
      goto <path>         - Change directory 
      display <file>      - Show file contents
      create_file <name>  - Create new empty file
      create_folder <name>- Create new directory
      copy <from> <to>    - Copy file to new location
      move <from> <to>    - Move file to new location
      delete <path>       - Delete file or directory
      delete_folder <dir> - Delete empty directory only
      
    System:
      info                - Show system information
      version             - Show shell version
      
    Special:
      __help__            - Show this help message
      __exit__            - Exit the shell
      
     All system commands should work too!
    """
    
    startup_text = """
    SHELL v3 
    Type __help__ for commands or just start typing!
    """

 

    # Main config
    SHELL_CFG = {
        "show_dir": True,  
        "version": 3,
        "name": "Shell"
    }

    # Startup banner 
    print(Fore.MAGENTA + startup_text + Fore.RESET)
    
    # custom welcome message
    current_hour = datetime.datetime.now().hour
    if current_hour < 12:
        greeting = "Good morning!"
    elif current_hour < 18:
        greeting = "Good afternoon!"
    else:
        greeting = "Good evening!"
        
    print(f"{greeting} Shell started at {datetime.datetime.now().strftime('%H:%M:%S')}")

    commands_run = 0  # Track how many commands we've run
    current_dir = os.getcwd()

    # Command loop
    while True:    
        # Path display
        if SHELL_CFG["show_dir"]:
            # Shorten home directory paths
            home = os.path.expanduser("~")
            if current_dir.startswith(home):
                display_dir = "~" + current_dir[len(home):]
            else:
                display_dir = current_dir
                
            print(Fore.GREEN + display_dir, end="")

        # Command prompt
        print(Fore.BLUE + " $ " + Fore.RESET, end="")

        # Get input
        input_cmd = input().strip()
        commands_run += 1
        
        # Skip empty commands
        if not input_cmd:
            continue

        # Command handling
        if input_cmd == "__exit__":
            print("Thanks for using Shell! Bye!")
            break
            
        elif input_cmd == "__help__":
            print(help_text)
            
        elif input_cmd == "view":
            files = view(current_dir)
            if files:
                for i, file in enumerate(files):
                    print(file, end="  ")
                    # Wrap lines for readability
                    if (i + 1) % 5 == 0:
                        print()
                print("\n")
            else:
                print("(Directory is empty)")
                
        elif input_cmd == "view_all":
            files = view_all(current_dir)
            if files:
                for file in files:
                    # Color hidden files differently
                    if file.startswith('.'):
                        print(Fore.BLUE + file + Fore.RESET, end="  ")
                    else:
                        print(file, end="  ")
                print("\n")
                
        elif input_cmd.startswith("goto "):
            target_dir = input_cmd[5:].strip()
            
            # Handle home directory shortcut
            if target_dir == "~":
                target_dir = os.path.expanduser("~")
                
            # Handle parent directory
            if target_dir == "..":
                target_dir = os.path.dirname(current_dir)
                
            try:
                os.chdir(target_dir)
                current_dir = os.getcwd()
                print(f"Changed to: {current_dir}")
            except FileNotFoundError:
                print(Fore.RED + "Directory not found: " + target_dir + Fore.RESET)
                
        elif input_cmd.startswith("display "):
            file_path = input_cmd[8:].strip()
            display(file_path)
            
        elif input_cmd.startswith("create_file "):
            file_name = input_cmd[12:].strip()
            create_file(file_name)
            
        elif input_cmd.startswith("create_folder "):
            folder_name = input_cmd[14:].strip()
            create_folder(folder_name)
            
        elif input_cmd.startswith("copy "):
            parts = parse_cmd(input_cmd[5:])
            if len(parts) == 2:
                cp(parts[0], parts[1])
            else:
                print(Fore.RED + "Usage: copy <source> <destination>" + Fore.RESET)
                
        elif input_cmd.startswith("move "):
            parts = parse_cmd(input_cmd[5:])
            if len(parts) == 2:
                mv(parts[0], parts[1])
            else:
                print(Fore.RED + "Usage: move <source> <destination>" + Fore.RESET)
                
        elif input_cmd.startswith("delete "):
            target = input_cmd[7:].strip()
            rm(target)
            
        elif input_cmd.startswith("delete_folder "):
            target = input_cmd[14:].strip()
            rmdir(target)
            
        elif input_cmd == "version":
            print(f" {SHELL_CFG['name']} version {SHELL_CFG['version']}")
            
        elif input_cmd == "info":
            system_info = get_system_info()
            print("\n===== SYSTEM INFO =====")
            for category, data in system_info.items():
                if isinstance(data, dict):
                    print(f"\n{category}:")
                    for key, value in data.items():
                        print(f"  {key}: {value}")
                else:
                    print(f"{category}: {data}")
                    
       # Handle system commands
        else:
            try:
         
                process = subprocess.Popen(
                    input_cmd, 
                    shell=True, 
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Show output in real-time
                for line in process.stdout:
                    print(line.rstrip())
                    
                process.wait()
                
                # Show errors if any
                if process.returncode != 0:
                    for line in process.stderr:
                        print(Fore.RED + line.rstrip() + Fore.RESET)
            except Exception as e:
                print(Fore.RED + f"Command failed: {e}" + Fore.RESET)



if __name__ == "__main__":
    # Start the shell!
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)
