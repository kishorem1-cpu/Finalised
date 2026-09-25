"""
app.py - Flask Server & REST API for Ward Ledger
Connects the Resident and Admin portals directly to the SQLite database (ward_ledger.db).
Supports voter auth, SHA-256 voting, bulk feeding, and civic grievances/suggestions.
"""

from flask import Flask, request, jsonify, send_from_directory, Response
import os
import csv
import io
import time
import db

app = Flask(__name__, static_folder='.')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Ensure database tables and initial seed data exist
db.init_db()

# Enable CORS on all responses so frontend works both directly and from localhost dev servers
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    return response


# --- Static page routes ---
@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/download/<path:filename>')
def download_file(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if filename.endswith('.xlsx') else ('text/csv' if filename.endswith('.csv') else None)
        return send_from_directory(BASE_DIR, filename, as_attachment=True, download_name=os.path.basename(filename), mimetype=mimetype)
    return jsonify({"error": "File not found"}), 404

@app.route('/<path:filename>')
def serve_static(filename):
    filepath = os.path.join(BASE_DIR, filename)
    if os.path.exists(filepath):
        if filename.endswith(('.xlsx', '.xls', '.csv')):
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' if filename.endswith('.xlsx') else 'text/csv'
            return send_from_directory(BASE_DIR, filename, as_attachment=True, download_name=os.path.basename(filename), mimetype=mimetype)
        return send_from_directory(BASE_DIR, filename)
    return jsonify({"error": "File not found"}), 404


# --- REST API Endpoints ---

@app.route('/api/bootstrap', methods=['GET'])
def get_bootstrap():
    """Returns full initial state from SQLite database."""
    with db.get_db() as conn:
        cursor = conn.cursor()

        # Wards
        cursor.execute("SELECT name FROM wards ORDER BY id ASC")
        wards = [db.normalize_ward(r[0]) for r in cursor.fetchall()]
        unique_wards = []
        for w in wards:
            if w not in unique_wards:
                unique_wards.append(w)

        # Proposals
        cursor.execute("SELECT id, ward, name, desc, budget FROM proposals ORDER BY id ASC")
        proposals = []
        for r in cursor.fetchall():
            d = dict(r)
            d["ward"] = db.normalize_ward(d["ward"])
            proposals.append(d)

        # Vote Log
        cursor.execute("SELECT proposal_id as proposalId, ward, voter_id as voterId, ts, prev_hash as prevHash, hash FROM votes ORDER BY id ASC")
        vote_log = []
        for r in cursor.fetchall():
            d = dict(r)
            d["ward"] = db.normalize_ward(d["ward"])
            vote_log.append(d)

        # Voted voter IDs
        cursor.execute("SELECT voter_id FROM votes")
        voted_voters = [r[0] for r in cursor.fetchall()]

        # Voters roll
        cursor.execute("SELECT voter_id, name, ward FROM voters")
        voter_roll = {
            r["voter_id"]: {
                "name": r["name"],
                "ward": db.normalize_ward(r["ward"])
            }
            for r in cursor.fetchall()
        }

        # Admin roll
        cursor.execute("SELECT admin_id, name, role FROM admins")
        admin_roll = {r["admin_id"]: {"name": r["name"], "role": r["role"]} for r in cursor.fetchall()}

        # Stats
        cursor.execute("SELECT COUNT(*) FROM voters")
        total_voters = cursor.fetchone()[0]

        # Grievances & suggestions
        grievances = db.get_grievances_db()

    return jsonify({
        "wards": unique_wards,
        "proposals": proposals,
        "voteLog": vote_log,
        "votedVoters": voted_voters,
        "voterRoll": voter_roll,
        "adminRoll": admin_roll,
        "grievances": grievances,
        "stats": {
            "voters": total_voters,
            "proposals": len(proposals),
            "votes": len(vote_log),
            "wards": len(unique_wards),
            "grievances": len(grievances)
        }
    })


@app.route('/api/auth/voter', methods=['POST'])
def auth_voter():
    data = request.get_json() or {}
    voter_id = data.get('voterId', '').strip().upper()
    if not voter_id:
        return jsonify({"ok": False, "error": "Voter ID is required"}), 400

    with db.get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT voter_id, name, ward FROM voters WHERE voter_id = ?", (voter_id,))
        voter = c.fetchone()
        if not voter:
            return jsonify({"ok": False, "error": "Voter ID not found in electoral roll."}), 404

        c.execute("SELECT id FROM votes WHERE voter_id = ?", (voter_id,))
        already_voted = c.fetchone() is not None

    return jsonify({
        "ok": True,
        "voter": {
            "voterId": voter["voter_id"],
            "name": voter["name"],
            "ward": db.normalize_ward(voter["ward"])
        },
        "alreadyVoted": already_voted
    })


@app.route('/api/auth/admin', methods=['POST'])
def auth_admin():
    data = request.get_json() or {}
    admin_id = data.get('adminId', '').strip().upper()
    if not admin_id:
        return jsonify({"ok": False, "error": "Admin ID is required"}), 400

    with db.get_db() as conn:
        c = conn.cursor()
        c.execute("SELECT admin_id, name, role FROM admins WHERE admin_id = ?", (admin_id,))
        admin = c.fetchone()
        if not admin:
            return jsonify({"ok": False, "error": "Staff ID not found on municipal roll."}), 404

    return jsonify({
        "ok": True,
        "admin": {
            "adminId": admin["admin_id"],
            "name": admin["name"],
            "role": admin["role"]
        }
    })


@app.route('/api/vote', methods=['POST'])
def vote():
    data = request.get_json() or {}
    proposal_id = data.get('proposalId')
    voter_id = data.get('voterId', '').strip().upper()
    ward = db.normalize_ward(data.get('ward', '').strip())

    if not proposal_id or not voter_id or not ward:
        return jsonify({"ok": False, "error": "Missing proposalId, voterId, or ward."}), 400

    success, result = db.cast_vote_db(int(proposal_id), voter_id, ward)
    if not success:
        return jsonify({"ok": False, "error": result}), 400

    return jsonify({"ok": True, "entry": result})


@app.route('/api/verify', methods=['GET'])
def verify():
    ok, msg = db.verify_chain_db()
    with db.get_db() as conn:
        count = conn.cursor().execute("SELECT COUNT(*) FROM votes").fetchone()[0]
    return jsonify({"ok": ok, "message": msg, "totalVotes": count})


@app.route('/api/proposals', methods=['POST'])
def add_proposal_api():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    desc = data.get('desc', '').strip()
    ward = db.normalize_ward(data.get('ward', '').strip())
    budget = data.get('budget', 0)

    try:
        budget = int(str(budget).replace(',', '').replace('₹', '').strip())
    except ValueError:
        return jsonify({"ok": False, "error": "Invalid budget value."}), 400

    if not name or not desc or not ward or budget <= 0:
        return jsonify({"ok": False, "error": "All fields (name, description, ward, budget) are required."}), 400

    added, errors = db.add_proposals_batch([{"name": name, "desc": desc, "ward": ward, "budget": budget}])
    if not added:
        return jsonify({"ok": False, "error": errors[0] if errors else "Failed to add proposal."}), 400

    with db.get_db() as conn:
        p = conn.cursor().execute("SELECT id, ward, name, desc, budget FROM proposals ORDER BY id DESC LIMIT 1").fetchone()

    d = dict(p)
    d["ward"] = db.normalize_ward(d["ward"])
    return jsonify({"ok": True, "proposal": d})


@app.route('/api/voters', methods=['POST'])
def add_voter_api():
    data = request.get_json() or {}
    vid = data.get('voter_id', '').strip().upper()
    name = data.get('name', '').strip()
    ward = db.normalize_ward(data.get('ward', '').strip())

    if not vid or not name or not ward:
        return jsonify({"ok": False, "error": "voter_id, name, and ward are required."}), 400

    added, skipped, errors = db.add_voters_batch([{"voter_id": vid, "name": name, "ward": ward}])
    if not added:
        return jsonify({"ok": False, "error": errors[0] if errors else "Failed to add voter."}), 400

    return jsonify({"ok": True, "message": f"Voter {name} ({vid}) registered successfully."})


# --- Civic Grievances & Suggestion Box Endpoints ---

@app.route('/api/grievances', methods=['GET', 'POST'])
def handle_grievances():
    if request.method == 'GET':
        return jsonify({"ok": True, "grievances": db.get_grievances_db()})
    
    data = request.get_json() or {}
    gid = data.get('id') or f"GRV-{int(time.time()*1000)%100000:05d}"
    gtype = data.get('type', 'suggestion').lower()
    voter_id = data.get('voter_id', '').strip().upper() or None
    name = data.get('name', 'Ward Resident').strip()
    ward = db.normalize_ward(data.get('ward', 'Ward 1 — Anna Nagar'))
    subject = data.get('subject', '').strip()
    details = data.get('details', '').strip()

    if not subject or not details:
        return jsonify({"ok": False, "error": "Subject and details are required."}), 400

    entry = db.add_grievance_db(gid, gtype, voter_id, name, ward, subject, details)
    if not entry:
        return jsonify({"ok": False, "error": "Failed to record grievance."}), 500

    return jsonify({"ok": True, "grievance": entry})


@app.route('/api/grievances/status', methods=['POST'])
def update_grievance_status():
    data = request.get_json() or {}
    gid = data.get('id')
    status = data.get('status', 'Pending')

    if not gid:
        return jsonify({"ok": False, "error": "Grievance ID required"}), 400

    ok = db.update_grievance_status_db(gid, status)
    return jsonify({"ok": ok})


def clean_val(val):
    if val is None:
        return ""
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    s = str(val).strip()
    return "" if s.lower() in ["nan", "none", "null"] else s


@app.route('/api/feed/csv', methods=['POST'])
def feed_csv():
    """Bulk feed data via CSV/Excel upload or raw CSV text with auto-detection and ward normalization."""
    requested_type = request.form.get('type', 'voters').lower()
    file = request.files.get('file')
    raw_text = request.form.get('text', '')

    records = []

    if file:
        filename = file.filename.lower()
        try:
            if filename.endswith(('.xlsx', '.xls')):
                import pandas as pd
                file_bytes = io.BytesIO(file.read())
                df = pd.read_excel(file_bytes)
                df = df.where(pd.notnull(df), None)
                records = df.to_dict(orient='records')
            else:
                content = file.read().decode('utf-8-sig', errors='replace')
                reader = csv.DictReader(io.StringIO(content))
                records = list(reader)
        except Exception as e:
            return jsonify({"ok": False, "error": f"Failed to read file: {str(e)}"}), 400
    elif raw_text:
        try:
            reader = csv.DictReader(io.StringIO(raw_text))
            records = list(reader)
        except Exception as e:
            return jsonify({"ok": False, "error": f"Failed to parse CSV text: {str(e)}"}), 400
    else:
        return jsonify({"ok": False, "error": "No file or CSV text provided."}), 400

    if not records:
        return jsonify({"ok": False, "error": "File or text contains no data rows."}), 400

    first_keys = [str(k).strip().lower() for k in records[0].keys() if k]
    is_voters_key = any(('voter' in k or 'epic' in k or 'resident' in k or k in ['id', 'vid', 'voter_id']) for k in first_keys)
    is_proposals_key = any(('budget' in k or 'cost' in k or 'proposal' in k or 'project' in k or 'desc' in k) for k in first_keys)

    target_type = requested_type
    if is_voters_key and not is_proposals_key:
        target_type = 'voters'
    elif is_proposals_key and not is_voters_key:
        target_type = 'proposals'

    if target_type == 'voters':
        normalized = []
        for r in records:
            norm = {}
            for k, v in r.items():
                if not k:
                    continue
                k_clean = str(k).strip().lower().replace('_', ' ').replace('-', ' ')
                val = clean_val(v)
                if not val:
                    continue
                if any(k_clean == x or k_clean.startswith(x) for x in ['voter id', 'voterid', 'voter no', 'vid', 'epic', 'card no']) or k_clean == 'id':
                    norm['voter_id'] = val
                elif any(k_clean == x for x in ['name', 'voter name', 'resident name', 'resident', 'full name', 'citizen name']):
                    norm['name'] = val
                elif 'ward' in k_clean:
                    norm['ward'] = db.normalize_ward(val)

            if 'voter_id' not in norm:
                for k, v in r.items():
                    k_clean = str(k).strip().lower()
                    if 'id' in k_clean and 'ward' not in k_clean:
                        val = clean_val(v)
                        if val:
                            norm['voter_id'] = val
                            break
            if 'name' not in norm:
                for k, v in r.items():
                    k_clean = str(k).strip().lower()
                    if 'name' in k_clean and 'ward' not in k_clean and 'id' not in k_clean:
                        val = clean_val(v)
                        if val:
                            norm['name'] = val
                            break
            if 'ward' not in norm:
                for k, v in r.items():
                    k_clean = str(k).strip().lower()
                    if 'ward' in k_clean:
                        val = clean_val(v)
                        if val:
                            norm['ward'] = db.normalize_ward(val)
                            break

            if norm:
                normalized.append(norm)

        added, skipped, errors = db.add_voters_batch(normalized)
        msg = f"Processed {len(records)} voter rows: {added} new voters registered."
        if skipped:
            msg += f" ({skipped} already registered / skipped)."
        return jsonify({
            "ok": True,
            "feedType": "voters",
            "totalProcessed": len(records),
            "added": added,
            "skipped": skipped,
            "errors": errors[:5],
            "message": msg
        })

    elif target_type == 'proposals':
        normalized = []
        for r in records:
            norm = {}
            for k, v in r.items():
                if not k:
                    continue
                k_clean = str(k).strip().lower().replace('_', ' ').replace('-', ' ')
                val = clean_val(v)
                if not val:
                    continue
                if 'ward' in k_clean:
                    norm['ward'] = db.normalize_ward(val)
                elif any(k_clean == x for x in ['name', 'title', 'project', 'proposal', 'project name', 'proposal name']):
                    norm['name'] = val
                elif any(k_clean == x for x in ['desc', 'description', 'details', 'detail', 'summary']):
                    norm['desc'] = val
                elif any(k_clean == x for x in ['budget', 'cost', 'amount', 'estimate', 'price']):
                    norm['budget'] = val
            if norm:
                normalized.append(norm)

        added, errors = db.add_proposals_batch(normalized)
        msg = f"Processed {len(records)} proposal rows: {added} proposals created."
        return jsonify({
            "ok": True,
            "feedType": "proposals",
            "totalProcessed": len(records),
            "added": added,
            "errors": errors[:5],
            "message": msg
        })
    else:
        return jsonify({"ok": False, "error": f"Unknown feed type '{target_type}'"}), 400


@app.route('/api/wards', methods=['POST'])
def add_ward_api():
    data = request.get_json() or {}
    ward_name = db.normalize_ward(data.get('name', '').strip())
    if not ward_name:
        return jsonify({"ok": False, "error": "Ward name is required."}), 400

    with db.get_db() as conn:
        conn.cursor().execute("INSERT OR IGNORE INTO wards (name) VALUES (?)", (ward_name,))
        conn.commit()

    return jsonify({"ok": True, "name": ward_name})


@app.route('/api/stats', methods=['GET'])
def get_stats():
    with db.get_db() as conn:
        c = conn.cursor()
        v_count = c.execute("SELECT COUNT(*) FROM voters").fetchone()[0]
        p_count = c.execute("SELECT COUNT(*) FROM proposals").fetchone()[0]
        w_count = c.execute("SELECT COUNT(*) FROM wards").fetchone()[0]
        vote_count = c.execute("SELECT COUNT(*) FROM votes").fetchone()[0]
        g_count = c.execute("SELECT COUNT(*) FROM grievances").fetchone()[0]
        ok, msg = db.verify_chain_db()

    return jsonify({
        "voters": v_count,
        "proposals": p_count,
        "wards": w_count,
        "votes": vote_count,
        "grievances": g_count,
        "ledgerVerified": ok,
        "ledgerMessage": msg
    })


@app.route('/api/reset', methods=['POST'])
def reset_db_api():
    db.reset_database()
    return jsonify({"ok": True, "message": "Database reset to clean default seed."})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Ward Ledger SQLite Backend running on http://0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
