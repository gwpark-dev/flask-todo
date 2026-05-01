# flask 패키지에서 필요한 도구들을 한꺼번에 가져옵니다.
# - Flask           : 웹 애플리케이션의 본체 역할을 하는 클래스
# - render_template : templates/ 폴더 안의 HTML 파일을 읽어
#                     파이썬에서 넘긴 데이터를 끼워 넣은 뒤 완성된 HTML 문자열로 돌려주는 함수
# - request         : 사용자가 보낸 요청(폼 입력값, URL 파라미터 등)을 읽기 위한 객체.
#                     예: request.form.get("task")  ->  <input name="task"> 의 값
# - redirect        : "이 URL 로 다시 가세요" 라고 브라우저에게 응답하는 함수.
#                     POST 처리 후에 GET / 으로 보내는 용도로 자주 씁니다 (PRG 패턴).
# - url_for         : 라우트 함수 이름을 주면 그에 해당하는 URL 문자열을 만들어 줍니다.
#                     예: url_for("index")                 ->  "/"
#                         url_for("toggle", todo_id=3)     ->  "/toggle/3"
#                     URL 경로를 하드코딩하지 않으니, 나중에 경로가 바뀌어도 한 곳만 고치면 됩니다.
from flask import Flask, render_template, request, redirect, url_for

# Flask-SQLAlchemy 는 Flask 와 SQLAlchemy(파이썬의 대표 ORM)를 매끄럽게 이어주는 확장입니다.
#  ORM(Object Relational Mapper) 한 줄 요약:
#    "테이블의 한 행 = 파이썬 객체 하나" 로 다루게 해주는 도구.
#    내가 객체의 속성을 바꾸면, 그 변경을 추적했다가 알맞은 SQL(INSERT/UPDATE/DELETE)을 자동으로 만들어 줍니다.
#
# ─────────────────────────────────────────────────────────────
# [학습 포인트 C] ORM 이 SQL 을 어떻게 "대체" 하는가 (대비표)
# ─────────────────────────────────────────────────────────────
#   직접 SQL 을 쓸 때                                | ORM 으로 쓸 때
#   --------------------------------------------------+---------------------------------------------------------------
#   SELECT * FROM todo;                               | Todo.query.all()
#   SELECT * FROM todo WHERE id = ?;                  | Todo.query.get(todo_id)
#   SELECT * FROM todo WHERE done = 1;                | Todo.query.filter_by(done=True).all()
#   SELECT COUNT(*) FROM todo WHERE done = 1;         | Todo.query.filter_by(done=True).count()
#   INSERT INTO todo (task, done) VALUES (?, ?);      | db.session.add(Todo(task=..., done=...)); db.session.commit()
#   UPDATE todo SET done = ? WHERE id = ?;            | todo.done = ...; db.session.commit()
#   DELETE FROM todo WHERE id = ?;                    | db.session.delete(todo); db.session.commit()
#
# 핵심 메시지: "파이썬 객체를 자연스럽게 다루기만 하면, SQLAlchemy 가 변경 사항을 추적해
#               필요한 SQL 을 자동으로 만들어 데이터베이스에 보낸다." 입니다.
#               우리는 더 이상 SQL 문자열을 손으로 쓰지 않아도 됩니다.
from flask_sqlalchemy import SQLAlchemy

# Flask 애플리케이션 인스턴스를 생성합니다.
# __name__ 은 파이썬이 자동으로 채워주는 "현재 모듈 이름"이며,
# Flask 가 정적 파일이나 템플릿 같은 리소스의 경로를 찾을 때 기준점으로 사용합니다.
app = Flask(__name__)

# ─────────────────────────────────────────────────────────────
# 데이터베이스 설정
# ─────────────────────────────────────────────────────────────
# SQLALCHEMY_DATABASE_URI 는 "어떤 DB 의 어디에 접속할지" 를 알려주는 주소입니다.
#   "sqlite:///todo.db" 의 의미:
#     - sqlite : SQLite (별도 서버 없이 파일 한 개로 동작하는 가벼운 DB) 사용
#     - ///todo.db : Flask 의 instance/ 폴더 안에 'todo.db' 라는 파일을 사용
#         (슬래시 3개는 "상대 경로", 4개면 "절대 경로" 라는 관례입니다.)
#   instance/ 폴더는 Flask 가 자동으로 만들어 주는 "런타임 데이터 보관 폴더" 이고,
#   .gitignore 에 이미 등록돼 있어 DB 파일이 실수로 커밋될 위험이 없습니다.
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.db"

