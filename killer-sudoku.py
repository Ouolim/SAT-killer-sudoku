import math
import subprocess
from argparse import ArgumentParser

class Cage:
	def __init__(self, total):
		self.total = total
		self.cells = []

	def addCell(self, cellX:int, cellY:int):
		self.cells.append((cellX, cellY))

	def generatePossibleEvaluationRec(self, depth, possibleValues, t):
		if t < 0:
			return None
		if depth == 0:
			if t!=0:
				return None
			if t == 0:
				return [[]]

		ret = []
		for valueAssigned in possibleValues:
			new = possibleValues.copy()
			new.remove(valueAssigned)
			r = self.generatePossibleEvaluationRec(depth - 1, new, t-valueAssigned)
			if r is None: continue
			for each in r:
				each.append(valueAssigned)
				ret.append(each)
		return ret

	def generatePossibleEvaluation(self, i: "Instance"):
		possibleValues = [i+1 for i in range(i.n)]
		return self.generatePossibleEvaluationRec(len(self.cells), possibleValues, self.total)



class Instance:
	def __init__(self, n: int):
		assert n>0, "Error, n must be greater than 0"
		self.boxSize = math.isqrt(n)
		assert self.boxSize**2 == n, "Error, n need to have perfect square"

		self.n = n
		self.cages = []

	def addCage(self, cage: Cage):
		self.cages.append(cage)

def load_instance(input_file_name):
	# read the input instance
	# the instance is the makespan to be used, the size of the grid, and the placement of tiles in the grid
	# tile 0 is the empty space

	with open(input_file_name, "r") as file:
		N, C = map(int, file.readline().split())
		instance = Instance(N)
		for i in range(C):
			line = file.readline().strip().split(";")
			if line:
				print(line)
				c = Cage(int(line[0]))
				for cell in line[1:]:
					x0, y0 = list(map(int, cell.split(",")))
					c.addCell(x0, y0)
			instance.addCage(c)

	return instance


def var(x, y, value, instance):
	assert 0 <= value < instance.n
	assert 0 <= x < instance.n
	assert 0 <= y < instance.n

	return value + instance.n * y + instance.n**2 * x + 1

def varBack(v, i:Instance):
	assert v <= i.n**3
	v -= 1

	x = v // i.n ** 2
	y = (v - x*(i.n ** 2))//i.n
	value = (v) % i.n
	assert var(x,y,value, i) == v + 1
	return x,y,value

def encode(i:Instance):

	# given the instance, create a cnf formula, i.e. a list of lists of integers
	# also return the total number of variables used

	cnf = []
	# number of vaiables - n*n for each cell and n numbers in it
	nr_vars = i.n ** 3

	# all tiles have exactly one number
	for x in range(i.n):
		for y in range(i.n):
			# at least 1 value for each cell
			cnf.append([var(x, y, color, i) for color in range(i.n)])

			# not two values at once -> at least 1 negation for every pair
			for value in range(i.n):
				for notValue in range(value+1, i.n):
					cnf.append([-var(x, y, value, i), -var(x,y, notValue, i)])

	# We don't need to make sure that value is not present in column, row or box twice, because
	# each value must apper. Py pigeonhole principle that is already assured.

	# Every value is found at each row
	for value in range(i.n):
		for y in range(i.n):
			cnf.append([var(x, y, value, i) for x in range(i.n)])

	# Every value is found at each column
	for value in range(i.n):
		for x in range(i.n):
			cnf.append([var(x, y, value, i) for y in range(i.n)])

	# Every value is found at each box
	for boxX in range(0, i.n, i.boxSize):
		for boxY in range(0, i.n, i.boxSize):
			for value in range(i.n):
				formula = []
				for x in range(boxX, boxX + i.boxSize):
					for y in range(boxY, boxY + i.boxSize):
						formula.append(var(x, y, value, i))
				cnf.append(formula)


	# Each cage is satisfied, its sum = cage.total
	for cage in i.cages:
		possibleEvaluations = cage.generatePossibleEvaluation(i)
		# we will need len(possibleEvaluations) new variables
		# - exactly one of them must be right
		# - and each variable x <=> cells in cage have values in possibleEvaluations

		# nr_vars is the label of the last variable
		nr_vars_start = nr_vars + 1
		nr_vars_end = nr_vars_start + len(possibleEvaluations)
		nr_vars = nr_vars_end - 1

		print(f"Doing cage with {cage.cells}, t: {cage.total}")
		print(f"There are those ways: {possibleEvaluations}")
		print(f"Encoded between {nr_vars_start} and {nr_vars_end}")

		# At least one
		cnf.append([i for i in range(nr_vars_start, nr_vars_end)])
		# At most one
		for var1 in range(nr_vars_start, nr_vars_end):
			for var2 in range(var1 + 1, nr_vars_end):
				cnf.append([-var1, -var2])

		# possibleEvaluation for cells is chosen (x) <=> (cell0 has v0 A cell1 has v1 A ...)
		for diff, pE in enumerate(possibleEvaluations):
			assert len(pE) == len(cage.cells), "Error in possible evaluations generation"

			x = nr_vars_start+diff
			# pE are in values of sudoku 1...n, program works with 0....(n-1)
			pE = [p-1 for p in pE]

			# x <-> (cel0 has v0 A cell1 has v1.....)
			# x -> (cel0 has v0 A cell1 has v1.....)
			# ~ -x OR (cel0 has v0 A cell1 has v1.....)
			# ~ (-x OR cel0 has v0) A (-x OR cel1 has v1)
			for value, cell in zip(pE, cage.cells):
				print(cell, value+1)
				cnf.append([-x, var(cell[0], cell[1], value, i)])

			# (cel0 has v0 A cell1 has v1.....) -> x
			# ~ -(cel0 has v0 A cell1 has v1.....) OR x
			# ~ -(cell0 has v0) OR -(cell1 has v1) ... OR x
			cnf.append([-var(cell[0], cell[1], value, i) for value, cell in zip(pE, cage.cells)] + [x])
	return (cnf, nr_vars)

