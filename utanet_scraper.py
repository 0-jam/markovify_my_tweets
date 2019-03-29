import argparse
import json
import urllib
import time
from tqdm import tqdm
from beautifulscraper import BeautifulScraper

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


# ページをBeautifulSoupオブジェクトとして取得
def get_page(url):
    body = scraper.go(url)
    time.sleep(1.0)

    return body


def bs_get_text(elem):
    return elem.get_text()


def search(query, attribute='lyricist'):
    # 検索URLを生成
    # クエリが日本語だと正しく処理されないのでエンコード
    search_url = domain + '/search/?Aselect=' + attributes[attribute] + '&Keyword=' + urllib.parse.quote(query) + '&Bselect=4&sort='

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
    titles = []
    artists = []
    lyricists = []
    composers = []
    for body in bodies:
        # 曲名と歌詞ページのURLを抽出
        for td in body.select('.td1'):
            song_ids.append(td.find_all('a')[0].get('href'))
            titles.append(bs_get_text(td))

        # 歌手名を抽出
        for td in body.select('.td2'):
            artists.append(bs_get_text(td))

        # 作詞者名を抽出
        for td in body.select('.td3'):
            lyricists.append(bs_get_text(td))

        # 作曲者名を抽出
        for td in body.select('.td4'):
            composers.append(bs_get_text(td))

    return (song_ids, titles, artists, lyricists, composers)


# song_idから歌詞を抽出
def extract_lyric(song_id):
    song_url = domain + song_id

    body = get_page(song_url)
    # 歌詞内の改行を半角スラッシュ/に置換して抽出
    lyric = body.find(id='kashi_area').get_text('/')

    return lyric


def main():
    parser = argparse.ArgumentParser(description='引数に指定した名前で作詞家を検索して曲情報を抽出')
    parser.add_argument('query', type=str, help='検索したい名前')
    parser.add_argument('-o', '--output', type=str, default='songs.json', help="出力ファイル名（デフォルト：'./songs.json'）")
    parser.add_argument('-a', '--attribute', type=str, default='lyricist', choices=['title', 'artist', 'lyricist', 'composer'], help="検索したい属性（デフォルト：'lyricist'（作詞者））")
    args = parser.parse_args()

    (song_ids, titles, artists, lyricists, composers) = search(args.query, attribute=args.attribute)
    results = {
        song_id: {
            'title': title,
            'artist': artist,
            'lyricist': lyricist,
            'composer': composer,
            'lyric': extract_lyric(song_id)
        } for song_id, title, artist, lyricist, composer in zip(tqdm(song_ids), titles, artists, lyricists, composers)
    }

    with open(args.output, 'w', encoding='utf-8') as out:
        # json.dumps(results, out)だと最後の波カッコが閉じられない
        out.write(json.dumps(results, ensure_ascii=False, indent=4))


if __name__ == '__main__':
    main()
