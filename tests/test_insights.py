"""Tests for the insights module."""

import pytest
from insights import (
    compute_dominant_language,
    compute_percentage_by_extension,
    compute_language_ranking,
    compute_documentation_ratio,
    compute_average_lines_per_file,
    compute_largest_file_extension,
    compute_complexity_level,
    compute_structural_balance_score,
    compute_health_score,
    compute_insights,
)


def test_dominant_language_detection():
    """Test dominant language identification."""
    # Python dominant
    by_ext = {
        ".py": {"files": 10, "lines": 1000, "characters": 5000},
        ".js": {"files": 5, "lines": 200, "characters": 1000},
    }
    assert compute_dominant_language(by_ext) == ".py"
    
    # JavaScript dominant
    by_ext2 = {
        ".js": {"files": 10, "lines": 2000, "characters": 10000},
        ".py": {"files": 5, "lines": 500, "characters": 2500},
    }
    assert compute_dominant_language(by_ext2) == ".js"
    
    # Empty dict
    assert compute_dominant_language({}) == ""


def test_percentage_calculations():
    """Test percentage calculation accuracy."""
    by_ext = {
        ".py": {"files": 10, "lines": 600, "characters": 3000},
        ".js": {"files": 5, "lines": 300, "characters": 1500},
        ".md": {"files": 2, "lines": 100, "characters": 500},
    }
    total_lines = 1000
    
    percentages = compute_percentage_by_extension(by_ext, total_lines)
    
    assert percentages[".py"] == 60.0
    assert percentages[".js"] == 30.0
    assert percentages[".md"] == 10.0
    
    # Sum should be 100% (with rounding tolerance)
    total = sum(percentages.values())
    assert abs(total - 100.0) < 0.01
    
    # Zero division handling
    percentages_zero = compute_percentage_by_extension(by_ext, 0)
    assert all(p == 0.0 for p in percentages_zero.values())
    
    # Single extension
    single_ext = {".py": {"files": 1, "lines": 100, "characters": 500}}
    single_percentages = compute_percentage_by_extension(single_ext, 100)
    assert single_percentages[".py"] == 100.0


def test_health_score_bounds():
    """Test health score is always 0-10."""
    # Perfect repo
    perfect_analysis = {
        "total_files": 100,
        "total_lines": 10000,
        "by_extension": {
            ".py": {"files": 50, "lines": 5000},
            ".js": {"files": 30, "lines": 3000},
            ".ts": {"files": 15, "lines": 1500},
            ".md": {"files": 5, "lines": 500},
        }
    }
    perfect_insights = compute_insights(perfect_analysis)
    health = perfect_insights["health_score"]
    assert 0 <= health <= 10
    
    # Empty repo
    empty_analysis = {
        "total_files": 0,
        "total_lines": 0,
        "by_extension": {}
    }
    empty_insights = compute_insights(empty_analysis)
    assert empty_insights["health_score"] == 0
    
    # Various configurations
    for files in [10, 50, 100, 500, 1000]:
        test_analysis = {
            "total_files": files,
            "total_lines": files * 100,
            "by_extension": {
                ".py": {"files": files, "lines": files * 100}
            }
        }
        test_insights = compute_insights(test_analysis)
        assert 0 <= test_insights["health_score"] <= 10


def test_documentation_ratio():
    """Test documentation ratio calculation."""
    # With documentation
    by_ext = {
        ".py": {"files": 10, "lines": 1000},
        ".md": {"files": 2, "lines": 100},
    }
    total_files = 12
    
    ratio = compute_documentation_ratio(by_ext, total_files)
    
    # File ratio: 2 md / 10 code = 0.2
    assert abs(ratio["files"] - 0.2) < 0.01
    
    # Line ratio: 100 md / 1000 code = 0.1
    assert abs(ratio["lines"] - 0.1) < 0.01
    
    # No documentation
    by_ext_no_docs = {
        ".py": {"files": 10, "lines": 1000},
    }
    ratio_no_docs = compute_documentation_ratio(by_ext_no_docs, 10)
    assert ratio_no_docs["files"] == 0.0
    assert ratio_no_docs["lines"] == 0.0


def test_largest_file_detection():
    """Test largest file extension identification."""
    # Python has higher average
    by_ext = {
        ".py": {"files": 10, "lines": 5000},  # avg 500
        ".js": {"files": 20, "lines": 4000},  # avg 200
    }
    assert compute_largest_file_extension(by_ext) == ".py"
    
    # JavaScript has higher average
    by_ext2 = {
        ".py": {"files": 20, "lines": 2000},  # avg 100
        ".js": {"files": 5, "lines": 1000},   # avg 200
    }
    assert compute_largest_file_extension(by_ext2) == ".js"
    
    # Empty dict
    assert compute_largest_file_extension({}) == ""


