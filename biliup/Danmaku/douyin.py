# 抖音的弹幕录制参考了 https://github.com/LyzenX/DouyinLiveRecorder 和 https://github.com/YunzhiYike/live-tool
# 2023.07.14：KNaiFen：这部分代码参考了https://github.com/SmallPeaches/DanmakuRender

import gzip
import logging
import aiohttp
import json
import re

from urllib.parse import unquote
from biliup.config import config
from .douyin_util.dy_pb2 import ChatMessage, PushFrame, Response
from biliup.plugins import match1, random_user_agent
from google.protobuf import json_format


logger = logging.getLogger('biliup')


class Douyin:
    headers = {
        'user-agent': random_user_agent(),
        'Referer': 'https://live.douyin.com/',
        # 'Cookie': config.get('user', {}).get('douyin_cookie', '')
        'Cookie': "__ac_nonce=066745f4100c8cbc6c32;__ac_signature=_02B4Z6wo00f01itZ-8wAAIDCaQO7lcaCA.Yref9AAOyw7znOjv51AHRLwepHoFMiKOExeXBCX8GbQSnUkPVjZf09Fug0eayO5jZPABkm-lZ0sg.g7jYaQFr17jh5rZUXZl5P8ffkOfK7crVt1e;"
    }
    heartbeat = b':\x02hb'
    heartbeatInterval = 10

    @staticmethod
    async def get_ws_info(url, context):
        webcast5_params = {
            # "app_name": "douyin_web",
            "version_code": "180800", # https://lf-cdn-tos.bytescm.com/obj/static/webcast/douyin_live/7697.782665f8.js -> a.ry
            "webcast_sdk_version": "1.0.14-beta.0", # https://lf-cdn-tos.bytescm.com/obj/static/webcast/douyin_live/7697.782665f8.js -> ee.VERSION = "1.0.14-beta.0"
            # "update_version_code": "1.0.14-beta.0",
            # "cookie_enabled": "true",
            # "screen_width": "1920",/
            # "screen_height": "1080",
            # "browser_online": "true",
            # "tz_name": "Asia/Shanghai",
            # "cursor": "t-1718899404570_r-1_d-1_u-1_h-7382616636258522175",
            # "internal_ext": "internal_src:dim|wss_push_room_id:7382580251462732598|wss_push_did:7344670681018189347|first_req_ms:1718899404493|fetch_time:1718899404570|seq:1|wss_info:0-1718899404570-0-0|wrds_v:7382616716703957597",
            # "host": "https://live.douyin.com",
            "live_id": "1",
            "did_rule": "3",
            # "endpoint": "live_pc",
            # "support_wrds": "1",
            "user_unique_id": "",
            # "im_path": "/webcast/im/fetch/",
            "identity": "audience",
            # "need_persist_msg_count": "15",
            # "insert_task_id": "",
            # "live_reason": "",
            # "heartbeatDuration": "0",
            # "signature": "",
        }
        async with aiohttp.ClientSession() as session:
            from biliup.plugins.douyin import DouyinUtils
            if "/user/" in url:
                async with session.get(url, headers=Douyin.headers, timeout=5) as resp:
                    user_page = await resp.text()
                    user_page_data = unquote(
                        user_page.split('<script id="RENDER_DATA" type="application/json">')[1].split('</script>')[0])
                    room_id = match1(user_page_data, r'"web_rid":"([^"]+)"')
            else:
                room_id = url.split('douyin.com/')[1].split('/')[0].split('?')[0]

            if room_id[0] == "+":
                room_id = room_id[1:]

            if "ttwid" not in Douyin.headers['Cookie']:
                Douyin.headers['Cookie'] = f'ttwid={DouyinUtils.get_ttwid()};{Douyin.headers["Cookie"]}'

            if "__ac_signature" in Douyin.headers['Cookie']:
                async with session.get(f"https://live.douyin.com/{room_id}", headers=Douyin.headers, timeout=5) as resp:
                    room_page = await resp.text()
                    if 'user_unique_id' in room_page:
                        user_unique_id = match1(
                            room_page.split('self.__pace_f.push([1,"2:[')[1].split('"},')[0].split("user_unique_id")[1], r'(\d+)')
                        webcast5_params['user_unique_id'] = user_unique_id

            room_info_url = DouyinUtils.build_request_url(f"https://live.douyin.com/webcast/room/web/enter/?web_rid={room_id}")
            async with session.get(
                    room_info_url, headers=Douyin.headers, timeout=5) as resp:
                room_info = json.loads(await resp.text())['data']['data'][0]
                url = DouyinUtils.build_request_url(
                    f"wss://webcast5-ws-web-lf.douyin.com/webcast/im/push/v2/?room_id={room_info['id_str']}&compress=gzip") \
                        + "&" + "&".join([f"{k}={v}" for k, v in webcast5_params.items()]) \
                        + "&" + DouyinUtils.get_signature(f",live_id=1,aid=6383,version_code={webcast5_params['version_code']},webcast_sdk_version={webcast5_params['webcast_sdk_version']},room_id={room_info['id_str']},sub_room_id=,sub_channel_id=,did_rule=3,user_unique_id={webcast5_params['user_unique_id']},device_platform=web,device_type=,ac=,identity=audience")
                return url, []

    @staticmethod
    def decode_msg(data):
        wss_package = PushFrame()
        wss_package.ParseFromString(data)
        log_id = wss_package.logId
        decompressed = gzip.decompress(wss_package.payload)
        payload_package = Response()
        payload_package.ParseFromString(decompressed)

        ack = None
        if payload_package.needAck:
            obj = PushFrame()
            obj.payloadType = 'ack'
            obj.logId = log_id
            obj.payloadType = payload_package.internalExt
            ack = obj.SerializeToString()

        msgs = []
        for msg in payload_package.messagesList:
            if msg.method == 'WebcastChatMessage':
                chat_message = ChatMessage()
                chat_message.ParseFromString(msg.payload)
                data = json_format.MessageToDict(chat_message, preserving_proto_field_name=True)
                # name = data['user']['nickName']
                content = data['content']
                # print(content)
                # msg_dict = {"time": now, "name": name, "content": content, "msg_type": "danmaku", "color": "ffffff"}
                msg_dict = {"content": content, "msg_type": "danmaku"}
                msgs.append(msg_dict)

        return msgs, ack
