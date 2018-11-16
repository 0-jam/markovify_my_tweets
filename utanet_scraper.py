from beautifulscraper import BeautifulScraper
import urllib
import argparse
import time
from tqdm import tqdm

scraper = BeautifulScraper()
domain = "https://www.uta-net.com"

## queryで作詞家を検索
def search(query):
    # 検索URLを生成
    # クエリが日本語だと正しく処理されないのでエンコード
    search_url = domain + "/search/?Aselect=3&Keyword=" + urllib.parse.quote(query) + "&Bselect=4&sort="

    body = scraper.go(search_url)

    urls = []
    # 1ページ目
    for td in body.select(".td1"):
        # "/song/21496/"の形で抽出される
        urls.append(td.find_all("a")[0].get("href"))

    # 2ページ目以降（あれば）
    try:
        pages = body.select("#page_list")[0]
        last_page = urllib.parse.urlparse(pages.find_all("a")[-1].get("href"))
        lpq = urllib.parse.parse_qs(last_page.query)
        last_page_num = int(lpq["pnum"][0])

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

            body = scraper.go(page_url)

            for td in body.select(".td1"):
                urls.append(td.find_all("a")[0].get("href"))
    except IndexError:
        pass

    return urls

## song_idから歌詞を抽出
def extract_lyric(song_id):
    song_url = domain + song_id

    body = scraper.go(song_url)

    return body.find(id="kashi_area").get_text("／")

def extract_lyrics(song_ids):
    lyrics = []

    for song_id in tqdm(song_ids):
        lyrics.append(extract_lyric(song_id))
        time.sleep(1.0)

    return lyrics

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="引数に指定した名前で作詞家を検索して歌詞を抽出")
    parser.add_argument("query", type=str, help="検索したい名前")
    parser.add_argument("-o", "--output", type=str, default="lyrics.txt", help="出力ファイル名（デフォルト：'./lyrics.txt'）")
    args = parser.parse_args()

    song_ids = search(args.query)

    lyrics = extract_lyrics(song_ids)

    with open(args.output, "w") as out:
        out.write("\n".join(lyrics))
