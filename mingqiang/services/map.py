import hashlib
import requests
import config
import json


district_list = {}


def map_ws(path: str, **kwargs) -> dict:
    kwargs["key"] = config.map_key
    keys = sorted(kwargs)
    url = f"/ws{path}?"
    for k in keys:
        url = f"{url}&{k}={kwargs[k]}"
    url = url.replace("?&", "?")
    sig = hashlib.md5(f"{url}{config.map_SK}".encode()).hexdigest()
    url = f"{url}&sig={sig}"
    url = f"https://apis.map.qq.com{url}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.text
    else:
        return "{}"
    
def map_district_list() -> None:
    global district_list
    data = {"struct_type": 1}
    res = map_ws(
        path = "/district/v1/list",
        **data
    )
    res = json.loads(res)
    if res["status"] == 0:
        district_list = res["result"]
    else:
        district_list = []
    return

def map_district_get_children(id: int | str) -> list:
    data = {"id": id}
    res = map_ws(
        path = "/district/v1/getchildren",
        **data
    )
    res = json.loads(res)
    if res["status"] == 0:
        return res["result"][0]
    else:
        return []

def map_geocoder(latitude: float, longitude: float):
    # 逆地址解析
    # latitude: 纬度
    # longitude: 经度
    data = {"location": f"{latitude},{longitude}"}
    res = map_ws(
        path = "/geocoder/v1",
        **data
    )
    region = json.loads(res)
    return region





