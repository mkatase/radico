# manager.py
from .utils import parse_radiko_time, handle_midnight_offset
from .auth import RadikoAuth
from .program import RadikoProgram
from .recorder import RadikoRecorder
from .commands import FFmpegCommands
from .constants import OVERWRITE
from pathlib import Path
from halo import Halo

class RadikoManager:
    def __init__(self):
        self.spinner = Halo(text='準備中...', spinner='dots')

    def execute(self, station_id, start_at):
        """昨日の main.py にあった『録音までの全工程』をここに移植"""
        self.spinner.start()
        try:
            # --- 認証 ---
            self.spinner.text = '鍵（Token）を生成中...'
            auth = RadikoAuth()
            token, area_id = auth.authenticate()

            # --- 5時境界とメタデータ取得 ---
            self.spinner.text = '番組情報を取得中...'
            prog = RadikoProgram(area_id)
            playlist_url = prog.fetch_playlist_url(station_id)
            
            dt_start = parse_radiko_time(start_at)
            api_dt = handle_midnight_offset(dt_start)
            api_date = api_dt.strftime('%Y%m%d')
            title, end_at = prog.fetch_program_meta(station_id, api_date, start_at)

            # --- 出力ファイルの有無チェック
            output_file = Path(f"{start_at[:8]}_{title}.aac") # 既存の命名規則

            if not OVERWRITE and output_file.exists():
                self.spinner.stop()
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                print(f"⚠️ Skip: 【{title}】")
                print(f"👉 同名ファイルが存在するため、録音をスキップ！")
                print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                return # ここで終了！

            self.spinner.stop()
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"▶ 録音対象: 【{title}】")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.spinner.start('録音中...')

            # 録音実行 (recorderはいじらない) ---
            FFmpegCommands.check_env()
            recorder = RadikoRecorder(token, area_id, self.spinner)
            recorder.record(station_id, start_at, end_at, playlist_url, title)

        except Exception as e:
            self.spinner.fail(f"停止しました: {e}")
