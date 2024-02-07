#Logging temporarily disabled, please uncomment logging lines
#in handle_file_cop and main function to re-enable.

import os
import shutil
import sqlite3
from tkinter import filedialog, Tk
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed


# Categorization of file types into respective folders
file_categories = {
    'Images': [
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', 
        '.tif', '.ico', '.pcx', '.tga', '.fpx', '.svg', '.psd', '.raw', 
        '.wmf', '.exif', '.ppm', '.pgm', '.pbm', '.pnm', '.heif', '.heic'
    ],
    'Videos': [
        '.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.mpg', '.mpeg', 
        '.webm', '.rm', '.rmvb', '.asf', '.divx', '.vob', '.m2ts', 
        '.3gp', '.m4v', '.ts', '.ogv', '.mxf'
    ],
    'Audio': [
        '.mp3', '.wav', '.aac', '.m4a', '.flac', '.ogg', '.wma', '.ra', 
        '.ram', '.mid', '.midi', '.aiff', '.aif', '.amr', '.ape', '.voc', 
        '.au'
    ],
    'Compressed Files': [
        '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.arj', 
        '.lzh', '.lha', '.ace', '.z', '.cab', '.sit', '.tgz'
    ],
    'Documents': [
        '.doc', '.docx', '.txt', '.pdf', '.xls', '.xlsx', '.ppt', 
        '.pptx', '.odt', '.ods', '.odp', '.rtf', '.wpd', '.wps', 
        '.abw', '.lwp', '.sxw', '.sxi', '.sxc', '.csv', '.epub', 
        '.pages', '.key', '.numbers'
    ],
  
    'Design & CAD': [
        '.psd', '.ai', '.dwg', '.dxf', '.skp', '.3ds', '.max', '.blend', 
        '.cad', '.stl', '.eps', '.svg'
    ],
    'Backups': [
        '.bak', '.tmp', '.old', '.bkp', '.backup', '.sav', '.save', 
        '.snapshot', '.gho', '.tib'
    ],
    'E-Books': [
        '.mobi', '.epub', '.pdf', '.azw', '.ibook', '.cbr', '.cbz'
    ],

    'Possible Crypto Wallets': [
        '.wallet', '.dat', '.keys' #'.json',  # Add other extensions as needed
    ]

}

# GUI to select source and destination directories
def select_directories():
    root = Tk()  # Using Tk directly as it's already imported
    root.withdraw()  # Hide the main window

    source_dir = filedialog.askdirectory(title="Select Source Directory")
    if not source_dir:
        return None, None

    dest_dir = filedialog.askdirectory(title="Select Destination Directory")
    if not dest_dir:
        return None, None

    root.destroy()
    return source_dir, dest_dir

# SQLite Database Functions
def initialize_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS processed_files (
            source_path TEXT PRIMARY KEY,
            dest_path TEXT,
            processed BOOLEAN
        )
    """)
    conn.commit()
    conn.close()


def update_or_insert_file_record(db_path, source_path, dest_path, processed):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO processed_files (source_path, dest_path, processed)
        VALUES (?, ?, ?)
        ON CONFLICT(source_path) DO UPDATE SET
        dest_path = excluded.dest_path,
        processed = excluded.processed
    """, (source_path, dest_path, processed))
    conn.commit()
    conn.close()

def file_record_exists(db_path, source_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_files WHERE source_path = ? AND processed = 1", (source_path,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def clear_database_if_output_empty(db_path, dest_dir):
    if not any(os.scandir(dest_dir)):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM processed_files")
        conn.commit()
        conn.close()
        print("Output directory is empty. Database has been cleared.")

# Adjustments in DB Functions for verification and update
def verify_and_update_db_for_missing_files(db_path, dest_dir):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT source_path, dest_path FROM processed_files WHERE processed = 1")
    all_records = cursor.fetchall()

    for source_path, dest_path in all_records:
        if not os.path.exists(dest_path):
            cursor.execute("UPDATE processed_files SET processed = 0 WHERE source_path = ?", (source_path,))
            print(f"Missing file detected: {source_path}. Marking for reprocessing.")

    conn.commit()
    conn.close()

def get_file_category(file_path):
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    for category, extensions in file_categories.items():
        if ext in extensions:
            return category
    return None

def handle_file_copy(file_path, dest_dir, possible_duplicates_dir, db_path):
    if file_record_exists(db_path, file_path):
        return  # Skip already processed files

    category = get_file_category(file_path)
    if category:
        category_path = os.path.join(dest_dir, category)
        os.makedirs(category_path, exist_ok=True)
        dest_file_path = os.path.join(category_path, os.path.basename(file_path))

        if os.path.exists(dest_file_path):
            shutil.copy2(file_path, os.path.join(possible_duplicates_dir, os.path.basename(file_path)))
        else:
            shutil.copy2(file_path, dest_file_path)

        update_or_insert_file_record(db_path, file_path, dest_file_path, True)



# Function to scan directories and return files
def scan_directory_recursive(directory):
    file_paths = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_paths.append(os.path.join(root, file))
    return file_paths



def main():
    source_dir, dest_dir = select_directories()
    if not source_dir or not dest_dir:
        print("Invalid directory selection. Exiting.")
        return

    db_path = 'processed_files.db'
    initialize_db(db_path)
    clear_database_if_output_empty(db_path, dest_dir)
    verify_and_update_db_for_missing_files(db_path, dest_dir)

    all_files = scan_directory_recursive(source_dir)
    possible_duplicates_dir = os.path.join(dest_dir, "Possible Duplicates")
    os.makedirs(possible_duplicates_dir, exist_ok=True)

    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(handle_file_copy, file_path, dest_dir, possible_duplicates_dir, db_path) for file_path in all_files]
        for _ in tqdm(as_completed(futures), total=len(futures), desc="Copying files"):
            pass

    print("Files have been successfully copied and verified.")

if __name__ == "__main__":
    main()