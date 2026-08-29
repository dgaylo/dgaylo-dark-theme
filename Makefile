SRC_DIR ?= $(CURDIR)/src
BUILD_DIR ?= $(CURDIR)/build
TOOLS_DIR ?= $(CURDIR)/tools

ADD_ON_ID ?= dark-theme@dgaylo.com

SRC_FILES := $(shell find $(SRC_DIR) -type f)

.PHONY: package clean

package: $(BUILD_DIR)/package.xpi

# Upload to Mozilla for signing
$(BUILD_DIR)/%.xpi: $(BUILD_DIR)/%.zip
	python $(TOOLS_DIR)/upload.py $(ADD_ON_ID) $< $@

# Create a tarball of the package
$(BUILD_DIR)/%.zip: $(SRC_FILES) | $(BUILD_DIR)
	cd $(SRC_DIR) && zip -r $@ *

# create the build directory
$(BUILD_DIR):
	mkdir -p $@

clean:
	-$(RM) -r $(BUILD_DIR)