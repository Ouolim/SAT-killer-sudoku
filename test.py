import random
import math

def is_valid(board, row, col, num, n):
    sqrt_n = int(math.sqrt(n))
    # Check if the number is in the current row or column
    for i in range(n):
        if board[row][i] == num or board[i][col] == num:
            return False

    # Check if the number is in the current subgrid
    start_row, start_col = row - row % sqrt_n, col - col % sqrt_n
    for i in range(start_row, start_row + sqrt_n):
        for j in range(start_col, start_col + sqrt_n):
            if board[i][j] == num:
                return False

    return True

def solve_sudoku(board, n):
    for row in range(n):
        for col in range(n):
            if board[row][col] == 0:
                for num in range(1, n + 1):
                    if is_valid(board, row, col, num, n):
                        board[row][col] = num
                        if solve_sudoku(board, n):
                            return True
                        board[row][col] = 0

                return False

    return True

def generate_sudoku(n):
    if not (math.sqrt(n).is_integer()):
        raise ValueError("n must be a perfect square (e.g., 4, 9, 16, etc.).")

    board = [[0] * n for _ in range(n)]
    numbers = list(range(1, n + 1))

    # Fill the diagonal subgrids with random numbers
    sqrt_n = int(math.sqrt(n))
    for i in range(0, n, sqrt_n):
        for row in range(i, i + sqrt_n):
            for col in range(i, i + sqrt_n):
                num = random.choice(numbers)
                while not is_valid(board, row, col, num, n):
                    num = random.choice(numbers)
                board[row][col] = num

    # Solve the partially filled board
    if not solve_sudoku(board, n):
        raise Exception("Failed to generate a valid Sudoku grid.")

    return board

# Function to print the Sudoku board
def print_sudoku(board):
    for row in board:
        print(" ".join(map(str, row)))

# Example usage
n = 9  # Change this to any perfect square size (e.g., 4, 9, 16)
sudoku = generate_sudoku(n)
print_sudoku(sudoku)

cages = 0
output = []
for x in range(0, n-1, 2):
	for y in range(0, n-1, 2):
		# cage 2x2, top left corner at x, y
		cageT = sudoku[x][y] + sudoku[x][y+1] + sudoku[x+1][y] + sudoku[x+1][y+1]
		output.append(f"{cageT};{x},{y};{x+1},{y};{x},{y+1};{x+1},{y+1}")
		cages+=1

print(f"{n} {cages}")
for x in output:
	print(x)