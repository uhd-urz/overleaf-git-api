.PHONY: setup 
# build run clean distclean install

VENV = .venv
PYTHON = $(VENV)/bin/python
PIP = $(VENV)/bin/pip
PYINSTALLER = $(VENV)/bin/pyinstaller
SCRIPT = main.py
NAME = Overleaf2GitlabAPI
BIN_DIR = $(HOME)/.local/bin

setup:
	@test -d $(VENV) || python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	@test -f requirements.txt && $(PIP) install -r requirements.txt || echo "Keine requirements.txt gefunden."
	$(PIP) install pyinstaller

#build: setup
#	$(PYINSTALLER) --onefile --name=$(NAME) $(SCRIPT)
#
#run: setup
#	$(PYTHON) $(SCRIPT) --help
#
#install: build
#	@mkdir -p $(BIN_DIR)
#	cp dist/$(NAME) $(BIN_DIR)/
#	chmod +x $(BIN_DIR)/$(NAME)
#	@echo "Installiert nach $(BIN_DIR)/$(NAME)"
#	@echo "Stelle sicher, dass '$(BIN_DIR)' in deinem PATH ist."
#
#clean:
#	rm -rf build/ dist/ __pycache__/ *.spec
#
#distclean: clean
#	rm -rf $(VENV)

