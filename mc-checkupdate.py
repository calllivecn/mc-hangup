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



if __name__ == "__main__":
    
    parse = argparse.ArgumentParser(usage=" Usage: %(prog)s [--release|--snapshot|--all] [--shell]",
                                    description="检查我的世界最新版本。")
    
    parse.add_argument("-n", action="store_true", help="只输出版本字符串。")

    parse.add_argument("--shell", action="store_true", help="输出可用bash格式。")

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


    if args.shell:
        print(f"RELEASE={latest_release}")
        print(f"SNAPSHOT={latest_snapshot}")
    else:

        if args.release:
            put_release(latest_release)
        elif args.snapshot:
            put_snapshot(latest_snaphost)
        else:
            put_release(latest_release)
            put_snapshot(latest_snapshot)

