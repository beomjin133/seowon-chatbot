# Frontend — 챗봇 웹 클라이언트

React 19 + Redux Toolkit 기반 채팅 UI입니다. `backend`(Spring Boot)의 `/api`를 호출하며,
비회원도 바로 질문할 수 있고 로그인하면 세션별로 대화 기록이 남습니다.

## 실행

```bash
npm install
npm start        # http://localhost:3000
```

API 주소는 기본값이 `http://localhost:8080/api`입니다. 다른 곳을 보게 하려면
`frontend/.env`에 아래를 넣으세요 (CRA 규칙상 `REACT_APP_` 접두사 필수).

```
REACT_APP_API_BASE_URL=http://your-backend:8080/api
```

## 스크립트

| 명령 | 설명 |
|---|---|
| `npm start` | 개발 서버 (craco) |
| `npm run build` | `build/`에 프로덕션 번들 생성 |
| `npm test` | 테스트 실행 |

## 구조

```
src/
├── pages/            # ChatPage · LoginPage · RegisterPage
├── routes/           # AppRouter — /, /auth/login, /auth/register
├── components/
│   ├── chat/         # 채팅 레이아웃(사이드바·헤더·입력창)과 UI(말풍선·모달 등)
│   ├── login/
│   └── register/     # 약관 → 이메일 인증 → 정보입력 → 완료 4단계
├── modules/
│   ├── auth/         # 로그인·회원가입 API·훅·slice
│   ├── chat/         # 채팅 API·훅·slice
│   └── shared/       # axiosInstance(JWT 인터셉터), store, 공용 유틸
├── hooks/            # useDarkMode
└── assets/           # 아이콘·로고
```

빌드는 [CRA](https://github.com/facebook/create-react-app)를 [craco](https://craco.js.org/)로
감싸 쓰며, craco에서 `@` → `src` 별칭을 걸어 두었습니다 (`import ChatPage from '@/pages/ChatPage'`).

JWT는 로그인 시 `localStorage`에 저장되고, `axiosInstance` 요청 인터셉터가 매 요청의
`Authorization: Bearer ...` 헤더에 자동으로 실어 보냅니다.
