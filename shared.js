/* ===== Ward Ledger — shared data, i18n & logic ===== */

// Canonical wards
let WARDS = [
  "Ward 1 — Anna Nagar",
  "Ward 2 — T Nagar",
  "Ward 3 — Adyar",
  "Ward 4 — Mylapore"
];

// Robust ward normalizer: matches numbers, localities, or cleans multi-dashes
function normalizeWard(raw){
  if(!raw) return '';
  const s = String(raw).trim();
  const match = s.match(/ward\s*([0-9]+)/i);
  if(match){
    const num = match[1];
    const found = WARDS.find(w => w.match(new RegExp(`ward\\s*${num}\\b`, 'i')));
    if(found) return found;
  }
  for(const w of WARDS){
    const parts = w.split(/[-—–]/);
    const locality = (parts.length > 1 ? parts[1] : parts[0]).trim().toLowerCase();
    if(locality && s.toLowerCase().includes(locality)){
      return w;
    }
  }
  return s.replace(/[-—–]{2,}/g, '—').replace(/\s*[-—–]\s*/g, ' — ');
}

// Short display name for tags (e.g., "Ward 1")
const shortWard = w => ((w || '').split(/[-—–]/)[0] || 'Ward').trim();

/* ==========================================================================
   MULTI-LANGUAGE TRANSLATION SYSTEM (English, Tamil தமிழ், Hindi हिन्दी)
   ========================================================================== */

let currentLang = 'en';
try {
  const savedLang = localStorage.getItem('ward_lang');
  if(savedLang && ['en', 'ta', 'hi'].includes(savedLang)){
    currentLang = savedLang;
  }
} catch(e){}

