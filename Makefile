SRC_DIR ?= $(CURDIR)/src
BUILD_DIR ?= $(CURDIR)/build
TOOLS_DIR ?= $(CURDIR)/tools

# Get version number from manifest
VERSION := $(shell $(TOOLS_DIR)/getVersion.py $(SRC_DIR)/manifest.json)

.PHONY: package upload

package: $(BUILD_DIR)/package.tar

# Upload to Mozilla for signing
upload: $(BUILD_DIR)/package.tar
	@$(TOOLS_DIR)/upload.py $(JWT_ISSUER) $(JWT_SECRET) $(VERSION) $<

# Create a tarball of the package
$(BUILD_DIR)/package.tar: FORCE $(BUILD_DIR)
	cd $(SRC_DIR) && tar -cf $@ *

# create the build directory
$(BUILD_DIR):
	mkdir -p $@

clean:
	-$(RM) -r $(BUILD_DIR)

FORCE: