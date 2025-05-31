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
    info = ""
    for test_case in test_cases:
        output = execute_code(stdin=test_case.input or "", code=code)

        if test_case.expected_run_time_ms < output.get("runtime", 0):
            info += f"Test Case {max_score + 1}: runtime failed ❌\nprocess run time = {output.get('runtime', 0)} ms more than expected run time ms = {test_case.expected_run_time_ms} ms\n\n"

        elif test_case.expected == output.get("stdout", output.get("stderr", "")):
            info += f"Test Case {max_score + 1}: Passed ✅\n\n"
            score += 1

        else:
            info += f"Test Case {max_score + 1}: output failed ❌\nyour output is not match expected :(\n\n"

        max_score += 1

    info = f"==== Result ====\n{score}/{max_score} ({(score/max_score) * 100}%)\n\n" + info

    submit = Submit().filter(filters=[("id", "=", submit_id)], limit=1)[0]
    submit.update({
        "max_score": max_score,
        "score": score,
        "info": info,
        "status": SubmitState.FINISH
    })
