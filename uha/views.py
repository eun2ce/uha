import requests
from bs4 import BeautifulSoup
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import YouTubeChannelSerializer


def get_youtube_channel_info():
    url = f"{settings.BASE_URLS['YOUTUBE']}/channels?id={settings.YOUTUBE_CHANNEL_ID}&part=id,snippet,statistics&key={settings.YOUTUBE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        items = response.json().get("items", [])
        if items:
            return items[0]
        else:
            raise Exception("채널 정보를 찾을 수 없습니다.")
    else:
        raise Exception("YouTube API 호출 실패")


class YouTubeChannelInfo(APIView):
    def get(self, request, *args, **kwargs):
        try:
            channel_info = get_youtube_channel_info()
            serializer = YouTubeChannelSerializer(channel_info)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def get_html(url):
    """네이버 카페 페이지 HTML을 가져오는 함수"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.encoding = "cp949"  # 네이버 카페는 주로 CP949 인코딩 사용
    return response.text if response.status_code == 200 else None


class NaverCafeProfileView(APIView):
    def get(self, request, *args, **kwargs):
        url = f"{settings.BASE_URLS['NAVER_CAFE']}/CafeProfileView.nhn?clubid={settings.NAVER_CAFE_ID}"
        html = get_html(url)
        if not html:
            return Response({"error": "네이버 카페 정보를 가져올 수 없습니다."}, status=400)

        soup = BeautifulSoup(html, "html.parser")
        profile = {
            "name": soup.select_one(".cafe_name").text.strip(),
            "thumbnail": soup.select_one(".mcafe_icon img")["src"],
            "members": soup.select_one(
                "#main-area > div > table > tbody > tr:nth-child(14) > td > span:nth-child(1)").text.strip(),
        }

        return Response(profile, status=200)


class NaverCafeArticlesView(APIView):
    def get(self, request, menu_id, page_id, *args, **kwargs):
        club_id = settings.NAVER_CAFE_ID
        url = f"{settings.BASE_URLS['NAVER_CAFE']}/ArticleList.nhn?search.clubid={club_id}&userDisplay=50&search.boardtype=C&search.cafeId={club_id}&search.page={page_id}&search.menuid={menu_id}"
        html = get_html(url)
        if not html:
            return Response({"error": "게시글 정보를 가져올 수 없습니다."}, status=400)

        soup = BeautifulSoup(html, "html.parser")
        lists = soup.select("#main-area > .article-movie-sub > li")

        data = []
        for li in lists:
            post = {
                "title": li.select_one(".inner").text.replace("\s+", " ").strip(),
                "author": li.select_one(".m-tcol-c").text,
                "date": li.select_one(".date").text,
                "link": "https://m.cafe.naver.com" + li.select_one("a")["href"],
                "image": li.select_one(".movie-img img")["src"] if li.select_one(".movie-img img") else None,
                "text": li.select_one("a").text,
            }
            data.append(post)

        return Response({"result": data, "page": page_id}, status=200)