const I18N = {
  en: {
    app_title: "Ward Ledger",
    tagline: "Participatory municipal budgeting",
    mode_resident: "Resident",
    mode_admin: "Admin",
    sign_out: "Sign out",
    res_login_title: "Verify your residency",
    res_login_sub: "Enter your voter ID. Your registered ward and details will be verified automatically from the electoral roll.",
    voter_id_label: "Voter ID",
    verify_enter: "Verify & enter",
    demo_id_note: "One vote per verified voter ID, locked to your registered ward.",
    sample_ids: "Sample Demo IDs",
    wards_title: "Wards",
    your_ward: "YOUR WARD",
    proposals_count: "proposals",
    proposal_single: "proposal",
    estimated_budget: "Estimated budget",
    cast_vote: "Cast vote",
    your_vote: "✓ Your vote",
    vote_cast: "Vote cast",
    outside_ward: "Outside your ward",
    no_proposals: "No proposals posted for this ward yet. Municipal officials can post proposals via the Admin portal.",
    live_results: "Live results",
    live_results_sub: "Updates in real time as votes are cast",
    turnout: "Turnout",
    of_residents: "of registered residents",
    vote_tally: "Vote tally",
    fund_allocation: "Fund allocation by vote share",
    no_votes_yet: "No votes cast yet — allocation will update live.",
    vote_ledger: "Vote ledger (SHA-256 chained cryptographic log)",
    verify_integrity: "Verify integrity",
    time_th: "Time",
    proposal_th: "Proposal",
    prev_hash_th: "Prev hash",
    entry_hash_th: "Entry hash",
    no_votes_db: "No votes recorded yet in the database.",
    admin_login_title: "Municipal staff verification",
    admin_login_sub: "Enter your staff ID. Only registered officials can feed proposals, register voters, or view results.",
    staff_id_label: "Staff ID",
    admin_login_note: "Try demo IDs: MC-ADM-001, MC-ADM-002, or MC-ADM-003. Verified against municipal roll.",
    admin_console: "Admin console",
    reg_voters: "Registered Voters",
    act_proposals: "Active Proposals",
    votes_recorded: "Votes Recorded",
    feed_data: "Feed Data",
    tab_proposal: "Proposal",
    tab_voter: "Voter",
    tab_bulk: "Bulk CSV/Excel",
    tab_ward: "Ward",
    tab_grievances: "Complaints & Suggestions",
    project_name: "Project name",
    description: "Description",
    budget_inr: "Budget (₹)",
    save_proposal: "Save Proposal",
    resident_name: "Resident Full Name",
    registered_ward: "Registered Ward",
    register_voter: "Register Voter",
    feed_target: "Feed Target",
    upload_file_lbl: "Upload CSV or Excel file (.csv, .xlsx)",
    paste_csv_lbl: "Or paste CSV text",
    upload_feed: "Upload & Feed",
    new_ward_name: "New Ward Name",
    add_ward: "Add Ward",
    active_props_table: "Active Proposals",
    registered_electoral_roll: "Registered Electoral Roll (Recent 15)",
    voters_in_roll: "voters in roll",
    no_voters_reg: "No voters registered.",
    status_th: "Status",
    pending: "Pending",
    voted: "✓ Voted",
    results_by_ward: "Results by ward",
    grievance_box_title: "Civic Complaints & Suggestions",
    grievance_box_sub: "Submit an issue, civic grievance, or participatory budget proposal idea directly to your ward office.",
    type_complaint: "⚠️ Complaint",
    type_suggestion: "💡 Suggestion",
    type_budget_idea: "🏗️ Budget Idea",
    subject_label: "Subject / Summary",
    details_label: "Detailed Description",
    submit_grievance: "Submit to Ward Office",
    your_submissions: "Recent Submissions in Your Ward",
    tracking_token: "Tracking ID",
    status_pending: "Pending",
    status_review: "Under Review",
    status_resolved: "Resolved",
    mark_review: "Mark Under Review",
    mark_resolved: "Mark Resolved",
    no_grievances_yet: "No complaints or suggestions submitted for this ward yet.",
    index_welcome: "A participatory budgeting platform for ward residents and municipal officials. Choose how you'd like to sign in.",
    index_resident_title: "I'm a resident",
    index_resident_sub: "Verify your voter ID, view your ward's proposals and cast your vote on how the budget is spent.",
    index_resident_cta: "Go to resident portal →",
    index_admin_title: "I'm a municipal official",
    index_admin_sub: "Verify your staff ID, post new ward projects with budgets, and monitor live voting results.",
    index_admin_cta: "Go to admin portal →",
    index_footnote: "Backed by a persistent SQLite database with SHA-256 cryptographic verification.",
    reset_db_btn: "Reset DB to clean seed"
  },
  ta: {
    app_title: "வார்டு லெட்ஜர்",
    tagline: "பங்கேற்பு நகராட்சி நிதி ஒதுக்கீடு",
    mode_resident: "குடியிருப்பாளர்",
    mode_admin: "நிர்வாகி",
    sign_out: "வெளியேறு",
    res_login_title: "உங்கள் குடியிருப்பை சரிபார்க்கவும்",
    res_login_sub: "உங்கள் வாக்காளர் அடையாள எண்ணை உள்ளிடவும். வாக்காளர் பட்டியலிலிருந்து உங்கள் வார்டு விவரங்கள் தானாகவே சரிபார்க்கப்படும்.",
    voter_id_label: "வாக்காளர் அடையாள எண் (Voter ID)",
    verify_enter: "சரிபார்த்து உள்நுழைக",
    demo_id_note: "சரிபார்க்கப்பட்ட ஒரு வாக்காளருக்கு ஒரு வாக்கு மட்டுமே, உங்கள் வார்டுக்குள் மட்டுமே வாக்களிக்க முடியும்.",
    sample_ids: "மாதிரி வாக்காளர் எண்கள்",
    wards_title: "வார்டுகள்",
    your_ward: "உங்கள் வார்டு",
    proposals_count: "திட்டங்கள்",
    proposal_single: "திட்டம்",
    estimated_budget: "மதிப்பிடப்பட்ட நிதி",
    cast_vote: "வாக்களியுங்கள்",
    your_vote: "✓ உங்கள் வாக்கு",
    vote_cast: "வாக்கு பதிவானது",
    outside_ward: "உங்கள் வார்டுக்கு வெளியே",
    no_proposals: "இந்த வார்டிற்கு இன்னும் திட்டங்கள் வெளியிடப்படவில்லை. நகராட்சி அலுவலர்கள் நிர்வாக தளத்தில் திட்டங்களை வெளியிடலாம்.",
    live_results: "நேரலை முடிவுகள்",
    live_results_sub: "வாக்குகள் பதிவாகும்போது உடனுக்குடன் புதுப்பிக்கப்படும்",
    turnout: "வாக்களிப்பு விகிதம்",
    of_residents: "பதிவு செய்யப்பட்ட குடிமக்களில்",
    vote_tally: "வாக்கு எண்ணிக்கை",
    fund_allocation: "வாக்கு விகிதத்தின்படி நிதி ஒதுக்கீடு",
    no_votes_yet: "வாக்குகள் இன்னும் பதிவாகவில்லை — ஒதுக்கீடு நேரலையில் புதுப்பிக்கப்படும்.",
    vote_ledger: "வாக்கு பதிவேடு (SHA-256 கிரிப்டோகிராஃபிக் பதிவு)",
    verify_integrity: "நம்பகத்தன்மையை சரிபார்",
    time_th: "நேரம்",
    proposal_th: "திட்டம்",
    prev_hash_th: "முந்தைய ஹாஷ்",
    entry_hash_th: "பதிவு ஹாஷ்",
    no_votes_db: "தரவுத்தளத்தில் இன்னும் வாக்குகள் எதுவும் பதிவாகவில்லை.",
    admin_login_title: "நகராட்சி அலுவலர் சரிபார்ப்பு",
    admin_login_sub: "உங்கள் அலுவலர் அடையாள எண்ணை உள்ளிடவும். பதிவு செய்யப்பட்ட அலுவலர்கள் மட்டுமே திட்டங்கள் மற்றும் வாக்காளர்களை உள்ளிட முடியும்.",
    staff_id_label: "அலுவலர் அடையாள எண் (Staff ID)",
    admin_login_note: "மாதிரி எண்கள்: MC-ADM-001, MC-ADM-002, அல்லது MC-ADM-003. அலுவலர் பட்டியலில் சரிபார்க்கப்படும்.",
    admin_console: "நிர்வாக கட்டுப்பாட்டு மையம்",
    reg_voters: "பதிவு செய்யப்பட்ட வாக்காளர்கள்",
    act_proposals: "செயலில் உள்ள திட்டங்கள்",
    votes_recorded: "பதிவான வாக்குகள்",
    feed_data: "தரவு உள்ளீடு",
    tab_proposal: "திட்டம்",
    tab_voter: "வாக்காளர்",
    tab_bulk: "மொத்த பதிவேற்றம்",
    tab_ward: "வார்டு",
    tab_grievances: "புகார்கள் & பரிந்துரைகள்",
    project_name: "திட்டத்தின் பெயர்",
    description: "விளக்கம்",
    budget_inr: "நிதி ஒதுக்கீடு (₹)",
    save_proposal: "திட்டத்தை சேமி",
    resident_name: "குடியிருப்பாளர் முழுப்பெயர்",
    registered_ward: "பதிவு செய்யப்பட்ட வார்டு",
    register_voter: "வாக்காளரை பதிவு செய்",
    feed_target: "உள்ளீட்டு வகை",
    upload_file_lbl: "CSV அல்லது Excel கோப்பைப் பதிவேற்றவும் (.csv, .xlsx)",
    paste_csv_lbl: "அல்லது CSV உரையை ஒட்டவும்",
    upload_feed: "பதிவேற்றி உள்ளிடுக",
    new_ward_name: "புதிய வார்டு பெயர்",
    add_ward: "வார்டைச் சேர்",
    active_props_table: "செயலில் உள்ள திட்டங்கள்",
    registered_electoral_roll: "பதிவு செய்யப்பட்ட வாக்காளர் பட்டியல் (சமீபத்திய 15)",
    voters_in_roll: "வாக்காளர்கள் பட்டியலில் உள்ளனர்",
    no_voters_reg: "வாக்காளர்கள் யாரும் பதிவு செய்யப்படவில்லை.",
    status_th: "நிலை",
    pending: "நிலுவையில்",
    voted: "✓ வாக்களித்தார்",
    results_by_ward: "வார்டு வாரியான முடிவுகள்",
    grievance_box_title: "குடிமக்கள் புகார்கள் & பரிந்துரைகள்",
    grievance_box_sub: "உங்கள் வார்டு அலுவலகத்திற்கு நகராட்சிப் பிரச்சினை, புகார் அல்லது புதிய திட்ட யோசனையை நேரடியாகச் சமர்ப்பிக்கவும்.",
    type_complaint: "⚠️ நகராட்சி புகார்",
    type_suggestion: "💡 பொது பரிந்துரை",
    type_budget_idea: "🏗️ புதிய நிதி யோசனை",
    subject_label: "தலைப்பு / சுருக்கம்",
    details_label: "முழு விவரங்கள்",
    submit_grievance: "வார்டு அலுவலகத்திற்கு சமர்ப்பி",
    your_submissions: "உங்கள் வார்டில் சமர்ப்பிக்கப்பட்ட பதிவுகள்",
    tracking_token: "கண்காணிப்பு எண்",
    status_pending: "நிலுவையில்",
    status_review: "பரிசீலனையில்",
    status_resolved: "நிறைவேறியது",
    mark_review: "பரிசீலனைக்கு மாற்று",
    mark_resolved: "நிறைவேறியதாக மாற்று",
    no_grievances_yet: "இந்த வார்டில் இன்னும் புகார்கள் அல்லது பரிந்துரைகள் எதுவும் பதிவு செய்யப்படவில்லை.",
    index_welcome: "வார்டு குடியிருப்பாளர்கள் மற்றும் நகராட்சி அலுவலர்களுக்கான பங்கேற்பு நிதி ஒதுக்கீட்டு தளம். உள்நுழைய வழியைத் தேர்ந்தெடுக்கவும்.",
    index_resident_title: "நான் ஒரு குடியிருப்பாளர்",
    index_resident_sub: "உங்கள் வாக்காளர் எண்ணைச் சரிபார்த்து, வார்டு திட்டங்களைப் பார்த்து, நிதி எங்கு செலவிடப்பட வேண்டும் என்பதற்கு வாக்களியுங்கள்.",
    index_resident_cta: "குடியிருப்பாளர் தளத்திற்குச் செல் →",
    index_admin_title: "நான் ஒரு நகராட்சி அலுவலர்",
    index_admin_sub: "உங்கள் அலுவலர் எண்ணைச் சரிபார்த்து, புதிய திட்டங்களை நிதி ஒதுக்கீட்டுடன் பதிவேற்றி, நேரலை முடிவுகளைக் கண்காணிக்கவும்.",
    index_admin_cta: "நிர்வாக தளத்திற்குச் செல் →",
    index_footnote: "SHA-256 கிரிப்டோகிராஃபிக் சரிபார்ப்புடன் பாதுகாப்பான SQLite தரவுத்தளத்தில் இயக்கப்படுகிறது.",
    reset_db_btn: "தரவுத்தளத்தை இயல்புநிலைக்கு மீட்டமை"
  },
  hi: {
    app_title: "वार्ड लेजर",
    tagline: "जनसहभागी नगरपालिका बजट प्रणाली",
    mode_resident: "नागरिक",
    mode_admin: "व्यवस्थापक",
    sign_out: "लॉग आउट",
    res_login_title: "अपने निवास का सत्यापन करें",
    res_login_sub: "अपना मतदाता पहचान पत्र (Voter ID) दर्ज करें। मतदाता सूची से आपका नाम और वार्ड स्वतः सत्यापित होगा।",
    voter_id_label: "मतदाता पहचान पत्र (Voter ID)",
    verify_enter: "सत्यापित करें और प्रवेश करें",
    demo_id_note: "सत्यापित मतदाता पहचान पत्र पर केवल एक मत, आपके पंजीकृत वार्ड तक ही सीमित।",
    sample_ids: "डेमो वोटर आईडी",
    wards_title: "वार्ड",
    your_ward: "आपका वार्ड",
    proposals_count: "प्रस्ताव",
    proposal_single: "प्रस्ताव",
    estimated_budget: "अनुमानित बजट",
    cast_vote: "मत दें",
    your_vote: "✓ आपका मत",
    vote_cast: "मत दर्ज किया गया",
    outside_ward: "आपके वार्ड से बाहर",
    no_proposals: "इस वार्ड के लिए अभी कोई प्रस्ताव पोस्ट नहीं किया गया है। नगरपालिका अधिकारी व्यवस्थापक पोर्टल के माध्यम से प्रस्ताव जोड़ सकते हैं।",
    live_results: "सजीव परिणाम",
    live_results_sub: "मतदान के साथ वास्तविक समय में अपडेट",
    turnout: "मतदान प्रतिशत",
    of_residents: "पंजीकृत नागरिकों में से",
    vote_tally: "मत गणना",
    fund_allocation: "मत हिस्सेदारी के अनुसार बजट आवंटन",
    no_votes_yet: "अभी तक कोई मत नहीं पड़ा है — आवंटन सजीव रूप से अपडेट होगा।",
    vote_ledger: "मतदान बहीखाता (SHA-256 क्रिप्टोग्राफ़िक खाता)",
    verify_integrity: "सत्यता जांचें",
    time_th: "समय",
    proposal_th: "प्रस्ताव",
    prev_hash_th: "पूर्व हैश",
    entry_hash_th: "प्रविष्टि हैश",
    no_votes_db: "डेटाबेस में अभी तक कोई मत दर्ज नहीं हुआ है।",
    admin_login_title: "नगरपालिका कर्मचारी सत्यापन",
    admin_login_sub: "अपना स्टाफ आईडी दर्ज करें। केवल पंजीकृत अधिकारी ही प्रस्ताव या मतदाता जोड़ सकते हैं।",
    staff_id_label: "कर्मचारी आईडी (Staff ID)",
    admin_login_note: "डेमो आईडी: MC-ADM-001, MC-ADM-002, या MC-ADM-003। कर्मचारी सूची से सत्यापित।",
    admin_console: "प्रशासनिक नियंत्रण केंद्र",
    reg_voters: "पंजीकृत मतदाता",
    act_proposals: "सक्रिय प्रस्ताव",
    votes_recorded: "कुल दर्ज मत",
    feed_data: "डेटा प्रविष्टि",
    tab_proposal: "प्रस्ताव",
    tab_voter: "मतदाता",
    tab_bulk: "बल्क अपलोड",
    tab_ward: "वार्ड",
    tab_grievances: "शिकायतें व सुझाव",
    project_name: "परियोजना का नाम",
    description: "विवरण",
    budget_inr: "बजट (₹)",
    save_proposal: "प्रस्ताव सुरक्षित करें",
    resident_name: "नागरिक का पूरा नाम",
    registered_ward: "पंजीकृत वार्ड",
    register_voter: "मतदाता पंजीकृत करें",
    feed_target: "प्रविष्टि लक्ष्य",
    upload_file_lbl: "CSV या Excel फ़ाइल अपलोड करें (.csv, .xlsx)",
    paste_csv_lbl: "या CSV टेक्स्ट पेस्ट करें",
    upload_feed: "अपलोड व सुरक्षित करें",
    new_ward_name: "नए वार्ड का नाम",
    add_ward: "वार्ड जोड़ें",
    active_props_table: "सक्रिय प्रस्ताव",
    registered_electoral_roll: "पंजीकृत मतदाता सूची (हाल के 15)",
    voters_in_roll: "मतदाता सूची में",
    no_voters_reg: "कोई मतदाता पंजीकृत नहीं है।",
    status_th: "स्थिति",
    pending: "लंबित",
    voted: "✓ मत दिया",
    results_by_ward: "वार्ड अनुसार परिणाम",
    grievance_box_title: "नागरिक शिकायत व सुझाव पेटी",
    grievance_box_sub: "अपने वार्ड कार्यालय को कोई समस्या, नागरिक शिकायत या नए बजट प्रस्ताव का सुझाव सीधे भेजें।",
    type_complaint: "⚠️ नागरिक शिकायत",
    type_suggestion: "💡 सार्वजनिक सुझाव",
    type_budget_idea: "🏗️ नया बजट विचार",
    subject_label: "विषय / सारांश",
    details_label: "विस्तृत विवरण",
    submit_grievance: "वार्ड कार्यालय में जमा करें",
    your_submissions: "आपके वार्ड में दर्ज प्रविष्टियां",
    tracking_token: "ट्रैकिंग आईडी",
    status_pending: "लंबित",
    status_review: "समीक्षाधीन",
    status_resolved: "हल किया गया",
    mark_review: "समीक्षा में डालें",
    mark_resolved: "हल घोषित करें",
    no_grievances_yet: "इस वार्ड के लिए अभी कोई शिकायत या सुझाव दर्ज नहीं है।",
    index_welcome: "वार्ड नागरिकों और नगरपालिका अधिकारियों के लिए एक सहभागी बजट मंच। चुनें कि आप कैसे साइन इन करना चाहते हैं।",
    index_resident_title: "मैं एक नागरिक हूँ",
    index_resident_sub: "अपने वोटर आईडी का सत्यापन करें, अपने वार्ड के प्रस्ताव देखें और बजट पर अपना मत दें।",
    index_resident_cta: "नागरिक पोर्टल पर जाएं →",
    index_admin_title: "मैं एक नगरपालिका अधिकारी हूँ",
    index_admin_sub: "अपनी स्टाफ आईडी सत्यापित करें, बजट के साथ नई परियोजनाएं जोड़ें और मतदान परिणामों की निगरानी करें।",
    index_admin_cta: "व्यवस्थापक पोर्टल पर जाएं →",
    index_footnote: "SHA-256 क्रिप्टोग्राफिक सत्यापन के साथ सुरक्षित SQLite डेटाबेस द्वारा संचालित।",
    reset_db_btn: "डेटाबेस को पुनः रीसेट करें"
  }
};

