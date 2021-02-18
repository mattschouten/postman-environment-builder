#!/usr/bin/env python3

import re

class STATE:
    WATCHING_WAITING = 1
    IN_TABLE = 2
    FINISHED_UNLABELED_TABLE = 3
    TARGET_LABEL_FOUND = 4
    IN_TARGET_TABLE = 5
    FINISHED_TARGET_TABLE = 6
    DONE = 99

def is_table_line(line):
    return re.search("(?:\|.+\|)|(?:-{3,})", line)

def is_target_label_heading(line, label_text):
    return label_text and re.search("#+.*{}".format(label_text), line)

def get_table_text(markdown, target_heading_text = None):
    md_lines = markdown.splitlines()
    state = STATE.WATCHING_WAITING
    table_text = []

    for line in md_lines:
        if state == STATE.WATCHING_WAITING:
            if is_table_line(line):
                state = STATE.IN_TABLE
                table_text = [line]
                continue

        if state == STATE.IN_TABLE:
            if (is_table_line(line)):
                table_text.append(line)
                continue
            else:
                state = STATE.FINISHED_UNLABELED_TABLE
                continue
        
        if state in [STATE.FINISHED_UNLABELED_TABLE, STATE.WATCHING_WAITING]:
            if (is_target_label_heading(line, target_heading_text)):
                state = STATE.TARGET_LABEL_FOUND
                continue
        
        if state == STATE.TARGET_LABEL_FOUND:
            if (is_table_line(line)):
                table_text = [line]
                state = STATE.IN_TARGET_TABLE
                continue
        
        if state == STATE.IN_TARGET_TABLE:
            if (is_table_line(line)):
                table_text.append(line)
                continue
            else:
                state = STATE.FINISHED_TARGET_TABLE
                continue

    table_lines = [line.strip() for line in table_text]

    return '\n'.join(table_lines)


def table_to_rows(table_text):
    if not table_text:
        return []

    rows = []
    lines = table_text.splitlines()
    headers = [entry.strip() for entry in lines[0].split('|') if entry and not entry.isspace()]

    entry_lines = [line for line in lines[1:] if not line.startswith('---')]

    for entry in entry_lines:
        cells = [cell.strip() for cell in entry.split('|') if cell and not cell.isspace()]
        rows.append(dict(zip(headers, cells)))

    return rows