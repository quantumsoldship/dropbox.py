token = "Put Token Here"
import os
import sys
import math
import datetime
# Initialize a Dropbox object using your access token
dbx = dropbox.Dropbox(token)
def read_settings():
    try:
        with open('settings.txt', 'r') as file:
            settings = file.read().strip()
            return settings
    except FileNotFoundError:
        # If settings.txt does not exist, create it with default sorting by name
        with open('settings.txt', 'w') as file:
            file.write('1')  # Default to sort by name
        return '1'
def upload_file(local_path):
    dropbox_path = 'settings.txt' + os.path.basename(local_path)
    try:
        with open(local_path, 'rb') as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode('overwrite'))
            print("File uploaded successfully.")
    except dropbox.exceptions.ApiError as err:
        print(f"API error: {err}")

def write_settings(sort_by):
    with open('settings.txt', 'w') as file:
        file.write(sort_by)

def settings_menu():
    print("Settings:")
    print("1. Sort by Name")
    print("2. Sort by Size")
    print("3. Sort by Date modified")
    sort_by = input("Choose your default sorting method: ")
    write_settings(sort_by)
    print("Settings updated.")
def get_sorting_preference():
    print("Choose sorting criteria:")
    print("1. Name")
    print("2. Size")
    print("3. Date modified")
    choice = input("Enter the number of your choice: ")
    return choice


def sort_files(files_and_folders, sort_by):
    if sort_by == "1":
        # Sort by name
        files_and_folders.sort(key=lambda x: x.name.lower())
    elif sort_by == "2":
        # Sort by size (folders will be listed first)
        files_and_folders.sort(key=lambda x: x.size if isinstance(x, dropbox.files.FileMetadata) else -1, reverse=True)
    elif sort_by == "3":
        # Sort by date modified
        files_and_folders.sort(key=lambda x: x.server_modified if isinstance(x, dropbox.files.FileMetadata) else datetime.min, reverse=True)
    return files_and_folders


def upload_file(local_path):
    dropbox_path = '/Users/isaacschool/Library/CloudStorage/Dropbox/' + os.path.basename(local_path)
    try:
        with open(local_path, 'rb') as f:
            dbx.files_upload(f.read(), dropbox_path, mode=dropbox.files.WriteMode('overwrite'))
            print("File uploaded successfully.")
    except dropbox.exceptions.ApiError as err:
        print(f"API error: {err}")


def get_predefined_path(option):
    home_path = os.path.expanduser('~')  # Gets the home directory path in macOS format
    if option == '1':
        return os.path.join(home_path, 'Documents')
    elif option == '2':
        return os.path.join(home_path, 'Desktop')
    elif option == '3':
        return input("Enter the custom local path where you want to save the file: ")
    else:
        return None

def download_file_with_progress(selected_item, local_file_path):
    with open(local_file_path, "wb") as f:
        md, res = dbx.files_download(selected_item.path_lower)
        file_size = int(res.headers.get('content-length', 0))
        chunk_size = 4096
        downloaded = 0

        for chunk in res.iter_content(chunk_size=chunk_size):
            # Write the chunk to the local file
            if chunk:
                downloaded += len(chunk)
                f.write(chunk)
                done = int(50 * downloaded / file_size)
                downloaded_str = convert_size(downloaded)
                file_size_str = convert_size(file_size)
                sys.stdout.write(f"\r[{'█' * done}{'.' * (50-done)}] {downloaded_str}/{file_size_str}")
                sys.stdout.flush()
        print("\nFile downloaded successfully.")  # Newline after download completes

def convert_size(size_bytes):
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"

def list_files_and_select(path):
    try:
        files_and_folders = dbx.files_list_folder(path).entries
        if not files_and_folders:
            print("No files or folders found.")
            return
        sort_by = get_sorting_preference()
        sorted_files_and_folders = sort_files(files_and_folders, sort_by)

        print("Contents:")
        for i, entry in enumerate(files_and_folders):
            if isinstance(entry, dropbox.files.FileMetadata):
                file_size = entry.size  # Get the file size from the metadata
                size_str = f"({convert_size(file_size)})"
            else:
                size_str = "(Folder)"
            print(f"{i + 1}. {entry.name} {size_str}")


        # Ask the user to select a file or folder
        selection_index = int(input("Enter the number to open a file or dive into a folder: ")) - 1

        # Validate user input
        if selection_index < 0 or selection_index >= len(files_and_folders):
            print("Invalid selection.")
            return

        # Get the selected item
        selected_item = files_and_folders[selection_index]

        # If it's a folder, dive into it
        if isinstance(selected_item, dropbox.files.FolderMetadata):
            print(f"Entering folder: {selected_item.name}")
            list_files_and_select(selected_item.path_lower)  # Recursive call with the new folder path
        else:
            print("Choose download location:")
            print("1. Documents")
            print("2. Desktop")
            print("3. Custom")
            location_option = input("Select an option (1-3): ")
            local_path = get_predefined_path(location_option)

            if not local_path:
                print("Invalid selection.")
                return

            if not os.path.exists(local_path):
                os.makedirs(local_path)

            local_file_path = os.path.join(local_path, selected_item.name)
            print(f"Downloading {selected_item.name} to {local_file_path}...")

            download_file_with_progress(selected_item, local_file_path)
            print(f"File downloaded successfully to {local_file_path}")

    except dropbox.exceptions.ApiError as err:
        print(f"API error: {err}")



def main_menu():
    while True:
        print("Main Menu:")
        print("1. List Files and Folders")
        print("2. Settings")
        print("3. Upload File")
        choice = input("Enter your choice: ")

        if choice == "1":
            sort_by = read_settings()
            # Call the function to list files and folders using the sort_by setting
            # list_files_and_select(path, sort_by)
            list_files_and_select('')
            list
        elif choice == "2":
            settings_menu()
        elif choice == "3":
            upload
        else:
            print("Invalid choice, please try again.")

main_menu()

