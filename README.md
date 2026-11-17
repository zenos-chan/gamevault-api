# Commercial Game Database REST API

A scalable, production-ready Game Details REST API built with **Python 3**, **Django**, **Django REST Framework (DRF)**, **SQLite**, and styled with the **Django Unfold** modern admin interface.

Features user registration, token-based authentication, per-minute rate limiting, and multi-tier subscription readiness (Free, Pro, Enterprise).

---

## 🚀 Key Features

* **Game Details by Name or ID**: Retrieve complete game profiles by numeric ID (`/api/games/1/`), slug (`/api/games/cyber-runner-2099/`), exact/partial title, or query parameter (`/api/games/by-name/?name=Galaxy Drift`).
* **Token Authentication & User Registration**: Developers can sign up (`/api/auth/register/`), obtain access tokens, and make authorized requests with `Authorization: Token <key>`.
* **Rate Limiting (Calls per Minute)**: Dynamic throttle limiting requests per minute (defaults to 60 calls/minute for the Free tier), returning standard `HTTP 429 Too Many Requests` when exceeded.
* **Monetization & Paid Tiers Ready**: Includes an `ApiUserProfile` model with tiered allowances (`FREE`: 60/min, `PRO`: 300/min, `ENTERPRISE`: 1200/min), making it seamless to connect a payment gateway (Stripe, LemonSqueezy, etc.) in the future.
* **Clean & Modern Admin Console**: Built on Tailwind CSS with clean, SEO-friendly endpoints (`/admin/games/`, `/admin/subscribers/`, `/admin/tokens/`).
* **Cross-Platform**: Includes 1-click startup scripts for Windows (`setup_windows.bat`) and macOS (`setup_mac.sh`).

---

## 🔑 Authentication Flow

All endpoints under `/api/games/` require authentication:

```http
Authorization: Token <your_access_token>
```

### 1. Developer Sign Up
```bash
curl -X POST http://127.0.0.1:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "indie_dev",
    "email": "dev@example.com",
    "password": "strongpassword123"
  }'
```
**Response:**
```json
{
  "id": 3,
  "username": "indie_dev",
  "email": "dev@example.com",
  "token": "1ed149f0502ba731650fb1ef054aeb05f016ded0",
  "tier": "FREE",
  "rate_limit_per_minute": 60
}
```

### 2. Login & Token Retrieval
```bash
curl -X POST http://127.0.0.1:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "indie_dev", "password": "strongpassword123"}'
```

### 3. Check Account Status & Rate Limits
```bash
curl -s http://127.0.0.1:8000/api/auth/me/ \
  -H "Authorization: Token <your_token>"
```

---

## 🎮 Game API Endpoints

### 1. Retrieve Game by ID
```bash
curl -s http://127.0.0.1:8000/api/games/1/ \
  -H "Authorization: Token <your_token>"
```

### 2. Retrieve Game by Slug or Title
```bash
curl -s http://127.0.0.1:8000/api/games/cyber-runner-2099/ \
  -H "Authorization: Token <your_token>"
```

### 3. Retrieve Game by Name Query
```bash
curl -s "http://127.0.0.1:8000/api/games/by-name/?name=Galaxy%20Drift" \
  -H "Authorization: Token <your_token>"
```

### 4. Search and Filter Catalog
```bash
# Filter by name, genre, developer, or platform:
curl -s "http://127.0.0.1:8000/api/games/?name=runner&genre=ACTION&platform=PC" \
  -H "Authorization: Token <your_token>"
```

**Example Game Response:**
```json
{
  "id": 1,
  "title": "Cyber Runner 2099",
  "slug": "cyber-runner-2099",
  "genre": "ACTION",
  "description": "A high-octane cyberpunk endless runner set in neon-drenched megacities with synthwave soundtrack.",
  "developer": "Neon Bytes Studio",
  "publisher": "Cybernetic Arts",
  "release_date": "2025-04-15",
  "platforms": ["PC", "PlayStation 5", "Xbox Series X"],
  "rating": "4.8",
  "website": "https://cyberrunner2099.example.com",
  "metadata": {
    "engine": "Unreal Engine 5",
    "languages": ["English", "Japanese", "German"]
  },
  "is_active": true,
  "created_at": "2026-11-17T20:05:39.506498Z",
  "updated_at": "2026-11-17T20:05:39.506671Z"
}
```

---

## ⏱️ Rate Limits & Paid Tiers

| Tier | Rate Limit | Purpose |
| :--- | :--- | :--- |
| **Free Tier** | 60 requests / min | Default for all newly registered developers |
| **Pro Tier** | 300 requests / min | For standard commercial integrations |
| **Enterprise Tier** | 1200 requests / min | For high-volume game publishers |

*When an account exceeds its quota, the API returns **`429 Too Many Requests`**.*

---

## 🛠️ Modern Admin Console

Visit: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
* **Username**: `admin`
* **Password**: `admin123`

* **Clean Routes**:
  * Games Catalog: [`/admin/games/`](http://127.0.0.1:8000/admin/games/)
  * API Subscribers & Tiers: [`/admin/subscribers/`](http://127.0.0.1:8000/admin/subscribers/)
  * API Tokens: [`/admin/tokens/`](http://127.0.0.1:8000/admin/tokens/)

---

## 🧪 Running Automated Tests

```bash
python manage.py test
```
