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

DEFAULT_TICKET_NUMBER = 1
client = httpx.Client()

def build_query(stream_name, anti_code, uid: int) -> str:
    '''
    构建anti_code
    :param stream_name: 流名称
    :param anti_code: 原始anti_code
    :param uid: 主播uid
    :return: 构建后的anti_code
    '''
    url_query = parse_qs(anti_code)
    if not url_query.get("fm"):
        return anti_code
    ctype = url_query['ctype']
    if len(ctype) == 0:
        ctype = random.choice(["huya_webh5", "huya_pc_exe", "huya_commserver"])
    else:
        ctype = ctype[0]
    platform_id = int(url_query.get('t', [100])[0])
    fm = unquote(url_query['fm'][0])
    secret_prefix = base64.b64decode(fm.encode()).decode().split('_')[0]
    seq_id = uid + int(time.time() * 1000)
    convert_uid = (uid << 8 | uid >> (32 - 8)) & 0xFFFFFFFF
    clac_uid = convert_uid if platform_id != 103 else uid
    secret_hash = hashlib.md5(f"{seq_id}|{ctype}|{platform_id}".encode()).hexdigest()
    ws_time = url_query['wsTime'][0]
    ws_time = hex(int(time.time()) + 60 * 60 * 24)[2:] # 修改过期时间为 1 day
    secret_str = f'{secret_prefix}_{clac_uid}_{stream_name}_{secret_hash}_{ws_time}'
    ws_secret = hashlib.md5(secret_str.encode()).hexdigest()

    ct = int((int(ws_time, 16) + random.random()) * 1000)
    uuid = str(int((ct % 1e10 + random.random()) * 1e3 % 0xffffffff))

    anti_code = {}
    anti_code.update({
        "wsSecret": ws_secret,
        "wsTime": ws_time,
        "fm": quote(url_query['fm'][0], encoding='utf-8'),
        "ctype": ctype,
        "fs": url_query['fs'][0],
        "t": platform_id,
        "seqid": seq_id,
        "ver": "1",
        # "sdkPcdn": "1_1",
    })
    if platform_id == 103: # wap
        anti_code.update({
            "uid": uid,
            "uuid": uuid,
        })
    else:
        anti_code.update({
            "u": convert_uid,
        })
    # anti_code.update({
    #     "sv": 2510150951,
    #     "sdk_sid": int(time.time() * 1000),
    #     "a_block": 0, # adBlock
    #     "sf": 1, # isWupFail
    #     "startPts": 0, # getIframePts
    # })

    return '&'.join([f"{k}={v}" for k, v in anti_code.items()])


if __name__ == "__main__":

    wup_url: str = "https://wup.huya.com"
    wmp_url: str = "https://mp.huya.com"
    huya_headers: dict = {
        "user-agent": f"HYSDK(Windows, 30000002)_APP(pc_exe&7020004&official)_SDK(trans&2.28.0.5380)",
        "referer": "https://www.huya.com/",
        "origin": "https://www.huya.com",
    }
    # presenterUid = 333393123
    room_id = 10188


    client.headers.update(huya_headers)

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
    tid.lUid = presenterUid
    tid.sDeviceId = "chrome"
    tid.sHuYaUA = "pc_exe&7020004&official"
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
    wup_rsp = Wup()
    wup_rsp.decode_v3(rsp_bytes)
    LivingInfoRsp = wup_rsp.get(
        vtype=HuyaGetLivingInfoRsp,
        name="tRsp"
    )
    result_dict = LivingInfoRsp.as_dict()


    for item in result_dict['tNotice']['vStreamInfo']:
        wup_req = Wup()
        wup_req.requestid = abs(DEFAULT_TICKET_NUMBER)
        wup_req.servant = "liveui"
        wup_req.func = "getCdnTokenInfo"
        token_info_req = HuyaGetCdnTokenReq()
        originStreamName = item['sStreamName'].replace('-imgplus', '')
        token_info_req.cdnType = item['sCdnType']
        token_info_req.streamName = originStreamName
        token_info_req.presenterUid = presenterUid
        wup_req.put(
            vtype=HuyaGetCdnTokenRsp,
            name="tReq",
            value=token_info_req
        )
        data = wup_req.encode_v3()
        rsp = client.post(wup_url, data=data)
        rsp_bytes = rsp.content
        wup_rsp = Wup()
        wup_rsp.decode_v3(rsp_bytes)
        token_info_rsp = wup_rsp.get(
            vtype=HuyaGetCdnTokenRsp,
            name="tRsp"
        )
        # print()
        token_info_dict = token_info_rsp.as_dict()

        flvurl = f"{item['sFlvUrl']}/{item['sStreamName']}.{item['sFlvUrlSuffix']}?{item['sFlvAntiCode']}"
        ogflvurl = f"{item['sFlvUrl']}/{originStreamName}.{item['sFlvUrlSuffix']}?{token_info_dict['flvAntiCode']}"
        og2flvurl = f"{'http://qn.flv.huya.com'}/{originStreamName}.{item['sFlvUrlSuffix']}?{build_query(originStreamName, item['sFlvAntiCode'], presenterUid)}"
        hlsurl = f"{item['sHlsUrl']}/{item['sStreamName']}.{item['sHlsUrlSuffix']}?{item['sHlsAntiCode']}"
        oghlsurl = f"{item['sHlsUrl']}/{originStreamName}.{item['sHlsUrlSuffix']}?{token_info_dict['hlsAntiCode']}"
        og2hlsurl = f"{item['sHlsUrl']}/{originStreamName}.{item['sHlsUrlSuffix']}?{build_query(originStreamName, item['sHlsAntiCode'], presenterUid)}"
        print(f"------------------------WUP------------------------")
        print(f"{item['sCdnType']}-FLV: {flvurl}")
        print(f"{item['sCdnType']}-OGFLV: {ogflvurl}")
        print(f"{item['sCdnType']}-OG2FLV: {og2flvurl}")
        print(f"{item['sCdnType']}-HLS: {hlsurl}")
        print(f"{item['sCdnType']}-OGHLS: {oghlsurl}")
        print(f"{item['sCdnType']}-OG2HLS: {og2hlsurl}")