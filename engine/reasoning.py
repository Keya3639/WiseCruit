"""Reasoning generator for WiseCruit."""

def generate_reasoning(candidate, scores, rank):
    profile = candidate.get("profile", {})
    signals = candidate.get("redrob_signals", {})
    skills = candidate.get("skills", [])
    career = candidate.get("career_history", [])
    
    title = profile.get("current_title", "Professional")
    years = profile.get("years_of_experience", 0)
    
    top_skills = sorted(skills, key=lambda s: s.get("endorsements", 0), reverse=True)[:3]
    skill_names = [s["name"] for s in top_skills]
    
    response_rate = signals.get("recruiter_response_rate", 0)
    notice_days = signals.get("notice_period_days", 90)
    interview_rate = signals.get("interview_completion_rate", 0)
    
    career_score = scores.get("career_match", 0)
    skill_score = scores.get("skill_match", 0)
    trust_score = scores.get("trust_score", 100)
    hiring_score = scores.get("hiring_readiness", 0)
    
    parts = []
    
    # Check for hidden talent — ML experience in career description but not in skills
    skills_text = " ".join([s["name"].lower() for s in skills])
    career_text = " ".join([job.get("description", "").lower() for job in career])
    
    hidden_signals = {
        "ranking": ["ranking", "ranked", "rank"],
        "retrieval": ["retrieval", "retrieve", "search system"],
        "embeddings": ["embedding", "sentence transformer", "vector"],
        "recommendation": ["recommendation", "recommender"],
        "deployment": ["deploy", "production", "shipped"],
    }
    
    hidden_found = []
    for category, terms in hidden_signals.items():
        if any(t in career_text for t in terms) and not any(t in skills_text for t in terms):
            hidden_found.append(category)
    
    if hidden_found:
        parts.append(f"hidden expertise detected: {', '.join(hidden_found[:2])}")
    
    # Career & experience summary
    if career_score > 70:
        parts.append(f"Strong career alignment with {years}y experience")
    elif career_score > 40:
        parts.append(f"Partial career alignment")
    else:
        parts.append(f"{title} with limited role relevance")
    
    # Skills highlight
    if skill_score > 70 and skill_names:
        parts.append(f"relevant skills ({', '.join(skill_names[:2])})")
    elif skill_names:
        parts.append(f"some skills ({skill_names[0]})")
    
    # Behavioral notes
    notes = []
    if response_rate > 0.7: notes.append(f"high recruiter response ({response_rate:.0%})")
    elif response_rate < 0.3: notes.append(f"low response rate ({response_rate:.0%})")
    if interview_rate > 0.8: notes.append("strong interview attendance")
    if notice_days > 90: notes.append(f"{notice_days}d notice (long)")
    elif notice_days <= 30: notes.append(f"{notice_days}d notice (short)")
    
    # Concerns
    concerns = []
    if trust_score < 50: concerns.append("profile consistency concerns")
    if hiring_score < 30: concerns.append("low hiring readiness")
    
    # Build final reasoning
    reasoning = "; ".join(parts)
    if notes: reasoning += ". " + "; ".join(notes) + "."
    if concerns: reasoning += f" Concerns: {', '.join(concerns)}."
    
    # Tone matching
    if rank <= 10 and career_score > 60: reasoning = "Excellent fit: " + reasoning
    elif rank <= 30: reasoning = "Good match: " + reasoning
    elif rank <= 60: reasoning = "Moderate fit: " + reasoning
    else: reasoning = "Marginal fit: " + reasoning
    
    if len(reasoning) > 300: reasoning = reasoning[:297] + "..."
    return reasoning