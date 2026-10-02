#!/usr/bin/env python3
"""Build the Commons Home Services site.

    python3 build.py        -> writes every *.html page and sitemap.xml next to this file

Content lives in CONFIG / SERVICES / FAQS below; markup lives in the page functions.
Edit content here, rebuild, never hand-edit the generated .html files.
No prices anywhere on the site (standing rule 2026-09-29).
"""
import json
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).parent

CONFIG = {
    "site_url": "https://commonshomeservices.com",
    "phone": "(650) 203-4266",
    "tel": "+16502034266",
    "email": "commonshomeservices@gmail.com",
    # Free key from web3forms.com, issued to the business Gmail. Empty = booking form
    # tells the customer to call or text instead (it never pretends to have sent).
    "web3forms_key": "7eeca234-f80f-404b-94c5-455190755da7",
    # Google reviews link (https://search.google.com/local/reviews?placeid=...),
    # available once the Business Profile is verified.
    "reviews_url": "",
    "booking_hours": [8, 18],  # first and last hour offered in the time picker, 24h
}

# Service area, Will 2026-10-02. AREA is the only place the wording lives; TOWNS feeds the
# marquee, town list, footer and schema areaServed.
AREA = "San Jose to Marin"
TOWNS = ["San Jose", "Santa Clara", "Sunnyvale", "Cupertino", "Mountain View", "Los Altos",
         "Los Altos Hills", "Palo Alto", "Menlo Park", "Atherton", "Portola Valley", "Woodside",
         "Redwood City", "San Carlos", "Belmont", "San Mateo", "Hillsborough", "Burlingame",
         "Millbrae", "San Bruno", "South San Francisco", "Daly City", "San Francisco", "Sausalito",
         "Mill Valley", "Tiburon", "Corte Madera", "Larkspur", "San Rafael"]

DONT_SENTENCE = ("Plumbing, electrical, roofing, HVAC, demolition, tree work off the ground, "
                 "asbestos or medical waste, or anything that needs a licensed contractor.")

