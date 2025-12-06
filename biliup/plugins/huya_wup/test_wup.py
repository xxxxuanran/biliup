try:
    from .wup import Wup
    from .packet import *
    from .wup_struct.UserId import HuyaUserId
except ImportError:
    from biliup.plugins.huya_wup import Wup
    from biliup.plugins.huya_wup.packet import *
    from biliup.plugins.huya_wup.wup_struct.UserId import HuyaUserId


import httpx
import base64
import hashlib
import random
import time
from urllib.parse import parse_qs, unquote, quote
from enum import Enum
import re
import json

DEFAULT_TICKET_NUMBER = 1
client = httpx.Client()

class PLATFORM(Enum):
    HUYA_PC_EXE = 0
    HUYA_ADR = 2
    HUYA_IOS = 3
    TV_HUYA_NFTV = 10
    HUYA_WEBH5 = 100
    HUYA_LIVE = 100
    TARS_MP = 102
    TARS_MOBILE = 103
    huya_liveshareh5 = 104

    @classmethod
    def get_random_as_tuple(cls):
        _ = random.choice(list(cls))
        return _.name.lower(), _.value

    @classmethod
    def get_platform_id(cls, platform: str) -> int:
        return cls[platform.upper()].value if platform.upper() in cls.__members__ else 100


rotl64 = lambda t: ((t & 0xFFFFFFFF) << 8 | (t & 0xFFFFFFFF) >> 24) & 0xFFFFFFFF | (t & ~0xFFFFFFFF)


def build_query(stream_name, anti_code, uid: int = 0, random_platform: bool = False) -> str:
    '''
    构建anti_code
    :param stream_name: 流名称
    :param anti_code: 原始anti_code
    :param uid: 用户或主播uid，允许为0
    :return: 构建后的anti_code
    '''
    url_query = parse_qs(anti_code)
    if not url_query.get("fm"):
        return anti_code

    ctype = url_query.get('ctype', [])
    platform_id = url_query.get('t', [])
    if len(ctype) == 0:
        ctype, platform_id = PLATFORM.get_random_as_tuple()
    elif len(platform_id) == 0:
        ctype = ctype[0]
        platform_id = PLATFORM.get_platform_id(ctype)
    else:
        ctype = ctype[0]
        platform_id = platform_id[0]
    ctype, platform_id = PLATFORM.get_random_as_tuple()

    is_wap = int(platform_id) in {103}
    clac_start_time = time.time()

    if uid == 0:
        if random.random() > 0.9:
            uid = int(f"1234{random.randint(0, 9999):04d}")
        else:
            uid = int(f"140000{random.randint(0, 9999999):07d}")
    seq_id = uid + int(clac_start_time * 1000)
    secret_hash = hashlib.md5(f"{seq_id}|{ctype}|{platform_id}".encode()).hexdigest()
    convert_uid = rotl64(uid)
    clac_uid = uid if is_wap else convert_uid

    fm = unquote(url_query['fm'][0])
    secret_prefix = base64.b64decode(fm.encode()).decode().split('_')[0]

    # ws_time = url_query['wsTime'][0]
    ws_time = hex(60 * 60 * 24 + int(clac_start_time))[2:] # 修改过期时间为 1 day
    secret_str = f'{secret_prefix}_{clac_uid}_{stream_name}_{secret_hash}_{ws_time}'
    ws_secret = hashlib.md5(secret_str.encode()).hexdigest()

    ct = int((int(ws_time, 16) + random.random()) * 1000)
    uuid = str(int((ct % 1e10 + random.random()) * 1e3 % 0xffffffff))

    anti_code = {}
    anti_code.update({
        "wsSecret": ws_secret,
        "wsTime": ws_time,
        "seqid": seq_id,
        "ctype": ctype,
        "ver": "1",
        "fs": url_query['fs'][0],
        "fm": quote(url_query['fm'][0], encoding='utf-8'),
        "t": platform_id,
    })
    if is_wap:
        anti_code.update({
            "uid": uid,
            "uuid": uuid,
        })
    else:
        anti_code.update({
            "u": convert_uid,
        })
    anti_code.update({
        # "sdkPcdn": "1_1",
        # "sv": 30000002,
        # "sdk_sid": int(time.time() * 1000),
        # "a_block": 0, # adBlock
        # "sf": 1, # isWupFail
        # "startPts": 0, # getIframePts
    })

    return '&'.join([f"{k}={v}" for k, v in anti_code.items()])


