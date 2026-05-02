# flask-tutorial — Claude Code Plugin (학습 데모)

## 이게 뭔가요

`flask-tutorial` 은 [`gwpark-dev/flask-todo`](https://github.com/gwpark-dev/flask-todo) 학습용 Flask 프로젝트에서 쓰던 Claude Code 워크플로 자산을 **plugin 패키지 형태로 묶어 본 데모**입니다.

이 패키지의 정체성은 두 가지입니다.

1. **학습 자료** — Claude Code Tier 6(Plugins) 학습의 결과물로, plugin / marketplace 구조가 어떻게 생겼는지 직접 만들어 보면서 익힌 산출물입니다.
2. **정적 데모** — npm publish 나 GitHub release 같은 실제 배포 절차는 거치지 않습니다. 이 폴더 자체가 "이런 모양이구나" 를 보여 주는 골격입니다. **실서비스 plugin 으로 오해하지 마세요.**

원본 자산은 같은 저장소의 `.claude/` 폴더에 살아 있고, 이 plugin 폴더의 내용물은 그것의 사본입니다. 두 벌이 동시에 있는 이유는 §"소스/원본" 절에서 설명합니다.

---

## 무엇이 들어 있나요

이 plugin 은 컴포넌트 **2개** 를 제공합니다.

### 1) Skill — `add-route`

`skills/add-route/SKILL.md` 에 들어 있습니다.

학습자가 "새 라우트 추가해 줘", "POST 라우트 만들어 줘", "버튼 누르면 ~ 하는 기능 만들어 줘" 같은 요청을 하면 자동으로 발동되는 절차서입니다. Flask 학습 프로젝트에서 자주 빠지는 함정 10개(PRG 패턴, `<int:>` 컨버터, `db.session.commit()` 누락 등)를 체크리스트로 묶어 두었고, 라우트 함수와 HTML 폼 작성 템플릿까지 끼워 두었습니다. 빠르게 동작하는 코드보다 **"왜 이렇게 쓰는지" 가 길게 풀려 있는 튜토리얼 톤** 을 새 라우트에서도 자동으로 유지시키는 게 목적입니다.

### 2) Subagent — `code-reviewer`

`agents/code-reviewer.md` 에 들어 있습니다.

학습자가 "리뷰해줘", "검토해줘", "점검해줘" 같은 요청을 하면 발동되는 **읽기 전용 리뷰어** 입니다 (Read / Grep / Glob 만 가지고 있어 코드를 절대 수정하지 않습니다). `CLAUDE.md` 의 규칙, `add-route` Skill 의 함정 체크리스트 10개, 학습 포인트 라벨 일관성, 튜토리얼 주석 밀도, YAGNI 위반 여부를 자동 점검하고 ✅/⚠️/❌ 형식으로 보고합니다. 학습자에게 "여기는 잘 됐다" 는 신호도 중요하므로 통과 항목도 비우지 않는 게 출력 규칙입니다.

---

## 왜 Hook 은 빠졌나요

원본 저장소(`flask-todo/.claude/hooks/notify-review.ps1`) 에는 Edit/Write 도구 사용 시 코드 리뷰를 권장하는 알림을 띄우는 PostToolUse 훅이 있습니다. 이 훅은 다음과 같은 이유로 **이 plugin 패키지에는 의도적으로 포함하지 않았습니다.**

- **`.ps1` 파일은 Windows PowerShell 전용** 입니다. macOS / Linux 환경에서 plugin 을 설치하면 훅 실행 자체가 실패합니다.
- 학습 데모로서 plugin 구조를 보여 주는 목적이 우선이고, OS 의존적인 자산은 노이즈가 됩니다.
- 기존 저장소의 `.claude/hooks/` 에서는 그대로 작동 중이므로, **Windows 사용자는 본 저장소의 `.claude/` 자산을 그대로 쓰면 됩니다** (이중 등록 불필요).

훅을 OS 중립적으로 재작성하는 작업은 후속 검토 항목이며, GitHub Issue #1 에 기록되어 있습니다.

---

## (가상) 설치 방법

> ⚠️ **아래 명령어는 가상 예시입니다.** 이 plugin 은 실제 marketplace 에 등록돼 있지 않으므로, 명령어 자체는 동작하지 않습니다. plugin 설치 흐름이 어떤 모양인지 보여 주는 골격으로만 읽어 주세요.

이 저장소를 marketplace 로 등록하고 plugin 을 설치하는 흐름은 대략 다음과 같습니다.

```
# 1) 마켓플레이스 등록 — 이 저장소가 .claude-plugin/marketplace.json 을 들고 있다고 알림
/plugin marketplace add gwpark-dev/flask-todo

# 2) 마켓플레이스 안의 plugin 설치
/plugin install flask-tutorial@gwpark-dev-marketplace

# 3) 설치 확인
/plugin list
```

설치가 끝나면 `flask-tutorial` plugin 이 활성화되고, Claude Code 가 새 세션에서 `add-route` Skill 과 `code-reviewer` Subagent 를 자동으로 인식합니다.

(**다시 강조**: 위 흐름은 학습용 골격이며, 본 패키지는 정적 데모라 실제 명령어로는 동작하지 않습니다. Tier 6 학습 단계에서 "이 그림이 어떻게 생겼는지" 만 잡고 갑니다.)

---

## 사용 방법

설치 후 학습자가 평소처럼 Claude Code 와 대화하면, 다음과 같은 발화에서 plugin 자산이 자동으로 발동됩니다.

### `add-route` Skill 발동 예시

- "할 일을 일괄 완료하는 라우트 추가해 줘"
- "/share/<int:id> 같이 단건 조회 GET 라우트 만들어 줘"
- "검색 기능 추가해 줘 — 폼 입력으로 task 필터링"

→ Claude 가 Skill 의 절차에 따라 "사전 점검 → 라우트 함수 → 템플릿 폼 → 튜토리얼 주석 → 검증" 5단계를 따라 진행합니다.

### `code-reviewer` Subagent 발동 예시

- "지금까지 작성한 코드 리뷰해 줘"
- "최근 추가한 라우트 점검해 줘"
- "PR 올리기 전에 한 번 검토해 줘"

→ 별도 Subagent 가 실행되며, ✅/⚠️/❌ 형식의 리뷰 보고를 돌려줍니다. 코드를 직접 수정하지는 않습니다(읽기 전용).

---

## 소스/원본

이 plugin 폴더의 자산은 본 저장소 `.claude/` 폴더의 **사본** 입니다. 정확한 대응표:

| 본 패키지의 위치 | 원본 위치 | 비고 |
| --- | --- | --- |
| `skills/add-route/SKILL.md` | `.claude/skills/add-route/SKILL.md` | 한 글자도 다르지 않은 사본 |
| `agents/code-reviewer.md` | `.claude/agents/code-reviewer.md` | 한 글자도 다르지 않은 사본 |
| (제외) | `.claude/hooks/notify-review.ps1` | OS 의존성 — §"왜 Hook 은 빠졌나요" 참고 |
| (제외) | `.claude/settings.json` | 훅 등록용이라 plugin 에는 불필요 |

**왜 두 벌이 있나** — 본 저장소의 `.claude/` 자산은 **이 저장소를 직접 열었을 때** 작동하는 워크플로이고, 본 plugin 폴더의 자산은 **plugin 을 설치한 다른 프로젝트에서** 작동하기 위한 패키지 사본입니다. 둘은 같은 내용을 두 가지 배포 방식으로 보여 주는 학습용 짝입니다.

---

## 라이선스 / 출처

학습용 자료입니다. 본 plugin 의 톤과 절차는 [`gwpark-dev/flask-todo`](https://github.com/gwpark-dev/flask-todo) 저장소의 `CLAUDE.md` 에서 비롯되며, AI(Claude Code) 와의 협업으로 작성되었습니다.
