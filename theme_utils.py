"""
Theme utilities, SVG Icon system, and Plotly theme adapter
for McDonald's Review Sentiment Intelligence System (2026 UI/UX Design System).
"""

THEMES = {
    "Light": {
        "bg": "#F8FAFC",
        "surface": "#FFFFFF",
        "surface_elevated": "#FFFFFF",
        "text_primary": "#0F172A",
        "text_secondary": "#475569",
        "text_muted": "#64748B",
        "border": "#E2E8F0",
        "border_hover": "#6366F1",
        "accent": "#4F46E5",
        "accent_bg": "#EEF2FF",
        "accent_hover": "#4338CA",
        "positive": "#10B981",
        "positive_bg": "#ECFDF5",
        "positive_border": "#A7F3D0",
        "neutral": "#F59E0B",
        "neutral_bg": "#FFFBEB",
        "neutral_border": "#FDE68A",
        "negative": "#E11D48",
        "negative_bg": "#FEF2F2",
        "negative_border": "#FECACA",
        "grid": "#E2E8F0",
        "shadow": "0 4px 20px rgba(15, 23, 42, 0.05)",
        "shadow_hover": "0 10px 25px rgba(79, 70, 229, 0.12)"
    },
    "Dark": {
        "bg": "#0B0F19",
        "surface": "#111827",
        "surface_elevated": "#1F2937",
        "text_primary": "#F9FAFB",
        "text_secondary": "#D1D5DB",
        "text_muted": "#9CA3AF",
        "border": "#1F2937",
        "border_hover": "#818CF8",
        "accent": "#818CF8",
        "accent_bg": "#1E1B4B",
        "accent_hover": "#A5B4FC",
        "positive": "#34D399",
        "positive_bg": "#064E3B",
        "positive_border": "#059669",
        "neutral": "#FBBF24",
        "neutral_bg": "#78350F",
        "neutral_border": "#D97706",
        "negative": "#F87171",
        "negative_bg": "#7F1D1D",
        "negative_border": "#DC2626",
        "grid": "#1F2937",
        "shadow": "0 4px 20px rgba(0, 0, 0, 0.4)",
        "shadow_hover": "0 10px 25px rgba(129, 140, 248, 0.2)"
    },
    "Soft": {
        "bg": "#F1F5F9",
        "surface": "#E2E8F0",
        "surface_elevated": "#CBD5E1",
        "text_primary": "#1E293B",
        "text_secondary": "#334155",
        "text_muted": "#475569",
        "border": "#CBD5E1",
        "border_hover": "#2563EB",
        "accent": "#2563EB",
        "accent_bg": "#DBEAFE",
        "accent_hover": "#1D4ED8",
        "positive": "#059669",
        "positive_bg": "#D1FAE5",
        "positive_border": "#6EE7B7",
        "neutral": "#D97706",
        "neutral_bg": "#FEF3C7",
        "neutral_border": "#FCD34D",
        "negative": "#DC2626",
        "negative_bg": "#FEE2E2",
        "negative_border": "#FCA5A5",
        "grid": "#CBD5E1",
        "shadow": "0 4px 15px rgba(100, 116, 139, 0.08)",
        "shadow_hover": "0 10px 20px rgba(37, 99, 235, 0.12)"
    }
}

SVG_ICONS = {
    "overview": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/></svg>',
    "predictor": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "analytics": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "explorer": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/></svg>',
    "performance": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
    "reports": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>',
    "info": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>',
    "positive": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>',
    "neutral": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="8" y1="12" x2="16" y2="12"/></svg>',
    "negative": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "search": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "calendar": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>',
    "filter": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></svg>',
    "download": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>',
    "check": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "trash": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/></svg>',
    "sun": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>',
    "moon": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>',
    "cloud": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/></svg>',
    "star": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>',
    "store": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    "shield": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "refresh": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>',
    "list": '<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>'
}

def get_svg_icon(name: str, size: int = 18, color: str = "currentColor") -> str:
    """Return inline SVG string for the requested icon name."""
    tmpl = SVG_ICONS.get(name, SVG_ICONS["info"])
    return tmpl.format(size=size, color=color)

def get_chart_theme(theme_name: str = "Light") -> dict:
    """Return unified Plotly theme configuration guaranteeing high contrast and readability."""
    t = THEMES.get(theme_name, THEMES["Light"])
    return {
        "paper_bgcolor": t["surface"],
        "plot_bgcolor": t["surface"],
        "font": {
            "family": "Plus Jakarta Sans, sans-serif",
            "color": t["text_primary"],
            "size": 12
        },
        "xaxis": {
            "showgrid": True,
            "gridcolor": t["grid"],
            "zerolinecolor": t["grid"],
            "tickfont": {"color": t["text_secondary"], "size": 11},
            "titlefont": {"color": t["text_primary"], "size": 12, "weight": "bold"}
        },
        "yaxis": {
            "showgrid": True,
            "gridcolor": t["grid"],
            "zerolinecolor": t["grid"],
            "tickfont": {"color": t["text_secondary"], "size": 11},
            "titlefont": {"color": t["text_primary"], "size": 12, "weight": "bold"}
        },
        "legend": {
            "font": {"color": t["text_primary"], "size": 11},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "rgba(0,0,0,0)"
        },
        "hoverlabel": {
            "bgcolor": t["surface_elevated"],
            "font": {"color": t["text_primary"], "size": 12, "family": "Plus Jakarta Sans, sans-serif"},
            "bordercolor": t["border"]
        },
        "margin": {"t": 35, "b": 35, "l": 35, "r": 35}
    }

