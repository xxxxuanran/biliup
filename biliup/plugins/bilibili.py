import time
import json
import re

from typing import *

from biliup.common.util import client
from biliup.config import config
from . import match1, logger
from biliup.Danmaku import DanmakuClient
from ..engine.decorators import Plugin
from ..engine.download import DownloadBase


OFFICIAL_API = "https://api.live.bilibili.com"
STREAM_NAME_REGEXP = r"/live-bvc/\d+/(live_[^/\.]+)"

@Plugin.download(regexp=r'https?://(b23\.tv|live\.bilibili\.com)')
class Bililive(DownloadBase):
    def __init__(self, fname, url, suffix='flv'):
        super().__init__(fname, url, suffix)
        self.live_start_time = 0
        self.bilibili_danmaku = config.get('bilibili_danmaku', False)
        self.bilibili_danmaku_detail = config.get('bilibili_danmaku_detail', False)
        self.__real_room_id = None
        self.__login_mid = 0
        self.bili_cookie = config.get('user', {}).get('bili_cookie')
        self.bili_cookie_file = config.get('user', {}).get('bili_cookie_file')
        self.bili_qn = -1
        self.bili_protocol = config.get('bili_protocol', 'stream')
        self.bili_cdn = config.get('bili_cdn', [])
        self.bili_hls_timeout = config.get('bili_hls_transcode_timeout', 60)
        self.bili_api_list = [
            normalize_url(config.get('bili_liveapi', OFFICIAL_API)).rstrip('/'),
            normalize_url(config.get('bili_fallback_api', OFFICIAL_API)).rstrip('/'),
        ]
        self.bili_force_source = config.get('bili_force_source', False)
        self.bili_anonymous_origin = config.get('bili_anonymous_origin', False)
        self.bili_ov2cn = config.get('bili_ov2cn', False)
        self.bili_normalize_cn204 = config.get('bili_normalize_cn204', False)
        self.cn01_sids = config.get('bili_replace_cn01', [])
        self.bili_cdn_fallback = config.get('bili_cdn_fallback', False)

    async def acheck_stream(self, is_check=False):

        if "b23.tv" in self.url:
            try:
                resp = await client.get(self.url, follow_redirects=False)
                if resp.status_code not in {301, 302}:
                    raise Exception("不支持的链接")
                url = str(resp.next_request.url)
                if "live.bilibili" not in url:
                    raise Exception("不支持的链接")
                self.url = url
            except Exception as e:
                logger.error(f"{self.plugin_msg}: {e}")
                return False

        room_id = match1(self.url, r'bilibili.com/(\d+)')
        if self.bili_cookie:
            self.fake_headers['cookie'] = self.bili_cookie
        if self.bili_cookie_file:
            try:
                with open(self.bili_cookie_file, encoding='utf-8') as stream:
                    cookies = json.load(stream)["cookie_info"]["cookies"]
                    cookies_str = ''
                    for i in cookies:
                        cookies_str += f"{i['name']}={i['value']};"
                    self.fake_headers['cookie'] = cookies_str
            except Exception:
                logger.exception("load_cookies error")
        self.fake_headers['referer'] = self.url

        # 获取直播状态与房间标题
        info_by_room_url = f"{OFFICIAL_API}/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id}"
        try:
            room_info = await client.get(info_by_room_url, headers=self.fake_headers)
            room_info = room_info.json()
        except Exception as e:
            logger.error(f"{self.plugin_msg}: {e}")
            return False
        if room_info['code'] != 0:
            logger.error(f"{self.plugin_msg}: {room_info}")
            return False
        else:
            room_info = room_info['data']
        if room_info['room_info']['live_status'] != 1:
            logger.debug(f"{self.plugin_msg}: 未开播")
            self.raw_stream_url = None
            return False

        self.live_cover_url = room_info['room_info']['cover']
        self.room_title = room_info['room_info']['title']
        self.__real_room_id = room_info['room_info']['room_id']
        live_start_time = room_info['room_info']['live_start_time']
        special_type = room_info['room_info']['special_type'] # 0: 公开直播, 1: 大航海专属

        if is_check:
            return True

        if self.__login_mid == 0:
            self.__login_mid = await self.check_login_status()

        # 复用原画 m3u8 流
        if  self.raw_stream_url is not None \
            and ".m3u8" in self.raw_stream_url \
            and self.bili_qn >= 10000:
            url = await self.acheck_url_healthy(self.raw_stream_url)
            if url is not None:
                logger.info(f"{self.plugin_msg}: 复用 {url}")
                return True
            self.raw_stream_url = None

        qn_with_codec = {}
        if self.bili_qn == -1:
            accept_qn = config.get('bili_qn', ['10000', 'avc10000', 'hevc10000'])
            accept_qn = ['hevc400', '10000', 'avc10000', 'hevc10000']
            if isinstance(accept_qn, int):
                # 旧配置的选项值
                accept_qn = [str(accept_qn)]
            elif isinstance(accept_qn, str):
                # 旧配置的自定义值
                accept_qn = [accept_qn]
            for qn in accept_qn:
                qn_str = match1(qn, r'(\d+)')
                codec = qn.split(qn_str)[0]
                if not codec:
                    codec = 'any'
                qn_with_codec.setdefault(int(qn_str), []).append(codec)

        stream_urls = await self.aget_stream(qn_with_codec, self.bili_protocol, special_type)
        if not stream_urls:
            if self.bili_protocol == 'hls_fmp4':
                if int(time.time()) - live_start_time <= self.bili_hls_timeout:
                    logger.warning(f"{self.plugin_msg}: 暂未提供 hls_fmp4 流，等待下一次检测")
                    return False
                else:
                    # 回退首个可用格式
                    stream_urls = await self.aget_stream(self.bili_qn, 'stream', special_type)
            else:
                logger.error(f"{self.plugin_msg}: 获取{self.bili_protocol}流失败")
                return False

        target_quality_stream = stream_urls.get(
            str(self.bili_qn), next(iter(stream_urls.values()))
        )
        stream_url = {}
        if self.bili_cdn is not None:
            for cdn in self.bili_cdn:
                stream_info = target_quality_stream.get(cdn)
                if stream_info is not None:
                    current_cdn = cdn
                    stream_url = stream_info['url']
                    break
        if not stream_url:
            current_cdn, stream_info = next(iter(target_quality_stream.items()))
            stream_url = stream_info['url']
            logger.debug(f"{self.plugin_msg}: 使用 {current_cdn} 流")

        self.raw_stream_url = self.normalize_cn204(
            f"{stream_url['host']}{stream_url['base_url']}{stream_url['extra']}"
        )

        # 替换 cn-gotcha01 节点
        if self.cn01_sids and "cn-gotcha01" in current_cdn:
            if isinstance(self.cn01_sids, str):
                self.cn01_sids = self.cn01_sids.split(',')
            for sid in self.cn01_sids:
                new_url = f"https://{sid}.bilivideo.com{stream_url['base_url']}{stream_url['extra']}"
                new_url = await self.acheck_url_healthy(new_url)
                if new_url is not None:
                    self.raw_stream_url = new_url
                    break
                else:
                    logger.debug(f"{self.plugin_msg}: {sid} is not available")

        # 强制原画
        if self.bili_qn <= 10000 and self.bili_force_source:
            # 不处理 qn 20000
            if stream_info['suffix'] not in {'origin', 'uhd', 'maxhevc'}:
                __base_url = stream_url['base_url'].replace(f"_{stream_info['suffix']}", "")
                __sk = match1(stream_url['extra'], r'sk=([^&]+)')
                __extra = stream_url['extra'].replace(__sk, __sk[:32])
                __url = self.normalize_cn204(f"{stream_url['host']}{__base_url}{__extra}")
                if (await self.acheck_url_healthy(__url)) is not None:
                    self.raw_stream_url = __url
                    logger.info(f"{self.plugin_msg}: force_source 处理 {current_cdn} 成功 {stream_info['stream_name']}")
                else:
                    logger.debug(
                        f"{self.plugin_msg}: force_source 处理 {current_cdn} 失败 {stream_info['stream_name']}"
                    )

        # 回退
        if self.bili_cdn_fallback:
            __url = await self.acheck_url_healthy(self.raw_stream_url)
            if __url is None:
                for cdn, stream_info in target_quality_stream.items():
                    stream_url = stream_info['url']
                    __fallback_url = self.normalize_cn204(
                        f"{stream_url['host']}{stream_url['base_url']}{stream_url['extra']}"
                    )
                    try:
                        __url = await self.acheck_url_healthy(__fallback_url)
                        if __url is not None:
                            self.raw_stream_url = __url
                            logger.info(f"{self.plugin_msg}: cdn_fallback 回退到 {cdn} - {__fallback_url}")
                            break
                    except Exception as e:
                        logger.error(f"{self.plugin_msg}: cdn_fallback {e} - {__fallback_url}")
                        continue
                else:
                    logger.error(f"{self.plugin_msg}: 所有 cdn 均不可用")
                    self.raw_stream_url = None
                    return False
            else:
                self.raw_stream_url = __url

        return True

    def danmaku_init(self):
        if self.bilibili_danmaku:
            self.danmaku = DanmakuClient(
                self.url, self.gen_download_filename(), {
                    'room_id': self.__real_room_id,
                    'cookie': self.fake_headers.get('cookie', ''),
                    'detail': self.bilibili_danmaku_detail,
                    'uid': self.__login_mid
                }
            )


    async def get_play_info(self, api: str, qn: int = 10000) -> dict:
        full_url = f"{api}/xlive/web-room/v2/index/getRoomPlayInfo"
        params = {
            'room_id': self.__real_room_id,
            'protocol': '0,1',  # 流协议，0: http_stream(flv), 1: http_hls
            'format': '0,1,2',  # 格式，0: flv, 1: ts, 2: fmp4
            'codec': '0,1',  # 编码器，0: avc, 1: hevc, 2: av1
            'qn': qn,
            'platform': 'html5',  # 平台名称，web, html5, android, ios
            # 'ptype': '8', # P2P配置，-1: disable, 8: WebRTC, 8192: MisakaTunnel
            # 'dolby': '5', # 杜比
            # 'panorama': '1', # 全景(不支持 html5)
            # 'hdr_type': '0,1', # HDR类型(不支持 html5)，0: SDR, 1: PQ
            # 'req_reason': '0', # 请求原因，0: Normal, 1: PlayError
            # 'http': '1', # 直播流是否使用 http
        }
        try:
            res = await client.get(
                full_url, params=params, headers=self.fake_headers
            )
            res = json.loads(res.text)
            return check_areablock(res)
        except json.JSONDecodeError:
            logger.error(f"{self.plugin_msg}: {api} 返回内容错误: {res.text}")
        except Exception as e:
            logger.error(f"{self.plugin_msg}: {api} 获取 play_info 失败 -> {e}", exc_info=True)
        return {}

    async def get_master_m3u8(self, api: str) -> dict:
        '''
        Web端首屏用的是 API，
        只有 API 存在 master_url 才会添加画质选项 -1(自动) 并隐式切换
        '''
        full_url = f"{api}/xlive/web-room/v2/index/master_playurl"
        params = {
            "cid": self.__real_room_id,
            "mid": self.__login_mid, # 若为有效用户之uid，将按qn降序排列流，否则按qn升序排列
            "pt": "html5", # platform
            "p2p_type": "-1", # -1 禁用，1 启用
            "net": "0", # 0 非无线网络
            "free_type": "0",
            "build": "0",
            # "stream_name": "", # 筛选流编码
        }
        try:
            res = await client.get(
                full_url, params=params, headers=self.fake_headers
            )
            if res.status_code != 200:
                raise Exception(f"Status Code: {res.status_code}")
            if not res.text.startswith("#EXTM3U"):
                raise ValueError(f"{res.text}")
            return self.parse_master_m3u8(res.text)
        except Exception as e:
            logger.error(f"{self.plugin_msg}: {api} 获取 m3u8 失败 -> {e}")
        return {}

    async def aget_stream(self, qn_with_codec: dict, protocol: str = 'stream', special_type: int = 0) -> dict:
        """
        :param qn_with_codec: 用户接受的 qn 与 codec
        :param protocol: 流协议
        :param special_type: 特殊直播类型
        :return: 流信息
        """
        stream_urls = {}
        play_info = {}
        for api in self.bili_api_list:
            '''
            一般用户配置均为原画，只传首个 qn 可减少请求次数
            在只有原画的流中，即使请求其他 qn，返回的流信息也是原画
            '''
            play_info = await self.get_play_info(api, list(qn_with_codec.keys())[0])
            if not play_info:
                continue
            if not play_info.get('pwd_verified', True):
                # 无解说声音的赛事转播清流等
                raise Exception("暂不支持密码保护的直播间")
            streams = play_info['playurl_info'].get('playurl', {}).get('stream')
            if not streams:
                continue
            if protocol == 'hls_fmp4':
                if self.bili_anonymous_origin:
                    if special_type in play_info['all_special_types'] and not self.__login_mid:
                        logger.warn(f"{self.plugin_msg}: 特殊直播 {special_type}")
                    else:
                        stream_urls = await self.get_master_m3u8(api)
                        if not stream_urls:
                            continue
                        break
                # 处理 API 信息
                stream = streams[1] if len(streams) > 1 else streams[0]
                for format in stream['format']:
                    if format['format_name'] == 'fmp4':
                        stream_urls = self.parse_stream_url(format['codec'])
                        # fmp4 可能没有原画
                        if qn == 10000 and qn in stream_urls.keys():
                            break
                        else:
                            stream_urls = {}
            else:
                stream_urls = self.parse_stream_url(streams[0]['format'][0]['codec'])
            if stream_urls:
                break
        # 空字典照常返回，重试交给上层方法处理
        return stream_urls

    async def check_login_status(self) -> int:
        """
        检查B站登录状态
        :return: 当前登录用户 mid
        """
        try:
            _res = await client.get(
                'https://api.bilibili.com/x/web-interface/nav',
                headers=self.fake_headers
            )
            user_data = json.loads(_res.text).get('data', {})
            if user_data.get('isLogin'):
                logger.info(f"当前录制用户: {user_data['uname']}")
                return user_data['mid']
            else:
                logger.warning(f"{self.plugin_msg}: 未登录，或将只能录制到最低画质。")
        except Exception as e:
            logger.error(f"{self.plugin_msg}: 登录态校验失败 {e}")
        return 0

    def normalize_cn204(self, url: str) -> str:
        if self.bili_normalize_cn204 and "cn-gotcha204" in url:
            return re.sub(r"(?<=cn-gotcha204)-[1-4]", "", url, 1)
        return url

    def ov2cn(self, host: str) -> str:
        if self.bili_ov2cn:
            return host.replace("ov-", "cn-")
        return host

    def parse_stream_url(self, *args) -> dict:
        suffix_regexp = r'suffix=([^&]+)'
        if isinstance(args[0], str):
            url = args[0]
            host = "https://" + match1(url, r'https?://([^/]+)')
            stream_url = {
                'host': self.ov2cn(host),
                'base_url': url.split("?")[0].split(host)[1] + "?",
                'extra': url.split("?")[1]
            }
            return {
                'url': stream_url,
                'stream_name': match1(url, STREAM_NAME_REGEXP),
                'suffix': match1(url, suffix_regexp)
            }
        elif isinstance(args[0], list):
            multi_codec_streams = args[0]
            streams = {}
            for codec in multi_codec_streams:
                cur_codec: str = codec['codec_name']
                cur_qn: int = codec['current_qn']
                base_url: str = codec['base_url']
                # 先确定画质再确定编码，更方便回退到指定画质的其他编码流
                streams.setdefault(cur_qn, { cur_codec: {} })
                streams[cur_qn][cur_codec] = {
                    'base_url': base_url,
                    'stream_name': match1(base_url, STREAM_NAME_REGEXP),
                }
                for info in codec['url_info']:
                    if "suffix" not in streams[cur_qn][cur_codec]:
                        suffix: str = match1(info['extra'], suffix_regexp)
                        streams[cur_qn][cur_codec]['suffix'] = suffix
                    cdn_name: str = match1(info['extra'], r'cdn=([^&]+)')
                    cdn_info = {
                        'host': self.ov2cn(info['host']),
                        'extra': info['extra']
                    }
                    streams[cur_qn][cur_codec][cdn_name] = cdn_info
        return streams

    def parse_master_m3u8(self, m3u8_content: str) -> dict:
        """
        Returns:
            {
                "code_with_qn": {
                    "cdn_name": {
                        "url": parsed_stream_url,
                        "stream_name": "流名称",
                        "suffix": "二压后缀"
                    }
                }
            }
        """
        lines = m3u8_content.strip().splitlines()
        cur_qn = None
        result = {}
        if not lines[0].startswith('#EXTM3U'):
            raise ValueError('Invalid m3u8 file')
        for line in lines:
            if line.startswith('#EXT-X-STREAM-INF:'):
                codec = match1(line, r'CODECS="([^"]+)"')
                cur_qn = match1(line, r'BILI-QN=(\d+)')

            elif line.startswith('http') and cur_qn is not None:
                cdn_name = match1(line, r'cdn=([^&]+)')
                if cdn_name:
                    result[cur_qn][cdn_name] = self.parse_stream_url(line)

        return dict(sorted(result.items(), key=lambda x: int(x[0]), reverse=True))

# Copy from room-player.js
def check_areablock(data) -> dict:
    '''
    :return: data['data']
    '''
    if data['code'] == 60005:
        logger.error('Sorry, bilibili is currently not available in your country according to copyright restrictions.')
        logger.error('非常抱歉，根据版权方要求，您所在的地区无法观看本直播')
        raise Exception(f'地区限制 {data["message"]}')
    return data['data']

def normalize_url(url: str) -> str:
    return url if url.startswith(('http://', 'https://')) else 'http://' + url