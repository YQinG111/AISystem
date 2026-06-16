import argparse
import logging
import os

from PIL import Image

from utils import check_image, ensure_clean_dir

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def apply_watermark(source_folder, output_folder, watermark_path):
    try:
        watermark = Image.open(watermark_path).convert("RGBA")
    except (IOError, OSError) as e:
        logger.error("无法打开水印图片 %s: %s", watermark_path, e)
        raise
    watermark_width, watermark_height = watermark.size

    ensure_clean_dir(output_folder)

    try:
        filenames = os.listdir(source_folder)
    except OSError as e:
        logger.error("无法列出源目录 %s: %s", source_folder, e)
        raise

    for filename in filenames:
        if not check_image(filename):
            logger.warning("CANNOT deal with images: %s", filename)
            continue

        logger.info("dealing with images: %s", filename)
        image_path = os.path.join(source_folder, filename)
        try:
            image = Image.open(image_path).convert("RGBA")
        except (IOError, OSError) as e:
            logger.error("无法打开图片 %s: %s", image_path, e)
            continue

        resized = image

        margin = 10
        baise_width = 1080
        src_width, src_height = image.size
        resized_width, resized_height = image.size

        # resize images
        if src_width > baise_width:
            resized_width = baise_width
            resized_height = int(baise_width/src_width * src_height)
            resized = image.resize((resized_width, resized_height))

        # watermark images
        src_width, src_height = resized_width, resized_height
        w_ration = watermark_height/watermark_width
        new_watermark_width = int(src_width/5)
        new_watermark_hight = int(src_width/5 * w_ration)
        watermark_x = src_width - new_watermark_width - margin
        watermark_y = src_height - new_watermark_hight - margin
        new_watermark = watermark.resize((new_watermark_width, new_watermark_hight))
        resized.paste(new_watermark, (watermark_x, watermark_y), new_watermark)

        # output images
        out_name = filename.split(".")[0] + ".png"
        logger.info("Outputing images name: %s", out_name)
        output_path = os.path.join(output_folder, out_name)
        try:
            resized.save(output_path, quality=100)
        except (IOError, OSError) as e:
            logger.error("保存图片失败 %s: %s", output_path, e)
            continue


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

    try:
        apply_watermark(source_folder, output_folder, watermark_path)
    except Exception as e:
        logger.error("水印处理失败: %s", e)
        raise SystemExit(1) from e
