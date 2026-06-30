import json
from io import StringIO
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from rich.console import Console

load_dotenv(override=True)

from src.agent import ViralMomentHijacker  # noqa: E402 — must load .env first

st.set_page_config(
    page_title="Viral Moment Hijacker",
    page_icon="🚀",
    layout="wide",
)

st.title("🚀 Viral Moment Hijacker")
st.caption("AI-powered trend + influencer marketing agent — powered by Gemini")

# ── Sidebar ────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("Campaign Setup")

    brand_name = st.text_input("Brand Name *", placeholder="Forkly")
    brand_description = st.text_area(
        "Brand Description *",
        placeholder="Fun meal kit brand delivering weekly recipe kits to millennials and Gen Z",
        height=90,
    )
    industry = st.text_input("Industry *", placeholder="food, fitness, beauty, fintech…")
    platform = st.selectbox("Platform", ["Instagram", "TikTok", "LinkedIn"])
    tone = st.text_input("Tone", value="casual", placeholder="casual, professional, witty…")
    brand_values = st.text_input(
        "Brand Values",
        value="authentic, creative, community-driven",
    )

    st.divider()
    st.subheader("Optional Agents")
    use_influencers = st.checkbox("Find influencers + write DM pitches")
    use_email = st.checkbox("Write + send customer email")

    st.divider()
    run_button = st.button("Run Campaign", type="primary", use_container_width=True)


# ── Results renderer ───────────────────────────────────────────────────────────

def display_campaign(campaign: dict, platform: str) -> None:
    trend = campaign.get("viral_trend", "—")
    brand_angle = campaign.get("brand_angle", "—")
    trend_summary = campaign.get("trend_summary", "")
    pitches = campaign.get("influencer_pitches", [])
    distribution = campaign.get("distribution", {})
    email_subs = distribution.get("customer_email_subscribers") or 0

    # Top metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Viral Trend", trend[:38] + ("…" if len(trend) > 38 else ""))
    col2.metric("Influencer Pitches", len(pitches) if pitches else "—")
    col3.metric("Email Reach", f"{email_subs:,}" if email_subs else "—")

    st.divider()

    # Campaign summary
    st.subheader("Campaign Summary")
    left, right = st.columns(2)
    with left:
        st.markdown("**Viral Trend**")
        st.info(trend)
        if trend_summary:
            st.caption(trend_summary)
    with right:
        st.markdown("**Brand Angle**")
        st.success(brand_angle)

    # Brand post
    brand_post = campaign.get("brand_post", "")
    if brand_post:
        st.subheader(f"{platform} Post")
        st.text_area(
            label="brand_post",
            value=brand_post,
            height=160,
            disabled=True,
            label_visibility="collapsed",
        )

    # Influencer DM pitches
    if pitches:
        st.subheader("Influencer DM Pitches")
        for pitch in pitches:
            name = pitch.get("name", "Unknown")
            handle = pitch.get("handle", "")
            followers = pitch.get("followers", "—")
            fit_score = pitch.get("fit_score", "")
            dm = pitch.get("dm_pitch", "")
            label = f"{name} ({handle})  ·  {followers} followers"
            if fit_score:
                label += f"  ·  Fit {fit_score}/10"
            with st.expander(label):
                st.text_area(
                    label="dm",
                    value=dm,
                    height=220,
                    disabled=True,
                    label_visibility="collapsed",
                    key=f"dm_{handle}",
                )

    # Hashtag strategy
    hashtags = campaign.get("hashtag_strategy", {})
    groups = hashtags.get("groups") or hashtags
    if groups.get("broad") or groups.get("niche"):
        st.subheader("Hashtag Strategy")
        formula = hashtags.get("caption_formula", "")
        cols = st.columns(4)
        for col, (label, key) in zip(
            cols,
            [("Broad", "broad"), ("Niche", "niche"), ("Brand", "branded"), ("Trend", "trend")],
        ):
            tags = groups.get(key, [])
            if tags:
                col.markdown(f"**{label}**")
                col.markdown("  \n".join(tags))
        if formula:
            st.caption(f"Caption formula: {formula}")

    # Content calendar
    calendar = campaign.get("content_calendar", [])
    if calendar:
        st.subheader("7-Day Content Calendar")
        rows = [
            {
                "Day": e.get("day", ""),
                "Format": e.get("format", ""),
                "Time": e.get("optimal_time", ""),
                "Caption": e.get("caption", "")[:120],
                "Hook": e.get("hook", ""),
            }
            for e in calendar
        ]
        st.dataframe(rows, use_container_width=True)

    # Distribution
    social_url = distribution.get("social_post_url", "")
    email_subject = distribution.get("customer_email_subject", "")
    email_body = distribution.get("customer_email_body", "")

    if social_url or email_subject:
        st.subheader("Distribution")
        if social_url:
            st.markdown(f"**{platform} post:** {social_url}")
        if email_subject:
            with st.expander(f'Customer email: "{email_subject}"'):
                if email_body:
                    st.text(email_body)
                else:
                    st.caption(f"Sent to {email_subs:,} subscribers")

    # Download
    st.divider()
    brand_slug = campaign.get("metadata", {}).get("brand", "campaign").replace(" ", "_")
    st.download_button(
        "Download Campaign JSON",
        data=json.dumps(campaign, indent=2),
        file_name=f"campaign_{brand_slug}.json",
        mime="application/json",
    )


# ── Main logic ─────────────────────────────────────────────────────────────────

if run_button:
    missing = [f for f, v in [("Brand Name", brand_name), ("Brand Description", brand_description), ("Industry", industry)] if not v]
    if missing:
        st.error(f"Please fill in: {', '.join(missing)}")
        st.stop()

    log_buffer = StringIO()
    # Rich console writes to a buffer so it doesn't conflict with Streamlit's output
    console = Console(file=log_buffer, markup=True, highlight=False, no_color=True)

    with st.spinner("Running campaign pipeline… this usually takes 1–2 minutes"):
        try:
            agent = ViralMomentHijacker(
                brand_name=brand_name,
                brand_description=brand_description,
                tone=tone,
                brand_values=brand_values,
                console=console,
                use_influencers=use_influencers,
                use_email=use_email,
            )
            saved_path = agent.run_campaign(industry=industry, platform=platform)
        except ValueError as e:
            st.error(f"Configuration error: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Pipeline error: {e}")
            with st.expander("Pipeline log"):
                st.text(log_buffer.getvalue())
            st.stop()

    st.success("Campaign complete!")

    if saved_path and Path(saved_path).exists():
        with open(saved_path, "r", encoding="utf-8") as f:
            campaign = json.load(f)
        display_campaign(campaign, platform)
    else:
        st.warning("Pipeline finished but no output file was saved. Check the log below.")

    with st.expander("Pipeline log"):
        st.text(log_buffer.getvalue())

else:
    st.markdown("""
Fill in your brand details in the sidebar and click **Run Campaign**.

The pipeline will:

1. **Discover** what's going viral in your industry right now
2. **Strategize** the best angle for your brand to join the conversation
3. **Identify** relevant influencers and write personalized DM pitches *(optional)*
4. **Create** a reactive brand post optimized for your platform
5. **Plan** a 7-day content calendar
6. **Write** a trend-inspired customer email *(optional)*

Results are displayed here and saved to `output/campaigns/` as JSON.
""")
