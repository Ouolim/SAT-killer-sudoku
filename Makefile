# Define variables
PYTHON_CONVERT_SCRIPT = convert.py
INPUT_FOLDER = instances/data-imported/2
OUTPUT_FOLDER = instances/data-imported-converted/2

# Find all input files recursively
INPUT_FILES = $(shell find $(INPUT_FOLDER) -type f -name '*.killer')
INPUT_FILES_ANS = $(shell find $(INPUT_FOLDER) -type f -name '*.ans')

# Derive output file paths by replacing input folder with output folder
OUTPUT_FILES = $(patsubst $(INPUT_FOLDER)/%, $(OUTPUT_FOLDER)/%, $(INPUT_FILES))
OUTPUT_FILES_ANS = $(patsubst $(INPUT_FOLDER)/%, $(OUTPUT_FOLDER)/%, $(INPUT_FILES_ANS))

all: $(OUTPUT_FILES) $(OUTPUT_FILES_ANS)

# Rule to process each file one by one
$(OUTPUT_FOLDER)/%.killer: $(INPUT_FOLDER)/%.killer $(PYTHON_CONVERT_SCRIPT)
	@mkdir -p $(dir $@)  # Ensure output folder exists
	@echo "Processing $< to $@"
	@python3 $(PYTHON_CONVERT_SCRIPT) $< $@

$(OUTPUT_FOLDER)/%.ans: $(INPUT_FOLDER)/%.ans $(PYTHON_CONVERT_SCRIPT)
	cp $< $@


ROOT_DIR := instances/data-imported-converted
PYTHON_SCRIPT := killer-sudoku.py

test-imported:
	@find $(ROOT_DIR) -type f -name '*.killer' | while read killer_file; do \
		ans_file=$${killer_file%.killer}.ans; \
		echo $$ans_file;\
		output=$$(mktemp); \
		ans_trimmed=$$(mktemp); \
		if [ -f $$ans_file ]; then \
			python $(PYTHON_SCRIPT) -i $$killer_file | tail -n 9 >> $$output; \
			head -n 9 $$ans_file >> $$ans_trimmed; \
			if diff -q -Z $$output $$ans_trimmed; then \
				echo "$$killer_file: PASS"; \
			else \
				echo "$$killer_file: FAIL $$output $$ans_trimmed"; \
				echo "Actual";\
					cat $$output; \
				echo "Expected:";\
					cat $$ans_trimmed; \
			fi; \
			rm $$output; \
			rm $$ans_trimmed; \
		else \
			echo "Answer file $$ans_file missing for $$killer_file"; \
		fi \
	done
# Clean target to remove processed files
clean:
	@echo "Cleaning output folder..."
	@rm -rf $(OUTPUT_FOLDER)
	@echo "Done."