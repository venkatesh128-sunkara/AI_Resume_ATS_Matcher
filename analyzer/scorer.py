import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .nlp import clean_tokens, sentence_aware_phrases, pos_noun_phrases, find_skill_mentions
from .skills_data import (
    SKILL_CATEGORIES,
    ALL_SKILLS,
    EDUCATION_LEVELS,
    SECTION_HEADINGS,
)

EMAIL_RE = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
PHONE_RE = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)\d{3}[-.\s]?\d{4}")
LINKEDIN_RE = re.compile(r"(?:linkedin\.com/in/|linkedin\.com)[a-zA-Z0-9\-_/]*", re.IGNORECASE)
YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

EXPERIENCE_PATTERNS = [
    r"(\d{1,2})\s*\+?\s*(?:years|yrs)[a-z\s]*experience",
    r"experience[a-z\s]*(\d{1,2})\s*(?:years|yrs)",
]

BOILERPLATE_WORDS = {
    "experience", "requirements", "requirement", "requisite", "skills", "skill",
    "knowledge", "proficiency", "bonus", "nice", "preferred", "strong", "hands",
    "years", "familiarity", "must", "plus", "points", "value", "working", "work",
    "development", "develop", "design", "build", "scale", "products", "team",
    "teams", "engineers", "including", "such", "least", "well", "engineer",
    "senior", "junior", "role", "roles", "position", "responsibilities",
    "duties", "hiring", "join", "platform", "power", "understanding",
}

WEIGHTS = {
    "Contact Information": 5,
    "Section Structure": 10,
    "Keyword Match": 25,
    "Skills Match": 25,
    "Experience": 15,
    "Education": 10,
    "ATS Formatting": 10,
}
SEMANTIC_BONUS_MAX = 10.0


def extract_contact_info(text: str):
    return {
        "email": list(set(EMAIL_RE.findall(text))),
        "phone": list(set(PHONE_RE.findall(text))),
        "linkedin": list(set(LINKEDIN_RE.findall(text))),
    }


def detect_sections(text: str):
    lines = [l.strip().strip(":-").lower() for l in text.splitlines() if l.strip()]
    found = []
    for line in lines:
        words = len(line.split())
        if 1 <= words <= 5 and line in SECTION_HEADINGS:
            found.append(line)
    return sorted(set(found))


def extract_keywords(jd_text: str, top_n: int = 30):
    candidates = set()
    for chunk in pos_noun_phrases(jd_text):
        toks = chunk.split()
        if not toks:
            continue
        if len(toks) == 1:
            if toks[0] not in BOILERPLATE_WORDS:
                candidates.add(chunk)
            continue
        if len(toks) <= 3 and not any(w in BOILERPLATE_WORDS for w in toks):
            candidates.add(chunk)
        for i in range(len(toks) - 1):
            window = toks[i : i + 2]
            if not any(w in BOILERPLATE_WORDS for w in window):
                candidates.add(" ".join(window))
    kept = []
    for cand in candidates:
        words = cand.split()
        if cand in ALL_SKILLS or all(w in ALL_SKILLS for w in words):
            continue
        kept.append(cand)
    kept.sort(key=lambda c: (len(c.split()), c), reverse=True)
    return kept[:top_n]


def canonical(phrase: str) -> str:
    return " ".join(clean_tokens(phrase))


def tfidf_similarity(resume_text: str, jd_text: str) -> float:
    try:
        corpus = [jd_text, resume_text]
        vec = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vec.fit_transform(corpus)
        return float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
    except Exception:
        return 0.0


def extract_experience_years(text: str) -> float:
    years = []
    for pattern in EXPERIENCE_PATTERNS:
        years.extend(int(m) for m in re.findall(pattern, text, re.IGNORECASE))
    if not years:
        years = [abs(int(m) - int(y)) for m, y in zip(re.findall(YEAR_RE, text)[:-1], re.findall(YEAR_RE, text)[1:]) if 0 < abs(int(m) - int(y)) < 40]
    return float(max(years)) if years else 0.0


def extract_highest_education(text: str):
    lowered = text.lower()
    for level in sorted(EDUCATION_LEVELS, key=lambda l: EDUCATION_LEVELS[l], reverse=True):
        if re.search(r"(^|[\s\W])" + re.escape(level) + r"([\s\W]|$)", lowered):
            return level, EDUCATION_LEVELS[level]
    return None, 0


def assess_ats_formatting(resume_text: str, contact: dict, sections: list) -> dict:
    checks = {}
    if contact["email"] and contact["phone"]:
        checks["Contact information present"] = True
    else:
        checks["Contact information present"] = False
    if any("education" in s for s in sections):
        checks["Education section present"] = True
    else:
        checks["Education section present"] = False
    if any("experience" in s or "work experience" in s for s in sections):
        checks["Work experience section present"] = True
    else:
        checks["Work experience section present"] = False
    if any("skill" in s for s in sections):
        checks["Skills section present"] = True
    else:
        checks["Skills section present"] = False
    if any("project" in s for s in sections):
        checks["Projects section present"] = True
    else:
        checks["Projects section present"] = False

    no_images = len(re.findall(r"\[image\]|image:|data:image", resume_text, re.IGNORECASE)) == 0
    checks["No embedded images/photos"] = no_images
    checks["Text length reasonable"] = len(resume_text) >= 400

    passed = sum(1 for v in checks.values() if v)
    return {"passed": passed, "total": len(checks), "checks": checks}


