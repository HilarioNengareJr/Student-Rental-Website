# Student Rental

a flask app for finding and listing property in north cyprus — lefke, güzelyurt, nicosia, girne, mağusa and i̇skele. it scrapes listings off 101evler.com and lets registered users post their own, then shows both in one feed. started out as a way for students to find accommodation, but it handles normal rentals and sales too.

## what it does

- browse everything, or filter down to rentals (`/to-rent`) or sales (`/to-buy`)
- drill into properties by feature — pool, garden, furnished, near a bus stop, that sort of thing
- search by location or price (elasticsearch when it's wired up, in-memory filtering when it isn't)
- register, log in, and post your own listings with photos
- manage your own listings — edit or delete them
- profile page + password reset
- email the owner an enquiry
- scraped blog feed on the landing page

## stack

- **flask** + jinja templates, server-rendered
- **sqlite** through sqlalchemy, schema managed with flask-migrate
- **flask-login + bcrypt** for auth
- **elasticsearch** for search, with an in-memory fallback so it still runs without a server
- **selenium + undetected-chromedriver** for the scrapers (101evler listings + blog)
- plain html/css/js on the front — jquery, glide.js, typed.js
- **gunicorn + docker** for deployment

## running it

deps are managed with [uv](https://docs.astral.sh/uv/) — it grabs python 3.11 and sets up the env for you, no manual venv.

local:

```bash
uv sync                       # creates .venv on python 3.11, installs deps
cp .env.example .env          # drop in your smtp creds etc.
uv run flask db upgrade       # build the database
uv run python run.py          # http://localhost:5001
```

(dev server runs on 5001 since macos parks airplay receiver on 5000 — override with `PORT=...`.)

a couple of env switches: `FLASK_DEBUG=true` for debug mode, `ENABLE_SCRAPER_THREADS=true` to kick off the scrapers on startup, `ELASTICSEARCH_URL` to point at a real elasticsearch instead of the fallback.

the scrapers (selenium + chrome) are an optional extra, since you don't need them just to run the site:

```bash
uv sync --extra scraper
```

docker (brings up the app and elasticsearch together):

```bash
docker compose up --build
```

tests:

```bash
uv run pytest
```

## Screenshots of app

<br/>

### Navbar
![Navbar](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/3a9a269d-f912-40a5-9691-fdcf8a303ca2)

<br/>

### Login Page
![Login Page](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/ca7b97f0-53df-40ed-aea2-5a279b1369e2)

<br/>

### Home Page
![Home Page](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/ed093f8c-9d3e-4da6-9c7a-bc9a1006f14c)

<br/>

### Hero Section
![Hero Section](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/b4138b55-77f7-4be8-be08-d47808321bfb)

<br/>

### Actions Section
![Actions Section](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/50cba6ed-bedf-41e3-9999-17559030fd82)

<br/>

### Amenities Section
![Amenities Section](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/77a86c18-c645-48ed-81b3-388c53985a23)

<br/>

### Blog Section
![Blog Section](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/388c23b0-cb9b-49c5-83da-42783e04f134)

<br/>

### Filter Section
![Filter Section](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/6647dcfe-d175-4546-b3d8-d99492931859)

<br/>

### Listings

<br/>

#### To Rent
![To Rent](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/90aeb267-f32a-49aa-a168-30f79b928ad1)

<br/>

#### On Sale
![On Sale](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/b6e763b0-afef-4c03-90df-287185b32767)

<br/>

### Post
![Post](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/08a3ea9e-08e9-49cb-9168-91e658b5eef2)

<br/>

### Expanded Post
![Expanded Post](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/b1292915-65b4-468b-8791-2a9fc29db491)

<br/>

### Featured Listings
![Featured Listings](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/c6476ba1-2090-4486-a7bb-9e0b5773b717)

<br/>

![Featured Listings](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/ceb21d04-d2d8-4cb4-a23b-e91222fc3735)

<br/>

### Footer
![Footer](https://github.com/HilarioNengareJr/Student-Rental-Website/assets/38634516/2d5fd7de-0e80-42a7-b481-fa26a3179d03)
