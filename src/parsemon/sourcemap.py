from typing import List, Sized


def display_location(line, column) -> str:
    return 'L: {line}, C: {column}'.format(
        line=line,
        column=column,
    )


def find_linebreak_indices(
        document: Sized
) -> List[int]:
    def iterate():
        for (character, index) in zip(document, range(0, len(document))):
            if character == '\n':
                yield index
    return list(iterate())


def find_line_in_indices(location, indices):
    if not indices:
        return 1
    length = len(indices)
    start = 0
    end = length
    while True:
        middle = (start + end) // 2
        if end - start <= 1:
            if indices[middle] < location:
                return middle + 2
            else:
                return middle + 1
        else:
            if indices[middle] > location:
                end = middle
            else:
                start = middle
