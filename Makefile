# Take a look at ..../ende/Makefile
# https://www.digitalocean.com/community/tutorials/how-to-use-makefiles-to-automate-repetitive-tasks-on-an-ubuntu-vps

# Git ignored and untracked files: http://stackoverflow.com/a/4855096
git_ignored_files=$(shell git ls-files . --ignored --exclude-standard --others)
# git_untracked_files=$(shell git ls-files . --exclude-standard --others)

# Getting makefile path: http://stackoverflow.com/a/18137056
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
project_dir := $(dir $(mkfile_path))

.PHONY: all
all: uninstall install_user

.PHONY: install_develop
install_develop:
	@echo "----------------------------------------"
	@echo -e "Installing keepass in development mode from\n\t" $(project_dir)
	@echo "----------------------------------------"
	pip install --user -e $(project_dir)

.PHONY: install_user
install_user:
	@echo "----------------------------------------"
	@echo -e "Installing keepass into home directory from\n\t" $(project_dir)
	@echo "----------------------------------------"
	pip install --user $(project_dir)

.PHONY: install
install:
	@echo "----------------------------------------"
	@echo -e "Installing keepass - may need root\n\t" $(project_dir)
	@echo "----------------------------------------"
	pip install $(project_dir)

.PHONY: uninstall
uninstall:
	-pip uninstall keepass-menu

# .PHONY: tests
# tests:
# 	@echo "----------------------------------------"
# 	@echo "Running tests for python3"
# 	@echo "----------------------------------------"
# 	python "$(project_dir)tests/test_keepass_db.py"
# 	python "$(project_dir)tests/test_keyring.py"
# 	python "$(project_dir)tests/test_keyring2.py"
# 	python "$(project_dir)tests/test_rofi.py"

.PHONY: tests
tests:
	@echo "----------------------------------------"
	@echo "Running tests for python3"
	@echo "----------------------------------------"
	py.test "$(project_dir)tests/"

.PHONY: clean
clean:
	@echo "----------------------------------------"
	@echo "Cleaning up"
	@echo -e "\tRemoving files that are ignored by git"
	@echo "----------------------------------------"
	@rm $(git_ignored_files)

