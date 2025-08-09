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
    sCookie = ""
    sGuid = "0a89b728acc80f670c02ab47ac479000"
    sGuid = ""
    wup_req.servant = "liveui"
    wup_req.func = "getLivingInfo"
    tid = HuyaUserId()
    tid.lUid = 1486197514
    tid.sCookie = sCookie
    tid.sDeviceId = "chrome"
    tid.sGuid = sGuid
    tid.sHuYaUA = "pc_exe&6090007&official"
    LivingInfoReq = HuyaGetLivingInfoReq()
    LivingInfoReq.lPresenterUid = 1708907089
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
    # # 验证字符串自动解码
    # print("✅ 字符串自动解码验证:")
    # print(f"  mMiscInfo 键值对类型: {type(list(LivingInfoRsp.tNotice.mMiscInfo.keys())[0])} / {type(list(LivingInfoRsp.tNotice.mMiscInfo.values())[0])}")
    # print(f"  vCdnList 元素类型: {type(LivingInfoRsp.tNotice.vCdnList[0])}")
    # print(f"  直接字符串字段类型: {type(LivingInfoRsp.tNotice.sGameName)}")

    # print(f"\n✅ 示例数据:")
    # print(f"  游戏名称: {LivingInfoRsp.tNotice.sGameName}")
    # print(f"  主播昵称: {LivingInfoRsp.tNotice.sNick}")
    # print(f"  CDN列表: {LivingInfoRsp.tNotice.vCdnList}")
    # print(f"  配置信息: {dict(list(LivingInfoRsp.tNotice.mMiscInfo.items())[:3])}")

    # # 测试 as_dict 方法
    # print(f"\n✅ as_dict 方法测试:")
    result_dict = LivingInfoRsp.as_dict()
    # print(f"  转换成功: {type(result_dict)}")
    # print(f"  顶层字段数: {len(result_dict)}")
    # print(f"  tNotice 字段数: {len(result_dict['tNotice'])}")
    # print(f"  mMiscInfo 类型: {type(result_dict['tNotice']['mMiscInfo'])}")
    # print(f"  vCdnList 类型: {type(result_dict['tNotice']['vCdnList'])}")

    # # 验证字典中的数据类型
    # import json
    # try:
    #     json_str = json.dumps(result_dict, ensure_ascii=False, indent=2)
    #     print(f"  JSON 序列化成功: {len(json_str)} 字符")
    # except Exception as e:
    #     print(f"  JSON 序列化失败: {e}")

    print(result_dict)

    print(LivingInfoRsp)