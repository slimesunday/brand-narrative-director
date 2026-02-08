"""
Brand Narrative Director — Streamlit Intake & Generation App
A multi-step wizard that collects brand data, scrapes publicly available info,
generates narrative concepts via LLM, and outputs pipeline-ready storyboards.
"""

import streamlit as st
import json
import os
import re
import time
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_SCRAPING = True
except ImportError:
    HAS_SCRAPING = False

# ---------------------------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Brand Narrative Director",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# CUSTOM CSS — Dark, editorial, high-end creative tool aesthetic
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,700;1,9..40,300;1,9..40,400&family=Space+Mono:wght@400;700&display=swap');

    /* Global */
    .stApp {
        background-color: #0a0a0a;
        color: #e0e0e0;
        font-family: 'DM Sans', sans-serif;
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Step indicator */
    .step-indicator {
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        color: #555;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-bottom: 0.25rem;
    }
    .step-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.25rem;
        line-height: 1.1;
    }
    .step-subtitle {
        font-family: 'DM Sans', sans-serif;
        font-size: 1rem;
        color: #888;
        margin-bottom: 2rem;
        font-weight: 300;
    }

    /* Progress bar */
    .progress-container {
        display: flex;
        gap: 6px;
        margin-bottom: 2.5rem;
    }
    .progress-segment {
        height: 3px;
        flex: 1;
        background: #1a1a1a;
        border-radius: 2px;
        transition: background 0.3s ease;
    }
    .progress-segment.active {
        background: #ffffff;
    }
    .progress-segment.completed {
        background: #444;
    }

    /* Input styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #111 !important;
        border: 1px solid #222 !important;
        color: #e0e0e0 !important;
        font-family: 'DM Sans', sans-serif !important;
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #555 !important;
        box-shadow: none !important;
    }
    .stTextInput > label, .stTextArea > label, .stSelectbox > label, .stMultiSelect > label {
        color: #aaa !important;
        font-family: 'DM Sans', sans-serif !important;
        font-size: 0.85rem !important;
        font-weight: 400 !important;
    }

    /* Selectbox */
    .stSelectbox > div > div {
        background-color: #111 !important;
        border: 1px solid #222 !important;
        border-radius: 8px !important;
    }

    /* Slider styling */
    .stSlider > div > div > div {
        background-color: #333 !important;
    }
    .stSlider label {
        color: #aaa !important;
        font-size: 0.85rem !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #ffffff !important;
        color: #000000 !important;
        border: none !important;
        border-radius: 8px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 500 !important;
        padding: 0.6rem 2rem !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background-color: #e0e0e0 !important;
        transform: translateY(-1px) !important;
    }

    /* Secondary / back button */
    .back-btn > button {
        background-color: transparent !important;
        color: #666 !important;
        border: 1px solid #333 !important;
    }
    .back-btn > button:hover {
        color: #fff !important;
        border-color: #555 !important;
        background-color: transparent !important;
    }

    /* Cards for visual picker */
    .visual-card {
        background: #111;
        border: 2px solid #222;
        border-radius: 12px;
        padding: 16px;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: center;
        min-height: 160px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .visual-card:hover {
        border-color: #444;
    }
    .visual-card.selected {
        border-color: #fff;
        background: #1a1a1a;
    }
    .visual-card-emoji {
        font-size: 2.5rem;
        margin-bottom: 8px;
    }
    .visual-card-label {
        font-size: 0.8rem;
        color: #999;
        font-weight: 400;
    }

    /* Spectrum labels */
    .spectrum-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: -10px;
    }
    .spectrum-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.7rem;
        color: #666;
        letter-spacing: 0.05em;
        text-transform: uppercase;
    }

    /* Narrative cards */
    .narrative-card {
        background: linear-gradient(145deg, #111, #0d0d0d);
        border: 1px solid #222;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.2s ease;
    }
    .narrative-card:hover {
        border-color: #444;
    }
    .narrative-card h3 {
        color: #fff;
        font-size: 1.2rem;
        margin-bottom: 8px;
    }
    .narrative-card .insight {
        color: #888;
        font-size: 0.85rem;
        font-style: italic;
        margin-bottom: 12px;
    }
    .narrative-card .arc {
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        color: #555;
        letter-spacing: 0.05em;
    }

    /* Divider */
    .custom-divider {
        border: none;
        border-top: 1px solid #1a1a1a;
        margin: 2rem 0;
    }

    /* Info boxes */
    .info-box {
        background: #111;
        border-left: 3px solid #333;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.85rem;
        color: #888;
    }

    /* Scraped data preview */
    .scraped-preview {
        background: #0d0d0d;
        border: 1px solid #1a1a1a;
        border-radius: 12px;
        padding: 20px;
        margin: 1rem 0;
    }
    .scraped-label {
        font-family: 'Space Mono', monospace;
        font-size: 0.65rem;
        color: #444;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-bottom: 4px;
    }
    .scraped-value {
        color: #ccc;
        font-size: 0.9rem;
        margin-bottom: 16px;
    }

    /* Loading animation */
    .generating {
        text-align: center;
        padding: 3rem;
    }
    .generating-text {
        font-family: 'Space Mono', monospace;
        font-size: 0.85rem;
        color: #555;
        letter-spacing: 0.1em;
        animation: pulse 1.5s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 1; }
    }

    /* JSON output */
    .json-output {
        background: #0d0d0d;
        border: 1px solid #1a1a1a;
        border-radius: 12px;
        padding: 20px;
        font-family: 'Space Mono', monospace;
        font-size: 0.75rem;
        color: #666;
        overflow-x: auto;
        white-space: pre-wrap;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #111 !important;
        border-radius: 8px !important;
        color: #aaa !important;
    }

    /* Multiselect */
    .stMultiSelect > div > div {
        background-color: #111 !important;
        border: 1px solid #222 !important;
        border-radius: 8px !important;
    }
    span[data-baseweb="tag"] {
        background-color: #222 !important;
    }

    /* Tab styling for output */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #111;
        border-radius: 8px;
        color: #888;
        border: 1px solid #222;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1a1a1a;
        color: #fff;
        border-color: #444;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# SESSION STATE INIT
# ---------------------------------------------------------------------------
DEFAULTS = {
    "current_step": 1,
    "return_to_review": False,
    "auto_filled": False,
    # LLM Settings
    "llm_provider": "Anthropic",
    "llm_model": "claude-sonnet-4-20250514",
    "api_key": "",
    "api_key_set": False,
    # Brand data
    "brand_name": "",
    "brand_url": "",
    "brand_category": "",
    "brand_description": "",
    "scraped_data": None,
    "scrape_attempted": False,
    "audience_lifestyle": "",
    "audience_brands": "",
    "audience_platform": "Instagram Reels",
    "personality_exclusive_accessible": 50,
    "personality_serious_playful": 50,
    "personality_minimal_expressive": 50,
    "personality_classic_trendy": 50,
    "personality_loud_quiet": 50,
    "personality_luxury_everyday": 50,
    "emotion_feel_after": "",
    "emotion_reject": "",
    "emotion_movie_scene": "",
    "visual_selections": [],
    "color_primary": "#000000",
    "color_secondary": "#ffffff",
    "color_accent": "#ff0000",
    "product_in_frame": "Ambient — worn/used naturally, never the focus",
    "text_overlay_pref": "Tagline at end only",
    "audio_direction": "",
    "generated_narratives": None,
    "selected_narrative": None,
    "generated_storyboard": None,
    "brand_profile_json": None,
}

# ---------------------------------------------------------------------------
# LLM PROVIDER CONFIGURATIONS
# ---------------------------------------------------------------------------
LLM_PROVIDERS = {
    "Anthropic": {
        "models": [
            ("Claude Opus 4.6", "claude-opus-4-6"),
            ("Claude Opus 4.5", "claude-opus-4-5-20250929"),
            ("Claude Sonnet 4.5", "claude-sonnet-4-5-20250929"),
            ("Claude Sonnet 4", "claude-sonnet-4-20250514"),
            ("Claude Haiku 4.5", "claude-haiku-4-5-20251001"),
        ],
        "key_prefix": "sk-ant-",
        "key_placeholder": "sk-ant-api03-...",
        "docs_url": "https://console.anthropic.com/settings/keys",
    },
    "OpenAI": {
        "models": [
            ("GPT-5.2", "gpt-5.2"),
            ("GPT-5.1", "gpt-5.1"),
            ("GPT-5", "gpt-5"),
            ("GPT-4.1", "gpt-4.1"),
            ("GPT-4.1 mini", "gpt-4.1-mini"),
            ("GPT-4.1 nano", "gpt-4.1-nano"),
            ("o3", "o3"),
            ("o4-mini", "o4-mini"),
        ],
        "key_prefix": "sk-",
        "key_placeholder": "sk-proj-...",
        "docs_url": "https://platform.openai.com/api-keys",
    },
    "Google": {
        "models": [
            ("Gemini 2.5 Pro", "gemini-2.5-pro"),
            ("Gemini 2.5 Flash", "gemini-2.5-flash"),
            ("Gemini 2.0 Flash", "gemini-2.0-flash"),
        ],
        "key_prefix": "AI",
        "key_placeholder": "AIzaSy...",
        "docs_url": "https://aistudio.google.com/apikey",
    },
}

