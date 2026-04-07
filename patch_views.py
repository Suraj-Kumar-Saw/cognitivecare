import ast
import sys

def insert_logging(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()

    # Insert imports
    for i, line in enumerate(lines):
        if line.startswith('from django.shortcuts import render'):
            lines.insert(i+1, "import logging\n\nlogger = logging.getLogger(__name__)\n")
            break

    out = []
    in_func = False
    func_name = ""
    for line in lines:
        out.append(line)
        if line.startswith('def '):
            func_name = line.split('(')[0][4:]
            in_func = True
        elif in_func and line.strip() and not line.startswith('def '):
            indent = len(line) - len(line.lstrip())
            out.insert(-1, " " * indent + f"logger.debug(f'Entering {func_name} {{getattr(request, \"method\", \"\") if \"request\" in locals() else \"\"}}')\n")
            in_func = False

    with open(filepath, 'w') as f:
        f.writelines(out)

insert_logging('care/views.py')