def test_complexity_level():
    """Test complexity level classification."""
    # Low: < 50 files
    assert compute_complexity_level(30, 150) == "Low"
    
    # Low: < 100 avg lines
    assert compute_complexity_level(100, 50) == "Low"
    
    # Medium: 50-500 files AND 100-500 avg
    assert compute_complexity_level(100, 200) == "Medium"
    assert compute_complexity_level(500, 500) == "Medium"
    
    # High: > 500 files
    assert compute_complexity_level(600, 200) == "High"
    
    # High: > 500 avg lines
    assert compute_complexity_level(100, 600) == "High"
    
    # High: > 500 files AND > 500 avg
    assert compute_complexity_level(600, 600) == "High"


def test_structural_balance_score():
    """Test structural balance score calculation."""
    # Single extension (perfectly unbalanced = 0.0)
    single_ext = {".py": 100.0}
    score = compute_structural_balance_score(single_ext)
    assert abs(score - 0.0) < 0.01
    
    # Unbalanced (one dominant)
    unbalanced = {
        ".py": 90.0,
        ".js": 5.0,
        ".md": 5.0,
    }
    score_unbalanced = compute_structural_balance_score(unbalanced)
    assert score_unbalanced < 0.3
    
    # More balanced
    balanced = {
        ".py": 40.0,
        ".js": 30.0,
        ".ts": 20.0,
        ".md": 10.0,
    }
    score_balanced = compute_structural_balance_score(balanced)
    assert score_balanced > 0.5
    
    # Range check
    assert 0.0 <= score_balanced <= 1.0
    assert 0.0 <= score_unbalanced <= 1.0
    
    # Empty dict
    assert compute_structural_balance_score({}) == 0.0


def test_language_family_classification():
    """Test language family classification."""
    from reporter import classify_language_family, get_language_name
    
    # Test various languages
    assert classify_language_family("Python") == "Scripting"
    assert classify_language_family("JavaScript") == "Web"
    assert classify_language_family("Java") == "JVM"
    assert classify_language_family("C") == "Systems"
    assert classify_language_family("Rust") == "Systems"
    assert classify_language_family("Haskell") == "Functional"
    assert classify_language_family("Markdown") == "Documentation"
    assert classify_language_family("JSON") == "Config"
    
    # Unknown language
    assert classify_language_family("UnknownLanguage") == "Other"


def test_ecosystem_breakdown():
    """Test ecosystem breakdown calculation."""
    from reporter import compute_ecosystem_breakdown
    
    analysis_data = {
        "total_files": 20,
        "total_lines": 2000,
        "by_extension": {
            ".py": {"files": 10, "lines": 1000},
            ".js": {"files": 5, "lines": 500},
            ".md": {"files": 5, "lines": 500},
        }
    }
    
    insights = {
        "dominant_language": ".py",
        "language_ranking": [(".py", 50.0), (".js", 25.0), (".md", 25.0)],
    }
    
    breakdown = compute_ecosystem_breakdown(insights, analysis_data)
    
    # Should have Scripting (Python), Web (JavaScript), Documentation (Markdown)
    assert "Scripting" in breakdown
    assert "Web" in breakdown
    assert "Documentation" in breakdown
    
    # Check percentages sum correctly
    total_percentage = sum(family["percentage"] for family in breakdown.values())
    assert abs(total_percentage - 100.0) < 0.01


def test_edge_cases():
    """Test edge cases."""
    # Empty repository
    empty_analysis = {
        "total_files": 0,
        "total_lines": 0,
        "total_characters": 0,
        "by_extension": {}
    }
    empty_insights = compute_insights(empty_analysis)
    assert empty_insights["dominant_language"] == ""
    assert empty_insights["language_ranking"] == []
    assert empty_insights["health_score"] == 0
    assert empty_insights["average_lines_per_file"] == 0.0
    
    # Single file repository
    single_file = {
        "total_files": 1,
        "total_lines": 100,
        "total_characters": 1000,
        "by_extension": {
            ".py": {"files": 1, "lines": 100, "characters": 1000}
        }
    }
    single_insights = compute_insights(single_file)
    assert single_insights["dominant_language"] == ".py"
    assert single_insights["health_score"] >= 0
    
    # Single extension repository
    single_ext = {
        "total_files": 10,
        "total_lines": 1000,
        "total_characters": 10000,
        "by_extension": {
            ".py": {"files": 10, "lines": 1000, "characters": 10000}
        }
    }
    single_ext_insights = compute_insights(single_ext)
    assert len(single_ext_insights["language_ranking"]) == 1
    assert single_ext_insights["language_ranking"][0][1] == 100.0
    
    # No documentation
    no_docs = {
        "total_files": 10,
        "total_lines": 1000,
        "total_characters": 10000,
        "by_extension": {
            ".py": {"files": 10, "lines": 1000, "characters": 10000}
        }
    }
    no_docs_insights = compute_insights(no_docs)
    assert no_docs_insights["documentation_ratio"]["files"] == 0.0
    assert not no_docs_insights["documentation_quality_signal"]
    
    # Zero division scenarios
    zero_analysis = {
        "total_files": 0,
        "total_lines": 0,
        "by_extension": {}
    }
    zero_insights = compute_insights(zero_analysis)
    # Should not crash, all values should be safe defaults
    assert isinstance(zero_insights, dict)
