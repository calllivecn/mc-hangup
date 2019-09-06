#!/usr/bin/env python3
# coding=utf-8
# date 2019-09-06 16:58:03
# author calllivecn <c-all@qq.com>


import sys
import json
import argparse
from urllib import request
from pprint import pprint


URL="https://launchermeta.mojang.com/mc/game/version_manifest.json"

def download(url=URL):
    html = request.urlopen(url)
    data = html.read()
    utf8str = data.decode()
    js = json.loads(utf8str)
    return js

def getjsonurl(versions_obj, release_y=True, count=10):
    c = 0

    version_json_url = []

    for v in versions_obj.get("versions"):

        obj = v.get("type")

        if release_y:
            if obj == "release":
                c += 1
                version_json_url.append(v)
        else:
            if obj == "release" or obj == "snapshot":
                c += 1
                version_json_url.append(v)

        if c > count:
            break

    return version_json_url


def getversionjson(version_json_url):
    for j in version_json_url:

        json_obj = download(j["url"])
        
        try:
            number = json_obj["minimumLauncherVersion"]
        except KeyError:
            print(url, "没有minimumLauncherVersion字段。。。")
            continue

        if number:
            j["minimumLauncherVersion"] = number

        print("-"*80)
        pprint(j)



if __name__ == "__main__":
    
    parse = argparse.ArgumentParser(usage=" Usage: %(prog)s [-n <number>] [--release|--snapshot]",
                                    description="查看各个版本对应的启动器Version号。")
    
    parse.add_argument("-n", action="store", type=int, default=10, help="只输出多少个(default: 10)")
    #parse.add_argument("--shell", action="store_true", help="输出可用bash格式。")
    #parse.add_argument("--time", action="store_true", help="输出版本时间。")

    groups = parse.add_mutually_exclusive_group()

    groups.add_argument("--release", action="store_true", default=True, help="只检查正式版。")
    groups.add_argument("--snapshot", action="store_true", help="只检查快照版。")


    args = parse.parse_args()
    #print(args)

    json_data = download()

    if args.snapshot:
        RELEASE = False
    else:
        RELEASE = True

    result = getjsonurl(json_data, release_y=RELEASE, count=args.n)

    getversionjson(result)



