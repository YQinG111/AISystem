# 适用于[License] (https://github.com/chenzomi12/AISystem/blob/main/LICENSE)版权许可

import logging
import os
import shutil

from utils import del_dir_byname, check_markdown, check_pdf

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


TEMP = """
```{toctree}
:maxdepth: 1

"""


def create_dir(path, name):
	new_path = os.path.join(path, name)
	del_dir_byname(new_path)
	if "images" in name:
		return None

	try:
		os.makedirs(new_path)
	except OSError as e:
		logger.error("创建文件夹失败 %s: %s", new_path, e)
		raise
	return new_path


def copystrtodir(path1, path2, rename):
	new_path2 = os.path.join(path2, rename)
	del_dir_byname(path2)
	del_dir_byname(new_path2)
	try:
		shutil.copytree(path1, new_path2)
	except OSError as e:
		logger.error("复制目录失败 %s -> %s: %s", path1, new_path2, e)
		raise


def add2readme(file_path, string):
	if file_path.split('/')[-1] == 'README.md':
		try:
			with open(file_path, encoding="utf-8", mode="a") as file:  
				file.write(string)
		except IOError as e:
			logger.error("写入 README 失败 %s: %s", file_path, e)
			raise


def change_iamgepath_markdown(file_path):
	"""
	change ![ENIAC01](images/01CPUBase01.png)
	to ![ENIAC01](../images/02Hardware02ChipBase/01CPUBase01.png)

	"""
	search_text = "images/"
	replace_text = "../images/" + file_path.split('/')[-2] + "/"
	logger.info("替换图片路径: %s -> %s in %s", search_text, replace_text, file_path)

	try:
		with open(file_path, 'r', encoding='UTF-8') as file:
			data = file.read()
			data = data.replace(search_text, replace_text)
	except IOError as e:
		logger.error("读取文件失败 %s: %s", file_path, e)
		raise

	try:
		with open(file_path, 'w', encoding='UTF-8') as file:
			file.write(data)
	except IOError as e:
		logger.error("写入文件失败 %s: %s", file_path, e)
		raise


def get_subfile(path, dir_path):
	try:
		file_path = os.listdir(path)
	except OSError as e:
		logger.error("无法列出目录 %s: %s", path, e)
		raise

	target_filenames = []
	target_pdf_filenames = []
	temp = TEMP
	file_path.sort()
	image_name = '/images/' + dir_path.split('/')[-1]
	save_name = dir_path.split('/')[:-1]
	save_path = '/'.join(save_name) + image_name
	## 找到所有的 md 并记录下来
	for file in file_path:
		fp = os.path.join(path, file)
		if os.path.isfile(fp) and check_markdown(fp):
			logger.info("dealing with MD: %s", fp)
			target_filenames.append(fp)

			if fp.split('/')[-1] == 'README.md':
				continue
			
			temp += fp.split('/')[-1][:-3]
			temp += "\n"
		
		# 移动 images 目录到外层
		elif os.path.isdir(fp) and fp.split('/')[-1] == "images":
			try:
				shutil.copytree(fp, save_path, dirs_exist_ok = True)
			except OSError as e:
				logger.error("复制 images 目录失败 %s -> %s: %s", fp, save_path, e)
				raise
	temp += "```"

	## 找到所有的 pdf 并记录下来
	for file in file_path:
		fp = os.path.join(path, file)
		if os.path.isfile(fp) and check_pdf(fp):
			logger.info("dealing with PDF: %s", fp)
			target_pdf_filenames.append(fp)

	## 迁移文件到新的地方
	logger.info("now we are going to move MD: %s", target_filenames)
	for filename in target_filenames:
		try:
			shutil.copy(filename, dir_path)
		except OSError as e:
			logger.error("复制文件失败 %s -> %s: %s", filename, dir_path, e)
			raise

	# 修改 markdown 里面的图片地址
	## 写 readme
	logger.info("write temp to readme...")
	file_path = os.listdir(dir_path)
	for file in file_path:
		fp = os.path.join(dir_path, file)
		add2readme(fp, temp)
		change_iamgepath_markdown(fp)

	logger.info("now we are going to move PDF: %s", target_pdf_filenames)
	for filename in target_pdf_filenames:
		try:
			shutil.copy(filename, dir_path)
		except OSError as e:
			logger.error("复制 PDF 失败 %s -> %s: %s", filename, dir_path, e)
			raise

	return target_filenames


def getallfile(path):
	try:
		file_path = os.listdir(path)
	except OSError as e:
		logger.error("无法列出目录 %s: %s", path, e)
		raise

	# 遍历该文件夹下的所有目录或者文件
	for file in file_path:
		fp = os.path.join(path, file)
		if os.path.isdir(fp) and fp.split('/')[-1] != "images":
			file_dist = fp.split('/')
			new_dir_name = ''.join(file_dist[-2:])
			new_path = create_dir(dir_paths, new_dir_name)
			if new_path:
				get_subfile(fp, new_path)
		
		elif os.path.isdir(fp) and fp.split('/')[-1] == "images":
			file_dist = fp.split('/')
			save_path = dir_paths +"images/"+ file_dist[-2]+"/"
			try:
				os.makedirs(save_path, exist_ok=True)
				shutil.copytree(fp, save_path, dirs_exist_ok = True)
			except OSError as e:
				logger.error("复制 images 目录失败 %s -> %s: %s", fp, save_path, e)
				raise
		elif os.path.isfile(fp):
			# 遍历 md 文件，并复制到指定目录
			if check_markdown(fp):
				new_dir_name = fp.split('/')[-2]
				logger.info("fp: %s %s %s", fp, new_dir_name, fp)
				new_path = dir_paths+"/"+new_dir_name
				try:
					os.makedirs(new_path, exist_ok=True)
					shutil.copy(fp, new_path)
				except OSError as e:
					logger.error("复制 markdown 失败 %s -> %s: %s", fp, new_path, e)
					raise
				# 修改image目录
				change_iamgepath_markdown(new_path+"/"+os.path.basename(fp))


if __name__ == "__main__":
	import argparse

	REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

	parser = argparse.ArgumentParser(description="Create directory structure for AISystem book.")
	parser.add_argument(
		"--repo-root", default=REPO_ROOT,
		help="Root of the AISystem repo (default: auto-detected).",
	)
	parser.add_argument(
		"--output-dir", default=None,
		help="Output source directory (default: <repo-root>_BOOK/source/).",
	)
	args = parser.parse_args()

	repo_root = args.repo_root
	dir_paths = args.output_dir or os.path.join(repo_root + "_BOOK", "source", "")

	target_dirs = [
		os.path.join(repo_root, "01Introduction"),
		os.path.join(repo_root, "02Hardware"),
		os.path.join(repo_root, "03Compiler"),
		os.path.join(repo_root, "04Inference"),
		os.path.join(repo_root, "05Framework"),
	]

	for target_dir in target_dirs:
		try:
			getallfile(target_dir)
		except Exception as e:
			logger.error("处理目录失败 %s: %s", target_dir, e)
			raise SystemExit(1) from e