# SQLALCHEMY_TRACK_MODIFICATIONS 는 "객체가 바뀔 때마다 신호를 쏘는" 부가 기능인데,
# 거의 안 쓰는 데다 메모리만 더 먹어서 보통은 꺼 둡니다(켜두면 시작할 때 경고도 뜸).
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db 는 앞으로 우리가 데이터베이스를 다룰 때 쓰는 "관문" 역할의 객체입니다.
#   - db.Model       : 우리가 만들 모든 테이블 클래스의 부모 클래스
#   - db.Column      : 테이블의 컬럼(열)을 정의할 때 사용
#   - db.session     : 변경 사항을 모았다가 한 번에 DB 로 보내는 "작업 묶음(트랜잭션)" 객체
db = SQLAlchemy(app)


# ─────────────────────────────────────────────────────────────
# Todo 모델 — 예전의 딕셔너리 한 칸이 "객체 하나" 로 옮겨옵니다.
#   기존: {"id": 1, "task": "...", "done": False}
#   현재: Todo(id=1, task="...", done=False)
# 클래스 이름(Todo)이 그대로 테이블 이름(todo)이 됩니다(소문자로 변환).
# ─────────────────────────────────────────────────────────────
class Todo(db.Model):
    # primary_key=True 는 "이 컬럼이 이 테이블의 식별자다" 라는 뜻이고,
    # SQLite 에서는 정수 PK 이면 자동으로 AUTO INCREMENT 처럼 번호를 매겨 줍니다.
    # 그래서 add() 라우트에서 더 이상 "max(id)+1" 같은 계산을 직접 하지 않아도 됩니다.
    id   = db.Column(db.Integer, primary_key=True)

    # nullable=False 는 NOT NULL 제약. 빈 task 가 DB 에 들어가지 못하도록 보장합니다.
    # String(200) 의 200 은 SQLite 에선 강제되지 않지만, 다른 DB 로 옮길 때를 대비한 힌트입니다.
    task = db.Column(db.String(200), nullable=False)

    # default=False 는 "INSERT 할 때 done 을 안 적어 주면 False 로 채워라" 라는 뜻입니다.
    # nullable=False 까지 같이 두면, "done 이 None 인 이상한 행" 자체가 생길 수 없어 안전합니다.
    done = db.Column(db.Boolean, nullable=False, default=False)

    # ─────────────────────────────────────────────────────────────
    # [학습 포인트 B] 자주 만나는 세 가지 조회 메서드 — 언제 무엇을 쓰나
    # ─────────────────────────────────────────────────────────────
    #
    #   Todo.query.all()
    #     → 테이블의 "모든 행" 을 파이썬 리스트로 가져옵니다.
    #       SQL 로 치면 SELECT * FROM todo. 비어 있으면 빈 리스트 [].
    #
    #   Todo.query.get(todo_id)
    #     → "기본키(PK) 로 한 건만" 가져옵니다. 없으면 None 을 돌려줍니다.
    #       SQL 로 치면 SELECT * FROM todo WHERE id = ? LIMIT 1.
    #       → "id 로 단건 조회" 라는 가장 흔한 패턴을 한 줄로 줄여주는 편의 메서드입니다.
    #
    #   Todo.query.filter_by(done=True)
    #     → "조건에 맞는 것만" 추리는 쿼리를 만듭니다. 이 자체로는 아직 결과가 아니라 '쿼리 객체'입니다.
    #       뒤에 .all()  / .first() / .count() 같은 마무리 메서드를 붙여 결과를 꺼냅니다.
    #         예) Todo.query.filter_by(done=True).count()  ->  완료 개수
    #
    #   왜 셋이 따로 있나요?
    #     "전체 / PK 한 건 / 조건" 은 정말 자주 나오는 패턴이라,
    #     매번 SQL 을 길게 쓰지 말고 짧게 표현할 수 있게끔 미리 만들어 둔 단축키들입니다.
    #
    #   참고: Flask-SQLAlchemy 3 / SQLAlchemy 2.0 부터는
    #         Todo.query.get(...)  대신  db.session.get(Todo, ...)  형태가 권장됩니다.
    #         하지만 인터넷 자료 거의 전부가 .query.get(...) 형태라 학습 단계에서는 그대로 사용합니다.
    # ─────────────────────────────────────────────────────────────


