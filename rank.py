#!/usr/bin/env python3
"""
WiseCruit - AI Recruitment Intelligence Engine
Main ranking script for the Redrob Hackathon.

Usage:
    python rank.py --candidates ./candidates.jsonl --out ./output/submission.csv
"""

import argparse
import time
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.loader import load_candidates, load_jd_text
from engine.jd_parser import parse_jd
from engine.ranker import WiseCruitRanker


def main():
    parser = argparse.ArgumentParser(description="WiseCruit - AI Recruitment Intelligence Engine")
    parser.add_argument("--candidates", type=str, default="candidates.jsonl.gz",
                       help="Path to candidates file (JSONL or JSONL.gz)")
    parser.add_argument("--jd", type=str, default="job_description.md",
                       help="Path to job description markdown file")
    parser.add_argument("--out", type=str, default="submission.csv",
                       help="Output CSV path")
    parser.add_argument("--top", type=int, default=100,
                       help="Number of top candidates to output")
    parser.add_argument("--limit", type=int, default=None,
                       help="Limit candidates for testing (optional)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧠 WiseCruit - AI Recruitment Intelligence Engine")
    print("=" * 60)
    
    # Step 1: Load Job Description
    print("\n📋 Loading Job Description...")
    start_time = time.time()
    jd_text = load_jd_text(args.jd)
    jd_requirements = parse_jd(jd_text)
    print(f"   ✅ JD parsed successfully")
    
    # Step 2: Load Candidates
    print(f"\n📦 Loading candidates from {args.candidates}...")
    candidates = load_candidates(args.candidates, limit=args.limit)
    print(f"   ✅ Loaded {len(candidates):,} candidates")
    
    # Step 3: Rank Candidates
    print(f"\n🎯 Ranking {len(candidates):,} candidates (CPU only, no network)...")
    ranker = WiseCruitRanker(jd_requirements)
    ranked = ranker.rank_candidates(candidates, top_n=args.top)
    
    # Step 4: Convert to DataFrame and Save
    print(f"\n💾 Saving top {len(ranked)} candidates to {args.out}...")
    df = ranker.to_dataframe(ranked)
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(args.out) if os.path.dirname(args.out) else ".", exist_ok=True)
    
    df.to_csv(args.out, index=False)
    
    elapsed = time.time() - start_time
    print(f"\n✅ Done! Ranked {len(ranked)} candidates in {elapsed:.1f} seconds")
    print(f"📁 Output saved to: {args.out}")
    print(f"\nTop 5 candidates:")
    print("-" * 60)
    for _, row in df.head(5).iterrows():
        print(f"  Rank {row['rank']:3d} | {row['candidate_id']} | Score: {row['score']:.3f}")
        print(f"         {row['reasoning'][:120]}...")
        print()
    
    # Constraint check
    if elapsed > 300:
        print(f"⚠️  WARNING: Ranking took {elapsed:.1f}s — exceeds 5-minute limit!")
    else:
        print(f"✅ Within 5-minute constraint ({elapsed:.1f}s)")
    
    print("=" * 60)


if __name__ == "__main__":
    main()