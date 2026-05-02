# PostToolUse 훅: app.py 또는 templates/*.html 가 Edit/Write 으로 수정되면
# code-reviewer 서브에이전트 리뷰를 권장하는 한 줄 알림을 Claude 의 다음 컨텍스트에 주입합니다.
#
# Claude Code 가 stdin 으로 훅 페이로드 JSON 을 흘려 줍니다. 모양은 다음과 같습니다.
#   {
#     "tool_name": "Edit",
#     "tool_input":  { "file_path": "...", ... },
#     "tool_response": { ... }
#   }
# matcher (settings.json) 는 tool_name 까지만 걸러 주므로, 파일 경로 필터는 이 안에서 합니다.
#
# 출력 방식 — 단순 텍스트(Write-Host) 가 아니라 JSON 한 줄을 stdout 으로 내보냅니다.
# Claude Code 의 PostToolUse 훅 스펙에서 아래 형태의 JSON 을 받으면
# additionalContext 문자열을 다음 모델 응답의 system 컨텍스트에 끼워 넣어 줍니다.
#   { "hookSpecificOutput": { "hookEventName": "PostToolUse", "additionalContext": "..." } }
# 이렇게 하면 transcript 뷰(Ctrl+R) 에만 머물지 않고 모델 응답 흐름에 자연스럽게 통합됩니다.
# exit code 는 0 을 유지합니다. exit 2 는 "차단" 시그널이라 도구 호출 자체가 막혀 의도와 다릅니다.

# 인코딩 방어 — 한국어 Windows + PowerShell 5.1 환경에서 가장 잘 깨지는 지점입니다.
# Claude Code 는 stdin/stdout 을 UTF-8 로 다루지만, PS 5.1 의 기본 InputEncoding/OutputEncoding 은
# 시스템 코드페이지(보통 CP949). 그대로 두면 한글 경로(예: C:\Users\박건우\...) 가
# 깨진 바이트로 들어와 ConvertFrom-Json 이 실패하고, 한글이 섞인 stdout 도 Claude Code 측에서
# JSON 디코드가 어긋날 수 있습니다. 양방향 모두 UTF-8 로 강제합니다.
#
# 추가로 — 이 .ps1 파일 자체도 반드시 "UTF-8 with BOM" 으로 저장돼 있어야 합니다.
# PS 5.1 은 BOM 이 없는 .ps1 을 시스템 코드페이지로 읽기 때문에, BOM 없는 UTF-8 로 저장하면
# 본문의 한글 문자열 리터럴(예: "수정됨") 이 스크립트 로드 시점에 이미 mojibake 가 됩니다.
# 그 단계에서 깨지면 아래 OutputEncoding 설정으로도 복구가 안 됩니다.
[Console]::InputEncoding  = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 주의: $input 자동변수 대신 [Console]::In.ReadToEnd() 를 쓰는 이유 —
# 호출 환경에 따라 $input 이 한 줄씩 끊겨 들어와 ConvertFrom-Json 이 실패할 수 있어,
# stdin 전체를 한 문자열로 읽는 방식이 가장 안정적입니다.
$json = [Console]::In.ReadToEnd()
if (-not $json) { return }

$payload = $json | ConvertFrom-Json
$p = $payload.tool_input.file_path
if (-not $p) { return }

# 학습 대상 파일만 알림. 그 밖의 파일(README.md, CLAUDE.md, .gitignore 등)은 조용히 통과.
if ($p -like '*\app.py' -or $p -like '*\templates\*.html') {
    $name = Split-Path $p -Leaf
    $msg  = "[code-reviewer] $name 수정됨 — code-reviewer 서브에이전트 리뷰를 권장합니다."

    # 해시테이블을 ConvertTo-Json -Compress 로 직렬화해 한 줄짜리 JSON 으로 만듭니다.
    # -Compress 가 없으면 여러 줄로 예쁘게 들여쓰여 나오는데, hook 출력은 한 줄 JSON 이
    # 가장 안전합니다 (Claude Code 가 줄 단위로 파싱할 가능성을 고려).
    $out = @{
        hookSpecificOutput = @{
            hookEventName     = "PostToolUse"
            additionalContext = $msg
        }
    } | ConvertTo-Json -Compress

    # Write-Host 는 PowerShell 의 호스트 UI 로 직접 쓰기 때문에 stdout 파이프에 잡히지 않을 수 있습니다.
    # 반드시 Write-Output (또는 표현식 그대로 두기) 으로 파이프라인 출력에 실어 보내야
    # Claude Code 가 stdout 을 읽어 JSON 으로 해석할 수 있습니다.
    Write-Output $out
}
