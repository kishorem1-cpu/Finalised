# Ward Ledger — Participatory Municipal Budgeting

A modern participatory budgeting and voting platform backed by **SHA-256 cryptographic chaining**, an optional **SQLite database backend (`ward_ledger.db`)**, an interactive **Admin Data Feeder**, **Multi-Language Support (English, தமிழ், हिन्दी)**, and an integrated **Civic Grievances & Suggestion Box**.

---

## 🌟 Innovative Features Added

1. **🌐 Multi-Language Translator (English, தமிழ் Tamil, हिन्दी Hindi)**:
   - Instant language switching across all pages (`EN | தமிழ் | हिंदी`) with zero page reload.
   - Comprehensive translations covering all municipal terms, ballot cards, live results, ledger entries, and admin actions.
   - Remembers language preferences across pages and browser sessions.

2. **💡 Civic Complaints & Suggestion Box**:
   - Compact, expandable widget in the Resident Portal for residents to submit:
     - ⚠️ **Civic Complaints** (e.g. broken streetlights, waterlogging, road repairs)
     - 💡 **Civic Suggestions** (e.g. EV charging spots, park benches)
     - 🏗️ **Participatory Budget Ideas** (e.g. community rooftop solar)
   - Generates a unique tracking token (e.g. `GRV-0881`) upon submission.
   - Municipal officials can review, filter by ward, and update status (`Pending` → `Under Review` → `Resolved`) directly from the Admin Console.

3. **🔗 Dual-Mode Architecture**:
   - **Backend Mode**: Powered by Python Flask and SQLite (`ward_ledger.db`) with SHA-256 chaining.
   - **Static Web / GitHub Pages Mode**: Runs 100% client-side with SheetJS Excel parsing, localStorage persistence, and BroadcastChannel real-time sync.

---

## 📁 Project Structure

```
WardLedger/
├── index.html          # Gateway with language selector & portal choices
├── resident.html       # Resident voting interface, live results & suggestion box
├── admin.html          # Municipal admin console with feeder & grievance review
├── shared.js           # Blockchain verification, i18n dictionaries & storage sync
├── styles.css          # Responsive design with smooth animations
├── app.py              # Flask server & REST API (serves web UI and SQLite)
├── db.py               # SQLite schema (wards, voters, proposals, votes, grievances)
├── feed_data.py        # Terminal data feeder & database inspection tool
├── voters.xlsx         # Clean Excel template with sample voters
├── proposals.xlsx      # Clean Excel template with sample proposals
├── requirements.txt    # Python dependencies (Flask, pandas, openpyxl)
├── .gitignore          # Git ignore configuration
└── README.md           # Documentation & guides
```

---

## 🚀 Running the Project

### Option A: Running with SQLite Backend (Localhost)
```bash
python -m pip install -r requirements.txt
python app.py
```
Open in your browser:
- **Home**: `http://127.0.0.1:5000/`
- **Resident Portal**: `http://127.0.0.1:5000/resident.html`
- **Admin Portal**: `http://127.0.0.1:5000/admin.html`

### Option B: Free Global Deployment via GitHub Pages
1. Install Git if not yet installed:
   ```powershell
   winget install --id Git.Git -e --source winget
   ```
2. In PowerShell:
   ```powershell
   cd "C:\Users\Kishore\Downloads\WardLedger"
   git init
   git add .
   git commit -m "Ward Ledger participatory budgeting with i18n and grievances"
   git branch -M main
   git remote add origin https://github.com/<YOUR-USERNAME>/WardLedger.git
   git push -u origin main
   ```
3. In your GitHub repo: **Settings** > **Pages** > Select branch `main` and root `/` > Click **Save**.
   Your site will be live worldwide at:
   `https://<YOUR-USERNAME>.github.io/WardLedger/`

---

## 🔑 Demo Login IDs

- **Municipal Staff ID:** `MC-ADM-001`, `MC-ADM-002`, `MC-ADM-003`
- **Resident Voter IDs:**
  - Ward 1 (Anna Nagar): `TN-0119284`, `TN-0880001`
  - Ward 2 (T Nagar): `TN-0223391`, `TN-0880002`
  - Ward 3 (Adyar): `TN-0337712`, `TN-0880003`
  - Ward 4 (Mylapore): `TN-0448827`, `TN-9949`