if __name__ == "__main__":

    wup_url: str = "https://wup.huya.com"
    wmp_url: str = "https://mp.huya.com"
    huya_headers: dict = {
        "user-agent": f"android, 20000313_APP(huya_nftv&2.5.1.3243&official&28)_SDK(trans&1.24.99-rel-tv)",
        "referer": "https://www.huya.com/",
        "origin": "https://www.huya.com",
    }
    # presenterUid = 333393123
    room_id = 243547

    # convertUid = rot_uid(1486197514)
    # print(convertUid, convertUid == 2509441624)

    client.headers.update(huya_headers)

    # web_context = client.get(f"https://m.huya.com/{room_id}").text
    # web_data_json = json.loads(web_context.split('window.HNF_GLOBAL_INIT = ')[1].split('</script>')[0])
    # presenterUid = web_data_json['roomInfo']['tLiveInfo']['lUid']
    # web_stream_info = web_data_json['roomInfo']['tLiveInfo']['tLiveStreamInfo']['vStreamInfo']['value']
    # for item in web_stream_info:
    #     if item['iWebPriorityRate'] < 0:
    #         continue
    #     originStreamName = item['sStreamName'].replace('-imgplus', '')
    #     flvurl = f"{item['sFlvUrl']}/{item['sStreamName']}.{item['sFlvUrlSuffix']}?{item['sFlvAntiCode']}"
    #     ogflvurl = f"{item['sFlvUrl']}/{originStreamName}.{item['sFlvUrlSuffix']}?{build_query(originStreamName, item['sFlvAntiCode'], presenterUid)}"
    #     hlsurl = f"{item['sHlsUrl']}/{item['sStreamName']}.{item['sHlsUrlSuffix']}?{item['sHlsAntiCode']}"
    #     oghlsurl = f"{item['sHlsUrl']}/{originStreamName}.{item['sHlsUrlSuffix']}?{build_query(originStreamName, item['sHlsAntiCode'], presenterUid)}"
    #     print(f"------------------------WEB------------------------")
    #     print(f"{item['sCdnType']}-FLV: {flvurl}")
    #     print(f"{item['sCdnType']}-OGFLV: {ogflvurl}")
    #     print(f"{item['sCdnType']}-HLS: {hlsurl}")
    #     print(f"{item['sCdnType']}-OGHLS: {oghlsurl}")

    api_rsp = client.get(
        url=f"{wmp_url}/cache.php",
        params={
            'm': 'Live',
            'do': 'profileRoom',
            'roomid': room_id,
            'showSecret': 1,
        }
    )
    api_dict = api_rsp.json()['data']
    presenterUid = api_dict['profileInfo']['uid']
    print(presenterUid)
    for item in api_dict['stream']['baseSteamInfoList']:
        if item['iWebPriorityRate'] < 0:
            continue
        originStreamName = item['sStreamName'].replace('-imgplus', '')
        flvurl = f"{item['sFlvUrl']}/{item['sStreamName']}.{item['sFlvUrlSuffix']}?{item['sFlvAntiCode']}"
        ogflvurl = f"{item['sFlvUrl']}/{originStreamName}.{item['sFlvUrlSuffix']}?{build_query(originStreamName, item['sFlvAntiCode'], presenterUid)}"
        hlsurl = f"{item['sHlsUrl']}/{item['sStreamName']}.{item['sHlsUrlSuffix']}?{item['sHlsAntiCode']}"
        oghlsurl = f"{item['sHlsUrl']}/{originStreamName}.{item['sHlsUrlSuffix']}?{build_query(originStreamName, item['sHlsAntiCode'], presenterUid)}"
        print(f"------------------------API------------------------")
        print(f"{item['sCdnType']}-FLV: {flvurl}")
        print(f"{item['sCdnType']}-OGFLV: {ogflvurl}")
        print(f"{item['sCdnType']}-HLS: {hlsurl}")
        print(f"{item['sCdnType']}-OGHLS: {oghlsurl}")


    wup_req = Wup()
    wup_req.requestid = abs(DEFAULT_TICKET_NUMBER)
    wup_req.servant = "liveui"
    wup_req.func = "getLivingInfo"
    tid = HuyaUserId()
    # tid.lUid = presenterUid
    # tid.sDeviceId = "chrome"
    tid.sDeviceId = "android_tv"
    # tid.sHuYaUA = "huya_nftv&7020004&official"
    tid.sHuYaUA = "huya_nftv&2.5.1.3141&official&30"
    LivingInfoReq = HuyaGetLivingInfoReq()
    LivingInfoReq.lPresenterUid = presenterUid
    LivingInfoReq.tId = tid
    wup_req.put(
        vtype=HuyaGetLivingInfoReq,
        name="tReq",
        value=LivingInfoReq
    )
    data = wup_req.encode_v3()
    rsp = client.post(wup_url, data=data)
    rsp_bytes = rsp.content
    # print(rsp_bytes)
    wup_rsp = Wup()
    wup_rsp.decode_v3(rsp_bytes)
    LivingInfoRsp = wup_rsp.get(
        vtype=HuyaGetLivingInfoRsp,
        name="tRsp"
    )
    result_dict = LivingInfoRsp.as_dict()
    # print(result_dict)


    for item in result_dict['tNotice']['vStreamInfo']:
    #     wup_req = Wup()
    #     wup_req.requestid = abs(DEFAULT_TICKET_NUMBER)
    #     wup_req.servant = "liveui"
    #     wup_req.func = "getCdnTokenInfo"
    #     token_info_req = HuyaGetCdnTokenReq()
        originStreamName = item['sStreamName'].replace('-imgplus', '')
        # print(item['sCdnType'], originStreamName)
    #     token_info_req.cdnType = item['sCdnType']
    #     token_info_req.streamName = originStreamName
    #     token_info_req.presenterUid = presenterUid
    #     wup_req.put(
    #         vtype=HuyaGetCdnTokenRsp,
    #         name="tReq",
    #         value=token_info_req
    #     )
    #     data = wup_req.encode_v3()
    #     rsp = client.post(wup_url, data=data)
    #     rsp_bytes = rsp.content
    #     wup_rsp = Wup()
    #     wup_rsp.decode_v3(rsp_bytes)
    #     token_info_rsp = wup_rsp.get(
    #         vtype=HuyaGetCdnTokenRsp,
    #         name="tRsp"
    #     )
    #     # print()
    #     token_info_dict = token_info_rsp.as_dict()

        flvurl = f"{item['sFlvUrl']}/{item['sStreamName']}.{item['sFlvUrlSuffix']}?{item['sFlvAntiCode']}"
        # ogflvurl = f"{item['sFlvUrl']}/{originStreamName}.{item['sFlvUrlSuffix']}?{token_info_dict['flvAntiCode']}"
        og2flvurl = f"{item['sFlvUrl']}/{originStreamName}.{item['sFlvUrlSuffix']}?{build_query(originStreamName, item['sFlvAntiCode'], presenterUid)}"
        hlsurl = f"{item['sHlsUrl']}/{item['sStreamName']}.{item['sHlsUrlSuffix']}?{item['sHlsAntiCode']}"
        # oghlsurl = f"{item['sHlsUrl']}/{originStreamName}.{item['sHlsUrlSuffix']}?{token_info_dict['hlsAntiCode']}"
        oghlsurl = f"{item['sHlsUrl']}/{originStreamName}.{item['sHlsUrlSuffix']}?{build_query(originStreamName, item['sHlsAntiCode'], presenterUid)}"
        og2hlsurl = f"{item['sHlsUrl']}/{originStreamName}.{item['sHlsUrlSuffix']}?{build_query(originStreamName, item['sHlsAntiCode'], presenterUid, True)}"
        print(f"------------------------WUP------------------------")
        print(f"{item['sCdnType']}-FLV: {flvurl}")
        # print(f"{item['sCdnType']}-OGFLV: {ogflvurl}")
        print(f"{item['sCdnType']}-OG2FLV: {og2flvurl}")
        print(f"{item['sCdnType']}-HLS: {hlsurl}")
        print(f"{item['sCdnType']}-OGHLS: {oghlsurl}")
        print(f"{item['sCdnType']}-OG2HLS: {og2hlsurl}")

        print(f'ffmpeg -y -headers "User-Agent: {huya_headers["user-agent"]}`r`nReferer: {huya_headers["referer"]}`r`nOrigin: {huya_headers["origin"]}" -i "{og2flvurl.replace("http://", "https://")}" -c copy E:\Videos\hy.flv')