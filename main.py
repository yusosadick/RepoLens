"""Main CLI entry point for RepoLens."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from analyzer import analyze_directory
from utils import clone_repository, cleanup_temp_directory, DEFAULT_LANGUAGE, get_text, normalize_path
from reporter import export_json, export_csv, export_markdown
from tui.utils import validate_directory_path, validate_github_url
import insights
import reporter


def format_summary(data: dict, lang: str = DEFAULT_LANGUAGE) -> str:
    """
    Format analysis results as a human-readable summary.
    
    Args:
        data: Analysis data dictionary
        lang: Language code for translations
        
    Returns:
        Formatted summary string
    """
    lines = []
    
    # Summary header
    lines.append(f"\n{get_text('summary', lang)}")
    lines.append("=" * 50)
    
    # Total statistics
    lines.append(f"{get_text('files', lang)}: {data['total_files']:,}")
    lines.append(f"{get_text('lines', lang)}: {data['total_lines']:,}")
    lines.append(f"{get_text('characters', lang)}: {data['total_characters']:,}")
    
    # Top extensions
    by_extension = data.get("by_extension", {})
    if by_extension:
        lines.append(f"\n{get_text('top_extensions', lang)}:")
        lines.append("-" * 50)
        
        # Sort by file count
        sorted_exts = sorted(
            by_extension.items(),
            key=lambda x: x[1]["files"],
            reverse=True
        )[:10]  # Top 10
        
        lines.append(f"{get_text('extension', lang):<20} {get_text('file_count', lang):<15} {get_text('line_count', lang)}")
        lines.append("-" * 50)
        
        for ext, stats in sorted_exts:
            ext_display = ext if ext else "(no extension)"
            lines.append(
                f"{ext_display:<20} {stats['files']:<15,} {stats['lines']:,}"
            )
    
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    """Main CLI entry point."""
    # TODO: Add command-line argument validation
    # TODO: Implement argument parsing error handling
    # TODO: Add verbose mode support
    
    parser = argparse.ArgumentParser(
        description="RepoLens - A lightweight GitHub repository analyzer"
    )
    
    # Mutually exclusive group for input source (now optional for interactive mode)
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument(
        "--dir",
        type=str,
        help="Path to local directory to analyze"
    )
    input_group.add_argument(
        "--repo",
        type=str,
        help="GitHub repository URL to clone and analyze"
    )
    
    parser.add_argument(
        "--lang",
        type=str,
        choices=["en", "es", "ar"],
        default=DEFAULT_LANGUAGE,
        help=f"Interface language (default: {DEFAULT_LANGUAGE})"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        choices=["json", "csv"],
        help="Export results to JSON or CSV file"
    )
    
    parser.add_argument(
        "--report",
        type=str,
        choices=["md", "json", "csv"],
        help="Generate report in specified format (md, json, or csv)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for generated reports"
    )
    
    args = parser.parse_args()
    
    # Mode detection: Interactive (default), Direct CLI, or Help
    # TODO: Add mode detection logging
    # TODO: Implement mode-specific configuration
    
    # Interactive mode - launch TUI if no --dir or --repo provided
    # (Help mode is automatically handled by argparse)
    if not args.dir and not args.repo:
        try:
            from tui.app import RepoLensApp
            app = RepoLensApp()
            app.run()
            return
        except ImportError as e:
            print(f"Error: TUI dependencies not installed. Install with: pip install textual rich")
            print(f"Details: {e}")
            sys.exit(1)
    
    # Direct CLI mode - existing logic
    
    # Determine analysis path
    analysis_path: Optional[str] = None
    temp_dir: Optional[str] = None
    
    try:
        if args.repo:
            # Validate GitHub URL before cloning
            is_valid, error = validate_github_url(args.repo)
            if not is_valid:
                print(f"{get_text('error', args.lang)}: {error}")
                sys.exit(1)
            
            # Clone repository
            print(get_text("cloning", args.lang))
            temp_dir = clone_repository(args.repo)
            analysis_path = temp_dir
        else:
            # Validate local directory path
            is_valid, error = validate_directory_path(args.dir)
            if not is_valid:
                print(f"{get_text('error', args.lang)}: {error}")
                sys.exit(1)
            
            # Normalize path before analysis
            analysis_path = str(normalize_path(args.dir))
        
        # Analyze (path is already normalized)
        print(get_text("analyzing", args.lang))
        results = analyze_directory(analysis_path)
        
        # Print summary
        if results["total_files"] == 0:
            print(get_text("no_files_found", args.lang))
        else:
            print(format_summary(results, args.lang))
        
        # Determine repo_path for filename generation
        repo_path = args.repo if args.repo else analysis_path
        
        # Export if requested (legacy --export flag)
        if args.export:
            if args.export == "json":
                output_path = export_json(results, output_dir=args.output_dir, repo_path=repo_path)
            else:
                output_path = export_csv(results, output_dir=args.output_dir, repo_path=repo_path)
            
            print(f"{get_text('exported_to', args.lang)}: {output_path}")
        
        # Generate report if requested (--report flag)
        if args.report:
            output_path = None
            
            if args.report == "md":
                # Compute insights
                computed_insights = insights.compute_insights(results)
                
                # Compute ecosystem breakdown
                computed_insights["ecosystem_breakdown"] = reporter.compute_ecosystem_breakdown(
                    computed_insights, results
                )
                
                # Generate Markdown report (use repo_path for name, analysis_path for tree)
                markdown_content = reporter.generate_markdown_report(
                    results, computed_insights, repo_path, analysis_path
                )
                
                # Export Markdown
                output_path = export_markdown(markdown_content, output_dir=args.output_dir, repo_path=repo_path)
                print(f"Markdown report saved to: {output_path}")
            elif args.report == "json":
                output_path = export_json(results, output_dir=args.output_dir, repo_path=repo_path)
                print(f"JSON report saved to: {output_path}")
            elif args.report == "csv":
                output_path = export_csv(results, output_dir=args.output_dir, repo_path=repo_path)
                print(f"CSV report saved to: {output_path}")
    
    except RuntimeError as e:
        print(f"{get_text('error', args.lang)}: {str(e)}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    
    finally:
        # Cleanup temporary directory if created
        if temp_dir:
            cleanup_temp_directory(temp_dir)


if __name__ == "__main__":
    main()
