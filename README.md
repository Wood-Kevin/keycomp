# KeyComp — Mythic+ Composition Analyzer

A web app that analyzes a World of Warcraft Mythic+ party using live Raider.io data and Claude AI to give honest, tactically specific feedback on your group's composition.

## What it does

Enter up to 5 characters (region, realm, name) and KeyComp will:

- Fetch each player's current M+ score and recent run history from Raider.io
- Send the full party data to Claude for analysis
- Return a structured breakdown: comp verdict, role/utility breakdown, score analysis, synergies, biggest risk, and a recommended starting key level and dungeon

## Stack

- **Backend:** Python / Flask
- **AI:** Anthropic Claude (`claude-sonnet-4-6`)
- **Data:** Raider.io public API
- **Frontend:** Vanilla JS + CSS

## Setup

```bash
git clone https://github.com/Wood-Kevin/keycomp.git
cd keycomp
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
flask run
```

Open http://localhost:5000.

## Docker

```bash
docker compose up
```

## API

**`POST /analyze`**

```json
{
  "characters": [
    { "region": "us", "realm": "stormrage", "name": "Thunderfury" },
    { "region": "us", "realm": "illidan",   "name": "Leeroy"      }
  ]
}
```

Returns character data from Raider.io plus a Claude-generated analysis string.

## Environment variables

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Required. Your Anthropic API key. |
| `RAIDERIO_BASE_URL` | Optional. Defaults to `https://raider.io/api/v1`. |
| `SECRET_KEY` | Optional. Flask secret key. Defaults to `dev`. |
