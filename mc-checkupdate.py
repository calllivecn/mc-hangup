#!/usr/bin/env python3
# coding=utf-8
# date 2019-01-08 09:35:55
# https://github.com/calllivecn

import os
import sys
import json
import argparse
from os import path
#from urllib import request

import httpx

URL="https://launchermeta.mojang.com/mc/game/version_manifest.json"


class Save:

    # default: ~/.mc-update
    def __init__(self):
        self._filename = ".mc-update"
        self.filepath = path.join(path.expanduser("~"), self._filename)

        self.etag = b""

        self.latest_release = None
        self.release_time = None
        self.release_update = None

        self.latest_snapshot = None
        self.snapshot_time = None
        self.snapshot_update = None
    
        self.__read()

    @property
    def etag(self):
        return self._etag
    
    @etag.setter
    def etag(self, v):
        self._etag = v
    
    @property
    def latest_release(self):
        return self._latest_release
    
    @latest_release.setter
    def latest_release(self, v):
        self._latest_release = v
    
    @property
    def release_time(self):
        return self._release_time
    
    @release_time.setter
    def release_time(self, v):
        self._release_time = v
    
    @property
    def release_update(self):
        return self._release_update
    
    @release_update.setter
    def release_update(self, v):
        self._release_update = v
    
    @property
    def latest_snapshot(self):
        return self._latest_snapshot
    
    @latest_snapshot.setter
    def latest_snapshot(self, v):
        self._latest_snapshot = v
    
    @property
    def snapshot_time(self):
        return self._snapshot_time
    
    @snapshot_time.setter
    def snapshot_time(self, v):
        self._snapshot_time = v
    
    @property
    def snapshot_update(self):
        return self._snapshot_update
    
    @snapshot_update.setter
    def snapshot_update(self, v):
        self._snapshot_update = v
    
    def __read(self):
        if not path.exists(self.filepath):
            return

        try:
            with open(self.filepath, "r") as fp:
                data = fp.read().split("\n")
        except Exception:
            print(f"打开文件：{self.filepath} 失败")
            sys.exit(1)

        self.etag = data[0]

        self.latest_release = data[1]
        self.release_time = data[2]
        self.release_update = data[3]

        self.latest_snapshot = data[4]
        self.snapshot_time = data[5]
        self.snapshot_update = data[6]

    def save(self):
        data = "\n".join([self.etag,
                        self.latest_release,
                        self.release_time,
                        self.release_update,
                        self.latest_snapshot,
                        self.snapshot_time,
                        self.snapshot_update,
                        ])
        try:
            with open(self.filepath, "w") as fp:
                fp.write(data)
        except Exception:
            print(f"写入文件：{self.filepath} 失败")
            sys.exit(1)
    

def head_check(save, url=URL):
    # head http 请求
    with httpx.Client(http2=True) as client:
        r = client.head(url)
        Etag = r.headers.get("Etag", "")

    if Etag == save.etag:
        return False
    else:
        save.etag = Etag
        return True

def download(url=URL):
    with httpx.Client(http2=True) as client:
        r = client.get(url)

    return r.text

def get_release(data):
    json_data = json.loads(data)

    latest = json_data.get("latest")

    latest_release = latest.get("release")
    latest_snapshot = latest.get("snapshot")

    #versions = json_data.get("versions")
    
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
    
    # head check
    save = Save()

    if head_check(save):
        json_data = download()

        save.latest_release, save.latest_snapshot = get_release(json_data)

        save.release_time, save.release_update = get_time(json_data, save.latest_release)
        save.snapshot_time, save.snapshot_update = get_time(json_data, save.latest_snapshot)

        #print("save.etag", type(save.etag), save.etag)
        save.save()
    else:
        print("没有更新。。。查看缓存:")

    if args.shell:
        print(f"RELEASE={save.latest_release}")
        print(f"SNAPSHOT={save.latest_snapshot}")
    else:

        if args.release:
            put_release(save.latest_release + " 版本发布时间:" + save.release_time + " 更新时间:" + save.release_update)
        elif args.snapshot:
            put_snapshot(save.latest_snapshot + " 版本发布时间:" + save.snapshot_time + " 更新时间:" + save.snapshot_update)
        else:
            put_release(save.latest_release + " 版本发布时间:" + save.release_time + " 更新时间:" + save.release_update)
            put_snapshot(save.latest_snapshot + " 版本发布时间:" + save.snapshot_time + " 更新时间:" + save.snapshot_update)

