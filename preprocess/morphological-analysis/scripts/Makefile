INPUT_DIR :=
OUTPUT_DIR :=

TRAIN_FILE_BASENAME :=
VALID_FILE_BASENAME :=
TEST_FILE_BASENAME :=

IN_TRAIN_FILE := $(INPUT_DIR)/$(TRAIN_FILE_BASENAME)
IN_VALID_FILE := $(INPUT_DIR)/$(VALID_FILE_BASENAME)
IN_TEST_FILE := $(INPUT_DIR)/$(TEST_FILE_BASENAME)

OUT_TRAIN_FILE := $(OUTPUT_DIR)/$(TRAIN_FILE_BASENAME)
OUT_VALID_FILE := $(OUTPUT_DIR)/$(VALID_FILE_BASENAME)
OUT_TEST_FILE := $(OUTPUT_DIR)/$(TEST_FILE_BASENAME)

COLUMN_NAMES :=
MORPHOLOGICAL_ANALYZER := jumanpp
INPUT_FILE_TYPE := json
H2Z :=
MECAB_DIC_DIR :=

args :=
ifdef H2Z
	args += --h2z
endif
ifdef MECAB_DIC_DIR
	args += --mecab-dic-dir $(MECAB_DIC_DIR)
endif

all: $(OUT_TRAIN_FILE) $(OUT_VALID_FILE) $(OUT_TEST_FILE)

define run_main
	mkdir -p $(dir $(2)) && \
	python apply_morphological_analysis.py $(args) \
	--column-names $(COLUMN_NAMES) \
	--morphological-analyzer $(MORPHOLOGICAL_ANALYZER) \
	--input-file-type $(INPUT_FILE_TYPE) < $(1) > $(2)
endef

out_train_file: $(OUT_TRAIN_FILE) 
$(OUT_TRAIN_FILE): $(IN_TRAIN_FILE)
	$(call run_main,$<,$@)

out_valid_file: $(OUT_VALID_FILE)
$(OUT_VALID_FILE): $(IN_VALID_FILE)
	$(call run_main,$<,$@)

out_test_file: $(OUT_TEST_FILE)
$(OUT_TEST_FILE): $(IN_TEST_FILE)
	$(call run_main,$<,$@)
