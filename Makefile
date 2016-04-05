# Global
TMPDIR := ./tmp
LOCAL_MIRROR = /tmp/pypi
MIRROR_REQ = ./dependencies/requirements.txt
SAMPLES = ./docs/samples
SITE_PACKAGES := $(shell python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")

# Assets-related
ASSETS_DIR = ./ui_assets_src
OUTPUT_DIR = ./librarian/static
COMPASS_CONF = $(ASSETS_DIR)/compass.rb
COFFEE_SRC = $(ASSETS_DIR)/coffee
SCSS_SRC = $(ASSETS_DIR)/scss
JS_OUT = $(OUTPUT_DIR)/js
JS_NOPRUNE = $(JS_OUT)/vendor

# FSAL-related
FSAL_CONF := $(TMPDIR)/fsal.ini

# Librarian-related
LIBRARIAN_CONF := $(TMPDIR)/librarian.ini

# PID files
COMPASS_PID = $(TMPDIR)/.compass_pid
COFFEE_PID = $(TMPDIR)/.coffee_pid
FSAL_PID = $(TMPDIR)/.fsal_pid

.PHONY: \
	stop-assets \
	restart-assets \
	recompile-assets \
	prepare \
	local-mirror \
	start \
	stop \
	restart \
	start-fsal \
	start-coffee \
	start-compass \
	stop-compass \
	stop-coffee

prepare: local-mirror $(FSAL_CONF) $(LIBRARIAN_CONF)
	pip install -e . --extra-index-url file://$(LOCAL_MIRROR)

local-mirror:
	pip install pip2pi
	pip2pi --normalize-package-names $(LOCAL_MIRROR) --no-deps \
		--no-binary :all: -r $(MIRROR_REQ)

start: start-assets start-fsal

stop: stop-assets stop-fsal

restart: stop
	# We don't use start as a dependency because we need a 5s pause
	echo "Waiting for things to settle..."
	sleep 5
	make start

start-assets: $(COMPASS_PID) $(COFFEE_PID)

stop-assets: stop-compass stop-coffee

start-fsal: $(FSAL_PID)

stop-compass: $(COMPASS_PID)
	-kill -s TERM $$(cat $<)
	-rm $<

stop-coffee: $(COFFEE_PID)
	-kill -s INT $$(cat $<)
	-rm $<

stop-fsal: $(FSAL_PID)
	-kill -s TERM $$(cat $<)
	-rm $<

restart-assets: stop-assets watch-assets

recompile-assets:
	compass compile --force -c $(COMPASS_CONF)
	find $(JS_OUT) -path $(JS_NOPRUNE) -prune -o -name "*.js" -exec rm {} +
	coffee --bare -c --output $(JS_OUT) $(COFFEE_SRC)

$(COMPASS_PID): $(TMPDIR)
	compass watch -c $(COMPASS_CONF) & echo $$! > $@

$(COFFEE_PID): $(TMPDIR)
	coffee --bare --watch --output $(JS_OUT) $(COFFEE_SRC) & echo $$! > $@

$(FSAL_PID): $(FSAL_CONF) $(TMPDIR)
	fsal-daemon --conf $(FSAL_CONF) --pid-file $@ && echo $$! > $@

$(FSAL_CONF): $(TMPDIR)
	cat $(SAMPLES)/fsal.ini | sed 's|PREFIX|$(SITE_PACKAGES)|' > $@

$(LIBRARIAN_CONF): $(TMPDIR)
	cat $(SAMPLES)/librarian.ini > $@

$(TMPDIR):
	mkdir -p $@
