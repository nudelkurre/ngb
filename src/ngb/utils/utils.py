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
