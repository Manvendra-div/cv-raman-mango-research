"""Unit tests for zone intelligence module."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from zone_intelligence.zone_profile import ZoneProfiler, ProfileSummary
from zone_intelligence.orchard_matching import OrchardMatcher, MatchResult


def test_zone_profiler_returns_profile_summary(sample_dataset):
    """Test ZoneProfiler.village_profile() returns ProfileSummary."""
    profiler = ZoneProfiler(sample_dataset)
    
    # Get profile for a village
    profile = profiler.village_profile("Malihabad")
    
    # Check it returns ProfileSummary
    assert isinstance(profile, ProfileSummary)
    assert profile.group_key == {"Village": "Malihabad"}
    assert profile.sample_count > 0
    assert "mean" in profile.yield_stats
    assert "std" in profile.yield_stats


def test_orchard_matcher_instantiation(sample_dataset):
    """Test OrchardMatcher can be instantiated."""
    matcher = OrchardMatcher(sample_dataset)
    assert matcher is not None
    assert hasattr(matcher, 'match')


def test_orchard_matcher_finds_matches(sample_dataset):
    """Test OrchardMatcher.match() returns MatchResult."""
    # Add Tree_Age column if not present
    if "Tree_Age" not in sample_dataset.columns:
        sample_dataset["Tree_Age"] = 10
    
    matcher = OrchardMatcher(sample_dataset)
    
    # Find matches for a specific village/variety combination
    result = matcher.match(
        village="Malihabad",
        variety="Dasheri",
        tree_age=10,
        management="Organic"
    )
    
    # Check result type
    assert isinstance(result, MatchResult)
    assert hasattr(result, 'matched_samples')
    assert hasattr(result, 'match_count')
    assert hasattr(result, 'criteria_used')


def test_zone_profiler_village_variety_profile(sample_dataset):
    """Test ZoneProfiler can create village+variety profiles."""
    profiler = ZoneProfiler(sample_dataset)
    
    # Get profile for village + variety
    profile = profiler.village_variety_profile("Malihabad", "Dasheri")
    
    # Check it returns ProfileSummary
    assert isinstance(profile, ProfileSummary)
    assert profile.group_key["Village"] == "Malihabad"
    assert profile.group_key["Mango_Variety"] == "Dasheri"
    assert profile.sample_count > 0
