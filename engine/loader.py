"""Candidate and JD loader for WiseCruit."""
import gzip
import json
from pathlib import Path

def load_jd_text(jd_path="job_description.md"):
    """Load the job description markdown file."""
    with open(jd_path, "r", encoding="utf-8") as f:
        return f.read()

def load_candidates(candidates_path="candidates.jsonl.gz", limit=None):
    """Load candidates from JSON, JSONL, or gzipped JSONL file."""
    candidates = []
    
    # Determine if file is gzipped
    is_gz = str(candidates_path).endswith(".gz")
    
    if is_gz:
        opener = gzip.open
        mode = "rt"
    else:
        opener = open
        mode = "r"
    
    with opener(candidates_path, mode, encoding="utf-8") as f:
        # Read first character to detect format
        first_char = f.read(1)
        f.seek(0)  # Go back to start
        
        if first_char == '[':
            # JSON array format (like sample_candidates.json)
            data = json.load(f)
            candidates = data if isinstance(data, list) else [data]
        else:
            # JSONL format (one JSON object per line)
            for i, line in enumerate(f):
                if line.strip():
                    try:
                        candidates.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue  # Skip malformed lines
                    if limit and len(candidates) >= limit:
                        break
    
    if limit:
        candidates = candidates[:limit]
    
    return candidates

def load_sample_candidates(sample_path="sample_candidates.json"):
    """Load sample candidates from pretty-printed JSON."""
    with open(sample_path, "r", encoding="utf-8") as f:
        return json.load(f)