# @app.route("/") 데코레이터는 "/" 경로(루트 URL)로 들어온 요청을
# 바로 아래 함수(index)가 처리하도록 Flask 에 등록해 줍니다.
@app.route("/")
def index():
    # 모든 할 일을 가져옵니다. SQL 로 치면 SELECT * FROM todo.
    # 결과는 Todo 객체들의 리스트이며, 템플릿에서는 todo.id / todo.task / todo.done 처럼
    # "속성"으로 접근하면 됩니다. (예전 딕셔너리 t["done"] 표기는 더 이상 필요 없음)
    todos = Todo.query.all()

    # 표시용 계산은 가능하면 파이썬 쪽에서 미리 해 두고, 템플릿(HTML) 에는 "출력만" 맡기는 편이 깔끔합니다.
    # 두 값 모두 DB 에 직접 COUNT 를 시키는 게 가장 빠르고 단순합니다(파이썬에서 다시 세지 않아도 됨).
    total      = Todo.query.count()
    done_count = Todo.query.filter_by(done=True).count()

    # render_template 은 templates/index.html 파일을 찾아서 읽고,
    # 그 안에 있는 Jinja2 문법({{ }}, {% %})을 실제 값으로 채워
    # 최종 HTML 문자열을 만들어 돌려줍니다.
    return render_template(
        "index.html",
        todos=todos,
        done_count=done_count,
        total=total,
    )


# ============================================================
#  지금부터는 "사용자 입력으로 상태를 바꾸는" POST 라우트들입니다.
#
#  공통 패턴(PRG, Post-Redirect-Get):
#    1) 브라우저가 폼을 제출(POST) 하면
#    2) 서버는 데이터를 변경하고
#    3) 마지막에 redirect(url_for("index")) 로 GET / 을 다시 호출하게 합니다.
#  이렇게 하면 사용자가 페이지를 새로고침해도 같은 POST 가 또 실행되지 않습니다
#  (예: 새로고침 한 번에 같은 할 일이 두 번 추가되는 사고를 막아 줌).
# ============================================================


# ─────────────────────────────────────────────────────────────
# (1) 할 일 추가
# ─────────────────────────────────────────────────────────────
@app.route("/add", methods=["POST"])
def add():
    # request.form 은 사용자가 보낸 폼 데이터를 담은 "딕셔너리 비슷한" 객체입니다.
    #   .get("task", "") -> "task" 키가 없을 때도 KeyError 안 내고 빈 문자열을 돌려줍니다.
    #   .strip()         -> 앞뒤 공백 제거. "    " 처럼 공백만 입력한 경우도 빈 입력으로 취급.
    task = request.form.get("task", "").strip()

    # 빈 입력은 그냥 무시합니다 (저장하지 않고 페이지만 새로 그림).
    if task:
        # Todo 객체를 "그냥 만들기만" 하면 아직 DB 와는 아무 상관이 없습니다.
        # id 는 적지 않습니다 — primary_key 라서 SQLite 가 자동으로 부여해 줍니다.
        new_todo = Todo(task=task, done=False)

        # ─────────────────────────────────────────────────────────────
        # [학습 포인트 A] db.session.add() 와 db.session.commit() 의 관계
        # ─────────────────────────────────────────────────────────────
        # 1) db.session.add(obj)
        #      → "이 객체를 다음 commit 때 INSERT 해 주세요" 라고 세션(작업 묶음) 에 적어두는 단계.
        #        장바구니에 상품을 담은 것과 같은 상태로, 아직 디스크에는 아무 일도 일어나지 않습니다.
        #
        # 2) db.session.commit()
        #      → 그제야 세션에 쌓인 변경들을 한꺼번에 실제 SQL 로 바꿔 DB 파일에 기록합니다.
        #        commit 을 부르지 않으면 서버를 껐다 켰을 때 입력이 통째로 사라집니다.
        #        (예전 인메모리 리스트일 때는 자동으로 사라지지 않다가, DB 로 옮긴 뒤로
        #         "왜 새로고침하면 그대로인데 재시작하면 사라지지?" 같은 함정이 commit 누락에서 옵니다.)
        #
        # 3) "원자성(atomicity)" 보너스
        #      → add 를 여러 번 한 다음 commit 한 번만 부르면, 그 묶음이 한 단위로 성공/실패합니다.
        #        중간에 에러가 나면 db.session.rollback() 으로 묶음 전체를 없던 일로 되돌릴 수 있습니다.
        #        (오늘 코드에서는 한 건씩 commit 하지만, 개념은 알고 있는 것이 좋습니다.)
        # ─────────────────────────────────────────────────────────────
        db.session.add(new_todo)
        db.session.commit()

    # 처리 끝났으니 메인 페이지로 보냅니다 (PRG 패턴).
    return redirect(url_for("index"))