SERVICES = [
    {
        "slug": "junk-removal", "icon": "truck", "name": "Junk Removal & Hauling",
        "short": "Furniture, mattresses, appliances, garage cleanouts and dump runs.",
        "lede": "Tell us what's going and when. A local crew does the lifting, loads the truck and hauls it away.",
        "does": ["Furniture removal", "Mattress disposal", "Appliance removal", "Garage cleanouts",
                 "Yard waste removal", "Dump runs", "One item or a full load"],
        "dont": ["Hazardous, asbestos or medical waste", "Demolition", "Dumpster drop-offs"],
        "placeholder": "Example: an old couch, two mattresses and some boxes in the garage",
        "faqs": [
            ("Do you take mattresses?", "Yes. Book a time and list how many in the job description."),
            ("Where does the junk go?", "We sort every load. Metal and appliances go to a scrap recycler in Redwood City. Furniture in good shape goes to Habitat for Humanity ReStore or Goodwill. Clean mattresses are recycled through California's Bye Bye Mattress program. The rest goes to RethinkWaste's Shoreway Environmental Center in San Carlos, where yard waste is sent on to be composted. Only what can't be reused or recycled goes to the landfill."),
            ("Can you clear out a whole garage?", "Yes. Describe what's in there when you book, and text photos to (650) 203-4266 so we can plan the crew and the truck."),
        ],
        "photos": [("truck-hauling.jpg", "Pickup truck bed full of hauled dirt", "A full load, hauled away"),
                   ("furniture-pickup.jpg", "Wooden table and bench set out for pickup", "Furniture pickup")],
    },
    {
        "slug": "yard-work", "icon": "leaf", "name": "Yard Work & Cleanup",
        "short": "Weeds, leaves, brush, mulch and yard waste. Defensible space clearing.",
        "lede": "From one overgrown corner to a full backyard, a local crew clears it and hauls the waste away.",
        "does": ["Yard cleanup", "Weed removal", "Leaf removal", "Brush clearing",
                 "Defensible space clearing", "Mulching", "Spreading gravel", "Yard waste hauled away"],
        "dont": ["Tree work off the ground", "Stump grinding", "Irrigation repair", "Landscape design"],
        "placeholder": "Example: clear the weeds and dry brush along the back fence and haul it away",
        "faqs": [
            ("What is defensible space clearing?", "Clearing dry brush, weeds and dead plants from around your home to lower fire risk. Describe your property when you book and we'll quote the job."),
            ("Do you haul the yard waste away?", "Yes. We can haul away everything we clear."),
        ],
        "photos": [("yard-before.jpg", "Overgrown backyard with dry grass and brush", "Before"),
                   ("yard-after.jpg", "Same backyard cleared to bare soil", "After"),
                   ("yard-after-2.jpg", "Cleared yard under oak trees with brush removed", "Brush and weeds cleared")],
    },
    {
        "slug": "moving-help", "icon": "box", "name": "Moving Help",
        "short": "Loading, unloading, carrying heavy furniture and assembly.",
        "lede": "Extra hands for moving day. We load, unload, carry and set up.",
        "does": ["Loading and unloading", "Carrying heavy furniture", "Moving items to storage",
                 "Furniture assembly"],
        "dont": [],
        "placeholder": "Example: load a two bedroom apartment into a rental truck",
        "faqs": [
            ("Can you help with just part of a move?", "Yes. Tell us what needs to move in the job description."),
            ("Do you assemble furniture?", "Yes. Furniture assembly is one of our services."),
        ],
        "photos": [],
    },
    {
        "slug": "gutter-cleaning", "icon": "home", "name": "Gutter Cleaning",
        "short": "Gutters and downspouts cleared on one and two story homes.",
        "lede": "Clogged gutters overflow in the first big rain. We clear them out before it gets there.",
        "does": ["Gutter cleaning", "Downspouts cleared", "Roof debris cleared", "One and two story homes"],
        "dont": ["Roof repairs", "Gutter installation or repair"],
        "placeholder": "Example: two story house, gutters on all sides",
        "faqs": [
            ("Do you clean two story homes?", "Yes."),
            ("When should gutters be cleaned?", "At least once a year for most homes, best in the fall before the rain starts."),
        ],
        "photos": [],
    },
    {
        "slug": "pressure-washing", "icon": "drop", "name": "Pressure Washing",
        "short": "Driveways, patios and walkways.",
        "lede": "We wash the grime off driveways, patios and walkways.",
        "does": ["Driveway cleaning", "Patio cleaning", "Walkway and path cleaning"],
        "dont": [],
        "placeholder": "Example: front driveway and the back patio",
        "faqs": [
            ("Do you bring the equipment?", "Yes. We bring the pressure washer."),
        ],
        "photos": [],
    },
    {
        "slug": "holiday-lights", "icon": "lights", "name": "Holiday Light Installation",
        "short": "Hung in November, taken down in January. Lights included.",
        "lede": "We hang your holiday lights in November and take them down in January. Lights included.",
        "does": ["Roofline lights", "Lights included", "Installed in November", "Taken down in January"],
        "dont": [],
        "season": "2026 season: booking now. Installs start in early November.",
        "placeholder": "Example: roofline across the front of a one story house",
        "faqs": [
            ("Do I need to buy my own lights?", "No. Lights are included."),
            ("When do you install and take down?", "Installs start in early November. We take everything down in January."),
            ("Do you do two story homes?", "Yes."),
        ],
        "photos": [],
    },
]

