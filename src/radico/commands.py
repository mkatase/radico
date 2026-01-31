# commands.py
import shutil
import secrets
from .utils import to_datetime

class FFmpegCommands:
    @staticmethod
    def check_env():
        if not shutil.which("ffmpeg") or not shutil.which("ffprobe"):
            raise EnvironmentError("FFmpeg or FFprobe not found in PATH.")

    @staticmethod
    def get_download_cmd(token, area_id, station_id, start_at, seek_unix, duration, output, playlist_url):
        """
        中継サーバ(playlist_url)に対し、
        start_at(番組開始), seek(現在地), end_at(チャンク終点)を三位一体で送る
        """
        seek_str = to_datetime(seek_unix)
        end_at_str = to_datetime(seek_unix + duration)
        lsid = secrets.token_hex(16)

        params = (
            f"station_id={station_id}&start_at={start_at}&ft={start_at}"
            f"&seek={seek_str}&end_at={end_at_str}&to={end_at_str}"
            f"&l={duration}&lsid={lsid}&type=c"
        )
        
        full_url = f"{playlist_url}?{params}"
        # 余計な空白を含まない、厳密なヘッダー形式
        header = f"X-Radiko-Authtoken: {token}\r\nX-Radiko-AreaId: {area_id}"

        return [
            "ffmpeg", "-nostdin", "-loglevel", "error",
            "-fflags", "+discardcorrupt",
            "-headers", header,
            "-http_seekable", "0",
            "-i", full_url,
            "-acodec", "copy", "-vn",
            "-bsf:a", "aac_adtstoasc", "-y", str(output)
        ]

    @staticmethod
    def get_duration_cmd(file_path):
        return [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(file_path)
        ]

    @staticmethod
    def get_concat_cmd(list_file, output_path):
        return [
            "ffmpeg", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(list_file),
            "-c", "copy", "-y", str(output_path)
        ]
