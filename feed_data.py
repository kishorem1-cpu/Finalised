"""
feed_data.py - CLI & Data Feeder utility for Ward Ledger SQLite Database
Allows feeding voters, proposals, wards, and staff via CLI, CSV, or Excel files.
"""

import argparse
import csv
import sys
import os
import db

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def clean_val(val):
    if val is None:
        return ""
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    s = str(val).strip()
    return "" if s.lower() in ["nan", "none", "null"] else s


def load_file_records(filepath):
    """Loads records from CSV or Excel file."""
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' does not exist.")
        return []

    ext = os.path.splitext(filepath)[1].lower()
    records = []

    if ext in ['.xlsx', '.xls']:
        try:
            import pandas as pd
            df = pd.read_excel(filepath)
            df = df.where(pd.notnull(df), None)
            records = df.to_dict(orient='records')
        except ImportError:
            print("Error: pandas and openpyxl are required to read Excel files. Use CSV or install them.")
            return []
    else:
        # Default CSV
        with open(filepath, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            records = list(reader)

    return records


def import_voters(filepath):
    records = load_file_records(filepath)
    if not records:
        print("No voter records found to import.")
        return

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
                norm['ward'] = val
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
        if norm:
            normalized.append(norm)

    added, skipped, errors = db.add_voters_batch(normalized)
    print(f"\n--- Voter Import Summary ---")
    print(f"Total processed: {len(records)}")
    print(f"Successfully added: {added}")
    print(f"Skipped / Duplicates: {skipped}")
    if errors:
        print("\nNotices:")
        for err in errors[:10]:
            print(f"  • {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more.")


def import_proposals(filepath):
    records = load_file_records(filepath)
    if not records:
        print("No proposal records found to import.")
        return

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
                norm['ward'] = val
            elif any(k_clean == x for x in ['name', 'title', 'project', 'proposal', 'project name', 'proposal name']):
                norm['name'] = val
            elif any(k_clean == x for x in ['desc', 'description', 'details', 'detail', 'summary']):
                norm['desc'] = val
            elif any(k_clean == x for x in ['budget', 'cost', 'amount', 'estimate', 'price']):
                norm['budget'] = val
        if norm:
            normalized.append(norm)

    added, errors = db.add_proposals_batch(normalized)
    print(f"\n--- Proposal Import Summary ---")
    print(f"Total processed: {len(records)}")
    print(f"Successfully added: {added}")
    if errors:
        print("\nNotices:")
        for err in errors:
            print(f"  • {err}")


def show_stats():
    with db.get_db() as conn:
        c = conn.cursor()
        v_count = c.execute("SELECT COUNT(*) FROM voters").fetchone()[0]
        p_count = c.execute("SELECT COUNT(*) FROM proposals").fetchone()[0]
        w_count = c.execute("SELECT COUNT(*) FROM wards").fetchone()[0]
        vote_count = c.execute("SELECT COUNT(*) FROM votes").fetchone()[0]
        
        print("\n==================================")
        print("    WARD LEDGER DATABASE STATS   ")
        print("==================================")
        print(f"  Database file: {db.DB_FILE}")
        print(f"  Wards:               {w_count}")
        print(f"  Registered Voters:   {v_count}")
        print(f"  Active Proposals:    {p_count}")
        print(f"  Cast Votes:          {vote_count}")
        print("==================================")

        ok, msg = db.verify_chain_db()
        status_icon = "[OK]" if ok else "[FAIL]"
        print(f"  SHA-256 Ledger: {status_icon} {msg}\n")


def interactive_feed():
    db.init_db()
    while True:
        print("\n--- Ward Ledger: Feed Data ---")
        print("1. Add a Single Voter")
        print("2. Add a Proposal")
        print("3. Add a Ward")
        print("4. View Database Stats")
        print("5. Generate Sample CSV Templates")
        print("6. Verify Cryptographic Vote Chain")
        print("0. Exit")
        choice = input("Select an option (0-6): ").strip()

        if choice == '1':
            vid = input("Enter Voter ID (e.g. TN-0551001): ").strip().upper()
            name = input("Enter Resident Name: ").strip()
            with db.get_db() as conn:
                wards = [r[0] for r in conn.cursor().execute("SELECT name FROM wards").fetchall()]
            print("Available Wards:")
            for i, w in enumerate(wards, 1):
                print(f"  {i}. {w}")
            w_choice = input(f"Select ward number (1-{len(wards)}) or type custom ward name: ").strip()
            if w_choice.isdigit() and 1 <= int(w_choice) <= len(wards):
                ward = wards[int(w_choice) - 1]
            else:
                ward = w_choice

            added, skipped, errs = db.add_voters_batch([{"voter_id": vid, "name": name, "ward": ward}])
            if added:
                print(f"[OK] Added voter {name} ({vid}) to {ward}")
            else:
                print(f"[FAIL] Failed to add voter: {', '.join(errs)}")

        elif choice == '2':
            with db.get_db() as conn:
                wards = [r[0] for r in conn.cursor().execute("SELECT name FROM wards").fetchall()]
            print("Select Ward for Proposal:")
            for i, w in enumerate(wards, 1):
                print(f"  {i}. {w}")
            w_choice = input(f"Select ward (1-{len(wards)}): ").strip()
            if w_choice.isdigit() and 1 <= int(w_choice) <= len(wards):
                ward = wards[int(w_choice) - 1]
            else:
                ward = w_choice

            name = input("Proposal Name: ").strip()
            desc = input("Proposal Description: ").strip()
            budget = input("Estimated Budget in INR (e.g. 1000000): ").strip()

            added, errs = db.add_proposals_batch([{"ward": ward, "name": name, "desc": desc, "budget": budget}])
            if added:
                print(f"[OK] Proposal '{name}' posted successfully.")
            else:
                print(f"[FAIL] Failed to post proposal: {', '.join(errs)}")

        elif choice == '3':
            wname = input("Enter New Ward Name (e.g. Ward 5 - Velachery): ").strip()
            if wname:
                with db.get_db() as conn:
                    conn.cursor().execute("INSERT OR IGNORE INTO wards (name) VALUES (?)", (wname,))
                    conn.commit()
                print(f"[OK] Ward '{wname}' added.")

        elif choice == '4':
            show_stats()

        elif choice == '5':
            generate_sample_files()

        elif choice == '6':
            ok, msg = db.verify_chain_db()
            print(f"\nLedger Integrity: {'[OK] PASS' if ok else '[FAIL] FAIL'} - {msg}")

        elif choice == '0':
            print("Exiting.")
            break
        else:
            print("Invalid option. Please choose between 0 and 6.")


def main():
    parser = argparse.ArgumentParser(description="Ward Ledger Data Feeder & Database Tool")
    parser.add_argument("--import-voters", help="Path to CSV or Excel file to bulk-import voters")
    parser.add_argument("--import-proposals", help="Path to CSV or Excel file to bulk-import proposals")
    parser.add_argument("--generate-samples", action="store_true", help="Generate sample CSV templates")
    parser.add_argument("--stats", action="store_true", help="Show current database statistics")
    parser.add_argument("--verify-ledger", action="store_true", help="Verify the SHA-256 cryptographic chain")
    parser.add_argument("--reseed", action="store_true", help="Reseed default demo voters, admins, and proposals")
    parser.add_argument("--interactive", action="store_true", help="Run interactive CLI menu")

    args = parser.parse_args()

    db.init_db()

    if args.generate_samples:
        generate_sample_files()
    elif args.import_voters:
        import_voters(args.import_voters)
    elif args.import_proposals:
        import_proposals(args.import_proposals)
    elif args.stats:
        show_stats()
    elif args.verify_ledger:
        ok, msg = db.verify_chain_db()
        print(f"Ledger Integrity: {'✓ PASS' if ok else '✗ FAIL'} - {msg}")
    elif args.reseed:
        db.seed_defaults_if_empty()
        print("✓ Reseeded defaults if empty.")
    elif args.interactive or len(sys.argv) == 1:
        interactive_feed()


if __name__ == "__main__":
    main()
