name = pybindfs
build-time != date -u +"%F_%H-%M-%S"
install-name=$(name)-$(build-time)
install_dir = install/$(install-name)

all: run

run:
	python3 src/$(name)/$(name).py

run-installed:
	python3 $(install_dir)/$(name)/$(name).py

clean:
	-rm -Rf src/$(name)/__pycache__
	-rm -Rf install/*

.ONESHELL:
install: clean
	mkdir -p $(install_dir)
	cp etc/$(name).desktop $(install_dir)
	cp etc/*.png $(install_dir)
	cp etc/$(name).toml $(install_dir)
	cp etc/install.sh  $(install_dir)
	cp -R src/$(name)  $(install_dir)
	echo "build_time='$(build-time)'" >$(install_dir)/$(name)/version.py
	echo "hash='$$(git rev-parse HEAD)'" >>$(install_dir)/$(name)/version.py
	cd install
	zip -r  $(install-name).zip $(install-name)


.PHONY: all clean install run-installed
