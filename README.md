# UHA (Uzuhama Hub Application)

![Image](https://github.com/user-attachments/assets/56f60526-72c0-4f36-8e0e-4ca9ba8e6569)

## 프로젝트 구조

```
uha/
├── features/                           # 공유 라이브러리
│   ├── uha-shared_kernel/             # 공통 도메인 로직
│   ├── uha-shared_kernel-infra-fastapi/  # FastAPI 인프라
│   └── uha-shared-kernel-infra-database-sqla/  # SQLAlchemy 인프라
├── projects/                          # 애플리케이션
│   ├── uha-backend/                   # FastAPI 백엔드
│   └── uha-frontend/                  # React Native 프론트엔드
└── uzuhama-live-link/                 # 서브모듈 (라이브 스트림 데이터)
```

## 주요 기능

- YouTube 채널 정보 및 최근 영상 조회
- Naver 카페 프로필 및 게시글 크롤링
- React Native 기반 크로스 플랫폼 UI
- **LM Studio Qwen3 연동**: 로컬 AI 모델을 통한 텍스트 요약
- **라이브 스트림 데이터 분석**: uzuhama-live-link 서브모듈 데이터 AI 요약
- **연도별 데이터 조회**: 2020-2025년 라이브 스트림 기록 분석
- **패턴 분석**: AI가 분석한 활동 패턴 및 특징 제공

## 빠른 시작

### 1. 저장소 클론 및 서브모듈 초기화
```bash
git clone <repository-url>
cd uha
git submodule update --init --recursive
```

### 2. LM Studio 설정
1. [LM Studio](https://lmstudio.ai/) 다운로드 및 설치
2. Qwen3 모델 다운로드
3. 로컬 서버 시작 (http://localhost:1234)

### 3. 백엔드 설정 및 실행
```bash
cd uha/projects/uha-backend

# 환경 변수 설정
cp env.example .env
# .env 파일에서 API 키들 설정

# 의존성 설치 및 실행
uv sync
uvicorn uha.backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 프론트엔드 설정 및 실행
```bash
cd uha/projects/uha-frontend

# 의존성 설치
npm install

# 웹에서 실행
npm run web
```

## 환경 변수 설정

백엔드 `.env` 파일에서 다음 값들을 설정해야 합니다:

```env
# YouTube API
UHA_YOUTUBE_API_KEY=your_youtube_api_key
UHA_YOUTUBE_CHANNEL_ID=your_channel_id

# Naver Cafe
UHA_NAVER_CAFE_ID=your_cafe_id

# LM Studio
UHA_LM_STUDIO_URL=http://localhost:1234
```

## API 엔드포인트

### YouTube
- `GET /youtube/channel-info` - 채널 정보 및 최근 영상

### Naver Cafe  
- `GET /naver-cafe/profile` - 카페 프로필
- `GET /naver-cafe/articles/{menu_id}/{page_id}` - 게시글 목록

### LLM (AI 요약) ✨
- `POST /llm/summarize` - 일반 텍스트 요약
- `POST /llm/summarize-live-streams` - 라이브 스트림 데이터 요약
- `GET /llm/health` - LM Studio 연결 상태

## 사용 방법

1. **기본 기능**: YouTube 채널 정보와 Naver 카페 게시글을 실시간으로 확인
2. **AI 요약**: 연도를 선택하고 "요약 생성" 버튼을 클릭하여 해당 연도의 라이브 스트림 활동 패턴을 AI로 분석
3. **데이터 탐색**: uzuhama-live-link 서브모듈의 연도별 데이터를 통해 과거 활동 기록 조회

## 기술 스택

### 백엔드
- FastAPI
- Pydantic
- httpx
- BeautifulSoup4
- LM Studio API 연동

### 프론트엔드  
- React Native
- Expo
- TypeScript
- Tailwind CSS

### AI/ML
- LM Studio
- Qwen3 모델
- 로컬 LLM 추론

## 개발 환경

- Python 3.12+
- Node.js 18+
- LM Studio (로컬 AI 모델 서버)

## 라이선스

MIT License

---

## 마이그레이션 노트

기존 `uha-main` 디렉토리의 Django 기반 코드를 FastAPI로 리팩토링하고, AI 요약 기능을 추가했습니다:

- Django → FastAPI 마이그레이션
- 모놀리식 → 마이크로서비스 아키텍처
- AI 요약 기능 추가 (LM Studio 연동)
- 서브모듈을 통한 외부 데이터 통합
