import re
from llm import complete
from prompt import build_system_prompt, RETRY_PROMPT

def _clean(text: str) -> str:
    text = re.sub(r"^```(?:sql)?\s*|\s*```$", "", text.strip(), flags=re.I).strip()
    if text.startswith("CANNOT_ANSWER"):
        return "CANNOT_ANSWER"
    return text.rstrip(";") + ";"

def generate_sql(question, schema, dialect="SQLite", history=None,
                 error=None, previous_sql=None) -> str:
    system = build_system_prompt(schema, dialect)
    messages = list(history or [])
    messages.append({"role": "user", "content": question})
    if error and previous_sql:
        messages.append({"role": "assistant", "content": previous_sql})
        messages.append({"role": "user", "content": RETRY_PROMPT.format(error=error)})
    return _clean(complete(system, messages))