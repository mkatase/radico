# manager.py
from .utils import parse_radiko_time, handle_midnight_offset
from .auth import RadikoAuth
from .program import RadikoProgram
from .recorder import RadikoRecorder
from .commands import FFmpegCommands
from halo import Halo

class RadikoManager:
    def __init__(self):
        self.spinner = Halo(text='準備中...', spinner='dots')

    def execute(self, station_id, start_at):
        """昨日の main.py にあった『録音までの全工程』をここに移植"""
        self.spinner.start()
        try:
            # --- 昨日の main の中身 1: 認証 ---
            self.spinner.text = '鍵（Token）を生成中...'
            auth = RadikoAuth()
            token, area_id = auth.authenticate()

            # --- 昨日の main の中身 2: 5時境界とメタデータ取得 ---
            self.spinner.text = '番組情報を取得中...'
            prog = RadikoProgram(area_id)
            playlist_url = prog.fetch_playlist_url(station_id)
            
            dt_start = parse_radiko_time(start_at)
            api_dt = handle_midnight_offset(dt_start)
            api_date = api_dt.strftime('%Y%m%d')
            title, end_at = prog.fetch_program_meta(station_id, api_date, start_at)

            self.spinner.stop()
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"▶ 録音対象: 【{title}】")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            self.spinner.start('録音中...')

            # --- 昨日の main の中身 3: 録音実行 (recorderはいじらない) ---
            FFmpegCommands.check_env()
            recorder = RadikoRecorder(token, area_id, self.spinner)
            recorder.record(station_id, start_at, end_at, playlist_url, title)

        except Exception as e:
            self.spinner.fail(f"停止しました: {e}")
