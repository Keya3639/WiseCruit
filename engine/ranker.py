"""Final ranking engine for WiseCruit."""
import pandas as pd
from .scorer import WiseCruitScorer
from .reasoning import generate_reasoning

class WiseCruitRanker:
    def __init__(self, jd_requirements):
        self.scorer = WiseCruitScorer(jd_requirements)
    
    def rank_candidates(self, candidates, top_n=100):
        results = []
        for i, candidate in enumerate(candidates):
            scores = self.scorer.score_candidate(candidate)
            results.append({"candidate_id": candidate["candidate_id"],
                          "score": round(scores["role_fit"], 6),  # Keep more precision for sorting
                          "scores_detail": scores, "candidate": candidate})
            if (i + 1) % 10000 == 0:
                print(f"  Processed {i+1} candidates...")
        
        # Sort by score descending, then candidate_id ascending for tie-breaking
        results.sort(key=lambda x: (-x["score"], x["candidate_id"]))
        
        # Take top N
        top_results = results[:top_n]
        
        ranked = []
        for rank, r in enumerate(top_results, 1):
            reasoning = generate_reasoning(r["candidate"], r["scores_detail"], rank)
            ranked.append({"candidate_id": r["candidate_id"],
                          "rank": rank, "score": round(r["score"], 3),  # Round to 3 for CSV
                          "reasoning": reasoning})
        return ranked
    
    def to_dataframe(self, ranked_results):
        df = pd.DataFrame(ranked_results)
        # Ensure scores are non-increasing (handle rounding issues)
        for i in range(1, len(df)):
            if df.loc[i, 'score'] > df.loc[i-1, 'score']:
                df.loc[i, 'score'] = df.loc[i-1, 'score']
        return df