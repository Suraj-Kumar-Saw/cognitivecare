import re

def process_file():
    with open('care/views.py', 'r') as f:
        content = f.read()

    if 'import logging' not in content:
        content = content.replace('from django.shortcuts import render\n', 'from django.shortcuts import render\nimport logging\n\nlogger = logging.getLogger(__name__)\n')

    # Find all def statements and insert logger right after
    pattern = re.compile(r'^(def\s+([a-zA-Z0-9_]+)\(.*?:\s*\n)(?:\s*\"\"\"(?:.*?)\"\"\"\n)?', re.MULTILINE | re.DOTALL)

    def replacer(match):
        full_def = match.group(0)
        func_name = match.group(2)
        indent = "    "
        log_statement = f'{indent}logger.info(f"Executing {func_name}")\n'

        # Determine if it's a request handler by checking if 'request' is an argument
        if '(request' in full_def:
            log_statement += f'{indent}logger.debug(f"Request method: {{request.method}}")\n'

        return full_def + log_statement

    new_content = pattern.sub(replacer, content)

    with open('care/views.py', 'w') as f:
        f.write(new_content)

process_file()
