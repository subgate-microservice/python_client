import ast
import re
import sys
import textwrap
from pathlib import Path

import pytest

from snippets.src.config import BASE_MD_DIR

MAPPER = {
    Path("../tests/test_10_client.py"): Path(BASE_MD_DIR, "client.md"),
    Path("../tests/test_20_simple_examples.py"): Path(BASE_MD_DIR, "simple-examples.md"),
    Path("../tests/test_30_plan_management.py"): Path(BASE_MD_DIR, "plan-management.md"),
    Path("../tests/test_40_subscription_management_create.py"): Path(BASE_MD_DIR, "subscription-management.md"),
    Path("../tests/test_50_webhook_management.py"): Path(BASE_MD_DIR, "webhook-management.md"),
}


def extract_functions(file_path: Path) -> dict:
    """Извлекает тело функций без сигнатуры, сохраняя комментарии и импорты."""
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source)

    functions = {}
    lines = source.splitlines()

    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            start_line = node.lineno  # Первая строка — это сигнатура функции
            end_line = node.end_lineno  # Последняя строка тела функции

            # Извлекаем строки с телом функции (без сигнатуры)
            body_lines = lines[start_line:end_line]

            # Убираем общий отступ
            body_text = textwrap.dedent("\n".join(body_lines))

            functions[node.name] = body_text

    return functions


def run_tests():
    """Запускает pytest, чтобы убедиться, что код рабочий."""
    result = pytest.main(["../tests", "-q", "--disable-warnings"])
    if result != 0:
        sys.exit("Некоторые тесты не прошли!")  # Останавливаем выполнение


def update_markdown(python_file_path: Path, md_file_path: Path):
    """Обновляет только вставки кода в Markdown."""
    functions = extract_functions(python_file_path)
    md_content = Path(md_file_path).read_text(encoding="utf-8")

    print(f"Updating docs in {md_file_path}\n"
          f"Replace following functions: {list(functions.keys())}\n")

    left_functions_for_replace = {x for x in functions.keys() if "test_" in x}

    def replace_code(match):
        func_name = match.group(1)
        left_functions_for_replace.discard(func_name)
        if func_name in functions:
            new_code = functions[func_name]
            return f'<!-- CODE: {func_name} -->\n\n```python\n{new_code}\n```\n\n<!-- END CODE -->'
        return match.group(0)  # Оставляем неизменным, если не нашли

    # Улучшенное регулярное выражение
    expression = r'<!-- CODE: (\w+) -->\n*\s*```python\n(.*?)\n\s*```\n*\s*<!-- END CODE -->'
    md_content = re.sub(expression, replace_code, md_content, flags=re.DOTALL)

    Path(md_file_path).write_text(md_content, encoding="utf-8")

    expected_len = len([x for x in functions.keys() if "test_" in x])
    real_len = expected_len - len(left_functions_for_replace)
    print(
        f"Expected snippets for replace: {expected_len}.\n"
        f"Real replaced snippets: {real_len}.\n"
        f"Missed functions: {left_functions_for_replace}"
    )


def main():
    for python_file_path, md_file_path in MAPPER.items():
        update_markdown(python_file_path, md_file_path)


if __name__ == "__main__":
    # run_tests()
    main()
