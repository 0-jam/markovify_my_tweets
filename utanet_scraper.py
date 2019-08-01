import argparse
import json
import time
import urllib

from beautifulscraper import BeautifulScraper
from tqdm import tqdm

scraper = BeautifulScraper()
domain = 'https://www.uta-net.com'
attributes = {
    # 歌手名
    'artist': '1',
    # 曲名
    'title': '2',
    # 作詞者名
    'lyricist': '3',
    # 作曲者名
    'composer': '8',
}
match_modes = {
    # 完全一致
    'exact': '4',
    # 部分一致
    'partial': '3',
}


# ページをBeautifulSoupオブジェクトとして取得
def get_page(url):
    body = scraper.go(url)
    time.sleep(1.0)

    return body


def bs_get_text(elem):
    return elem.get_text()


def search(query, attribute='lyricist', match_mode='exact'):
    # 検索URLを生成
    # クエリが日本語だと正しく処理されないのでエンコード
    search_url = domain + '/search/?Aselect=' + attributes[attribute] + '&Keyword=' + urllib.parse.quote(query) + '&Bselect=' + match_modes[match_mode] + '&sort='
    print('Retrieving lyrics list from:', search_url)

    bodies = [get_page(search_url)]

    pages = bodies[0].select('#page_list')[0].find_all('a')
    if len(pages) > 0:
        page_urls = [urllib.parse.urlparse(page.get('href')) for page in pages]
        queries = [urllib.parse.parse_qs(page.query) for page in page_urls]
        last_page = page_urls[-1]
        last_page_num = max([int(query['pnum'][0]) for query in queries])
        lpq = queries[-1]
        print(last_page_num, 'pages found')

        for pnum in tqdm(range(2, last_page_num + 1)):
            # ページ番号だけ変えて新しくURLを生成
            lpq['pnum'] = [str(pnum)]
            page = urllib.parse.ParseResult(
                last_page.scheme,
                last_page.netloc,
                last_page.path,
                last_page.params,
                urllib.parse.urlencode(lpq, True),
                ''
            )
            page_url = urllib.parse.urlunparse(page)

            bodies.append(get_page(page_url))
    else:
        print('1 page found')

    song_ids = []
    for body in bodies:
        # 歌詞ページのURLを抽出
        for td in body.select('.td1'):
            song_ids.append(td.find_all('a')[0].get('href'))

    return song_ids


# song_idから歌詞などの情報を抽出
def extract_song(song_id):
    song_url = domain + song_id

    body = get_page(song_url)
    title = body.select('.title h2')[0].text
    # 歌詞内の改行を半角スラッシュ/に置換して抽出
    lyric = body.find(id='kashi_area').get_text('/')
    artist = body.select('h3[itemprop="recordedAs"]')[0].text
    lyricist = body.select('h4[itemprop="lyricist"]')[0].text
    composer = body.select('h4[itemprop="composer"]')[0].text

    return {
        'title': title,
        'lyric': lyric,
        'artist': artist,
        'lyricist': lyricist,
        'composer': composer,
    }


def main():
    parser = argparse.ArgumentParser(description='引数に指定した名前で作詞家を検索して曲情報を抽出')
    parser.add_argument('query', type=str, help='検索したい名前')
    parser.add_argument('-o', '--output', type=str, default='songs.json', help="出力ファイル名（デフォルト：'./songs.json'）")
    parser.add_argument('-a', '--attribute', type=str, default='lyricist', choices=['title', 'artist', 'lyricist', 'composer'], help="検索したい属性（デフォルト：'lyricist'（作詞者））")
    parser.add_argument('-m', '--match_mode', type=str, default='exact', choices=['exact', 'partial'], help="検索モード（デフォルト：'exact'（完全一致））")
    args = parser.parse_args()

    song_ids = search(args.query, attribute=args.attribute, match_mode=args.match_mode)

    songs = {song_id: extract_song(song_id) for song_id in tqdm(song_ids)}

    with open(args.output, 'w', encoding='utf-8') as out:
        # json.dumps(songs, out)だと最後の波カッコが閉じられない
        out.write(json.dumps(songs, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
