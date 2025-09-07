# UHA Backend

YouTube Data API와 Naver 카페 크롤링을 기반으로 한 웹앱의 FastAPI 백엔드입니다.

## 주요 기능

- YouTube 채널 정보 및 최근 영상 조회
- Naver 카페 프로필 및 게시글 조회
- LM Studio(Qwen3) 연동을 통한 라이브 스트림 데이터 요약
- uzuhama-live-link 서브모듈 데이터 분석

## 설정

1. 환경 변수 설정:
   ```bash
   cp env.example .env
   ```

2. `.env` 파일에서 다음 값들을 설정:
   - `UHA_YOUTUBE_API_KEY`: YouTube Data API v3 키
   - `UHA_YOUTUBE_CHANNEL_ID`: 조회할 YouTube 채널 ID
   - `UHA_NAVER_CAFE_ID`: 조회할 Naver 카페 ID

## LM Studio 설정

1. [LM Studio](https://lmstudio.ai/) 다운로드 및 설치
2. Qwen3 모델 다운로드
3. 로컬 서버 시작 (기본 포트: 1234)
   ```
   http://localhost:1234
   ```

## 실행

```bash
# 의존성 설치
uv sync

# 개발 서버 실행
uvicorn uha.backend.main:app --reload --host 0.0.0.0 --port 8000
```

## API 엔드포인트

### YouTube
- `GET /youtube/channel-info` - 채널 정보 및 최근 영상

### Naver Cafe
- `GET /naver-cafe/profile` - 카페 프로필 정보
- `GET /naver-cafe/articles/{menu_id}/{page_id}` - 카페 게시글 목록

### LLM (요약 기능)
- `POST /llm/summarize` - 텍스트 요약
- `POST /llm/summarize-live-streams` - 라이브 스트림 데이터 요약
- `GET /llm/health` - LM Studio 연결 상태 확인

### 기타
- `GET /health` - 서버 상태 확인
- `GET /docs` - API 문서 (Swagger UI)

## 프로젝트 구조

```
src/uha/backend/
├── api/
│   ├── youtube.py      # YouTube API 엔드포인트
│   ├── naver_cafe.py   # Naver 카페 API 엔드포인트
│   └── llm.py          # LLM 연동 API 엔드포인트
├── main.py             # FastAPI 앱 설정
├── settings.py         # 설정 관리
└── container.py        # 의존성 주입 컨테이너
```