# ─────────────────────────────────────────────────────────────
# (2) 완료 토글
#     - URL 의 <int:todo_id> 부분이 함수 인자 todo_id 로 들어옵니다.
#     - 'int:' 컨버터를 쓰면 문자열이 자동으로 int 로 변환됩니다.
# ─────────────────────────────────────────────────────────────
@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    # 기본키로 한 건만 가져옵니다. 없으면 None.
    # 예전 코드처럼 리스트를 직접 for 로 돌며 id 를 비교할 필요가 없어졌습니다 — 한 줄이면 끝.
    todo = Todo.query.get(todo_id)

    # 존재하는 경우에만 done 을 뒤집습니다.
    # 'not todo.done' 으로 True <-> False 를 반전.
    # 주의: 객체의 속성을 바꿨다고 해서 자동으로 DB 가 업데이트되지는 않습니다.
    #       세션에는 "이 객체가 바뀌었구나" 라는 흔적만 남고, commit() 호출 시점에야 UPDATE 문이 날아갑니다.
    if todo is not None:
        todo.done = not todo.done
        db.session.commit()

    return redirect(url_for("index"))


# ─────────────────────────────────────────────────────────────
# (3) 삭제
# ─────────────────────────────────────────────────────────────
@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    # 인메모리 리스트일 때는 "리스트 컴프리헨션으로 새 리스트를 만들어 다시 대입" 했지만,
    # ORM 에서는 "지울 객체를 찾아서 → session.delete → commit" 의 3단계가 표준 흐름입니다.
    # (덕분에 예전 함수 머리에 있던 'global todos' 선언도 더 이상 필요하지 않습니다.)
    todo = Todo.query.get(todo_id)
    if todo is not None:
        db.session.delete(todo)
        db.session.commit()

    return redirect(url_for("index"))


# ─────────────────────────────────────────────────────────────
# [학습 포인트 D] GET 라우트의 모양 — POST/PRG 와의 대비
# ─────────────────────────────────────────────────────────────
# 지금까지 만든 라우트 4개 중 "변경" 을 일으키는 셋(add/toggle/delete)은
# 모두 method="post" 였고, 마지막에 redirect(url_for("index")) 로 끝났습니다.
# 이른바 PRG (Post-Redirect-Get) 패턴이죠. 새로고침을 눌렀을 때 같은 POST 가
# 한 번 더 날아가서 같은 일이 두 번 일어나는 사고를 막기 위함이었습니다.
#
# 반면 아래 share 라우트는 "보여주기만" 합니다. DB 를 건드리지 않으므로,
#   - 새로고침해도 다시 일어날 일 자체가 없습니다 → redirect 가 필요 없습니다.
#   - methods=["POST"] 도 필요 없습니다 → 기본값인 GET 만 받으면 됩니다.
#     (@app.route 에 methods 를 안 적으면 GET 만 허용하는 게 기본입니다.)
#   - 응답은 render_template 한 줄로 끝납니다. 새로고침 = 같은 페이지를 다시 그릴 뿐.
#
# 트리거 형태의 차이도 함께 익혀 두면 좋습니다.
#   - GET  → <a href="..."> 링크. 주소창에 노출돼도 안전(부수효과 없음).
#   - POST → <form method="post"> 폼. 부수효과를 일으키므로, 링크처럼 함부로
#            클릭/크롤링되지 않게 일부러 폼 제출이라는 명시적 동작을 요구합니다.
# 그래서 templates/index.html 에서도 토글/삭제는 <form>, 공유는 <a> 로 트리거합니다.
#
# 한 줄 요약: "변경 라우트 = POST + PRG + form / 조회 라우트 = GET + render + 링크"
# ─────────────────────────────────────────────────────────────
@app.route("/share/<int:todo_id>")
def share(todo_id):
    # 토글/삭제와 똑같이 PK 단건 조회. 없으면 None.
    # (→ [학습 포인트 B] 참고: query.get(PK) 는 못 찾으면 None 을 돌려준다.)
    todo = Todo.query.get(todo_id)

    # 존재 여부를 그대로 템플릿에 넘깁니다.
    # share.html 안에서 {% if todo %} ... {% else %} 없는 항목입니다 ... {% endif %} 로
    # 두 경우를 한 화면에서 갈라 보여 줍니다.
    # POST 라우트들과 달리 redirect 가 보이지 않는 점에 주목하세요 — DB 변경이 없으니
    # 새로고침 사고를 걱정할 일도 없고, render_template 으로 곧장 응답을 만들면 됩니다.
    return render_template("share.html", todo=todo)


# ─────────────────────────────────────────────────────────────
# 첫 실행 시 자동 처리: 테이블 생성 + 시드 데이터 삽입
# ─────────────────────────────────────────────────────────────
# Flask 의 많은 기능(특히 db.session)은 "지금 어떤 앱에서 동작 중인가" 라는 정보를 필요로 하는데,
# 이 정보는 보통 요청을 처리하는 동안 자동으로 켜져 있습니다.
# 하지만 지금처럼 요청과 무관한 "스크립트 시작 시점" 에서 DB 를 건드리려면,
# 우리가 직접 "지금부터 이 앱의 컨텍스트야" 라고 알려 줘야 합니다 → with app.app_context():
with app.app_context():
    # create_all() 은 db.Model 을 상속한 모든 클래스를 보고,
    # 아직 없는 테이블만 새로 만들어 줍니다. 이미 있으면 그냥 둡니다.
    # (주의: 컬럼 정의를 바꿔도 이 함수는 기존 테이블을 자동으로 변경해 주지는 않습니다.
    #        나중에 학습이 진전되면 'Flask-Migrate' 같은 도구로 스키마 변경을 다루게 됩니다.)
    db.create_all()

    # DB 가 비어 있을 때만 초기 5개를 넣습니다.
    # 이 검사가 없으면 서버를 껐다 켤 때마다 같은 5개가 매번 추가되어 목록이 점점 길어지는 문제가 생깁니다.
    if Todo.query.count() == 0:
        # add_all() 은 add() 의 "여러 개 버전". 한 번에 여러 객체를 세션에 넣을 때 편합니다.
        db.session.add_all([
            Todo(task="파이썬 기초 복습하기",     done=True),
            Todo(task="Flask 라우팅 익히기",      done=True),
            Todo(task="Jinja2 템플릿 사용해보기", done=False),
            Todo(task="할 일 추가 기능 만들기",   done=False),
            Todo(task="DB 연결하기",              done=False),
        ])
        db.session.commit()


# 이 파일을 `python app.py` 명령으로 직접 실행했을 때만 아래 블록이 동작합니다.
# (다른 파일에서 import 해서 사용할 때는 서버가 자동으로 뜨지 않게 하기 위함입니다.)
if __name__ == "__main__":
    # 개발용 서버를 실행합니다.
    # debug=True 로 두면 코드를 수정했을 때 서버가 자동으로 다시 시작되고,
    # 에러가 났을 때 브라우저에 자세한 디버그 화면이 보여서 학습에 편리합니다.
    # (실제 서비스 배포 시에는 반드시 debug=False 로 바꿔야 합니다.)
    app.run(debug=True)
