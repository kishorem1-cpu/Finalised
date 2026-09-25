"""
db.py - SQLite Database Management for Ward Ledger
Handles schema creation, connections, seeding, cryptographic hash chain verification,
and the civic complaints/suggestions repository.
"""

import sqlite3
import os
import hashlib
import json
import time
import re

DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ward_ledger.db')

DEFAULT_WARDS = [
    "Ward 1 — Anna Nagar",
    "Ward 2 — T Nagar",
    "Ward 3 — Adyar",
    "Ward 4 — Mylapore"
]

DEFAULT_ADMINS = [
    {"admin_id": "MC-ADM-001", "name": "S. Kalaivani", "role": "Ward Engineer"},
    {"admin_id": "MC-ADM-002", "name": "R. Venkataraghavan", "role": "Municipal Commissioner Office"},
    {"admin_id": "MC-ADM-003", "name": "T. Preethi", "role": "Budget Officer"}
]

DEFAULT_VOTERS = [
    # Ward 1 — Anna Nagar
    {"voter_id": "TN-0119284", "name": "Priya Raman", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0880001", "name": "Kavya Sundaram", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119285", "name": "Arjun Suresh", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119286", "name": "Kavitha Nair", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119287", "name": "Deepak Iyer", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119288", "name": "Meena Krishnan", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-1234",    "name": "Raja Sekhar", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119289", "name": "Sanjay Anand", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119290", "name": "Uma Maheswari", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119291", "name": "Balaji Swaminathan", "ward": "Ward 1 — Anna Nagar"},

    # Ward 2 — T Nagar
    {"voter_id": "TN-0223391", "name": "Rahul Verma", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0880002", "name": "Rohan Mukherjee", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223392", "name": "Sowmya Rangan", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223393", "name": "Vignesh Kumar", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223394", "name": "Anitha Bose", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223395", "name": "Karthik Subramaniam", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223396", "name": "Harini Parthasarathy", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223397", "name": "Vijay Krishnan", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223398", "name": "Geetha Narayanan", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223399", "name": "Abishek Chawla", "ward": "Ward 2 — T Nagar"},

    # Ward 3 — Adyar
    {"voter_id": "TN-0337712", "name": "Lakshmi Venkatesh", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0880003", "name": "Shalini Narayanan", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337713", "name": "Suresh Pillai", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337714", "name": "Divya Shankar", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337715", "name": "Naveen Raj", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337716", "name": "Bhavani Murthy", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337717", "name": "Goutham Ramachandran", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337718", "name": "Shruti Padmanabhan", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337719", "name": "Aditya Menon", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337720", "name": "Varsha Srinivasan", "ward": "Ward 3 — Adyar"},

    # Ward 4 — Mylapore
    {"voter_id": "TN-0448827", "name": "Ganesh Babu", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-9949",    "name": "Kaviya Sundar", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-2404",    "name": "Rency Mary", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448828", "name": "Revathi Chandran", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448829", "name": "Manoj Sekar", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448830", "name": "Swathi Ravi", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448831", "name": "Vinoth Kannan", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448832", "name": "Jayashree Raghavan", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448833", "name": "Santhosh Kumar", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448834", "name": "Deepa Rangarajan", "ward": "Ward 4 — Mylapore"}
]

DEFAULT_PROPOSALS = [
    # Ward 1 — Anna Nagar
    {
        "id": 1,
        "ward": "Ward 1 — Anna Nagar",
        "name": "Anna Park Eco-Renovation & Jogging Track",
        "desc": "Resurface 1.2km walking paths with porous eco-tiles, install solar LED pathway lights, and add shaded benches.",
        "budget": 1450000
    },
    {
        "id": 2,
        "ward": "Ward 1 — Anna Nagar",
        "name": "Smart LED Streetlight Transition (Phase 2)",
        "desc": "Replace 65 legacy sodium lamps with energy-efficient smart LED luminaires along residential 2nd & 3rd Avenues.",
        "budget": 880000
    },
    {
        "id": 3,
        "ward": "Ward 1 — Anna Nagar",
        "name": "Rainwater Harvesting & Storm Drain Desilting",
        "desc": "Deep desilting of arterial stormwater conduits and installation of 8 percolation filtration chambers before monsoon.",
        "budget": 1120000
    },
    {
        "id": 4,
        "ward": "Ward 1 — Anna Nagar",
        "name": "Automated Solid Waste Compactor Station",
        "desc": "Deploy modern odor-free closed hydraulic refuse compactor on 6th Main Road for hygienic waste processing.",
        "budget": 1600000
    },

    # Ward 2 — T Nagar
    {
        "id": 5,
        "ward": "Ward 2 — T Nagar",
        "name": "Pedestrian Plaza Expansion & Pavement Upgrades",
        "desc": "Extend accessible bollard-protected tactile walkways, anti-skid paver tiles, and ornamental planters along Pondy Bazaar corridor.",
        "budget": 1850000
    },
    {
        "id": 6,
        "ward": "Ward 2 — T Nagar",
        "name": "Automated Two-Wheeler Parking Facility",
        "desc": "Construct a 40-slot automated stacked bike parking hub near Usman Road junction to eliminate sidewalk congestion.",
        "budget": 2200000
    },
    {
        "id": 7,
        "ward": "Ward 2 — T Nagar",
        "name": "Modern Public Sanitation & Hygiene Complex",
        "desc": "Construct a 24x7 accessible public toilet with touchless sensor fittings and dedicated child/elderly care stalls.",
        "budget": 750000
    },
    {
        "id": 8,
        "ward": "Ward 2 — T Nagar",
        "name": "Overhead Cable Trenching & Underground Ducting",
        "desc": "Relocate haphazard overhead optical fiber cables into underground micro-ducts along Ranganathan Street cross-lanes.",
        "budget": 1380000
    },

    # Ward 3 — Adyar
    {
        "id": 9,
        "ward": "Ward 3 — Adyar",
        "name": "Adyar Riverfront Green Corridor & Solar Lighting",
        "desc": "Install 45 standalone solar luminary poles and native avenue trees along the riverside pedestrian walkway.",
        "budget": 1250000
    },
    {
        "id": 10,
        "ward": "Ward 3 — Adyar",
        "name": "Aquifer Percolation Recharge Wells",
        "desc": "Construct 10 decentralized stormwater percolation recharge wells in low-lying residential sectors to prevent seasonal waterlogging.",
        "budget": 920000
    },
    {
        "id": 11,
        "ward": "Ward 3 — Adyar",
        "name": "Elderly Wellness Park & Outdoor Open-Air Gym",
        "desc": "Establish an outdoor rehabilitation gym with low-impact equipment, acupressure walking track, and first-aid kiosk.",
        "budget": 680000
    },
    {
        "id": 12,
        "ward": "Ward 3 — Adyar",
        "name": "Community Aerobic Composting & Biogas Unit",
        "desc": "Set up an aerobic community composting facility at Gandhi Nagar for local organic wet waste conversion.",
        "budget": 840000
    },

    # Ward 4 — Mylapore
    {
        "id": 13,
        "ward": "Ward 4 — Mylapore",
        "name": "Heritage Temple Tank Restoration & Embankment Repair",
        "desc": "Restore historic stone embankments, install aeration water fountains, and desilt peripheral catchment feeders.",
        "budget": 1900000
    },
    {
        "id": 14,
        "ward": "Ward 4 — Mylapore",
        "name": "Traffic Calming & Heritage Lane Signage",
        "desc": "Install rubberized modular speed tables, retro-reflective heritage street signage, and bollards around temple squares.",
        "budget": 550000
    },
    {
        "id": 15,
        "ward": "Ward 4 — Mylapore",
        "name": "Secondary Drainage Pipeline & Stormwater Interceptor",
        "desc": "Lay 800m high-density polyethylene pipeline to divert excess rainwater into temple tank reservoirs.",
        "budget": 1520000
    },
    {
        "id": 16,
        "ward": "Ward 4 — Mylapore",
        "name": "Solar-Powered E-Library & Digital Study Centre",
        "desc": "Modernize the municipal reading room with 15 digital learning tablets, high-speed Wi-Fi, and 5kW rooftop solar panels.",
        "budget": 1050000
    }
]


DEFAULT_GRIEVANCES = [
    {
        "id": "GRV-0881",
        "type": "suggestion",
        "voter_id": "TN-0119284",
        "name": "Priya Raman",
        "ward": "Ward 1 — Anna Nagar",
        "subject": "Add EV charging points near park entrance",
        "details": "With rising electric scooter adoption, 4 public charging docks at Anna Park would greatly benefit residents.",
        "status": "Under Review"
    },
    {
        "id": "GRV-0882",
        "type": "complaint",
        "voter_id": "TN-0223391",
        "name": "Rahul Verma",
        "ward": "Ward 2 — T Nagar",
        "subject": "Pothole on 3rd Cross Street",
        "details": "Deep crater after recent rain causing waterlogging and traffic hazards.",
        "status": "Pending"
    }
]


def normalize_ward(val):
    """Normalizes any ward string into its canonical representation."""
    if not val:
        return ""
    s = str(val).strip()
    m = re.search(r'ward\s*([0-9]+)', s, re.IGNORECASE)
    if m:
        num = m.group(1)
        for dw in DEFAULT_WARDS:
            if re.search(rf'ward\s*{num}\b', dw, re.IGNORECASE):
                return dw
    for dw in DEFAULT_WARDS:
        loc = dw.split('—')[-1].strip().lower()
        if loc and loc in s.lower():
            return dw
    return re.sub(r'[-—–]{2,}', '—', s).replace('-', '—').strip()


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(seed=True):
    """Initializes tables and seeds initial data if empty."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Wards table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS wards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # Admins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                admin_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL
            )
        ''')
        
        # Voters table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voters (
                voter_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                ward TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Proposals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS proposals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ward TEXT NOT NULL,
                name TEXT NOT NULL,
                desc TEXT NOT NULL,
                budget INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Votes ledger table (Cryptographically chained SHA-256)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                proposal_id INTEGER NOT NULL,
                ward TEXT NOT NULL,
                voter_id TEXT UNIQUE NOT NULL,
                ts INTEGER NOT NULL,
                prev_hash TEXT NOT NULL,
                hash TEXT NOT NULL,
                FOREIGN KEY(proposal_id) REFERENCES proposals(id)
            )
        ''')

        # Grievances & Suggestion Box table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS grievances (
                id TEXT PRIMARY KEY,
                type TEXT NOT NULL,
                voter_id TEXT,
                name TEXT NOT NULL,
                ward TEXT NOT NULL,
                subject TEXT NOT NULL,
                details TEXT NOT NULL,
                status TEXT DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

        if seed:
            seed_defaults_if_empty(conn)


def seed_defaults_if_empty(conn=None):
    close_conn = False
    if conn is None:
        conn = get_db()
        close_conn = True

    try:
        cursor = conn.cursor()

        # Seed wards if empty
        cursor.execute("SELECT COUNT(*) FROM wards")
        if cursor.fetchone()[0] == 0:
            for w in DEFAULT_WARDS:
                cursor.execute("INSERT OR IGNORE INTO wards (name) VALUES (?)", (w,))

        # Seed admins if empty
        cursor.execute("SELECT COUNT(*) FROM admins")
        if cursor.fetchone()[0] == 0:
            for a in DEFAULT_ADMINS:
                cursor.execute(
                    "INSERT OR IGNORE INTO admins (admin_id, name, role) VALUES (?, ?, ?)",
                    (a["admin_id"], a["name"], a["role"])
                )

        # Seed voters if empty
        cursor.execute("SELECT COUNT(*) FROM voters")
        if cursor.fetchone()[0] == 0:
            for v in DEFAULT_VOTERS:
                cursor.execute(
                    "INSERT OR IGNORE INTO voters (voter_id, name, ward) VALUES (?, ?, ?)",
                    (v["voter_id"], v["name"], normalize_ward(v["ward"]))
                )

        # Seed proposals if empty
        cursor.execute("SELECT COUNT(*) FROM proposals")
        if cursor.fetchone()[0] == 0:
            for p in DEFAULT_PROPOSALS:
                cursor.execute(
                    "INSERT OR IGNORE INTO proposals (id, ward, name, desc, budget) VALUES (?, ?, ?, ?, ?)",
                    (p["id"], normalize_ward(p["ward"]), p["name"], p["desc"], p["budget"])
                )

        # Seed grievances if empty
        cursor.execute("SELECT COUNT(*) FROM grievances")
        if cursor.fetchone()[0] == 0:
            for g in DEFAULT_GRIEVANCES:
                cursor.execute(
                    "INSERT OR IGNORE INTO grievances (id, type, voter_id, name, ward, subject, details, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (g["id"], g["type"], g["voter_id"], g["name"], normalize_ward(g["ward"]), g["subject"], g["details"], g["status"])
                )

        conn.commit()
    finally:
        if close_conn:
            conn.close()


def calculate_hash(prev_hash, entry):
    """Calculates SHA-256 matching the frontend algorithm: sha256(prevHash + JSON.stringify(entry))."""
    data = json.dumps({
        "proposalId": entry["proposalId"],
        "ward": entry["ward"],
        "voterId": entry["voterId"],
        "ts": entry["ts"]
    }, separators=(',', ':'))
    raw = prev_hash + data
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()


def cast_vote_db(proposal_id, voter_id, ward):
    """Atomically casts a vote with cryptographic SHA-256 chaining."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verify voter exists
        cursor.execute("SELECT voter_id, ward FROM voters WHERE voter_id = ?", (voter_id,))
        voter = cursor.fetchone()
        if not voter:
            return False, "Voter ID not found in electoral roll."
        
        voter_ward = normalize_ward(voter["ward"])
        input_ward = normalize_ward(ward)
        if voter_ward != input_ward:
            return False, f"Voter registered in {voter_ward}, cannot vote in {input_ward}."

        cursor.execute("SELECT id, ward FROM proposals WHERE id = ?", (proposal_id,))
        proposal = cursor.fetchone()
        if not proposal:
            return False, "Proposal not found."
        
        prop_ward = normalize_ward(proposal["ward"])
        if prop_ward != input_ward:
            return False, "Proposal is not in the voter's registered ward."

        cursor.execute("SELECT id FROM votes WHERE voter_id = ?", (voter_id,))
        if cursor.fetchone():
            return False, "Voter has already cast a vote."

        cursor.execute("SELECT hash FROM votes ORDER BY id DESC LIMIT 1")
        last_vote = cursor.fetchone()
        prev_hash = last_vote["hash"] if last_vote else "GENESIS-WARD-LEDGER"

        ts = int(time.time() * 1000)
        entry = {
            "proposalId": proposal_id,
            "ward": voter_ward,
            "voterId": voter_id,
            "ts": ts
        }
        entry_hash = calculate_hash(prev_hash, entry)

        cursor.execute('''
            INSERT INTO votes (proposal_id, ward, voter_id, ts, prev_hash, hash)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (proposal_id, voter_ward, voter_id, ts, prev_hash, entry_hash))
        
        conn.commit()
        return True, {"proposalId": proposal_id, "ward": voter_ward, "voterId": voter_id, "ts": ts, "prevHash": prev_hash, "hash": entry_hash}


def verify_chain_db():
    """Verifies the SHA-256 ledger integrity from genesis."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT proposal_id, ward, voter_id, ts, prev_hash, hash FROM votes ORDER BY id ASC")
        rows = cursor.fetchall()

        prev = "GENESIS-WARD-LEDGER"
        for r in rows:
            entry = {
                "proposalId": r["proposal_id"],
                "ward": r["ward"],
                "voterId": r["voter_id"],
                "ts": r["ts"]
            }
            computed = calculate_hash(prev, entry)
            if computed != r["hash"] or r["prev_hash"] != prev:
                return False, f"Integrity check failed at voter {r['voter_id']}"
            prev = r["hash"]

        return True, f"Chain verified ({len(rows)} votes intact)"


def add_voters_batch(voters_list):
    added = 0
    skipped = 0
    errors = []
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM wards")
        existing_wards = set(row[0] for row in cursor.fetchall())

        for idx, item in enumerate(voters_list):
            vid = str(item.get('voter_id', '')).strip().upper()
            name = str(item.get('name', '')).strip()
            raw_ward = str(item.get('ward', '')).strip()
            ward = normalize_ward(raw_ward)

            if not vid or not name or not ward:
                errors.append(f"Row {idx+1}: Missing required field (voter_id, name, or ward)")
                skipped += 1
                continue

            if ward not in existing_wards:
                cursor.execute("INSERT OR IGNORE INTO wards (name) VALUES (?)", (ward,))
                existing_wards.add(ward)

            try:
                cursor.execute(
                    "INSERT INTO voters (voter_id, name, ward) VALUES (?, ?, ?)",
                    (vid, name, ward)
                )
                added += 1
            except sqlite3.IntegrityError:
                skipped += 1
                errors.append(f"Voter {vid} already exists (skipped)")

        conn.commit()

    return added, skipped, errors


def add_proposals_batch(proposals_list):
    added = 0
    errors = []
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM wards")
        existing_wards = set(row[0] for row in cursor.fetchall())

        for idx, item in enumerate(proposals_list):
            name = str(item.get('name', '')).strip()
            desc = str(item.get('desc', '')).strip()
            raw_ward = str(item.get('ward', '')).strip()
            ward = normalize_ward(raw_ward)
            budget_raw = item.get('budget', 0)

            try:
                budget = int(str(budget_raw).replace(',', '').replace('₹', '').strip())
            except ValueError:
                errors.append(f"Row {idx+1}: Invalid budget '{budget_raw}'")
                continue

            if not name or not desc or not ward or budget <= 0:
                errors.append(f"Row {idx+1}: Missing name, description, ward, or positive budget")
                continue

            if ward not in existing_wards:
                cursor.execute("INSERT OR IGNORE INTO wards (name) VALUES (?)", (ward,))
                existing_wards.add(ward)

            cursor.execute(
                "INSERT INTO proposals (ward, name, desc, budget) VALUES (?, ?, ?, ?)",
                (ward, name, desc, budget)
            )
            added += 1

        conn.commit()

    return added, errors


def add_grievance_db(gid, gtype, voter_id, name, ward, subject, details):
    """Inserts a new civic grievance / suggestion."""
    norm_ward = normalize_ward(ward)
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO grievances (id, type, voter_id, name, ward, subject, details, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending')
        ''', (gid, gtype, voter_id, name, norm_ward, subject, details))
        conn.commit()
        cursor.execute("SELECT id, type, voter_id, name, ward, subject, details, status, created_at FROM grievances WHERE id = ?", (gid,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_grievances_db():
    """Retrieves all civic grievances & suggestions sorted by recency."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, type, voter_id, name, ward, subject, details, status, created_at FROM grievances ORDER BY created_at DESC")
        return [dict(r) for r in cursor.fetchall()]


def update_grievance_status_db(gid, new_status):
    """Updates grievance status (Pending, Under Review, Resolved)."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE grievances SET status = ? WHERE id = ?", (new_status, gid))
        conn.commit()
        return cursor.rowcount > 0


def reset_database():
    """Wipes tables and re-seeds default data."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS grievances")
        cursor.execute("DROP TABLE IF EXISTS votes")
        cursor.execute("DROP TABLE IF EXISTS proposals")
        cursor.execute("DROP TABLE IF EXISTS voters")
        cursor.execute("DROP TABLE IF EXISTS admins")
        cursor.execute("DROP TABLE IF EXISTS wards")
        conn.commit()
    init_db(seed=True)