for key, val in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = val

TOTAL_STEPS = 7  # Identity, Audience, Personality, Emotion, Visual, Review, Generate


# ---------------------------------------------------------------------------
# HELPER: LLM INTEGRATION (Multi-provider)
# ---------------------------------------------------------------------------
def call_llm(system_prompt: str, user_message: str, max_tokens: int = 4096) -> str:
    """Route LLM calls to the selected provider and model."""
    provider = st.session_state.get("llm_provider", "Anthropic")
    model = st.session_state.get("llm_model", "claude-sonnet-4-20250514")
    api_key = st.session_state.get("api_key", "")

    if not api_key:
        return "__LLM_UNAVAILABLE__: No API key configured. Open the sidebar (⚙️) to add your key."

    try:
        if provider == "Anthropic":
            return _call_anthropic(system_prompt, user_message, model, api_key, max_tokens)
        elif provider == "OpenAI":
            return _call_openai(system_prompt, user_message, model, api_key, max_tokens)
        elif provider == "Google":
            return _call_google(system_prompt, user_message, model, api_key, max_tokens)
        else:
            return f"__LLM_ERROR__: Unknown provider {provider}"
    except Exception as e:
        return f"__LLM_ERROR__: {str(e)}"


def _call_anthropic(system_prompt: str, user_message: str, model: str, api_key: str, max_tokens: int) -> str:
    """Call Anthropic Claude API."""
    try:
        import anthropic
    except ImportError:
        return "__LLM_ERROR__: `anthropic` package not installed. Run: pip install anthropic"

    client = anthropic.Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return response.content[0].text


def _call_openai(system_prompt: str, user_message: str, model: str, api_key: str, max_tokens: int) -> str:
    """Call OpenAI API (GPT-4.x, GPT-5.x, and o-series)."""
    try:
        import openai
    except ImportError:
        return "__LLM_ERROR__: `openai` package not installed. Run: pip install openai"

    client = openai.OpenAI(api_key=api_key)

    # GPT-5.x and o-series are reasoning models
    is_reasoning = model.startswith("o") or model.startswith("gpt-5")

    if is_reasoning:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "developer", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            reasoning_effort="high",              # bare string for Chat Completions API
            max_completion_tokens=max_tokens,     # NOT max_tokens — reasoning models reject it
        )
    else:
        # GPT-4.x and older non-reasoning models
        response = client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
    return response.choices[0].message.content


def _call_google(system_prompt: str, user_message: str, model: str, api_key: str, max_tokens: int) -> str:
    """Call Google Gemini API."""
    try:
        from google import genai
    except ImportError:
        return "__LLM_ERROR__: `google-genai` package not installed. Run: pip install google-genai"

    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model,
        contents=user_message,
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            max_output_tokens=max_tokens,
        ),
    )
    return response.text


def _fetch_website_text(url: str, max_chars: int = 8000) -> str:
    """Fetch and extract readable text from a URL."""
    if not HAS_SCRAPING or not url:
        return ""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove script, style, nav, footer noise
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "iframe"]):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        # Collapse multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text[:max_chars]
    except Exception:
        return ""


def _try_fetch_about_page(base_url: str) -> str:
    """Try to find and fetch an about/story page for richer brand info."""
    if not HAS_SCRAPING or not base_url:
        return ""
    about_paths = ["/pages/about", "/about", "/pages/story", "/story", "/our-story", "/about-us"]
    base = base_url.rstrip("/")
    for path in about_paths:
        try:
            text = _fetch_website_text(f"{base}{path}", max_chars=4000)
            if len(text) > 200:  # Only return if we got meaningful content
                return text
        except Exception:
            continue
    return ""


def _parse_json_response(text: str) -> dict | list | None:
    """Parse JSON from an LLM response — matches the proven Synth.Human pattern."""
    if not text:
        return None

    json_str = text.strip()

    # Strip markdown code fences (the main culprit with OpenAI models)
    if "```json" in json_str:
        json_str = json_str.split("```json")[1].split("```")[0]
    elif "```" in json_str:
        json_str = json_str.split("```")[1].split("```")[0]

    json_str = json_str.strip()

    # Try direct parse
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        pass

    # Try extracting JSON object or array
    for pattern in [r'\{[\s\S]*\}', r'\[[\s\S]*\]']:
        try:
            match = re.search(pattern, json_str)
            if match:
                return json.loads(match.group())
        except json.JSONDecodeError:
            continue

    # Try fixing trailing commas
    try:
        fixed = re.sub(r',\s*([}\]])', r'\1', json_str)
        return json.loads(fixed)
    except json.JSONDecodeError:
        pass

    return None


def scrape_brand_info(brand_name: str, url: str, category: str) -> dict:
    """Research a brand by scraping its website and using LLM to structure the data."""

    # --- Step 1: Try to scrape real website content ---
    site_text = ""
    about_text = ""
    if url:
        site_text = _fetch_website_text(url)
        about_text = _try_fetch_about_page(url)

    has_site_content = len(site_text) > 100

    # --- Step 2: Build the LLM prompt based on what we have ---
    system = """You are a brand research analyst. Your job is to produce a structured brand profile.
Return ONLY a valid JSON object — no markdown fences, no commentary, no preamble. Just the raw JSON.
The JSON must have exactly these fields:
{
    "tagline": "brand tagline or slogan if found, empty string if unknown",
    "ethos": "1-2 sentence brand mission/ethos",
    "values": ["value1", "value2", "value3"],
    "anti_positioning": "what the brand explicitly is NOT or avoids being",
    "emotional_territory": "the core feeling/emotion the brand owns",
    "audience_description": "psychographic description of typical customer",
    "aesthetic_description": "visual style, color tendencies, design language",
    "price_tier": "budget / accessible / mid-range / premium / luxury",
    "notable_info": "any other relevant brand context",
    "confidence": "high / medium / low"
}
CRITICAL: Return ONLY the JSON object. No other text before or after it."""

    if has_site_content:
        user_msg = f"""Analyze this brand and produce a structured profile.

Brand: {brand_name}
Website: {url}
Category: {category}

=== HOMEPAGE CONTENT ===
{site_text[:5000]}

=== ABOUT PAGE CONTENT ===
{about_text[:3000] if about_text else 'Not found'}

Use the website content above as your primary source. Extract the tagline, values, aesthetic, and audience from what you can see. Set confidence to 'high' if the site gave you clear brand signals, 'medium' if partial."""
    else:
        user_msg = f"""Analyze this brand and produce a structured profile based on your knowledge.

Brand: {brand_name}
Website: {url}
Category: {category}

If you know this brand, provide detailed information. If you don't recognize it, set confidence to 'low' and make reasonable inferences based on the category and name."""

    result = call_llm(system, user_msg, max_tokens=1024)

    if result.startswith("__LLM_"):
        return None

    parsed = _parse_json_response(result)
    return parsed


