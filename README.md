# BtheB — Beyond the Book

**읽는 것을 넘어, 스스로 생각하는 힘으로.**

책을 읽은 사람과 철학자 페르소나(첫 대상: **맹자**)가 **정답 대신 질문**으로 책 너머를 생각하는 대화 서비스입니다.
AI가 대신 이해해 주는 것이 아니라, 사용자가 스스로 읽고 추론하도록 돕는 것이 목표입니다.

> 상태: **M0(인프라) 완료.** 아직 RAG·화면은 없습니다. 아래 "현재 상태"를 확인하세요.

## 작동 방식 (목표 구조)

```
[인덱싱: 책마다 1회]
책 텍스트 → 문단 청크 → 임베딩 → 벡터 DB 저장 (메타: 출처 층, 위치)

[질문마다]
질문 → 임베딩 → 관련 문단 검색
     → 프롬프트 = 페르소나 지침 + 검색 문단 + 대화 기록 + "정답 직접 제시 금지, 질문으로 유도"
     → LLM → 답변 + 인용 위치 → 로그(평가용)
```

- **RAG**는 모델을 학습시키는 것이 아니라 답하기 직전에 책의 관련 부분을 찾아 붙여 주는 방식입니다. 책이 바뀌면 인덱스만 교체합니다.
- 자료는 층으로 나눕니다: **1층 = 사용자가 읽는 책(해설서·번역본)**, **2층 = 원문·개념·맥락**, 이후 다른 철학자·현실 사례.
- LLM 호출은 어댑터 하나로 감싸서, 개발은 `claude` headless, 이후 API, 소형 오픈모델(LoRA)로 바꿔 비교합니다.

## 폴더 구조

```
backend/app/
  core/        설정(.env 로딩)
  engines/     여러 기능이 공유하는 엔진: llm(어댑터), rag, persona
  features/    기능별 폴더: chat (이후 books, auth, progress)
  main.py      기능 라우터를 모아 앱 생성
frontend/      React (M2에서 추가)
data/ eval/ docs/
```

## 현재 상태

| 단계 | 내용 | 상태 |
|---|---|---|
| M0 | 저장소 뼈대, LLM 어댑터(headless), `/health`, `/chat` | 완료 |
| M1 | 해설서 샘플 OCR, 원문 정리, 인덱싱·검색, 인용 포함 답변 | 예정 |
| M2 | React 채팅 화면, 맹자 페르소나 (**여기까지 MVP**) | 예정 |
| M3 | 평가(답 누설률, 인용 정확도, 지연·비용), 요약 색인 실험 | 예정 |
| M4 | LoRA 페르소나 소형모델 + 서빙, API LLM과 비교 | 예정 |
| M5 | API 백엔드 전환, 요청 한도, 배포, 책 목록·로그인 | 예정 |

아직 하지 않은 것: RAG, 페르소나, 화면, 평가, 모델 비교, 배포. 설계는 [`docs/superpowers/specs/`](docs/superpowers/specs/2026-10-29-btheb-design.md)에 있습니다.

## 실행 방법

필요: Python 3.12 이상 (개발은 3.14에서 확인), `claude` CLI(로그인 상태).

```bash
cd backend
python -m venv .venv
.venv/Scripts/python -m pip install -e ".[dev]"      # macOS/Linux: .venv/bin/python
cp ../.env.example ../.env                            # 저장소 루트의 .env, 서버 시작 시 읽음(실제 환경변수가 우선)
.venv/Scripts/python -m uvicorn app.main:create_app --factory --port 8000
```

```bash
curl localhost:8000/health                            # {"status":"ok"}
```

`/chat`은 UTF-8 JSON으로 호출하세요. Windows 셸의 curl은 한글을 다른 인코딩으로 보내 오류가 날 수 있어, 한글 테스트는 Python `httpx` 등을 권장합니다.

```bash
.venv/Scripts/python -m pytest                        # 테스트
```

## 자료와 저작권

- 이 저장소에는 **책·논문 텍스트를 포함하지 않습니다.** `data/books/`와 `etc/`는 git에서 제외됩니다.
- 개발에 쓰는 자료는 개인 개발용으로 로컬에서만 사용합니다. 공개 서비스에는 권리자(출판사 등)의 허락을 받은 텍스트만 사용하는 구조입니다.

## LLM 백엔드의 한계

- 현재 `claude` headless(`claude -p`)는 도구·MCP·CLAUDE.md·훅을 모두 끄고(`--tools "" --safe-mode --strict-mcp-config`) 빈 임시 폴더에서 실행해 개발 환경의 지침이 새어 들어가지 않게 했습니다. 그래도 **개발과 본인 시연 전용**입니다. 요청마다 프로세스를 띄워 느리고 동시 요청에 약합니다.
- 다른 사용자에게 공개하는 서비스에는 쓰지 않습니다. 공개 단계(M5)에서 API 백엔드로 전환합니다.
- 비밀 값은 `.env`에 두며 커밋하지 않습니다 (`.env.example`만 커밋).
