# UHA

[demo video](https://youtu.be/demk_b-eLPM?feature=shared)

## 유튜버 우주하마 팬 웹앱

유튜브 API와 네이버 데이터 크롤링을 활용하여 필요한 정보들을 추려 제공합니다.

![](https://github.com/user-attachments/assets/156d319a-3b5d-4859-bec3-104f9e8a0491)

### 기능

* 유튜브 채널 정보
* 실시간 라이브 다시보기 링크 – 일부 공개된 URL을 자동으로 정리
  * GitHub Actions를 활용하여 일정 주기로 라이브 여부를 확인 및 링크 크롤링 하여 연도 및 날짜별로 정리된 [다시보기 링크](https://github.com/eun2ce/uzuhama-live-link) 제공
* 네이버 카페 인기 게시글 및 공지 확인 - 팬카페의 주요 소식과 인기 글 제공
  * bs4기반 크롤링

### 사용기술

react native, Django

## Getting Started

### youtube api key 발급

### env 작성

프로젝트 root 에 아래와 같은 내용이 작성

```
YOUTUBE_API_KEY="*"
YOUTUBE_CHANNEL_ID="UC2NFRq9s2neD_Ml0tPhNC2Q"
NAVER_CAFE_ID="30027092"
```

### server run

```
$ conda create -n uha python=3.11
$ conda activate uha
$ pip install -r requriements.txt
$ python manage.py runserver
```
