import os

def rename_pictures(folder_path):
    # Check if the given path is a directory
    if not os.path.isdir(folder_path):
        print(f"Error: Not a valid directory - {folder_path}")
        return

    # Get a list of all files in the directory
    files = os.listdir(folder_path)

    # Filter out non-image files (you may customize this based on your file types)
    image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    # Sort the image files for consistent renaming
    image_files.sort()

    # Rename each file with a series starting from '0001'
    for i, old_name in enumerate(image_files, start=1):
        extension = os.path.splitext(old_name)[1].lower()
        new_name = f"{i:04d}{extension}"
        old_path = os.path.join(folder_path, old_name)
        new_path = os.path.join(folder_path, new_name)

        # Rename the file
        os.rename(old_path, new_path)

        print(f"Renamed: {old_name} -> {new_name}")

if __name__ == "__main__":
    # Replace 'your_folder_path' with the path to your folder of pictures
    folder_path = r'D:\yolov8-gpu\UWDK_Pose\Data'

    # Call the function to rename the pictures
    rename_pictures(folder_path)