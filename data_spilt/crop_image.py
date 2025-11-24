import os
from PIL import Image


def crop_and_save_images(input_dir, output_dir, txt_file_path):
    """
    To find RGB and nDSM image pairs, first remove the black borders, then crop to 1024x1024 with a 256-pixel overlap,and write the paired filenames to a text file.
    """
    # Ensure the output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Find all RGB images as the starting point for processing
    rgb_files = [f for f in os.listdir(input_dir) if f.endswith('_RGB.tif')]

    txt_lines = []
    print(f"Start scanning: {input_dir}")

    for rgb_filename in rgb_files:
        ndsm_filename = rgb_filename.replace('_RGB.tif', '_nDSM.tif')
        rgb_path = os.path.join(input_dir, rgb_filename)
        ndsm_path = os.path.join(input_dir, ndsm_filename)

        if os.path.exists(ndsm_path):
            try:
                rgb_img_original = Image.open(rgb_path)
                ndsm_img_original = Image.open(ndsm_path)

                bbox = rgb_img_original.getbbox()

                        # If bbox is None, the entire image is black, skip processing
                if not bbox:
                    print(f"Warning: Image {rgb_filename} is empty (all black), skipped.")
                    continue

                # Crop RGB and nDSM images based on the bounding box to ensure alignment
                rgb_img_cropped = rgb_img_original.crop(bbox)
                ndsm_img_cropped = ndsm_img_original.crop(bbox)

                # Use the new size of the cropped images for subsequent operations
                img_width, img_height = rgb_img_cropped.size

                # Define cropping parameters
                tile_size = 1024
                overlap = 256
                stride = tile_size - overlap

                # Safety check: if the image size after removing black borders is smaller than the tile size, slicing is not possible
                if img_width < tile_size or img_height < tile_size:
                    print(
                        f"Warning: After removing black borders, the size of image {rgb_filename} ({img_width}x{img_height}) is smaller than the tile size {tile_size}x{tile_size}, skipped.")
                    continue

                print(f"Processing image pair: {rgb_filename} (Effective area: {img_width}x{img_height})")

                # Perform exactly the same slicing operation on the two images with black borders removed
                for i in range(0, img_width - tile_size + 1, stride):
                    for j in range(0, img_height - tile_size + 1, stride):
                        box = (i, j, i + tile_size, j + tile_size)

                        rgb_tile = rgb_img_cropped.crop(box)
                        ndsm_tile = ndsm_img_cropped.crop(box)

                        rgb_base_name = os.path.splitext(rgb_filename)[0]
                        ndsm_base_name = os.path.splitext(ndsm_filename)[0]

                        output_rgb_filename = f"{rgb_base_name}_tile_{i}_{j}.tif"
                        output_ndsm_filename = f"{ndsm_base_name}_tile_{i}_{j}.tif"

                        output_rgb_path = os.path.join(output_dir, output_rgb_filename)
                        output_ndsm_path = os.path.join(output_dir, output_ndsm_filename)

                        rgb_tile.save(output_rgb_path)
                        ndsm_tile.save(output_ndsm_path)

                        txt_lines.append(f"{output_rgb_filename} {output_ndsm_filename}\n")

            except Exception as e:
                print(f"Error processing image pair {rgb_filename}: {e}")
        else:
            print(f"Warning: Matching nDSM file not found for {rgb_filename}.")

    # Write all pairing information to the txt file at once
    if txt_lines:
        with open(txt_file_path, 'w') as f:
            f.writelines(txt_lines)
        print(f"Successfully processed directory {input_dir} and generated {txt_file_path}")
    else:
        print(f"No slices were generated in directory {input_dir}.")


if __name__ == '__main__':
    # --- Please modify the following variables according to your actual paths ---
    # Original data paths
    train_data_path = '/media/wgy/Marigold/Marigold-main/data/SN5/train'
    test_data_path = '/media/wgy/Marigold/Marigold-main/data/SN5/test'

    # Paths to save cropped images
    output_images_path = '/media/wgy/Marigold/Marigold-main/data/spacenet5'

    # Paths to save generated txt files
    train_txt_path = '/media/wgy/Marigold/Marigold-main/data_split/spacenet5/file_list_train.txt'
    test_txt_path = '/media/wgy/Marigold/Marigold-main/data_split/spacenet5/file_list_test.txt'

    # --- Execute cropping and file generation ---

    print("Starting to process training data...")
    crop_and_save_images(train_data_path, output_images_path, train_txt_path)

    print("\nStarting to process testing data...")
    crop_and_save_images(test_data_path, output_images_path, test_txt_path)

    print("\nAll processing completed!")