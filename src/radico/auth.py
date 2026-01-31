# auth.py
import requests
import base64
import hashlib
from typing import Tuple, Optional

class RadikoAuth:
    """
    Radiko認証クラス v1.0.0
    Seleniumを廃止し、ピュアなHTTPリクエストで認証を完結させる。
    """
    AUTH_KEY = "bcd151073c03b352e1ef2fd66c32209da9ca0afa"
    APP_NAME = "pc_html5"
    USER_ID  = "test-stream"
    DEVICE   = "pc"

    def __init__(self, session: Optional[requests.Session] = None):
        self.session = session or requests.Session()
        self.authtoken = None
        self.area_id = None

    def authenticate(self) -> Tuple[str, str]:
        """Auth1 & Auth2 を実行し、トークンとエリアIDを返す"""
        
        # --- Auth1 ---
        headers = {
            "X-Radiko-App": self.APP_NAME,
            "X-Radiko-App-Version": "0.0.1",
            "X-Radiko-Device": "pc",
            "X-Radiko-User": "dummy_user",
        }
        res1 = self.session.get("https://radiko.jp/v2/api/auth1", headers=headers)
        res1.raise_for_status()

        self.authtoken = res1.headers["x-radiko-authtoken"]
        offset = int(res1.headers["x-radiko-keyoffset"])
        length = int(res1.headers["x-radiko-keylength"])

        # Partial Keyの生成（ここがHLS対応の肝のひとつ）
        partial_key = base64.b64encode(
            self.AUTH_KEY[offset : offset + length].encode("utf-8")
        ).decode("utf-8")

        # --- Auth2 ---
        headers2 = {
            "x-radiko-authtoken": self.authtoken,
            "x-radiko-partialkey": partial_key,
            "x-radiko-device": self.DEVICE,
        }
        res2 = self.session.get("https://radiko.jp/v2/api/auth2", headers=headers2)
        res2.raise_for_status()

        # エリアIDの抽出 (例: JP13, JP14など)
        self.area_id = res2.text.split(",")[0].strip()
        
        return self.authtoken, self.area_id

    def get_headers(self) -> dict:
        """FFmpeg等で使用する共通ヘッダー"""
        return {
            "X-Radiko-Authtoken": self.authtoken,
            "X-Radiko-AreaId": self.area_id
        }