def get_custom_css(theme_name: str = "Light") -> str:
    """Generate dynamic CSS tokens and rules according to active theme."""
    t = THEMES.get(theme_name, THEMES["Light"])
    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {{
        --bg: {t["bg"]};
        --surface: {t["surface"]};
        --surface-elevated: {t["surface_elevated"]};
        --text-primary: {t["text_primary"]};
        --text-secondary: {t["text_secondary"]};
        --text-muted: {t["text_muted"]};
        --border: {t["border"]};
        --border-hover: {t["border_hover"]};
        --accent: {t["accent"]};
        --accent-bg: {t["accent_bg"]};
        --accent-hover: {t["accent_hover"]};
        --positive: {t["positive"]};
        --positive-bg: {t["positive_bg"]};
        --positive-border: {t["positive_border"]};
        --neutral: {t["neutral"]};
        --neutral-bg: {t["neutral_bg"]};
        --neutral-border: {t["neutral_border"]};
        --negative: {t["negative"]};
        --negative-bg: {t["negative_bg"]};
        --negative-border: {t["negative_border"]};
        --grid: {t["grid"]};
        --shadow: {t["shadow"]};
        --shadow-hover: {t["shadow_hover"]};
    }}

    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    .stApp {{
        background-color: var(--bg) !important;
        color: var(--text-primary) !important;
    }}

    #MainMenu, footer, .stDeployButton {{ display: none !important; }}

    /* Sidebar Theme Override */
    [data-testid="stSidebar"], section[data-testid="stSidebar"] {{
        background-color: var(--surface) !important;
        border-right: 1px solid var(--border) !important;
    }}
    [data-testid="stSidebarContent"] {{
        background-color: var(--surface) !important;
        padding: 1.25rem 1rem !important;
    }}
    [data-testid="stSidebar"] * {{
        color: var(--text-primary) !important;
    }}
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {{
        color: var(--text-primary) !important;
        font-weight: 800 !important;
    }}

    /* Modern Card Container */
    .card-2026 {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 20px 24px !important;
        box-shadow: var(--shadow) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    .card-2026:hover {{
        transform: translateY(-2px);
        border-color: var(--border-hover) !important;
        box-shadow: var(--shadow-hover) !important;
    }}

    /* KPI Cards with 3D Elevation */
    .kpi-card-2026 {{
        background-color: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        position: relative !important;
        overflow: hidden !important;
        box-shadow: var(--shadow) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}
    .kpi-card-2026:hover {{
        transform: translateY(-3px) scale(1.01);
        border-color: var(--accent) !important;
        box-shadow: var(--shadow-hover) !important;
    }}
    .kpi-icon-badge {{
        width: 40px;
        height: 40px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: var(--accent-bg);
        color: var(--accent);
        margin-bottom: 12px;
    }}
    .kpi-label {{
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-muted);
    }}
    .kpi-value {{
        font-size: 2rem;
        font-weight: 800;
        color: var(--text-primary);
        line-height: 1.15;
        margin: 4px 0;
    }}
    .kpi-desc {{
        font-size: 0.8rem;
        color: var(--text-secondary);
        font-weight: 500;
    }}

    /* Sentiment Breakdown Badge Cards */
    .sent-card-pos {{
        background-color: var(--positive-bg) !important;
        border: 1px solid var(--positive-border) !important;
        color: var(--text-primary) !important;
        border-radius: 16px;
        padding: 18px 20px;
        transition: transform 0.2s ease;
    }}
    .sent-card-neu {{
        background-color: var(--neutral-bg) !important;
        border: 1px solid var(--neutral-border) !important;
        color: var(--text-primary) !important;
        border-radius: 16px;
        padding: 18px 20px;
        transition: transform 0.2s ease;
    }}
    .sent-card-neg {{
        background-color: var(--negative-bg) !important;
        border: 1px solid var(--negative-border) !important;
        color: var(--text-primary) !important;
        border-radius: 16px;
        padding: 18px 20px;
        transition: transform 0.2s ease;
    }}
    .sent-card-pos:hover, .sent-card-neu:hover, .sent-card-neg:hover {{
        transform: translateY(-2px);
    }}

    /* Progress Bar */
    .progress-bar-bg {{
        width: 100%;
        height: 6px;
        background-color: rgba(0,0,0,0.08);
        border-radius: 999px;
        overflow: hidden;
        margin-top: 8px;
    }}
    .progress-bar-fill {{
        height: 100%;
        border-radius: 999px;
    }}

    /* Input & Form Control Styling */
    div[data-testid="stTextArea"] textarea, div[data-baseweb="input"] input {{
        background-color: var(--bg) !important;
        color: var(--text-primary) !important;
        border: 1.5px solid var(--border) !important;
        border-radius: 10px !important;
    }}
    div[data-testid="stTextArea"] textarea:focus, div[data-baseweb="input"] input:focus {{
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-bg) !important;
    }}
    div[data-baseweb="select"] > div {{
        background-color: var(--bg) !important;
        border: 1.5px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
    }}

    /* Streamlit Button Overrides */
    .stButton>button {{
        border-radius: 10px !important;
        font-weight: 700 !important;
        border: 1px solid var(--border) !important;
        background-color: var(--surface) !important;
        color: var(--text-primary) !important;
        transition: all 0.2s ease !important;
    }}
    .stButton>button:hover {{
        border-color: var(--accent) !important;
        background-color: var(--accent-bg) !important;
        color: var(--accent) !important;
    }}
    
    /* Filter Chip Badges */
    .filter-chip {{
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background-color: var(--accent-bg);
        color: var(--accent);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 4px 10px;
        font-size: 0.78rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }}

    /* Dataframe Overrides */
    [data-testid="stDataFrame"] {{
        background-color: var(--surface) !important;
        border-radius: 12px !important;
        border: 1px solid var(--border) !important;
    }}
</style>
"""
