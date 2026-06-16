import logging
import os
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


IMAGE_EXTENSIONS = (
    '.bmp', '.dib', '.png', '.jpg', '.jpeg',
    '.pbm', '.pgm', '.ppm', '.tif', '.tiff',
)


def del_dir_byname(path):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
            logger.info("文件夹已删除！ %s", path)
        except OSError as e:
            logger.error("删除文件夹失败 %s: %s", path, e)
            raise
    else:
        logger.info("文件夹不存在！ %s", path)


def ensure_clean_dir(path):
    del_dir_byname(path)
    try:
        os.makedirs(path)
    except OSError as e:
        logger.error("创建文件夹失败 %s: %s", path, e)
        raise
    return path


def check_file_extension(file_name, extensions):
    ext = os.path.splitext(file_name)[1].lower()
    return ext in extensions


def check_markdown(file_name):
    return check_file_extension(file_name, ('.md',))


def check_pdf(file_name):
    return check_file_extension(file_name, ('.pdf',))


def check_image(file_name):
    return check_file_extension(file_name, IMAGE_EXTENSIONS)
