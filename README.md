# Overleaf to GitLab Backup Tool

Ein Python-Tool zur automatischen Sicherung von Overleaf-Projekten in GitLab-Repositories über die Git-API von Overleaf.

## Beschreibung

Dieses Tool ermöglicht es, Overleaf-Projekte automatisch als Backup in GitLab-Repositories zu synchronisieren. Es nutzt die Git-API von Overleaf, um Projekte als Git-Repositories zu klonen und diese dann in ein oder mehrere GitLab-Repositories zu pushen.

### Features

- 🔄 Automatische Synchronisation von Overleaf-Projekten mit GitLab
- 📁 Unterstützung für mehrere Backup-Ziele pro Projekt
- 🔧 Konfigurierbare Projekt-Mappings über INI-Datei
- 🧹 Optionale Cache-Bereinigung nach dem Backup
- 📝 Verbose-Modus für detaillierte Ausgaben
- 🔐 SSH-basierte Authentifizierung für GitLab

## Voraussetzungen

- Python 3.6+
- Git
- SSH-Zugang zu GitLab-Instanzen
- Zugang zu Overleaf-Projekten

## Installation

1. Repository klonen:
```bash
git clone <repository-url>
cd urz-sb-fire-overleafgitapi
```

2. Virtuelle Umgebung einrichten und Abhängigkeiten installieren:
```bash
make setup
```

## Konfiguration

### 1. SSH-Konfiguration

Erstellen Sie SSH-Aliase für Ihre GitLab-Instanzen in `~/.ssh/config`:

```
Host gitlab-urz
    HostName gitlab.urz.uni-heidelberg.de
    User git
    IdentityFile ~/.ssh/id_rsa_gitlab
```

### 2. Konfigurationsdatei

Erstellen Sie eine Konfigurationsdatei (Standard: `~/.config/overleaf2gitlab/config.ini`):

```ini
[repos]
# Mapping: Overleaf-Projekt-ID = GitLab-Repository-Pfad(e)
; noch angemerrt `gitlab-urz` ist ein ssh alias
689b16659d1d083b3131e989 = gitlab-urz/username/project1.git
662a5ab30650c57e5355029b = gitlab-urz/username/project2.git, gitlab-urz/backup/project2.git
```

**Wichtig:** 
- Die Overleaf-Projekt-ID finden Sie in der URL Ihres Overleaf-Projekts
- SSH-Keys müssen über `ssh-add` im SSH-Agent geladen sein
- Mehrere Backup-Ziele können durch Komma getrennt angegeben werden

### 3. Overleaf-Anmeldedaten

Das Tool nutzt Git Credential Helper. Beim ersten Zugriff werden Sie nach Ihren Overleaf-Anmeldedaten gefragt. Diese werden sicher in `~/.gitconfig.d/overleaf` gespeichert.

## Verwendung

### Einzelnes Projekt sichern

```bash
python main.py backup-single <overleaf-projekt-id>
```

Beispiel:
```bash
python main.py backup-single 689b16659d1d083b3131e989
```

### Alle konfigurierten Projekte sichern

```bash
python main.py backup-all
```

### Optionen

```bash
python main.py --help
```

Verfügbare globale Optionen:
- `--verbose`: Detaillierte Ausgaben aktivieren
- `--config PATH`: Pfad zur Konfigurationsdatei (Standard: `~/.config/overleaf2gitlab/config.ini`)
- `--cache-dir PATH`: Cache-Verzeichnis (Standard: `~/.local/share/overleaf2gitlab`)
- `--clean-cache`: Cache nach dem Backup löschen

### Beispiele

```bash
# Verbose-Modus mit benutzerdefinierter Konfiguration
python main.py --verbose --config ./my-config.ini backup-single 689b16659d1d083b3131e989

# Alle Projekte mit Cache-Bereinigung
python main.py --clean-cache backup-all

# Benutzerdefiniertes Cache-Verzeichnis
python main.py --cache-dir /tmp/overleaf-backup backup-all
```

## Funktionsweise

1. **Git-Repository-Setup**: Für jedes Overleaf-Projekt wird ein lokales Git-Repository im Cache-Verzeichnis erstellt
2. **Remote-Konfiguration**: 
   - `origin`: Overleaf Git-API (`https://git.overleaf.com/<projekt-id>`)
   - `backup0`, `backup1`, ...: Konfigurierte GitLab-Repositories
3. **Synchronisation**:
   - Aktualisierung aller Remotes
   - Pull vom Overleaf-Repository (versucht `main` und `master` Branches)
   - Fetch von Tags
   - Push zu allen Backup-Repositories

## Verzeichnisstruktur

```
~/.local/share/overleaf2gitlab/    # Cache-Verzeichnis
├── overleaf_<projekt-id-1>/       # Git-Repository für Projekt 1
├── overleaf_<projekt-id-2>/       # Git-Repository für Projekt 2
└── ...

~/.config/overleaf2gitlab/         # Konfiguration
└── config.ini                     # Haupt-Konfigurationsdatei

~/.gitconfig.d/                    # Git-Anmeldedaten
└── overleaf                       # Gespeicherte Overleaf-Credentials
```

## Fehlerbehebung

### Häufige Probleme

1. **SSH-Authentifizierung fehlgeschlagen**
   - Überprüfen Sie Ihre SSH-Konfiguration und -Keys
   - Stellen Sie sicher, dass der SSH-Agent läuft: `ssh-add -l`

2. **Overleaf-Anmeldung fehlgeschlagen**
   - Überprüfen Sie Ihre Anmeldedaten
   - Löschen Sie `~/.gitconfig.d/overleaf` für eine neue Anmeldung

3. **Projekt nicht gefunden**
   - Überprüfen Sie die Overleaf-Projekt-ID in der Konfiguration
   - Stellen Sie sicher, dass Sie Zugriff auf das Projekt haben

### Debug-Modus

Verwenden Sie `--verbose` für detaillierte Ausgaben:

```bash
python main.py --verbose backup-single <projekt-id>
```

## Entwicklung

### Projekt-Setup für Entwickler

```bash
make setup
```

### Code-Struktur

- `main.py`: Haupt-Einstiegspunkt und Koordination
- `parser.py`: Argument-Parsing und Validierung
- `config.py`: Konfigurationsdatei-Handling
- `backup.py`: Git-Operationen und Backup-Logik

## Lizenz

TODO: geh[Lizenz-Information hier einfügen]

## Autoren

- **Philip Mack** - [philip.mack@urz.uni-heidelberg.de](mailto:philip.mack@urz.uni-heidelberg.de)
- **URZ-SB-FIRE Team** - Universität Heidelberg

## Beitragen

Beiträge sind willkommen! Bitte erstellen Sie einen Merge Request für Änderungen.

## Support

Bei Fragen oder Problemen wenden Sie sich an:
- **Philip Mack**: [philip.mack@urz.uni-heidelberg.de](mailto:philip.mack@urz.uni-heidelberg.de)
- **URZ-SB-FIRE Team**: Universität Heidelberg
