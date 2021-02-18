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

class TRANSITION_LABELS:
    START_STATE = 'START_STATE'
    CONDITION_FUNCTION = 'CONDITION'
    NEXT_STATE = 'NEXT_STATE'
    SHOULD_START_NEW_TEXT = 'NEW_TEXT'
    SHOULD_APPEND_TEXT = 'APPEND_TEXT'

def is_table_line(line):
    return re.search("(?:\|.+\|)|(?:-{3,})", line)

def not_table_line(line):
    return not is_table_line(line)

def is_target_label_heading(line, label_text):
    return label_text and re.search("#+.*{}".format(label_text), line)

def get_state_transitions(target_heading_text):
    
    def is_target_label_heading_curry(line):
        return is_target_label_heading(line, target_heading_text)
   
    STATE_TRANSITION_LABELS = [
        TRANSITION_LABELS.START_STATE,
        TRANSITION_LABELS.CONDITION_FUNCTION,
        TRANSITION_LABELS.NEXT_STATE,
        TRANSITION_LABELS.SHOULD_START_NEW_TEXT,
        TRANSITION_LABELS.SHOULD_APPEND_TEXT
    ]

    STATE_TRANSITIONS = [
        [STATE.WATCHING_WAITING, is_table_line, STATE.IN_TABLE, True, True],
        [STATE.WATCHING_WAITING, is_target_label_heading_curry, STATE.TARGET_LABEL_FOUND, False, False],
        [STATE.IN_TABLE, is_table_line, STATE.IN_TABLE, False, True],
        [STATE.IN_TABLE, not_table_line, STATE.FINISHED_UNLABELED_TABLE, False, False],
        [STATE.FINISHED_UNLABELED_TABLE, is_target_label_heading_curry, STATE.TARGET_LABEL_FOUND, False, False],
        [STATE.TARGET_LABEL_FOUND, is_table_line, STATE.IN_TARGET_TABLE, True, True],
        [STATE.IN_TARGET_TABLE, is_table_line, STATE.IN_TARGET_TABLE, False, True],
        [STATE.IN_TARGET_TABLE, not_table_line, STATE.FINISHED_TARGET_TABLE, False, False]
    ]
    transition_dictionaries = [dict(zip(STATE_TRANSITION_LABELS, transition)) for transition in STATE_TRANSITIONS]
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
                continue
        
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

    entry_lines = [line for line in lines[1:] if not line.startswith('---')]

    for entry in entry_lines:
        cells = [cell.strip() for cell in entry.split('|') if cell and not cell.isspace()]
        rows.append(dict(zip(headers, cells)))

    return rows