def auto_fill_all_fields(brand_name: str, url: str, category: str, scraped_data: dict = None) -> dict:
    """Use LLM to auto-fill every wizard field based on brand research."""

    # Gather site content if available
    site_text = ""
    about_text = ""
    if url:
        site_text = _fetch_website_text(url)
        about_text = _try_fetch_about_page(url)

    scraped_context = ""
    if scraped_data:
        scraped_context = f"\n=== PREVIOUSLY SCRAPED BRAND DATA ===\n{json.dumps(scraped_data, indent=2)}"

    site_context = ""
    if len(site_text) > 100:
        site_context = f"\n=== HOMEPAGE CONTENT ===\n{site_text[:5000]}"
        if about_text:
            site_context += f"\n=== ABOUT PAGE CONTENT ===\n{about_text[:3000]}"

    system = """You are an expert brand strategist and creative director. Given a brand, you will fill out a complete creative brief for a 10-12 second brand messaging video.

Return ONLY a valid JSON object — no markdown fences, no commentary, no preamble. Just the raw JSON.

The JSON must have EXACTLY these fields:
{
    "brand_description": "1-2 sentence description of the brand — what they make and their vibe",
    "tagline": "brand tagline or slogan, empty string if unknown",
    "ethos": "1-2 sentence brand mission/ethos",
    "values": ["value1", "value2", "value3"],
    "anti_positioning": "what the brand explicitly is NOT or avoids being",
    "emotional_territory": "the core feeling/emotion the brand owns",
    "audience_description": "psychographic description of typical customer — lifestyle, not demographics",
    "aesthetic_description": "visual style, color tendencies, design language",
    "price_tier": "budget / accessible / mid-range / premium / luxury",
    "audience_lifestyle": "2-3 sentence psychographic portrait of the ideal customer — what they care about, how they discover brands, their relationship with the product category",
    "adjacent_brands": "3-5 brands the customer also loves, comma-separated",
    "platform": "Instagram Reels or TikTok or YouTube Shorts",
    "personality_exclusive_accessible": 50,
    "personality_serious_playful": 50,
    "personality_minimal_expressive": 50,
    "personality_classic_trendy": 50,
    "personality_loud_quiet": 50,
    "personality_luxury_everyday": 50,
    "emotion_feel_after": "2-3 sentences describing how someone should feel after watching the video — be specific and evocative, not generic",
    "emotion_reject": "1-2 sentences describing the feelings/vibes the brand explicitly rejects",
    "emotion_movie_scene": "A specific movie scene description — if this brand were a moment in a film, what would be happening? Be concrete and visual, not abstract",
    "visual_styles": ["id1", "id2"],
    "color_primary": "#hexcode",
    "color_secondary": "#hexcode",
    "color_accent": "#hexcode",
    "product_presence": "None — no product visible at all | Ambient — worn/used naturally, never the focus | Visible — clearly present but story-first",
    "text_overlay": "None — visuals only | Tagline at end only | Minimal text throughout (3-7 words max per overlay) | Text-heavy / typographic style",
    "audio_direction": "genre, mood, voiceover preference — be specific",
    "confidence": "high / medium / low"
}

PERSONALITY SLIDERS: Each is 0-100 where 0 is the first trait and 100 is the second trait. 
- exclusive_accessible: 0=very exclusive, 100=very accessible
- serious_playful: 0=very serious, 100=very playful
- minimal_expressive: 0=very minimal, 100=very expressive
- classic_trendy: 0=very classic, 100=very trendy
- loud_quiet: 0=very loud, 100=very quiet
- luxury_everyday: 0=very luxury, 100=very everyday

VISUAL STYLES: Pick 2-4 from: cinematic, documentary, editorial, surreal, lofi, minimal, maximalist, vintage, neon, organic, graphic, luxe

COLOR PALETTE: Extract actual brand colors from the website content if possible. Use hex codes.

PRODUCT PRESENCE: Pick exactly one of the three options listed.
TEXT OVERLAY: Pick exactly one of the four options listed.

MOVIE SCENE: This is the most important creative field. Be SPECIFIC and CINEMATIC — describe a concrete scene with setting, action, characters, mood. Not abstract feelings, but what you'd actually SEE on screen.

CRITICAL: Return ONLY the JSON object. No other text before or after it."""

    user_msg = f"""Fill out a complete creative brief for this brand:

Brand: {brand_name}
Website: {url}
Category: {category}
{scraped_context}
{site_context}

Be specific, creative, and insightful. Avoid generic filler. Every field should feel like it was written by someone who deeply understands this brand."""

    result = call_llm(system, user_msg, max_tokens=3000)

    if result.startswith("__LLM_"):
        return None

    parsed = _parse_json_response(result)
    return parsed


def apply_auto_fill(data: dict):
    """Apply auto-filled data to session state."""
    if not data:
        return

    # Brand identity
    if data.get("brand_description"):
        st.session_state.brand_description = data["brand_description"]

    # Store scraped-style data
    st.session_state.scraped_data = {
        "tagline": data.get("tagline", ""),
        "ethos": data.get("ethos", ""),
        "values": data.get("values", []),
        "anti_positioning": data.get("anti_positioning", ""),
        "emotional_territory": data.get("emotional_territory", ""),
        "audience_description": data.get("audience_description", ""),
        "aesthetic_description": data.get("aesthetic_description", ""),
        "price_tier": data.get("price_tier", ""),
        "confidence": data.get("confidence", "medium"),
    }

    # Audience
    if data.get("audience_lifestyle"):
        st.session_state.audience_lifestyle = data["audience_lifestyle"]
    if data.get("adjacent_brands"):
        st.session_state.audience_brands = data["adjacent_brands"]
    if data.get("platform"):
        st.session_state.audience_platform = data["platform"]

    # Personality sliders
    for key in ["personality_exclusive_accessible", "personality_serious_playful",
                "personality_minimal_expressive", "personality_classic_trendy",
                "personality_loud_quiet", "personality_luxury_everyday"]:
        if key in data and isinstance(data[key], (int, float)):
            st.session_state[key] = max(0, min(100, int(data[key])))

    # Emotional territory
    if data.get("emotion_feel_after"):
        st.session_state.emotion_feel_after = data["emotion_feel_after"]
    if data.get("emotion_reject"):
        st.session_state.emotion_reject = data["emotion_reject"]
    if data.get("emotion_movie_scene"):
        st.session_state.emotion_movie_scene = data["emotion_movie_scene"]

    # Visual direction
    if data.get("visual_styles") and isinstance(data["visual_styles"], list):
        valid_ids = [s["id"] for s in VISUAL_STYLES]
        st.session_state.visual_selections = [v for v in data["visual_styles"] if v in valid_ids]
    if data.get("color_primary"):
        st.session_state.color_primary = data["color_primary"]
    if data.get("color_secondary"):
        st.session_state.color_secondary = data["color_secondary"]
    if data.get("color_accent"):
        st.session_state.color_accent = data["color_accent"]

    # Production
    if data.get("product_presence"):
        for opt in PRODUCT_PRESENCE_OPTIONS:
            if data["product_presence"].lower() in opt.lower():
                st.session_state.product_in_frame = opt
                break
    if data.get("text_overlay"):
        for opt in TEXT_OVERLAY_OPTIONS:
            if data["text_overlay"].lower() in opt.lower():
                st.session_state.text_overlay_pref = opt
                break
    if data.get("audio_direction"):
        st.session_state.audio_direction = data["audio_direction"]

    st.session_state.auto_filled = True
    st.session_state.scrape_attempted = True


def generate_narrative_concepts(brand_profile: dict) -> str:
    """Generate narrative concepts using the full system prompt."""
    # Load the system prompt
    system_prompt_path = os.path.join(os.path.dirname(__file__), "brand_narrative_system_prompt.md")
    if os.path.exists(system_prompt_path):
        with open(system_prompt_path, "r") as f:
            system_prompt = f.read()
    else:
        # Fallback: use embedded core principles
        system_prompt = """You are a world-class creative director specializing in short-form brand messaging video narratives.
Follow the Hook → Shift → Payoff micro-narrative structure. Start with a human truth / tension, not a brand message.
The brand is never the hero. Content must pass the 'would someone share this without the brand?' test.
Push past generic first ideas. Specificity beats beauty. Tension beats tone."""

    user_msg = f"""Based on the following brand profile, generate exactly 3 narrative concepts for a 10-12 second brand messaging video.

BRAND PROFILE:
{json.dumps(brand_profile, indent=2)}

For each concept, provide:
1. CONCEPT TITLE — a working creative title
2. HUMAN TRUTH — the tension/insight driving the narrative (use the formula: "[Audience] are motivated by [X], but they experience [Y], creating a tension that [concept] resolves")
3. ONE-LINE SUMMARY — what literally HAPPENS in the video in one sentence
4. EMOTIONAL ARC — [Starting emotion] → [Shift] → [Resolution]
5. HOOK DESCRIPTION — what the viewer sees/hears in the first 2 seconds
6. WHY IT WORKS — 1-2 sentences on why this specific concept is right for this specific brand

Return ONLY a raw JSON array (no markdown code fences, no ```json```, no preamble, no explanation). Just the [ ... ] array.
Each object must have keys: title, human_truth, summary, emotional_arc, hook, rationale

CRITICAL: Do NOT generate generic concepts. No golden hour montages. No slow-motion smiling. No 'beautiful people doing beautiful things.' Each concept must have a specific, surprising, narratively coherent idea that could ONLY work for this brand."""

    return call_llm(system_prompt, user_msg, max_tokens=3000)


