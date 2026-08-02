import unittest

from cogs.redsec_chat import ReyChat


class ReyChatTests(unittest.TestCase):

    def test_sanitize_answer_removes_generic_ai_identity(self):
        chat = ReyChat.__new__(ReyChat)
        answer = "Soy ChatGPT, basado en la arquitectura GPT-4 de OpenAI."

        cleaned = chat._sanitize_answer(answer)

        self.assertNotIn("ChatGPT", cleaned)
        self.assertNotIn("OpenAI", cleaned)
        self.assertIn("Rey", cleaned)

    def test_system_prompt_mentions_albion_and_real_item_names(self):
        prompt = ReyChat._build_system_prompt()

        self.assertIn("Albion Online", prompt)
        self.assertIn("Grailseeker", prompt)
        self.assertIn("Spirit Hunter", prompt)
