# recorder.py
import shutil
import subprocess
from pathlib import Path
from .commands import FFmpegCommands
from .utils import parse_radiko_time, to_unix_time, to_datetime

class RadikoRecorder:
    def __init__(self, auth_token, area_id, spinner):
        self.auth_token = auth_token
        self.area_id = area_id
        self.spinner = spinner

    def _download_chunk(self, station_id, start_at, current_seek, duration, chunk_file, playlist_url):
        """
        1つのチャンクをダウンロードする。
        失敗した場合は例外を投げる。
        """
        cmd = FFmpegCommands.get_download_cmd(
            self.auth_token, self.area_id, station_id, 
            start_at, current_seek, duration, chunk_file, playlist_url
        )
        subprocess.run(cmd, check=True, timeout=duration + 60)

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
            while left_sec > 5:
            #while left_sec > 0:
                duration = 300 if left_sec >= 300 else int(left_sec)
                chunk_file = tmp_dir / f"chunk_{chunk_no}.m4a"

                # 【可視化】取得開始を告げる
                self.spinner.stop()
                print(f"📦 [{chunk_no}] {to_datetime(current_seek)} 取得開始... (残り {left_sec}s)      ", end="\r")
                self.spinner.start()

                try:
                    # 通常のダウンロード試行
                    self._download_chunk(station_id, start_at, current_seek, duration, chunk_file, playlist_url)
                    # 実再生時間を取得
                    probe_cmd = FFmpegCommands.get_duration_cmd(chunk_file)
                    res = subprocess.check_output(probe_cmd).decode().strip()
                
                    if not res:
                        raise ValueError("Empty Probe Result")

                    actual_duration = int(float(res) + 0.5)

                    if actual_duration == 0: # 0秒チャンクは無限ループの元なので排除
                        raise ValueError("Zero duration chunk")

                    chunk_list.append(chunk_file)

                    # 成功後のステータス更新
                    left_sec -= actual_duration
                    current_seek += actual_duration
                    chunk_no += 1

                    # 【可視化】完了報告
                    self.spinner.stop()
                    print(f"✅ [{chunk_no}] {to_datetime(current_seek - actual_duration)} 完了! (残り {max(0, left_sec)}s)      ", end="\r")
                except (subprocess.CalledProcessError, ValueError, Exception) as e:
                    self.spinner.stop()

                    # 終端間際の「数秒」で 400 Bad Request が出た時の処置
                    if left_sec < 10:
                        print(f"\n⚠️  境界線(残り{left_sec}秒)でエラー。1秒手前で終了！")
                        break # このループを抜けて結合（finalize）へ向かう
                    #else:
                    #    raise # 10秒以上あるのに失敗したのは本物のエラー

                    # これにより、無限ループを防ぎつつ、エラー箇所だけを「穴」として飛ばせるざます！
                    print(f"\n⚠️  障害発生: {to_datetime(current_seek)} 付近...")
                    print(f"   原因: {str(e)[:60]}...")
                    #print(f"   1秒ずらして再試行！")
                    actual_duration = 1
                    left_sec -= actual_duration
                    current_seek += actual_duration
                    # chunk_listには入れない

            if chunk_list:
                self.spinner.start()
                self.finalize(chunk_list, output_file)
                self.spinner.stop()

            if tmp_dir.exists():
                shutil.rmtree(tmp_dir)

            print(f"\n✨ 録音成功: {output_file}")

        except KeyboardInterrupt:
            self.spinner.stop()
            print("\n🛑 手動停止を確認。そこまでの録音を保存！")
            if chunk_list:
                self.finalize(chunk_list, output_file)
            raise
        except Exception as e:
            self.spinner.stop()
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
