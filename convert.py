import re
import sys

def convert_killer_sudoku(input_file, output_file):
    cages = []
    max_coordinate = 0

    # Process the input file
    with open(input_file, 'r') as infile:
        for line in infile:
            line = line.strip()
            if not line:
                continue

            # Split the total from the cells
            total, cells = line.split('=')

            # Handle cell formats and ignore results
            processed_cells = []
            for cell in cells.split('+'):
                clean_coords = cell.replace(')','').replace('(', '').replace(' ','').split(',')[0:2]
                if clean_coords:
                    # Remove parentheses if they exist
                    x, y = map(int, clean_coords)
                    max_coordinate = max(max_coordinate, x, y)
                    processed_cells.append(f"{x},{y}")

            cages.append((total, processed_cells))

    # Determine board size and number of cages
    board_size = max_coordinate + 1  # Assuming zero-based indexing
    num_cages = len(cages)

    # Write the output file
    with open(output_file, 'w') as outfile:
        # Write metadata
        outfile.write(f"{board_size} {num_cages}\n")

        # Write each cage
        for total, cells in cages:
            formatted_line = f"{total};" + ';'.join(cells) + "\n"
            outfile.write(formatted_line)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python convert_killer_sudoku.py <input_file> <output_file>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    convert_killer_sudoku(input_file, output_file)
