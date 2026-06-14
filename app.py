# ============================================================
# Bucket-List - interaktives Mock-up (Streamlit Community Cloud)
#
# MVP-Konzept "Relationale Freizeitplattform":
#   - Profil mit Vorlieben je Kategorie (frei erweiterbar)
#   - Equipment zum Teilen (frei erweiterbar)
#   - Matching-Vorschläge (gemeinsame Vorlieben)
#   - Aktivitäts-Posts mit Zielgruppenauswahl
#   - "Ich bin dabei!" und Kommentare (nur für Teilnehmende)
#   - Ruhemodus / Verfügbarkeitsstatus
#
# Hinweis: Reines Mock-up. Der Zustand liegt in st.session_state
# und wird je Session zurückgesetzt (keine persistente Datenbank).
# Das Logo wird aus assets/logo.svg geladen und kann dort durch
# das offizielle Markenasset ersetzt werden.
# ============================================================

import base64
import html
import pathlib
from datetime import datetime, timedelta

import streamlit as st

BASE_DIR = pathlib.Path(__file__).parent
LOGO_PATH = BASE_DIR / "assets" / "logo.svg"

st.set_page_config(
    page_title="Bucket-List",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None,
    layout="wide",
)

# ------------------------------------------------------------
# Branding (Layout / Typografie / Farben)
# ------------------------------------------------------------
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600&display=swap');

:root{
  --bl-terra:#C0613F; --bl-terra-dark:#A44E30; --bl-sand:#FBF7EF;
  --bl-beige:#EADBC0; --bl-ink:#37414A; --bl-muted:#8A8F94;
  --bl-card:#FFFFFF; --bl-line:#ECE3D2;
  --bl-sage-bg:#E4EDDA; --bl-sage-ink:#4F6B3E;
}
.stApp{ background:var(--bl-sand); }
html, body, [class^="st-"], .stMarkdown, p, span, div, label, input, textarea, button{
  font-family:'Inter', -apple-system, Arial, sans-serif;
}
h1,h2,h3,[data-testid="stHeading"]{
  font-family:'Fraunces','Georgia',serif !important;
  color:var(--bl-ink); letter-spacing:-0.01em; font-weight:600;
}
.block-container{ padding-top:2.2rem; max-width:1100px; }

