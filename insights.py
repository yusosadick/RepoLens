"""Intelligence engine for RepoLens - converts raw statistics into structured insights."""

from typing import Dict, Any, List, Tuple, Optional


def compute_dominant_language(by_extension: Dict[str, Dict[str, int]]) -> str:
    """
    Find the extension with the highest line count.
    
    Args:
        by_extension: Dictionary mapping extensions to their statistics
        
    Returns:
        Extension string (e.g., ".py") or empty string if no extensions
    """
    if not by_extension:
        return ""
    
    dominant = max(by_extension.items(), key=lambda x: x[1].get("lines", 0))
    return dominant[0]


def compute_percentage_by_extension(
    by_extension: Dict[str, Dict[str, int]], 
    total_lines: int
) -> Dict[str, float]:
    """
    Calculate percentage of total lines per extension.
    
    Args:
        by_extension: Dictionary mapping extensions to their statistics
        total_lines: Total number of lines across all files
        
    Returns:
        Dictionary mapping extension to percentage (0-100)
    """
    if total_lines == 0:
        return {ext: 0.0 for ext in by_extension.keys()}
    
    percentages = {}
    for ext, stats in by_extension.items():
        lines = stats.get("lines", 0)
        percentages[ext] = (lines / total_lines) * 100.0
    
    return percentages


def compute_language_ranking(
    percentage_by_extension: Dict[str, float]
) -> List[Tuple[str, float]]:
    """
    Sort extensions by percentage descending.
    
    Args:
        percentage_by_extension: Dictionary mapping extension to percentage
        
    Returns:
        List of (extension, percentage) tuples sorted by percentage descending
    """
    return sorted(
        percentage_by_extension.items(),
        key=lambda x: x[1],
        reverse=True
    )


def compute_documentation_ratio(
    by_extension: Dict[str, Dict[str, int]],
    total_files: int
) -> Dict[str, float]:
    """
    Calculate documentation ratio (file ratio and line ratio).
    
    Args:
        by_extension: Dictionary mapping extensions to their statistics
        total_files: Total number of files
        
    Returns:
        Dictionary with 'files' and 'lines' keys containing ratios
    """
    md_files = by_extension.get(".md", {}).get("files", 0)
    md_lines = by_extension.get(".md", {}).get("lines", 0)
    
    code_files = total_files - md_files
    code_lines = sum(
        stats.get("lines", 0)
        for ext, stats in by_extension.items()
        if ext != ".md"
    )
    
    file_ratio = (md_files / code_files) if code_files > 0 else 0.0
    line_ratio = (md_lines / code_lines) if code_lines > 0 else 0.0
    
    return {
        "files": file_ratio,
        "lines": line_ratio
    }


def compute_average_lines_per_file(total_lines: int, total_files: int) -> float:
    """
    Calculate average lines per file.
    
    Args:
        total_lines: Total number of lines
        total_files: Total number of files
        
    Returns:
        Average lines per file, or 0.0 if no files
    """
    if total_files == 0:
        return 0.0
    return float(total_lines) / total_files


def compute_largest_file_extension(
    by_extension: Dict[str, Dict[str, int]]
) -> str:
    """
    Find extension with highest average lines per file.
    
    Args:
        by_extension: Dictionary mapping extensions to their statistics
        
    Returns:
        Extension string with highest average, or empty string if no extensions
    """
    if not by_extension:
        return ""
    
    max_avg = 0.0
    largest_ext = ""
    
    for ext, stats in by_extension.items():
        files = stats.get("files", 0)
        lines = stats.get("lines", 0)
        
        if files > 0:
            avg = lines / files
            if avg > max_avg:
                max_avg = avg
                largest_ext = ext
    
    return largest_ext


def compute_complexity_level(total_files: int, avg_lines: float) -> str:
    """
    Classify repository complexity level.
    
    Args:
        total_files: Total number of files
        avg_lines: Average lines per file
        
    Returns:
        "Low", "Medium", or "High"
    """
    if total_files < 50 or avg_lines < 100:
        return "Low"
    elif 50 <= total_files <= 500 and 100 <= avg_lines <= 500:
        return "Medium"
    else:
        return "High"


def compute_structural_balance_score(
    percentage_by_extension: Dict[str, float]
) -> float:
    """
    Calculate structural balance score (0-1, higher = more balanced).
    
    Uses formula: 1 - sum(squared proportions)
    
    Args:
        percentage_by_extension: Dictionary mapping extension to percentage
        
    Returns:
        Balance score between 0 and 1
    """
    if not percentage_by_extension:
        return 0.0
    
    # Convert percentages to proportions (0-1)
    total = sum(percentage_by_extension.values())
    if total == 0:
        return 0.0
    
    proportions = [p / total for p in percentage_by_extension.values()]
    
    # Calculate sum of squared proportions
    sum_squared = sum(p * p for p in proportions)
    
    # Balance score: 1 - sum(squared proportions)
    # Perfect balance (all equal) = 1.0
    # Perfect imbalance (one dominant) = 0.0
    return 1.0 - sum_squared