def generate_full_storyboard(brand_profile: dict, selected_concept: dict) -> str:
    """Generate complete storyboard with keyframe and animation prompts."""
    system_prompt_path = os.path.join(os.path.dirname(__file__), "brand_narrative_system_prompt.md")
    if os.path.exists(system_prompt_path):
        with open(system_prompt_path, "r") as f:
            system_prompt = f.read()
    else:
        system_prompt = "You are a world-class creative director for short-form brand video."

    # Add explicit JSON formatting instructions to the system prompt
    system_prompt += """

CRITICAL OUTPUT RULES:
- Return ONLY a valid JSON object. No markdown code fences. No commentary before or after.
- Do NOT wrap the response in ```json``` blocks.
- The response must start with { and end with }
- All string values must use double quotes and escape internal quotes properly."""

    user_msg = f"""Generate a COMPLETE storyboard for this brand and selected narrative concept.

BRAND PROFILE:
{json.dumps(brand_profile, indent=2)}

SELECTED NARRATIVE CONCEPT:
{json.dumps(selected_concept, indent=2)}

Produce a storyboard with:
- 5 detailed keyframes with timestamps, scene descriptions, camera, lighting, color, emotion, composition
- A style suffix for image generation consistency
- 5 complete image generation prompts
- 4 animation/transition prompts
- Anti-generic audit results
- Creative director notes

Return ONLY a raw JSON object (no markdown, no code fences, no preamble) with these keys:
{{
  "style_suffix": "persistent style string for all keyframes",
  "keyframes": [
    {{
      "timestamp": "0s",
      "narrative_beat": "HOOK",
      "scene_description": "...",
      "camera": "...",
      "lighting": "...",
      "color_palette": "...",
      "emotion": "...",
      "text_overlay": "none",
      "product_presence": "...",
      "composition_notes": "..."
    }}
  ],
  "image_prompts": ["prompt 1", "prompt 2", "prompt 3", "prompt 4", "prompt 5"],
  "animation_prompts": [
    {{
      "transition": "1→2",
      "motion_type": "...",
      "camera_motion": "...",
      "subject_motion": "...",
      "pacing": "...",
      "visual_transition": "...",
      "emotional_trajectory": "...",
      "audio_cue": "..."
    }}
  ],
  "anti_generic_audit": {{"all_passed": true, "notes": "..."}},
  "creative_director_notes": "..."
}}"""

    return call_llm(system_prompt, user_msg, max_tokens=8000)


# ---------------------------------------------------------------------------
# HELPER: Progress bar
# ---------------------------------------------------------------------------
def render_progress():
    step = st.session_state.current_step
    segments = ""
    for i in range(1, TOTAL_STEPS + 1):
        if i < step:
            cls = "completed"
        elif i == step:
            cls = "active"
        else:
            cls = ""
        segments += f'<div class="progress-segment {cls}"></div>'
    st.markdown(f'<div class="progress-container">{segments}</div>', unsafe_allow_html=True)


