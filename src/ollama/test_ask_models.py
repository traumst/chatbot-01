import unittest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.ollama.ask_models import AskRequest, AskResponse, AskResponseComplete

LONG_STRING_130: str = "very long text, i repeat, " * 5
assert len(LONG_STRING_130) == 130

LONG_STRING_1170: str = "very long text, i repeat, " * 45
assert len(LONG_STRING_1170) == 1170

class TestGenerationModels(unittest.TestCase):

    def test_generation_request_success(self):
        valid_data = {
            "model": "deepseek-r1:1.5b",
            "prompt": "same here",
            "options": None
        }
        req = AskRequest(**valid_data)
        self.assertEqual(req.model, valid_data["model"])
        self.assertEqual(req.prompt, valid_data["prompt"])

    def test_generation_request_fail_model_too_long(self):
        invalid_data = {
            "model": LONG_STRING_130,
            "prompt": "some unimportant valid text",
        }
        with self.assertRaises(ValidationError):
            AskRequest(**invalid_data)

    def test_generation_request_fail_prompt_too_long(self):
        invalid_data = {
            "model": "deepseek-r1:1.5b",
            "prompt": LONG_STRING_1170,
        }
        with self.assertRaises(ValidationError):
            AskRequest(**invalid_data)

    def test_generation_response_success(self):
        iso_string = "2024-07-30T14:30:00"
        dt_object = datetime.fromisoformat(iso_string)
        valid_data = {
            "model": "deepseek-r1:1.5b",
            "created_at": iso_string,
            "response": "some chars, numbers, punctuation...",
            "done": False
        }
        resp = AskResponse(**valid_data)
        self.assertEqual(resp.model, valid_data["model"])
        self.assertTrue(isinstance(resp.created_at, datetime))
        self.assertEqual(dt_object, resp.created_at)
        self.assertEqual(resp.response, valid_data["response"])
        self.assertEqual(resp.done, valid_data["done"])

    def test_generation_response_fail_invalid_created_at(self):
        invalid_data = {
            "model": "deepseek-r1:1.5b",
            "created_at": "THIS-IS-NOT-A-DATE",
            "response": "some respectable chatter",
            "done": False
        }
        with self.assertRaises(ValidationError):
            AskResponse(**invalid_data)

    def test_generation_response_complete_success(self):
        valid_data = {
            "model": "deepseek-r1:1.5b",
            "created_at": "2025-02-20T22:01:08.74437Z",
            "response": "... and this is how it ended.",
            "done": True,
            "done_reason": "stop",
            "context": [1, 2, 3, 4],
            "total_duration": 2_000_000_000,  # 2 seconds
            "load_duration": 50_000_000,      # 0.05 seconds
            "prompt_eval_count": 5,
            "prompt_eval_duration": 100_000_000,  # 0.1 seconds
            "eval_count": 10,
            "eval_duration": 500_000_000        # 0.5 seconds
        }
        complete_resp = AskResponseComplete(**valid_data)
        self.assertEqual(complete_resp.model, valid_data["model"])
        self.assertTrue(isinstance(complete_resp.created_at, datetime))
        self.assertEqual(complete_resp.done_reason, valid_data["done_reason"])
        self.assertEqual(complete_resp.context, valid_data["context"])
        self.assertEqual(complete_resp.total_duration, timedelta(seconds=2))
        self.assertEqual(complete_resp.load_duration, timedelta(seconds=0.05))
        self.assertEqual(complete_resp.prompt_eval_duration, timedelta(seconds=0.1))
        self.assertEqual(complete_resp.eval_duration, timedelta(seconds=0.5))
        self.assertEqual(complete_resp.prompt_eval_count, valid_data["prompt_eval_count"])
        self.assertEqual(complete_resp.eval_count, valid_data["eval_count"])

    def test_generation_response_complete_fail_missing_fields(self):
        invalid_data = {
            "model": "deepseek-r1:1.5b",
            "created_at": "2025-02-20T22:01:08.74437Z",
            "response": "... this will not end well.",
            "done": True,
            # Missing done_reason, context, durations, counts
        }
        with self.assertRaises(ValidationError):
            AskResponseComplete(**invalid_data)

    def test_generation_response_complete_fail_invalid_duration(self):
        invalid_data = {
            "model": "deepseek-r1:1.5b",
            "created_at": "2025-02-20T22:01:08.74437Z",
            "response": "... this will not end well.",
            "done": True,
            "done_reason": "stop",
            "context": [1, 2, 3],
            "total_duration": "YO-THIS-IS-NOT-NANOSECONDS",
            "load_duration": 50_000_000,
            "prompt_eval_count": 5,
            "prompt_eval_duration": 100_000_000,
            "eval_count": 10,
            "eval_duration": 500_000_000
        }
        with self.assertRaises(ValidationError):
            AskResponseComplete(**invalid_data)

if __name__ == '__main__':
    unittest.main()
