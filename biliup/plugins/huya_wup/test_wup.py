try:
    from .wup import Wup
    from .packet import *
    from .wup_struct.UserId import HuyaUserId
except ImportError:
    from biliup.plugins.huya_wup import Wup
    from biliup.plugins.huya_wup.packet import *
    from biliup.plugins.huya_wup.wup_struct.UserId import HuyaUserId


import httpx

# 定义缺少的常量
DEFAULT_TICKET_NUMBER = 1
client = httpx.Client()

if __name__ == "__main__":
    # import base64
    # cdn: str = "TX"
    # stream_name: str = "1199627305549-1199627305549-5718448156589424640-2399254734554-10057-A-0-1-imgplus.flv"
    # presenter_uid: int = 1199627305549
    wup_url: str = "https://wup.huya.com"
    huya_headers: dict = {
        "user-agent": f"HYSDK(Windows, 30000002)_APP(pc_exe&6090007&official)_SDK(trans&2.24.0.5157)",
        "referer": "https://www.huya.com/",
        "origin": "https://www.huya.com",
    }
    # TupVersion3 = 3
    # wup_req = Wup()
    # wup_req.version = TupVersion3
    # wup_req.requestid = abs(DEFAULT_TICKET_NUMBER)
    # wup_req.servant = "liveui"
    # wup_req.func = "getCdnTokenInfo"
    # token_info_req = HuyaGetCdnTokenReq()
    # token_info_req.cdnType = cdn
    # token_info_req.streamName = stream_name
    # token_info_req.presenterUid = presenter_uid
    # wup_req.put(
    #     vtype=HuyaGetCdnTokenRsp,
    #     name="tReq",
    #     value=token_info_req
    # )
    # data = wup_req.encode_v3()
    # rsp = client.post(wup_url, data=data, headers=huya_headers)
    # rsp_bytes = rsp.content
    # wup_rsp = Wup()
    # wup_rsp.decode_v3(rsp_bytes)
    # token_info_rsp = wup_rsp.get(
    #     vtype=HuyaGetCdnTokenRsp,
    #     # name=bytes("tRsp", encoding=STANDARD_CHARSET)
    #     name="tRsp"
    # )
    # print(token_info_rsp.as_dict())

    wup_req = Wup()
    wup_req.requestid = abs(DEFAULT_TICKET_NUMBER)
    wup_req.servant = "liveui"
    wup_req.func = "getLivingInfo"
    tid = HuyaUserId()
    tid.lUid = 1001276654
    tid.sDeviceId = "chrome"
    tid.sHuYaUA = "pc_exe&6090007&official"
    LivingInfoReq = HuyaGetLivingInfoReq()
    LivingInfoReq.lPresenterUid = 1001276654
    LivingInfoReq.tId = tid
    wup_req.put(
        vtype=HuyaGetLivingInfoReq,
        name="tReq",
        value=LivingInfoReq
    )
    data = wup_req.encode_v3()
    rsp = client.post(wup_url, data=data, headers=huya_headers)
    rsp_bytes = rsp.content
    wup_rsp = Wup()
    wup_rsp.decode_v3(rsp_bytes)
    LivingInfoRsp = wup_rsp.get(
        vtype=HuyaGetLivingInfoRsp,
        name="tRsp"
    )
    result_dict = LivingInfoRsp.as_dict()


    print(result_dict)

    for item in result_dict['tNotice']['vStreamInfo']:
        flvurl = f"{item['sFlvUrl']}/{item['sStreamName']}.{item['sFlvUrlSuffix']}?{item['sFlvAntiCode']}"
        hlsurl = f"{item['sHlsUrl']}/{item['sStreamName']}.{item['sHlsUrlSuffix']}?{item['sHlsAntiCode']}"
        print(f"flvurl: {flvurl}")
        print(f"hlsurl: {hlsurl}")
