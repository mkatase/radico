# utils.py
from datetime import datetime, timedelta, timezone

def parse_radiko_time(time_str: str) -> datetime:
    """14桁の文字列をdatetimeオブジェクトに変換"""
    return datetime.strptime(time_str, '%Y%m%d%H%M%S')

def to_unix_time(dt: datetime) -> int:
    """datetimeをUNIXタイム(int)に変換"""
    return int(dt.timestamp())

def to_datetime(unix_time: int) -> str:
    """UNIXタイムをRadiko用の14桁文字列(JST)に変換"""
    jst = timezone(timedelta(hours=9))
    dt = datetime.fromtimestamp(unix_time, jst)
    return dt.strftime('%Y%m%d%H%M%S')

def handle_midnight_offset(dt: datetime) -> datetime:
    """早朝5時までは前日扱いとする、Radiko伝統の仕様"""
    if dt.hour < 5:
        return dt - timedelta(days=1)
    return dt
