import math
import os
from time import sleep
from icecream import ic
from requests import session
from json import dumps, loads
from datetime import datetime


RED = '\033[91m'
GREEN = '\033[32m'
RESET = '\033[0m'
BLUE = '\033[94m'

client = session()


def get_up_info():
    ...

def bvid2aid(bvid):
    api = f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}'
    resp = client.get(api)
    resp.raise_for_status()
    jd = resp.json()
    if jd['code'] != 0:
        raise RuntimeError("json code is not 0", jd)
    data = jd['data']
    return data['aid']

def bvid2aid_v2(bvid):
    table='fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr={}
    for i in range(58):
        tr[table[i]]=i
    s=[11,10,3,8,4,6]
    xor=177451812
    add=8728348608
    r=0
    for i in range(6):
        r+=tr[bvid[s[i]]]*58**i
    return (r-add)^xor

def aid2bvid_v2(aid):
    table='fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr={}
    for i in range(58):
        tr[table[i]]=i
    s=[11,10,3,8,4,6]
    xor=177451812
    add=8728348608
    r=0
    for i in range(6):
        r+=tr[aid[s[i]]]*58**i
    return (r-add)^xor


def get_videos(uid: int):
    api = 'https://api.bilibili.com/x/space/arc/search?mid={}&ps=30&tid=0&pn={}&keyword=&order=pubdate&jsonp=jsonp'

    vlists = []
    resp = client.get(api.format(uid, 1))
    print(f'{GREEN}get: [{api.format(uid, 1)}]{RESET}')
    resp.raise_for_status()
    jd = resp.json()
    if jd['code'] != 0:
        raise RuntimeError("json code is not 0", jd)
    data = jd['data']
    vlists += data['list']['vlist']
    video_count = data['page']['count']

    for pn in range(2, math.ceil(video_count/30) + 1):
        resp = client.get(api.format(uid, pn))
        print(f'{GREEN}get: [{api.format(uid, pn)}]{RESET}')
        resp.raise_for_status()
        jd = resp.json()
        if jd['code'] != 0:
            raise RuntimeError("json code is not 0", jd)
        data = jd['data']
        vlists += data['list']['vlist']
        video_count = data['page']['count']
    return vlists

def get_video_info(bvid):
    api = f'https://www.bilibili.com/video/{bvid}'
    resp = client.get(api)
    resp.raise_for_status()
    text = resp.text
    text = text[text.find('window.__INITIAL_STATE__={') + 25: text.rfind(';(function(){')]
    jd = loads(text)
    return jd

def get_video_info_v2(bvid):
    api = f'https://api.bilibili.com/x/web-interface/view/detail?bvid={bvid}'
    resp = client.get(api)
    resp.raise_for_status()
    jd = resp.json()
    if jd['code'] != 0:
        raise RuntimeError("json code is not 0", jd)
    data = jd['data']
    return data

def get_up_info(uid):
    api = f'https://api.bilibili.com/x/space/acc/info?mid={uid}&jsonp=jsonp'
    resp = client.get(api)
    resp.raise_for_status()
    jd = resp.json()
    if jd['code'] != 0:
        raise RuntimeError("json code is not 0", jd)
    data = jd['data']
    return data


def get_comments(aid, pg=1, pn=2^31-1):
    api = f'https://api.bilibili.com/x/v2/reply/main?jsonp=jsonp&next={pg}&type=1&oid={aid}&mode=3&plat=1'
    resp = client.get(api)
    resp.raise_for_status()
    jd = resp.json()
    pn -= 1
    pg += 1
    yield jd['data']['replies'], jd['data']['cursor']['prev']
    
    while not jd['data']['cursor']['is_end'] and pn > 0:
        api = f'https://api.bilibili.com/x/v2/reply/main?jsonp=jsonp&next={pg}&type=1&oid={aid}&mode=3&plat=1'
        resp = client.get(api)
        resp.raise_for_status()
        jd = resp.json()
        pn -= 1
        pg += 1
        yield jd['data']['replies'], jd['data']['cursor']['prev']
    if jd['data']['cursor']['is_end']:
        yield None

REQUEST_INTERVAL = 1
SAVE_PATH = './data/'

def nowstr():
    return datetime.now().strftime('%Y%m%d-%H%M%S')

def daystr():
    return datetime.now().strftime('%Y%m%d')

def saveto(data, path):
    with open(path, 'w') as f:
        f.write(dumps(data))
    return path

def crawl(uid, save_path):
    _daystr = daystr()
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    _video_info_dir = f'{save_path}/infos'

    if not os.path.exists(_video_info_dir):
        os.mkdir(_video_info_dir)
    if not os.path.exists(f'{_video_info_dir}/{_daystr}'):
        os.mkdir(f'{_video_info_dir}/{_daystr}')

    _up_info_path = f'{_video_info_dir}/{_daystr}/up_info.json'
    _videos_path = f'{_video_info_dir}/{_daystr}/videos.json'

    _videos_dir = f'{save_path}/videos'
    if not os.path.exists(_videos_dir):
        os.mkdir(_videos_dir)

    _up_info = get_up_info(uid)
    _videos = get_videos(uid)

    saveto(_up_info, _up_info_path)
    saveto(_videos, _videos_path)

    for _video in _videos:
        _bvid = _video['bvid']
        print('crawler video: {}' .format(_bvid))

        _video_dir = f'{_videos_dir}/{_bvid}'
        if not os.path.exists(_video_dir):
            os.mkdir(_video_dir)
        
        _day_dir = f'{_video_dir}/{_daystr}'
        if not os.path.exists(_day_dir):
            os.mkdir(_day_dir)
        
        _video_info_path = f'{_day_dir}/video_info.json'
        _video_info = get_video_info_v2(_video['bvid'])
        _video_info_path = saveto(_video_info, _video_info_path)

        _comment_dir = f'{_day_dir}/comments'
        if not os.path.exists(_comment_dir):
            os.mkdir(_comment_dir)

        for comment, index in get_comments(_video['aid']):
            print(f'crawler comment: {index}')
            _comment_path = f'{_comment_dir}/comment_{index}.json'
            saveto(comment, _comment_path)
            sleep(REQUEST_INTERVAL)

crawl(401742377, SAVE_PATH)

# _ = get_videos(401742377)
# _ = get_video_info_v2('BV1ZF411g7EZ')
# _ = get_comments(298290791, 0, 1)
# ic(_)