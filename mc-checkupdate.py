#!/usr/bin/env python3
# coding=utf-8
# date 2019-01-08 09:35:55
# https://github.com/calllivecn


import sys
import json
import argparse
from urllib import request


URL="https://launchermeta.mojang.com/mc/game/version_manifest.json"

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
    
    parse = argparse.ArgumentParser(usage=" Usage: %(prog)s [--release|--snapshot|--all] [--shell]",
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

