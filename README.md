# Overleaf To GitLab Backup CLI

Ein schlankes Python‑Werkzeug, das Overleaf‑Projekte automatisiert in GitLab‑Repositories spiegelt – per Overleaf‑Git‑API und normalem `git push`.

---

## Inhaltsverzeichnis
- [Beschreibung](#beschreibung)
- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Deinstallation](#deinstallation)
- [Schnellstart](#schnellstart)
- [Konfiguration](#konfiguration)
  - [SSH-Konfiguration](#1-ssh-konfiguration)
  - [Overleaf-Anmeldedaten](#2-overleaf-anmeldedaten)
  - [Konfigurationsdatei](#3-konfigurationsdatei)
- [Verwendung](#verwendung)
- [Beispiele](#beispiele)
- [Funktionsweise](#funktionsweise)
- [Verzeichnisstruktur](#verzeichnisstruktur)
- [Fehlerbehebung](#fehlerbehebung)
- [Automatisierung (Cron)](#automatisierung-cron)
- [Entwicklung](#entwicklung)
- [Lizenz](#lizenz)
- [Autoren & Support](#autoren--support)
- [Beitragen](#beitragen)

---

## Beschreibung

Dieses CLI‑Tool synchronisiert Overleaf‑Projekte als Backup in ein oder mehrere GitLab‑Repositories. Es klont Projekte über die Overleaf‑Git‑API und pusht anschließend in die von Ihnen definierten Ziele. Typische Einsatzfälle sind redundante Backups, Team‑Spiegel oder Archivierung.

### Merkmale
- Interaktive Konfigurationsverwaltung (`overleaf2gitlab config`)
- Mehrere GitLab‑Ziele pro Overleaf‑Projekt
- Optionale Cache‑Bereinigung
- Ausführliches Logging via `--verbose`
- Robuste Fehlerbehandlung
- Einfache, konsistente CLI

---

## Voraussetzungen

- Python 3.8+
- Git
- SSH‑Zugang zu den Ziel‑GitLab‑Instanzen
- Zugriff auf die Overleaf‑Projekte (Git‑Token)

> Hinweis: Ältere Python‑Versionen (z. B. 3.6) werden nicht mehr empfohlen.

---

## Installation

Es gibt zwei bewährte Wege:

### 1) In virtueller Umgebung (empfohlen)
```bash
# Repository klonen
git clone <repository-url>
cd urz-sb-fire-overleafgitapi

# Virtuelle Umgebung erstellen & aktivieren
python -m venv .venv
source .venv/bin/activate     # Linux/macOS
# ODER
.venv\Scripts\activate      # Windows

# Paket im Editiermodus installieren
pip install -e .
```

### 2) Benutzerlokal installieren
```bash
git clone <repository-url>
cd urz-sb-fire-overleafgitapi
pip install --user -e .
```

Nach der Installation steht der Befehl `overleaf2gitlab` systemweit zur Verfügung.

---

## Deinstallation
```bash
python -m pip uninstall overleaf2gitlab
```

---

## Schnellstart

1. **Konfiguration starten**
   ```bash
   overleaf2gitlab config
   ```
2. **Projekt‑Mapping anlegen**
   - Overleaf‑Projekt‑ID aus der URL kopieren (z. B. `662a5ab30650c57e5355029b`).
   - Ein oder mehrere GitLab‑Ziele (per SSH‑Alias) hinterlegen.
3. **Backup ausführen**
   ```bash
   # einzelnes Projekt
   overleaf2gitlab backup-single 662a5ab30650c57e5355029b

   # alle Projekte
   overleaf2gitlab backup-all
   ```

---

## Konfiguration

### 1) SSH‑Konfiguration

**SSH‑Alias anlegen** in `~/.ssh/config`:
```
Host gitlab-urz
    HostName gitlab.urz.uni-heidelberg.de
    User git
    IdentityFile ~/.ssh/id_rsa_gitlab
```

**SSH‑Key im Agent laden**:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_rsa_gitlab
ssh-add -l   # geladene Keys prüfen
```

### 2) Overleaf‑Anmeldedaten

Legen Sie eine Credentials‑Datei mit Token an:
```bash
mkdir -p ~/.gitconfig.d
cat > ~/.gitconfig.d/overleaf << 'EOF'
https://git:<OVERLEAF-TOKEN>@git.overleaf.com
EOF
chmod 600 ~/.gitconfig.d/overleaf
```

**Sicherheit**: Die Datei `~/.gitconfig.d/overleaf` darf nur für Sie lesbar sein und gehört *nicht* ins Versionskontrollsystem.

### 3) Konfigurationsdatei

Standardpfad: `~/.config/overleaf2gitlab/config.ini` (INI‑Format)

```ini
[repos]
; <Overleaf-Projekt-ID> = <SSH-ALIAS>/<Namespace>/<Repo>.git
662a5ab30650c57e5355029b = gitlab-urz/urz-sb-fire/sg-sdm/e-science-tage/urz-sb-fire-tagungsband.git
; mehrere Ziele per Komma trennen:
; 662a5ab30650c57e5355029b = gitlab-urz/user/repo.git, gitlab-urz/team/backup.git
```

- **Overleaf‑Projekt‑ID**: in der Overleaf‑URL (z. B. `https://www.overleaf.com/project/<ID>`)
- **GitLab‑Repo‑Pfad**: `ssh-alias/namespace/repository.git`
- **Mehrere Ziele**: per Komma getrennt

---

## Verwendung

Allgemeine Befehle:
```bash
# Interaktive Konfiguration
overleaf2gitlab config

# Einzelnes Projekt sichern
overleaf2gitlab backup-single <overleaf-id>

# Alle konfigurierten Projekte sichern
overleaf2gitlab backup-all

# Hilfe
overleaf2gitlab --help
```

Globale Optionen:
- `--verbose` – detaillierte Ausgaben
- `--config PATH` – alternativer Pfad zur Konfigurationsdatei (Standard: `~/.config/overleaf2gitlab/config.ini`)
- `--cache-dir PATH` – Cache‑Verzeichnis (Standard: `~/.local/share/overleaf2gitlab`)
- `--clean` – Cache nach erfolgreichem Backup löschen

---

## Beispiele

```bash
# Einzelnes Projekt im Verbose‑Modus mit eigener Konfig
overleaf2gitlab --verbose --config ./my-config.ini backup-single 689b16659d1d083b3131e989

# Alle Projekte sichern und Cache bereinigen
overleaf2gitlab --clean backup-all

# Benutzerdefiniertes Cache-Verzeichnis nutzen
overleaf2gitlab --cache-dir /tmp/overleaf-backup backup-all
```

---

## Funktionsweise

1. **Lokales Repo vorbereiten** – für jede Overleaf‑ID wird im Cache ein Git‑Repo angelegt.
2. **Remotes setzen**
   - `origin` → Overleaf (`https://git.overleaf.com/<projekt-id>`)
   - `backup0`, `backup1`, … → Ihre GitLab‑Ziele
3. **Synchronisieren**
   - Remotes aktualisieren
   - Pull von Overleaf (Branch `main` bzw. Fallback `master`)
   - Tags holen
   - Push in alle Backup‑Remotes

---

## Verzeichnisstruktur

```
~/.cache/overleaf2gitlab/          # Cache
├── overleaf_<projekt-id-1>/
├── overleaf_<projekt-id-2>/
└── ...

~/.config/overleaf2gitlab/
└── config.ini                     # Hauptkonfiguration

~/.gitconfig.d/
└── overleaf                       # Overleaf-Credentials
```

Projektstruktur (im Repository):
```
src/overleaf2gitlab/
├── __init__.py
├── main.py           # CLI-Einstiegspunkt
├── parser.py         # Argument-Parsing
├── backup/           # Backup-Funktionalität
│   ├── __init__.py
│   ├── git.py        # Git-Operationen
│   └── operations.py # Backup-Logik
└── config/           # Konfigurationsverwaltung
    ├── __init__.py
    ├── manager.py    # Interaktive Konfiguration
    ├── operations.py # Basis-Operationen
    └── validation.py # Validierung
```

---

## Fehlerbehebung

**SSH-Authentifizierung fehlgeschlagen**
- SSH‑Config und Keys prüfen
- Läuft der Agent? `ssh-add -l`

**Overleaf‑Login schlägt fehl**
- Token bzw. `~/.gitconfig.d/overleaf` prüfen
- Datei ggf. löschen und neu anlegen

**Projekt nicht gefunden**
- Overleaf‑ID korrekt?
- Haben Sie Zugriff auf das Projekt?

Tipp: `--verbose` liefert zusätzliche Hinweise.

---

## Automatisierung (Cron)

Regelmäßige Backups via Cron einrichten (Beispiel Linux, täglich 03:00):
```cron
0 3 * * * /usr/bin/overleaf2gitlab backup-all >> "$HOME/.local/share/overleaf2gitlab/cron.log" 2>&1
```

---

## Entwicklung

```bash
# einmalig
make setup
```

---

## Lizenz

*Platzhalter* – bitte Lizenz in `LICENSE` hinterlegen und hier verlinken.

---

## Autoren & Support

- **Philip Mack** – <philip.mack@urz.uni-heidelberg.de>
- **URZ‑SB‑FIRE Team** – Universität Heidelberg

---

## Beitragen

Merge Requests sind willkommen. Eröffnen Sie bitte vor größeren Änderungen ein Issue zur Abstimmung.
