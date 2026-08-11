import streamlit as st

from analyzer import extract_text, analyze_resume
from analyzer.llm import llm_analyze

st.set_page_config(page_title="AI Resume ATS Analyzer", page_icon="\U0001F4C4", layout="wide")

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(1100px 500px at 10% -10%, rgba(56, 189, 248, 0.22), transparent 60%),
        radial-gradient(900px 500px at 95% 5%, rgba(99, 102, 241, 0.18), transparent 60%),
        linear-gradient(160deg, #eef7ff 0%, #dceefe 35%, #e8f2ff 70%, #f4f9ff 100%);
    background-attachment: fixed;
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
    color: #1e293b;
}

[data-testid="stHeader"] { background: transparent; }
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.65) !important;
    backdrop-filter: blur(10px);
    border-right: 1px solid rgba(147, 197, 253, 0.5);
}

.hero {
    text-align: center;
    padding: 8px 0 4px 0;
    animation: fadeInUp 0.7s ease both;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
    background: linear-gradient(90deg, #1d4ed8, #0ea5e9, #6366f1, #1d4ed8);
    background-size: 300% 100%;
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: gradientFlow 6s ease infinite;
}
.hero-sub {
    margin: 6px 0 0 0;
    color: #475569;
    font-size: 1.05rem;
    font-weight: 600;
    opacity: 0.9;
}

.orbs { position: fixed; inset: 0; pointer-events: none; z-index: 0; overflow: hidden; }
.orb {
    position: absolute;
    border-radius: 50%;
    filter: blur(60px);
    opacity: 0.45;
    animation: float 12s ease-in-out infinite;
}
.o1 { width: 340px; height: 340px; background: #7dd3fc; top: -80px; left: -80px; }
.o2 { width: 300px; height: 300px; background: #a5b4fc; bottom: -90px; right: -60px; animation-delay: -4s; }
.o3 { width: 240px; height: 240px; background: #bfdbfe; top: 40%; left: 75%; animation-delay: -8s; }

[data-testid="stMetric"] {
    background: rgba(255, 255, 255, 0.75);
    border: 1px solid rgba(147, 197, 253, 0.6);
    border-radius: 16px;
    padding: 14px 18px;
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.12);
    backdrop-filter: blur(6px);
    animation: fadeInUp 0.6s ease both;
}
[data-testid="stMetric"]:hover { transform: translateY(-3px); box-shadow: 0 12px 30px rgba(59, 130, 246, 0.22); }
[data-testid="stMetric"] { transition: transform 0.25s ease, box-shadow 0.25s ease; }
[data-testid="stMetricLabel"] { color: #475569; font-weight: 600; }
[data-testid="stMetricValue"] { color: #1d4ed8; font-weight: 800; }

.stMarkdown, .stText { animation: fadeInUp 0.5s ease both; }

h1, h2, h3 { color: #0f2a4a; }
[data-testid="stHeading"] h2, .stMarkdown h2, .stMarkdown h3 {
    background: linear-gradient(90deg, #1d4ed8, #0ea5e9);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    display: inline-block;
}

.stButton > button, [data-testid="stDownloadButton"] > button {
    background: linear-gradient(135deg, #2563eb 0%, #38bdf8 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 22px !important;
    box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35) !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    animation: pulse 2.4s ease-in-out infinite;
}
.stButton > button:hover, [data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-2px) scale(1.02) !important;
    box-shadow: 0 10px 28px rgba(37, 99, 235, 0.5) !important;
}

[data-testid="stProgress"] { animation: fadeInUp 0.6s ease both; }
[data-testid="stProgress"] > div > div > div > div {
    background: linear-gradient(90deg, #38bdf8, #6366f1, #38bdf8) !important;
    background-size: 200% 100% !important;
    animation: progressFlow 2.4s linear infinite;
    border-radius: 8px !important;
}

[data-testid="stFileUploader"] {
    background: rgba(255, 255, 255, 0.75);
    border: 1.5px dashed #93c5fd !important;
    border-radius: 14px !important;
    padding: 8px;
    backdrop-filter: blur(6px);
}
[data-testid="stTextArea"] textarea, [data-testid="stTextInput"] input {
    border-radius: 12px !important;
    background: rgba(255, 255, 255, 0.8) !important;
    border-color: #bfdbfe !important;
}
[data-testid="stTextArea"] textarea:focus, [data-testid="stTextInput"] input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.15) !important;
}

[data-testid="stSuccess"], [data-testid="stWarning"], [data-testid="stError"] {
    border-radius: 12px !important;
    animation: fadeInUp 0.5s ease both;
}

.score-badge {
    display: inline-block;
    font-size: 3.4rem;
    font-weight: 800;
    color: #ffffff;
    background: linear-gradient(135deg, #2563eb, #38bdf8);
    padding: 10px 34px;
    border-radius: 20px;
    box-shadow: 0 10px 34px rgba(37, 99, 235, 0.45);
    animation: pop 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both, glow 2.5s ease-in-out infinite;
}
.tag {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 0.85rem;
    font-weight: 700;
    margin: 3px 4px 3px 0;
    animation: fadeInUp 0.5s ease both;
}
.tag-ok   { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
.tag-warn { background: #fef9c3; color: #a16207; border: 1px solid #fde047; }

@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(14px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes gradientFlow {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes float {
    0%, 100% { transform: translate(0, 0) scale(1); }
    33% { transform: translate(24px, -18px) scale(1.06); }
    66% { transform: translate(-16px, 14px) scale(0.96); }
}
@keyframes progressFlow {
    0% { background-position: 200% 0; }
    100% { background-position: 0 0; }
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35); }
    50% { box-shadow: 0 6px 28px rgba(37, 99, 235, 0.6); }
}
@keyframes pop {
    from { transform: scale(0.6); opacity: 0; }
    to   { transform: scale(1); opacity: 1; }
}
@keyframes glow {
    0%, 100% { box-shadow: 0 10px 34px rgba(37, 99, 235, 0.45); }
    50% { box-shadow: 0 10px 46px rgba(37, 99, 235, 0.7); }
}
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)


def render_hero():
    st.markdown(
        """
        <div class="orbs"><div class="orb o1"></div><div class="orb o2"></div><div class="orb o3"></div></div>
        <div class="hero">
            <h1 class="hero-title">\U0001F4C4 AI Resume ATS Analyzer</h1>
            <p class="hero-sub">Score, match &amp; optimize your resume against any job description</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_suggestions(suggestions):
    for s in suggestions:
        st.markdown(f"- {s}")


def render_tags(items, kind):
    cls = "tag-ok" if kind == "ok" else "tag-warn"
    if not items:
        st.markdown('<span class="tag tag-ok">None - great coverage!</span>' if kind == "warn" else '<span class="tag tag-warn">None</span>', unsafe_allow_html=True)
        return
    html = "".join(f'<span class="tag {cls}">{i}</span>' for i in items)
    st.markdown(html, unsafe_allow_html=True)


def main():
    inject_css()
    render_hero()

    with st.sidebar:
        st.header("\U00002699\U0000FE0F LLM Settings (optional)")
        api_key = st.text_input("OpenAI API Key", type="password",
                                help="Optional. Used for AI-powered feedback. Leave blank for rule-based analysis only.")
        base_url = st.text_input("API Base URL (optional)",
                                 help="e.g. https://openrouter.ai/api/v1 for OpenRouter or a local Ollama endpoint.")
        model = st.text_input("Model", value="gpt-4o-mini")
        use_llm = st.checkbox("Enable LLM feedback", value=bool(api_key))
        st.divider()
        st.caption("Supports PDF, DOCX, and TXT resumes. No file leaves your machine for the rule-based analysis.")

    col1, col2 = st.columns(2)
    with col1:
        uploaded = st.file_uploader("1. Upload your resume", type=["pdf", "docx", "txt"])
    with col2:
        jd_text = st.text_area("2. Paste the job description", height=220)

    if st.button("Analyze Resume", type="primary", use_container_width=True):
        if uploaded is None or not jd_text.strip():
            st.warning("Please upload a resume AND paste a job description first.")
            return

        try:
            resume_text = extract_text(uploaded.name, uploaded.getvalue())
        except Exception as exc:
            st.error(f"Could not read resume: {exc}")
            return

        if len(resume_text.strip()) < 50:
            st.error("The resume file appears to contain no readable text. Try a text-based PDF/DOCX (not a scanned image).")
            return

        result = analyze_resume(resume_text, jd_text)
        total = result["total_score"]

        st.markdown("---")
        top1, top2, top3, top4 = st.columns(4)
        top1.metric("Overall ATS Score", f"{total} / 100")
        top2.metric("Keyword Match", f"{len(result['matched_keywords'])} / {len(result['matched_keywords']) + len(result['missing_keywords'])}")
        top3.metric("Skill Match", f"{len(result['matched_skills'])} / {len(result['matched_skills']) + len(result['missing_skills'])}")
        top4.metric("Experience (est.)", f"{result['experience_years']:.0f} yrs")

        st.markdown(
            f'<div style="text-align:center; padding:14px 0;">'
            f'<span class="score-badge">{total}</span>'
            f'<span style="font-size:1.2rem; font-weight:700; color:#334155; margin-left:12px;">/ 100</span></div>',
            unsafe_allow_html=True,
        )
        st.progress(total / 100.0)
        if total >= 80:
            st.success(f"Strong match \U0001F389")
        elif total >= 60:
            st.warning("Decent match - room for improvement")
        else:
            st.error("Weak match - needs tailoring")

        st.subheader("Score Breakdown")
        weights = result["weights"]
        for name, score in result["breakdown"].items():
            max_val = weights.get(name, 20)
            row = st.columns([3, 1, 6])
            row[0].write(name)
            row[1].write(f"{score} / {max_val:.0f}")
            row[2].progress(min(score, max_val) / max_val)

        st.markdown("---")
        left, right = st.columns(2)

        with left:
            st.subheader("\U00002705 Matched Keywords")
            render_tags(result["matched_keywords"], "ok")
            st.subheader("\U0000274C Missing Keywords")
            render_tags(result["missing_keywords"], "warn")

        with right:
            st.subheader("\U0001F9D1\u200D\U0001F4BB Matched Skills")
            render_tags(result["matched_skills"], "ok")
            st.subheader("\U0001F6AB Missing Skills")
            render_tags(result["missing_skills"], "warn")
            st.subheader("\U0001F3AF Skill Categories Covered")
            render_tags(result["skill_categories"], "ok")

        st.markdown("---")
        st.subheader("\U0001F4DD ATS Formatting Checks")
        checks = result["ats_checks"]
        for name, passed in checks.items():
            icon = "\U00002705" if passed else "\U0000274C"
            st.write(f"{icon} {name}")

        st.markdown("---")
        st.subheader("\U0001F4A1 Suggestions")
        render_suggestions(result["suggestions"])

        if use_llm and api_key:
            st.markdown("---")
            st.subheader("\U0001F916 LLM Feedback")
            with st.spinner("Running LLM analysis..."):
                llm = llm_analyze(resume_text, jd_text, api_key=api_key, base_url=base_url or None, model=model)
            if llm["enabled"]:
                if llm.get("interview_readiness") is not None:
                    st.metric("Interview Readiness", f"{llm['interview_readiness']} / 100")
                st.markdown(f"**Overall feedback:** {llm['feedback']}")
                c1, c2 = st.columns(2)
                c1.markdown("**Strengths**")
                render_suggestions(llm["strengths"])
                c2.markdown("**Weaknesses**")
                render_suggestions(llm["weaknesses"])
                st.markdown("**Tailored suggestions**")
                render_suggestions(llm["tailored_suggestions"])
            else:
                st.info(llm["feedback"])

        st.download_button(
            "Download Analysis Report",
            data=render_report(result),
            file_name="ats_report.txt",
            mime="text/plain",
        )


def render_report(result):
    lines = ["=" * 60, "AI RESUME ATS ANALYSIS REPORT", "=" * 60, ""]
    lines.append(f"Overall Score: {result['total_score']} / 100")
    lines.append("")
    lines.append("BREAKDOWN")
    weights = result["weights"]
    for name, score in result["breakdown"].items():
        max_val = weights.get(name, 20)
        lines.append(f"  {name}: {score} / {max_val:.0f}")
    lines.append("")
    lines.append(f"Keyword Match: {len(result['matched_keywords'])} matched, {len(result['missing_keywords'])} missing")
    lines.append(f"Skills Match : {len(result['matched_skills'])} matched, {len(result['missing_skills'])} missing")
    lines.append(f"Est. Experience: {result['experience_years']:.0f} years")
    lines.append(f"Education Detected: {result['education']}")
    lines.append(f"Semantic Similarity: {result['semantic_similarity']:.0%}")
    lines.append("")
    lines.append("MATCHED KEYWORDS: " + (", ".join(result["matched_keywords"]) or "None"))
    lines.append("MISSING KEYWORDS: " + (", ".join(result["missing_keywords"]) or "None"))
    lines.append("")
    lines.append("ATS CHECKS")
    for name, passed in result["ats_checks"].items():
        lines.append(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    lines.append("")
    lines.append("SUGGESTIONS")
    for s in result["suggestions"]:
        lines.append(f"  - {s}")
    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


if __name__ == "__main__":
    main()
