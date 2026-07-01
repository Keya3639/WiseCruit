"""Job Description parser — extracts structured requirements."""

def parse_jd(jd_text):
    """Extract structured requirements from the JD."""
    jd = {
        "title": "Senior AI Engineer",
        "must_have_skills": [
            "embeddings", "retrieval", "ranking", "vector database", "vector search",
            "sentence-transformers", "bge", "e5", "openai embeddings",
            "pinecone", "weaviate", "qdrant", "milvus", "opensearch", "elasticsearch", "faiss",
            "ndcg", "mrr", "map", "evaluation framework", "a/b test",
            "python", "production", "deployed",
        ],
        "nice_to_have_skills": [
            "lora", "qlora", "peft", "fine-tuning", "finetuning",
            "xgboost", "learning-to-rank", "learning to rank",
            "distributed systems", "inference optimization",
        ],
        "disqualify_companies": [
            "tcs", "infosys", "wipro", "accenture", "cognizant", "capgemini",
            "tech mahindra", "mindtree",
        ],
        "disqualify_titles": [
            "marketing manager", "operations manager", "accountant", "hr manager",
            "customer support", "content writer", "graphic designer",
            "civil engineer", "mechanical engineer", "sales executive",
            "business analyst", "project manager", "qa engineer",
        ],
        "target_experience_min": 5,
        "target_experience_max": 9,
        "target_locations": ["pune", "noida", "mumbai", "hyderabad", "delhi", "bangalore", "gurgaon"],
        "target_country": "india",
        "work_mode_preference": ["hybrid", "onsite"],
        "max_notice_period": 60,
    }
    jd["required_skills_keywords"] = jd["must_have_skills"] + jd["nice_to_have_skills"]
    return jd