
# coding: utf-8

# # yangs - Yet Another NonoGram Solver
# 
# 
# 

# ## Aim
# 
# Solve the first part of the GCHQ Christmas puzzle using a concise, easy-to-understand Python program.
# 
# ## Method
# 
# The [puzzle](http://www.gchq.gov.uk/press_and_media/news_and_features/Pages/Directors-Christmas-puzzle-2015.aspx) is a 25x25 [nonogram](https://en.wikipedia.org/wiki/Nonogram). I decided to write a program that uses the same method that I would use if solving the puzzle by hand:
# 
# 1. For each row and column, **generate the set of patterns** that match the given clues
# 2. For each row, **eliminate the patterns** that don't match the cells we already know
# 3. For each row, **deduce the known cells** based on the reduced pattern set
# 4. For each column, **eliminate the patterns** that don't match the cells we already know
# 5. For each column, **deduce the known cells** based on the reduced pattern set
# 6. Go back to 2. and repeat, unless we've solved it

# ## Imports and settings

# In[1]:

from itertools import combinations_with_replacement
SHOW_TESTS = True


# ## Input data
# 
# Put all the clues into a list of lists:

# In[2]:

ROW_CLUES = [
    [7, 3, 1, 1, 7,],
    [1, 1, 2, 2, 1, 1,],
    [1, 3, 1, 3, 1, 1, 3, 1,],
    [1, 3, 1, 1, 6, 1, 3, 1,],
    [1, 3, 1, 5, 2, 1, 3, 1,],
    [1, 1, 2, 1, 1,],
    [7, 1, 1, 1, 1, 1, 7,],
    [3, 3,],
    [1, 2, 3, 1, 1, 3, 1, 1, 2,],
    [1, 1, 3, 2, 1, 1,],
    [4, 1, 4, 2, 1, 2,],
    [1, 1, 1, 1, 1, 4, 1, 3,],
    [2, 1, 1, 1, 2, 5,],
    [3, 2, 2, 6, 3, 1,],
    [1, 9, 1, 1, 2, 1,],
    [2, 1, 2, 2, 3, 1,],
    [3, 1, 1, 1, 1, 5, 1,],
    [1, 2, 2, 5,],
    [7, 1, 2, 1, 1, 1, 3,],
    [1, 1, 2, 1, 2, 2, 1,],
    [1, 3, 1, 4, 5, 1,],
    [1, 3, 1, 3, 10, 2,],
    [1, 3, 1, 1, 6, 6,],
    [1, 1, 2, 1, 1, 2,],
    [7, 2, 1, 2, 5,],
]

COL_CLUES = [
    [7, 2, 1, 1, 7,],
    [1, 1, 2, 2, 1, 1,],
    [1, 3, 1, 3, 1, 3, 1, 3, 1,],
    [1, 3, 1, 1, 5, 1, 3, 1,],
    [1, 3, 1, 1, 4, 1, 3, 1,],
    [1, 1, 1, 2, 1, 1,],
    [7, 1, 1, 1, 1, 1, 7,],
    [1, 1, 3,],
    [2, 1, 2, 1, 8, 2, 1,],
    [2, 2, 1, 2, 1, 1, 1, 2,],
    [1, 7, 3, 2, 1,],
    [1, 2, 3, 1, 1, 1, 1, 1,],
    [4, 1, 1, 2, 6,],
    [3, 3, 1, 1, 1, 3, 1,],
    [1, 2, 5, 2, 2,],
    [2, 2, 1, 1, 1, 1, 1, 2, 1,],
    [1, 3, 3, 2, 1, 8, 1,],
    [6, 2, 1,],
    [7, 1, 4, 1, 1, 3,],
    [1, 1, 1, 1, 4,],
    [1, 3, 1, 3, 7, 1,],
    [1, 3, 1, 1, 1, 2, 1, 1, 4,],
    [1, 3, 1, 4, 3, 3,],
    [1, 1, 2, 2, 2, 6, 1,],
    [7, 1, 3, 2, 1, 1,],
]

ROW_LEN = len(COL_CLUES)
COL_LEN = len(ROW_CLUES)


# Set up a grid to contain the result, and fill in the cells we already know.
# 
# Notes:
# - I'm using 1 to represent a known filled cell, 0 for a known blank cell, and None for an unknown cell.
# - The rows must be repeated using list comprehension. Using list repetition **(i.e. result = [[None] \* ROW_LEN] * COL_LEN)** would result in a list of references to the same row list.

# In[3]:

# Create blank results grid
result = [[None] * ROW_LEN for c in range(COL_LEN)]

# Fill in the cells we already know
known_coords = {3: (3, 4, 12, 13, 21),
                8: (6, 7, 10, 14, 15, 18),
                16: (6, 11, 16, 20),
                21: (3, 4, 9, 10, 15, 20, 21)
               }

for row, cols in known_coords.items():
    for col in cols:
        result[row][col] = 1


# ## Helper functions
# 
# Define some functions to display the results:

# In[4]:

SYMBOLS = {None: '?', 1:'#', 0:'.'}

def print_row(row, i=0):
    print '%s [%s]' % (str(i).rjust(2), ' '.join(SYMBOLS[cell] for cell in row))
        
def print_grid(rows):
    col_labels = [str(i).rjust(2) for i in range (len(rows[0]))]
    print '   ', ' '.join(cl[0] for cl in col_labels)
    print '   ', ' '.join(cl[1] for cl in col_labels)
    for i, row in enumerate(rows):
        print_row(row, i)

# Test
if SHOW_TESTS:
    print_grid(result)


# And a function to count the number of unknown cells in the results. We'll use this to check if we've solved the puzzle, or if we're not making progress.

