import logging
from systemd.journal import JournalHandler
import sys


def cut_string_length(text, length):
    old_text = text.split(" ")
    new_text = text[:length].split(" ")
    new_text_last_index = len(new_text) - 1
    if old_text[new_text_last_index] == new_text[new_text_last_index]:
        return " ".join(new_text)
    else:
        return " ".join(new_text[:-1])


def wrap_string_at(text, length):
    words = text.split(" ")
    lines = []
    line = ""
    for index, word in enumerate(words):
        tmp_line = line
        tmp_line = f"{tmp_line} {word}".lstrip().rstrip()
        if index == len(words) - 1:
            lines.append(tmp_line)
        elif len(word) >= length:
            lines.append(word)
            line = ""
        elif index < len(words) - 1 and len(tmp_line) >= length:
            lines.append(line)
            line = ""
        else:
            line = tmp_line
    return "\n".join(lines)


def log_error(message, write_to_journal=True):
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    log = logging.getLogger(__name__)
    if write_to_journal:
        log.addHandler(JournalHandler())
    log.addHandler(stdout_handler)
    log.setLevel(logging.ERROR)
    log.error(message)


def log_warning(message, write_to_journal=True):
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    log = logging.getLogger(__name__)
    if write_to_journal:
        log.addHandler(JournalHandler())
    log.addHandler(stdout_handler)
    log.setLevel(logging.WARNING)
    log.warn(message)


def log_info(message, write_to_journal=True):
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    log = logging.getLogger(__name__)
    if write_to_journal:
        log.addHandler(JournalHandler())
    log.addHandler(stdout_handler)
    log.setLevel(logging.INFO)
    log.info(message)
