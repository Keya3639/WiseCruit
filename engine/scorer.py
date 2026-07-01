"""Multi-dimensional candidate scorer for WiseCruit."""
from datetime import datetime

class WiseCruitScorer:
    def __init__(self, jd_requirements):
        self.jd = jd_requirements
        self.today = datetime(2026, 7, 1)
        
    def score_candidate(self, candidate):
        scores = {}
        scores["skill_match"] = self._score_skills(candidate)
        scores["career_match"] = self._score_career(candidate)
        scores["experience_fit"] = self._score_experience(candidate)
        scores["education_fit"] = self._score_education(candidate)
        scores["location_fit"] = self._score_location(candidate)
        scores["company_fit"] = self._score_company(candidate)
        scores["hiring_readiness"] = self._score_behavior(candidate)
        scores["trust_score"] = self._score_trust(candidate)
        scores["startup_mindset"] = self._score_startup_mindset(candidate)
        scores["role_fit"] = self._compute_role_fit(scores)
        return scores
    
    def _score_skills(self, candidate):
        skills_list = [s["name"].lower() for s in candidate.get("skills", [])]
        skill_profs = {s["name"].lower(): s["proficiency"] for s in candidate.get("skills", [])}
        skill_durs = {s["name"].lower(): s.get("duration_months", 0) for s in candidate.get("skills", [])}
        skill_endos = {s["name"].lower(): s.get("endorsements", 0) for s in candidate.get("skills", [])}
        
        career_text = " ".join([job.get("description", "") for job in candidate.get("career_history", [])]).lower()
        profile_text = (candidate.get("profile", {}).get("summary", "") + " " + 
                       candidate.get("profile", {}).get("headline", "")).lower()
        all_text = career_text + " " + profile_text
        
        must_have_score = 0
        for skill in self.jd["must_have_skills"]:
            matched = False
            for cand_skill in skills_list:
                if skill in cand_skill or cand_skill in skill:
                    prof = skill_profs.get(cand_skill, "beginner")
                    dur = skill_durs.get(cand_skill, 0)
                    endo = skill_endos.get(cand_skill, 0)
                    prof_w = {"beginner": 0.3, "intermediate": 0.6, "advanced": 0.85, "expert": 1.0}
                    dur_b = min(dur / 36, 1.0)
                    endo_b = min(endo / 20, 1.0)
                    must_have_score += prof_w.get(prof, 0.3) * 0.5 + dur_b * 0.3 + endo_b * 0.2
                    matched = True
                    break
            if not matched and skill in all_text:
                must_have_score += 0.3
        
        max_mh = max(len(self.jd["must_have_skills"]), 1)
        must_have_score = (must_have_score / max_mh) * 100
        
        nice_score = 0
        for skill in self.jd["nice_to_have_skills"]:
            if any(skill in s for s in skills_list) or skill in all_text:
                nice_score += 1
        nice_score = (nice_score / max(len(self.jd["nice_to_have_skills"]), 1)) * 100
        
        penalty = 15 if "langchain" in skills_list else 0
        return max(must_have_score * 0.7 + nice_score * 0.3 - penalty, 0)
    
    def _score_career(self, candidate):
        current_title = candidate.get("profile", {}).get("current_title", "").lower()
        headline = candidate.get("profile", {}).get("headline", "").lower()
        career_history = candidate.get("career_history", [])
        career_desc = " ".join([j.get("description", "").lower() for j in career_history])
        career_titles = [j.get("title", "").lower() for j in career_history]
        
        for bad in self.jd["disqualify_titles"]:
            if bad in current_title or bad in headline:
                return 5
        
        ml_signals = ["ranking", "retrieval", "embedding", "recommendation", "search",
                      "machine learning", "nlp", "llm", "rag", "vector", "model",
                      "fine-tun", "deploy", "production ml", "a/b test", "ndcg", "mrr"]
        ml_count = sum(1 for sig in ml_signals if sig in career_desc)
        
        target_titles = ["ai engineer", "ml engineer", "machine learning", "data scientist",
                        "software engineer", "backend engineer", "search engineer", "ranking",
                        "nlp engineer", "data engineer", "devops", "full stack", "fullstack"]
        title_match = sum(1 for t in career_titles for tt in target_titles if tt in t)
        
        product_cos = ["zomato", "razorpay", "flipkart", "ola", "pied piper",
                      "hooli", "initech", "acme corp", "stark industries", "wayne enterprises"]
        has_product = any(j.get("company", "").lower() in product_cos for j in career_history)
        
        score = min(ml_count * 8, 40) + min(title_match * 10, 30) + (20 if has_product else 0)
        return min(score, 100)
    
    def _score_experience(self, candidate):
        years = candidate.get("profile", {}).get("years_of_experience", 0)
        tmin, tmax = self.jd["target_experience_min"], self.jd["target_experience_max"]
        if years < 2: return 10
        elif years < tmin: return 30 + (years / tmin) * 40
        elif tmin <= years <= tmax: return 100
        elif years <= tmax + 3: return 80
        elif years <= 15: return 50
        return 20
    
    def _score_education(self, candidate):
        education = candidate.get("education", [])
        if not education: return 20
        tier_scores = {"tier_1": 100, "tier_2": 75, "tier_3": 40, "tier_4": 20, "unknown": 30}
        relevant = ["computer science", "artificial intelligence", "machine learning",
                   "data science", "computer engineering", "information technology", "statistics", "mathematics"]
        best_tier = max(tier_scores.get(e.get("tier", "unknown"), 30) for e in education)
        field_bonus = 25 if any(any(rf in e.get("field_of_study", "").lower() for rf in relevant) for e in education) else 0
        degrees = [e.get("degree", "").lower() for e in education]
        degree_bonus = 15 if any(d in ["m.tech", "m.e.", "m.s.", "m.sc", "ph.d"] for d in degrees) else 0
        return min(best_tier + field_bonus + degree_bonus, 100)
    
    def _score_location(self, candidate):
        loc = candidate.get("profile", {}).get("location", "").lower()
        country = candidate.get("profile", {}).get("country", "").lower()
        sig = candidate.get("redrob_signals", {})
        relocate = sig.get("willing_to_relocate", False)
        work_mode = sig.get("preferred_work_mode", "").lower()
        
        loc_match = any(tl in loc for tl in self.jd["target_locations"])
        if loc_match and country == "india": score = 100
        elif country == "india": score = 85 if relocate else 60
        elif relocate: score = 40
        else: score = 10
        
        if work_mode in self.jd["work_mode_preference"]:
            score = min(score + 10, 100)
        return score
    
    def _score_company(self, candidate):
        career = candidate.get("career_history", [])
        companies = [j.get("company", "").lower() for j in career]
        disqual = self.jd["disqualify_companies"]
        all_bad = all(any(dc in c for dc in disqual) for c in companies)
        if all_bad and len(companies) >= 2: return 5
        has_bad = any(any(dc in c for dc in disqual) for c in companies)
        if has_bad and len(companies) >= 2: return 50
        if any(dc in candidate.get("profile", {}).get("current_company", "").lower() for dc in disqual): return 40
        return 100
    
    def _score_behavior(self, candidate):
        sig = candidate.get("redrob_signals", {})
        score = sig.get("profile_completeness_score", 0) * 0.10
        if sig.get("open_to_work_flag"): score += 15
        score += sig.get("recruiter_response_rate", 0) * 20
        resp_h = sig.get("avg_response_time_hours", 999)
        if resp_h < 24: score += 15
        elif resp_h < 72: score += 10
        elif resp_h < 168: score += 5
        score += sig.get("interview_completion_rate", 0) * 15
        offer = sig.get("offer_acceptance_rate", -1)
        if offer >= 0: score += offer * 10
        notice = sig.get("notice_period_days", 180)
        if notice <= 30: score += 10
        elif notice <= 60: score += 5
        last = sig.get("last_active_date", "")
        if last:
            try:
                days = (self.today - datetime.strptime(last, "%Y-%m-%d")).days
                if days < 30: score += 10
                elif days < 90: score += 5
                elif days > 180: score -= 15
            except: pass
        if sig.get("verified_email"): score += 3
        if sig.get("verified_phone"): score += 2
        gh = sig.get("github_activity_score", -1)
        if gh > 50: score += 5
        score += min(sig.get("saved_by_recruiters_30d", 0), 20) * 0.25
        return min(score, 100)
    
    def _score_trust(self, candidate):
        penalty = 0
        career = candidate.get("career_history", [])
        skills = candidate.get("skills", [])
        for job in career:
            start = job.get("start_date", "")
            end = job.get("end_date", "")
            dur = job.get("duration_months", 0)
            if start and end:
                try:
                    sd = datetime.strptime(start, "%Y-%m-%d")
                    ed = datetime.strptime(end, "%Y-%m-%d")
                    actual = (ed - sd).days / 30.44
                    if abs(actual - dur) > 12: penalty += 25
                    if sd > ed: penalty += 50
                except: pass
        expert_low = [s for s in skills if s.get("proficiency") == "expert" and s.get("duration_months", 0) < 6]
        if len(expert_low) >= 3: penalty += 20
        if len(skills) > 20: penalty += 10
        title = candidate.get("profile", {}).get("current_title", "").lower()
        summary = candidate.get("profile", {}).get("summary", "").lower()
        bad_titles = self.jd["disqualify_titles"]
        if any(bt in title for bt in bad_titles):
            if any(t in summary for t in ["ml", "ai", "machine learning", "rag", "llm"]): penalty += 10
        sal = candidate.get("redrob_signals", {}).get("expected_salary_range_inr_lpa", {})
        if sal.get("min", 0) > sal.get("max", 0): penalty += 15
        return max(100 - penalty, 0)
    
    def _score_startup_mindset(self, candidate):
        """Score for startup/agile signals per JD requirements."""
        career = candidate.get("career_history", [])
        signals = candidate.get("redrob_signals", {})
        
        score = 0
        
        # Has worked at small companies (<200 employees)
        small_co_sizes = ["1-10", "11-50", "51-200"]
        small_co_experience = any(
            job.get("company_size", "") in small_co_sizes
            for job in career
        )
        if small_co_experience:
            score += 30
        
        # Has worn multiple hats (different titles across career)
        titles = list(set(job.get("title", "").lower() for job in career))
        if len(titles) >= 3:
            score += 20
        
        # Early-stage / product company experience
        product_companies = ["pied piper", "hooli", "initech", "acme corp", 
                            "stark industries", "wayne enterprises", "zomato", 
                            "razorpay", "flipkart", "ola"]
        has_product = any(
            job.get("company", "").lower() in product_companies
            for job in career
        )
        if has_product:
            score += 25
        
        # High engagement = "scrappy, active" attitude
        response_rate = signals.get("recruiter_response_rate", 0)
        interview_rate = signals.get("interview_completion_rate", 0)
        github_score = signals.get("github_activity_score", -1)
        
        if response_rate > 0.7 and interview_rate > 0.8:
            score += 15
        
        if github_score > 30:
            score += 10
        
        return min(score, 100)
    
    def _compute_role_fit(self, scores):
        """Combine all dimension scores into final role fit."""
        weights = {
            "skill_match": 0.28,
            "career_match": 0.23,
            "experience_fit": 0.10,
            "education_fit": 0.05,
            "location_fit": 0.05,
            "company_fit": 0.10,
            "hiring_readiness": 0.09,
            "trust_score": 0.05,
            "startup_mindset": 0.05,
        }
        
        total = sum(scores.get(k, 0) * weights.get(k, 0) for k in weights)
        
        # Trust score acts as a penalty multiplier if very low
        trust = scores.get("trust_score", 100)
        if trust < 30:
            total *= 0.3
        elif trust < 50:
            total *= 0.6
        
        return min(total, 100)