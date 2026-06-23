"""
ui_components.py

UI-only helpers for the LIFT Agent Streamlit app.

LIFT Agent = Locate, Identify, Follow-up, Track.

Purpose:
- Make the app calmer, cleaner, and easier for non-technical users.
- Keep the main app as one continuous scrolling page.
- Keep advanced/project details in lower-page optional sections.
- Use the real local animation files in assets/lift_animation.
- Use the real local brand icon in assets/lift_brand when available.
- Do not use fake visual placeholders.

Expected animation files:
- assets/lift_animation/1 LIFT Project.png
- assets/lift_animation/2 LIFT Project.png
- ...
- assets/lift_animation/32 LIFT Project.png

Expected brand icon files:
- assets/lift_brand/LIFT Agent icon.png

Important:
Most functions are presentational only.
render_archived_project_panel() intentionally reads and updates:
- st.session_state["language"]
- st.session_state["language_access_needed"]

It also reads trace/session evidence if available, but it does not gate,
stop, hide, or control the main app flow.
"""

import base64
import html
from pathlib import Path
from typing import List, Optional, Tuple

import streamlit as st
import streamlit.components.v1 as components


LIFT_COLORS = {
    "background": "#FAFAF6",
    "card": "#FFFFFF",
    "teal": "#1F7A78",
    "deep_teal": "#0E5F73",
    "sage": "#A8C3A0",
    "muted_blue": "#6E9CB3",
    "soft_blue": "#B8D7E0",
    "champagne": "#EFE2C6",
    "light_champagne": "#F7EEDC",
    "cream": "#F7F3EC",
    "gray_green": "#7C8B7A",
    "mist": "#E7EFEC",
    "text": "#24302F",
    "muted_text": "#5F6F6B",
    "border": "#DDE5DF",
}

ANIMATION_FRAME_DIR = Path("assets/lift_animation")
BRAND_ICON_DIR = Path("assets/lift_brand")
WHAT_IMAGE_PATH = Path("assets/clean_info_lift/What.png")

ANIMATION_FRAME_NAMES = [
    f"{number} LIFT Project.png"
    for number in range(1, 33)
]

BRAND_ICON_NAMES = [
    "LIFT Agent icon.png",
]


