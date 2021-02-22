#!/usr/bin/env python3

import re

def is_table_line(line):
    return _is_table_line(line) and not _is_dashes_and_pipes_only(line)

def is_table_dash_row(line):
    return _is_table_line(line) and _is_dashes_and_pipes_only(line)
    #return re.search("(?:\|[ \-\t]*)+\|", line)

def _is_table_line(line):
    return re.search("(?:\|.+\|)|(?:-{3,})", line)

def _is_dashes_and_pipes_only(line):
    return len(re.sub('[\|\\s-]', '', line)) == 0

def not_table_line(line):
    return not is_table_line(line)

def is_target_label_heading(line, label_text):
    return label_text and re.search("#+.*{}".format(label_text), line)

class STATE:
    WATCHING_WAITING = 'WATCHING_WAITING'
    IN_TABLE = 'IN_TABLE'
    ON_TABLE_DASH_ROW = 'ON_TABLE_DASH_ROW'
    FINISHED_UNLABELED_TABLE = 'FINISHED_UNLABELED_TABLE'
    TARGET_LABEL_FOUND = 'TARGET_LABEL_FOUND'
    IN_TARGET_TABLE = 'IN_TARGET_TABLE'
    ON_TARGET_TABLE_DASH_ROW = 'ON_TARGET_TABLE_DASH_ROW'
    FINISHED_TARGET_TABLE = 'FINISHED_TARGET_TABLE'
    DONE = 'DONE'

class TRANSITION_LABELS:
    START_STATE = 'START_STATE'
    CONDITION_FUNCTION = 'CONDITION'
    NEXT_STATE = 'NEXT_STATE'
    SHOULD_START_NEW_TEXT = 'NEW_TEXT'
    SHOULD_APPEND_TEXT = 'APPEND_TEXT'

    ALL_LABELS = (
        START_STATE,
        CONDITION_FUNCTION,
        NEXT_STATE,
        SHOULD_START_NEW_TEXT,
        SHOULD_APPEND_TEXT
    )

def get_state_transitions(target_heading_text):

    def is_target_label_heading_curry(line):
        return is_target_label_heading(line, target_heading_text)

    STATE_TRANSITIONS = [
        [STATE.WATCHING_WAITING, is_table_line, STATE.IN_TABLE, True, True],
        [STATE.WATCHING_WAITING, is_target_label_heading_curry, STATE.TARGET_LABEL_FOUND, False, False],
        [STATE.IN_TABLE, is_table_line, STATE.IN_TABLE, False, True],
        [STATE.IN_TABLE, is_table_dash_row, STATE.ON_TABLE_DASH_ROW, False, True],
        [STATE.IN_TABLE, not_table_line, STATE.FINISHED_UNLABELED_TABLE, False, False],
        [STATE.ON_TABLE_DASH_ROW, is_table_line, STATE.IN_TABLE, False, True],
        [STATE.FINISHED_UNLABELED_TABLE, is_target_label_heading_curry, STATE.TARGET_LABEL_FOUND, False, False],
        [STATE.TARGET_LABEL_FOUND, is_table_line, STATE.IN_TARGET_TABLE, True, True],
        [STATE.IN_TARGET_TABLE, is_table_line, STATE.IN_TARGET_TABLE, False, True],
        [STATE.IN_TARGET_TABLE, is_table_dash_row, STATE.ON_TARGET_TABLE_DASH_ROW, False, True],
        [STATE.IN_TARGET_TABLE, not_table_line, STATE.FINISHED_TARGET_TABLE, False, False],
        [STATE.ON_TARGET_TABLE_DASH_ROW, is_table_line, STATE.IN_TARGET_TABLE, False, True],
    ]
    transition_dictionaries = [dict(zip(TRANSITION_LABELS.ALL_LABELS, transition)) for transition in STATE_TRANSITIONS]
    starting_states = list(set([td[TRANSITION_LABELS.START_STATE] for td in transition_dictionaries]))
    transitions = {k: [td for td in transition_dictionaries if td[TRANSITION_LABELS.START_STATE] == k] for k in starting_states}
    return transitions

def get_table_text(markdown, target_heading_text = None):
    TRANSITIONS = get_state_transitions(target_heading_text)

    md_lines = markdown.splitlines()
    state = STATE.WATCHING_WAITING
    table_text = []

    for line in md_lines:
        possible_transitions = TRANSITIONS[state]

        for transition in possible_transitions:
            if (transition[TRANSITION_LABELS.CONDITION_FUNCTION](line)):
                state = transition[TRANSITION_LABELS.NEXT_STATE]
                if transition[TRANSITION_LABELS.SHOULD_START_NEW_TEXT]: table_text = []
                if transition[TRANSITION_LABELS.SHOULD_APPEND_TEXT]: table_text.append(line)
                break

        if state not in TRANSITIONS:
            break

    table_lines = [line.strip() for line in table_text]

    return '\n'.join(table_lines)


def table_to_rows(table_text):
    if not table_text:
        return []

    rows = []
    lines = table_text.splitlines()
    headers = [entry.strip() for entry in lines[0].split('|') if entry and not entry.isspace()]

    entry_lines = [line.strip() for line in lines[1:] if not _is_dashes_and_pipes_only(line)]

    for entry in entry_lines:
        cells = [cell.strip() for cell in entry.split('|')][1:-1]
        row = dict(zip(headers, cells))
        for key in headers:
            if row[key] == '': row.pop(key)

        rows.append(row)

    return rows