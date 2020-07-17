#!/usr/bin/env python3
# coding=utf-8
# date 2019-01-08 09:35:55
# https://github.com/calllivecn

import os
import sys
import json
import argparse
from os import path
from urllib import request


URL="https://launchermeta.mojang.com/mc/game/version_manifest.json"


class Save:

    # default: ~/.mc-update
    def __init__(self, filepath=None):

        self._filename = ".mc-update"
        self.filepath = path.join(path.expanduser("~"), self._filename)
        try:
            self._fp = open(self.filepath, "r+b")
        except Exception:
            print(f"打开文件：{self.filepath} 失败")
            sys.exit(1)
    @property
    def etag(self):
        return self._etag
    
    @etag.setter
    def etag(self, v):
        self._etag = v
    
    
    @property
    def release(self):
        return self._release
    
    @release.setter
    def release(self, v):
        self._release = v
    
    @property
    def release_time(self):
        return self._release_time
    
    @release_time.setter
    def release_time(self, v):
        self._release_time = v
    
    @property
    def snapshot(self):
        return self._snaphost
    
    @snapshot.setter
    def snapshot(self, v):
        self._snapshot = v
    
    @property
    def snapshot_time(self):
        return self._snaphost_time
    
    @snapshot_time.setter
    def snapshot_time(self, v):
        self._snapshot_time = v
    
    def read(self):

        data = self._fp.read()

        try:
            self._etag, self._release, self._snapshot, self._release_time, self._snapshot_time = data.split('\n')
        except Exception:
            os.remove(sefl.filepath)
            return False
        
        return True
    
    def write(self):
        self._fp.seek(0, os.SEEK_SET)
        self._fp.write("\n".join(self._etag, self._release, self._release_time, self._snapshot, self._snapshot_time))
    
    def close(self):
        if not self._fp.closed:
            self._fp.close()


def head_check(url=URL):
    req = request.Request(url, method="HEAD")
    result = request.urlopen(req)
    Etag = result.getheader("Etag")

    save = Save()

    if Etag == local_Etag:

def download(url=URL):
    html = request.urlopen(url)
    data = html.read()
    return data.decode()

def check(data):
    json_data = json.loads(data)

    latest = json_data.get("latest")

    latest_release = latest.get("release")
    latest_snapshot = latest.get("snapshot")
    versions = json_data.get("versions")
    
    #print("最新正式版：", latest_release)
    #print("资源json地址：", version.get(lstest_release))

    #print("最新快照版：", latest_snapshot)
    #print("资源json地址：", version.get(lstest_))
    return latest_release, latest_snapshot

def get_time(data, release_id):

    versions = json.loads(data).get("versions")

    for re_id in versions:
        if re_id.get("id") == release_id:
            releasetime = re_id.get("releaseTime")
            time = re_id.get("time")
            break


    return releasetime, time


def test():
    with open('version_manifest.json') as f:
        data = f.read()

    releasetime, time = get_time(data,"1.13.2")
    print("版本发布时间:",releasetime,"更新时间:",time)
    
#test();exit(0)


if __name__ == "__main__":
    
    parse = argparse.ArgumentParser(usage=" Usage: %(prog)s [-n] [--release|--snapshot|--all] [--shell|--time]",
                                    description="检查我的世界最新版本。")
    
    parse.add_argument("-n", action="store_true", help="只输出版本字符串。")
    parse.add_argument("--shell", action="store_true", help="输出可用bash格式。")
    parse.add_argument("--time", action="store_true", help="输出版本时间。")

    groups = parse.add_mutually_exclusive_group()

    groups.add_argument("--all",action="store_true", help="检查正式版和快照版。")
    groups.add_argument("--release",action="store_true",help="只检查正式版。")
    groups.add_argument("--snapshot",action="store_true",help="只检查快照版。")


    args = parse.parse_args()
    #print(args)

    if args.n:
        put_release = print
        put_snapshot = print
    else:
        put_release = lambda t: print("最新正式版:",t)
        put_snapshot = lambda s: print("最新快照版:",s)

    json_data = download()

    latest_release, latest_snapshot = check(json_data)

    releasetime_release, time_release = get_time(json_data,latest_release)
    releasetime_snapshot, time_snapshot = get_time(json_data,latest_snapshot)

    if args.shell:
        print(f"RELEASE={latest_release}")
        print(f"SNAPSHOT={latest_snapshot}")
    else:

        if args.release:
            put_release(latest_release + " 版本发布时间:" + releasetime_release + " 更新时间:" + time_release)
        elif args.snapshot:
            put_snapshot(latest_snapshot + " 版本发布时间:" + releasetime_snapshot + " 更新时间:" + time_snapshot)
        else:
            put_release(latest_release + " 版本发布时间:" + releasetime_release + " 更新时间:" + time_release)
            put_snapshot(latest_snapshot + " 版本发布时间:" + releasetime_snapshot + " 更新时间:" + time_snapshot)

