# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository defines a standard for tracking hitchhiking rides, providing:
- A comprehensive data schema for hitchhiking records (`STANDARD.md`)
- Python Pydantic models for validation (`python/hitchhiking_data_standard_pydantic_model.py`)
- Nostr protocol integration for sharing hitchhiking data (`nostr/`)
- TypeScript tools for fetching hitchhiking events (`nostr/fetch_hitchhiking_events/`)

## Architecture

### Core Components

**Data Standard (`STANDARD.md`)**
- Defines required, recommended, and optional fields for hitchhiking records
- Uses structured objects: `stop`, `hitchhiker`, `signal`, `occupant`, `ride`, etc.
- Follows RFC 9557 for timestamps and ISO 8601 for durations
- Individual tag definitions in `tags/` directory (e.g., `tags/stop.md`, `tags/signal.md`)

**Python Implementation (`python/`)**
- `hitchhiking_data_standard_pydantic_model.py`: Pydantic models for validation
- Uses enums for standardized values (MethodEnum, GenderEnum, ReasonEnum, etc.)
- Validates the complete hitchhiking record structure

**Nostr Integration (`nostr/`)**
- `publish_ride.py`: Publish single ride to Nostr network
- `publish_past_rides.py`: Bulk publish historical rides
- `fetch_hitchhiking_events/`: TypeScript tools for retrieving Nostr events
- Uses Nostr event kind `34242` for hitchhiking records

### Key Data Objects

The standard centers around these main objects:
- **HitchhikingRecord**: Top-level container with version, stops, hitchhikers, etc.
- **Stop**: Location and timing information (origin, destination, intermediate stops)
- **Hitchhiker**: Person information (can be anonymous for privacy)
- **Signal**: Methods used to solicit rides (thumb, sign, asking, etc.)
- **Occupant**: Vehicle occupants who picked up the hitchhiker

## Development Commands

### Python Environment Setup
```bash
cd python/
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Nostr Environment Setup
```bash
cd nostr/
cp example.env .env
# Edit .env with your configuration
python3 -m venv .venv
source .venv/bin/activate  
pip install -r requirements.txt
```

### TypeScript Environment Setup
```bash
cd nostr/fetch_hitchhiking_events/
npm install
```

### Running Examples
```bash
# Publish a single ride to Nostr
cd nostr/
python publish_ride.py

# Publish historical rides
python publish_past_rides.py

# Fetch hitchhiking events
cd fetch_hitchhiking_events/
npx tsx index.ts
```

## File Structure

```
├── STANDARD.md              # Main data standard specification
├── tags/                    # Individual object definitions
│   ├── stop.md             # Stop object definition
│   ├── signal.md           # Signal object definition
│   └── ...                 # Other tag definitions
├── python/                  # Python validation models
│   └── hitchhiking_data_standard_pydantic_model.py
├── nostr/                   # Nostr protocol integration
│   ├── publish_ride.py     # Single ride publisher
│   ├── publish_past_rides.py # Bulk ride publisher
│   └── fetch_hitchhiking_events/ # TypeScript fetching tools
└── .github/                 # Issue templates for proposals
```

## Contributing Guidelines

### Proposal Process
1. Create issue with "Proposal: xxx" title
2. Discuss implementation details in issue
3. Update `STANDARD.md` when consensus reached
4. Update Python Pydantic model in `python/hitchhiking_data_standard_pydantic_model.py`
5. Add "Approved" checkbox to new tag definition files
6. Close proposal issue with "accepted" comment

### Data Standard Rules
- Required fields must always be present and non-null
- Optional fields should be omitted (not null) when no data available
- Use RFC 9557 format for timestamps with timezone information
- Use ISO 8601 duration format (e.g., "PT30M" for 30 minutes)
- Location coordinates use WGS84 decimal degrees
- Anonymous hitchhikers use `{"nickname": "Anonymous"}` for privacy

### Nostr Integration
- Event kind: `34242`
- Use `d` tag with UUID for ride identification
- Use cascading `g` tags with geohash for location filtering
- Content field contains JSON following the data standard
- Trusted sources are tracked in `nostr/README.md`

## Dependencies

**Python**: `pydantic==2.11.7` (core validation)
**Nostr Python**: `pynostr`, `geohash2`, `pandas`, `requests`
**TypeScript**: `nostr-fetch`, `ws`, `typescript`