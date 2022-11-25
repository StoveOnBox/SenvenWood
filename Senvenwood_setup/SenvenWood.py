import os
import time

from tqdm import tqdm

from update import update, local_json, check_exists
from uzip import uncompress

update()
content = local_json("update.json")
oldname = content["name"]
# if check_exists(oldname):
#     print("")
# else:
#     os.popen(f"mkdir {oldname}")

dest_dir = f"./{oldname}"
if check_exists(f"{oldname}.zip"):
    with open(f"{oldname}.zip", 'rb') as src_file:
        result = uncompress(src_file, dest_dir)

        for i in tqdm(range(100), desc='解压中'):
            time.sleep(0.5)
        print("解压完成,一切准备就绪")

if check_exists(oldname + ".zip"):
    os.remove(oldname + ".zip")
    print("已删除压缩包")
print("启动游戏,玩得愉快")

os.popen("./Plain Craft Launcher 2")
input("输入任意字符以结束")