function t(key, fallback){
  const dict = I18N[currentLang] || I18N.en;
  if(dict && dict[key] !== undefined) return dict[key];
  return (I18N.en && I18N.en[key] !== undefined) ? I18N.en[key] : (fallback || key);
}

function setLanguage(lang){
  if(!['en', 'ta', 'hi'].includes(lang)) return;
  currentLang = lang;
  try { localStorage.setItem('ward_lang', lang); } catch(e){}
  
  // Update buttons across all headers
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-lang') === lang);
  });

  // Re-render whichever view is active
  if(typeof render === 'function'){
    render();
  }
}

function renderLangSelector(){
  return `
  <div class="lang-switch" role="group" aria-label="Language selector">
    <button type="button" class="lang-btn ${currentLang==='en'?'active':''}" data-lang="en" onclick="setLanguage('en')">EN</button>
    <button type="button" class="lang-btn ${currentLang==='ta'?'active':''}" data-lang="ta" onclick="setLanguage('ta')">தமிழ்</button>
    <button type="button" class="lang-btn ${currentLang==='hi'?'active':''}" data-lang="hi" onclick="setLanguage('hi')">हिंदी</button>
  </div>`;
}

/* ==========================================================================
   DEFAULT ELECTORAL ROLL & PROPOSALS
   ========================================================================== */

