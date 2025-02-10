import asyncio

import httpx
from datetime import datetime, time, timezone, timedelta
from biliup.config import config
import logging


# This setup works very well on my Swedish machine, but who knows about others...
DEFAULT_TIMEOUT = httpx.Timeout(timeout=15.0, connect=10.0)
DEFAULT_MAX_RETRIES = 2
DEFAULT_CONNECTION_LIMITS = httpx.Limits(max_connections=100, max_keepalive_connections=100)

client = httpx.AsyncClient(http2=True, follow_redirects=True, timeout=DEFAULT_TIMEOUT, limits=DEFAULT_CONNECTION_LIMITS)
loop = asyncio.get_running_loop()
logger = logging.getLogger('biliup')


def get_duration(segment_time_str, time_range):
    """
    计算当前时间到给定结束时间的时差
    如果计算的时差大于segment_time，则返回segment_time。
    """
    if not time_range or '-' not in time_range:
        return segment_time_str
    end_time_str = time_range.split('-')[1]

    now = datetime.now()
    end_time_today_str = now.strftime("%Y-%m-%d") + " " + end_time_str
    end_time_today = datetime.strptime(end_time_today_str, "%Y-%m-%d %H:%M:%S")
    # 判断结束时间是否是第二天的时间
    if now > end_time_today:
        end_time_today += timedelta(days=1)

    time_diff = end_time_today - now
    if segment_time_str:
        segment_time_parts = list(map(int, segment_time_str.split(":")))
        segment_time = timedelta(hours=segment_time_parts[0],
                                 minutes=segment_time_parts[1], seconds=segment_time_parts[2])

        if time_diff > segment_time:
            return segment_time_str

    # 增加10s，防止time_diff过小多次执行下载
    if time_diff.total_seconds() <= 60:
        time_diff = time_diff + timedelta(seconds=10)

    hours, remainder = divmod(time_diff.total_seconds(), 3600)
    minutes, seconds = divmod(remainder, 60)

    to_parameter = f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    return to_parameter

def check_timerange(name):
    time_range = config['streamers'].get(name, {}).get('time_range')
    now = datetime.now(tz=timezone(timedelta(hours=8))).time()
    logger.debug(f"{name}: 校验时间范围 {time_range} 当前时间 {now.strftime('%H:%M:%S')}")

    if not time_range or '-' not in time_range:
        return True

    try:
        start_time, end_time = map(time_string_to_time, time_range.split('-'))
    except (ValueError, IndexError) as e:
        logger.exception(f"Invalid time range format: {e}")
        return True

    if start_time > end_time:
        is_in_range = now >= start_time or now <= end_time
    else:
        is_in_range = start_time <= now <= end_time
    return is_in_range


def time_string_to_time(time_string):
    h, m, s = map(int, time_string.split(':'))
    return time(h, m, s)
