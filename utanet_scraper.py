import argparse
import json
import urllib
import time
from tqdm import tqdm
from beautifulscraper import BeautifulScraper
from modules.multi_sub import replace_str
import unicodedata

scraper = BeautifulScraper()
domain = "https://www.uta-net.com"

## queryで作詞家を検索
def search(query):
    # 検索URLを生成
    # クエリが日本語だと正しく処理されないのでエンコード
    search_url = domain + "/search/?Aselect=3&Keyword=" + urllib.parse.quote(query) + "&Bselect=4&sort="

    bodies = [scraper.go(search_url)]

    try:
        pages = bodies[0].select("#page_list")[0].find_all("a")
        page_urls = [urllib.parse.urlparse(page.get("href")) for page in pages]
        queries = [urllib.parse.parse_qs(page.query) for page in page_urls]
        last_page = page_urls[-1]
        last_page_num = max([int(query["pnum"][0]) for query in queries])
        lpq = queries[-1]

        for pnum in range(2, last_page_num + 1):
            # ページ番号だけ変えて新しくURLを生成
            lpq["pnum"] = [str(pnum)]
            page = urllib.parse.ParseResult(
                last_page.scheme,
                last_page.netloc,
                last_page.path,
                last_page.params,
                urllib.parse.urlencode(lpq, True),
                ""
            )
            page_url = urllib.parse.urlunparse(page)

            bodies.append(scraper.go(page_url))
    except IndexError:
        pass

    song_ids = []
    titles = []
    artists = []
    lyricists = []
    composers = []
    for body in bodies:
        # 曲名と歌詞ページのURLを抽出
        for td in body.select(".td1"):
            song_ids.append(td.find_all("a")[0].get("href"))
            titles.append(td.get_text())

        # 歌手名を抽出
        for td in body.select(".td2"):
            artists.append(td.get_text())

        # 作詞者名を抽出
        for td in body.select(".td3"):
            lyricists.append(td.get_text())

        # 作曲者名を抽出
        for td in body.select(".td4"):
            composers.append(td.get_text())

    return (song_ids, titles, artists, lyricists, composers)

## song_idから歌詞を抽出
def extract_lyric(song_id):
    song_url = domain + song_id

    body = scraper.go(song_url)
    # 歌詞内の改行を半角スラッシュ/に置換して抽出
    lyric = body.find(id="kashi_area").get_text("/")

    # すべての全角英数字，丸括弧（），全角スペース　，！，？などをそれぞれ半角に置換
    lyric = unicodedata.normalize('NFKC', lyric)
    # 3つ以上続くピリオド..., 全角ピリオド・・・を三点リーダー…に置換
    # （上記normalize()で三点リーダーがピリオド3つに置換されているのをここで戻している）
    # 2回以上続く三点リーダー……を1つ…にする
    # 各要素：(置換したい文字, 置換先の文字)
    patterns = [(r"\.{3,}", "…"), (r"・{3,}", "…"), (r"…{2,}", "…")]

    return replace_str(lyric, patterns)

def extract_lyrics(song_ids):
    lyrics = []

    for song_id in tqdm(song_ids, desc="Extracting lyrics..."):
        lyrics.append(extract_lyric(song_id))
        time.sleep(1.0)

    return lyrics

## queryで作詞家を検索して情報を抽出
# 戻り値はdict
def search_songs(query):
    (song_ids, titles, artists, lyricists, composers) = search(query)

    lyrics = extract_lyrics(song_ids)

    results = {}
    for song_id, title, artist, lyricist, composer, lyric in zip(song_ids, titles, artists, lyricists, composers, lyrics):
        results[song_id]={
            'title': unicodedata.normalize('NFKC', title),
            'artist': artist,
            'lyricist': lyricist,
            'composer': composer,
            'lyric': lyric
        }

    return results

def main():
    parser = argparse.ArgumentParser(description="引数に指定した名前で作詞家を検索して曲情報を抽出")
    parser.add_argument("query", type=str, help="検索したい名前")
    parser.add_argument("-o", "--output", type=str, default="songs.json", help="出力ファイル名（デフォルト：'./songs.json'）")
    args = parser.parse_args()

    results = search_songs(args.query)

    with open(args.output, "w", encoding='utf-8') as out:
        # json.dumps(results, out)だと最後の波括弧が閉じられない
        out.write(json.dumps(results, ensure_ascii=False, indent=4))

if __name__ == "__main__":
    main()
