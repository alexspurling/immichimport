import os

# Go through all the untitled folders and find the date of the images or videos

photos_dir = "/home/alex/Downloads/Takeout/Google Photos/"
untitled_dir = "/home/alex/Downloads/Takeout/Google Photos/Untitled"

os.makedirs(untitled_dir, exist_ok=True)

for file in os.listdir(photos_dir):
    if file.startswith("Untitled"):
        file_path = os.path.join(photos_dir, file)
        for untitled_file in os.listdir(file_path):
            untitled_file_path = os.path.join(file_path, untitled_file)
            if not untitled_file.endswith(".json"):
                new_file_path = os.path.join(untitled_dir, untitled_file)
                print("Moving", untitled_file_path, "to", new_file_path)
                os.rename(untitled_file_path, new_file_path)






