# constants.py
# (C) 2026 Ulmus Studio
# Licensed under the MIT License.

APP_NAME  = "radico"
VERSION   = "1.0.0"
DEVDATE   = "2026-02-01"
COPYRIGHT = "Copyright (C) 2026 Ulmus Studio"

# エンドポイントは program.py のロジックに準拠
STATION_XML_URL = "https://radiko.jp/v3/station/stream/pc_html5/{station_id}.xml"
PROG_API_URL    = "https://api.radiko.jp/program/v3/date/{api_date}/area/{area_id}.xml"

# 認証系
AUTH1_URL = "https://radiko.jp/v2/api/auth1"
AUTH2_URL = "https://radiko.jp/v2/api/auth2"
