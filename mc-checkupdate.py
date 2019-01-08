#!/usr/bin/env python3
# coding=utf-8
# date 2019-01-08 09:35:55
# https://github.com/calllivecn


import sys
import json
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
    
    print("最新正式版：", latest_release)
    #print("资源json地址：", version.get(lstest_release))

    print("最新快照版：", latest_snapshot)
    #print("资源json地址：", version.get(lstest_))



json_data = download()

check(json_data)