let VOTER_ROLL = {
  "TN-0119284": {name:"Priya Raman", ward:"Ward 1 — Anna Nagar"},
  "TN-0119285": {name:"Arjun Suresh", ward:"Ward 1 — Anna Nagar"},
  "TN-0119286": {name:"Kavitha Nair", ward:"Ward 1 — Anna Nagar"},
  "TN-0119287": {name:"Deepak Iyer", ward:"Ward 1 — Anna Nagar"},
  "TN-0119288": {name:"Meena Krishnan", ward:"Ward 1 — Anna Nagar"},
  "TN-0223391": {name:"Rahul Verma", ward:"Ward 2 — T Nagar"},
  "TN-0223392": {name:"Sowmya Rangan", ward:"Ward 2 — T Nagar"},
  "TN-0223393": {name:"Vignesh Kumar", ward:"Ward 2 — T Nagar"},
  "TN-0223394": {name:"Anitha Bose", ward:"Ward 2 — T Nagar"},
  "TN-0223395": {name:"Karthik Subramaniam", ward:"Ward 2 — T Nagar"},
  "TN-0337712": {name:"Lakshmi Venkatesh", ward:"Ward 3 — Adyar"},
  "TN-0337713": {name:"Suresh Pillai", ward:"Ward 3 — Adyar"},
  "TN-0337714": {name:"Divya Shankar", ward:"Ward 3 — Adyar"},
  "TN-0337715": {name:"Naveen Raj", ward:"Ward 3 — Adyar"},
  "TN-0337716": {name:"Bhavani Murthy", ward:"Ward 3 — Adyar"},
  "TN-0448827": {name:"Ganesh Babu", ward:"Ward 4 — Mylapore"},
  "TN-0448828": {name:"Revathi Chandran", ward:"Ward 4 — Mylapore"},
  "TN-0448829": {name:"Manoj Sekar", ward:"Ward 4 — Mylapore"},
  "TN-0448830": {name:"Swathi Ravi", ward:"Ward 4 — Mylapore"},
  "TN-0448831": {name:"Vinoth Kannan", ward:"Ward 4 — Mylapore"},
  "TN-0880001": {name:"Kavya Sundaram", ward:"Ward 1 — Anna Nagar"},
  "TN-0880002": {name:"Rohan Mukherjee", ward:"Ward 2 — T Nagar"},
  "TN-0880003": {name:"Shalini Narayanan", ward:"Ward 3 — Adyar"},
  "TN-9949":    {name:"Kaviya", ward:"Ward 4 — Mylapore"}
};

