# FileCat-Transfer
An efficient Python tool for automated file transfer and categorization, featuring resilience to interruptions and database-backed progress tracking for reliability.


# File Transfer and Categorization Tool
Overview
--------
This Python script is designed to transfer files from a source directory to a destination directory, categorizing them based on their file types. It will search every subdirectory in the source and create a SQL database entry for each file. It uses a SQLite database to track the progress of file transfers, ensuring resilience against interruptions such as crashes or manual stops. Has been tested and been proven stable on inputs up tp 250GB.

Key Features
------------
- File Categorization: Automatically sorts files into predefined categories based on their extensions.
- Duplicate Handling: Places duplicate files in a separate "Possible Duplicates" folder.
- Resilience: Utilizes a SQLite database to remember transferred files, allowing the script to resume from where it left off in case of an interruption.
- Verification: Confirms the presence of files in the destination directory for consistency and data integrity.
- Searches entire directory trees to make it easy to collect file types from a multitude of locations. 

File Categories
---------------
Files are categorized into the following types:
- Images (e.g., .jpg, .png)
- Videos (e.g., .mp4, .avi)
- Audio (e.g., .mp3, .wav)
- Compressed Files (e.g., .zip, .rar)
- Documents (e.g., .pdf, .docx)
- Design & CAD (e.g., .psd, .dwg)
- Backups (e.g., .bak, .tib)
- E-Books (e.g., .epub, .mobi)
- Possible Crypto Wallets (e.g., .wallet, .dat)
  
Note: Additional catagories may be added or removed manually, as can additional filetypes. Simply make modifications to the file_categories function. 

Usage
-----
1. Running the Script: Launch the script in a Python environment. The script uses a GUI prompt to select the source and destination directories.
2. Select Directories: Use the file dialog to choose the source directory (where files are located) and the destination directory (where files will be transferred and categorized).
3. Automatic Processing: The script will start processing the files, showing progress in the terminal. If interrupted, you can simply rerun the script, and it will resume from where it left off.
4. Completion: Once complete, the script will display a message confirming the successful transfer and categorization of files.

Note on Database Handling
-------------------------
- The script creates a SQLite database (processed_files.db) to track file processing.
- It checks the database at the start to determine which files have already been processed, ensuring no unnecessary reprocessing.
- In case the output directory is empty but the database exists (indicating a previous run), it clears the database to avoid inconsistencies.

Requirements
------------
- Python environment with the following packages: os, shutil, sqlite3, tkinter, tqdm, concurrent.futures.
- Adequate permissions to access the source and destination directories.

Disclaimer
----------
- Always back up important data before running bulk file operations.
- The script handles duplicates cautiously but verify the 'Possible Duplicates' folder manually to ensure no data loss.

This tool aims to simplify large-scale file transfers and organization tasks, especially beneficial for users dealing with diverse file types and large datasets. Its resilience to interruptions and ability to track progress make it suitable for situations where reliability is crucial.
"""