def render_step_header(step_num: int, title: str, subtitle: str):
    step_labels = {
        1: "BRAND IDENTITY",
        2: "AUDIENCE",
        3: "BRAND PERSONALITY",
        4: "EMOTIONAL TERRITORY",
        5: "VISUAL DIRECTION",
        6: "REVIEW PROFILE",
        7: "NARRATIVE CONCEPTS",
    }
    st.markdown(f'<div class="step-indicator">STEP {step_num} OF {TOTAL_STEPS} — {step_labels.get(step_num, "")}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="step-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="step-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def nav_buttons(back=True, next_label="Continue", next_disabled=False):
    """Render navigation buttons. Shows 'Back to Review' when editing from review."""
    is_editing = st.session_state.return_to_review

    if is_editing:
        # Editing mode: show Back to Review instead of normal nav
        cols = st.columns([1, 1, 3])
        with cols[0]:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button("← Back", key=f"back_{st.session_state.current_step}", use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with cols[1]:
            if st.button("✓ Back to Review", key=f"review_{st.session_state.current_step}", use_container_width=True):
                st.session_state.current_step = 6
                st.session_state.return_to_review = False
                st.rerun()
    elif back:
        cols = st.columns([1, 1, 3])
        with cols[0]:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button("← Back", key=f"back_{st.session_state.current_step}", use_container_width=True):
                st.session_state.current_step -= 1
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with cols[1]:
            if st.button(next_label, key=f"next_{st.session_state.current_step}", disabled=next_disabled, use_container_width=True):
                st.session_state.current_step += 1
                st.rerun()
    else:
        cols = st.columns([1, 4])
        with cols[0]:
            if st.button(next_label, key=f"next_{st.session_state.current_step}", disabled=next_disabled, use_container_width=True):
                st.session_state.current_step += 1
                st.rerun()


# ---------------------------------------------------------------------------
# CATEGORIES
# ---------------------------------------------------------------------------
CATEGORIES = [
    "", "Apparel", "Personal Care", "Shoes", "Jewelry", "Health Care", "Home",
    "Lawn & Garden", "Electronics", "Vehicles & Parts", "Food",
    "Beverages & Tobacco", "Animals & Pet Supplies", "Toys, Puzzles & Games",
    "Luggage, Wallets & Handbags", "Sporting Goods", "Furniture",
]

# Visual direction options with emoji placeholders
VISUAL_STYLES = [
    {"id": "cinematic", "emoji": "🎬", "label": "Cinematic / Film", "desc": "Widescreen, dramatic lighting, shallow DOF"},
    {"id": "documentary", "emoji": "📹", "label": "Documentary / Raw", "desc": "Handheld, natural light, observational"},
    {"id": "editorial", "emoji": "📰", "label": "Editorial / Fashion", "desc": "High contrast, posed, graphic"},
    {"id": "surreal", "emoji": "🌀", "label": "Surreal / Dreamlike", "desc": "Unexpected scale, impossible physics, fantasy"},
    {"id": "lofi", "emoji": "📱", "label": "Lo-Fi / Social Native", "desc": "Phone-shot aesthetic, casual, authentic"},
    {"id": "minimal", "emoji": "◻️", "label": "Minimal / Clean", "desc": "Negative space, muted tones, restrained"},
    {"id": "maximalist", "emoji": "🎨", "label": "Maximalist / Bold", "desc": "Color-saturated, busy, energetic"},
    {"id": "vintage", "emoji": "📼", "label": "Vintage / Retro", "desc": "Film grain, muted color, nostalgic"},
    {"id": "neon", "emoji": "💜", "label": "Neon / Night", "desc": "Dark backgrounds, vivid lighting, urban"},
    {"id": "organic", "emoji": "🌿", "label": "Organic / Natural", "desc": "Earth tones, soft light, textured"},
    {"id": "graphic", "emoji": "🔲", "label": "Graphic / Flat", "desc": "Bold shapes, solid colors, 2D feel"},
    {"id": "luxe", "emoji": "✨", "label": "Luxe / High-End", "desc": "Rich textures, warm metals, elevated"},
]

PLATFORMS = ["Instagram Reels", "TikTok", "YouTube Shorts", "Multi-platform"]

PRODUCT_PRESENCE_OPTIONS = [
    "None — no product visible at all",
    "Ambient — worn/used naturally, never the focus",
    "Visible — clearly present but story-first",
]

TEXT_OVERLAY_OPTIONS = [
    "None — visuals only",
    "Tagline at end only",
    "Minimal text throughout (3-7 words max per overlay)",
    "Text-heavy / typographic style",
]


# ===========================================================================
# STEP 1: BRAND IDENTITY
# ===========================================================================
def step_brand_identity():
    render_step_header(1, "Who's the brand?", "Start with the basics. If the brand has a web presence, we can auto-fill everything.")

    st.session_state.brand_name = st.text_input(
        "Brand name",
        value=st.session_state.brand_name,
        placeholder="e.g., Roxanne Assoulin",
    )

    st.session_state.brand_url = st.text_input(
        "Website URL (optional — helps us research the brand)",
        value=st.session_state.brand_url,
        placeholder="e.g., https://roxanneassoulin.com",
    )

    st.session_state.brand_category = st.selectbox(
        "Product category",
        CATEGORIES,
        index=CATEGORIES.index(st.session_state.brand_category) if st.session_state.brand_category in CATEGORIES else 0,
    )

    st.session_state.brand_description = st.text_area(
        "Describe the brand in 1-2 sentences (what do they make, what's their vibe?)",
        value=st.session_state.brand_description,
        placeholder="e.g., Colorful enamel jewelry designed to be stacked and layered. Known for playful, accessible luxury that makes people smile.",
        height=100,
    )

    # --- Auto-fill section ---
    can_research = bool(st.session_state.brand_name and st.session_state.brand_category)

    if can_research:
        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            # Full auto-fill: research + fill all fields + jump to review
            if st.button("🚀 Research & Auto-Fill Everything", key="autofill_btn", use_container_width=True):
                with st.spinner("Researching brand and filling all fields... (this may take 30-60 seconds)"):
                    try:
                        data = auto_fill_all_fields(
                            st.session_state.brand_name,
                            st.session_state.brand_url,
                            st.session_state.brand_category,
                        )
                        if data:
                            apply_auto_fill(data)
                            st.session_state.current_step = 6  # Jump to review
                            st.rerun()
                        else:
                            st.error("Auto-fill failed — could not parse LLM response. Try the manual flow instead.")
                    except Exception as e:
                        st.error(f"Auto-fill failed: {e}")

        with col2:
            # Research only: just populate scraped_data, stay on page
            if not st.session_state.scrape_attempted:
                if st.button("🔍 Research only (manual fill)", key="scrape_btn", use_container_width=True):
                    with st.spinner("Researching brand..."):
                        try:
                            data = scrape_brand_info(
                                st.session_state.brand_name,
                                st.session_state.brand_url,
                                st.session_state.brand_category,
                            )
                            st.session_state.scraped_data = data
                        except Exception as e:
                            st.error(f"Research failed: {e}")
                            st.session_state.scraped_data = None
                        st.session_state.scrape_attempted = True
                        st.rerun()

        # Show scraped data preview if available
        if st.session_state.scraped_data:
            d = st.session_state.scraped_data
            confidence = d.get("confidence", "unknown")
            conf_color = {"high": "#4a9", "medium": "#c93", "low": "#c55"}.get(confidence, "#888")

            st.markdown(f"""
            <div class="scraped-preview">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                    <span style="font-family:'Space Mono',monospace; font-size:0.7rem; color:#444; text-transform:uppercase; letter-spacing:0.1em;">BRAND RESEARCH RESULTS</span>
                    <span style="font-family:'Space Mono',monospace; font-size:0.65rem; color:{conf_color}; text-transform:uppercase; letter-spacing:0.1em;">CONFIDENCE: {confidence}</span>
                </div>
                <div class="scraped-label">TAGLINE</div>
                <div class="scraped-value">{d.get('tagline', 'Unknown')}</div>
                <div class="scraped-label">ETHOS</div>
                <div class="scraped-value">{d.get('ethos', 'Unknown')}</div>
                <div class="scraped-label">VALUES</div>
                <div class="scraped-value">{', '.join(d.get('values', []))}</div>
                <div class="scraped-label">ANTI-POSITIONING</div>
                <div class="scraped-value">{d.get('anti_positioning', 'Unknown')}</div>
                <div class="scraped-label">EMOTIONAL TERRITORY</div>
                <div class="scraped-value">{d.get('emotional_territory', 'Unknown')}</div>
                <div class="scraped-label">AUDIENCE</div>
                <div class="scraped-value">{d.get('audience_description', 'Unknown')}</div>
                <div class="scraped-label">AESTHETIC</div>
                <div class="scraped-value">{d.get('aesthetic_description', 'Unknown')}</div>
                <div class="scraped-label">PRICE TIER</div>
                <div class="scraped-value">{d.get('price_tier', 'Unknown')}</div>
            </div>
            """, unsafe_allow_html=True)

            if st.session_state.auto_filled:
                st.markdown('<div class="info-box">✓ All fields auto-filled. Review everything on the next page.</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-box">Research complete. Continue to fill in the remaining fields manually, or click "Research & Auto-Fill Everything" to fill them all at once.</div>', unsafe_allow_html=True)

        elif st.session_state.scrape_attempted:
            st.markdown('<div class="info-box">Could not auto-research this brand. No worries — we\'ll build the profile manually in the next steps.</div>', unsafe_allow_html=True)

    st.markdown("")  # spacer
    nav_buttons(back=False, next_label="Continue → (manual fill)", next_disabled=not can_research)


# ===========================================================================
# STEP 2: AUDIENCE
# ===========================================================================
def step_audience():
    render_step_header(2, "Who are you talking to?", "Not demographics — psychographics. Help us understand the human on the other side.")

    # Pre-fill from scraped data if available
    default_lifestyle = st.session_state.audience_lifestyle
    if not default_lifestyle and st.session_state.scraped_data:
        default_lifestyle = st.session_state.scraped_data.get("audience_description", "")

    st.session_state.audience_lifestyle = st.text_area(
        "Describe your ideal customer's lifestyle in a sentence or two",
        value=default_lifestyle,
        placeholder="e.g., Fashion-forward women 20-45 who mix high and low, care about self-expression more than status, and discover brands through Instagram and friends.",
        height=100,
    )

    st.session_state.audience_brands = st.text_input(
        "What other brands does your customer love? (This is a cheat code — list 3-5)",
        value=st.session_state.audience_brands,
        placeholder="e.g., Glossier, Jacquemus, Mejuri, Reformation, Aesop",
    )

    st.session_state.audience_platform = st.selectbox(
        "Primary platform for this video",
        PLATFORMS,
        index=PLATFORMS.index(st.session_state.audience_platform) if st.session_state.audience_platform in PLATFORMS else 0,
    )

    st.markdown('<div class="info-box">The competing brands input is incredibly valuable — it lets us infer aesthetic, price point, and emotional territory from brands we understand well, even if yours is brand new.</div>', unsafe_allow_html=True)

    nav_buttons(next_label="Continue →")


# ===========================================================================
# STEP 3: BRAND PERSONALITY (Spectrum Sliders)
# ===========================================================================
def step_personality():
    render_step_header(3, "Brand personality", "Position your brand on each spectrum. Don't overthink it — go with your gut.")

    spectrums = [
        ("personality_exclusive_accessible", "Exclusive", "Accessible"),
        ("personality_serious_playful", "Serious", "Playful"),
        ("personality_minimal_expressive", "Minimal", "Expressive"),
        ("personality_classic_trendy", "Classic", "Trendy"),
        ("personality_loud_quiet", "Loud", "Quiet"),
        ("personality_luxury_everyday", "Luxury", "Everyday"),
    ]

    for key, left, right in spectrums:
        st.markdown(f"""
        <div class="spectrum-row">
            <span class="spectrum-label">{left}</span>
            <span class="spectrum-label">{right}</span>
        </div>
        """, unsafe_allow_html=True)
        st.session_state[key] = st.slider(
            f"{left} — {right}",
            min_value=0,
            max_value=100,
            value=st.session_state[key],
            label_visibility="collapsed",
            key=f"slider_{key}",
        )
        st.markdown("")  # spacer

    nav_buttons(next_label="Continue →")


# ===========================================================================
# STEP 4: EMOTIONAL TERRITORY
# ===========================================================================
def step_emotion():
    render_step_header(4, "Emotional territory", "The feelings your brand owns — and the ones it rejects.")

    st.session_state.emotion_feel_after = st.text_area(
        "How should someone FEEL after watching your brand's video?",
        value=st.session_state.emotion_feel_after,
        placeholder="e.g., Like they just discovered something that gets them. A spark of joy mixed with 'I need to send this to someone.'",
        height=100,
    )

    st.session_state.emotion_reject = st.text_area(
        "What feeling does your brand REJECT? (Anti-positioning is your secret weapon)",
        value=st.session_state.emotion_reject,
        placeholder="e.g., We reject exclusivity, pretension, and the idea that you need to be 'cool enough' to wear jewelry. No gatekeeping.",
        height=100,
    )

    st.session_state.emotion_movie_scene = st.text_area(
        "If your brand were a scene in a movie, what would be happening?",
        value=st.session_state.emotion_movie_scene,
        placeholder="e.g., A group of friends getting ready together before going out — music playing, everyone borrowing each other's stuff, laughing at nothing. The moment right before the night begins.",
        height=100,
    )

    st.markdown('<div class="info-box">That last question sounds whimsical but produces some of the richest creative signal we can get. Don\'t hold back.</div>', unsafe_allow_html=True)

    nav_buttons(next_label="Continue →")


# ===========================================================================
# STEP 5: VISUAL DIRECTION
# ===========================================================================
def step_visual():
    render_step_header(5, "Visual direction", "Pick 2-4 visual styles that feel like your brand. Then set your palette.")

    # Visual style cards
    cols_per_row = 4
    for row_start in range(0, len(VISUAL_STYLES), cols_per_row):
        cols = st.columns(cols_per_row)
        for idx, col in enumerate(cols):
            style_idx = row_start + idx
            if style_idx >= len(VISUAL_STYLES):
                break
            style = VISUAL_STYLES[style_idx]
            is_selected = style["id"] in st.session_state.visual_selections
            with col:
                border_color = "#fff" if is_selected else "#222"
                bg_color = "#1a1a1a" if is_selected else "#111"
                check = " ✓" if is_selected else ""
                st.markdown(f"""
                <div style="background:{bg_color}; border:2px solid {border_color}; border-radius:12px; 
                     padding:16px; text-align:center; min-height:140px; display:flex; flex-direction:column; 
                     justify-content:center; align-items:center; margin-bottom:8px;">
                    <div style="font-size:2.2rem; margin-bottom:6px;">{style['emoji']}</div>
                    <div style="font-size:0.8rem; color:#ccc; font-weight:500;">{style['label']}{check}</div>
                    <div style="font-size:0.65rem; color:#666; margin-top:4px;">{style['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button(
                    "Select" if not is_selected else "Remove",
                    key=f"vis_{style['id']}",
                    use_container_width=True,
                ):
                    if is_selected:
                        st.session_state.visual_selections.remove(style["id"])
                    else:
                        st.session_state.visual_selections.append(style["id"])
                    st.rerun()

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Color palette
    st.markdown('<div class="step-subtitle" style="margin-bottom:1rem;">Brand color palette</div>', unsafe_allow_html=True)
    c1, c2, c3, _ = st.columns([1, 1, 1, 2])
    with c1:
        st.session_state.color_primary = st.color_picker("Primary", st.session_state.color_primary)
    with c2:
        st.session_state.color_secondary = st.color_picker("Secondary", st.session_state.color_secondary)
    with c3:
        st.session_state.color_accent = st.color_picker("Accent", st.session_state.color_accent)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # Production parameters
    st.markdown('<div class="step-subtitle" style="margin-bottom:1rem;">Production parameters</div>', unsafe_allow_html=True)

    st.session_state.product_in_frame = st.selectbox(
        "Product presence in video",
        PRODUCT_PRESENCE_OPTIONS,
        index=PRODUCT_PRESENCE_OPTIONS.index(st.session_state.product_in_frame),
    )

    st.session_state.text_overlay_pref = st.selectbox(
        "Text overlay preference",
        TEXT_OVERLAY_OPTIONS,
        index=TEXT_OVERLAY_OPTIONS.index(st.session_state.text_overlay_pref),
    )

    st.session_state.audio_direction = st.text_input(
        "Audio direction (optional — genre, mood, VO preference)",
        value=st.session_state.audio_direction,
        placeholder="e.g., Upbeat indie pop, no voiceover, natural ambient sound mixed in",
    )

    nav_buttons(next_label="Review Profile →")


# ===========================================================================
# STEP 6: REVIEW
# ===========================================================================
def build_brand_profile() -> dict:
    """Assemble the complete brand profile from all session state."""
    # Interpret personality sliders
    def interpret_slider(val, low_label, high_label):
        if val < 30:
            return f"Strongly {low_label}"
        elif val < 45:
            return f"Leans {low_label}"
        elif val <= 55:
            return f"Balanced {low_label}/{high_label}"
        elif val <= 70:
            return f"Leans {high_label}"
        else:
            return f"Strongly {high_label}"

    personality = {
        "exclusive_vs_accessible": interpret_slider(st.session_state.personality_exclusive_accessible, "Exclusive", "Accessible"),
        "serious_vs_playful": interpret_slider(st.session_state.personality_serious_playful, "Serious", "Playful"),
        "minimal_vs_expressive": interpret_slider(st.session_state.personality_minimal_expressive, "Minimal", "Expressive"),
        "classic_vs_trendy": interpret_slider(st.session_state.personality_classic_trendy, "Classic", "Trendy"),
        "loud_vs_quiet": interpret_slider(st.session_state.personality_loud_quiet, "Loud", "Quiet"),
        "luxury_vs_everyday": interpret_slider(st.session_state.personality_luxury_everyday, "Luxury", "Everyday"),
    }

    # Determine maturity mode
    scraped = st.session_state.scraped_data
    data_density_score = 0
    if scraped and scraped.get("confidence") == "high":
        data_density_score += 3
    elif scraped and scraped.get("confidence") == "medium":
        data_density_score += 2
    if st.session_state.brand_description:
        data_density_score += 1
    if st.session_state.audience_lifestyle:
        data_density_score += 1
    if st.session_state.emotion_feel_after:
        data_density_score += 1
    if st.session_state.visual_selections:
        data_density_score += 1

    if data_density_score >= 6:
        maturity = "EVOLUTION"
    elif data_density_score >= 3:
        maturity = "AMPLIFICATION"
    else:
        maturity = "DISCOVERY"

    visual_style_labels = [s["label"] for s in VISUAL_STYLES if s["id"] in st.session_state.visual_selections]

    profile = {
        "brand_name": st.session_state.brand_name,
        "website": st.session_state.brand_url,
        "category": st.session_state.brand_category,
        "description": st.session_state.brand_description,
        "maturity_mode": maturity,
        "identity": {
            "tagline": scraped.get("tagline", "") if scraped else "",
            "ethos": scraped.get("ethos", "") if scraped else "",
            "values": scraped.get("values", []) if scraped else [],
            "anti_positioning": scraped.get("anti_positioning", "") if scraped else "",
            "emotional_territory": scraped.get("emotional_territory", "") if scraped else "",
            "price_tier": scraped.get("price_tier", "") if scraped else "",
        },
        "audience": {
            "lifestyle": st.session_state.audience_lifestyle,
            "adjacent_brands": st.session_state.audience_brands,
            "primary_platform": st.session_state.audience_platform,
        },
        "personality": personality,
        "emotional_direction": {
            "desired_feeling": st.session_state.emotion_feel_after,
            "rejected_feeling": st.session_state.emotion_reject,
            "movie_scene": st.session_state.emotion_movie_scene,
        },
        "visual_direction": {
            "styles": visual_style_labels,
            "color_palette": {
                "primary": st.session_state.color_primary,
                "secondary": st.session_state.color_secondary,
                "accent": st.session_state.color_accent,
            },
        },
        "production": {
            "product_presence": st.session_state.product_in_frame,
            "text_overlay": st.session_state.text_overlay_pref,
            "audio_direction": st.session_state.audio_direction,
            "duration": "10-12 seconds",
            "keyframes": 5,
        },
    }

    return profile


def step_review():
    render_step_header(6, "Review your brand profile", "This is what we'll feed to the narrative engine. Click Edit on any section to refine it.")

    profile = build_brand_profile()
    st.session_state.brand_profile_json = profile

    # Maturity badge
    mode = profile["maturity_mode"]
    mode_colors = {"DISCOVERY": "#c55", "AMPLIFICATION": "#c93", "EVOLUTION": "#4a9"}
    mode_descriptions = {
        "DISCOVERY": "Limited brand data — the system will build your narrative identity from scratch and flag assumptions.",
        "AMPLIFICATION": "Solid brand data — the system will find the narrative angle you haven't explored yet.",
        "EVOLUTION": "Rich brand data — the system will push to the edge of what your brand can credibly say.",
    }

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:1.5rem;">
        <span style="font-family:'Space Mono',monospace; font-size:0.7rem; color:{mode_colors[mode]}; 
              letter-spacing:0.1em; text-transform:uppercase; border:1px solid {mode_colors[mode]}; 
              padding:4px 12px; border-radius:4px;">{mode} MODE</span>
        <span style="font-size:0.8rem; color:#666;">{mode_descriptions[mode]}</span>
    </div>
    """, unsafe_allow_html=True)

    # Section definitions: (section_name, edit_step, fields)
    sections = [
        ("IDENTITY", 1, [
            ("Brand", profile["brand_name"]),
            ("Category", profile["category"]),
            ("Description", profile["description"]),
            ("Tagline", profile["identity"]["tagline"]),
            ("Ethos", profile["identity"]["ethos"]),
            ("Values", ", ".join(profile["identity"]["values"]) if profile["identity"]["values"] else "—"),
            ("Anti-positioning", profile["identity"]["anti_positioning"]),
            ("Emotional Territory", profile["identity"]["emotional_territory"]),
            ("Price Tier", profile["identity"]["price_tier"]),
        ]),
        ("AUDIENCE", 2, [
            ("Lifestyle", profile["audience"]["lifestyle"]),
            ("Adjacent Brands", profile["audience"]["adjacent_brands"]),
            ("Platform", profile["audience"]["primary_platform"]),
        ]),
        ("PERSONALITY", 3, [(k.replace("_vs_", " vs ").replace("_", " ").title(), v) for k, v in profile["personality"].items()]),
        ("EMOTIONAL DIRECTION", 4, [
            ("Desired Feeling", profile["emotional_direction"]["desired_feeling"]),
            ("Rejected Feeling", profile["emotional_direction"]["rejected_feeling"]),
            ("Movie Scene", profile["emotional_direction"]["movie_scene"]),
        ]),
        ("VISUAL & PRODUCTION", 5, [
            ("Visual Styles", ", ".join(profile["visual_direction"]["styles"]) if profile["visual_direction"]["styles"] else "—"),
            ("Colors", f'Primary: {profile["visual_direction"]["color_palette"]["primary"]} | Secondary: {profile["visual_direction"]["color_palette"]["secondary"]} | Accent: {profile["visual_direction"]["color_palette"]["accent"]}'),
            ("Product Presence", profile["production"]["product_presence"]),
            ("Text Overlay", profile["production"]["text_overlay"]),
            ("Audio", profile["production"]["audio_direction"] or "—"),
            ("Duration", profile["production"]["duration"]),
        ]),
    ]

    for section_name, edit_step, fields in sections:
        # Section header with Edit button
        header_cols = st.columns([5, 1])
        with header_cols[0]:
            st.markdown(f'<div class="scraped-label" style="margin-top:20px; margin-bottom:12px; font-size:0.7rem;">{section_name}</div>', unsafe_allow_html=True)
        with header_cols[1]:
            st.markdown('<div class="back-btn" style="margin-top:16px;">', unsafe_allow_html=True)
            if st.button("✏️ Edit", key=f"edit_{section_name}", use_container_width=True):
                st.session_state.return_to_review = True
                st.session_state.current_step = edit_step
                # Clear generated content since profile is being modified
                st.session_state.generated_narratives = None
                st.session_state.selected_narrative = None
                st.session_state.generated_storyboard = None
                st.session_state.brand_profile_json = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        for label, value in fields:
            if value and value != "—":
                st.markdown(f"""
                <div style="display:flex; gap:12px; margin-bottom:8px; align-items:baseline;">
                    <span style="font-size:0.75rem; color:#555; min-width:140px; font-weight:500;">{label}</span>
                    <span style="font-size:0.85rem; color:#ccc;">{value}</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="display:flex; gap:12px; margin-bottom:8px; align-items:baseline;">
                    <span style="font-size:0.75rem; color:#555; min-width:140px; font-weight:500;">{label}</span>
                    <span style="font-size:0.85rem; color:#333;">Not provided</span>
                </div>
                """, unsafe_allow_html=True)

    # Raw JSON expander
    with st.expander("View raw JSON profile"):
        st.code(json.dumps(profile, indent=2), language="json")

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    nav_buttons(next_label="Generate Narrative Concepts →")


# ===========================================================================
# STEP 7: GENERATE & SELECT
# ===========================================================================
def step_generate():
    render_step_header(7, "Narrative concepts", "The creative engine has produced concepts based on your brand profile. Pick the one that resonates.")

    profile = st.session_state.brand_profile_json or build_brand_profile()

    # --- Generate concepts if not yet generated ---
    if st.session_state.generated_narratives is None:
        st.markdown("""
        <div class="generating">
            <div class="generating-text">GENERATING NARRATIVE CONCEPTS...</div>
            <div style="color:#333; font-size:0.75rem; margin-top:8px;">Finding human truths, building micro-narratives, filtering generic ideas</div>
        </div>
        """, unsafe_allow_html=True)

        try:
            result = generate_narrative_concepts(profile)
        except Exception as e:
            st.error(f"LLM call failed: {e}")
            st.stop()

        if result.startswith("__LLM_"):
            st.error(f"LLM integration issue: {result}")
            st.stop()

        # Parse the JSON response
        try:
            parsed = _parse_json_response(result)
            if isinstance(parsed, list):
                st.session_state.generated_narratives = parsed
            elif isinstance(parsed, dict):
                st.session_state.generated_narratives = [parsed]
            else:
                st.error("Could not parse narrative concepts. Raw response:")
                st.code(result[:2000], language=None)
                st.stop()
        except Exception as e:
            st.error(f"JSON parsing failed: {e}")
            st.code(result[:2000], language=None)
            st.stop()

        st.rerun()

    # --- Display concepts ---
    narratives = st.session_state.generated_narratives

    if isinstance(narratives, list) and len(narratives) > 0:
        for i, concept in enumerate(narratives):
            is_selected = st.session_state.selected_narrative == i
            border = "#fff" if is_selected else "#222"
            bg = "#1a1a1a" if is_selected else "linear-gradient(145deg, #111, #0d0d0d)"

            title = concept.get("title", f"Concept {i+1}")
            truth = concept.get("human_truth", "")
            summary = concept.get("summary", "")
            arc = concept.get("emotional_arc", "")
            hook = concept.get("hook", "")
            rationale = concept.get("rationale", "")

            st.markdown(f"""
            <div style="background:{bg}; border:1px solid {border}; border-radius:16px; padding:24px; margin-bottom:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                    <span style="font-family:'DM Sans',sans-serif; font-size:1.2rem; font-weight:700; color:#fff;">{title}</span>
                    <span style="font-family:'Space Mono',monospace; font-size:0.65rem; color:#444; text-transform:uppercase;">CONCEPT {i+1}</span>
                </div>
                <div style="color:#999; font-size:0.8rem; font-style:italic; margin-bottom:12px; line-height:1.5;">"{truth}"</div>
                <div style="color:#ccc; font-size:0.85rem; margin-bottom:12px; line-height:1.5;">{summary}</div>
                <div style="display:flex; gap:24px; margin-bottom:8px;">
                    <div>
                        <span style="font-family:'Space Mono',monospace; font-size:0.6rem; color:#444; text-transform:uppercase;">ARC</span>
                        <div style="font-size:0.8rem; color:#888; margin-top:2px;">{arc}</div>
                    </div>
                </div>
                <div style="margin-top:12px;">
                    <span style="font-family:'Space Mono',monospace; font-size:0.6rem; color:#444; text-transform:uppercase;">HOOK</span>
                    <div style="font-size:0.8rem; color:#888; margin-top:2px; line-height:1.4;">{hook}</div>
                </div>
                <div style="margin-top:12px;">
                    <span style="font-family:'Space Mono',monospace; font-size:0.6rem; color:#444; text-transform:uppercase;">WHY IT WORKS</span>
                    <div style="font-size:0.8rem; color:#666; margin-top:2px; line-height:1.4;">{rationale}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(
                "✓ Selected" if is_selected else "Select this concept",
                key=f"select_concept_{i}",
                use_container_width=True,
            ):
                st.session_state.selected_narrative = i
                st.rerun()

        # --- Regenerate button ---
        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
        regen_col1, regen_col2, _ = st.columns([1, 1, 3])
        with regen_col1:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button("← Back to Review", key="back_to_review", use_container_width=True):
                st.session_state.current_step = 6
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        with regen_col2:
            st.markdown('<div class="back-btn">', unsafe_allow_html=True)
            if st.button("🔄 Regenerate Concepts", key="regen", use_container_width=True):
                st.session_state.generated_narratives = None
                st.session_state.selected_narrative = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        # --- Generate storyboard if concept selected ---
        if st.session_state.selected_narrative is not None:
            st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

            try:
                selected = narratives[st.session_state.selected_narrative]
            except (IndexError, TypeError):
                st.error("Selected concept not found. Try selecting again.")
                selected = None

            if selected and st.session_state.generated_storyboard is None:
                if st.button("🎬 Generate Full Storyboard & Prompts", key="gen_storyboard", use_container_width=True):
                    # Step 1: Call LLM
                    with st.spinner("Generating storyboard (this may take 30-60 seconds)..."):
                        try:
                            sb_result = generate_full_storyboard(profile, selected)
                        except Exception as e:
                            st.error(f"LLM call failed: {e}")
                            st.stop()

                    # Step 2: Check for LLM errors
                    if sb_result is None or sb_result.startswith("__LLM_"):
                        st.error(f"Storyboard generation failed: {sb_result}")
                        st.stop()

                    # Step 3: Parse JSON
                    try:
                        parsed = _parse_json_response(sb_result)
                        if parsed:
                            st.session_state.generated_storyboard = parsed
                        else:
                            # JSON parse failed — show raw response so user can see what happened
                            st.session_state.generated_storyboard = {"raw": sb_result}
                    except Exception as e:
                        st.error(f"JSON parsing failed: {e}")
                        st.session_state.generated_storyboard = {"raw": sb_result}

                    st.rerun()

            # Display storyboard
            if st.session_state.generated_storyboard:
                sb = st.session_state.generated_storyboard

                st.markdown(f"""
                <div style="margin-top:1rem; margin-bottom:1.5rem;">
                    <div class="step-title" style="font-size:1.5rem;">Storyboard Output</div>
                    <div class="step-subtitle">Pipeline-ready keyframes and prompts for NanoBanana Pro + Veo 3.1</div>
                </div>
                """, unsafe_allow_html=True)

                if "raw" in sb:
                    st.markdown(sb["raw"])
                else:
                    tab1, tab2, tab3, tab4 = st.tabs(["📋 Keyframes", "🖼️ Image Prompts", "🎥 Animation Prompts", "📦 Export JSON"])

                    with tab1:
                        # Style suffix
                        if sb.get("style_suffix"):
                            st.markdown(f"""
                            <div style="background:#0d0d0d; border:1px solid #1a1a1a; border-radius:8px; padding:12px 16px; margin-bottom:16px;">
                                <span style="font-family:'Space Mono',monospace; font-size:0.6rem; color:#444; text-transform:uppercase;">STYLE SUFFIX (ALL KEYFRAMES)</span>
                                <div style="font-size:0.8rem; color:#888; margin-top:4px;">{sb['style_suffix']}</div>
                            </div>
                            """, unsafe_allow_html=True)

                        for kf in sb.get("keyframes", []):
                            ts = kf.get("timestamp", "")
                            beat = kf.get("narrative_beat", "")
                            st.markdown(f"""
                            <div style="background:#111; border:1px solid #1a1a1a; border-radius:12px; padding:20px; margin-bottom:12px;">
                                <div style="display:flex; justify-content:space-between; margin-bottom:10px;">
                                    <span style="font-family:'Space Mono',monospace; font-size:0.7rem; color:#fff; letter-spacing:0.05em;">{ts}</span>
                                    <span style="font-family:'Space Mono',monospace; font-size:0.65rem; color:#444; text-transform:uppercase;">{beat}</span>
                                </div>
                                <div style="color:#ccc; font-size:0.85rem; line-height:1.5; margin-bottom:10px;">{kf.get('scene_description', '')}</div>
                                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:0.75rem;">
                                    <div><span style="color:#555;">Camera:</span> <span style="color:#888;">{kf.get('camera', '')}</span></div>
                                    <div><span style="color:#555;">Lighting:</span> <span style="color:#888;">{kf.get('lighting', '')}</span></div>
                                    <div><span style="color:#555;">Emotion:</span> <span style="color:#888;">{kf.get('emotion', '')}</span></div>
                                    <div><span style="color:#555;">Product:</span> <span style="color:#888;">{kf.get('product_presence', '')}</span></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    with tab2:
                        for idx, prompt in enumerate(sb.get("image_prompts", [])):
                            st.markdown(f"""
                            <div style="background:#111; border:1px solid #1a1a1a; border-radius:12px; padding:16px; margin-bottom:12px;">
                                <span style="font-family:'Space Mono',monospace; font-size:0.65rem; color:#444;">KEYFRAME {idx+1} — NANOBANA PRO PROMPT</span>
                                <div style="color:#ccc; font-size:0.8rem; margin-top:8px; line-height:1.5;">{prompt}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    with tab3:
                        for idx, trans in enumerate(sb.get("animation_prompts", [])):
                            label = trans.get("transition", f"Transition {idx+1} → {idx+2}")
                            st.markdown(f"""
                            <div style="background:#111; border:1px solid #1a1a1a; border-radius:12px; padding:16px; margin-bottom:12px;">
                                <span style="font-family:'Space Mono',monospace; font-size:0.65rem; color:#444;">{label} — VEO 3.1 PROMPT</span>
                                <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; font-size:0.75rem; margin-top:10px;">
                                    <div><span style="color:#555;">Camera:</span> <span style="color:#888;">{trans.get('camera_motion', '')}</span></div>
                                    <div><span style="color:#555;">Subject:</span> <span style="color:#888;">{trans.get('subject_motion', '')}</span></div>
                                    <div><span style="color:#555;">Pacing:</span> <span style="color:#888;">{trans.get('pacing', '')}</span></div>
                                    <div><span style="color:#555;">Transition:</span> <span style="color:#888;">{trans.get('visual_transition', '')}</span></div>
                                    <div><span style="color:#555;">Emotion:</span> <span style="color:#888;">{trans.get('emotional_trajectory', '')}</span></div>
                                    <div><span style="color:#555;">Audio:</span> <span style="color:#888;">{trans.get('audio_cue', '')}</span></div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    with tab4:
                        # Full pipeline export
                        export = {
                            "brand_profile": profile,
                            "selected_concept": selected,
                            "storyboard": sb,
                            "generated_at": datetime.now().isoformat(),
                            "pipeline_version": "0.1.0",
                        }
                        st.code(json.dumps(export, indent=2), language="json")
                        st.download_button(
                            label="📥 Download Pipeline JSON",
                            data=json.dumps(export, indent=2),
                            file_name=f"{profile['brand_name'].lower().replace(' ', '_')}_narrative_pipeline.json",
                            mime="application/json",
                        )

                # Director notes and audit
                if sb.get("creative_director_notes"):
                    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div style="background:#0d0d0d; border-left:3px solid #444; padding:16px 20px; border-radius:0 8px 8px 0;">
                        <span style="font-family:'Space Mono',monospace; font-size:0.65rem; color:#444; text-transform:uppercase;">CREATIVE DIRECTOR NOTES</span>
                        <div style="color:#888; font-size:0.85rem; margin-top:8px; line-height:1.5;">{sb['creative_director_notes']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Regenerate storyboard button
                st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
                st.markdown('<div class="back-btn">', unsafe_allow_html=True)
                if st.button("🔄 Regenerate Storyboard", key="regen_storyboard", use_container_width=False):
                    st.session_state.generated_storyboard = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)


# ===========================================================================
# SIDEBAR: API SETTINGS
# ===========================================================================
def render_sidebar():
    """Render the API configuration sidebar."""
    with st.sidebar:
        st.markdown("""
        <div style="margin-bottom:1.5rem;">
            <div style="font-family:'DM Sans',sans-serif; font-size:1.1rem; font-weight:700; color:#fff; margin-bottom:4px;">⚙️ API Settings</div>
            <div style="font-size:0.75rem; color:#555;">Configure your LLM provider and model</div>
        </div>
        """, unsafe_allow_html=True)

        # Provider selection
        providers = list(LLM_PROVIDERS.keys())
        current_provider = st.session_state.llm_provider
        provider = st.selectbox(
            "Provider",
            providers,
            index=providers.index(current_provider) if current_provider in providers else 0,
            key="sidebar_provider",
        )

        # If provider changed, update model to first in new provider's list
        if provider != st.session_state.llm_provider:
            st.session_state.llm_provider = provider
            st.session_state.llm_model = LLM_PROVIDERS[provider]["models"][0][1]
            st.session_state.api_key = ""
            st.session_state.api_key_set = False
            st.rerun()

        # Model selection
        provider_config = LLM_PROVIDERS[provider]
        model_labels = [m[0] for m in provider_config["models"]]
        model_ids = [m[1] for m in provider_config["models"]]

        current_model = st.session_state.llm_model
        if current_model in model_ids:
            model_index = model_ids.index(current_model)
        else:
            model_index = 0

        selected_label = st.selectbox(
            "Model",
            model_labels,
            index=model_index,
            key="sidebar_model",
        )
        selected_model_id = model_ids[model_labels.index(selected_label)]

        if selected_model_id != st.session_state.llm_model:
            st.session_state.llm_model = selected_model_id

        # API Key
        st.markdown(f"""
        <div style="margin-top:1rem; margin-bottom:0.5rem;">
            <span style="font-size:0.75rem; color:#666;">
                Get your key → <a href="{provider_config['docs_url']}" target="_blank" style="color:#888;">{provider}</a>
            </span>
        </div>
        """, unsafe_allow_html=True)

        api_key_input = st.text_input(
            "API Key",
            value=st.session_state.api_key,
            type="password",
            placeholder=provider_config["key_placeholder"],
            key="sidebar_api_key",
        )

        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input
            st.session_state.api_key_set = bool(api_key_input)

        # Status indicator
        if st.session_state.api_key_set:
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin-top:12px; padding:8px 12px; 
                 background:#0d1a0d; border:1px solid #1a331a; border-radius:6px;">
                <span style="color:#4a9; font-size:1rem;">●</span>
                <span style="font-size:0.75rem; color:#4a9;">{provider} · {selected_label}</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="display:flex; align-items:center; gap:8px; margin-top:12px; padding:8px 12px; 
                 background:#1a1210; border:1px solid #332218; border-radius:6px;">
                <span style="color:#c55; font-size:1rem;">●</span>
                <span style="font-size:0.75rem; color:#c55;">No API key configured</span>
            </div>
            """, unsafe_allow_html=True)

        # Dependency info
        st.markdown('<hr style="border:none; border-top:1px solid #1a1a1a; margin:1.5rem 0;">', unsafe_allow_html=True)
        st.markdown(f"""
        <div style="font-family:'Space Mono',monospace; font-size:0.6rem; color:#333; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">
            REQUIRED PACKAGE
        </div>
        """, unsafe_allow_html=True)

        pkg_map = {"Anthropic": "anthropic", "OpenAI": "openai", "Google": "google-genai"}
        pkg = pkg_map.get(provider, "")
        st.code(f"pip install {pkg}", language="bash")

        st.markdown("""
        <div style="margin-top:1.5rem; padding-top:1rem; border-top:1px solid #1a1a1a;">
            <div style="font-family:'Space Mono',monospace; font-size:0.6rem; color:#333; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">
                ABOUT
            </div>
            <div style="font-size:0.7rem; color:#444; line-height:1.5;">
                Your API key is stored only in your browser session and is never sent anywhere except directly to your chosen provider's API. Keys are not persisted between sessions.
            </div>
        </div>
        """, unsafe_allow_html=True)


# ===========================================================================
# MAIN ROUTER
# ===========================================================================
def main():
    # Render sidebar settings
    render_sidebar()

    # Constrain step range
    st.session_state.current_step = max(1, min(TOTAL_STEPS, st.session_state.current_step))

    render_progress()

    step = st.session_state.current_step

    if step == 1:
        step_brand_identity()
    elif step == 2:
        step_audience()
    elif step == 3:
        step_personality()
    elif step == 4:
        step_emotion()
    elif step == 5:
        step_visual()
    elif step == 6:
        step_review()
    elif step == 7:
        step_generate()


if __name__ == "__main__":
    main()