FAQS = [
    ("Booking and quotes", [
        ("How do I book?", "Pick a date and time on the booking form and tell us about the job. We'll text you to confirm."),
        ("How much will it cost?", "Every job is different, so we quote each one. Text a photo to (650) 203-4266 for a free quote."),
        ("Can I send photos?", "Yes. Text them to (650) 203-4266. Photos help us plan the crew and the truck."),
        ("How soon can you come out?", "Pick the date and time that works for you on the booking form. We'll text you to confirm."),
        ("Do I need to be home?", "No. Tell us how to get in when you book, like a gate code or an open garage, and we'll text you when the job is done. Our crew are local students who care about this community, take care of your property, and take pride in their work."),
        ("How do I pay?", "We take Zelle. You pay when the job is done. For junk hauls, you pay once everything is loaded on the truck."),
    ]),
    ("Our crew and area", [
        ("Who does the work?", "High school and college students from the towns we serve."),
        ("Where do you work?", f"Anywhere from {AREA}."),
    ]),
    ("Services", [
        ("What don't you do?", DONT_SENTENCE),
        ("My job isn't listed. Can you still help?", "Ask. Describe it when you book, or text us at (650) 203-4266."),
    ]),
]

ICONS = {
    "truck": '<path d="M1 4h13v11H1zM14 8h4.5L22 11.5V15h-8z"/><circle cx="5.5" cy="17.5" r="2"/><circle cx="17.5" cy="17.5" r="2"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 4 13c0-5 4-9 16-9 0 12-4 16-9 16z"/><path d="M4 20c4-6 8-9 13-11"/>',
    "box": '<path d="M21 8 12 3 3 8v8l9 5 9-5z"/><path d="m3 8 9 5 9-5M12 13v8"/>',
    "home": '<path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/><path d="M2 11h20"/>',
    "drop": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    "lights": '<path d="M2 5c5 4 15 4 20 0"/><path d="M6 7.5v2.5M12 8.5v2.5M18 7.5v2.5"/><path d="M5 12.5a1 1 0 0 0 2 0l-1-2.5zM11 13.5a1 1 0 0 0 2 0l-1-2.5zM17 12.5a1 1 0 0 0 2 0l-1-2.5z"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "x": '<path d="M18 6 6 18M6 6l12 12"/>',
    "calendar": '<rect x="3" y="4" width="18" height="17" rx="2"/><path d="M3 9h18M8 2v4M16 2v4"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "pin": '<path d="M12 22s7-6.2 7-12a7 7 0 0 0-14 0c0 5.8 7 12 7 12z"/><circle cx="12" cy="10" r="2.5"/>',
    "phone": '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/>',
    "star": '<path d="m12 2 3.1 6.3 6.9 1-5 4.9 1.2 6.8L12 17.8 5.8 21l1.2-6.8-5-4.9 6.9-1z"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "menu": '<path d="M3 6h18M3 12h18M3 18h18"/>',
}

LOGO = ('<svg class="logo-mark" viewBox="0 0 140 100" aria-hidden="true"><path d="M4 90 L4 62 L22 47 L40 62 L40 90 Z M100 90 L100 62 L118 47 L136 62 L136 90 Z" fill="#3A4763"/>'
        '<path d="M34 44 L70 14 L106 44 L106 84 Q106 90 100 90 L40 90 Q34 90 34 84 Z" fill="#D8D2C8" stroke="#1F2A44" stroke-width="5" stroke-linejoin="round"/>'
        '<path d="M42 47 L70 24 L98 47" fill="none" stroke="#A8683E" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round"/>'
        '<text x="70" y="83" text-anchor="middle" font-family="Bitter,Georgia,serif" font-weight="800" font-size="40" fill="#1F2A44">C</text></svg>')

HERO_SLIDES = [("truck-hauling.jpg", "Commons truck loaded with a haul"),
               ("yard-after-2.jpg", "Yard cleared under oak trees"),
               ("furniture-pickup.jpg", "Furniture set out for pickup")]

WORK = [("yard-before.jpg", "Overgrown backyard with dry grass and brush", "Yard cleanup, before"),
        ("yard-after.jpg", "Same backyard cleared to bare soil", "Yard cleanup, after"),
        ("truck-hauling.jpg", "Pickup truck bed full of hauled dirt", "A full load, hauled away"),
        ("yard-after-2.jpg", "Cleared yard under oak trees", "Brush and weeds cleared"),
        ("furniture-pickup.jpg", "Wooden table and bench set out for pickup", "Furniture pickup")]


