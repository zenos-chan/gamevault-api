# Django Game REST API

A modular, production-ready RESTful Game Platform API built with **Python 3**, **Django**, **Django REST Framework (DRF)**, and **SQLite**.

---

## Cross-Platform Collaboration Guide

When collaborating across **macOS** and **Windows**, virtual environment files (`env/`) and local databases (`*.sqlite3`) are ignored in Git so that platform-specific binaries do not conflict.

Each developer creates their own local virtual environment and runs migrations upon cloning.

---

### 💻 Instructions for Windows Users

Your friend on Windows can set up and run the project either automatically or manually.

#### Option A: Quick Automated Setup (1-Click / 1-Command)
In Windows Command Prompt or PowerShell inside the cloned folder, simply run:
```cmd
setup_windows.bat
```
This script automatically:
1. Creates the `env` virtual environment
2. Activates it
3. Installs dependencies from `requirements.txt`
4. Applies migrations
5. Seeds initial sample data and the `admin` superuser
6. Starts the server

---

#### Option B: Manual Setup

1. **Clone the repository**:
   ```cmd
   git clone <repo-url>
   cd <repo-folder>
   ```

2. **Create the virtual environment**:
   ```cmd
   python -m venv env
   ```

3. **Activate the virtual environment**:
   * **In Command Prompt (cmd.exe)**:
     ```cmd
     env\Scripts\activate.bat
     ```
   * **In PowerShell**:
     ```powershell
     .\env\Scripts\Activate.ps1
     ```
     *(Note: If PowerShell throws an execution policy error, run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`)*
   * **In Git Bash**:
     ```bash
     source env/Scripts/activate
     ```

4. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

5. **Run migrations & seed initial data**:
   ```cmd
   python manage.py migrate
   python manage.py seed_data
   ```

6. **Start the server**:
   ```cmd
   python manage.py runserver
   ```

---

### 🍎 Instructions for macOS / Linux Users

#### Quick Automated Setup:
```bash
./setup_mac.sh
```

#### Manual Setup:
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

---

## Default Admin Credentials

* **Admin Portal**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
* **Username**: `admin`
* **Password**: `admin123`

### Clean & SEO-Friendly Admin Routes

| Section | Clean Modern URL | Legacy Redirected URL |
| :--- | :--- | :--- |
| **Games Catalog** | `/admin/games/` | `/admin/games/game/` (301 redirect) |
| **Players** | `/admin/players/` | `/admin/games/player/` (301 redirect) |
| **Leaderboards** | `/admin/leaderboards/` | `/admin/games/gamescore/` (301 redirect) |
| **Achievements** | `/admin/achievements/` | `/admin/games/achievement/` (301 redirect) |
| **Player Badges** | `/admin/badges/` | `/admin/games/playerachievement/` (301 redirect) |
| **Match Sessions** | `/admin/sessions/` | `/admin/games/gamesession/` (301 redirect) |
| **Users** | `/admin/users/` | `/admin/auth/user/` (301 redirect) |
| **Groups** | `/admin/groups/` | `/admin/auth/group/` (301 redirect) |

---

## Project Structure

```text
├── env/                       # Python virtual environment (ignored in Git)
├── config/                    # Django project configuration
│   ├── settings.py            # SQLite & DRF configuration
│   ├── urls.py                # Main routing & root API endpoint
│   ├── wsgi.py
│   └── asgi.py
├── games/                     # Games application
│   ├── models.py              # Models: Game, Player, GameScore, Achievement, Session
│   ├── serializers.py         # DRF Serializers & XP/leveling logic
│   ├── views.py               # ViewSets & custom actions
│   ├── urls.py                # API router routes
│   ├── admin.py               # Django Admin dashboard registrations
│   ├── tests.py               # Automated unit & integration tests
│   └── management/commands/
│       └── seed_data.py       # Database seeder & admin creator
├── .gitattributes             # Cross-platform line ending normalization
├── .gitignore                 # Excludes env/, *.sqlite3, cache
├── setup_windows.bat          # 1-click Windows setup script
├── setup_mac.sh               # 1-click macOS setup script
├── requirements.txt           # Dependency lockfile
├── manage.py                  # Django CLI entrypoint
└── README.md
```

---

## API Endpoints Overview

| Category | Endpoint | Methods | Description |
| :--- | :--- | :--- | :--- |
| **API Root** | `/` | `GET` | Overview of endpoints & service info |
| **Browsable API**| `/api/` | `GET` | Interactive DRF navigation |
| **Games** | `/api/games/` | `GET`, `POST` | List and create games (`?genre=ACTION`, `?active=true`) |
| **Leaderboard** | `/api/games/{id}/leaderboard/` | `GET` | Top scores for a specific game |
| **Game Badges** | `/api/games/{id}/achievements/` | `GET` | List achievements linked to a game |
| **Players** | `/api/players/` | `GET`, `POST` | Manage players with automatic XP & leveling |
| **Player Profile**| `/api/players/{id}/profile/` | `GET` | Player summary (recent scores & unlocked badges) |
| **Player Status** | `/api/players/{id}/status/` | `POST` | Toggle status (`ONLINE`, `OFFLINE`, `IN_GAME`) |
| **Scores** | `/api/scores/` | `GET`, `POST` | Submit scores (awards XP) |
| **Achievements**| `/api/player-achievements/` | `GET`, `POST` | Unlock badges for players |
| **Sessions** | `/api/sessions/` | `GET`, `POST` | Multiplayer room & match management |

---

## Running Automated Tests

```bash
python manage.py test
```
