from llm_answers import LLMAnswer
import string

class LLMOutputParser():
    def parse(self, text: str) -> LLMAnswer:
        s = text.strip().lower().translate(str.maketrans('', '', string.punctuation))
        if "the solution is" in s:
            return LLMAnswer.SHOW_RIDDLE

        if "you won" in s:
            return LLMAnswer.WIN

        if "yes" in s:
            return LLMAnswer.YES
        if "no" in s:
            return LLMAnswer.NO


        return LLMAnswer.INVALID
