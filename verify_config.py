#!/usr/bin/env python3
"""Simple verification that config loading works"""

import sys
import os

# Add repo to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("✓ Testing config loading...")

try:
    from src.config import get_recommendation_weights
    print("✓ Successfully imported get_recommendation_weights")
    
    weights = get_recommendation_weights()
    print(f"✓ Loaded weights: {weights}")
    
    if weights.get("skill") == 3 and weights.get("level") == 2:
        print("✓ Weights are correct!")
        print("\n✅ ALL CHECKS PASSED - Configuration is working!")
    else:
        print(f"⚠ Weights differ: {weights}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()