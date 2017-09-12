from parsemon.sourcemap import display_location


def test_display_location_contains_the_actual_line_number():
    line = 283
    assert str(line) in display_location(line=line, column=0)

def test_dist_location_contains_the_actual_column_number_supplied():
    column = 465
    assert str(column) in display_location(line=0, column=column)
