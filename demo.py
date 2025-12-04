import os
from PIL import Image, ImageStat

image_folder = '/home/udara/Data/projects/personal/python/images3'
image_files = [_ for _ in os.listdir(image_folder) if _.endswith('.jpg')]

duplicate_files = []

for file_org in image_files:
    if not file_org in duplicate_files:
        image_org = Image.open(os.path.join(image_folder, file_org))
        pix_mean1 = ImageStat.Stat(image_org).mean

        for file_check in image_files:
            if file_check !=file_org:
                image_check = Image.open(os.path.join(image_folder, file_check))
                pix_mean2 = ImageStat.Stat(image_check).mean

                if pix_mean1 == pix_mean2:
                    duplicate_files.append(file_org)
                    duplicate_files.append(file_check)

print(duplicate_files)