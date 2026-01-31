# recorder.py
import shutil
import subprocess
from pathlib import Path
from .commands import FFmpegCommands
from .utils import parse_radiko_time, to_unix_time

class RadikoRecorder:
    def __init__(self, auth_token, area_id, spinner):
        self.auth_token = auth_token
        self.area_id = area_id
        self.spinner = spinner

    def record(self, station_id, start_at, end_at, playlist_url, title):
        """情報の整合性確認は program.py が済ませている前提で実行"""
        start_unix = to_unix_time(parse_radiko_time(start_at))
        end_unix = to_unix_time(parse_radiko_time(end_at))
        current_seek = start_unix
        left_sec = end_unix - start_unix
        
        # 主のこだわり: 日付_タイトル.aac
        output_file = Path(f"{start_at[:8]}_{title}.aac")
        tmp_dir = Path("./tmp_chunks")
        tmp_dir.mkdir(exist_ok=True)
        chunk_list = []

        try:
            chunk_no = 0
            while left_sec > 0:
                duration = 300 if left_sec >= 300 else int(left_sec)
                chunk_file = tmp_dir / f"chunk_{chunk_no}.m4a"

                cmd = FFmpegCommands.get_download_cmd(
                    self.auth_token, self.area_id, station_id, 
                    start_at, current_seek, duration, chunk_file, playlist_url
                )
                # FFmpeg実行
                subprocess.run(cmd, check=True)

                # 実再生時間を取得
                probe_cmd = FFmpegCommands.get_duration_cmd(chunk_file)
                res = subprocess.check_output(probe_cmd).decode().strip()
                actual_duration = int(float(res) + 0.5)

                chunk_list.append(chunk_file)
                left_sec -= actual_duration
                current_seek += actual_duration
                chunk_no += 1

            self.finalize(chunk_list, output_file)

            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)

            print(f"\n✨ 録音成功: {output_file}")

        except Exception as e:
            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)
            raise e
        finally:
            self.spinner.stop()

    def finalize(self, chunk_list, output_file):
        list_file = Path("./tmp_chunks/list.txt")
        with open(list_file, "w") as f:
            for c in chunk_list:
                f.write(f"file '{c.name}'\n")
        
        subprocess.run(FFmpegCommands.get_concat_cmd(list_file, output_file), check=True)
        # 後片付け
        for c in chunk_list: c.unlink()
        list_file.unlink()
