import os
from PIL import Image
import hashlib
import json
import shutil

# Configuration
# Define the project's base path once for cleaner structure
# BASE_PATH = '/home/udara/Data/projects/personal/python/visual_duplicate_refactor'
# BASE_PATH = 'google-drive://daredefy47@gmail.com/0AEM4-UGXnv5_Uk9PVA/1CfMdwzWfi1zseYIEkvMiAvYE_gOsB8Iw/'
BASE_PATH = '/home/udara/Data/software_projects/personal/python/visual-duplicate-refactor/'

# Build the specific folder paths relative to the base path
# image_folder = BASE_PATH
image_folder = os.path.join(BASE_PATH, 'images')
output_folder = os.path.join(BASE_PATH, 'output')
duplicates_folder = os.path.join(BASE_PATH, 'images/duplicates')

# Define the file extensions you care about
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')

# If True, every file in each duplicate group gets moved into
# duplicates_folder (none are kept behind in image_folder).
MOVE_DUPLICATES = True

# --- Helper Function for Hashing ---
def get_image_hash(filepath):
    """
    Calculates a hash for an image's pixel data.
    This is the method used to determine visual content similarity.
    """
    try:
        img = Image.open(filepath)
        # Convert to RGB to standardize the format, ensuring cross-format comparison (JPG vs PNG)
        img_data = img.convert("RGB").tobytes()
        return hashlib.sha1(img_data).hexdigest()
    except Exception as e:
        print(f"Error processing {filepath}: {e}")
        return None

# --- Main Logic ---
# {hash_value: [list of filepaths with that hash]}
hash_map = {}
# This list will ONLY store groups that have duplicate files (count > 1)
duplicate_groups_data = []

# Ensure the output directory exists
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 1. Get all relevant image files
image_files = [f for f in os.listdir(image_folder) 
               if f.lower().endswith(ALLOWED_EXTENSIONS) and os.path.isfile(os.path.join(image_folder, f))]

print(f"Found {len(image_files)} potential images to check...")

# 2. Iterate through files, calculate hash, and map it
for filename in image_files:
    filepath = os.path.join(image_folder, filename)
    file_hash = get_image_hash(filepath)

    if file_hash:
        if file_hash in hash_map:
            hash_map[file_hash].append(filepath)
        else:
            hash_map[file_hash] = [filepath]

# 3. Collect ONLY duplicate file groups (count > 1)
# We now iterate over the entire hash_map and filter down to duplicate groups.
for file_hash, file_list in hash_map.items():
    # --- FILTER APPLIED HERE: Only proceed if there are 2 or more files with the same hash ---
    if len(file_list) > 1: 
        # Create a dictionary for the group
        group_entry = {
            "group_id": file_hash,
            # Store file names (basename)
            "files": [os.path.basename(f) for f in file_list], 
            "count": len(file_list)
        }
        duplicate_groups_data.append(group_entry)


## --- Output and JSON Saving ---
print("\n--- Duplicate Image Analysis ---")

if duplicate_groups_data:
    total_duplicate_files = sum(group['count'] - 1 for group in duplicate_groups_data)
    
    print(f"Found {len(duplicate_groups_data)} groups containing a total of {total_duplicate_files} redundant files.")
    print("--------------------------------------")
        
    # Print a summary of the duplicate groups to the console
    for i, group in enumerate(duplicate_groups_data):
        print(f"\nDUPLICATE Group {i+1} (Count: {group['count']}):")
        print(f"  Hash ID (first 8 chars): {group['group_id'][:8]}")
        for file in group['files']:
            print(f"    - {file}")
            
    # Save the structured list containing ONLY the duplicate groups to results.json
    results_filepath = os.path.join(output_folder, 'results.json')
    try:
        with open(results_filepath, 'w') as f:
            # Save the list of structured dictionaries
            json.dump(duplicate_groups_data, f, indent=4)
        print(f"\n✅ Successfully saved {len(duplicate_groups_data)} duplicate groups to: {results_filepath}")
    except Exception as e:
        print(f"\n❌ Error saving JSON file: {e}")

    # --- Move ALL files in every duplicate group to duplicates_folder ---
    if MOVE_DUPLICATES:
        if not os.path.exists(duplicates_folder):
            os.makedirs(duplicates_folder)

        moved_count = 0
        print("\n--- Moving Duplicate Files ---")

        for group in duplicate_groups_data:
            files = group['files']
            # Move every file in the group (none are kept behind)
            files_to_move = files

            for filename in files_to_move:
                src_path = os.path.join(image_folder, filename)
                dest_path = os.path.join(duplicates_folder, filename)

                # Avoid overwriting if a file with the same name already exists
                # in the duplicates folder (e.g. from a previous run)
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        dest_path = os.path.join(duplicates_folder, f"{base}_{counter}{ext}")
                        counter += 1

                try:
                    shutil.move(src_path, dest_path)
                    print(f"  Moved: {filename} -> {os.path.basename(dest_path)}")
                    moved_count += 1
                except Exception as e:
                    print(f"  ❌ Error moving {filename}: {e}")

        print(f"\n✅ Moved {moved_count} duplicate file(s) to: {duplicates_folder}")
        print(f"   (All files in each duplicate group were moved — none kept in: {image_folder})")

else:
    # If no duplicates are found, this message is printed, and no JSON file is created.
    print("No exact pixel duplicates found. JSON file skipped.")
