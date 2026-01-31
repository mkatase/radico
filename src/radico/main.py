import sys
import re
import argparse
from .manager import RadikoManager  # 司令官を呼ぶだけ
from .constants import APP_NAME, VERSION, COPYRIGHT

def main():
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME} - {COPYRIGHT}",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-v", "--version", action="version", version=f"{APP_NAME} v{VERSION}")
    parser.add_argument("-b", "--broadcast", help="放送局ID (例: QRR)")
    parser.add_argument("-d", "--date", help="日時 (12/14桁)")
    parser.add_argument("url", nargs="?", help="番組URL")

    args = parser.parse_args()
    mgr = RadikoManager()

    # URL指定がある場合 (最優先)
    if args.url:
        m = re.search(r'ts/([A-Z0-9_-]+)/([0-9]{14})', args.url)
        if m:
            mgr.execute(*m.groups())
        else:
            print("❌ Error: URLの形式が正しくありません")

    # -b と -d 指定がある場合
    elif args.broadcast and args.date:
        start_at = args.date + "00" if len(args.date) == 12 else args.date
        mgr.execute(args.broadcast, start_at)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
