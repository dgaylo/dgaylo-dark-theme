SRC_DIR ?= $(CURDIR)/src
BUILD_DIR ?= $(CURDIR)/build
TOOLS_DIR ?= $(CURDIR)/tools

# Get version number from manifest
VERSION := $(shell $(TOOLS_DIR)/getVersion.py $(SRC_DIR)/manifest.json)

.PHONY: package upload

package: $(BUILD_DIR)/package.zip

# Upload to Mozilla for signing
upload: $(BUILD_DIR)/package.zip
	@$(TOOLS_DIR)/upload.py $(JWT_ISSUER) $(JWT_SECRET) $(VERSION) $<

# Create a tarball of the package
$(BUILD_DIR)/package.zip: FORCE $(BUILD_DIR)
	cd $(SRC_DIR) && zip -FS $@ *

# create the build directory
$(BUILD_DIR):
	mkdir -p $@

clean:
	-$(RM) -r $(BUILD_DIR)

FORCE: