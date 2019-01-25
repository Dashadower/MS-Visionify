# -*- coding:utf-8 -*-

import hashlib, os, requests, time

def get_diskdrive_hash():
    sid = os.popen("wmic diskdrive get serialnumber").read().split()[-1]
    hash = hashlib.sha256(sid.rstrip().encode()).hexdigest()
    return str(hash)

def authenticate_device():
    server = "http://ms-rbw.appspot.com/auth"
    payload = {
        "uuid":get_diskdrive_hash()
    }
    request = requests.post(server, payload)
    try:
        data = request.json()
    except:
        return -1
    if data["result"] == "fail":
        if data["type"] == "expired":
            errortext = "사용기간이 만료되었습니다. 카카오톡으로 문의 바랍니다."
            return 0, errortext, data["UserID"], data["time"]

        elif data["type"] == "unidentified_pc":
            errortext = "등록되지 않은 PC입니다. 구매자인 경우 PC등록을 홈페이지에서 해주시고, 비구매자인 경우 카카오톡으로 문의 바랍니다."
            return 1, errortext

    elif data["result"] == "success":
        return 2, "인증되었습니다", data["UserID"], data["time"]





