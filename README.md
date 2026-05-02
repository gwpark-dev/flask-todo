# Flask TODO

> Flask + SQLAlchemy 로 만든 가장 단순한 할 일 관리 웹앱 — **학습용** 프로젝트입니다.

`Python` · `Flask` · `Flask-SQLAlchemy` · `SQLite` · `Jinja2`

---

## 이 저장소는 어떤 프로젝트인가요

> 이 저장소는 Flask 의 라우팅 / 템플릿 / ORM 흐름을 직접 손으로 따라가며 익히기 위한 **학습용** 프로젝트입니다.
> 실서비스용이 아니라, "왜 이렇게 쓰는지" 를 한국어 주석으로 길게 풀어 두는 데 목적이 있습니다.
> 코드와 주석은 AI(Anthropic Claude) 와 함께 페어로 작성했습니다.

---

## 주요 기능

- [x] 할 일 추가
- [x] 완료 / 미완료 토글
- [x] 할 일 삭제
- [x] 완료 개수 / 전체 개수 표시
- [x] SQLite 파일에 영구 저장 (서버를 껐다 켜도 유지)
- [x] 🔗 공유 페이지 (개별 할 일을 읽기 전용으로 보여주는 페이지)

---

## 사용 기술

| 기술 | 역할 |
| --- | --- |
| Python | 프로그래밍 언어 |
| Flask | 웹 프레임워크 (라우팅, 요청/응답 처리) |
| Flask-SQLAlchemy | Flask 와 SQLAlchemy 를 매끄럽게 이어 주는 확장 |
| SQLAlchemy ORM | 파이썬 객체와 데이터베이스 테이블을 1:1 로 매핑 |
| SQLite | 파일 한 개로 동작하는 가벼운 데이터베이스 (`instance/todo.db`) |
| Jinja2 | 서버 사이드 HTML 템플릿 엔진 |

---

## 프로젝트 구조

```text
flask-todo/
├─ app.py              # Flask 앱 본체 (라우트 5개 + Todo 모델)
├─ requirements.txt    # 의존성 목록
├─ templates/
│  ├─ index.html       # Jinja2 템플릿 (목록 + 추가 폼)
│  └─ share.html       # 개별 할 일 공유(읽기 전용) 페이지
└─ instance/           # 런타임에 자동 생성, .gitignore 됨
   └─ todo.db          # SQLite 데이터베이스 파일
```

---

## 설치 방법

### Windows (PowerShell)

```powershell
git clone <이 저장소 URL>
cd flask-todo

python -m venv venv
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### macOS / Linux (bash)

```bash
git clone <이 저장소 URL>
cd flask-todo

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
```

---

## 실행 방법

```bash
python app.py
```

서버가 뜨면 브라우저에서 다음 주소로 접속합니다.

```
http://127.0.0.1:5000
```

처음 실행하면 `instance/todo.db` 가 자동으로 만들어지고, DB 가 비어 있을 때 한해 시드 데이터 5건이 들어갑니다. 두 번째 실행부터는 직전 상태가 그대로 보입니다.

---

## 학습 포인트

이 프로젝트를 만들면서 익힌 핵심 개념입니다. 자세한 설명은 각 파일의 한국어 주석을 함께 보세요.

### 1. Jinja2 템플릿

`{{ 변수 }}` 출력, `{% for %}` / `{% if %}` 흐름 제어, `{% else %}` 로 빈 리스트 처리, `url_for()` 로 URL 하드코딩 피하기.

- 코드: `templates/index.html`

### 2. PRG (Post → Redirect → Get) 패턴

폼 제출(POST) 을 처리한 뒤 곧바로 `redirect(url_for("index"))` 로 GET 페이지로 보냅니다. 새로고침을 눌러도 같은 요청이 다시 제출되지 않게 막는 흔한 패턴입니다.

- 코드: `app.py` 의 `add` / `toggle` / `delete` 함수

### 3. 동적 URL 파라미터

`/<int:todo_id>` 처럼 경로 변수에 `int:` 컨버터를 붙이면, Flask 가 문자열을 자동으로 정수로 변환해서 함수 인자로 넘겨 줍니다. `<todo_id>` 만 쓰면 문자열이 들어와 비교가 어긋나는 함정이 있습니다.

- 코드: `app.py` 의 `toggle(todo_id)`, `delete(todo_id)`

### 4. SQLAlchemy ORM 기초

- `db.Model` 을 상속한 `Todo` 클래스로 테이블을 선언합니다.
- 자주 쓰는 조회 메서드 세 가지의 차이:
  - `Todo.query.all()` — 모든 행을 리스트로
  - `Todo.query.get(id)` — 기본키로 단건 (없으면 `None`)
  - `Todo.query.filter_by(...)` — 조건 쿼리, 뒤에 `.all()` / `.count()` 등을 붙여 마무리
- `db.session.add(obj)` 는 "장바구니에 담기", `db.session.commit()` 이 호출돼야 비로소 실제 SQL 이 DB 에 기록됩니다.

코드 안에 `[학습 포인트 A]` / `[B]` / `[C]` 라벨로 해당 위치를 표시해 두었습니다.

- 코드: `app.py` 상단 `Todo` 클래스 + `add` / `toggle` / `delete` 함수

### 5. `with app.app_context():`

`db.create_all()` 처럼 요청 처리 밖에서 DB 를 만지려면, "지금부터 이 앱의 컨텍스트야" 를 직접 알려 줘야 합니다. 그래서 첫 실행 시 테이블 생성과 시드 삽입을 `app.app_context()` 블록 안에서 처리합니다.

- 코드: `app.py` 하단의 `with app.app_context():` 블록

### 6. GET 라우트의 모양 (POST/PRG 와의 대비)

`/share/<int:todo_id>` 는 DB 를 건드리지 않고 "보여주기만" 하는 라우트입니다. 그래서 `methods=["POST"]` 도, 마지막의 `redirect(...)` 도 필요 없고 `render_template` 한 줄로 끝납니다. 트리거도 `<form>` 이 아니라 `<a href="...">` 링크입니다 — 부수효과가 없으니 주소창에 노출돼도 안전하기 때문이죠.

한 줄 요약: **변경 라우트 = POST + PRG + form / 조회 라우트 = GET + render + 링크.** 코드에는 `[학습 포인트 D]` 라벨로 위치를 표시해 두었습니다.

- 코드: `app.py` 의 `share(todo_id)` 함수, `templates/share.html`

---

## 함께 만든 사람

코드와 한국어 주석은 **Anthropic Claude** 와 페어로 작성했습니다. 학습용이라는 성격에 맞게, 주석이 의도적으로 길고 자세합니다. 익숙해지면 주석을 줄여 가며 본인 스타일로 다시 써 보는 것을 권합니다.