# In[5]:

def count_unknowns(rows):
    return sum(row.count(None) for row in rows)

# Test
if SHOW_TESTS:
    print 'Unknowns = %s' % count_unknowns(result)


# ## Generate sets of patterns
# 
# Terminology:
# - Block = one or more consecutive filled cells
# - Space = an unfilled cell
# - Clue = the lengths of each block
# - Pattern = a series of cells that match the clue
# 
# The **generate_patterns** function does step 1 of the general approach: give it the clue and the pattern length, and it generates all the possible patterns.
# 
# For the clue [7, 3, 1, 1, 7] and length = 25:
# 
# - There are 5 blocks, comprising 7 + 3 + 1 + 1 + 7 = 19 filled cells.
# - There are 6 **positions** where spaces can be inserted (numbered 0 through 5)
# - The middle 4 positions all must have at least one space - so there are 4 **fixed spaces**
# - That means there are 25 - 19 - 4 = 2 **movable spaces**, which can go in any permutation of the 6 positions
# - Therefore, there are 6CR2 = 21 different patterns that match this clue
# 
# 
# | position                | 0 | 1       | 1 |  2  | 2 | 3 | 3 | 4 | 4 | 5       | 5 |
# |-
# | blocks and fixed spaces |   | 1111111 | 0 | 111 | 0 | 1 | 0 | 1 | 0 | 1111111 |   |
# | movable spaces (any 2 of 6 positions)      | ? |         | ? |     | ? |   | ? |   | ? |         | ? | 
# 
# 

# In[6]:

def generate_patterns(clue, length):
    blocks = [0] + clue
    fixed_spaces = [0] + [1] * (len(clue) - 1) + [0]
    positions = range(len(blocks))
    n_movable_spaces = length - sum(clue) - len(clue) + 1
    for space_positions in combinations_with_replacement(positions, n_movable_spaces):
        movable_spaces = [space_positions.count(p) for p in positions]
        yield sum(([1] * b + [0] * (fs + ms) for b, fs, ms in zip(blocks, fixed_spaces, movable_spaces)), [])

# Test
if SHOW_TESTS:
    test_pats = list(generate_patterns([7, 3, 1, 1, 7], 25))
    print_grid(test_pats)


# ## Eliminate patterns
# 
# The **eliminate_patterns** function does steps 2 and 4 of the general approach: give it a list of patterns, and it will eliminate the patterns that don't match the already-known cells.
# 
# Notes:
# - The set of patterns is iterated in reverse order so that deleting an item won't change the indices of the items yet to be iterated.
# - The **any** function will short circuit as soon as it finds a cell in the pattern that conflicts with the known cells
# - I've used **del patterns[i]** instead of **patterns.pop(i)** because we don't need to do anything with the item after it's removed from the list
# 
# 

# In[7]:

def eliminate_patterns(patterns, knowns):
    for i in reversed(range(len(patterns))):
        if any(k not in (p, None) for p, k in zip(patterns[i], knowns)):
            del patterns[i]

# Test
if SHOW_TESTS:
    print 'Before:'
    print_grid(test_pats)
    print
    print 'Apply Knowns:'
    test_knowns = [1] + [None]*23 + [1]
    print_row(test_knowns)
    print
    print 'After:'
    eliminate_patterns(test_pats, test_knowns)
    print_grid(test_pats)


# ## Deduce known cells
# 
# The **generate_knowns** function does steps 3 and 5 of the general approach: give it a set of patterns, and it will deduce which cells are now known.
# 
# For each cell, if all the patterns have the same value for each cell, then that is the only possible value for that cell.
# 
# Notes:
# - **zip(*patterns)** transposes the pattern set so that we check one column at a time instead of one row a time
# - the **all** function will short circuit as soon as it finds a cell that doesn't match the cell in first pattern

# In[8]:

def generate_knowns(patterns):
    for col in zip(*patterns):
        yield col[0] if all(c == col[0] for c in col) else None

# Test
if SHOW_TESTS:
    print 'Patterns:'
    print_grid(test_pats)
    print
    print 'Knowns:'
    test_knowns = list(generate_knowns(test_pats))
    print_row(test_knowns)


# ## Solve it
# 
# Do step 1: generate sets of patterns that match the clues given for each row and column.

# In[9]:

rows_valid_patterns = [list(generate_patterns(c, ROW_LEN)) for c in ROW_CLUES]
cols_valid_patterns = [list(generate_patterns(c, COL_LEN)) for c in COL_CLUES]


# Calculate how many unknowns there are before we start trying to solve:

# In[10]:

unknowns = [count_unknowns(result)]


# Repeat through steps 2-5 until either:
# - There are no more unknowns i.e. we've solved it
# - The number of unknowns hasn't decreased since the last pass i.e. we've solved as much as possible
# 
# Notes:
# - **map** is used to apply **eliminate_patterns** and **generate_knowns** to multiple rows/columns
# - **zip(\*)** is used to transpose the **results** grid when working on columns, and transpose it back again before working on rows

# In[11]:

while len(unknowns) < 2 or unknowns[-1] not in (0, unknowns[-2]):
    map(eliminate_patterns, rows_valid_patterns, result)
    result = map(generate_knowns, rows_valid_patterns)
    map(eliminate_patterns, cols_valid_patterns, zip(*result))
    result = zip(*map(generate_knowns, cols_valid_patterns))
    unknowns.append(count_unknowns(result))


# Display the results:

# In[12]:

for i, u in enumerate(unknowns):
    print 'pass %s: %s unknowns' % (i, u)
print_grid(result)


# In[ ]:



