# coding=utf-8

import requests
import json
import time
import math
import traceback

x_pi = 3.14159265358979324 * 3000.0 / 180.0
pi = 3.1415926535897932384626
a = 6378245.0
ee = 0.00669342162296594323


# 火星坐标系转wgs84
def gcj02towgs84(lng, lat):
    if out_of_china(lng, lat):
        return lng, lat
    dlat = transformlat(lng - 105.0, lat - 35.0)
    dlng = transformlng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)
    mglat = lat + dlat
    mglng = lng + dlng
    return '{},{}'.format(lng * 2 - mglng, lat * 2 - mglat)


def out_of_china(lng, lat):
    if lng < 72.004 or lng > 137.8347:
        return True
    if lat < 0.8293 or lat > 55.8271:
        return True
    return False


def transformlat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * pi) + 40.0 *
            math.sin(lat / 3.0 * pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *
            math.sin(lat * pi / 30.0)) * 2.0 / 3.0
    return ret


def transformlng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))
    ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *
            math.sin(2.0 * lng * pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * pi) + 40.0 *
            math.sin(lng / 3.0 * pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *
            math.sin(lng / 30.0 * pi)) * 2.0 / 3.0
    return ret


# 通过接口获取速度信息
def getjson(rectangle):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.67 Safari/537.36'
    }
    pa = {
        'key': 'b1ad166a90e7347b75d709c6eecd89f5',
        'level': 6,
        'rectangle': rectangle,
        'extensions': 'all',
        'output': 'JSON'
    }
    r = requests.get('https://restapi.amap.com/v3/traffic/status/rectangle?', params=pa, headers=headers)
    decodejson = json.loads(r.text)
    return decodejson


if __name__ == '__main__':
    # 设定查询范围 左下角和右上角（xmin ymin xmax ymax）
    # each_point = "108.904849,34.231103;109.001481,34.269367"
    each_point = "108.904849,34.231103;109.001481,34.269367"

    lastTime = time.clock()

    for i in range(288):
        decodejson = getjson(each_point)
        dt = time.localtime()
        ft = "%Y-%m-%d %H:%M:%S"
        nt = time.strftime(ft, dt)
        print nt

        # 向文件中输出爬虫的结果
        f = open("{}.txt".format(str(nt).replace("-", "_").replace(" ", "_").replace(":", "_")), 'w+')

        if decodejson['trafficinfo']['roads']:
            for each in decodejson['trafficinfo']['roads']:
                # print each
                try:
                    speed = each['speed']
                except:
                    speed = None
                try:
                    polyline = each['polyline'].split(';')
                    for i in range(0, len(polyline)):
                        try:
                            x, y = float(polyline[i].split(',')[0]), float(polyline[i].split(',')[1])
                            roadloc = gcj02towgs84(x, y) + ',' + speed
                            f.write(roadloc + "\n")
                        except:
                            pass
                except:
                    polyline = None
                    # print traceback.format_exc()

        f.close()

        # 300秒一个循环
        time.sleep(lastTime + 300 - time.clock())
        lastTime = lastTime + 300
