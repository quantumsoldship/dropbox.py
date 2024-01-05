token = "YOUR ACCESS TOKEN HERE"
# Get one at https://www.dropbox.com/developers/apps/create
import dropbox
import os
import sys

# Initialize a Dropbox object using your access token
dbx = dropbox.Dropbox(token)
def main_menu():

    print("1. List files and download")
    print("2. Upload a file to Dropbox")
    choice = input("Select an option (1-2): ")
    if choice == '1':
        list_files_and_select('')
    elif choice == '2':
        local_file_path = input("Enter the local file path to upload: ")
        upload_file(local_file_path)
    else:
        print("Invalid selection. Please try again.")


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
                sys.stdout.write("\r[{}{}] {}%".format('█' * done, '.' * (50-done), 2 * done))
                sys.stdout.flush()
        print()  # Newline after download completes

def list_files_and_select(path):
    try:
        files_and_folders = dbx.files_list_folder(path).entries
        if not files_and_folders:
            print("No files or folders found.")
            return

        print("Contents:")
        for i, entry in enumerate(files_and_folders):
            entry_type = '(Folder)' if isinstance(entry, dropbox.files.FolderMetadata) else '(File)'
            print(f"{i + 1}. {entry.name} {entry_type}")

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

# Start by listing the contents of the root directory
main_menu()