def inject_global_styles() -> None:
    """Inject global CSS for the LIFT Agent visual design."""
    st.markdown(
        f"""
        <style>
        html {{
            scroll-behavior: smooth;
        }}

        .stApp {{
            background:
                radial-gradient(circle at 20% 10%, rgba(184, 215, 224, 0.34), transparent 28%),
                radial-gradient(circle at 85% 18%, rgba(168, 195, 160, 0.22), transparent 26%),
                linear-gradient(180deg, #F8FBFA 0%, {LIFT_COLORS['background']} 48%, #F7F4EF 100%);
            color: {LIFT_COLORS['text']};
        }}

        .block-container {{
            padding-top: 0.45rem;
            padding-bottom: 2.5rem;
            max-width: 1180px;
        }}

        section[data-testid="stSidebar"] {{
            background-color: rgba(250, 250, 246, 0.98);
            border-right: 1px solid {LIFT_COLORS['border']};
        }}

        .lift-brand-wrap {{
            display: flex;
            align-items: center;
            justify-content: flex-start;
            gap: 1rem;
            padding: 0.75rem 0.95rem;
            margin: 0 0 0.45rem 0;
            background: {LIFT_COLORS['background']};
            border: 1px solid {LIFT_COLORS['border']};
            border-radius: 12px;
        }}

        .lift-brand-logo {{
            width: clamp(92px, 20vw, 170px);
            height: auto;
            display: block;
            border-radius: 8px;
            box-shadow: none;
            flex: 0 0 auto;
        }}

        .lift-dot-flower {{
            position: relative;
            width: 42px;
            height: 42px;
            flex: 0 0 auto;
        }}

        .lift-dot-flower span {{
            position: absolute;
            width: 9px;
            height: 9px;
            border-radius: 999px;
            box-shadow: 0 2px 8px rgba(36, 48, 47, 0.10);
        }}

        .lift-dot-flower .dot-center {{
            width: 10px;
            height: 10px;
            left: 16px;
            top: 16px;
            background: {LIFT_COLORS['champagne']};
        }}

        .lift-dot-flower .dot-1 {{
            left: 16px;
            top: 2px;
            background: {LIFT_COLORS['teal']};
        }}

        .lift-dot-flower .dot-2 {{
            left: 29px;
            top: 9px;
            background: {LIFT_COLORS['muted_blue']};
        }}

        .lift-dot-flower .dot-3 {{
            left: 29px;
            top: 25px;
            background: {LIFT_COLORS['sage']};
        }}

        .lift-dot-flower .dot-4 {{
            left: 16px;
            top: 31px;
            background: {LIFT_COLORS['soft_blue']};
        }}

        .lift-dot-flower .dot-5 {{
            left: 3px;
            top: 25px;
            background: {LIFT_COLORS['gray_green']};
        }}

        .lift-dot-flower .dot-6 {{
            left: 3px;
            top: 9px;
            background: {LIFT_COLORS['light_champagne']};
        }}

        .lift-brand-title {{
            font-size: clamp(1.2rem, 2.9vw, 2.15rem);
            font-weight: 850;
            line-height: 1.08;
            color: {LIFT_COLORS['teal']};
            letter-spacing: 0;
            margin: 0;
        }}

        .lift-brand-subtitle {{
            font-size: 0.98rem;
            color: {LIFT_COLORS['text']};
            margin-top: 0.25rem;
        }}

        .lift-top-menu {{
            margin: 0 0 0.55rem 0;
        }}

        .lift-start-cue {{
            color: {LIFT_COLORS['deep_teal']};
            background: rgba(247, 243, 236, 0.92);
            border: 1px solid {LIFT_COLORS['border']};
            border-radius: 12px;
            padding: 0.7rem 0.9rem;
            margin: 0.35rem 0 0.65rem 0;
            font-weight: 750;
            text-align: center;
        }}

        .lift-what-wrap {{
            display: flex;
            justify-content: center;
            margin: 0.15rem 0 0.55rem 0;
        }}

        .lift-what-image {{
            width: min(430px, 96vw);
            height: auto;
            display: block;
            border-radius: 18px;
            box-shadow: 0 14px 42px rgba(36, 48, 47, 0.08);
        }}

        .lift-scroll-wrap {{
            text-align: center;
            margin: 0.35rem 0 0.55rem 0;
        }}

        .lift-scroll-button {{
            display: inline-block;
            background: #C9574D;
            color: #FFFFFF !important;
            padding: 0.78rem 1.45rem;
            border-radius: 999px;
            font-size: 1rem;
            font-weight: 750;
            text-decoration: none !important;
            box-shadow: 0 14px 34px rgba(31, 122, 120, 0.25);
            transition: transform 0.2s ease, box-shadow 0.2s ease, filter 0.2s ease;
        }}

        .lift-scroll-button:hover {{
            transform: translateY(-3px);
            filter: saturate(1.05);
            box-shadow: 0 18px 44px rgba(31, 122, 120, 0.32);
        }}

        .lift-section-title {{
            text-align: center;
            color: {LIFT_COLORS['deep_teal']};
            font-size: clamp(1.7rem, 3vw, 2.4rem);
            margin: 1.2rem 0 0.25rem 0;
        }}

        .lift-section-subtitle {{
            text-align: center;
            color: {LIFT_COLORS['muted_text']};
            font-size: 1.03rem;
            margin-bottom: 1.4rem;
        }}

        .lift-explainer-card {{
            min-height: 142px;
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid {LIFT_COLORS['border']};
            border-radius: 8px;
            padding: 1.1rem 1.15rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 14px 40px rgba(36, 48, 47, 0.08);
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .lift-explainer-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 18px 48px rgba(36, 48, 47, 0.11);
        }}

        .lift-explainer-letter {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 2rem;
            height: 2rem;
            border-radius: 999px;
            background: {LIFT_COLORS['mist']};
            color: {LIFT_COLORS['deep_teal']};
            font-size: 1.2rem;
            font-weight: 800;
            margin-right: 0.45rem;
        }}

        .lift-explainer-word {{
            color: {LIFT_COLORS['deep_teal']};
            font-size: 1.05rem;
            font-weight: 800;
        }}

        .lift-explainer-desc {{
            font-size: 0.94rem;
            line-height: 1.48;
            margin-top: 0.65rem;
            color: {LIFT_COLORS['text']};
        }}

        .lift-soft-card {{
            background: rgba(255, 255, 255, 0.78);
            border: 1px solid {LIFT_COLORS['border']};
            border-radius: 8px;
            padding: 1rem 1.15rem;
            box-shadow: 0 12px 34px rgba(36, 48, 47, 0.07);
            margin: 0.6rem 0 1rem 0;
        }}

        .lift-result-card {{
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid {LIFT_COLORS['border']};
            border-left: 6px solid {LIFT_COLORS['muted_blue']};
            border-radius: 8px;
            padding: 1rem 1.15rem;
            margin-bottom: 0.85rem;
            box-shadow: 0 12px 34px rgba(36, 48, 47, 0.07);
        }}

        .lift-result-card h4 {{
            margin-top: 0;
            margin-bottom: 0.45rem;
            color: {LIFT_COLORS['deep_teal']};
        }}

        .lift-result-card li {{
            color: {LIFT_COLORS['text']};
            line-height: 1.42;
        }}

        .lift-small-note {{
            color: {LIFT_COLORS['muted_text']};
            font-size: 0.92rem;
            line-height: 1.45;
        }}

        .stMarkdown,
        .stMarkdown p,
        .stCaptionContainer,
        label,
        [data-testid="stWidgetLabel"],
        [data-testid="stCheckbox"] label,
        [data-testid="stCheckbox"] p,
        [data-testid="stSelectbox"] label,
        [data-testid="stTextArea"] label,
        [data-testid="stTextInput"] label,
        [data-testid="stSlider"] label {{
            color: {LIFT_COLORS['text']} !important;
        }}

        [data-testid="stCaptionContainer"],
        .stCaptionContainer p,
        small {{
            color: {LIFT_COLORS['muted_text']} !important;
        }}

        .stTextInput input,
        .stTextArea textarea,
        [data-baseweb="select"] > div,
        [data-testid="stNumberInput"] input {{
            background-color: #FFFFFF !important;
            color: {LIFT_COLORS['text']} !important;
            border-color: {LIFT_COLORS['border']} !important;
        }}

        .stButton > button,
        [data-testid="stDownloadButton"] button {{
            border-radius: 8px !important;
        }}

        .stButton > button[kind="primary"],
        [data-testid="stDownloadButton"] button[kind="primary"] {{
            background: #C9574D !important;
            border-color: #C9574D !important;
        }}

        h1, h2, h3 {{
            color: {LIFT_COLORS['deep_teal']} !important;
            letter-spacing: 0 !important;
        }}

        [data-testid="stExpander"] {{
            background: rgba(255, 255, 255, 0.72);
            border-color: {LIFT_COLORS['border']};
        }}

        [data-testid="stExpander"] details,
        [data-testid="stExpander"] summary,
        [data-testid="stAlert"],
        [data-testid="stAlert"] p {{
            color: {LIFT_COLORS['text']} !important;
        }}

        @media (max-width: 900px) {{
            .lift-brand-wrap {{
                justify-content: flex-start;
                align-items: center;
                gap: 0.75rem;
                padding: 0.45rem 0.55rem;
            }}

            .lift-brand-logo {{
                width: 92px;
            }}

            .lift-brand-title {{
                font-size: 1.05rem;
            }}

            .lift-brand-subtitle {{
                font-size: 0.8rem;
            }}

            .block-container {{
                padding-left: 0.85rem;
                padding-right: 0.85rem;
            }}

            h1 {{
                font-size: 1.55rem !important;
            }}

            h2, h3 {{
                font-size: 1.18rem !important;
                margin-top: 0.75rem !important;
            }}

            div[data-testid="stVerticalBlock"] {{
                gap: 0.45rem;
            }}

            .lift-explainer-card {{
                min-height: auto;
            }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            html {{
                scroll-behavior: auto;
            }}

            .lift-scroll-button,
            .lift-explainer-card {{
                transition: none !important;
                transform: none !important;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _encode_image_to_data_uri(path: Path) -> str:
    """Convert a local image file to a base64 data URI."""
    suffix = path.suffix.lower().replace(".", "")

    if suffix == "jpg":
        suffix = "jpeg"

    if suffix not in {"png", "jpeg", "webp", "gif"}:
        raise ValueError(f"Unsupported image type: {path.name}")

    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/{suffix};base64,{encoded}"


def _find_first_existing_file(folder: Path, file_names: List[str]) -> Optional[Path]:
    """Return the first file that exists from a preferred-name list."""
    for name in file_names:
        path = folder / name
        if path.is_file():
            return path
    return None


def render_header(app_title: str, subtitle: str) -> None:
    """
    Compatibility function from the earlier app.
    New app flow should use render_brand_header().
    """
    render_brand_header(app_name=app_title, author_line="from Britney Katherine Lindsey")
    if subtitle:
        st.caption(subtitle)


def render_brand_header(
    app_name: str = "LIFT Agent",
    author_line: str = "from Britney Katherine Lindsey",
    icon_dir: Path = BRAND_ICON_DIR,
    icon_names: Optional[List[str]] = None,
) -> None:
    """
    Render the top-left brand label.

    Uses the real brand icon image if found:
    - assets/lift_brand/LIFT Agent icon.png

    If no brand icon is found, it falls back to text with a CSS dot flower and
    gives a warning so the missing asset is visible.
    """
    tagline = "LOCATE IDENTIFY FOLLOW-UP TRACK"

    if icon_names is None:
        icon_names = BRAND_ICON_NAMES

    icon_path = _find_first_existing_file(Path(icon_dir), icon_names)
    safe_tagline = html.escape(tagline)
    safe_author_line = html.escape(author_line)

    if icon_path:
        try:
            icon_data_uri = _encode_image_to_data_uri(icon_path)
            st.markdown(
                f"""
                <div class="lift-brand-wrap">
                    <img
                        class="lift-brand-logo"
                        src="{icon_data_uri}"
                        alt="{html.escape(app_name)} logo"
                    />
                    <div>
                        <div class="lift-brand-title">{safe_tagline}</div>
                        <div class="lift-brand-subtitle">{safe_author_line}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            return
        except Exception as exc:
            st.warning(f"Brand icon was found but could not be loaded: {exc}")

    safe_app_name = html.escape(app_name)

    st.warning(
        "Brand icon not found. Expected" "assets/lift_brand/LIFT Agent icon.png`."
    )

    st.markdown(
        f"""
        <div class="lift-brand-wrap">
            <div class="lift-dot-flower" aria-hidden="true">
                <span class="dot-center"></span>
                <span class="dot-1"></span>
                <span class="dot-2"></span>
                <span class="dot-3"></span>
                <span class="dot-4"></span>
                <span class="dot-5"></span>
                <span class="dot-6"></span>
            </div>
            <div>
                <div class="lift-brand-title">{safe_tagline}</div>
                <div class="lift-brand-subtitle">{safe_author_line}</div>
                <div class="lift-small-note">{safe_app_name}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_menu(supported_languages: List[str]) -> None:
    """Render compact top navigation/help without changing the main workflow."""
    with st.expander("Menu / Help", expanded=False):
        st.markdown('<div class="lift-top-menu">', unsafe_allow_html=True)

        current_language = st.session_state.get("language", "English")
        language_index = (
            supported_languages.index(current_language)
            if current_language in supported_languages
            else 0
        )

        language_choice = st.selectbox(
            "Language",
            supported_languages,
            index=language_index,
            key="top_language_select",
        )
        st.session_state["language"] = language_choice

        tab_about, tab_safety, tab_workflow, tab_notes = st.tabs(
            ["About LIFT", "Privacy / Safety", "How it works", "Evidence / Project notes"]
        )

        with tab_about:
            st.markdown(
                "LIFT Agent means Locate, Identify, Follow-up, Track. It helps organize "
                "resource options, access barriers, outreach drafts, and next steps."
            )

        with tab_safety:
            st.markdown(
                "Use public information only. Nothing is sent automatically, and generated "
                "outreach must be reviewed by a human before use."
            )

        with tab_workflow:
            st.markdown(
                "Start below with the need and location. LIFT checks consent, routes the "
                "request, gathers public or fallback resources, and keeps a case record."
            )

        with tab_notes:
            st.markdown(
                "Project evidence and agent traces remain available in lower-page sections and after "
                "a plan is generated."
            )

        st.markdown("</div>", unsafe_allow_html=True)


def render_start_cue() -> None:
    """Render a clear cue before the visual content begins."""
    st.markdown(
        """
        <div class="lift-start-cue">
            Start below: tell LIFT what you need.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_panel() -> None:
    """Compatibility function from the earlier app."""
    with st.expander("How LIFT works", expanded=False):
        st.markdown(
            """
LIFT Agent helps organize resource navigation into four plain-language steps:

1. **Locate** local options.
2. **Identify** barriers, gaps, or verification needs.
3. **Follow-up** with draft language the user reviews first.
4. **Track** next steps in one place.

Nothing is sent automatically. Provider details should be verified directly.
"""
        )


def render_safety_notice() -> None:
    """Compatibility safety notice from the earlier app."""
    st.info(
        "Use public information only. Do not enter private, classified, restricted, protected, "
        "or sensitive information. LIFT can send approved SMTP email only after review. "
        "LIFT does not call providers, monitor voicemail, or scan inboxes."
    )


def _load_animation_frames(
    frame_dir: Path = ANIMATION_FRAME_DIR,
    frame_names: Optional[List[str]] = None,
) -> Tuple[List[str], List[str]]:
    """
    Load animation frames from disk.

    Returns:
        frames: base64 data URIs
        missing: expected files that were not found or could not be read
    """
    if frame_names is None:
        frame_names = ANIMATION_FRAME_NAMES

    frames = []
    missing = []

    for name in frame_names:
        path = frame_dir / name

        if not path.is_file():
            missing.append(name)
            continue

        try:
            frames.append(_encode_image_to_data_uri(path))
        except Exception:
            missing.append(name)

    return frames, missing


def render_hover_animation(
    frame_dir: Path = ANIMATION_FRAME_DIR,
    frame_names: Optional[List[str]] = None,
    width_px: int = 320,
    height_px: int = 320,
    frame_delay_ms: int = 1250,
) -> None:
    """
    Render a hover-triggered flipbook animation using real local image files.

    Behavior:
    - Resting image = 1 LIFT Project.png
    - Hover/focus = cycles through the available images in order
    - Mouse leave/blur = returns to image 1

    No fake placeholder artwork is shown.
    If files are missing, the app shows a clear warning/error.
    """
    if frame_names is None:
        frame_names = ANIMATION_FRAME_NAMES

    frame_dir = Path(frame_dir)
    frames, missing = _load_animation_frames(frame_dir, frame_names)

    if len(frames) < 2:
        st.error(
            f"Animation images are missing. Add at least `1 LIFT Project.png` and "
            f"`2 LIFT Project.png` to `{frame_dir.as_posix()}/`."
        )
        return

    if missing:
        with st.expander("Animation image files missing", expanded=False):
            st.warning(
                "The animation will still run with the images it found, but these expected "
                "files were not found or could not be read:"
            )
            st.write(missing)

    frames_js_array = ", ".join([f'"{frame}"' for frame in frames])

    component_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
        html, body {{
            margin: 0;
            padding: 0;
            background: transparent;
            overflow: hidden;
        }}

        .lift-art-shell {{
            width: min({width_px}px, 96vw);
            height: min({height_px}px, 96vw);
            margin: 0 auto;
            padding: 6px;
            box-sizing: border-box;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.78);
            box-shadow: 0 14px 42px rgba(14, 95, 115, 0.11);
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        #lift-hover-img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
            border-radius: 16px;
            cursor: pointer;
            display: block;
            transition: transform 900ms ease, filter 900ms ease, opacity 700ms ease;
        }}

        #lift-hover-img:hover {{
            transform: scale(1.012);
            filter: saturate(1.04);
        }}

        @media (prefers-reduced-motion: reduce) {{
            #lift-hover-img {{
                transition: none;
            }}

            #lift-hover-img:hover {{
                transform: none;
                filter: none;
            }}
        }}

        @media (max-width: 700px) {{
            .lift-art-shell {{
                width: min(240px, 82vw);
                height: min(240px, 82vw);
                padding: 4px;
                border-radius: 14px;
            }}

            #lift-hover-img {{
                border-radius: 10px;
            }}
        }}
        </style>
    </head>
    <body>
        <div class="lift-art-shell">
            <img
                id="lift-hover-img"
                src="{frames[0]}"
                alt="LIFT Agent pointillism animation"
                tabindex="0"
            />
        </div>

        <script>
        (function() {{
            const frames = [{frames_js_array}];
            const img = document.getElementById("lift-hover-img");

            if (!img || frames.length < 2) {{
                return;
            }}

            let index = 0;
            let intervalId = null;

            function startCycle() {{
                if (intervalId) {{
                    return;
                }}

                index = 0;

                intervalId = setInterval(function() {{
                    index += 1;

                    if (index >= frames.length) {{
                        index = frames.length - 1;
                        img.style.opacity = "0.72";
                        img.src = frames[index];
                        window.setTimeout(function() {{ img.style.opacity = "1"; }}, 220);
                        clearInterval(intervalId);
                        intervalId = null;
                        return;
                    }}

                    img.style.opacity = "0.72";
                    img.src = frames[index];
                    window.setTimeout(function() {{ img.style.opacity = "1"; }}, 220);
                }}, {frame_delay_ms});
            }}

            function resetCycle() {{
                if (intervalId) {{
                    clearInterval(intervalId);
                    intervalId = null;
                }}

                index = 0;
                img.src = frames[0];
            }}

            img.addEventListener("mouseenter", startCycle);
            img.addEventListener("mouseleave", resetCycle);
            img.addEventListener("focus", startCycle);
            img.addEventListener("blur", resetCycle);
        }})();
        </script>
    </body>
    </html>
    """

    components.html(component_html, height=height_px + 34, scrolling=False)


def render_what_image(image_path: Path = WHAT_IMAGE_PATH) -> None:
    """Render the clean LIFT information image immediately after the animation."""
    if not image_path.is_file():
        st.warning(f"Info image not found: `{image_path.as_posix()}`")
        return

    try:
        image_data_uri = _encode_image_to_data_uri(image_path)
    except Exception as exc:
        st.warning(f"Info image was found but could not be loaded: {exc}")
        return

    st.markdown(
        f"""
        <div class="lift-what-wrap">
            <img
                class="lift-what-image"
                src="{image_data_uri}"
                alt="What LIFT helps with"
            />
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_scroll_cta(
    target_anchor_id: str = "lift-form-section",
    label: str = "Let’s LIFT You Up",
) -> None:
    """
    Render a button-styled anchor link that scrolls down the same page.

    This is intentionally not st.button().
    A true st.button() causes a Streamlit rerun and is unreliable for same-click scrolling.
    """
    safe_target = html.escape(target_anchor_id, quote=True)
    safe_label = html.escape(label)

    st.markdown(
        f"""
        <div class="lift-scroll-wrap">
            <a class="lift-scroll-button" href="#{safe_target}">
                {safe_label}
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_anchor(anchor_id: str) -> None:
    """Render an invisible anchor target for in-page scrolling."""
    safe_anchor = html.escape(anchor_id, quote=True)
    st.markdown(f'<div id="{safe_anchor}" style="height: 1px;"></div>', unsafe_allow_html=True)


def render_lift_explainer() -> None:
    """Render a simple visual explanation of LIFT for non-technical users."""
    st.markdown(
        """
        <h2 class="lift-section-title">How LIFT Works</h2>
        <div class="lift-section-subtitle">
            Four simple steps: find options, understand barriers, prepare what to say, and track what happens next.
        </div>
        """,
        unsafe_allow_html=True,
    )

    rows = [
        ("L", "Locate", "Find public resource options based on the need, location, and access limits."),
        ("I", "Identify", "Notice possible barriers early, like hours, eligibility, transportation, or documents."),
        ("F", "Follow-up", "Create respectful outreach language the user can review before using."),
        ("T", "Track", "Organize next steps, status, dates, notes, and follow-up actions."),
    ]

    cols = st.columns(4)

    for col, (letter, word, description) in zip(cols, rows):
        with col:
            st.markdown(
                f"""
                <div class="lift-explainer-card">
                    <div>
                        <span class="lift-explainer-letter">{html.escape(letter)}</span>
                        <span class="lift-explainer-word">{html.escape(word)}</span>
                    </div>
                    <div class="lift-explainer-desc">{html.escape(description)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_soft_intro_card() -> None:
    """Render a small user-friendly card before the form."""
    st.markdown(
        f"""
        <div class="lift-soft-card">
            <strong style="color:{LIFT_COLORS['deep_teal']};">Start simple.</strong>
            <div class="lift-small-note" style="margin-top:0.35rem;">
                You do not need to know the perfect agency or program name. Start with the kind of help needed,
                where to look, and anything that could make access harder.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_archived_project_panel(
    supported_languages: List[str],
    openai_available: bool,
    api_key_present: bool,
) -> None:
    """
    Render archived project notes if called by a future page.

    This helper does not control the main page.
    It does not switch pages.
    It does not call st.stop().
    """
    with st.container():
        st.markdown("### LIFT Agent")
        st.caption("Archived panel. Optional. The main app works without using this.")

        with st.expander("⚙️ Settings", expanded=False):
            current_language = st.session_state.get("language", "English")

            language_index = (
                supported_languages.index(current_language)
                if current_language in supported_languages
                else 0
            )

            language_choice = st.selectbox(
                "Display language",
                supported_languages,
                index=language_index,
                key="archived_language_select",
            )

            st.session_state["language"] = language_choice

            current_need = st.session_state.get("language_access_needed", "No preference")

            language_need_options = ["No preference"] + [
                language for language in supported_languages if language != "English"
            ]

            need_index = (
                language_need_options.index(current_need)
                if current_need in language_need_options
                else 0
            )

            language_need_choice = st.selectbox(
                "Service language need",
                language_need_options,
                index=need_index,
                key="archived_language_need_select",
            )

            st.session_state["language_access_needed"] = language_need_choice

            if not api_key_present:
                st.info(
                    "OPENAI_API_KEY is not set. The app can still run with external public data "
                    "when reachable and a clearly labeled demo fallback route."
                )
            elif not openai_available:
                st.warning("The OpenAI package could not be imported in this environment.")
            else:
                st.success("OpenAI package and API key appear available.")

        with st.expander("🎓 Demo / Class Project Notes", expanded=False):
            st.markdown(
                """
- This is a **Project 3 human-supervised agent** for a Generative AI course.
- LIFT means **Locate, Identify, Follow-up, Track**.
- Public external data source: **OpenStreetMap / Nominatim**.
- If public search returns no usable results, that action uses clearly labeled fallback data.
- Provider details still need direct verification before real-world use.
"""
            )

        with st.expander("🔐 Security and Privacy Roadmap", expanded=False):
            st.markdown(
                """
Future production features could include:

- User login
- Multi-factor authentication
- Role-based access control
- Consent-based outreach only
- No automatic provider contact
- Audit logs
- Encrypted storage
- Limited permissions
- Saved user sessions
- Human review before outreach
"""
            )

        with st.expander("🛣️ Future Work", expanded=False):
            st.markdown(
                """
- Stronger resource directory integrations
- Ongoing provider validation monitoring
- Accessibility testing
- Keyboard and screen-reader review
- Multilingual human review
- Admin/coordinator dashboard
- Saved tracker history
- Provider status re-checks over time
"""
            )

        with st.expander("🧾 Project Evidence", expanded=False):
            route_trace = st.session_state.get("route_trace")
            tool_trace = st.session_state.get("tool_trace")
            data_source_trace = st.session_state.get("data_source_trace")
            provider_checks = st.session_state.get("provider_checks")

            if not any([route_trace, tool_trace, data_source_trace, provider_checks]):
                st.caption(
                    "No plan generated yet. Evidence will appear here after you generate a LIFT plan."
                )
            else:
                if route_trace:
                    st.markdown("**Route trace**")
                    st.json(route_trace)

                if tool_trace:
                    st.markdown("**Tool trace**")
                    st.json(tool_trace)

                if data_source_trace:
                    st.markdown("**External data trace**")
                    st.json(data_source_trace)

                if provider_checks:
                    st.markdown("**Provider check results**")
                    st.json(provider_checks)


def render_result_card(title: str, items: Optional[List[str]]) -> None:
    """Render one calm summary card."""
    safe_title = html.escape(title)

    if not items:
        body = "<div class='lift-small-note'>Nothing flagged here right now.</div>"
    else:
        body = "<ul style='margin:0.35rem 0 0 1.1rem; padding:0;'>"
        for item in items:
            body += f"<li>{html.escape(str(item))}</li>"
        body += "</ul>"

    st.markdown(
        f"""
        <div class="lift-result-card">
            <h4>{safe_title}</h4>
            {body}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result_cards_from_tool_result(tool_result: dict) -> None:
    """
    Show a calm user-facing summary from the existing tool_result.
    This does not replace the existing dataframe, trace, tracker, or downloads.
    """
    if not tool_result:
        return

    recommended = tool_result.get("recommended_first_resource", "")

    if recommended:
        render_result_card("Best place to start", [recommended])

    combined_barriers = []
    combined_barriers.extend(tool_result.get("fit_concerns", []))
    combined_barriers.extend(tool_result.get("eligibility_barriers", []))
    combined_barriers.extend(tool_result.get("access_barriers", []))
    combined_barriers.extend(tool_result.get("twenty_four_seven_gaps", []))
    combined_barriers.extend(tool_result.get("validation_flags", []))

    render_result_card("Things to double-check", combined_barriers)

    contingency_titles = []
    for plan in tool_result.get("contingency_plans", []):
        title = plan.get("title")
        if title:
            contingency_titles.append(title)

    render_result_card("Backup options", contingency_titles)

    next_actions = []
    for row in tool_result.get("tracker_rows", [])[:5]:
        resource_name = row.get("Resource Name", "Resource")
        action = row.get("Next Action", "Verify details and record the result.")
        next_actions.append(f"{resource_name}: {action}")

    render_result_card("Next actions", next_actions)