let ADMIN_ROLL = {
  "MC-ADM-001": {name:"S. Kalaivani", role:"Ward Engineer"},
  "MC-ADM-002": {name:"R. Venkataraghavan", role:"Municipal Commissioner Office"},
  "MC-ADM-003": {name:"T. Preethi", role:"Budget Officer"}
};

const CHART_COLORS = ['var(--gold)','var(--teal)','#8B8FD6','#D68B70','#6FBF9B'];

let proposals = [
  {id:1, ward:"Ward 1 — Anna Nagar", name:"Anna Park Renovation", desc:"Resurface walking paths, repair fencing and add shaded seating in the community park.", budget:1200000},
  {id:2, ward:"Ward 1 — Anna Nagar", name:"Street Light Upgrade", desc:"Replace 40 sodium-vapour lamps along residential lanes with LED fixtures.", budget:850000},
  {id:3, ward:"Ward 2 — T Nagar", name:"Main Road Repair", desc:"Pothole repair and resurfacing of the 2km arterial stretch through the ward market.", budget:1500000},
  {id:4, ward:"Ward 2 — T Nagar", name:"Public Toilet Block", desc:"Construct a new accessible public toilet block near the bus terminus.", budget:600000},
  {id:5, ward:"Ward 3 — Adyar", name:"Solar Pathway Lighting", desc:"Install 30 solar-powered LED lights along the Adyar riverfront path.", budget:950000},
  {id:6, ward:"Ward 3 — Adyar", name:"Rainwater Recharge Wells", desc:"Construct 6 community rainwater percolation wells to elevate the water table.", budget:720000},
  {id:7, ward:"Ward 4 — Mylapore", name:"Heritage Walkway Restoration", desc:"Repair traditional cobblestones and install visitor directionals around the temple circle.", budget:1100000},
  {id:8, ward:"Ward 4 — Mylapore", name:"Stormwater Culvert Desilting", desc:"Deep desilting and reinforced grating for flood prevention in residential streets.", budget:820000}
];

let nextId = 9;
let voteLog = [];            // [{proposalId, ward, voterId, ts, prevHash, hash}]
let votedVoters = new Set(); // set of voter IDs that have voted
let dbStats = { voters: 24, proposals: 8, votes: 0, wards: 4, grievances: 2 };

let grievances = [
  {
    id: "GRV-0881",
    type: "suggestion",
    voter_id: "TN-0119284",
    name: "Priya Raman",
    ward: "Ward 1 — Anna Nagar",
    subject: "Add EV charging points near park entrance",
    details: "With rising electric scooter adoption, 4 public charging docks at Anna Park would greatly benefit residents.",
    status: "Under Review",
    created_at: new Date(Date.now() - 3600000 * 24).toISOString()
  },
  {
    id: "GRV-0882",
    type: "complaint",
    voter_id: "TN-0223391",
    name: "Rahul Verma",
    ward: "Ward 2 — T Nagar",
    subject: "Pothole on 3rd Cross Street",
    details: "Deep crater after recent rain causing waterlogging and traffic hazards.",
    status: "Pending",
    created_at: new Date(Date.now() - 3600000 * 5).toISOString()
  }
];

let API_URL = '';
if (typeof window !== 'undefined') {
  if (window.location.protocol === 'file:') {
    API_URL = 'http://127.0.0.1:5000';
  } else if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    API_URL = (window.location.port === '5000') ? '' : 'http://127.0.0.1:5000';
  } else {
    API_URL = '';
  }
}

let isDbConnected = false;
const STORAGE_KEY = 'wardLedgerState_v3';

/* ---------------- synchronization & persistence ---------------- */

async function loadState(){
  if(API_URL !== '' || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')){
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 1800);
      const res = await fetch(`${API_URL}/api/bootstrap`, { cache: 'no-store', signal: controller.signal });
      clearTimeout(timeoutId);
      if(res.ok){
        const data = await res.json();
        if(data.wards && data.wards.length) WARDS = data.wards.map(normalizeWard);
        if(data.proposals) proposals = data.proposals.map(p => ({...p, ward: normalizeWard(p.ward)}));
        if(data.voteLog) voteLog = data.voteLog.map(v => ({...v, ward: normalizeWard(v.ward)}));
        if(data.votedVoters) votedVoters = new Set(data.votedVoters);
        if(data.voterRoll && Object.keys(data.voterRoll).length){
          for(const [k, v] of Object.entries(data.voterRoll)){
            VOTER_ROLL[k] = { name: v.name, ward: normalizeWard(v.ward) };
          }
        }
        if(data.adminRoll && Object.keys(data.adminRoll).length) ADMIN_ROLL = data.adminRoll;
        if(data.grievances && data.grievances.length) grievances = data.grievances;
        if(data.stats) dbStats = data.stats;
        isDbConnected = true;
        saveLocalBackup();
        return true;
      }
    } catch(e) {
      isDbConnected = false;
    }
  }

  try{
    const raw = localStorage.getItem(STORAGE_KEY);
    if(raw){
      const s = JSON.parse(raw);
      if(s.proposals && s.proposals.length) proposals = s.proposals.map(p => ({...p, ward: normalizeWard(p.ward)}));
      if(typeof s.nextId === 'number') nextId = s.nextId;
      if(s.voteLog) voteLog = s.voteLog.map(v => ({...v, ward: normalizeWard(v.ward)}));
      if(s.votedVoters) votedVoters = new Set(s.votedVoters);
      if(s.wards && s.wards.length) WARDS = s.wards.map(normalizeWard);
      if(s.voterRoll && Object.keys(s.voterRoll).length){
        for(const [k, v] of Object.entries(s.voterRoll)){
          VOTER_ROLL[k] = { name: v.name, ward: normalizeWard(v.ward) };
        }
      }
      if(s.adminRoll && Object.keys(s.adminRoll).length) ADMIN_ROLL = s.adminRoll;
      if(s.grievances && s.grievances.length) grievances = s.grievances;
    } else {
      saveLocalBackup();
    }
  }catch(e){
    console.warn('Ward Ledger: Local storage backup unavailable.', e);
  }
  return false;
}

