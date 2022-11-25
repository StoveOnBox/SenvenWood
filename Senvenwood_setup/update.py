# coding=utf-8
import json
import os
import re
import shutil
import sys
import time
from os import path, rename
from urllib.request import urlretrieve

import requests
from tqdm import tqdm

self_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:107.0) Gecko/20100101 Firefox/107.0"
}

f = open(r"cookie.txt", "r")
cookies = {}  # 初始化cookies字典变量
for line in f.read().split(';'):  # 按照字符：进行划分读取
    # 其设置为1就会把字符串拆分成2份
    name, value = line.strip().split('=', 1)
    cookies[name] = value  # 为字典cookies添加内容


def local_json(update_file):
    with open("update.json", "r", encoding="utf-8") as f:
        content = json.loads(f.read())
        return content


def web_version(content_url, target):
    r_content = requests.get(content_url["version_url"], headers=self_headers, cookies=cookies)
    obj = re.compile(f"{target}&quot;:(?P<vernum>.*?),&#x000A;")
    result = obj.finditer(r_content.text)
    for it in result:
        it.group("vernum")
        r_content.close()
        return it.group("vernum")


def web_download(content_url, target):
    r_content = requests.get(content_url["download_url"], headers=self_headers, cookies=cookies)
    obj = re.compile(f"&quot;{target}&quot;:&quot;(?P<downnum>.*?)\*")
    result = obj.finditer(r_content.text)
    for it in result:
        it.group("downnum")
        r_content.close()
        return it.group("downnum")


def web_download_last(content_url, target):
    r_content = requests.get(content_url["download_url"], headers=self_headers, cookies=cookies)
    obj = re.compile(f"\*(?P<downnum>.*?)&quot;{target}&#x000A;")
    result = obj.finditer(r_content.text)
    for it in result:
        it.group("downnum")
        r_content.close()
        return it.group("downnum")


def check_exists(file):
    """检查文件是否存在
    : file 文件
    : return boolen
    """
    return path.exists(file)


def is_updated(old, new):
    """对比版本信息
    :old 老版本号 float
    :new 新版本号 new
    :return boolen
    """
    updated = False
    if old < new:
        updated = True
    return updated


def download(url, name):
    """下载文件
    :url 网址 str
    :name 存储名称 str
    """
    try:
        urlretrieve(url, name)
    except (RuntimeError, ConnectionError):
        urlretrieve(url, name)
    dic = ["游戏主文件", "游戏资源文件", "游戏配置文件", "游戏版权信息", "最后合并"]
    pbar = tqdm(dic)
    for i in pbar:
        pbar.set_description("下载进度:" + i)
        time.sleep(5)


def fake_animation(time_self, desc_self):
    for i in tqdm(range(10), desc=desc_self):
        time.sleep(time_self)


def update():
    fake_animation(0.05, "正在启动运行更新程序")

    fake_animation(0.5, "读取本地信息文件")
    if check_exists("update.json"):
        update_file = "update.json"
        content = local_json(update_file)
        print("已获取本地信息")
    else:
        print("读取本地文件update.json失败,被阻挡或者文件不存在")
        print("准备退出更新程序,请等待后续版本更新或者联系开发者")
        sys.exit()

    print("本地更新程序版本为")
    print(content["version_self"])
    print("本地游戏版本为")
    print(content["version"])

    fake_animation(0.7, "正在读取服务器最新版本")
    content_r = web_version(content, "version")
    content_r_self = web_version(content, "version_self")

    print("服务器最新更新程序版本为")
    print(content_r_self)

    print("服务器最新游戏版本为")
    print(content_r)

    old = content["version"]
    new = content_r
    old_self = content["version_self"]
    new_self = content_r_self

    appname = content["name"] + "_new.zip"
    oldname = content["name"]
    new = float(new)
    old = float(old)
    new_self = float(new_self)
    old_self = float(old_self)
    updated_self = is_updated(old_self, new_self)
    if updated_self:
        fake_animation(0.3, "需要更新本程序,正在获取下载链接")
        web_front_self = str(web_download(content, "download_url_self"))
        web_back_self = str(web_download_last(content, "download_url_self"))
        html_self = f"{web_front_self}" + f"{web_back_self}"
        for i in html_self:
            # if i=="amp;":
            html_self = html_self.replace("amp;", '')  # 将amp;删掉
        download(html_self, "step.exe")
        fake_animation(0.1,"正在打开安装程序")
        print("请安装最新版")
        os.system("./step.exe")
    else:
        print("更新程序暂不需要更新")
    updated = is_updated(old, new)
    if updated:
        fake_animation(0.6, "需要更新游戏,正在获取下载链接")
        web_front = str(web_download(content, "download_url"))
        web_back = str(web_download_last(content, "download_url"))
        html = f"{web_front}" + f"{web_back}"
        for i in html:
            # if i=="amp;":
            html = html.replace("amp;", '')  # 将amp;删掉

    else:
        print("已经是最新版,正在退出更新程序,请稍等")
    if updated and not check_exists(oldname):
        print("没有本地文件，正在获取下载链接")
        # print("服务器下载地址为:")
        # print(html)
        print("已经开始下载任务,程序正常运行,请勿退出")
        print(f"如果程序意外断网,可以尝试删除该目录下的{oldname}.zip")
        download(html, f"{appname}")
        print("下载完成,等待解压")

    if updated and not check_exists(appname):
        print("本地版本过旧,检测到更新，准备下载")
        print("已经开始下载任务,程序正常运行,请勿退出")
        print(f"如果程序意外断网,可以尝试删除该目录下的{oldname}.zip")
        download(html, f"{appname}")
        print("下载完成,等待解压")
        fake_animation(0.9, "正在清理本地文件")
        shutil.rmtree(oldname, ignore_errors=True)
        print("清理完成")

    if updated and check_exists(appname) and not check_exists(oldname):
        fake_animation(1, "正在覆盖旧版文件")
        rename(appname, oldname + ".zip")

        if updated:
            fake_animation(0.2, "正在写入游戏版本信息")
            content["version"] = content_r
            with open(update_file, "w", encoding="utf-8") as f:
                print("已写入版本信息")
                json.dump(content, f, ensure_ascii=False, indent=4)
        # if updated_self:
        #     fake_animation(0.2, "正在写入更新程序版本信息")
        #     content["version_self"] = content_r_self
        #     with open(update_file, "w", encoding="utf-8") as f:
        #         print("已写入版本信息")
        #         json.dump(content, f, ensure_ascii=False, indent=4)



if __name__ == "__main__":
    update()