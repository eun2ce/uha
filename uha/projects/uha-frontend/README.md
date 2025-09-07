# UHA Frontend

YouTube Data API와 Naver 카페 크롤링을 기반으로 한 웹앱의 React Native 프론트엔드입니다.

## 주요 기능

- YouTube 채널 정보 및 최근 영상 표시
- Naver 카페 프로필 및 게시글 표시
- 라이브 스트림 데이터 요약 기능 (LM Studio 연동)
- 연도별 라이브 스트림 데이터 조회
- uzuhama-live-link 데이터 시각화

## 새로 추가된 기능

### 라이브 스트림 요약
- 연도별 라이브 스트림 데이터 분석
- LM Studio Qwen3 모델을 통한 AI 요약
- 스트림 패턴 및 활동 특징 분석
- 총 스트림 횟수 및 통계 표시

## 설정

1. 의존성 설치:
   ```bash
   npm install
   ```

2. 백엔드 서버가 실행 중인지 확인 (http://127.0.0.1:8000)

3. LM Studio가 실행 중인지 확인 (http://localhost:1234)

## 실행

```bash
# 웹에서 실행
npm run web

# 전체 개발 서버 시작
npm start
```

## 컴포넌트 구조

```
screens/
├── youtube/
│   ├── YouTubeScreen.tsx           # 메인 YouTube 화면
│   └── components/
│       ├── Content.tsx             # 기존 콘텐츠 표시
│       └── SummarySection.tsx      # 새로 추가된 요약 기능
├── cafe/
│   ├── CafeScreen.tsx              # Naver 카페 화면
│   └── components/
│       └── Content.tsx             # 카페 콘텐츠 표시
└── common/
    └── Header.tsx                  # 공통 헤더
```

## 요약 기능 사용법

1. YouTube 화면에서 "라이브 스트림 요약" 섹션 확인
2. 원하는 연도 선택 (2020-2025)
3. "YYYY년 요약 생성" 버튼 클릭
4. AI가 생성한 요약 내용 확인

## 기술 스택

- React Native
- Expo
- TypeScript
- React Navigation
- Tailwind CSS (React Native)

## 백엔드 연동

프론트엔드는 다음 백엔드 API와 연동됩니다:

- `GET /youtube/channel-info` - YouTube 채널 정보
- `GET /naver-cafe/profile` - 카페 프로필
- `GET /naver-cafe/articles/{menu_id}/{page_id}` - 카페 게시글
- `POST /llm/summarize-live-streams` - 라이브 스트림 요약 (신규)
- `GET /llm/health` - LM Studio 상태 확인 (신규)

## 외부 데이터 소스

- GitHub 저장소: [uzuhama-live-link](https://github.com/eun2ce/uzuhama-live-link)
- 연도별 라이브 스트림 데이터 (readme-YYYY.md 파일)
