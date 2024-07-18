import os

photos_dir = "/home/alex/Downloads/Takeout/Google Photos/"
bin_dir = "/home/alex/Downloads/Takeout/ToDelete/"

os.makedirs(bin_dir, exist_ok=True)

file_map = {}

total_files = 0
duplicate_files = 0
moved_files = 0


def move_to_bin(src_file, dest_file):
    print("Moving", src_file, "to", dest_file)
    try:
        os.rename(src_file, dest_file)
    except FileNotFoundError:
        print("Warning: file not found: ", src_file)
    global moved_files
    moved_files += 1


for root, dirs, files in os.walk(photos_dir):
    for file_name in files:
        if file_name.endswith(".json"):
            continue
        file_path = os.path.join(root, file_name)
        size = os.path.getsize(file_path)

        total_files += 1

        if (file_name, size) in file_map:
            duplicate_path = file_map[(file_name, size)]
            print(file_path, duplicate_path)
            duplicate_files += 1

            if "/Untitled/" in file_path:
                move_to_bin(file_path, os.path.join(bin_dir, file_name))
            elif "/Untitled/" in duplicate_path:
                move_to_bin(duplicate_path, os.path.join(bin_dir, file_name))
            elif "/Photos from 20" in file_path:
                move_to_bin(file_path, os.path.join(bin_dir, file_name))
            elif "/Photos from 20" in duplicate_path:
                move_to_bin(duplicate_path, os.path.join(bin_dir, file_name))
            elif "/Trip to " in file_path:
                move_to_bin(file_path, os.path.join(bin_dir, file_name))
            elif "/Trip to " in duplicate_path:
                move_to_bin(duplicate_path, os.path.join(bin_dir, file_name))
            elif "/Weekend in England/" in file_path:
                move_to_bin(file_path, os.path.join(bin_dir, file_name))
            elif "/Weekend in England/" in duplicate_path:
                move_to_bin(duplicate_path, os.path.join(bin_dir, file_name))

        else:
            file_map[(file_name, size)] = file_path


print("Found", duplicate_files, "out of", total_files, "duplicates. Moved", moved_files, "files to bin.")