/* Hero */
.bl-hero{
  display:flex; align-items:center; gap:20px;
  background:linear-gradient(180deg,#FFFFFF 0%, #FCF6EC 100%);
  border:1px solid var(--bl-line); border-radius:20px;
  padding:20px 26px; margin-bottom:22px;
  box-shadow:0 6px 24px rgba(55,65,74,0.06);
}
.bl-hero-logo{ width:64px; height:64px; flex:0 0 auto; }
.bl-hero-title{ font-family:'Fraunces',serif; font-size:34px; font-weight:700; color:var(--bl-terra); line-height:1.05; }
.bl-hero-sub{ font-size:15px; color:var(--bl-muted); margin-top:2px; }

/* Karten (bordered container) */
[data-testid="stVerticalBlockBorderWrapper"]{
  background:var(--bl-card); border:1px solid var(--bl-line) !important;
  border-radius:16px; padding:6px 18px 14px 18px;
  box-shadow:0 4px 16px rgba(55,65,74,0.05);
}
.bl-card-head{ border-bottom:1px solid var(--bl-line); padding-bottom:8px; margin-bottom:8px; }
.bl-title{ font-family:'Fraunces',serif; font-size:21px; font-weight:600; color:var(--bl-ink); }
.bl-meta{ font-size:13px; color:var(--bl-muted); margin-top:2px; }

/* Buttons */
.stButton > button, .stFormSubmitButton > button{
  background:var(--bl-terra); color:#fff; border:0; border-radius:10px;
  font-weight:600; padding:0.45rem 1.1rem; transition:background .15s ease;
}
.stButton > button:hover, .stFormSubmitButton > button:hover{ background:var(--bl-terra-dark); color:#fff; }

/* Tabs */
.stTabs [data-baseweb="tab-list"]{ gap:6px; border-bottom:1px solid var(--bl-line); }
.stTabs [data-baseweb="tab"]{ font-weight:600; color:var(--bl-muted); }
.stTabs [aria-selected="true"]{ color:var(--bl-terra) !important; }
.stTabs [data-baseweb="tab-highlight"]{ background-color:var(--bl-terra) !important; }

/* Multiselect-Chips */
[data-baseweb="tag"]{ background-color:#F3D9CB !important; color:#7A3A22 !important; border-radius:8px !important; }

/* Sidebar */
[data-testid="stSidebar"]{ background:#F6EEDF; border-right:1px solid var(--bl-line); }

/* Pills, Badges, Vorschlag */
.bl-pill{ display:inline-block; background:#F3D9CB; color:#7A3A22; border-radius:999px;
  padding:3px 11px; margin:3px 6px 3px 0; font-size:13px; font-weight:500; }
.bl-badge{ display:inline-block; border-radius:999px; padding:3px 12px; font-size:13px; font-weight:600; }
.bl-badge-open{ background:var(--bl-sage-bg); color:var(--bl-sage-ink); }
.bl-badge-quiet{ background:#E7E4DE; color:#6B6F74; }
.bl-suggest{ background:#FBEEE6; border-left:3px solid var(--bl-terra); border-radius:8px;
  padding:8px 12px; margin-top:8px; color:var(--bl-ink); font-size:14px; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if LOGO_PATH.exists():
    try:
        st.logo(str(LOGO_PATH), size="large")
    except Exception:
        pass


def logo_data_uri():
    try:
        b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode()
        return f"data:image/svg+xml;base64,{b64}"
    except Exception:
        return ""


# ------------------------------------------------------------
# Stammdaten / Kataloge
# ------------------------------------------------------------
VORLIEBEN = {
    "Sport": ["Padel", "Fussball", "Laufen", "Velo fahren", "Klettern", "Yoga", "Tennis",
              "Tanzen", "Gym", "Bouldern"],
    "Kultur": ["Museen", "Konzerte", "Kino", "Theater", "Lesungen", "Poetry Slam", "Comedy"],
    "Kulinarik": ["Restaurants", "Gemeinsam Kochen", "Kaffee trinken", "Feierabend-Bier", "Brunch"],
    "Ausflüge": ["Stadtrundgang", "Wandern", "Velotour", "Badi / See", "Fahrt ins Blaue"],
    "Adventure": ["Klettersteig", "Kajak / SUP", "Bergtour", "Ski-Tour", "River Rafting"],
    "Kids": ["Spielplatz", "Basteln", "Zoo", "Schwimmbad"],
    "Spiel & Spass": ["Tischtennis", "Brettspiele", "Jassen", "Boule", "Kartenspiele", "Gamen", "Karaoke"],
    "Events": ["Konzerte (Open Air)", "Festivals", "Food-Festivals", "Märkte"],
}

EQUIPMENT = [
    "Segelboot (Bareboat)", "Segelschein", "Auto", "Velo / E-Bike",
    "SUP-Board", "Zelt", "Pizzaofen", "Gesellschaftsspiele", "Leinwand / Beamer",
    "Kanu", "Raclette-Ofen", "Festbank-Garnitur", "GA", "PlayStation", "Karaoke",
]

STATUS_OFFEN = "Offen für Aktivitäten"
STATUS_RUHE = "Ruhemodus"


# ------------------------------------------------------------
# Seed-Daten
# ------------------------------------------------------------
def seed_users():
    return {
        "Gabriel": {
            "vorlieben": {"Padel", "Velo fahren", "Wandern", "Feierabend-Bier", "Jassen", "Restaurants"},
            "equipment": {"Velo / E-Bike", "Pizzaofen", "Gesellschaftsspiele", "GA"},
            "status": STATUS_OFFEN,
        },
        "Anna": {
            "vorlieben": {"Padel", "Yoga", "Brunch", "Konzerte (Open Air)", "Wandern", "Tanzen"},
            "equipment": {"Auto", "Zelt", "SUP-Board"},
            "status": STATUS_OFFEN,
        },
        "Marco": {
            "vorlieben": {"Fussball", "Feierabend-Bier", "Jassen", "Velo fahren", "Restaurants", "Gamen"},
            "equipment": {"Segelboot (Bareboat)", "Segelschein", "Leinwand / Beamer", "PlayStation"},
            "status": STATUS_RUHE,
        },
        "Lena": {
            "vorlieben": {"Klettern", "Kajak / SUP", "Bergtour", "Kaffee trinken", "Festivals", "Bouldern"},
            "equipment": {"Kanu", "Auto"},
            "status": STATUS_OFFEN,
        },
        "Sophie": {
            "vorlieben": {"Museen", "Kino", "Brunch", "Wandern", "Restaurants", "Comedy", "Karaoke"},
            "equipment": {"Raclette-Ofen", "Gesellschaftsspiele", "Karaoke"},
            "status": STATUS_OFFEN,
        },
    }


def seed_posts():
    heute = datetime.now()
    return [
        {
            "id": 1, "author": "Anna", "titel": "Padel am Samstagvormittag",
            "text": "Court in Bern für Samstag 10:00 reserviert. Zwei Plätze frei.",
            "wann": (heute + timedelta(days=2)).strftime("%d.%m.%Y, 10:00"), "link": "",
            "audience": ["Gabriel", "Marco", "Lena", "Sophie"],
            "participants": ["Gabriel"],
            "comments": [("Gabriel", "Bin dabei. Soll ich Bälle mitbringen?")],
        },
        {
            "id": 2, "author": "Marco", "titel": "Segeltörn Bielersee",
            "text": "Nächstes Wochenende mit dem Boot raus. Segelschein nicht nötig.",
            "wann": (heute + timedelta(days=8)).strftime("%d.%m.%Y, ganztags"), "link": "",
            "audience": ["Gabriel", "Lena"], "participants": [], "comments": [],
        },
        {
            "id": 3, "author": "Gabriel", "titel": "Feierabend-Bier",
            "text": "Kurzfristig: heute 18:30 in der Altstadt. Spontan vorbeikommen.",
            "wann": heute.strftime("%d.%m.%Y, 18:30"), "link": "",
            "audience": ["Anna", "Marco", "Sophie"], "participants": ["Marco"],
            "comments": [("Marco", "Bin um 18:45 da.")],
        },
    ]


# ------------------------------------------------------------
# Session-State
# ------------------------------------------------------------
if "users" not in st.session_state:
    st.session_state.users = seed_users()
if "posts" not in st.session_state:
    st.session_state.posts = seed_posts()
if "next_post_id" not in st.session_state:
    st.session_state.next_post_id = 4

users = st.session_state.users
all_names = list(users.keys())


# ------------------------------------------------------------
# Hilfsfunktionen
# ------------------------------------------------------------
def status_badge(status):
    css = "bl-badge-open" if status == STATUS_OFFEN else "bl-badge-quiet"
    return f"<span class='bl-badge {css}'>{html.escape(status)}</span>"


def pills(items):
    return "".join(f"<span class='bl-pill'>{html.escape(i)}</span>" for i in items)


# ------------------------------------------------------------
# Sidebar: Identität + Verfügbarkeit
# ------------------------------------------------------------
with st.sidebar:
    st.caption("Angemeldet als (Mock)")
    current = st.selectbox("Profil", all_names, index=0, label_visibility="collapsed")
    status_neu = st.radio(
        "Verfügbarkeit",
        [STATUS_OFFEN, STATUS_RUHE],
        index=0 if users[current]["status"] == STATUS_OFFEN else 1,
        key=f"status_{current}",
        help="Im Ruhemodus signalisierst du, dass du aktuell keine Gesellschaft suchst.",
    )
    users[current]["status"] = status_neu
    st.markdown(status_badge(status_neu), unsafe_allow_html=True)
    st.divider()
    st.caption("Interaktives Mock-up. Der Zustand wird pro Session gehalten.")


# ------------------------------------------------------------
# Hero
# ------------------------------------------------------------
uri = logo_data_uri()
logo_img = f'<img src="{uri}" class="bl-hero-logo" alt="Bucket-List Logo"/>' if uri else ""
st.markdown(
    f'<div class="bl-hero">{logo_img}'
    f'<div><div class="bl-hero-title">Bucket-List</div>'
    f'<div class="bl-hero-sub">Freizeit teilen mit Freunden und Familie</div></div></div>',
    unsafe_allow_html=True,
)

tab_feed, tab_profil, tab_freunde, tab_neu = st.tabs(
    ["Feed", "Mein Profil", "Freunde & Matches", "Neuer Post"]
)


# ------------------------------------------------------------
# Tab: Feed
# ------------------------------------------------------------
with tab_feed:
    st.subheader("Aktivitäten")

    sichtbar = [
        p for p in st.session_state.posts
        if current == p["author"] or current in p["audience"]
    ]
    if not sichtbar:
        st.info("Keine sichtbaren Posts für dieses Profil.")

    for p in sorted(sichtbar, key=lambda x: x["id"], reverse=True):
        with st.container(border=True):
            st.markdown(
                f"<div class='bl-card-head'>"
                f"<span class='bl-title'>{html.escape(p['titel'])}</span>"
                f"<div class='bl-meta'>von {html.escape(p['author'])} · {html.escape(p['wann'])}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
            st.write(p["text"])
            if p["link"]:
                st.write(f"Link: {p['link']}")

            teilnehmer = p["participants"]
            st.markdown(
                f"**Dabei ({len(teilnehmer)}):** "
                + (pills(teilnehmer) if teilnehmer else "noch niemand"),
                unsafe_allow_html=True,
            )

            ist_autor = current == p["author"]
            ist_dabei = current in teilnehmer

            if not ist_autor:
                if not ist_dabei:
                    if st.button("Ich bin dabei!", key=f"join_{p['id']}", type="primary"):
                        p["participants"].append(current)
                        st.rerun()
                else:
                    if st.button("Doch nicht mehr", key=f"leave_{p['id']}"):
                        p["participants"].remove(current)
                        st.rerun()

            darf_kommentieren = ist_autor or ist_dabei
            with st.expander(f"Absprache / Kommentare ({len(p['comments'])})"):
                if p["comments"]:
                    for autor, txt in p["comments"]:
                        st.markdown(f"**{html.escape(autor)}:** {html.escape(txt)}")
                else:
                    st.caption("Noch keine Kommentare.")

                if darf_kommentieren:
                    with st.form(key=f"cform_{p['id']}", clear_on_submit=True):
                        kommentar = st.text_input("Kommentar", key=f"cinput_{p['id']}")
                        gesendet = st.form_submit_button("Senden")
                    if gesendet and kommentar.strip():
                        p["comments"].append((current, kommentar.strip()))
                        st.rerun()
                else:
                    st.caption(
                        'Kommentare sind den Teilnehmenden vorbehalten. '
                        'Klicke "Ich bin dabei!", um mitzureden.'
                    )


# ------------------------------------------------------------
# Tab: Mein Profil
# ------------------------------------------------------------
with tab_profil:
    st.subheader(f"Profil von {current}")
    st.caption(
        "Eigene Einträge lassen sich in jeder Liste direkt eintippen und mit Enter bestätigen."
    )

    st.markdown("#### Vorlieben")
    aktuelle = set(users[current]["vorlieben"])
    neue_vorlieben = set()
    for kategorie, optionen in VORLIEBEN.items():
        gewaehlt = st.multiselect(
            kategorie,
            options=sorted(set(optionen) | aktuelle),
            default=[v for v in (set(optionen) | aktuelle) if v in aktuelle],
            accept_new_options=True,
            placeholder="auswählen oder Eigenes eintippen",
            key=f"vl_{current}_{kategorie}",
        )
        neue_vorlieben.update(gewaehlt)
    users[current]["vorlieben"] = neue_vorlieben

    st.markdown("#### Equipment zum Teilen")
    akt_eq = set(users[current]["equipment"])
    neues_equipment = st.multiselect(
        "Equipment",
        options=sorted(set(EQUIPMENT) | akt_eq),
        default=[e for e in (set(EQUIPMENT) | akt_eq) if e in akt_eq],
        accept_new_options=True,
        placeholder="auswählen oder Eigenes eintippen",
        key=f"eq_{current}",
        label_visibility="collapsed",
    )
    users[current]["equipment"] = set(neues_equipment)


# ------------------------------------------------------------
# Tab: Freunde & Matches
# ------------------------------------------------------------
with tab_freunde:
    st.subheader("Freunde & Matches")
    st.caption(f"Gemeinsamkeiten zwischen dir ({current}) und deinem Netzwerk.")

    meine = users[current]["vorlieben"]
    for name in all_names:
        if name == current:
            continue
        with st.container(border=True):
            st.markdown(
                f"<div class='bl-card-head'>"
                f"<span class='bl-title'>{html.escape(name)}</span> &nbsp; {status_badge(users[name]['status'])}"
                f"</div>",
                unsafe_allow_html=True,
            )
            gemeinsame = sorted(meine & users[name]["vorlieben"])
            if gemeinsame:
                st.markdown(
                    "**Gemeinsame Vorlieben:** " + pills(gemeinsame), unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='bl-suggest'>Vorschlag: gemeinsam "
                    f"<b>{html.escape(gemeinsame[0])}</b> unternehmen.</div>",
                    unsafe_allow_html=True,
                )
            else:
                st.write("Noch keine gemeinsamen Vorlieben.")

            eq = sorted(users[name]["equipment"])
            if eq:
                st.markdown("**Teilt:** " + pills(eq), unsafe_allow_html=True)


# ------------------------------------------------------------
# Tab: Neuer Post
# ------------------------------------------------------------
with tab_neu:
    st.subheader("Neuen Aktivitäts-Post erstellen")
    andere = [n for n in all_names if n != current]

    with st.form(key="neuer_post", clear_on_submit=True):
        titel = st.text_input("Titel der Aktivität")
        text = st.text_area("Beschreibung")
        wann = st.text_input("Wann (z.B. Sa, 14.06.2026, 10:00)")
        link = st.text_input("Link (optional)")
        audience = st.multiselect("Wer soll den Post sehen?", andere, default=andere)
        absenden = st.form_submit_button("Post veröffentlichen", type="primary")

    if absenden:
        if not titel.strip():
            st.warning("Bitte einen Titel angeben.")
        elif not audience:
            st.warning("Bitte mindestens eine Person auswählen.")
        else:
            st.session_state.posts.append({
                "id": st.session_state.next_post_id,
                "author": current,
                "titel": titel.strip(),
                "text": text.strip(),
                "wann": wann.strip() or "noch offen",
                "link": link.strip(),
                "audience": audience,
                "participants": [],
                "comments": [],
            })
            st.session_state.next_post_id += 1
            st.success("Post veröffentlicht. Sichtbar im Feed der ausgewählten Personen.")
