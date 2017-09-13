from typing import List


def display_location(line, column):
    return 'L: {line}, C: {column}'.format(
        line=line,
        column=column,
    )

def find_linebreak_indices(document) -> List[int]:
    def iterate():
        for (character, index) in zip(document,range(0,len(document))):
            if character == '\n':
                yield index
    return list(iterate())
