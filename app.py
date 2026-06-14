# ============================================================
# Bucket-List - interaktives Mock-up (Streamlit Community Cloud)
#
# Demonstriert das MVP-Konzept "Relationale Freizeitplattform":
#   - Profil mit Vorlieben je Kategorie
#   - Equipment zum Teilen
#   - Matching-Vorschlaege (gemeinsame Vorlieben)
#   - Aktivitaets-Posts mit Zielgruppenauswahl
#   - "Ich bin dabei!" und Kommentare (nur fuer Teilnehmende)
#   - Ruhemodus / Verfuegbarkeitsstatus
#
# Hinweis: Reines Mock-up. Der Zustand liegt in st.session_state
# und wird je Session zurueckgesetzt (keine persistente Datenbank).
# ============================================================

from datetime import datetime, timedelta

import streamlit as st

st.set_page_config(page_title="Bucket-List - Mock-up", layout="wide")

# ------------------------------------------------------------
# Stammdaten / Kataloge
# ------------------------------------------------------------
VORLIEBEN = {
    "Sport": ["Padel", "Fussball", "Laufen", "Velo fahren", "Klettern", "Yoga", "Tennis"],
    "Kultur": ["Museen", "Konzerte", "Kino", "Theater", "Lesungen"],
    "Kulinarik": ["Restaurants", "Gemeinsam Kochen", "Kaffee trinken", "Feierabend-Bier", "Brunch"],
    "Ausfluege": ["Stadtrundgang", "Wandern", "Velotour", "Badi / See"],
    "Adventure": ["Klettersteig", "Kajak / SUP", "Bergtour", "Ski-Tour"],
    "Kids": ["Spielplatz", "Basteln", "Zoo", "Schwimmbad"],
    "Spiel & Spass": ["Tischtennis", "Brettspiele", "Jassen", "Boule"],
    "Events": ["Konzerte (Open Air)", "Festivals", "Food-Festivals", "Maerkte"],
}

EQUIPMENT = [
    "Segelboot (Bareboat)", "Segelschein", "Auto", "Velo / E-Bike",
    "SUP-Board", "Zelt", "Pizzaofen", "Gesellschaftsspiele", "Leinwand / Beamer",
    "Kanu", "Raclette-Ofen", "Festbank-Garnitur",
]

STATUS_OFFEN = "Offen fuer Aktivitaeten"
STATUS_RUHE = "Ruhemodus"


# ------------------------------------------------------------
# Seed-Daten
# ------------------------------------------------------------
def seed_users():
    return {
        "Gabriel": {
            "vorlieben": {"Padel", "Velo fahren", "Wandern", "Feierabend-Bier", "Jassen", "Restaurants"},
            "equipment": {"Velo / E-Bike", "Pizzaofen", "Gesellschaftsspiele"},
            "status": STATUS_OFFEN,
        },
        "Anna": {
            "vorlieben": {"Padel", "Yoga", "Brunch", "Konzerte (Open Air)", "Wandern"},
            "equipment": {"Auto", "Zelt", "SUP-Board"},
            "status": STATUS_OFFEN,
        },
        "Marco": {
            "vorlieben": {"Fussball", "Feierabend-Bier", "Jassen", "Velo fahren", "Restaurants"},
            "equipment": {"Segelboot (Bareboat)", "Segelschein", "Leinwand / Beamer"},
            "status": STATUS_RUHE,
        },
        "Lena": {
            "vorlieben": {"Klettern", "Kajak / SUP", "Bergtour", "Kaffee trinken", "Festivals"},
            "equipment": {"Kanu", "Auto"},
            "status": STATUS_OFFEN,
        },
        "Sophie": {
            "vorlieben": {"Museen", "Kino", "Brunch", "Wandern", "Restaurants"},
            "equipment": {"Raclette-Ofen", "Gesellschaftsspiele"},
            "status": STATUS_OFFEN,
        },
    }


def seed_posts():
    heute = datetime.now()
    return [
        {
            "id": 1,
            "author": "Anna",
            "titel": "Padel am Samstagvormittag",
            "text": "Court in Bern fuer Samstag 10:00 reserviert. Zwei Plaetze frei.",
            "wann": (heute + timedelta(days=2)).strftime("%d.%m.%Y, 10:00"),
            "link": "",
            "audience": ["Gabriel", "Marco", "Lena", "Sophie"],
            "participants": ["Gabriel"],
            "comments": [("Gabriel", "Bin dabei. Soll ich Baelle mitbringen?")],
        },
        {
            "id": 2,
            "author": "Marco",
            "titel": "Segeltoern Bielersee",
            "text": "Naechstes Wochenende mit dem Boot raus. Segelschein nicht noetig.",
            "wann": (heute + timedelta(days=8)).strftime("%d.%m.%Y, ganztags"),
            "link": "",
            "audience": ["Gabriel", "Lena"],
            "participants": [],
            "comments": [],
        },
        {
            "id": 3,
            "author": "Gabriel",
            "titel": "Feierabend-Bier",
            "text": "Kurzfristig: heute 18:30 in der Altstadt. Spontan vorbeikommen.",
            "wann": heute.strftime("%d.%m.%Y, 18:30"),
            "link": "",
            "audience": ["Anna", "Marco", "Sophie"],
            "participants": ["Marco"],
            "comments": [("Marco", "Bin um 18:45 da.")],
        },
    ]


