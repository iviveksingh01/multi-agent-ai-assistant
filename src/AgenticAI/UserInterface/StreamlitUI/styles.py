"""Custom styling for the Streamlit chat interface."""

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --accent: #4f46e5;
    --accent-2: #7c3aed;
    --ink: #0f172a;
    --muted: #64748b;
    --line: #e2e8f0;
    --soft: #f5f7fb;
}

.stApp { font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif; }
.stApp { background: linear-gradient(180deg, #f5f7fb 0px, #ffffff 320px); }
#MainMenu, footer, [data-testid="stDecoration"] { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2rem; padding-bottom: 7rem; max-width: 1080px; }

/* ---------- Hero ---------- */
.hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 60%, #a855f7 100%);
    border-radius: 18px; padding: 20px 24px; color: #fff;
    display: flex; align-items: center; gap: 16px;
    box-shadow: 0 14px 34px -16px rgba(79, 70, 229, .6);
    margin-bottom: 1.25rem;
}
.hero-icon {
    font-size: 30px; width: 56px; height: 56px; flex: 0 0 56px;
    border-radius: 14px; background: rgba(255,255,255,.18);
    display: flex; align-items: center; justify-content: center;
}
.hero-text { flex: 1; min-width: 0; }
.hero-title { font-size: 1.35rem; font-weight: 700; line-height: 1.2; color: #fff; }
.hero-sub { font-size: .9rem; color: rgba(255,255,255,.85); margin-top: 3px; }
.hero-pill {
    font-size: .75rem; font-weight: 600; padding: 6px 12px; border-radius: 999px;
    background: rgba(255,255,255,.16); border: 1px solid rgba(255,255,255,.28);
    white-space: nowrap; color: #fff;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid var(--line); }
.side-brand { display: flex; align-items: center; gap: 12px; padding: 4px 0 10px; }
.side-brand .logo {
    width: 40px; height: 40px; border-radius: 11px; font-size: 20px;
    background: linear-gradient(135deg, #4f46e5, #a855f7);
    display: flex; align-items: center; justify-content: center;
}
.side-brand .name { font-weight: 700; font-size: 1.02rem; color: var(--ink); }
.side-brand .sub { font-size: .72rem; color: var(--muted); line-height: 1.3; }
.side-section {
    font-size: .7rem; letter-spacing: .09em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; margin: 18px 0 4px;
    padding-top: 14px; border-top: 1px solid var(--line);
}
.side-footer { font-size: .75rem; color: var(--muted); margin-top: 18px; line-height: 1.6; }
.side-footer a { color: var(--accent); text-decoration: none; }

/* ---------- Status badges ---------- */
.status {
    display: inline-flex; align-items: center; gap: 6px; font-size: .75rem;
    padding: 3px 10px; border-radius: 999px; font-weight: 500; margin: 2px 0 6px;
}
.status::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: currentColor; }
.status.ok   { background: #dcfce7; color: #15803d; }
.status.warn { background: #fef3c7; color: #b45309; }
.status.soon { background: #f1f5f9; color: #475569; }
.status a { color: inherit; font-weight: 600; }

/* ---------- Chat bubbles ---------- */
[data-testid="stChatMessage"] {
    background: #ffffff; border: 1px solid var(--line); border-radius: 16px;
    padding: 14px 18px; margin-bottom: 12px;
    box-shadow: 0 1px 3px rgba(15, 23, 42, .05);
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: #eef2ff; border-color: #c7d2fe;
}
[data-testid="stChatMessage"] [data-testid="stCaptionContainer"] { opacity: .7; }
[data-testid="stChatInput"] {
    border-radius: 16px;
    box-shadow: 0 8px 28px -12px rgba(79, 70, 229, .45);
}

/* ---------- Buttons ---------- */
[data-testid="stElementContainer"]:has(.stButton), .stButton { width: 100% !important; }
.stButton > button, .stDownloadButton > button {
    width: 100%; border-radius: 12px; border: 1px solid var(--line);
    background: #fff; color: var(--ink); font-weight: 500;
    padding: .6rem .9rem; transition: all .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    border-color: var(--accent); color: var(--accent);
    box-shadow: 0 6px 16px -8px rgba(79, 70, 229, .5); transform: translateY(-1px);
}
.stButton > button:disabled { opacity: .5; transform: none; box-shadow: none; }

/* ---------- Welcome screen ---------- */
.welcome { text-align: center; padding: 26px 8px 6px; }
.welcome .big { font-size: 46px; line-height: 1; }
.welcome .title { font-size: 1.55rem; font-weight: 700; color: var(--ink); margin-top: 12px; }
.welcome .sub { color: var(--muted); font-size: .95rem; margin: 6px auto 0; max-width: 560px; }
.flow { display: flex; flex-wrap: wrap; justify-content: center; gap: 8px; margin: 18px 0 8px; }
.flow .step {
    font-size: .8rem; color: #3730a3; background: #eef2ff; border: 1px solid #e0e7ff;
    padding: 6px 12px; border-radius: 999px; font-weight: 500;
}
.flow .arrow { color: #a5b4fc; align-self: center; }
.try-label {
    text-align: center; font-size: .72rem; letter-spacing: .09em; text-transform: uppercase;
    color: var(--muted); font-weight: 600; margin: 18px 0 8px;
}

/* ---------- Tool sources ---------- */
.src {
    border: 1px solid var(--line); border-radius: 12px; padding: 10px 12px;
    margin-bottom: 8px; background: #fff;
}
.src a { font-weight: 600; color: var(--accent); text-decoration: none; font-size: .9rem; }
.src a:hover { text-decoration: underline; }
.src .host { font-size: .72rem; color: var(--muted); margin-top: 1px; }
.src .snip { font-size: .83rem; color: #334155; margin-top: 4px; line-height: 1.45; }

/* ---------- Notices ---------- */
.notice {
    border-left: 4px solid #f59e0b; background: #fffbeb; color: #78350f;
    padding: 10px 14px; border-radius: 10px; font-size: .9rem; margin-bottom: 8px;
}

/* ---------- Metrics ---------- */
[data-testid="stMetric"] {
    background: var(--soft); border: 1px solid var(--line);
    border-radius: 12px; padding: 10px 14px;
}
[data-testid="stMetricValue"] { font-size: 1.25rem; }
</style>
"""