def analyze_resume(resume_text: str, job_description: str) -> dict:
    resume_text = resume_text or ""
    job_description = job_description or ""
    if not resume_text:
        raise ValueError("Resume text is empty")

    contact = extract_contact_info(resume_text)
    sections = detect_sections(resume_text)
    jd_keywords = extract_keywords(job_description)
    resume_phrases = sentence_aware_phrases(resume_text)
    jd_phrases = sentence_aware_phrases(job_description)

    matched_keywords = [kw for kw in jd_keywords if canonical(kw) in resume_phrases]
    missing_keywords = [kw for kw in jd_keywords if canonical(kw) not in resume_phrases]

    resume_skills = find_skill_mentions(resume_text, ALL_SKILLS)
    jd_skills = find_skill_mentions(job_description, ALL_SKILLS)
    matched_skills = [s for s in jd_skills if s in resume_skills]
    missing_skills = [s for s in jd_skills if s not in resume_skills]

    skill_categories_present = []
    for category, skills in SKILL_CATEGORIES.items():
        if any(s in resume_skills for s in skills):
            skill_categories_present.append(category)

    experience = extract_experience_years(resume_text)
    edu_level, edu_score = extract_highest_education(resume_text)
    similarity = tfidf_similarity(resume_text, job_description)
    ats = assess_ats_formatting(resume_text, contact, sections)

    contact_score = WEIGHTS["Contact Information"] * min(1.0, sum(bool(v) for v in contact.values()) / 3.0)
    section_score = WEIGHTS["Section Structure"] * (ats["passed"] / ats["total"])
    keyword_score = WEIGHTS["Keyword Match"] * (len(matched_keywords) / max(1, len(jd_keywords)))
    skill_score = WEIGHTS["Skills Match"] * (len(matched_skills) / max(1, len(jd_skills)))
    experience_score = WEIGHTS["Experience"] * min(1.0, experience / 5.0)
    education_score = WEIGHTS["Education"] * min(1.0, edu_score / 8.0)
    ats_score = WEIGHTS["ATS Formatting"] * (ats["passed"] / ats["total"])
    semantic_bonus = SEMANTIC_BONUS_MAX * max(0.0, min(1.0, similarity))

    breakdown = {
        "Contact Information": round(contact_score, 1),
        "Section Structure": round(section_score, 1),
        "Keyword Match": round(keyword_score, 1),
        "Skills Match": round(skill_score, 1),
        "Experience": round(experience_score, 1),
        "Education": round(education_score, 1),
        "ATS Formatting": round(ats_score, 1),
        "Semantic Similarity (bonus)": round(semantic_bonus, 1),
    }

    total = min(100.0, sum(v for k, v in breakdown.items() if k != "Semantic Similarity (bonus)") + semantic_bonus)
    total = round(total, 1)

    suggestions = build_suggestions(
        contact, ats, matched_keywords, missing_keywords,
        matched_skills, missing_skills, jd_skills, experience,
    )

    return {
        "total_score": total,
        "breakdown": breakdown,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "required_skills": jd_skills,
        "skill_categories": skill_categories_present,
        "experience_years": experience,
        "education": edu_level,
        "semantic_similarity": round(similarity, 3),
        "weights": {**WEIGHTS, "Semantic Similarity (bonus)": SEMANTIC_BONUS_MAX},
        "contact": contact,
        "sections": sections,
        "ats_checks": ats["checks"],
        "suggestions": suggestions,
    }


def build_suggestions(contact, ats, matched_kw, missing_kw, matched_sk, missing_sk, jd_skills, experience):
    suggestions = []
    if not contact["email"] or not contact["phone"]:
        suggestions.append("Add your email address and phone number to the top of the resume.")
    if not contact["linkedin"]:
        suggestions.append("Add your LinkedIn profile URL. Recruiters and ATS software often look for it.")
    if not ats["checks"].get("Education section present"):
        suggestions.append("Add a dedicated Education section with degree, institution, and year of completion.")
    if not ats["checks"].get("Work experience section present"):
        suggestions.append("Add a Work Experience section with clear job titles, company names, and date ranges.")
    if not ats["checks"].get("Skills section present"):
        suggestions.append("Add a Skills section listing your core technical skills in plain text.")
    if not ats["checks"].get("Projects section present"):
        suggestions.append("Add a Projects section to showcase relevant work and quantifiable outcomes.")
    if ats["checks"].get("No embedded images/photos") is False:
        suggestions.append("Remove embedded images and photos - many ATS systems cannot read them.")
    if not ats["checks"].get("Text length reasonable"):
        suggestions.append("Your resume text is quite short; add more detail about roles, projects, and achievements.")
    if missing_kw:
        top = ", ".join(missing_kw[:8])
        suggestions.append(f"Missing important keywords from the job description: {top}. Work these terms naturally into your summary and bullet points.")
    if missing_sk:
        top = ", ".join(missing_sk[:8])
        suggestions.append(f"Missing key skills the job requires: {top}. Add them if you genuinely have them.")
    if experience and experience < 2:
        suggestions.append("Highlight internships, freelance work, and academic projects to compensate for limited experience.")
    if len(matched_sk) / max(1, len(jd_skills)) < 0.6:
        suggestions.append("Cover more of the required skills or re-word your resume to use the exact skill names from the job posting.")
    if not suggestions:
        suggestions.append("Great resume! Consider tailoring bullet points further by adding measurable results (e.g., 'increased X by 20%').")
    return suggestions
