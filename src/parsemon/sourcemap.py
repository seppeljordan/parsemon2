from typing import List


def display_location(line, column) -> str:
    return "L: {line}, C: {column}".format(
        line=line,
        column=column,
    )


def find_linebreak_indices(document) -> List[int]:
    def iterate():
        for (character, index) in zip(document, range(0, len(document))):
            if character == "\n":
                yield index

    return list(iterate())


def find_line_in_indices(index, indices):
    return find_location_in_indices(index, indices)[0]


def find_column_in_indices(index, indices):
    return find_location_in_indices(index, indices)[1]


def find_location_in_indices(index, indices):
    if not indices:
        line = 1
        column = index
    else:
        length = len(indices)
        start = 0
        end = length
        while True:
            middle = (start + end) // 2
            if end - start <= 1:
                line = middle + (2 if indices[middle] < index else 1)
                break
            else:
                if indices[middle] >= index:
                    end = middle
                else:
                    start = middle
        column = index - indices[line - 2] - 1
    return line, column
