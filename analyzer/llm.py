import json
import os

SYSTEM_PROMPT = """You are a senior technical recruiter and ATS (Applicant Tracking System) expert.
Analyze the resume against the job description and return STRICT JSON only, with no markdown fences, using exactly this schema:
{
  "overall_feedback": "string, 2-3 sentences on overall fit",
  "strengths": ["array of strings, strong points of the resume for this role"],
  "weaknesses": ["array of strings, gaps between resume and job description"],
  "missing_keywords": ["array of strings, high-value terms from the JD absent from the resume"],
  "tailored_suggestions": ["array of strings, concrete actions to improve the resume"],
  "interview_readiness": 0-100 (integer)
}"""


def llm_analyze(resume_text, job_description, api_key=None, base_url=None, model="gpt-4o-mini"):
    """Run LLM analysis. Returns dict with an 'enabled' flag and result fields.
    If no API key is provided or the call fails, returns a safe fallback dict."""
    api_key = api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return {
            "enabled": False,
            "feedback": "No OpenAI API key configured. The rule-based ATS analysis was used instead.",
        }

    try:
        from openai import OpenAI
        kwargs = {"api_key": api_key}
        if base_url:
            kwargs["base_url"] = base_url
        client = OpenAI(**kwargs)

        user_prompt = (
            "JOB DESCRIPTION:\n" + job_description[:12000] +
            "\n\nRESUME:\n" + resume_text[:12000] +
            "\n\nProvide the JSON analysis."
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        data = json.loads(content)
        return {
            "enabled": True,
            "feedback": data.get("overall_feedback", ""),
            "strengths": data.get("strengths", []),
            "weaknesses": data.get("weaknesses", []),
            "missing_keywords": data.get("missing_keywords", []),
            "tailored_suggestions": data.get("tailored_suggestions", []),
            "interview_readiness": data.get("interview_readiness", None),
        }
    except Exception as exc:
        return {
            "enabled": False,
            "feedback": f"LLM analysis unavailable ({type(exc).__name__}). The rule-based ATS analysis was used instead.",
            "error": str(exc),
        }