# ------------------------------------------------------------
# Session-State initialisieren
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
# Kopf / "Login"-Simulation
# ------------------------------------------------------------
st.title("Bucket-List")
st.caption("Interaktives Mock-up - Freizeitgestaltung mit Freunden und Familie")

kopf_links, kopf_rechts = st.columns([2, 3])
with kopf_links:
    current = st.selectbox("Angemeldet als (Mock)", all_names, index=0)
with kopf_rechts:
    st.write("")
    st.write(f"Aktueller Status: **{users[current]['status']}**")

st.divider()

tab_feed, tab_profil, tab_freunde, tab_neu = st.tabs(
    ["Feed", "Mein Profil", "Freunde & Matches", "Neuer Post"]
)


# ------------------------------------------------------------
# Tab: Feed
# ------------------------------------------------------------
with tab_feed:
    st.subheader("Aktivitaeten")

    sichtbar = [
        p for p in st.session_state.posts
        if current == p["author"] or current in p["audience"]
    ]

    if not sichtbar:
        st.info("Keine sichtbaren Posts fuer dieses Profil.")

    for p in sorted(sichtbar, key=lambda x: x["id"], reverse=True):
        with st.container(border=True):
            st.markdown(f"### {p['titel']}")
            st.caption(f"von {p['author']} - {p['wann']}")
            st.write(p["text"])
            if p["link"]:
                st.write(f"Link: {p['link']}")

            teilnehmer = p["participants"]
            st.write(
                f"**Dabei ({len(teilnehmer)}):** "
                + (", ".join(teilnehmer) if teilnehmer else "noch niemand")
            )

            ist_autor = current == p["author"]
            ist_dabei = current in teilnehmer

            if not ist_autor:
                if not ist_dabei:
                    if st.button("Ich bin dabei!", key=f"join_{p['id']}"):
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
                        st.markdown(f"**{autor}:** {txt}")
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

    status_neu = st.radio(
        "Verfuegbarkeit",
        [STATUS_OFFEN, STATUS_RUHE],
        index=0 if users[current]["status"] == STATUS_OFFEN else 1,
        horizontal=True,
        key=f"status_{current}",
        help="Im Ruhemodus signalisierst du, dass du aktuell keine Gesellschaft suchst.",
    )
    users[current]["status"] = status_neu

    st.markdown("#### Vorlieben")
    st.caption("Interessen je Kategorie waehlen. Andere sehen, worauf du Lust hast.")

    aktuelle_vorlieben = set(users[current]["vorlieben"])
    neue_vorlieben = set()
    for kategorie, optionen in VORLIEBEN.items():
        gewaehlt = st.multiselect(
            kategorie,
            optionen,
            default=[v for v in optionen if v in aktuelle_vorlieben],
            key=f"vl_{current}_{kategorie}",
        )
        neue_vorlieben.update(gewaehlt)
    users[current]["vorlieben"] = neue_vorlieben

    st.markdown("#### Equipment zum Teilen")
    st.caption("Was kannst du teilen? So sehen alle, welche Moeglichkeiten bestehen.")
    neues_equipment = st.multiselect(
        "Equipment",
        EQUIPMENT,
        default=[e for e in EQUIPMENT if e in users[current]["equipment"]],
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

    meine_vorlieben = users[current]["vorlieben"]
    for name in all_names:
        if name == current:
            continue
        with st.container(border=True):
            st.markdown(f"### {name}")
            st.caption(f"Status: {users[name]['status']}")

            gemeinsame = sorted(meine_vorlieben & users[name]["vorlieben"])
            if gemeinsame:
                st.write("**Gemeinsame Vorlieben:** " + ", ".join(gemeinsame))
                st.info(f"Vorschlag: gemeinsam **{gemeinsame[0]}** unternehmen.")
            else:
                st.write("Noch keine gemeinsamen Vorlieben.")

            eq = sorted(users[name]["equipment"])
            if eq:
                st.write("**Teilt:** " + ", ".join(eq))


# ------------------------------------------------------------
# Tab: Neuer Post
# ------------------------------------------------------------
with tab_neu:
    st.subheader("Neuen Aktivitaets-Post erstellen")
    andere = [n for n in all_names if n != current]

    with st.form(key="neuer_post", clear_on_submit=True):
        titel = st.text_input("Titel der Aktivitaet")
        text = st.text_area("Beschreibung")
        wann = st.text_input("Wann (z.B. Sa, 14.06.2026, 10:00)")
        link = st.text_input("Link (optional)")
        audience = st.multiselect("Wer soll den Post sehen?", andere, default=andere)
        absenden = st.form_submit_button("Post veroeffentlichen")

    if absenden:
        if not titel.strip():
            st.warning("Bitte einen Titel angeben.")
        elif not audience:
            st.warning("Bitte mindestens eine Person auswaehlen.")
        else:
            st.session_state.posts.append(
                {
                    "id": st.session_state.next_post_id,
                    "author": current,
                    "titel": titel.strip(),
                    "text": text.strip(),
                    "wann": wann.strip() or "noch offen",
                    "link": link.strip(),
                    "audience": audience,
                    "participants": [],
                    "comments": [],
                }
            )
            st.session_state.next_post_id += 1
            st.success("Post veroeffentlicht. Sichtbar im Feed der ausgewaehlten Personen.")
