import os
from PIL import Image


def crop_and_save_images(input_dir, output_dir, txt_file_path):
    """
    查找RGB和nDSM图像对，首先去除黑边，然后以256像素重叠度进行1024x1024的裁剪，
    并将配对的文件名写入txt文件。

    参数:
    input_dir (str): 输入图像的目录 (e.g., 'path/to/your/train').
    output_dir (str): 所有裁剪后图像的统一保存目录。
    txt_file_path (str): 生成的txt文件的路径 (e.g., 'path/to/your/train.txt').
    """
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 查找所有RGB图像作为处理的起点
    rgb_files = [f for f in os.listdir(input_dir) if f.endswith('_RGB.tif')]

    # 用于存储将要写入txt文件的所有行
    txt_lines = []
    print(f"开始扫描目录: {input_dir}")

    for rgb_filename in rgb_files:
        ndsm_filename = rgb_filename.replace('_RGB.tif', '_nDSM.tif')
        rgb_path = os.path.join(input_dir, rgb_filename)
        ndsm_path = os.path.join(input_dir, ndsm_filename)

        if os.path.exists(ndsm_path):
            try:
                rgb_img_original = Image.open(rgb_path)
                ndsm_img_original = Image.open(ndsm_path)

                # --- 新增代码开始: 移除黑边 ---
                # 使用RGB图像来获取有效内容的边界框 (bounding box)
                bbox = rgb_img_original.getbbox()

                # 如果bbox为None，说明整个图像是纯黑的，跳过处理
                if not bbox:
                    print(f"警告: 图像 {rgb_filename} 是空的 (全黑)，已跳过。")
                    continue

                # 根据边界框裁剪RGB和nDSM图像，确保它们保持对齐
                rgb_img_cropped = rgb_img_original.crop(bbox)
                ndsm_img_cropped = ndsm_img_original.crop(bbox)
                # --- 新增代码结束 ---

                # 使用裁剪后图像的新尺寸进行后续操作
                img_width, img_height = rgb_img_cropped.size

                # 定义裁剪参数
                tile_size = 1024
                overlap = 256
                stride = tile_size - overlap

                # 安全检查：如果裁剪黑边后的图像尺寸小于切片尺寸，则无法切片
                if img_width < tile_size or img_height < tile_size:
                    print(
                        f"警告: 移除黑边后，图像 {rgb_filename} 的尺寸 ({img_width}x{img_height}) 小于切片尺寸 {tile_size}x{tile_size}，已跳过。")
                    continue

                print(f"正在处理图像对: {rgb_filename} (有效区域: {img_width}x{img_height})")

                # 在两个已裁剪掉黑边的图像上执行完全相同的切片操作
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
                print(f"处理图像对 {rgb_filename} 时出错: {e}")
        else:
            print(f"警告: 找不到与 {rgb_filename} 匹配的nDSM文件。")

    # 将所有配对信息一次性写入txt文件
    if txt_lines:
        with open(txt_file_path, 'w') as f:
            f.writelines(txt_lines)
        print(f"成功处理目录 {input_dir} 并生成 {txt_file_path}")
    else:
        print(f"在目录 {input_dir} 中没有生成任何切片。")

    #             # 定义裁剪的步长
    #             tile_size = 512
    #
    #             # 裁剪图像
    #             for i in range(0, img_width, tile_size):
    #                 for j in range(0, img_height, tile_size):
    #                     # 定义裁剪框
    #                     box = (i, j, i + tile_size, j + tile_size)
    #                     tile = img.crop(box)
    #
    #                     # 构建输出文件名
    #                     base_filename = os.path.splitext(filename)[0]
    #                     output_filename = f"{base_filename}_tile_{i}_{j}.tif"
    #                     output_path = os.path.join(output_dir, output_filename)
    #
    #                     # 保存裁剪后的图像
    #                     tile.save(output_path)
    #
    #                     # 将裁剪后图像的路径写入txt文件
    #                     f.write(output_path + '\n')
    #
    #         except Exception as e:
    #             print(f"处理图像 {filename} 时出错: {e}")
    #
    # print(f"成功处理目录 {input_dir} 并生成 {txt_file_path}")


if __name__ == '__main__':
    # --- 请根据您的实际路径修改以下变量 ---

    # 原始数据路径
    train_data_path = '/media/wgy/Marigold/Marigold-main/data/SN5/train'
    test_data_path = '/media/wgy/Marigold/Marigold-main/data/SN5/test'

    # 裁剪后图像的保存路径
    output_images_path = '/media/wgy/Marigold/Marigold-main/data/spacenet5'

    # 生成的txt文件的保存路径
    train_txt_path = '/media/wgy/Marigold/Marigold-main/data_split/spacenet5/train.txt'
    test_txt_path = '/media/wgy/Marigold/Marigold-main/data_split/spacenet5/test.txt'

    # --- 执行裁剪和文件生成 ---

    print("开始处理训练数据...")
    crop_and_save_images(train_data_path, output_images_path, train_txt_path)

    print("\n开始处理测试数据...")
    crop_and_save_images(test_data_path, output_images_path, test_txt_path)

    print("\n所有处理完成！")