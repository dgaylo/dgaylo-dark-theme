SRC_DIR ?= $(CURDIR)/src
BUILD_DIR ?= $(CURDIR)/build
TOOLS_DIR ?= $(CURDIR)/tools

ADD_ON_ID ?= dark-theme@dgaylo.com

# Get version number from manifest
VERSION := $(shell $(TOOLS_DIR)/getVersion.py $(SRC_DIR)/manifest.json)

.PHONY: package upload

package: $(BUILD_DIR)/package.zip

# Upload to Mozilla for signing
upload: $(BUILD_DIR)/package.zip
	python $(TOOLS_DIR)/upload.py $(JWT_ISSUER) $(JWT_SECRET) $(ADD_ON_ID) $<

# Create a tarball of the package
$(BUILD_DIR)/package.zip: FORCE $(BUILD_DIR)
	cd $(SRC_DIR) && zip -FS $@ *

# create the build directory
$(BUILD_DIR):
	mkdir -p $@

clean:
	-$(RM) -r $(BUILD_DIR)

FORCE: