# 콘텐츠 자동화 첫 실습

채널을 만들기 전, 콘텐츠 아이디어와 제작 상태를 기록하고 매일 현황을 저장하는 작은 자동화입니다.
조회수, 매출, 실제 채널 데이터는 포함하지 않습니다.

## 도구별 역할

| 도구 | 역할 |
| --- | --- |
| GitHub | 이 코드를 보관하고 변경 이력 기록 |
| Supabase | 아이디어와 제작 상태, 날짜별 현황 저장 |
| Render | 매일 Python 프로그램 실행 |
| vidIQ | 채널 준비 후 소재·키워드 분석에 활용 예정 |
| Windsor.ai | 채널 준비 후 실제 성과 수집에 연결 예정 |

## 지금 실행할 수 있는 연습

Python 3.11 이상을 사용합니다. 추가 라이브러리 설치는 필요 없습니다.

```sh
python3 daily_review.py --demo
python3 -m unittest -v
```

연습 데이터 3개로 계산해 로컬 `demo.sqlite3` 파일에 저장합니다.
같은 날 다시 실행하면 같은 날짜의 기록을 갱신하며, 다음 날에는 새 기록을 만듭니다.
데모 데이터는 실제 성과가 아니고 Supabase에 올라가지 않습니다.

## Supabase 연결 후

1. 연습 전용 프로젝트의 기존 테이블을 확인한 뒤 `schema.sql`을 한 번 적용합니다.
2. Table Editor의 `content_items`에 직접 정한 아이디어를 추가합니다.
3. `status`는 idea(아이디어), draft(대본), production(제작 중), ready(게시 준비), published(게시 완료), archived(보관) 중 하나입니다.
4. 마감일 `due_date`는 한국 날짜 기준입니다. 제목 외 항목은 비워도 됩니다.
5. Render 환경 설정에 프로젝트 URL과 서버 전용 Secret API key를 입력합니다.

테이블은 RLS를 켜고 일반 사용자·공개 키 접근을 차단했습니다.
이 버전은 Supabase 관리 화면과 서버 전용 작업에서만 사용하는 개인용 연습입니다.
공유용 앱으로 발전시키려면 사용자별 접근 정책을 별도로 설계해야 합니다.

## Render 연결 후

비공개 GitHub 저장소를 연결하고 Cron Job을 구성합니다.

- Runtime: Python 3.11 이상
- Build Command: `python -m py_compile daily_review.py`
- Command: `python daily_review.py`
- 환경 변수: `SUPABASE_URL`, `SUPABASE_SECRET_KEY`
- 일정 후보: 한국 시간 매일 오전 9시. Render의 UTC 표현은 `0 0 * * *`입니다.

일정은 아직 활성화되지 않았습니다. 생성 전 비용과 실행 시간을 확인합니다.
먼저 수동 실행을 한 번 하고 Supabase의 `daily_reviews`에 기록되는지 확인합니다.
기록은 총 콘텐츠 수, 상태별 개수, 오늘까지 마감인 미완료 개수입니다.
실패 시 성공 기록으로 처리하지 않고 종료 코드 1을 반환합니다.

## 검증 범위와 다음 단계

로컬 데모와 단위 테스트를 제공하며, 실제 클라우드 연결은 계정·프로젝트 준비 후 검증합니다.
자동 게시, 영상 생성, 외부 메시지 발송 기능은 이 첫 실습의 범위에 포함되지 않습니다.
콘텐츠가 대량으로 변경되는 동안 실행하면 페이지 간 현황이 달라질 수 있으므로, 이 구현은 작은 개인 작업용입니다.

채널 생성 후 Windsor.ai의 연결된 계정과 실제 필드 목록을 확인하고 성과 수집 모듈을 추가합니다.
vidIQ의 기획 결과도 콘텐츠 기록에 연결합니다. 플러그인 인증과 서버 API 인증은 별도입니다.

참고: [Supabase API 키](https://supabase.com/docs/guides/getting-started/api-keys),
[Render 정기 실행](https://render.com/docs/cronjobs),
[Windsor.ai API](https://windsor.ai/api-documentation/).
