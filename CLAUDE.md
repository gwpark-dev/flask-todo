# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 프로젝트 성격

학습용 Flask 프로젝트입니다. 실서비스 코드가 아니라 **튜토리얼 자료**에 가깝습니다.
- 모든 코드 주석은 **한국어**로, "왜 이렇게 쓰는지" 를 길게 풀어 쓰는 스타일을 유지합니다 (단순 설명/한 줄 주석 X).
- 의도적으로 단순하게 둡니다: 단일 파일(`app.py`), `<style>` 인라인, `static/` 분리 없음, blueprint 없음.
- **YAGNI 엄수**: 아직 안 쓰는 CSS 클래스/유틸 함수/플레이스홀더 라우트를 미리 만들지 않습니다.
- 비자명한 변경은 **계획 먼저** 보여 주고 사용자 동의를 받은 뒤 구현합니다.

## 자주 쓰는 명령

```powershell
# 가상환경 활성화 (Windows / PowerShell)
.\venv\Scripts\Activate.ps1

# 의존성 설치
pip install -r requirements.txt

# 개발 서버 실행 (debug=True 라 코드 저장 시 자동 재시작)
python app.py
# → http://127.0.0.1:5000
```

테스트/린트는 아직 도입하지 않았습니다 (학습 단계). 프레임워크를 추가하기 전에 사용자에게 먼저 확인하세요.

## 아키텍처 한눈에

`app.py` 한 파일이 앱 전부입니다. 위에서 아래로 읽으면 흐름이 그대로 보이도록 의도된 구조입니다.

1. **App + DB 설정** (`SQLALCHEMY_DATABASE_URI = "sqlite:///todo.db"` → 실제 파일은 `instance/todo.db`)
2. **`Todo` 모델** — `id` / `task` / `done` 3개 컬럼만. 주석에 학습 포인트 A/B/C 라벨이 박혀 있음.
3. **라우트 4개** — `index` (GET /), `add` (POST), `toggle` (POST), `delete` (POST). 모든 변경 라우트는 **PRG 패턴**으로 `redirect(url_for("index"))` 종료.
4. **모듈 임포트 시점에 실행되는 부트스트랩 블록**:
   ```python
   with app.app_context():
       db.create_all()
       if Todo.query.count() == 0:
           db.session.add_all([...])  # 시드 5건
           db.session.commit()
   ```
   요청 컨텍스트 밖에서 DB 를 만지므로 `app.app_context()` 가 반드시 필요합니다.

`templates/index.html` 는 Jinja2 단일 템플릿. 진행률 표시 + 추가 폼 + 항목 리스트(각 항목당 토글 폼/삭제 폼 2개)로 구성. JS 없이 순수 HTML 폼 왕복으로 동작합니다.

## 작업 시 주의할 함정

- **스키마 변경 시 `db.create_all()` 은 기존 테이블을 변경하지 않습니다.** `Todo` 컬럼을 추가/변경하면 `instance/todo.db` 파일을 삭제해서 다시 만들거나, Flask-Migrate 도입을 사용자와 합의해야 합니다.
- **`Todo.query.get(...)` 사용 유지**. SQLAlchemy 2.0 에서 `db.session.get(Todo, ...)` 가 권장이지만, 학습 자료/튜토리얼이 거의 다 `.query.get` 형태라 일부러 그대로 둡니다 (주석에도 명시되어 있음). 사용자가 "이제 마이그레이션 해 보자" 라고 명시하기 전에는 바꾸지 마세요.
- **`if __name__ == "__main__":` 안의 `app.run(debug=True)` 와, 모듈 최상단의 `with app.app_context():` 부트스트랩은 분리 상태를 유지합니다.** import 만 해도 테이블/시드가 준비되어야 하므로 부트스트랩을 `__main__` 블록으로 옮기지 마세요.
- **`url_for()` 우선**. 템플릿/리다이렉트 어디에서도 `/toggle/3` 같은 하드코딩 금지. 학습 포인트 중 하나입니다.
- **`instance/`, `*.db`, `venv/` 는 `.gitignore` 에 등록되어 있습니다.** DB 파일이나 가상환경을 커밋하지 마세요.

## 수정 작업 톤

- 새 기능을 추가할 때도 기존 라우트들과 같은 **튜토리얼 주석 밀도**를 맞춥니다 (컬럼/메서드/Jinja 문법의 의미와 이유 설명).
- 추상화 욕구가 들어도 참습니다. 한 파일/한 함수에서 비슷한 코드 3줄이 반복돼도 헬퍼로 빼지 않는 편이 학습에 더 도움이 됩니다.
- 사용자는 한국어로 소통합니다. 응답/계획/주석 모두 한국어로.