def call_solver(cnf, nr_vars, output_name, solver_name, verbosity):
	# print CNF into formula.cnf in DIMACS format
	with open(output_name, "w") as file:
		file.write("p cnf " + str(nr_vars) + " " + str(len(cnf)) + '\n')
		for clause in cnf:
			file.write(' '.join(str(lit) for lit in clause) + " 0\n")
	# call the solver and return the output
	return subprocess.run([solver_name, '-model', '-verb=' + str(verbosity), output_name],
						  stdout=subprocess.PIPE)


def print_result(result):
	for line in result.stdout.decode('utf-8').split('\n'):
		print(line)  # print the whole output of the SAT solver to stdout, so you can see the raw output for yourself

	# check the returned result
	if (result.returncode == 20):  # returncode for SAT is 10, for UNSAT is 20
		return
	print("Done")
	# parse the model from the output of the solver
	# the model starts with 'v'
	model = []
	for line in result.stdout.decode('utf-8').split('\n'):
		if line.startswith("v"):  # there might be more lines of the model, each starting with 'v'
			vars = line.split(" ")
			vars.remove("v")
			model.extend(int(v) for v in vars)
	model.remove(0)  # 0 is the end of the model, just ignore it

	print()
	print("##################################################################")
	print("###########[ Human readable result of the tile puzzle ]###########")
	print("##################################################################")
	print()

	result = [["?" for y in range(instance.n)] for x in range(instance.n)]
	for i in model[:(instance.n**3)]:
		if i>0:
			x, y, value = varBack(i, instance)
			assert result[x][y] == "?"
			result[x][y] = value + 1

	for i, cage in enumerate(instance.cages):
		print(f"CAGE {i} should have total of {cage.total}")
		v = 0
		for cell in cage.cells:
			v += result[cell[0]][cell[1]]
			print(f"cell {cell}, has value {result[cell[0]][cell[1]]}")
		print(f"TOTAL OF CAGE {i} is {v}\n")
	print("SOULUTION:")

	for l in result:
		print(l)




if __name__ == "__main__":
	parser = ArgumentParser()

	parser.add_argument(
		"-i",
		"--input",
		default="instances/own-tests/16x16",
		type=str,
		help=(
			"The instance file."
		),
	)
	parser.add_argument(
		"-o",
		"--output",
		default="formula.cnf",
		type=str,
		help=(
			"Output file for the DIMACS format (i.e. the CNF formula)."
		),
	)
	parser.add_argument(
		"-s",
		"--solver",
		default="glucose-syrup",
		type=str,
		help=(
			"The SAT solver to be used."
		),
	)
	parser.add_argument(
		"-v",
		"--verb",
		default=1,
		type=int,
		choices=range(0, 2),
		help=(
			"Verbosity of the SAT solver used."
		),
	)
	args = parser.parse_args()

	# get the input instance
	instance = load_instance(args.input)
	print("Enconding")
	# encode the problem to create CNF formula
	cnf, nr_vars = encode(instance)
	print("Encoded")

	# call the SAT solver and get the result
	result = call_solver(cnf, nr_vars, args.output, args.solver, args.verb)

	# interpret the result and print it in a human-readable format
	print_result(result)
