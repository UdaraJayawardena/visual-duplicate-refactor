import os
from PIL import Image
import hashlib
import json

# Configuration
# Define the project's base path once for cleaner structure
BASE_PATH = '/home/udara/Data/projects/personal/python/visual_duplicate_refactor'
# BASE_PATH = 'google-drive://daredefy47@gmail.com/0AEM4-UGXnv5_Uk9PVA/1CfMdwzWfi1zseYIEkvMiAvYE_gOsB8Iw/'

# Build the specific folder paths relative to the base path
image_folder = os.path.join(BASE_PATH, 'images')
output_folder = os.path.join(BASE_PATH, 'output')

# Define the file extensions you care about
ALLOWED_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.gif')

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
        
else:
    # If no duplicates are found, this message is printed, and no JSON file is created.
    print("No exact pixel duplicates found. JSON file skipped.")