def icon(name, cls="ico"):
    return (f'<svg class="{cls}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def book_href(page, slug=None):
    if page == "index.html":
        return "#book"
    return f"book.html?service={slug}" if slug else "book.html"


# ---------------------------------------------------------------- shared chrome

def head(title, desc, page, extra=""):
    url = CONFIG["site_url"] + ("/" if page == "index.html" else "/" + page)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<meta name="description" content="{escape(desc)}">
<link rel="canonical" href="{url}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:title" content="{escape(title)}">
<meta property="og:description" content="{escape(desc)}">
<meta property="og:image" content="{CONFIG['site_url']}/img/og.jpg">
<meta property="og:url" content="{url}">
<meta name="theme-color" content="#1F2A44">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bitter:wght@700;800&family=Manrope:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="styles.css">
<script>document.documentElement.classList.add('js');window.COMMONS={json.dumps({k: CONFIG[k] for k in ('web3forms_key', 'booking_hours', 'phone')})};</script>
<script src="site.js" defer></script>
{extra}</head>
"""


def header(page):
    svc_links = "".join(f'<a href="{s["slug"]}.html">{icon(s["icon"])}{escape(s["name"])}</a>' for s in SERVICES)
    reviews = "index.html#reviews" if page != "index.html" else "#reviews"
    return f"""<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap bar">
    <a class="brand" href="index.html" aria-label="Commons Home Services, home">{LOGO}<span class="brand-text"><b>COMMONS</b><small>Home Services</small></span></a>
    <nav class="nav" id="nav" aria-label="Main">
      <div class="nav-drop">
        <button class="nav-link" aria-expanded="false" aria-controls="svc-menu">Services <span class="caret"></span></button>
        <div class="drop-menu" id="svc-menu">{svc_links}</div>
      </div>
      <a class="nav-link" href="faq.html">FAQ</a>
      <a class="nav-link" href="{reviews}">Reviews</a>
      <a class="nav-link nav-phone" href="tel:{CONFIG['tel']}">{icon('phone')}{CONFIG['phone']}</a>
    </nav>
    <div class="bar-actions">
      <a class="btn btn-primary btn-sm" href="{book_href(page)}">Book a job</a>
      <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="nav">{icon('menu')}</button>
    </div>
  </div>
</header>
<main id="main">
"""


def footer(page):
    svc = "".join(f'<li><a href="{s["slug"]}.html">{escape(s["name"])}</a></li>' for s in SERVICES)
    reviews = "index.html#reviews" if page != "index.html" else "#reviews"
    return f"""</main>
<footer class="site-footer">
  <div class="wrap foot-grid">
    <div class="foot-brand">
      <a class="brand" href="index.html">{LOGO}<span class="brand-text"><b>COMMONS</b><small>Home Services</small></span></a>
      <p>Local crews for local homes.</p>
      <a class="btn btn-primary" href="{book_href(page)}">Book a job</a>
    </div>
    <div><h3>Services</h3><ul>{svc}</ul></div>
    <div><h3>Company</h3><ul><li><a href="book.html">Book a job</a></li><li><a href="faq.html">FAQ</a></li><li><a href="{reviews}">Reviews</a></li></ul></div>
    <div><h3>Contact</h3><ul><li><a href="tel:{CONFIG['tel']}">{CONFIG['phone']}</a></li><li><a href="sms:{CONFIG['tel']}">Text us</a></li><li><a href="mailto:{CONFIG['email']}">{CONFIG['email']}</a></li></ul></div>
  </div>
  <div class="wrap foot-towns"><span>Serving</span> {' · '.join(TOWNS)}</div>
  <div class="wrap foot-legal">© {date.today().year} Commons Home Services</div>
</footer>
<nav class="dock" aria-label="Book or call">
  <a class="btn btn-primary" href="{book_href(page)}">{icon('calendar')}Book a job</a>
  <a class="btn btn-quiet" href="tel:{CONFIG['tel']}" aria-label="Call {CONFIG['phone']}">{icon('phone')}Call</a>
</nav>
</body>
</html>
"""


# ---------------------------------------------------------------- blocks

def booking_form(slug=None, heading=True):
    svc = next((s for s in SERVICES if s["slug"] == slug), None)
    placeholder = svc["placeholder"] if svc else "Example: haul away an old couch and clear the weeds out back"
    head_html = ('<div class="form-head"><h2>Book a job</h2><p>Pick a time and tell us about the job. '
                 "We'll text you to confirm.</p></div>") if heading else ""
    return f"""<form class="book-form" novalidate>
  {head_html}
  <input type="hidden" name="service" value="{escape(svc['name']) if svc else ''}">
  <input type="checkbox" name="botcheck" class="hp" tabindex="-1" autocomplete="off" aria-hidden="true">
  <div class="row two">
    <label><span>Date</span><input type="date" name="date" required></label>
    <label><span>Time</span><select name="time" required><option value="">Select</option></select></label>
  </div>
  <label><span>What's the job?</span><textarea name="job" rows="4" required placeholder="{escape(placeholder)}"></textarea></label>
  <div class="row two">
    <label><span>Name</span><input name="name" autocomplete="name" required></label>
    <label><span>Phone</span><input type="tel" name="phone" autocomplete="tel" inputmode="tel" required></label>
  </div>
  <label><span>Address or town</span><input name="address" autocomplete="street-address" required></label>
  <button class="btn btn-primary btn-block" type="submit">{icon('calendar')}Book this time</button>
  <p class="form-note">Have photos? Text them to <a href="sms:{CONFIG['tel']}">{CONFIG['phone']}</a>.</p>
  <div class="form-status" role="status" aria-live="polite"></div>
</form>"""


def steps():
    items = [("calendar", "Book a time", "Pick a date and time and describe the job. It takes about a minute."),
             ("chat", "We confirm by text", "We text you to confirm the time and talk through the job."),
             ("users", "A local crew shows up", "Students from your area do the work.")]
    li = "".join(f'<li class="reveal">{icon(i)}<span class="step-n">{n}</span><h3>{t}</h3><p>{d}</p></li>'
                 for n, (i, t, d) in enumerate(items, 1))
    return f'<ol class="steps">{li}</ol>'


def carousel(items, label):
    slides = "".join(f'<figure class="slide"><img src="img/{f}" alt="{escape(a)}" loading="lazy" width="1200" height="628"><figcaption>{escape(c)}</figcaption></figure>'
                     for f, a, c in items)
    return f"""<div class="carousel reveal" data-count="{len(items)}" aria-roledescription="carousel" aria-label="{escape(label)}">
  <div class="track" tabindex="0">{slides}</div>
  <div class="car-ctrl">
    <button class="car-btn prev" aria-label="Previous photo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg></button>
    <div class="dots" aria-hidden="true"></div>
    <button class="car-btn next" aria-label="Next photo"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M9 6l6 6-6 6"/></svg></button>
  </div>
</div>"""


def faq_list(pairs):
    return '<div class="faq">' + "".join(
        f'<details class="reveal"><summary>{escape(q)}<span class="plus"></span></summary><p>{escape(a)}</p></details>'
        for q, a in pairs) + "</div>"


def reviews_block():
    url = CONFIG["reviews_url"]
    btn = (f'<a class="btn btn-outline" href="{url}" target="_blank" rel="noopener">{icon("star")}Read our Google reviews</a>'
           if url else f'<a class="btn btn-outline" href="#reviews" data-pending="reviews">{icon("star")}Read our Google reviews</a>')
    return f"""<section class="reviews" id="reviews">
  <div class="wrap reviews-inner reveal">
    <div class="r-badge">{icon('star')}</div>
    <div><h2>Reviews</h2><p>See what neighbors say about Commons on Google.</p></div>
    {btn}
  </div>
</section>"""


def cta_band(page, slug=None, title="Book your job"):
    return f"""<section class="cta-band">
  <div class="wrap cta-inner reveal">
    <div><h2>{title}</h2><p>Pick a date and time. We'll text you to confirm.</p></div>
    <div class="cta-actions">
      <a class="btn btn-primary btn-lg" href="{book_href(page, slug)}">{icon('calendar')}Book a job</a>
      <a class="cta-phone" href="tel:{CONFIG['tel']}">or call {CONFIG['phone']}</a>
    </div>
  </div>
</section>"""


def towns_marquee():
    row = "".join(f"<span>{t}</span>" for t in TOWNS)
    return f'<div class="marquee" aria-hidden="true"><div class="marquee-track">{row}{row}</div></div>'


def schema():
    data = {
        "@context": "https://schema.org", "@type": "HomeAndConstructionBusiness",
        "name": "Commons Home Services", "slogan": "Local crews for local homes.",
        "url": CONFIG["site_url"] + "/", "image": CONFIG["site_url"] + "/img/og.jpg",
        "telephone": "+1-650-203-4266", "email": CONFIG["email"],
        "areaServed": [f"{t}, CA" for t in TOWNS],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Services", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": s["name"],
                                                 "url": f"{CONFIG['site_url']}/{s['slug']}.html"}}
            for s in SERVICES]},
    }
    return f'<script type="application/ld+json">{json.dumps(data)}</script>\n'


# ---------------------------------------------------------------- pages

def page_home():
    p = "index.html"
    slides = "".join(f'<img src="img/{f}" alt="" class="{"on" if i == 0 else ""}">' for i, (f, _) in enumerate(HERO_SLIDES))
    cards = "".join(f"""<a class="svc-card reveal" href="{s['slug']}.html">
      <span class="svc-ico">{icon(s['icon'])}</span><h3>{escape(s['name'])}</h3><p>{escape(s['short'])}</p>
      <span class="more">Learn more {icon('arrow','arr')}</span></a>""" for s in SERVICES)
    trust = [("calendar", "Book online"), ("chat", "Free quotes"), ("users", "Students from your community"), ("pin", AREA)]
    trust_html = "".join(f"<li>{icon(i)}<span>{t}</span></li>" for i, t in trust)
    home_faq = [q for _, group in FAQS for q in group][:4]
    body = f"""
<section class="hero">
  <div class="hero-bg" aria-hidden="true">{slides}</div>
  <div class="wrap hero-grid">
    <div class="hero-copy">
      <p class="eyebrow">Local crews for local homes.</p>
      <h1>Junk removal, yard work and moving help on the Peninsula</h1>
      <p class="lede">Commons Home Services is a crew of high school and college students from your community. Pick a time, tell us the job, and we'll handle the rest.</p>
      <div class="hero-actions">
        <a class="btn btn-primary btn-lg" href="#book">{icon('calendar')}Book a job</a>
        <a class="btn btn-ghost btn-lg" href="tel:{CONFIG['tel']}">{icon('phone')}{CONFIG['phone']}</a>
      </div>
    </div>
    <div class="hero-form" id="book">{booking_form()}</div>
  </div>
</section>
<section class="trust"><ul class="wrap trust-list">{trust_html}</ul></section>

<section class="sec">
  <div class="wrap">
    <div class="sec-head reveal"><p class="eyebrow">Services</p><h2>What we do</h2></div>
    <div class="svc-grid">{cards}</div>
    <p class="dont-line reveal"><strong>We don't do:</strong> {DONT_SENTENCE[0].lower() + DONT_SENTENCE[1:]}</p>
  </div>
</section>

<section class="sec sec-alt">
  <div class="wrap">
    <div class="sec-head reveal"><p class="eyebrow">How it works</p><h2>Booked in a minute</h2></div>
    {steps()}
    <div class="center reveal"><a class="btn btn-primary btn-lg" href="#book">{icon('calendar')}Book a job</a></div>
  </div>
</section>

<section class="sec">
  <div class="wrap">
    <div class="sec-head reveal"><p class="eyebrow">Recent work</p><h2>Jobs around the Peninsula</h2></div>
    {carousel(WORK, "Recent work")}
  </div>
</section>

<section class="sec about">
  <div class="wrap about-grid">
    <div class="reveal"><p class="eyebrow">Who we are</p><h2>Your neighbors, with a truck</h2></div>
    <div class="reveal">
      <p>Commons Home Services is a group of high school and college students from your community, here to help with hauling, yard work, moving help, gutters, pressure washing and holiday lights.</p>
      <p>It started with Will, a Foothill College student paying his own way through school, doing weekend yard work in Woodside.</p>
    </div>
  </div>
</section>

<section class="area">
  <div class="wrap sec-head reveal"><p class="eyebrow">Where we work</p><h2>{AREA}</h2></div>
  {towns_marquee()}
  <ul class="wrap town-list">{''.join(f'<li>{icon("pin")}{t}</li>' for t in TOWNS)}</ul>
</section>

<section class="sec sec-alt">
  <div class="wrap faq-wrap">
    <div class="sec-head reveal"><p class="eyebrow">FAQ</p><h2>Common questions</h2><a class="link-arrow" href="faq.html">All questions {icon('arrow','arr')}</a></div>
    {faq_list(home_faq)}
  </div>
</section>

{cta_band(p)}
{reviews_block()}
"""
    title = "Commons Home Services | Junk Removal, Yard Work & Moving Help on the Peninsula"
    desc = ("Book junk removal, hauling, yard cleanup, moving help, gutter cleaning, pressure washing and holiday "
            f"lights from {AREA}. Local student crews. Free quotes.")
    return head(title, desc, p, schema()) + header(p) + body + footer(p)


def page_service(s):
    p = f"{s['slug']}.html"
    does = "".join(f'<li>{icon("check")}{escape(d)}</li>' for d in s["does"])
    dont = ("<div class=\"dont-box reveal\"><h3>Not part of this service</h3><ul>"
            + "".join(f'<li>{icon("x")}{escape(d)}</li>' for d in s["dont"]) + "</ul></div>") if s["dont"] else ""
    season = f'<p class="season reveal">{icon("calendar")}{escape(s["season"])}</p>' if s.get("season") else ""
    photos = (f'<section class="sec"><div class="wrap"><div class="sec-head reveal"><p class="eyebrow">Recent work</p>'
              f'<h2>{escape(s["name"])} jobs</h2></div>{carousel(s["photos"], s["name"] + " photos")}</div></section>') if s["photos"] else ""
    others = "".join(f'<a href="{o["slug"]}.html">{icon(o["icon"])}{escape(o["name"])}</a>' for o in SERVICES if o is not s)
    body = f"""
<section class="page-hero">
  <div class="wrap page-hero-grid">
    <div class="reveal">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><span>Services</span><span>/</span><span>{escape(s['name'])}</span></nav>
      <h1>{escape(s['name'])} on the Peninsula</h1>
      <p class="lede">{escape(s['lede'])}</p>
      {season}
      <div class="hero-actions">
        <a class="btn btn-primary btn-lg" href="{book_href(p, s['slug'])}">{icon('calendar')}Book a job</a>
        <a class="btn btn-ghost btn-lg" href="sms:{CONFIG['tel']}">{icon('chat')}Text a photo</a>
      </div>
    </div>
    <div class="page-hero-ico reveal">{icon(s['icon'], 'big-ico')}</div>
  </div>
</section>

<section class="sec">
  <div class="wrap incl-grid">
    <div class="reveal"><p class="eyebrow">What's included</p><h2>What we do</h2><ul class="checks">{does}</ul></div>
    {dont}
  </div>
</section>
{photos}
<section class="sec sec-alt">
  <div class="wrap">
    <div class="sec-head reveal"><p class="eyebrow">How it works</p><h2>Booked in a minute</h2></div>
    {steps()}
  </div>
</section>

<section class="sec">
  <div class="wrap faq-wrap">
    <div class="sec-head reveal"><p class="eyebrow">FAQ</p><h2>{escape(s['name'])} questions</h2><a class="link-arrow" href="faq.html">All questions {icon('arrow','arr')}</a></div>
    {faq_list(s['faqs'])}
  </div>
</section>

{cta_band(p, s['slug'])}
<section class="sec other-svc"><div class="wrap"><h2 class="reveal">Other services</h2><div class="other-grid reveal">{others}</div></div></section>
"""
    title = f"{s['name']} in Woodside, Palo Alto & Redwood City | Commons Home Services"
    desc = f"{s['short']} Local student crews from {AREA}. Book online or call {CONFIG['phone']}."
    return head(title, desc, p) + header(p) + body + footer(p)


def page_book():
    p = "book.html"
    body = f"""
<section class="page-hero book-hero">
  <div class="wrap book-grid">
    <div class="reveal">
      <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><span>Book a job</span></nav>
      <h1>Book a job</h1>
      <p class="lede">Pick a date and time and tell us about the job. We'll text you to confirm.</p>
      <ul class="book-points">
        <li>{icon('chat')}<span><b>Free quotes.</b> Text a photo to {CONFIG['phone']} and we'll quote the job.</span></li>
        <li>{icon('users')}<span><b>Local crews.</b> High school and college students from the towns we serve.</span></li>
        <li>{icon('pin')}<span><b>{AREA}.</b> {len(TOWNS)} towns.</span></li>
      </ul>
      <p class="book-call">Rather talk? Call or text <a href="tel:{CONFIG['tel']}">{CONFIG['phone']}</a>.</p>
    </div>
    <div class="hero-form reveal">{booking_form(heading=False)}</div>
  </div>
</section>
"""
    return head("Book a Job | Commons Home Services", "Book junk removal, yard work, moving help, gutter cleaning, pressure washing or holiday lights. Pick a date and time online.", p) + header(p) + body + footer(p)


def page_faq():
    p = "faq.html"
    groups = "".join(f'<div class="faq-group"><h2 class="reveal">{escape(g)}</h2>{faq_list(pairs)}</div>' for g, pairs in FAQS)
    svc_groups = "".join(f'<div class="faq-group"><h2 class="reveal">{escape(s["name"])}</h2>{faq_list(s["faqs"])}</div>' for s in SERVICES)
    data = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}}
        for _, pairs in FAQS for q, a in pairs]}
    body = f"""
<section class="page-hero">
  <div class="wrap reveal">
    <nav class="crumbs" aria-label="Breadcrumb"><a href="index.html">Home</a><span>/</span><span>FAQ</span></nav>
    <h1>Frequently asked questions</h1>
    <p class="lede">Don't see your question? Call or text <a href="tel:{CONFIG['tel']}">{CONFIG['phone']}</a>.</p>
  </div>
</section>
<section class="sec"><div class="wrap faq-page">{groups}{svc_groups}</div></section>
{cta_band(p)}
"""
    extra = f'<script type="application/ld+json">{json.dumps(data)}</script>\n'
    return head("FAQ | Commons Home Services", "Answers about booking, quotes, our student crews, service area and each service.", p, extra) + header(p) + body + footer(p)


def main():
    pages = {"index.html": page_home(), "book.html": page_book(), "faq.html": page_faq()}
    pages.update({f"{s['slug']}.html": page_service(s) for s in SERVICES})
    for name, html in pages.items():
        (ROOT / name).write_text(html)
    urls = "".join(f"<url><loc>{CONFIG['site_url']}/{'' if n == 'index.html' else n}</loc></url>" for n in pages)
    (ROOT / "sitemap.xml").write_text(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {CONFIG['site_url']}/sitemap.xml\n")
    print(f"built {len(pages)} pages + sitemap.xml")
    for key, why in (("web3forms_key", "booking form can't send; it tells customers to call or text instead"),
                     ("reviews_url", "Google reviews button points nowhere until the Business Profile is verified")):
        if not CONFIG[key]:
            print(f"WARNING: CONFIG['{key}'] is empty: {why}")


if __name__ == "__main__":
    main()