def compute_health_score(
    insights: Dict[str, Any],
    analysis_data: Dict[str, Any]
) -> int:
    """
    Calculate repository health score (0-10).
    
    Heuristics:
    - +2 if documentation files (.md) present
    - +2 if multiple language types (3+ extensions with significant code)
    - +1 if no giant files (largest file < 5000 lines)
    - +2 if balanced distribution (structural_balance_score > 0.5)
    - +2 if moderate file density (50-500 files)
    - +1 if average lines per file is reasonable (50-500)
    
    Args:
        insights: Insights dictionary with computed metrics
        analysis_data: Raw analysis data
        
    Returns:
        Health score from 0 to 10
    """
    score = 0
    
    # Check for documentation
    by_extension = analysis_data.get("by_extension", {})
    if ".md" in by_extension and by_extension[".md"].get("files", 0) > 0:
        score += 2
    
    # Check for multiple language types (3+ extensions with >100 lines)
    significant_extensions = [
        ext for ext, stats in by_extension.items()
        if stats.get("lines", 0) > 100 and ext != ".md"
    ]
    if len(significant_extensions) >= 3:
        score += 2
    
    # Check for giant files (using extension-based proxy)
    largest_ext = insights.get("largest_file_extension", "")
    if largest_ext:
        largest_stats = by_extension.get(largest_ext, {})
        files = largest_stats.get("files", 1)
        lines = largest_stats.get("lines", 0)
        avg_lines = lines / files if files > 0 else 0
        if avg_lines < 5000:
            score += 1
    
    # Check balanced distribution
    balance_score = insights.get("structural_balance_score", 0.0)
    if balance_score > 0.5:
        score += 2
    
    # Check moderate file density
    total_files = analysis_data.get("total_files", 0)
    if 50 <= total_files <= 500:
        score += 2
    
    # Check reasonable average lines per file
    avg_lines = insights.get("average_lines_per_file", 0.0)
    if 50 <= avg_lines <= 500:
        score += 1
    
    return min(score, 10)  # Cap at 10


def compute_insights(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to compute all insights from analysis data.
    
    Args:
        analysis_data: Raw analysis data from analyzer.py
        
    Returns:
        Complete insights dictionary with all computed metrics
    """
    by_extension = analysis_data.get("by_extension", {})
    total_files = analysis_data.get("total_files", 0)
    total_lines = analysis_data.get("total_lines", 0)
    
    # Handle edge case: empty repository
    if total_files == 0:
        return {
            "dominant_language": "",
            "language_ranking": [],
            "percentage_by_extension": {},
            "documentation_ratio": {"files": 0.0, "lines": 0.0},
            "average_lines_per_file": 0.0,
            "largest_file_extension": "",
            "complexity_level": "Low",
            "health_score": 0,
            "structural_balance_score": 0.0,
            "documentation_quality_signal": False,
            "ecosystem_breakdown": {}
        }
    
    # Compute basic metrics
    dominant_language = compute_dominant_language(by_extension)
    percentage_by_extension = compute_percentage_by_extension(by_extension, total_lines)
    language_ranking = compute_language_ranking(percentage_by_extension)
    documentation_ratio = compute_documentation_ratio(by_extension, total_files)
    average_lines_per_file = compute_average_lines_per_file(total_lines, total_files)
    largest_file_extension = compute_largest_file_extension(by_extension)
    complexity_level = compute_complexity_level(total_files, average_lines_per_file)
    structural_balance_score = compute_structural_balance_score(percentage_by_extension)
    documentation_quality_signal = by_extension.get(".md", {}).get("files", 0) > 0
    
    # Create insights dict
    insights = {
        "dominant_language": dominant_language,
        "language_ranking": language_ranking,
        "percentage_by_extension": percentage_by_extension,
        "documentation_ratio": documentation_ratio,
        "average_lines_per_file": average_lines_per_file,
        "largest_file_extension": largest_file_extension,
        "complexity_level": complexity_level,
        "structural_balance_score": structural_balance_score,
        "documentation_quality_signal": documentation_quality_signal,
        "ecosystem_breakdown": {}  # Will be computed in reporter.py
    }
    
    # Compute health score (needs insights dict)
    insights["health_score"] = compute_health_score(insights, analysis_data)
    
    return insights