function saveLocalBackup(){
  try{
    localStorage.setItem(STORAGE_KEY, JSON.stringify({
      wards: WARDS,
      proposals,
      nextId,
      voteLog,
      votedVoters: [...votedVoters],
      voterRoll: VOTER_ROLL,
      adminRoll: ADMIN_ROLL,
      grievances
    }));
  }catch(e){}
}

let _channel = null;
let _onUpdateCallback = null;

function subscribeToUpdates(onChange){
  _onUpdateCallback = onChange;
  try{
    _channel = new BroadcastChannel('ward-ledger');
    _channel.onmessage = async () => { await loadState(); onChange(); };
  }catch(e){}

  window.addEventListener('storage', async e=>{
    if(e.key === STORAGE_KEY){ await loadState(); onChange(); }
  });

  setInterval(async () => {
    const prevVoteCount = voteLog.length;
    const prevPropCount = proposals.length;
    const prevVoterCount = Object.keys(VOTER_ROLL).length;
    const prevGrvCount = grievances.length;
    await loadState();
    if(voteLog.length !== prevVoteCount || proposals.length !== prevPropCount || Object.keys(VOTER_ROLL).length !== prevVoterCount || grievances.length !== prevGrvCount){
      if(_onUpdateCallback) _onUpdateCallback();
    }
  }, 3500);
}

function broadcastChange(){
  saveLocalBackup();
  if(_channel){ try{ _channel.postMessage('update'); }catch(e){} }
}

/* ---------------- crypto chain & vote operations ---------------- */

async function sha256(str){
  const buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(str));
  return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,'0')).join('');
}
function shortHash(h){ return h ? (h.slice(0,6)+'…'+h.slice(-4)) : ''; }

async function castVote(proposalId, session){
  if(!session) return { ok: false, error: "No active resident session." };
  
  const normWard = normalizeWard(session.ward);

  if(isDbConnected){
    try{
      const res = await fetch(`${API_URL}/api/vote`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          proposalId,
          voterId: session.voterId,
          ward: normWard
        })
      });
      const data = await res.json();
      if(res.ok && data.ok){
        voteLog.push(data.entry);
        votedVoters.add(session.voterId);
        broadcastChange();
        return { ok: true, entry: data.entry };
      } else {
        return { ok: false, error: data.error || 'Failed to cast vote in database.' };
      }
    }catch(err){
      console.warn('API vote failed, falling back to local chain', err);
    }
  }

  if(votedVoters.has(session.voterId)) return { ok: false, error: "Voter has already cast a vote." };
  const prevHash = voteLog.length ? voteLog[voteLog.length-1].hash : 'GENESIS-WARD-LEDGER';
  const entry = {proposalId: Number(proposalId), ward: normWard, voterId: session.voterId, ts: Date.now()};
  const hash = await sha256(prevHash + JSON.stringify(entry));
  const fullEntry = {...entry, prevHash, hash};
  voteLog.push(fullEntry);
  votedVoters.add(session.voterId);
  broadcastChange();
  return { ok: true, entry: fullEntry };
}

async function verifyChain(){
  if(isDbConnected){
    try{
      const res = await fetch(`${API_URL}/api/verify`);
      if(res.ok){
        const data = await res.json();
        return data.ok;
      }
    }catch(e){}
  }

  let prev = 'GENESIS-WARD-LEDGER';
  for(const e of voteLog){
    const entry = {proposalId: Number(e.proposalId), ward: normalizeWard(e.ward), voterId: e.voterId, ts: e.ts};
    const h = await sha256(prev + JSON.stringify(entry));
    if(h !== e.hash || e.prevHash !== prev) return false;
    prev = e.hash;
  }
  return true;
}

/* ---------------- proposal & voter data feeding ---------------- */

async function addProposal(name, desc, budget, rawWard){
  const ward = normalizeWard(rawWard);
  if(isDbConnected){
    try{
      const res = await fetch(`${API_URL}/api/proposals`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, desc, budget, ward})
      });
      const data = await res.json();
      if(res.ok && data.ok){
        proposals.push(data.proposal);
        broadcastChange();
        return { ok: true, proposal: data.proposal };
      }
    }catch(e){
      console.warn('Failed to add proposal via API, adding locally', e);
    }
  }

  const p = {id: nextId++, ward, name, desc, budget};
  proposals.push(p);
  if(!WARDS.includes(ward)) WARDS.push(ward);
  broadcastChange();
  return { ok: true, proposal: p };
}

async function addSingleVoter(voterId, name, rawWard){
  const ward = normalizeWard(rawWard);
  if(isDbConnected){
    try{
      const res = await fetch(`${API_URL}/api/voters`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({voter_id: voterId, name, ward})
      });
      const data = await res.json();
      if(res.ok && data.ok){
        VOTER_ROLL[voterId] = { name, ward };
        broadcastChange();
        return { ok: true, message: data.message };
      } else {
        return { ok: false, error: data.error || 'Failed to add voter' };
      }
    }catch(e){
      return { ok: false, error: 'Database network error' };
    }
  }

  if(VOTER_ROLL[voterId]){
    return { ok: false, error: `Voter ${voterId} already exists in roll.` };
  }
  VOTER_ROLL[voterId] = { name, ward };
  if(!WARDS.includes(ward)) WARDS.push(ward);
  broadcastChange();
  return { ok: true, message: `Voter ${name} (${voterId}) registered successfully.` };
}

