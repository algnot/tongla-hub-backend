import json

from model.submit import Submit, SubmitState
from model.test_case import TestCase
from util.code import execute_code


def callback_submit(message):
    question_id = message.get("question_id")
    submit_id = message.get("submit_id")
    code = message.get("code")

    if not question_id:
        return

    test_cases = TestCase().filter([("question_id", "=", question_id)])

    max_score = 0
    score = 0
    info = []
    for test_case in test_cases:
        output = execute_code(stdin=test_case.input or "", code=code)

        base_info = {
            "test_case_id": test_case.id,
            "output": output,
            "expected_run_time_ms": test_case.expected_run_time_ms,
            "expected_output": test_case.expected,
        }

        if test_case.expected_run_time_ms < output.get("runtime", 0):
            info.append({
                **base_info,
                "score": 0,
                "description": f"process run time = {output.get('runtime', 0)} ms more than expected run time ms = {test_case.expected_run_time_ms} ms"
            })

        elif test_case.expected == output.get("stdout", output.get("stderr", "")):
            info.append({
                **base_info,
                "score": 1,
            })
            score += 1

        else:
            info.append({
                **base_info,
                "score": 0,
                "description": f"your output is not match expected"
            })

        max_score += 1

    submit = Submit().filter(filters=[("id", "=", submit_id)], limit=1)[0]
    submit.update({
        "max_score": max_score,
        "score": score,
        "info": json.dumps(info),
        "status": SubmitState.FINISH
    })
