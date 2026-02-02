# A Simple Radiko TimeFree Downloader for HLS
radiko(HLS対応版)のTime Free用Downloaderです。
[morinokamiさん](https://github.com/morinokami/radiko-downloader)のScriptと
[うる。さん](https://github.com/uru2/rec_radiko_ts)(HLS対応版)のScriptを参考にし、
[旧版](https://github.com/mkatase/radiko-downloader)を改良したものです。

## Modification Points
- Radiko新仕様(HLS対応)に伴う大幅修正 (v1.0.0)

改修ポイントではないですが、本Scriptは、プレミアムやエリアフリーに非対応です。[うる。さん](https://github.com/uru2/rec_radiko_ts)のScriptは対応されています。

## 開発環境
- Fedora 43 6.18.7-200.fc43.x86_64
- Python 3.14.2
- ffmpeg 7.1.2

## Addtional Programs
- ffmpeg

```bash
$ sudo dnf install ffmpeg
```

## Addtional Python Modules
追加モジュールは以下の通りです。
- halo
- lxml
- requests

## Install radico
インストール方法は以下の通り。
```
$ pip install git+https://github.com/mkatase/radico.git
```

## Usage
使用方法は、オリジナルのものに加えて、局と時間を指定する２つのモードがあります。ただし、Script名は変更されていますので、ご注意ください。

[radiko.jp](http://radiko.jp/)の[タイムフリー](http://radiko.jp/#!/timeshift)のページからダウンロードしたい番組を表示し、URLをコピーします。そしてターミナルから、次のようにプログラムを起動してください:

### パターン１
```bash
$ radico 'http://radiko.jp/#!/ts/<station_id>/<ft>'
```
### パターン2
```bash
$ radico -b <station_id> -d <ft>
```

`<station_id>`にはアルファベットの大文字やハイフンが、また`<ft>`には数字がそれぞれ含まれているはずです。URL指定の場合は、シングルクオート（`'`）で囲むことを忘れないようにしてください。  
パターン2の桁数は、URLベースの14桁でも、秒の桁を除いた12桁でも実行可能です。

## 出力ファイル
出力ファイル名は、{日付}_{番組名}.aacとなっています。

## Thanks to
- [morinokamiさん](https://github.com/morinokami)
- [うる。さん](https://github.com/uru2/rec_radiko_ts)
- Gemini
