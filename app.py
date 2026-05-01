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

# Flask 애플리케이션 인스턴스를 생성합니다.
# __name__ 은 파이썬이 자동으로 채워주는 "현재 모듈 이름"이며,
# Flask 가 정적 파일이나 템플릿 같은 리소스의 경로를 찾을 때 기준점으로 사용합니다.
app = Flask(__name__)


# 화면에 보여줄 임시 할 일 데이터입니다.
# 지금 단계에서는 데이터베이스 없이 그냥 파이썬 리스트(메모리 변수)에 담아 둡니다.
# - 리스트 안에는 딕셔너리가 5개 들어 있고,
# - 각 딕셔너리는 세 개의 키를 가집니다:
#     "id"   -> 항목을 구분하는 고유 번호 (정수)
#     "task" -> 할 일 내용 (문자열)
#     "done" -> 완료 여부 (True / False)
#
# id 가 왜 필요할까요?
#   "토글" 이나 "삭제" 를 처리하려면 서버가 "어느 항목인지" 정확히 알아야 합니다.
#   리스트 인덱스(예: todos[2]) 를 식별자로 쓰면, 한 항목이 지워질 때마다 그 뒤 항목들의
#   인덱스가 전부 1씩 밀려서 다음 요청에서 엉뚱한 항목을 건드리는 사고가 납니다.
#   그래서 한 번 부여하면 변하지 않는 고유 번호(id) 를 따로 갖는 것이 안전합니다.
#
# 나중에 DB 를 붙이면, 이 id 는 자연스럽게 테이블의 PRIMARY KEY 로 옮겨갑니다.
todos = [
    {"id": 1, "task": "파이썬 기초 복습하기",   "done": True},
    {"id": 2, "task": "Flask 라우팅 익히기",     "done": True},
    {"id": 3, "task": "Jinja2 템플릿 사용해보기", "done": False},
    {"id": 4, "task": "할 일 추가 기능 만들기",   "done": False},
    {"id": 5, "task": "DB 연결하기",             "done": False},
]


