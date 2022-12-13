# coding=utf-8
import json
import os
import re
import shutil
import sys
import time
import platform
from os import path, rename
from urllib.request import urlretrieve
from sendmail import mailsender
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
    """
    :param update_file: 读取本地的json文件
    :return:读取到的json文件
    """
    with open(update_file, "r", encoding="utf-8") as f:
        content = json.loads(f.read())
        return content


# 读取储存在服务器上的版本信息
def web_version(content_url, target):
    """
    :param content_url: 读取本地的json文件,r_content将读取其中的版本信息地址
    :param target: 读取目标服务器上的哪一个参数,为了函数复用
    :return: 返回是完整的读取到的版本地址
    """
    r_content = requests.get(content_url["version_url"], headers=self_headers, cookies=cookies)
    obj = re.compile(f"{target}&quot;:(?P<vernum>.*?),&#x000A;")
    result = obj.finditer(r_content.text)
    for it in result:
        it.group("vernum")
        r_content.close()
        return it.group("vernum")


def web_download(content_url, target):
    """
    :param content_url: 传入本地的json文件,r_content将解析其中的下载地址
    :param target: 读取目标服务器上的哪一个参数
    :return: 返回下载地址的前半部分(不包含用户信息)
    """
    r_content = requests.get(content_url["download_url"], headers=self_headers, cookies=cookies)
    obj = re.compile(f"&quot;{target}&quot;:&quot;(?P<downnum>.*?)\*")
    result = obj.finditer(r_content.text)
    for it in result:
        it.group("downnum")
        r_content.close()
        return it.group("downnum")


def web_download_last(content_url, target):
    """
    :param content_url: 传入本地的json文件,r_content将解析其中的下载地址
    :param target: 读取目标服务器上的哪一个参数
    :return: 返回下载地址的后半部分(用户信息)
    """
    r_content = requests.get(content_url["download_url"], headers=self_headers, cookies=cookies)
    obj = re.compile(f"&quot;{target}&quot;:&quot;.*?\*(?P<downnum>.*?)&quot;{target}&#x000A;")
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


def download(url, name, savepath='./'):
    """
    download file from internet
    :param url: 下载路径
    :param savepath: 文件保存路径
    :return: None
    """

    def reporthook(a, b, c):
        """
        显示下载进度
        :param a: 已经下载的数据块
        :param b: 数据块的大小
        :param c: 远程文件大小
        :return: None
        """
        print("\rdownloading: %5.1f%%" % (a * b * 100.0 / c), end="")

    # filename = os.path.basename(url)
    filename = name
    # 判断文件是否存在，如果不存在则下载
    if not os.path.isfile(os.path.join(savepath, filename)):
        # print("Downloading data from %s" % url)
        try:
            urlretrieve(url, os.path.join(savepath, filename), reporthook=reporthook)
            print("\n下载完成")
        except:
            fake_animation(0.5, "首次连接失效,重新发起请求")
            try:
                urlretrieve(url, os.path.join(savepath, filename), reporthook=reporthook)
            except:
                print("下载链接已经失效，请重试或者联系作者换源")
                mailsender(f"\n下载链接失效,请重新替换{name}下载源"
                           f"\n失效的链接为:{url}"
                           f"\n上报操作系统:{platform.platform()}"
                           f"\n上报系统版本号:{platform.version()}"
                           f"\n上报网络信息:{platform.node()}")
                input("按任意键退出程序")
                sys.exit()


    else:
        print("文件已经存在")
    # 获取文件大小
    filesize = os.path.getsize(os.path.join(savepath, filename))
    # 文件大小默认以Bytes计， 转换为Mb
    print('File size = %.2f Mb' % (filesize / 1024 / 1024))


def fake_animation(time_self, desc_self):
    """

    :param time_self: 播放时间
    :param desc_self: 播放提示
    :return: NONE
    """
    for i in tqdm(range(10), desc=desc_self):
        time.sleep(time_self)


def update():
    """
    更新功能的完整代码
    其中的所有进度条为假进度条
    :return: NONE
    """
    global html
    fake_animation(0.05, "正在启动运行更新程序")
    shutil.rmtree("C:\\temp\\", ignore_errors=True)

    fake_animation(0.3, "读取本地信息文件")
    try:
        update_file = "update.json"
        content = local_json(update_file)
        print("已获取本地信息")
    except:
        print("读取本地文件update.json失败,被阻挡或者文件不存在"
              "准备退出更新程序,请等待后续版本更新或者联系开发者")
        sys.exit()

    print(f"本地更新程序版本为{content['version_self']}")
    print(f"本地游戏版本为{content['version']}")

    fake_animation(0.7, "正在读取服务器最新版本")
    content_r = web_version(content, "version")
    content_r_self = web_version(content, "version_self")

    print(f"服务器最新更新程序版本为{content_r_self}")
    print(f"服务器最新游戏版本为{content_r}")

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
        os.popen("mkdir C:\\temp")
        download(html_self, "step.exe", savepath='C:\\temp')
        fake_animation(0.1, "正在打开安装程序")
        print("请安装最新版"
              "请先退出该程序,然后覆盖安装即可")
        input("回车开始安装")
        os.popen("C:\\temp\\.\step.exe")
        sys.exit()
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
        print("本地版本过旧,检测到更新，准备下载"
              "已经开始下载任务,程序正常运行,请勿退出")
        print(f"如果程序意外断网,可以尝试删除该目录下的{oldname}.zip")
        print(f"下载链接为{html}")
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


if __name__ == "__main__":
    update()
