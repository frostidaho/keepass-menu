# Take a look at ..../ende/Makefile
# https://www.digitalocean.com/community/tutorials/how-to-use-makefiles-to-automate-repetitive-tasks-on-an-ubuntu-vps

# Getting makefile path: http://stackoverflow.com/a/18137056
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
project_dir := $(dir $(mkfile_path))
pkg_name := keepass-menu
setup_py := $(join $(project_dir), setup.py)
WHEELS = $(join $(project_dir), $(wildcard dist/dynmen_scripts*.whl))

.PHONY: all
all: uninstall install-user

.PHONY: install-develop
install-develop:
	@echo "----------------------------------------"
	@echo -e "Installing keepass in development mode from\n\t" $(project_dir)
	@echo "----------------------------------------"
	pip install --user -e $(project_dir)

.PHONY: install-user
install-user: build-wheel $(WHEELS)
	@echo "----------------------------------------"
	@echo "Installing $(pkg_name) as $$USER"
	@echo -e "\twheel file: " $(word 2, $^)
	@echo "----------------------------------------"
	pip install --user --upgrade $(word 2, $^)

.PHONY: install
install: build-wheel $(WHEELS)
	@echo "----------------------------------------"
	@echo -e "Installing keepass - may need root\n\t" $(word 2, $^)
	@echo "----------------------------------------"
	pip install $(word 2, $^)

.PHONY: uninstall
uninstall:
	-yes | pip uninstall $(pkg_name)

.PHONY: build-wheel
build-wheel: clean
	@echo "----------------------------------------"
	@echo "Building wheel for $(pkg_name)"
	@echo "----------------------------------------"
	python $(setup_py) bdist_wheel

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
	@echo "----------------------------------------"
	rm -rf $(project_dir)dist
	rm -rf $(project_dir)build
	rm -rf $(project_dir)dynmen_scripts.egg-info


