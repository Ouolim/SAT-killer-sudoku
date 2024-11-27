# Killer sudoku
- I made this project as homework for my university class Propositional and Predicate Logic (NAIL062) 
- run with 
- ```make test-imported``` for imported tests, see [Readme](instances/data-imported/Readme.md)
- Want to run other tests? See [Data format](#data-format)
- How to get glucose? I installed from my package manager u can clone it and copile it yourself.
- ```
  git clone https://github.com/audemard/glucose
  cd glucose
  cmake .
  make ```
- Now run killer-sudoku with ```python3 killer-sudoku.py -s PATH/TO/GLUCOSE```

# Documentation
## Problem description
Killer Sudoku is a puzzle played on a {$n\cdot n$} grid. Note that $n$ muse have an integer square root. 
The cells are filled in with numbers from {$1\dots n$}.
- each row and column must contain all numbers from the set
- there are subsquares named boxes sized {$\sqrt{n}\cdot\sqrt{n}$}, each of them is also filled with numbers {$1\dots n$}
- apart from nurmal sudoku, Killer sudoku has a set of cages. Cage is a continuous set of cells and a total. The numbers in the cells
must add up to the total. Cells in one cage cannot contain the same number more than once. Cages don't overlap and cover all cells.

## Data format
- program gets input from a file. First line contains two numbers $N C$. N is the size of grid - n. It must have an integer square root 
(4,9,16,25, etc.). C is the number of cages.
- Next $C$ lines describe cages. Lines are separated by ; to tokens. First token is the total of the cage, other tokens are comma separated
 coordinates of cells in the cage.

An example of a valid input file format is:
```
4 6
6;0,0;0,1;0,2
6;0,3;1,3
8;2,3;3,3;3,2
11;1,0;2,0;1,1
4;1,2;2;2;2;1
5;3,0;3,1
```
That problem is 4x4 and has 6 cages. First cage has total of 6 and has cells (0,0), (0,1) and (0,2).

## Encoding
First we need to encode traditional sudoku. Each call has n variables assigned to it - for each possible numer that 
can fit into that cell. 

Each cell has at least one number - simple disjunction of each variable
Each cell has at most 1 number - disjunction of negation of each pair of variables - at most one can be in there.

Than we encode lines and columns. We say that number must be in a column at least once - disjunction of all cells 
in a column/row with number x, that repeated for each number x = 1 to n, that repeated for each column/row.
We don't need to encode that each number is there at most once, because than other numbers won't fit and the formula 
can't be satisfied.

Encoding squares is the same, we just use disjunction of all cells in a square with number x, that repeated for each
number x = 1 to n, that repeated for each square.

Now for the cages. We generate all possible ways of assigning numbers to squares in a cage so the total is met.
For example, total=5 with 2 squares in a cage. The ways are:
- s1 = 1 and s2 = 4
- s1 = 2 and s2 = 3
- s1 = 3 and s2 = 2
- s1 = 4 and s2 = 1

Note that we take all use all permutations. Then we assign each of those ways a new variable, say x. We encode
equivalence of x and the cells in that cage have those exact numbers assigned to them. We split that equivalence to
two implications.

- $$x\rightarrow (c_0=v_0 \land c_1=v_1 ...) \sim\neg x \vee (c_0 =v_0 \land c_1=v_1...) \sim (\neg x\vee cel_0=v_0) \land (\neg x \vee  c_1=v_1)$$
- So we create multiple clauses with disjunction of negation of x and cells with given value
- $(c_0 = v_0 A cell1 has v1.....$) -> x$ ~ $\neg ($cel0 has v0 $\land$ cell1 has v1.....$) \lor x $~ $\neg($cell0 has v0$) \lor \neg($cell1 has v1) $\dots \lor x$
- So we create one clause with negation of each cell with given value and x

See implementation for details. Then we just say that exactly one of those ways is right, similar to the way how we 
encoded a number assigned to a square
- at least one of them -> disjunction of all
- at most one of them -> disjunction of negation of each pair.

Then we just call the solver and print it in human-readable format.

## Data sets
I imported some data set from the internet, see [Readme](instances/data-imported/Readme.md) and used [script](convert.py)
to convert them to my data format. They can be run with ``make test-imported``. Note that some of the tests are have 
ambiguous output so some of them fail.

I also made a script [test.py](test.py) that generates cage input for sudoku sized n*n (can be changed in the file). The cages
are always blocks 2x2. I used it to generate some inputs that take longer. I removed some cages in [this test](instances/own-tests/9x9-slow-missing-cages.in)
so it takes longer to compute, and it takes more than 10 sec.

|              Problem file |                                 Description | time    | number of variables | number of clauses |
|--------------------------:|--------------------------------------------:|---------|---------------------|-------------------|
| 4x4-easy.in               | handmade                                    | instant | 94                  | 347               |
| 9x9-easy.in               | generated with test.py                      | instant | 916                 | 4240              |
| 9x9-slow-missing-cages.in | generated with test.py,  removed some cages | 12 s    | 3705                | 373189            |
| 4x4 unsolvable            | handmade, same value in square              | instant |                     |                   |
| 16x16.in                  | generated with test.py                      | inf     | 75472               | 56162792          |

I found out that my solver can solve basically any 9x9 (even with no cages) and smaller in a reasonable time. 
The next step is 16x16. That did never finish on  my machine (unless trivial, for example with 1x1 cages).