# @app.route("/") 데코레이터는 "/" 경로(루트 URL)로 들어온 요청을
# 바로 아래 함수(index)가 처리하도록 Flask 에 등록해 줍니다.
@app.route("/")
def index():
    # 진행 상황(완료된 개수)을 미리 계산해 둡니다.
    # 'sum(1 for t in todos if t["done"])' 는 파이썬의 "제너레이터 표현식"으로,
    #   - todos 안의 각 항목 t 를 하나씩 보면서
    #   - t["done"] 이 True 인 것만 1을 만들어 모두 더한다
    # 는 뜻입니다. 결과적으로 "완료된 항목의 개수" 가 나옵니다.
    #
    # 표시용 계산은 가능하면 파이썬 쪽(여기) 에서 미리 해 두고,
    # 템플릿(HTML) 에는 "출력만" 맡기는 것이 깔끔합니다.
    done_count = sum(1 for t in todos if t["done"])

    # render_template 은 templates/index.html 파일을 찾아서 읽고,
    # 그 안에 있는 Jinja2 문법({{ }}, {% %})을 실제 값으로 채워
    # 최종 HTML 문자열을 만들어 돌려줍니다.
    #
    # 키워드 인자 형태(이름=값)로 넘긴 값들은 템플릿 안에서 그 '이름' 으로 사용됩니다.
    #   todos=todos          -> 템플릿에서 'todos' 라는 변수로 접근
    #   done_count=done_count -> 템플릿에서 'done_count' 변수로 접근
    #   total=len(todos)     -> 템플릿에서 'total' 변수로 접근 (전체 개수)
    return render_template(
        "index.html",
        todos=todos,
        done_count=done_count,
        total=len(todos),
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
#     - 메인 페이지 위쪽 폼이 <form action="/add" method="post"> 로 보내옵니다.
#     - methods=["POST"] 를 지정하지 않으면 기본은 GET 만 허용해서 405 에러가 납니다.
# ─────────────────────────────────────────────────────────────
@app.route("/add", methods=["POST"])
def add():
    # request.form 은 사용자가 보낸 폼 데이터를 담은 "딕셔너리 비슷한" 객체입니다.
    # 키는 HTML 의 <input name="..."> 의 name 값과 똑같아야 합니다.
    #   .get("task", "") -> "task" 키가 없을 때도 KeyError 안 내고 빈 문자열을 돌려줍니다.
    #   .strip()         -> 앞뒤 공백 제거. "    " 처럼 공백만 입력한 경우도 빈 입력으로 취급.
    task = request.form.get("task", "").strip()

    # 빈 입력은 그냥 무시합니다 (저장하지 않고 페이지만 새로 그림).
    if task:
        # 새 id = (지금 todos 안 id 들 중 최댓값) + 1
        #   max() 의 default=0 인자는 "리스트가 비어 있을 때는 0 을 반환" 하라는 뜻입니다.
        #   default 가 없으면 빈 시퀀스에 max() 를 호출했을 때 ValueError 가 납니다.
        new_id = max((t["id"] for t in todos), default=0) + 1

        # 새로 만든 할 일은 기본적으로 미완료(done=False) 상태입니다.
        # .append() 는 리스트의 "내용" 을 바꾸는 메서드라 'global todos' 선언이 필요 없습니다.
        todos.append({"id": new_id, "task": task, "done": False})

    # 처리 끝났으니 메인 페이지로 보냅니다 (PRG 패턴).
    return redirect(url_for("index"))


# ─────────────────────────────────────────────────────────────
# (2) 완료 토글
#     - URL 의 <int:todo_id> 부분이 함수 인자 todo_id 로 들어옵니다.
#     - 'int:' 컨버터를 쓰면 문자열이 자동으로 int 로 변환됩니다.
#       만약 그냥 <todo_id> 라고만 쓰면 todo_id 가 문자열로 들어오기 때문에,
#       'todos' 안의 정수 id 와 비교가 항상 False 가 되는 흔한 함정이 있습니다.
# ─────────────────────────────────────────────────────────────
@app.route("/toggle/<int:todo_id>", methods=["POST"])
def toggle(todo_id):
    # 리스트를 순회하면서 id 가 일치하는 항목을 찾고, 그 항목의 done 을 뒤집습니다.
    # 'not t["done"]' 은 True <-> False 를 반전시키는 가장 단순한 방법입니다.
    for t in todos:
        if t["id"] == todo_id:
            t["done"] = not t["done"]
            break  # 일치하는 항목은 단 하나뿐이니, 찾으면 더 볼 필요 없음
    return redirect(url_for("index"))


# ─────────────────────────────────────────────────────────────
# (3) 삭제
#     - 해당 id 를 가진 항목을 todos 에서 제거합니다.
# ─────────────────────────────────────────────────────────────
@app.route("/delete/<int:todo_id>", methods=["POST"])
def delete(todo_id):
    # 'global todos' 가 왜 여기서만 필요할까요?
    #   파이썬은 함수 안에서 어떤 이름에 '대입(=)' 이 일어나면 기본적으로 그 이름을 지역 변수로 봅니다.
    #   아래 'todos = [...]' 는 변수 자체를 새 리스트로 '재대입' 하는 코드라서,
    #   global 선언이 없으면 바깥의 todos 를 못 건드리고 함수 안에서만 새 변수를 만들고 끝납니다.
    #   반면 add() 의 todos.append(...) 와 toggle() 의 t["done"] = ... 는
    #   '리스트/딕셔너리의 내용을 바꾸는' 동작이라 global 이 필요 없습니다.
    global todos

    # 리스트 컴프리헨션: "id 가 todo_id 와 다른 것만" 골라서 새 리스트를 만듭니다.
    # 결과적으로 해당 id 항목 하나가 빠진 새 리스트가 만들어지고, todos 가 그것을 가리키게 됩니다.
    todos = [t for t in todos if t["id"] != todo_id]

    return redirect(url_for("index"))


# 이 파일을 `python app.py` 명령으로 직접 실행했을 때만 아래 블록이 동작합니다.
# (다른 파일에서 import 해서 사용할 때는 서버가 자동으로 뜨지 않게 하기 위함입니다.)
if __name__ == "__main__":
    # 개발용 서버를 실행합니다.
    # debug=True 로 두면 코드를 수정했을 때 서버가 자동으로 다시 시작되고,
    # 에러가 났을 때 브라우저에 자세한 디버그 화면이 보여서 학습에 편리합니다.
    # (실제 서비스 배포 시에는 반드시 debug=False 로 바꿔야 합니다.)
    app.run(debug=True)
