from utils import *
from itertools import combinations

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI')
                for cs in ('123', '456', '789')]
unitlist = row_units + column_units + square_units

# Update the unit list to add the new diagonal units
unitlist = unitlist + \
           [[''.join(i) for i in zip(rows, cols)]] + \
           [[''.join(i) for i in zip(rows, cols[::-1])]]

# Must be called after all units (including diagonals) are added to the
# unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated
    boxes in a unit and there are only two digits that can go in those two
    boxes, then those two digits can be eliminated from the possible
    assignments of all other boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input
    once, or it can continue processing pairs of naked twins until there are no
    such pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all
    pairs of naked twins from the original input. (For example, if you start
    processing pairs of twins and eliminate another pair of twins before the
    second pair is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other
    strategies, and because it is simpler (since the reduce_puzzle function
    already calls this strategy repeatedly).
    """

    for box1, v in values.items():
        # find boxes with two values
        if len(v) == 2:
            # find other boxes in unit with same two values
            for unit in units[box1]:
                bs = [box1 for box1 in unit if values[box1] == v]
                # if there are two boxes with the same two values, eliminate
                # values from other boxes in unit
                if len(bs) == 2:
                    for box2 in [box for box in unit if box not in bs]:
                        for i in v:
                            values[box2] = values[box2].replace(i, '')

    return values


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    for values_k, values_v in values.items():
        # find boxes with only a single value
        if len(values_v) == 1:
            for box in peers[values_k]:
                # elimate single value from peer boxes
                values[box] = values[box].replace(values_v, '')

    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a
    certain digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the
    classroom
    """
    for unit in unitlist:
        for d in '123456789':
            # find the locations in which digit d is present in the unit
            d_locations = [b for b in unit if d in values[b]]
            # if only once, set that box to d
            if len(d_locations) == 1:
                values[d_locations[0]] = d

    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint
        strategies no longer produces any changes, or False if the puzzle is
        unsolvable
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys()
                                    if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys()
                                  if len(values[box]) == 1])

        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available
        # values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve
    puzzles that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the
    classroom and extending it to call the naked twins strategy.
    """

    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False
    elif all(len(v) == 1 for v in values.values()):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    m = min({b: values[b] for b in boxes if len(values[b]) > 1},
            key=lambda k: len(values[k]))

    # Now use recursion to solve each one of the resulting sudokus, and if one
    # returns a value (not False), return that answer!
    for v in values[m]:
        candidate = values.copy()
        candidate[m] = v
        res = search(candidate)
        if res:
            return res


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.

        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....
        52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no
        solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6.."\
    "4...4....8....52.............3'

    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print("We could not visualize your board due to a pygame issue. Not a"
              "problem! It is not a requirement.")
