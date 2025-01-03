from pathlib import Path
import logging
import os
import shutil

def ensure_directory_exists(directory_path,create=True,print_info=True):
    directory = Path(directory_path)
    if not directory.exists():
        if create: 
            directory.mkdir(parents=True, exist_ok=True)
            if print_info: print(f'Directory {directory_path} created.')
        else:
            raise FileNotFoundError(f'Directory {directory_path} does not exist.')
    else:
        if print_info: print(f'Directory {directory_path} already exists.')
    return directory_path


def ensure_file_exists(file_path, raise_error=True):
    file = Path(file_path)
    if not file.exists():
        if raise_error:
            raise FileNotFoundError(f'File {file_path} does not exist.')
        else:
            return False
    else: return True

def clean_logs(log_directory):
    old_log_directory = Path(log_directory) / '_old'

    # Create the _old directory if it doesn't exist
    old_log_directory.mkdir(exist_ok=True)

    # Get a list of all log files in the log directory
    log_files = [f for f in os.listdir(log_directory) if f.endswith('.log')]

    # Sort the log files by modification time (newest first)
    log_files.sort(key=lambda x: os.path.getmtime(os.path.join(log_directory, x)), reverse=True)

    # Get the newest log file
    newest_log_file = log_files[0] if log_files else None

    # Move all log files except the newest one to the _old directory
    for log_file in log_files:
        if log_file != newest_log_file:
            source_path = os.path.join(log_directory, log_file)
            destination_path = old_log_directory / log_file
            shutil.move(source_path, destination_path)
            print(f'Moved {log_file} to _old folder.')
    
    print('Done moving log files.')
    logging.info('Done moving log files.')
   

