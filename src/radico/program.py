# program.py
import requests
from lxml import etree

class RadikoProgram:
    def __init__(self, area_id):
        self.area_id = area_id

    def fetch_playlist_url(self, station_id):
        """局XMLから Smartstream 等の中継サーバURLを取得"""
        url = f"https://radiko.jp/v3/station/stream/pc_html5/{station_id}.xml"
        res = requests.get(url)
        root = etree.fromstring(res.content)
        # 主の hoge ロジック：タイムフリー用URLを一本釣り
        xpath = "/urls/url[@timefree='1' and @areafree='0']/playlist_create_url/text()"
        result = root.xpath(xpath)
        if not result:
            raise ValueError(f"Playlist URL not found for {station_id}")
        return result[0]

    def fetch_program_meta(self, station_id, api_date, start_at):
        """番組表XMLから『タイトル』と『終了時刻』を取得"""
        """
        api_date: 5時境界を考慮した「番組表の取得用日付」
        start_at: 検索したい番組の「本来の開始時間(14桁)」
        """
        url = f"https://api.radiko.jp/program/v3/date/{api_date}/area/{self.area_id}.xml"
        res = requests.get(url)
        root = etree.fromstring(res.content)
        ## 【デバッグ用】その局の番組開始時間を全部出すざます
        #progs = root.xpath(f"//station[@id='{station_id}']/progs/prog")
        #print(f"\n--- {station_id} の番組リスト ({api_date}) ---")
        #for p in progs:
        #    print(f"ID: {p.get('ft')} | Title: {p.findtext('title')}")
        #print("--------------------------------------")
        # 主の hoge ロジック：指定時刻の番組を特定
        xpath = f"//station[@id='{station_id}']/progs/prog[@ft='{start_at}']"
        nodes = root.xpath(xpath)
        if not nodes:
            raise ValueError(f"Program not found: {station_id} at {start_at}")
        
        node = nodes[0]
        title = node.xpath("./title/text()")[0]
        end_at = node.get("to") # 14桁の終了時刻
        return title, end_at
