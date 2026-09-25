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
    {"voter_id": "TN-0119284", "name": "Priya Raman", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119285", "name": "Arjun Suresh", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119286", "name": "Kavitha Nair", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119287", "name": "Deepak Iyer", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0119288", "name": "Meena Krishnan", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0223391", "name": "Rahul Verma", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223392", "name": "Sowmya Rangan", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223393", "name": "Vignesh Kumar", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223394", "name": "Anitha Bose", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0223395", "name": "Karthik Subramaniam", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0337712", "name": "Lakshmi Venkatesh", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337713", "name": "Suresh Pillai", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337714", "name": "Divya Shankar", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337715", "name": "Naveen Raj", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0337716", "name": "Bhavani Murthy", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-0448827", "name": "Ganesh Babu", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448828", "name": "Revathi Chandran", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448829", "name": "Manoj Sekar", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448830", "name": "Swathi Ravi", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0448831", "name": "Vinoth Kannan", "ward": "Ward 4 — Mylapore"},
    {"voter_id": "TN-0880001", "name": "Kavya Sundaram", "ward": "Ward 1 — Anna Nagar"},
    {"voter_id": "TN-0880002", "name": "Rohan Mukherjee", "ward": "Ward 2 — T Nagar"},
    {"voter_id": "TN-0880003", "name": "Shalini Narayanan", "ward": "Ward 3 — Adyar"},
    {"voter_id": "TN-9949", "name": "Kaviya", "ward": "Ward 4 — Mylapore"}
]

DEFAULT_PROPOSALS = [
    {
        "id": 1,
        "ward": "Ward 1 — Anna Nagar",
        "name": "Anna Park Renovation",
        "desc": "Resurface walking paths, repair fencing and add shaded seating in the community park.",
        "budget": 1200000
    },
    {
        "id": 2,
        "ward": "Ward 1 — Anna Nagar",
        "name": "Street Light Upgrade",
        "desc": "Replace 40 sodium-vapour lamps along the ward's residential lanes with LED fixtures.",
        "budget": 850000
    },
    {
        "id": 3,
        "ward": "Ward 2 — T Nagar",
        "name": "Main Road Repair",
        "desc": "Pothole repair and resurfacing of the 2km arterial stretch through the ward market.",
        "budget": 1500000
    },
    {
        "id": 4,
        "ward": "Ward 2 — T Nagar",
        "name": "Public Toilet Block",
        "desc": "Construct a new accessible public toilet block near the bus terminus.",
        "budget": 600000
    },
    {
        "id": 5,
        "ward": "Ward 3 — Adyar",
        "name": "Solar Pathway Lighting",
        "desc": "Install 30 solar-powered LED lights along the Adyar riverfront path.",
        "budget": 950000
    },
    {
        "id": 6,
        "ward": "Ward 3 — Adyar",
        "name": "Rainwater Recharge Wells",
        "desc": "Construct 6 community rainwater percolation wells to elevate the water table.",
        "budget": 720000
    },
    {
        "id": 7,
        "ward": "Ward 4 — Mylapore",
        "name": "Heritage Walkway Restoration",
        "desc": "Repair traditional cobblestones and install visitor directionals around the temple circle.",
        "budget": 1100000
    },
    {
        "id": 8,
        "ward": "Ward 4 — Mylapore",
        "name": "Stormwater Culvert Desilting",
        "desc": "Deep desilting and reinforced grating for flood prevention in residential streets.",
        "budget": 820000
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
