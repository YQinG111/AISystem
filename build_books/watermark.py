import argparse
import os
import shutil
from PIL import Image, ImageDraw, ImageFont, ImageEnhance

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def check_image(img_path):
    if(img_path.lower().endswith(('.bmp', '.dib', '.png', '.jpg', '.jpeg', '.pbm', '.pgm', '.ppm', '.tif', '.tiff'))):
        return True
    else:
        return False

def del_dir_byname(path):
	if os.path.exists(path):
		shutil.rmtree(path)
		print("文件夹已删除！", path)
	else:
		print("文件夹不存在！", path)


def create_dir(path):
	del_dir_byname(path)
	os.makedirs(path)
	return path


def apply_watermark(source_folder, output_folder, watermark_path):
    watermark = Image.open(watermark_path).convert("RGBA")
    watermark_width, watermark_height = watermark.size

    create_dir(output_folder)
    for filename in os.listdir(source_folder):
        if check_image(filename):
            print("dealing with images:" + filename)
            image_path = os.path.join(source_folder, filename)
            image = Image.open(image_path).convert("RGBA")
            resized = image

            margin = 10
            baise_width = 1080
            src_width, src_height = image.size
            resized_width, resized_height = image.size

            if src_width > baise_width:
                resized_width = baise_width
                resized_height = int(baise_width/src_width * src_height)
                resized = image.resize((resized_width, resized_height))

            src_width, src_height = resized_width, resized_height
            w_ration = watermark_height/watermark_width
            new_watermark_width = int(src_width/5)
            new_watermark_hight = int(src_width/5 * w_ration)
            watermark_x = src_width - new_watermark_width - margin
            watermark_y = src_height - new_watermark_hight - margin
            new_watermark = watermark.resize((new_watermark_width, new_watermark_hight))
            resized.paste(new_watermark, (watermark_x, watermark_y), new_watermark)

            out_name = filename.split(".")[0] + ".png"
            print("Outputing images name:", out_name)
            output_path = os.path.join(output_folder, out_name)
            resized.save(output_path, quality=100)
        else:
            print("CANNOT dealing images:" + filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Apply watermark to images.")
    parser.add_argument(
        "--repo-root", default=REPO_ROOT,
        help="Root of the AISystem repo (default: auto-detected).",
    )
    args = parser.parse_args()

    watermark_path = os.path.join(args.repo_root, "images", "watermark.png")
    source_folder = os.path.join(args.repo_root, "images")
    output_folder = os.path.join(args.repo_root, "watermark")

    apply_watermark(source_folder, output_folder, watermark_path)