async function bulkFeedData(type, fileOrText, isFile=false){
  if(isDbConnected){
    const formData = new FormData();
    formData.append('type', type);
    if(isFile){
      formData.append('file', fileOrText);
    } else {
      formData.append('text', fileOrText);
    }

    try{
      const res = await fetch(`${API_URL}/api/feed/csv`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if(res.ok && data.ok){
        await loadState();
        broadcastChange();
        return data;
      } else {
        return { ok: false, error: data.error || 'Feed operation failed.' };
      }
    }catch(e){
      console.warn('Backend feed failed, trying browser parse fallback', e);
    }
  }

  let rawRows = [];

  if(isFile && fileOrText.name && fileOrText.name.match(/\.xlsx?$|\.csv$/i)){
    if(window.XLSX && fileOrText.name.match(/\.xlsx?$/i)){
      try {
        const buffer = await fileOrText.arrayBuffer();
        const workbook = window.XLSX.read(buffer, { type: 'array' });
        const firstSheetName = workbook.SheetNames[0];
        const worksheet = workbook.Sheets[firstSheetName];
        rawRows = window.XLSX.utils.sheet_to_json(worksheet, { defval: '' });
      } catch(err){
        return { ok: false, error: "Failed to parse Excel file in browser." };
      }
    } else {
      try {
        const text = await fileOrText.text();
        rawRows = parseCsvTextToRows(text);
      } catch(err){
        return { ok: false, error: "Failed to read CSV file in browser." };
      }
    }
  } else if(!isFile && typeof fileOrText === 'string'){
    rawRows = parseCsvTextToRows(fileOrText);
  }

  if(!rawRows || rawRows.length === 0){
    return { ok: false, error: "No data rows could be parsed from file or text." };
  }

  let target = type;
  const firstKeys = Object.keys(rawRows[0]).map(k => k.toLowerCase());
  const hasVoterKeys = firstKeys.some(k => k.includes('voter') || k.includes('epic') || k.includes('vid') || k === 'id');
  const hasPropKeys = firstKeys.some(k => k.includes('budget') || k.includes('cost') || k.includes('proposal') || k.includes('project'));
  if(hasVoterKeys && !hasPropKeys) target = 'voters';
  if(hasPropKeys && !hasVoterKeys) target = 'proposals';

  let added = 0, skipped = 0;
  if(target === 'voters'){
    for(const row of rawRows){
      let vid = '', name = '', ward = '';
      for(const [k, v] of Object.entries(row)){
        const kl = k.trim().toLowerCase().replace(/[-_]/g, ' ');
        const val = String(v).trim();
        if(!val) continue;
        if(kl.includes('voter') || kl.includes('epic') || kl.includes('vid') || kl === 'id'){
          vid = val.toUpperCase();
        } else if(kl.includes('name') || kl.includes('resident') || kl.includes('citizen')){
          name = val;
        } else if(kl.includes('ward')){
          ward = normalizeWard(val);
        }
      }
      if(!vid || !name || !ward) continue;
      if(VOTER_ROLL[vid]){
        skipped++;
        continue;
      }
      VOTER_ROLL[vid] = { name, ward };
      if(!WARDS.includes(ward)) WARDS.push(ward);
      added++;
    }
    broadcastChange();
    return {
      ok: true,
      added,
      skipped,
      totalProcessed: rawRows.length,
      message: `Processed ${rawRows.length} rows: ${added} new voters registered (${skipped} duplicates skipped).`
    };
  } else {
    for(const row of rawRows){
      let name = '', desc = '', ward = '', budget = 0;
      for(const [k, v] of Object.entries(row)){
        const kl = k.trim().toLowerCase().replace(/[-_]/g, ' ');
        const val = String(v).trim();
        if(!val) continue;
        if(kl.includes('ward')){
          ward = normalizeWard(val);
        } else if(kl.includes('name') || kl.includes('title') || kl.includes('project') || kl.includes('proposal')){
          name = val;
        } else if(kl.includes('desc') || kl.includes('detail') || kl.includes('summary')){
          desc = val;
        } else if(kl.includes('budget') || kl.includes('cost') || kl.includes('amount') || kl.includes('estimate')){
          budget = parseInt(val.replace(/[^0-9]/g, ''), 10) || 0;
        }
      }
      if(!name || !ward || !budget) continue;
      proposals.push({ id: nextId++, ward, name, desc: desc || name, budget });
      if(!WARDS.includes(ward)) WARDS.push(ward);
      added++;
    }
    broadcastChange();
    return {
      ok: true,
      added,
      skipped: 0,
      totalProcessed: rawRows.length,
      message: `Processed ${rawRows.length} rows: ${added} proposals added.`
    };
  }
}

function parseCsvTextToRows(text){
  const lines = text.split(/\r?\n/).map(l => l.trim()).filter(l => l);
  if(lines.length < 2) return [];
  const headers = lines[0].split(',').map(h => h.trim().replace(/^["']|["']$/g, ''));
  const rows = [];
  for(let i=1; i<lines.length; i++){
    const cols = lines[i].split(',').map(c => c.trim().replace(/^["']|["']$/g, ''));
    const obj = {};
    headers.forEach((h, idx) => {
      obj[h] = cols[idx] !== undefined ? cols[idx] : '';
    });
    rows.push(obj);
  }
  return rows;
}

async function addWard(rawWard){
  const wardName = normalizeWard(rawWard);
  if(isDbConnected){
    try{
      await fetch(`${API_URL}/api/wards`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name: wardName})
      });
    }catch(e){}
  }
  if(!WARDS.includes(wardName)){
    WARDS.push(wardName);
    broadcastChange();
  }
  return { ok: true, name: wardName };
}

/* ---------------- Civic Grievances & Suggestion Box ---------------- */

async function submitGrievance(type, voterId, name, rawWard, subject, details){
  const ward = normalizeWard(rawWard);
  const gid = 'GRV-' + Math.floor(1000 + Math.random() * 9000);
  const entry = {
    id: gid,
    type,
    voter_id: voterId || null,
    name: name || 'Ward Resident',
    ward,
    subject,
    details,
    status: 'Pending',
    created_at: new Date().toISOString()
  };

  if(isDbConnected){
    try{
      const res = await fetch(`${API_URL}/api/grievances`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(entry)
      });
      const data = await res.json();
      if(res.ok && data.ok){
        grievances.unshift(data.grievance);
        broadcastChange();
        return { ok: true, grievance: data.grievance };
      }
    }catch(e){}
  }

  grievances.unshift(entry);
  broadcastChange();
  return { ok: true, grievance: entry };
}

async function updateGrievanceStatus(gid, newStatus){
  if(isDbConnected){
    try{
      await fetch(`${API_URL}/api/grievances/status`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({id: gid, status: newStatus})
      });
    }catch(e){}
  }

  const found = grievances.find(g => g.id === gid);
  if(found){
    found.status = newStatus;
    broadcastChange();
    return true;
  }
  return false;
}

async function resetDbToCleanSeed(){
  if(isDbConnected){
    try{
      const res = await fetch(`${API_URL}/api/reset`, { method: 'POST' });
      if(res.ok){
        await loadState();
        broadcastChange();
        return true;
      }
    }catch(e){}
  }
  localStorage.removeItem(STORAGE_KEY);
  await loadState();
  broadcastChange();
  return true;
}

/* ---------------- helpers ---------------- */
const inr = n => '₹' + Number(n).toLocaleString('en-IN');
const votesFor = pid => voteLog.filter(v=>Number(v.proposalId)===Number(pid)).length;
const proposalsByWard = w => proposals.filter(p => normalizeWard(p.ward) === normalizeWard(w));
function registeredCount(w){ return Object.values(VOTER_ROLL).filter(v => normalizeWard(v.ward) === normalizeWard(w)).length; }
function turnoutCount(w){ return [...votedVoters].filter(id => VOTER_ROLL[id] && normalizeWard(VOTER_ROLL[id].ward) === normalizeWard(w)).length; }

/* ---------------- UI rendering helpers ---------------- */
function renderSyncNote(){
  if(isDbConnected){
    return `<span class="dot" style="background:#5FA893;"></span><span><b>SQLite Database Active</b> (ward_ledger.db) · Real-time persistent state</span>`;
  }
  return `<span class="dot" style="background:#E4C766;"></span><span><b>Standalone Web Storage Mode</b> · SHA-256 chained client ledger active</span>`;
}

function renderResultsForWard(w){
  const list = proposalsByWard(w);
  const registered = registeredCount(w);
  const turnout = turnoutCount(w);
  const turnoutHTML = `
    <div class="panel" style="margin-bottom:18px;">
      <div class="bar-row" style="margin-bottom:0;">
        <div class="bar-label"><span class="name">${t('turnout')}</span><span class="n">${turnout} ${t('of_residents')} (${registered})</span></div>
        <div class="bar-track"><div class="bar-fill" style="width:${registered? (turnout/registered*100):0}%"></div></div>
      </div>
    </div>`;
  if(list.length===0) return turnoutHTML + `<div class="empty">${t('no_proposals')}</div>`;
  const counted = list.map(p=>({...p, votes:votesFor(p.id)}));
  const totalVotes = counted.reduce((s,p)=>s+p.votes,0);
  const maxVotes = Math.max(1, ...counted.map(p=>p.votes));

  const bars = counted.map((p,i)=>`
    <div class="bar-row">
      <div class="bar-label"><span class="name">${p.name}</span><span class="n">${p.votes} ${p.votes===1?t('proposal_single'):t('proposals_count')}</span></div>
      <div class="bar-track"><div class="bar-fill ${i%2===0?'gold':''}" style="width:${(p.votes/maxVotes*100)}%"></div></div>
    </div>`).join('');

  let donutHTML, legendHTML;
  if(totalVotes===0){
    donutHTML = `<div class="donut" style="background:var(--panel-3)"></div>`;
    legendHTML = `<span style="color:var(--text-faint)">${t('no_votes_yet')}</span>`;
  } else {
    let acc=0; const stops=[];
    counted.forEach((p,i)=>{
      const pct = p.votes/totalVotes*100;
      const color = CHART_COLORS[i%CHART_COLORS.length];
      stops.push(`${color} ${acc}% ${acc+pct}%`);
      acc+=pct;
    });
    donutHTML = `<div class="donut" style="background:conic-gradient(${stops.join(',')})"></div>`;
    legendHTML = counted.map((p,i)=>{
      const pct = totalVotes? (p.votes/totalVotes*100):0;
      return `<div><span class="swatch" style="background:${CHART_COLORS[i%CHART_COLORS.length]}"></span>${p.name} — ${pct.toFixed(0)}%</div>`;
    }).join('');
  }

  return turnoutHTML + `
    <div class="panel">
      <h3 style="font-size:0.95rem; margin-bottom:14px; color:var(--text-dim); font-family:'IBM Plex Sans'; font-weight:600;">${t('vote_tally')}</h3>
      ${bars}
    </div>
    <div class="panel">
      <h3 style="font-size:0.95rem; margin-bottom:14px; color:var(--text-dim); font-family:'IBM Plex Sans'; font-weight:600;">${t('fund_allocation')}</h3>
      <div class="allocation-donut">
        ${donutHTML}
        <div class="donut-legend">${legendHTML}</div>
      </div>
    </div>`;
}

async function renderLedgerPanel(scopeWard){
  const rows = (scopeWard ? voteLog.filter(v => normalizeWard(v.ward) === normalizeWard(scopeWard)) : voteLog).slice(-8).reverse();
  const rowsHTML = rows.length ? rows.map(v=>{
    const p = proposals.find(pp=>Number(pp.id)===Number(v.proposalId));
    return `<tr><td>${new Date(v.ts).toLocaleTimeString()}</td><td>${p?p.name:'—'}</td><td>${shortHash(v.prevHash)}</td><td>${shortHash(v.hash)}</td></tr>`;
  }).join('') : `<tr><td colspan="4" style="color:var(--text-faint); font-family:'IBM Plex Sans'">${t('no_votes_db')}</td></tr>`;

  return `
    <div class="panel">
      <div class="verify-row">
        <h3 style="font-size:0.95rem; color:var(--text-dim); font-family:'IBM Plex Sans'; font-weight:600;">${t('vote_ledger')}</h3>
        <button class="btn-secondary" onclick="runVerify()">${t('verify_integrity')}</button>
      </div>
      <div id="verify-result"></div>
      <div class="ledger-wrap">
        <table class="ledger-table">
          <thead><tr><th>${t('time_th')}</th><th>${t('proposal_th')}</th><th>${t('prev_hash_th')}</th><th>${t('entry_hash_th')}</th></tr></thead>
          <tbody>${rowsHTML}</tbody>
        </table>
      </div>
    </div>`;
}

async function runVerify(){
  const ok = await verifyChain();
  const resEl = document.getElementById('verify-result');
  if(resEl){
    resEl.innerHTML = ok
      ? `<div class="verify-badge">✓ Chain verified — ${voteLog.length} vote${voteLog.length===1?'':'s'} intact</div>`
      : `<div class="verify-badge" style="background:rgba(193,85,58,0.18); color:var(--danger);">✗ Chain broken — tampering detected</div>`;
  }
}
