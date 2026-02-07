"""Markdown report generator and export functionality for RepoLens - creates professional one-page intelligence reports."""

import os
import hashlib
import random
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple, Set

from utils import extract_repo_name, normalize_path

# ============================================================================
# Phrase Banks for Dynamic Insight and Recommendation Generation
# ============================================================================

# Dominant Language Phrases
DOMINANT_LANGUAGE_PHRASES: List[str] = [
    "The repository is strongly centered around {language}",
    "The codebase is primarily driven by {language}",
    "{language} forms the architectural backbone of the project",
    "The project exhibits a clear preference for {language}",
    "{language} dominates the technical landscape of the repository",
    "The repository demonstrates a {language}-centric architecture",
    "{language} serves as the primary technical foundation",
    "The codebase shows strong alignment with {language}",
    "{language} represents the core technology choice",
    "The project's technical identity is shaped by {language}",
]

# Documentation Commentary - High Ratio
DOCUMENTATION_HIGH_PHRASES: List[str] = [
    "Documentation coverage is notably strong",
    "The repository prioritizes written clarity",
    "Documentation presence enhances maintainability",
    "Written guidance demonstrates engineering discipline",
    "Documentation depth supports long-term sustainability",
    "The codebase benefits from comprehensive documentation",
    "Documentation quality indicates mature development practices",
]

# Documentation Commentary - Medium Ratio
DOCUMENTATION_MEDIUM_PHRASES: List[str] = [
    "Documentation coverage is moderate",
    "Written guidance exists but could expand",
    "Documentation provides basic orientation",
    "Some documentation presence aids navigation",
    "Documentation coverage meets minimum requirements",
]

# Documentation Commentary - Low Ratio
DOCUMENTATION_LOW_PHRASES: List[str] = [
    "Documentation footprint is minimal",
    "Limited documentation may impact onboarding",
    "Documentation coverage is sparse",
    "The repository would benefit from expanded documentation",
    "Written guidance is insufficient for complex navigation",
]

# Documentation Commentary - None
DOCUMENTATION_NONE_PHRASES: List[str] = [
    "Documentation is absent, which may hinder collaboration",
    "No documentation detected, creating potential knowledge gaps",
    "The repository lacks written guidance entirely",
]

# Complexity Commentary - Low
COMPLEXITY_LOW_PHRASES: List[str] = [
    "The structure suggests lightweight modular design",
    "File density indicates clean separation of concerns",
    "Low complexity reflects thoughtful architectural decisions",
    "The codebase demonstrates elegant simplicity",
    "Structural minimalism enhances code clarity",
    "File organization suggests disciplined engineering",
]

# Complexity Commentary - Medium
COMPLEXITY_MEDIUM_PHRASES: List[str] = [
    "The repository maintains moderate structural complexity",
    "Module sizing reflects practical engineering balance",
    "Complexity levels indicate realistic project scope",
    "The codebase shows balanced architectural density",
    "Structural complexity aligns with project maturity",
]

# Complexity Commentary - High
COMPLEXITY_HIGH_PHRASES: List[str] = [
    "The project leans toward dense architectural design",
    "Large modules increase structural weight",
    "High complexity suggests consolidation opportunities",
    "The codebase exhibits significant structural density",
    "Complexity levels may benefit from refactoring efforts",
]

# Structural Balance Commentary - Balanced
BALANCE_GOOD_PHRASES: List[str] = [
    "The code distribution appears balanced across modules",
    "File sizing suggests healthy modular segmentation",
    "Structural symmetry contributes to maintainability",
    "Even distribution indicates thoughtful organization",
    "The codebase demonstrates architectural equilibrium",
    "Balanced structure supports scalable development",
]

# Structural Balance Commentary - Moderate
BALANCE_MODERATE_PHRASES: List[str] = [
    "Code distribution shows moderate balance",
    "Structural organization has room for optimization",
    "Module distribution is somewhat uneven",
    "The codebase exhibits partial structural symmetry",
]

# Structural Balance Commentary - Unbalanced
BALANCE_POOR_PHRASES: List[str] = [
    "Uneven distribution may benefit from refactoring",
    "Code concentration suggests consolidation opportunities",
    "Structural imbalance indicates architectural debt",
    "The repository shows significant distribution skew",
    "Concentrated code structure may impact maintainability",
]

# Ecosystem Commentary
ECOSYSTEM_PHRASES: List[str] = [
    "Primary ecosystem focus: {family}",
    "The repository aligns with the {family} ecosystem",
    "Technical orientation favors {family} tooling",
    "The project demonstrates strong {family} ecosystem integration",
    "Ecosystem alignment centers on {family} technologies",
    "The codebase reflects {family} ecosystem conventions",
    "The repository shows clear {family} ecosystem orientation",
    "Technical stack emphasizes {family} ecosystem patterns",
]

# Health Commentary - High Score (8-10)
HEALTH_HIGH_PHRASES: List[str] = [
    "Overall repository health is strong",
    "Engineering hygiene appears well maintained",
    "The codebase demonstrates excellent structural quality",
    "Repository health indicators are positive",
    "The project exhibits robust engineering practices",
]

# Health Commentary - Medium Score (5-7)
HEALTH_MEDIUM_PHRASES: List[str] = [
    "Repository health is stable with improvement potential",
    "The codebase shows moderate engineering quality",
    "Structural health has room for enhancement",
    "Repository indicators suggest steady maintenance",
]

# Health Commentary - Low Score (0-4)
HEALTH_LOW_PHRASES: List[str] = [
    "Structural signals suggest maintenance opportunities",
    "Repository health indicates refactoring needs",
    "The codebase would benefit from structural improvements",
    "Health metrics reveal optimization potential",
    "Engineering quality shows areas for enhancement",
]

# Code Density Commentary
DENSITY_REASONABLE_PHRASES: List[str] = [
    "Average file size indicates manageable complexity",
    "File density supports maintainable code structure",
    "Module sizing reflects practical engineering constraints",
    "Code density aligns with best practices",
]

DENSITY_LOW_PHRASES: List[str] = [
    "Low file density suggests highly modular design",
    "Small average file size indicates granular architecture",
    "Minimal file density reflects micro-module approach",
]

DENSITY_HIGH_PHRASES: List[str] = [
    "High file density may indicate consolidation needs",
    "Large average file size suggests refactoring opportunities",
    "Dense file structure could benefit from decomposition",
]

# Recommendation Phrase Banks

# Test Coverage Recommendations
TEST_COVERAGE_PHRASES: List[str] = [
    "Consider expanding automated test coverage",
    "Adding comprehensive test suites would enhance reliability",
    "Test coverage appears limited and could be strengthened",
    "Implementing systematic testing would improve code quality",
    "The repository would benefit from expanded test infrastructure",
]

# Documentation Recommendations
DOCUMENTATION_RECOMMENDATIONS: List[str] = [
    "Increasing documentation depth would improve maintainability",
    "Expanding written guidance would enhance developer onboarding",
    "Documentation coverage should be prioritized for long-term sustainability",
    "Consider establishing documentation standards and practices",
    "The repository would benefit from comprehensive documentation",
]

# Modularization Recommendations
MODULARIZATION_PHRASES: List[str] = [
    "Refactoring oversized modules may enhance clarity",
    "Consider breaking down large files into focused components",
    "Modularization efforts could improve code maintainability",
    "Large modules present opportunities for structural decomposition",
    "File size reduction would improve code navigation",
]

# Structural Recommendations
STRUCTURAL_PHRASES: List[str] = [
    "Structural simplification could improve long-term scalability",
    "Optimizing file organization would enhance maintainability",
    "Consider reorganizing code distribution for better balance",
    "Structural refactoring could improve architectural clarity",
    "File organization patterns could be standardized",
]

# Health Score Recommendations
HEALTH_IMPROVEMENT_PHRASES: List[str] = [
    "Repository health could be improved through systematic refactoring",
    "Addressing structural debt would enhance overall code quality",
    "Comprehensive code review could identify improvement opportunities",
    "Engineering practices could be strengthened to improve health metrics",
]

# Transition phrases for natural sentence flow
TRANSITION_PHRASES: List[str] = [
    "Furthermore, ",
    "Additionally, ",
    "Moreover, ",
    "In addition, ",
    "Notably, ",
    "Significantly, ",
    "Importantly, ",
    "Consequently, ",
    "Accordingly, ",
    "",
]

# Synonym dictionaries for phrase variation
SYNONYMS = {
    "strongly": ["strongly", "heavily", "significantly", "substantially", "markedly", "notably", "considerably", "greatly", "deeply", "intensely"],
    "primarily": ["primarily", "mainly", "chiefly", "predominantly", "mostly", "largely", "principally", "essentially", "fundamentally", "basically"],
    "demonstrates": ["demonstrates", "shows", "exhibits", "displays", "reveals", "indicates", "suggests", "illustrates", "manifests", "presents"],
    "coverage": ["coverage", "presence", "extent", "scope", "breadth", "range", "span", "reach", "comprehensiveness", "thoroughness"],
    "notably": ["notably", "remarkably", "particularly", "especially", "significantly", "substantially", "considerably", "markedly", "distinctly", "pronouncedly"],
    "maintainability": ["maintainability", "sustainability", "longevity", "durability", "viability", "stability", "reliability", "consistency", "continuity", "persistence"],
    "moderate": ["moderate", "reasonable", "acceptable", "adequate", "satisfactory", "tolerable", "fair", "balanced", "measured", "controlled"],
    "sparse": ["sparse", "limited", "minimal", "scant", "meager", "thin", "scarce", "inadequate", "insufficient", "deficient"],
    "lightweight": ["lightweight", "streamlined", "efficient", "optimized", "refined", "simplified", "minimalist", "lean", "compact", "concise"],
    "complexity": ["complexity", "sophistication", "intricacy", "elaboration", "complication", "involvement", "depth", "richness", "nuance", "subtlety"],
    "balanced": ["balanced", "equitable", "proportional", "symmetrical", "harmonious", "even", "uniform", "consistent", "stable", "steady"],
    "opportunities": ["opportunities", "potential", "possibilities", "prospects", "avenues", "options", "alternatives", "chances", "prospects", "scope"],
    "refactoring": ["refactoring", "restructuring", "reorganization", "reengineering", "redesign", "revision", "improvement", "optimization", "enhancement", "modernization"],
    "consolidation": ["consolidation", "integration", "unification", "merging", "combination", "amalgamation", "synthesis", "coalescence", "fusion", "aggregation"],
    "health": ["health", "quality", "condition", "state", "status", "wellness", "fitness", "robustness", "vigor", "vitality"],
    "strong": ["strong", "robust", "solid", "sturdy", "resilient", "durable", "powerful", "vigorous", "forceful", "potent"],
    "enhancement": ["enhancement", "improvement", "refinement", "optimization", "upgrade", "advancement", "development", "progress", "evolution", "growth"],
    "density": ["density", "concentration", "compactness", "thickness", "intensity", "richness", "saturation", "packing", "crowding", "tightness"],
    "manageable": ["manageable", "controllable", "handleable", "workable", "feasible", "practical", "achievable", "attainable", "realistic", "viable"],
    "modular": ["modular", "component-based", "segmented", "compartmentalized", "sectional", "divided", "partitioned", "structured", "organized", "systematic"],
    "granular": ["granular", "detailed", "fine-grained", "precise", "specific", "particular", "meticulous", "thorough", "comprehensive", "exhaustive"],
    "decomposition": ["decomposition", "breakdown", "dissection", "analysis", "separation", "division", "fragmentation", "segmentation", "partitioning", "splitting"],
}

# Intensity modifiers
INTENSITY_MODIFIERS = [
    "", "clearly", "evidently", "obviously", "apparently", "seemingly", 
    "potentially", "possibly", "likely", "probably", "arguably", 
    "undoubtedly", "certainly", "definitely", "absolutely", "positively"
]

# Temporal/contextual modifiers
CONTEXTUAL_MODIFIERS = [
    "", "currently", "presently", "recently", "historically", 
    "traditionally", "typically", "generally", "usually", "commonly",
    "often", "frequently", "occasionally", "sometimes", "rarely"
]


def _expand_phrase_variations(base_phrase: str, target_count: int = 10) -> List[str]:
    """Generate multiple variations of a base phrase using synonyms, structure changes, and modifiers."""
    variations: Set[str] = {base_phrase}
    base_lower = base_phrase.lower()
    
    # Synonym substitution (case-insensitive)
    for word, synonyms in SYNONYMS.items():
        if word in base_lower:
            for synonym in synonyms[:4]:
                import re
                pattern = re.compile(re.escape(word), re.IGNORECASE)
                variation = pattern.sub(synonym, base_phrase, count=1)
                if variation != base_phrase and variation not in variations:
                    variations.add(variation)
                    if len(variations) >= target_count:
                        break
        if len(variations) >= target_count:
            break
    
    # Add intensity modifiers
    for modifier in INTENSITY_MODIFIERS[:6]:
        if modifier:
            if base_phrase.startswith("The "):
                variation = base_phrase.replace("The ", f"The {modifier} ", 1)
                if variation not in variations:
                    variations.add(variation)
            elif base_phrase.startswith("This "):
                variation = base_phrase.replace("This ", f"This {modifier} ", 1)
                if variation not in variations:
                    variations.add(variation)
            if len(variations) >= target_count:
                break
    
    # Add contextual modifiers
    for modifier in CONTEXTUAL_MODIFIERS[:6]:
        if modifier:
            if base_phrase.startswith("The "):
                variation = base_phrase.replace("The ", f"The {modifier} ", 1)
                if variation not in variations:
                    variations.add(variation)
            if len(variations) >= target_count:
                break
    
    # Passive/active voice variations
    if " is " in base_phrase or " are " in base_phrase:
        if " is centered " in base_phrase:
            variation = base_phrase.replace(" is centered ", " centers ")
            if variation not in variations:
                variations.add(variation)
        if " is driven " in base_phrase:
            variation = base_phrase.replace(" is driven ", " drives ")
            if variation not in variations:
                variations.add(variation)
    
    # Add "appears to be", "seems to be" variations
    if " is " in base_phrase:
        for prefix in ["appears to be", "seems to be", "tends to be"]:
            variation = base_phrase.replace(" is ", f" {prefix} ", 1)
            if variation not in variations:
                variations.add(variation)
                if len(variations) >= target_count:
                    break
    
    result = list(variations)
    
    # If we still need more, create additional semantic variations
    while len(result) < target_count and len(result) < target_count * 2:
        for suffix_word in ["overall", "in general", "typically", "generally"]:
            if base_phrase.endswith("."):
                variation = base_phrase[:-1] + f", {suffix_word}."
            else:
                variation = base_phrase + f", {suffix_word}"
            if variation not in result:
                result.append(variation)
                break
        else:
            break
    
    return result[:target_count]


def _expand_phrase_list(original_phrases: List[str], expansion_factor: int = 10) -> List[str]:
    """Expand a list of phrases by the specified factor."""
    expanded: List[str] = []
    target_per_phrase = expansion_factor
    
    for phrase in original_phrases:
        variations = _expand_phrase_variations(phrase, target_per_phrase)
        expanded.extend(variations)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_expanded = []
    for phrase in expanded:
        if phrase not in seen:
            seen.add(phrase)
            unique_expanded.append(phrase)
    
    return unique_expanded


# Store original lists before expansion
_ORIGINAL_DOMINANT_LANGUAGE_PHRASES = DOMINANT_LANGUAGE_PHRASES.copy()
_ORIGINAL_DOCUMENTATION_HIGH_PHRASES = DOCUMENTATION_HIGH_PHRASES.copy()
_ORIGINAL_DOCUMENTATION_MEDIUM_PHRASES = DOCUMENTATION_MEDIUM_PHRASES.copy()
_ORIGINAL_DOCUMENTATION_LOW_PHRASES = DOCUMENTATION_LOW_PHRASES.copy()
_ORIGINAL_DOCUMENTATION_NONE_PHRASES = DOCUMENTATION_NONE_PHRASES.copy()
_ORIGINAL_COMPLEXITY_LOW_PHRASES = COMPLEXITY_LOW_PHRASES.copy()
_ORIGINAL_COMPLEXITY_MEDIUM_PHRASES = COMPLEXITY_MEDIUM_PHRASES.copy()
_ORIGINAL_COMPLEXITY_HIGH_PHRASES = COMPLEXITY_HIGH_PHRASES.copy()
_ORIGINAL_BALANCE_GOOD_PHRASES = BALANCE_GOOD_PHRASES.copy()
_ORIGINAL_BALANCE_MODERATE_PHRASES = BALANCE_MODERATE_PHRASES.copy()
_ORIGINAL_BALANCE_POOR_PHRASES = BALANCE_POOR_PHRASES.copy()
_ORIGINAL_ECOSYSTEM_PHRASES = ECOSYSTEM_PHRASES.copy()
_ORIGINAL_HEALTH_HIGH_PHRASES = HEALTH_HIGH_PHRASES.copy()
_ORIGINAL_HEALTH_MEDIUM_PHRASES = HEALTH_MEDIUM_PHRASES.copy()
_ORIGINAL_HEALTH_LOW_PHRASES = HEALTH_LOW_PHRASES.copy()
_ORIGINAL_DENSITY_REASONABLE_PHRASES = DENSITY_REASONABLE_PHRASES.copy()
_ORIGINAL_DENSITY_LOW_PHRASES = DENSITY_LOW_PHRASES.copy()
_ORIGINAL_DENSITY_HIGH_PHRASES = DENSITY_HIGH_PHRASES.copy()
_ORIGINAL_TEST_COVERAGE_PHRASES = TEST_COVERAGE_PHRASES.copy()
_ORIGINAL_DOCUMENTATION_RECOMMENDATIONS = DOCUMENTATION_RECOMMENDATIONS.copy()
_ORIGINAL_MODULARIZATION_PHRASES = MODULARIZATION_PHRASES.copy()
_ORIGINAL_STRUCTURAL_PHRASES = STRUCTURAL_PHRASES.copy()
_ORIGINAL_HEALTH_IMPROVEMENT_PHRASES = HEALTH_IMPROVEMENT_PHRASES.copy()

# Expand all phrase lists programmatically (10x expansion)
DOMINANT_LANGUAGE_PHRASES = _expand_phrase_list(_ORIGINAL_DOMINANT_LANGUAGE_PHRASES, 10)
DOCUMENTATION_HIGH_PHRASES = _expand_phrase_list(DOCUMENTATION_HIGH_PHRASES, 10)
DOCUMENTATION_MEDIUM_PHRASES = _expand_phrase_list(DOCUMENTATION_MEDIUM_PHRASES, 10)
DOCUMENTATION_LOW_PHRASES = _expand_phrase_list(DOCUMENTATION_LOW_PHRASES, 10)
DOCUMENTATION_NONE_PHRASES = _expand_phrase_list(DOCUMENTATION_NONE_PHRASES, 10)
COMPLEXITY_LOW_PHRASES = _expand_phrase_list(COMPLEXITY_LOW_PHRASES, 10)
COMPLEXITY_MEDIUM_PHRASES = _expand_phrase_list(COMPLEXITY_MEDIUM_PHRASES, 10)
COMPLEXITY_HIGH_PHRASES = _expand_phrase_list(COMPLEXITY_HIGH_PHRASES, 10)
BALANCE_GOOD_PHRASES = _expand_phrase_list(BALANCE_GOOD_PHRASES, 10)
BALANCE_MODERATE_PHRASES = _expand_phrase_list(BALANCE_MODERATE_PHRASES, 10)
BALANCE_POOR_PHRASES = _expand_phrase_list(BALANCE_POOR_PHRASES, 10)
ECOSYSTEM_PHRASES = _expand_phrase_list(ECOSYSTEM_PHRASES, 10)
HEALTH_HIGH_PHRASES = _expand_phrase_list(HEALTH_HIGH_PHRASES, 10)
HEALTH_MEDIUM_PHRASES = _expand_phrase_list(HEALTH_MEDIUM_PHRASES, 10)
HEALTH_LOW_PHRASES = _expand_phrase_list(HEALTH_LOW_PHRASES, 10)
DENSITY_REASONABLE_PHRASES = _expand_phrase_list(DENSITY_REASONABLE_PHRASES, 10)
DENSITY_LOW_PHRASES = _expand_phrase_list(DENSITY_LOW_PHRASES, 10)
DENSITY_HIGH_PHRASES = _expand_phrase_list(DENSITY_HIGH_PHRASES, 10)
TEST_COVERAGE_PHRASES = _expand_phrase_list(TEST_COVERAGE_PHRASES, 10)
DOCUMENTATION_RECOMMENDATIONS = _expand_phrase_list(DOCUMENTATION_RECOMMENDATIONS, 10)
MODULARIZATION_PHRASES = _expand_phrase_list(MODULARIZATION_PHRASES, 10)
STRUCTURAL_PHRASES = _expand_phrase_list(STRUCTURAL_PHRASES, 10)
HEALTH_IMPROVEMENT_PHRASES = _expand_phrase_list(HEALTH_IMPROVEMENT_PHRASES, 10)


# Comprehensive extension to language name mapping
EXTENSION_TO_LANGUAGE: Dict[str, str] = {
    # Python ecosystem
    ".py": "Python",
    ".pyw": "Python",
    ".pyi": "Python Stub",
    ".pyx": "Cython",
    ".pxd": "Cython",
    ".ipynb": "Jupyter Notebook",
    
    # JavaScript / Web ecosystem
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".mts": "TypeScript",
    ".cts": "TypeScript",
    ".d.ts": "TypeScript Declaration",
    ".jsx": "React JSX",
    ".tsx": "React TSX",
    ".html": "HTML",
    ".htm": "HTML",
    ".xhtml": "XHTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "Sass",
    ".less": "Less",
    ".styl": "Stylus",
    ".vue": "Vue",
    ".svelte": "Svelte",
    ".astro": "Astro",
    
    # Template Languages (Shopify, etc.)
    ".liquid": "Liquid",
    ".hbs": "Handlebars",
    ".handlebars": "Handlebars",
    ".ejs": "EJS",
    ".pug": "Pug",
    ".jade": "Jade",
    ".mustache": "Mustache",
    ".njk": "Nunjucks",
    ".twig": "Twig",
    ".jinja": "Jinja",
    ".jinja2": "Jinja2",
    ".j2": "Jinja2",
    ".slim": "Slim",
    ".haml": "HAML",
    ".marko": "Marko",
    ".dust": "Dust",
    ".eta": "Eta",
    ".edge": "Edge",
    ".blade.php": "Blade",
    ".cshtml": "Razor",
    ".vbhtml": "Razor VB",
    ".razor": "Razor",
    
    # JVM ecosystem
    ".java": "Java",
    ".kt": "Kotlin",
    ".kts": "Kotlin Script",
    ".scala": "Scala",
    ".sc": "Scala Script",
    ".groovy": "Groovy",
    ".gvy": "Groovy",
    ".gy": "Groovy",
    ".gsh": "Groovy",
    ".gradle": "Gradle",
    ".gradle.kts": "Gradle Kotlin",
    
    # Systems languages
    ".c": "C",
    ".h": "C Header",
    ".i": "C Inline",
    ".ii": "C++ Inline",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".c++": "C++",
    ".hpp": "C++ Header",
    ".hh": "C++ Header",
    ".hxx": "C++ Header",
    ".h++": "C++ Header",
    ".inl": "C++ Inline",
    ".ipp": "C++ Inline",
    ".tcc": "C++ Template",
    ".tpp": "C++ Template",
    ".rs": "Rust",
    ".go": "Go",
    ".zig": "Zig",
    ".nim": "Nim",
    ".nimble": "Nimble",
    ".d": "D",
    ".di": "D Interface",
    ".v": "V",
    ".vv": "V",
    ".odin": "Odin",
    ".carbon": "Carbon",
    
    # Microsoft ecosystem
    ".cs": "C#",
    ".csx": "C# Script",
    ".fs": "F#",
    ".fsi": "F# Signature",
    ".fsx": "F# Script",
    ".fsscript": "F# Script",
    ".vb": "VB.NET",
    ".vbs": "VBScript",
    ".asp": "ASP Classic",
    ".aspx": "ASP.NET",
    ".ascx": "ASP.NET Control",
    ".asmx": "ASP.NET Service",
    ".axd": "ASP.NET Handler",
    
    # Apple ecosystem
    ".swift": "Swift",
    ".m": "Objective-C",
    ".mm": "Objective-C++",
    ".storyboard": "Storyboard",
    ".xib": "Interface Builder",
    ".pbxproj": "Xcode Project",
    ".xcconfig": "Xcode Config",
    ".entitlements": "Entitlements",
    ".plist": "Property List",
    
    # Scripting languages
    ".sh": "Shell",
    ".bash": "Bash",
    ".zsh": "Zsh",
    ".fish": "Fish",
    ".ksh": "Korn Shell",
    ".csh": "C Shell",
    ".tcsh": "TENEX C Shell",
    ".ps1": "PowerShell",
    ".psm1": "PowerShell Module",
    ".psd1": "PowerShell Data",
    ".bat": "Batch",
    ".cmd": "Batch",
    ".rb": "Ruby",
    ".rbw": "Ruby",
    ".rake": "Rake",
    ".gemspec": "Gemspec",
    ".erb": "ERB",
    ".rhtml": "ERB",
    ".pl": "Perl",
    ".pm": "Perl Module",
    ".pod": "Perl Documentation",
    ".t": "Perl Test",
    ".lua": "Lua",
    ".tcl": "Tcl",
    ".tk": "Tcl/Tk",
    ".awk": "AWK",
    ".sed": "Sed",
    
    # Backend / Web servers
    ".php": "PHP",
    ".php3": "PHP",
    ".php4": "PHP",
    ".php5": "PHP",
    ".php7": "PHP",
    ".phps": "PHP",
    ".phtml": "PHP HTML",
    ".inc": "Include",
    
    # Functional languages
    ".hs": "Haskell",
    ".lhs": "Literate Haskell",
    ".elm": "Elm",
    ".clj": "Clojure",
    ".cljs": "ClojureScript",
    ".cljc": "Clojure Common",
    ".edn": "EDN",
    ".ml": "OCaml",
    ".mli": "OCaml Interface",
    ".mll": "OCaml Lex",
    ".mly": "OCaml Yacc",
    ".re": "Reason",
    ".rei": "Reason Interface",
    ".res": "ReScript",
    ".resi": "ReScript Interface",
    ".sml": "Standard ML",
    ".sig": "Standard ML Signature",
    ".fun": "Standard ML Functor",
    
    # Elixir / Erlang (BEAM)
    ".ex": "Elixir",
    ".exs": "Elixir Script",
    ".eex": "EEx",
    ".heex": "HEEx",
    ".leex": "LEEx",
    ".erl": "Erlang",
    ".hrl": "Erlang Header",
    ".app.src": "Erlang App",
    
    # Lisp family
    ".lisp": "Lisp",
    ".lsp": "Lisp",
    ".cl": "Common Lisp",
    ".el": "Emacs Lisp",
    ".elc": "Emacs Lisp Compiled",
    ".scm": "Scheme",
    ".ss": "Scheme",
    ".rkt": "Racket",
    ".scrbl": "Scribble",
    ".fnl": "Fennel",
    ".hy": "Hy",
    
    # Other programming languages
    ".coffee": "CoffeeScript",
    ".litcoffee": "Literate CoffeeScript",
    ".cr": "Crystal",
    ".ecr": "Crystal Template",
    ".pas": "Pascal",
    ".pp": "Pascal",
    ".dpr": "Delphi",
    ".dfm": "Delphi Form",
    ".lpr": "Lazarus",
    ".ada": "Ada",
    ".adb": "Ada Body",
    ".ads": "Ada Spec",
    ".cob": "COBOL",
    ".cbl": "COBOL",
    ".cobol": "COBOL",
    ".cpy": "COBOL Copybook",
    ".f": "Fortran",
    ".for": "Fortran",
    ".ftn": "Fortran",
    ".f77": "Fortran 77",
    ".f90": "Fortran 90",
    ".f95": "Fortran 95",
    ".f03": "Fortran 2003",
    ".f08": "Fortran 2008",
    ".f18": "Fortran 2018",
    ".forth": "Forth",
    ".fth": "Forth",
    ".4th": "Forth",
    ".factor": "Factor",
    ".io": "Io",
    ".ioke": "Ioke",
    ".pony": "Pony",
    ".red": "Red",
    ".reds": "Red/System",
    ".ring": "Ring",
    ".wren": "Wren",
    ".vala": "Vala",
    ".vapi": "Vala API",
    ".hx": "Haxe",
    ".hxml": "Haxe Build",
    ".moon": "MoonScript",
    ".mint": "Mint",
    ".gleam": "Gleam",
    ".roc": "Roc",
    ".zig": "Zig",
    ".unison": "Unison",
    ".idris": "Idris",
    ".idr": "Idris",
    ".agda": "Agda",
    ".lean": "Lean",
    ".coq": "Coq",
    ".v": "Coq",
    ".pvs": "PVS",
    
    # Blockchain / Smart Contracts
    ".sol": "Solidity",
    ".vy": "Vyper",
    ".yul": "Yul",
    ".move": "Move",
    ".clar": "Clarity",
    ".ride": "Ride",
    ".teal": "TEAL",
    ".ligo": "LIGO",
    ".mligo": "CameLIGO",
    ".jsligo": "JsLIGO",
    ".religo": "ReasonLIGO",
    ".michelson": "Michelson",
    ".tz": "Michelson",
    ".fc": "Func",
    ".cairo": "Cairo",
    ".ink": "ink!",
    ".rs.ink": "ink!",
    
    # Data / Config formats
    ".json": "JSON",
    ".jsonc": "JSON with Comments",
    ".json5": "JSON5",
    ".jsonl": "JSON Lines",
    ".ndjson": "Newline JSON",
    ".geojson": "GeoJSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".xml": "XML",
    ".xsd": "XML Schema",
    ".dtd": "DTD",
    ".rng": "RELAX NG",
    ".xsl": "XSLT",
    ".xslt": "XSLT",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "Config",
    ".conf": "Config",
    ".config": "Config",
    ".env": "Environment",
    ".env.example": "Environment Example",
    ".env.local": "Environment Local",
    ".env.development": "Environment Development",
    ".env.production": "Environment Production",
    ".properties": "Properties",
    ".hocon": "HOCON",
    ".hcl": "HCL",
    ".tf": "Terraform",
    ".tfvars": "Terraform Variables",
    ".tfstate": "Terraform State",
    ".nix": "Nix",
    ".dhall": "Dhall",
    ".cue": "CUE",
    ".jsonnet": "Jsonnet",
    ".libsonnet": "Jsonnet Library",
    ".pkl": "Pkl",
    ".rego": "Rego",
    ".sentinel": "Sentinel",
    ".ron": "RON",
    ".kdl": "KDL",
    
    # Data science / Scientific
    ".r": "R",
    ".rmd": "R Markdown",
    ".rnw": "R Noweb",
    ".jl": "Julia",
    ".mat": "MATLAB",
    ".m": "MATLAB",
    ".mlx": "MATLAB Live",
    ".sas": "SAS",
    ".sps": "SPSS",
    ".do": "Stata",
    ".ado": "Stata",
    ".dta": "Stata Data",
    ".stan": "Stan",
    ".bug": "BUGS",
    ".jags": "JAGS",
    
    # Databases / Query Languages
    ".sql": "SQL",
    ".psql": "PostgreSQL",
    ".pgsql": "PostgreSQL",
    ".mysql": "MySQL",
    ".plsql": "PL/SQL",
    ".tsql": "T-SQL",
    ".cql": "Cassandra CQL",
    ".cypher": "Cypher",
    ".sparql": "SPARQL",
    ".rq": "SPARQL",
    ".graphql": "GraphQL",
    ".gql": "GraphQL",
    ".prisma": "Prisma",
    ".edgeql": "EdgeQL",
    ".surql": "SurrealQL",
    ".aql": "AQL",
    ".n1ql": "N1QL",
    ".flux": "Flux",
    ".influxql": "InfluxQL",
    
    # Documentation / Text
    ".md": "Markdown",
    ".mdx": "MDX",
    ".markdown": "Markdown",
    ".mdown": "Markdown",
    ".mkd": "Markdown",
    ".mkdn": "Markdown",
    ".rst": "reStructuredText",
    ".rest": "reStructuredText",
    ".txt": "Text",
    ".text": "Text",
    ".tex": "LaTeX",
    ".ltx": "LaTeX",
    ".latex": "LaTeX",
    ".sty": "LaTeX Style",
    ".cls": "LaTeX Class",
    ".bib": "BibTeX",
    ".adoc": "AsciiDoc",
    ".asciidoc": "AsciiDoc",
    ".asc": "AsciiDoc",
    ".org": "Org Mode",
    ".pod": "Pod",
    ".rdoc": "RDoc",
    ".creole": "Creole",
    ".wiki": "Wiki",
    ".mediawiki": "MediaWiki",
    ".textile": "Textile",
    ".djot": "Djot",
    ".typ": "Typst",
    
    # Containers / DevOps
    ".dockerfile": "Dockerfile",
    ".containerfile": "Containerfile",
    ".vagrantfile": "Vagrantfile",
    ".make": "Makefile",
    ".mk": "Makefile",
    ".mak": "Makefile",
    ".makefile": "Makefile",
    ".justfile": "Justfile",
    ".taskfile": "Taskfile",
    ".earthfile": "Earthfile",
    
    # CI/CD Configuration
    ".jenkinsfile": "Jenkinsfile",
    ".gitlab-ci.yml": "GitLab CI",
    ".travis.yml": "Travis CI",
    ".circleci": "CircleCI",
    ".github": "GitHub Actions",
    ".buildkite": "Buildkite",
    ".drone.yml": "Drone CI",
    ".azure-pipelines.yml": "Azure Pipelines",
    ".bitbucket-pipelines.yml": "Bitbucket Pipelines",
    ".appveyor.yml": "AppVeyor",
    ".harness": "Harness",
    ".helmfile": "Helmfile",
    ".argocd": "ArgoCD",
    
    # Infrastructure as Code
    ".pp": "Puppet",
    ".epp": "Puppet Template",
    ".cf": "CloudFormation",
    ".cfn": "CloudFormation",
    ".sam": "AWS SAM",
    ".bicep": "Bicep",
    ".arm": "ARM Template",
    ".pulumi": "Pulumi",
    ".cdktf": "CDK for Terraform",
    
    # Kubernetes / Containers
    ".helm": "Helm",
    ".chart": "Helm Chart",
    ".kustomization": "Kustomize",
    ".k8s": "Kubernetes",
    
    # Build systems
    ".cmake": "CMake",
    ".bazel": "Bazel",
    ".buck": "Buck",
    ".build": "Build",
    ".bzl": "Starlark",
    ".sky": "Starlark",
    ".gn": "GN",
    ".gni": "GN Include",
    ".meson": "Meson",
    ".ninja": "Ninja",
    ".gyp": "GYP",
    ".gypi": "GYP Include",
    ".podspec": "CocoaPods",
    ".fastfile": "Fastlane",
    ".sln": "Solution",
    ".csproj": "C# Project",
    ".fsproj": "F# Project",
    ".vbproj": "VB.NET Project",
    ".vcxproj": "VC++ Project",
    ".targets": "MSBuild Targets",
    ".props": "MSBuild Props",
    ".proj": "MSBuild Project",
    
    # Mobile / Modern
    ".dart": "Dart",
    ".arb": "Dart ARB",
    ".proto": "Protocol Buffers",
    ".protobuf": "Protocol Buffers",
    ".thrift": "Thrift",
    ".avsc": "Avro Schema",
    ".avdl": "Avro IDL",
    ".fbs": "FlatBuffers",
    ".capnp": "Cap'n Proto",
    ".aidl": "Android IDL",
    ".hal": "Android HAL",
    
    # Game Development
    ".gd": "GDScript",
    ".gdscript": "GDScript",
    ".tscn": "Godot Scene",
    ".tres": "Godot Resource",
    ".gdns": "Godot NativeScript",
    ".gdshader": "Godot Shader",
    ".shader": "Shader",
    ".hlsl": "HLSL",
    ".glsl": "GLSL",
    ".frag": "Fragment Shader",
    ".vert": "Vertex Shader",
    ".geom": "Geometry Shader",
    ".comp": "Compute Shader",
    ".tesc": "Tessellation Control",
    ".tese": "Tessellation Evaluation",
    ".spv": "SPIR-V",
    ".wgsl": "WGSL",
    ".metal": "Metal",
    ".cg": "Cg",
    ".fx": "Effect",
    ".cgfx": "CgFX",
    ".uasset": "Unreal Asset",
    ".umap": "Unreal Map",
    ".uplugin": "Unreal Plugin",
    ".uproject": "Unreal Project",
    ".unity": "Unity Scene",
    ".prefab": "Unity Prefab",
    ".mat": "Unity Material",
    ".anim": "Unity Animation",
    ".controller": "Unity Controller",
    ".asset": "Unity Asset",
    
    # Hardware / Low-level
    ".asm": "Assembly",
    ".s": "Assembly",
    ".S": "Assembly",
    ".nasm": "NASM",
    ".yasm": "YASM",
    ".gas": "GNU Assembly",
    ".vhd": "VHDL",
    ".vhdl": "VHDL",
    ".sv": "SystemVerilog",
    ".svh": "SystemVerilog Header",
    ".bsv": "Bluespec",
    ".tcl": "Tcl",
    ".sdc": "SDC",
    ".xdc": "XDC",
    ".ucf": "UCF",
    ".qsf": "Quartus",
    ".pcf": "PCF",
    ".lpf": "LPF",
    ".spice": "SPICE",
    ".cir": "SPICE",
    ".lib": "Library",
    ".lef": "LEF",
    ".def": "DEF",
    ".gds": "GDSII",
    ".oas": "OASIS",
    ".kicad_sch": "KiCad Schema",
    ".kicad_pcb": "KiCad PCB",
    ".brd": "Eagle Board",
    ".sch": "Schematic",
    ".pcb": "PCB",
    
    # Certificates / Security
    ".pem": "PEM Certificate",
    ".crt": "Certificate",
    ".cer": "Certificate",
    ".der": "DER Certificate",
    ".p12": "PKCS12",
    ".pfx": "PKCS12",
    ".key": "Private Key",
    ".pub": "Public Key",
    ".csr": "Certificate Request",
    ".ca": "CA Certificate",
    ".keystore": "Java Keystore",
    ".jks": "Java Keystore",
    ".truststore": "Trust Store",
    
    # License Files
    ".license": "License",
    ".bsd": "BSD License",
    ".mit": "MIT License",
    ".apache": "Apache License",
    ".gpl": "GPL License",
    ".lgpl": "LGPL License",
    ".mpl": "MPL License",
    ".isc": "ISC License",
    ".unlicense": "Unlicense",
    
    # WebAssembly
    ".wasm": "WebAssembly",
    ".wat": "WebAssembly Text",
    ".wast": "WebAssembly Script",
    ".witx": "WITX",
    ".wit": "WIT",
    
    # API Specifications
    ".openapi": "OpenAPI",
    ".swagger": "Swagger",
    ".raml": "RAML",
    ".api": "API Blueprint",
    ".apib": "API Blueprint",
    ".wsdl": "WSDL",
    ".wadl": "WADL",
    ".grpc": "gRPC",
    ".smithy": "Smithy",
    ".asyncapi": "AsyncAPI",
    
    # Audio / Music
    ".abc": "ABC Notation",
    ".ly": "LilyPond",
    ".ily": "LilyPond Include",
    ".mma": "MMA",
    ".csound": "Csound",
    ".csd": "Csound",
    ".scd": "SuperCollider",
    ".faust": "Faust",
    ".dsp": "Faust DSP",
    ".chuck": "ChucK",
    ".sonic-pi": "Sonic Pi",
    
    # Other file types
    ".log": "Log",
    ".diff": "Diff",
    ".patch": "Patch",
    ".ics": "iCalendar",
    ".vcf": "vCard",
    ".csv": "CSV",
    ".tsv": "TSV",
    ".parquet": "Parquet",
    ".arrow": "Arrow",
    ".orc": "ORC",
    ".avro": "Avro",
    
    # Notebooks / Literate Programming
    ".qmd": "Quarto",
    ".weave.jl": "Weave Julia",
    ".jmd": "Julia Markdown",
    ".pluto.jl": "Pluto",
    
    # Editor / IDE Config
    ".editorconfig": "EditorConfig",
    ".prettierrc": "Prettier",
    ".eslintrc": "ESLint",
    ".stylelintrc": "Stylelint",
    ".babelrc": "Babel",
    ".browserslistrc": "Browserslist",
    ".npmrc": "npm",
    ".nvmrc": "nvm",
    ".ruby-version": "Ruby Version",
    ".python-version": "Python Version",
    ".node-version": "Node Version",
    ".tool-versions": "asdf",
}

# Filename to language mapping for files without extensions or special names
FILENAME_TO_LANGUAGE: Dict[str, str] = {
    # Build systems
    "Makefile": "Makefile",
    "makefile": "Makefile",
    "GNUmakefile": "Makefile",
    "BSDmakefile": "Makefile",
    "Justfile": "Justfile",
    "justfile": "Justfile",
    "Taskfile": "Taskfile",
    "Rakefile": "Rake",
    "rakefile": "Rake",
    "Earthfile": "Earthfile",
    "Snakefile": "Snakemake",
    "SConstruct": "SCons",
    "SConscript": "SCons",
    "BUILD": "Bazel",
    "BUILD.bazel": "Bazel",
    "WORKSPACE": "Bazel",
    "WORKSPACE.bazel": "Bazel",
    "BUCK": "Buck",
    "Tupfile": "Tup",
    "Kbuild": "Kbuild",
    "Kconfig": "Kconfig",
    
    # Containers / DevOps
    "Dockerfile": "Dockerfile",
    "dockerfile": "Dockerfile",
    "Containerfile": "Containerfile",
    "containerfile": "Containerfile",
    "docker-compose.yml": "Docker Compose",
    "docker-compose.yaml": "Docker Compose",
    "compose.yml": "Docker Compose",
    "compose.yaml": "Docker Compose",
    "Vagrantfile": "Vagrantfile",
    "Procfile": "Procfile",
    "Brewfile": "Brewfile",
    "Gemfile": "Gemfile",
    "Podfile": "Podfile",
    "Cartfile": "Cartfile",
    "Puppetfile": "Puppetfile",
    "Berksfile": "Berksfile",
    "Cheffile": "Cheffile",
    "Fastfile": "Fastlane",
    "Appfile": "Fastlane",
    "Matchfile": "Fastlane",
    "Deliverfile": "Fastlane",
    "Snapfile": "Fastlane",
    "Scanfile": "Fastlane",
    "Gymfile": "Fastlane",
    "Pluginfile": "Fastlane",
    
    # CI/CD
    "Jenkinsfile": "Jenkinsfile",
    ".travis.yml": "Travis CI",
    ".gitlab-ci.yml": "GitLab CI",
    "azure-pipelines.yml": "Azure Pipelines",
    "bitbucket-pipelines.yml": "Bitbucket Pipelines",
    "appveyor.yml": "AppVeyor",
    ".drone.yml": "Drone CI",
    "netlify.toml": "Netlify",
    "vercel.json": "Vercel",
    "now.json": "Vercel",
    "render.yaml": "Render",
    "fly.toml": "Fly.io",
    "railway.toml": "Railway",
    "heroku.yml": "Heroku",
    
    # Package manifests
    "package.json": "npm Package",
    "package-lock.json": "npm Lock",
    "yarn.lock": "Yarn Lock",
    "pnpm-lock.yaml": "pnpm Lock",
    "bun.lockb": "Bun Lock",
    "Cargo.toml": "Cargo",
    "Cargo.lock": "Cargo Lock",
    "go.mod": "Go Module",
    "go.sum": "Go Sum",
    "go.work": "Go Workspace",
    "pyproject.toml": "pyproject",
    "setup.py": "Python Setup",
    "setup.cfg": "Python Config",
    "requirements.txt": "Python Requirements",
    "requirements.in": "Python Requirements",
    "Pipfile": "Pipfile",
    "Pipfile.lock": "Pipfile Lock",
    "poetry.lock": "Poetry Lock",
    "pdm.lock": "PDM Lock",
    "uv.lock": "uv Lock",
    "composer.json": "Composer",
    "composer.lock": "Composer Lock",
    "build.gradle": "Gradle",
    "settings.gradle": "Gradle Settings",
    "build.gradle.kts": "Gradle Kotlin",
    "settings.gradle.kts": "Gradle Kotlin Settings",
    "pom.xml": "Maven POM",
    "build.sbt": "SBT",
    "project/build.properties": "SBT Properties",
    "mix.exs": "Mix",
    "mix.lock": "Mix Lock",
    "rebar.config": "Rebar",
    "rebar.lock": "Rebar Lock",
    "pubspec.yaml": "Pubspec",
    "pubspec.lock": "Pubspec Lock",
    "Package.swift": "Swift Package",
    "Package.resolved": "Swift Package Lock",
    "Packages.props": "NuGet Props",
    "nuget.config": "NuGet Config",
    "packages.config": "NuGet Packages",
    "paket.dependencies": "Paket",
    "paket.lock": "Paket Lock",
    "cpanfile": "CPAN",
    "META.json": "CPAN Meta",
    "META.yml": "CPAN Meta",
    "cabal.project": "Cabal",
    "stack.yaml": "Stack",
    "elm.json": "Elm Package",
    "dub.json": "Dub",
    "dub.sdl": "Dub",
    "shard.yml": "Shards",
    "shard.lock": "Shards Lock",
    "spago.dhall": "Spago",
    "packages.dhall": "Spago Packages",
    "esy.json": "Esy",
    "opam": "OPAM",
    "dune": "Dune",
    "dune-project": "Dune Project",
    "Project.toml": "Julia Project",
    "Manifest.toml": "Julia Manifest",
    "DESCRIPTION": "R Package",
    "NAMESPACE": "R Namespace",
    "conanfile.txt": "Conan",
    "conanfile.py": "Conan",
    "vcpkg.json": "vcpkg",
    "xmake.lua": "xmake",
    "premake5.lua": "Premake",
    "meson.build": "Meson",
    "CMakeLists.txt": "CMake",
    
    # License files
    "LICENSE": "License",
    "LICENSE.txt": "License",
    "LICENSE.md": "License",
    "LICENSE.rst": "License",
    "LICENSE-MIT": "MIT License",
    "LICENSE-APACHE": "Apache License",
    "LICENSE.MIT": "MIT License",
    "LICENSE.APACHE": "Apache License",
    "LICENCE": "License",
    "LICENCE.txt": "License",
    "LICENCE.md": "License",
    "COPYING": "License",
    "COPYING.txt": "License",
    "COPYING.md": "License",
    "UNLICENSE": "Unlicense",
    "UNLICENSE.txt": "Unlicense",
    "MIT-LICENSE": "MIT License",
    "MIT-LICENSE.txt": "MIT License",
    "Apache-2.0": "Apache License",
    "BSD-3-Clause": "BSD License",
    "GPL-3.0": "GPL License",
    "LGPL-3.0": "LGPL License",
    "MPL-2.0": "MPL License",
    "ISC": "ISC License",
    "WTFPL": "WTFPL License",
    "CC0": "CC0 License",
    "CC-BY-4.0": "CC BY License",
    
    # Documentation
    "README": "Readme",
    "README.txt": "Readme",
    "README.md": "Readme",
    "README.rst": "Readme",
    "README.adoc": "Readme",
    "README.asciidoc": "Readme",
    "CHANGELOG": "Changelog",
    "CHANGELOG.md": "Changelog",
    "CHANGELOG.txt": "Changelog",
    "CHANGELOG.rst": "Changelog",
    "HISTORY": "History",
    "HISTORY.md": "History",
    "HISTORY.txt": "History",
    "HISTORY.rst": "History",
    "NEWS": "News",
    "NEWS.md": "News",
    "CHANGES": "Changes",
    "CHANGES.md": "Changes",
    "CHANGES.txt": "Changes",
    "AUTHORS": "Authors",
    "AUTHORS.md": "Authors",
    "AUTHORS.txt": "Authors",
    "CONTRIBUTORS": "Contributors",
    "CONTRIBUTORS.md": "Contributors",
    "MAINTAINERS": "Maintainers",
    "MAINTAINERS.md": "Maintainers",
    "CODEOWNERS": "Code Owners",
    "SECURITY": "Security",
    "SECURITY.md": "Security",
    "SECURITY.txt": "Security",
    "CODE_OF_CONDUCT": "Code of Conduct",
    "CODE_OF_CONDUCT.md": "Code of Conduct",
    "CONTRIBUTING": "Contributing",
    "CONTRIBUTING.md": "Contributing",
    "CONTRIBUTING.rst": "Contributing",
    "SUPPORT": "Support",
    "SUPPORT.md": "Support",
    "FUNDING": "Funding",
    "FUNDING.yml": "Funding",
    "CITATION": "Citation",
    "CITATION.cff": "Citation",
    "CITATION.bib": "Citation",
    "ACKNOWLEDGMENTS": "Acknowledgments",
    "ACKNOWLEDGMENTS.md": "Acknowledgments",
    "CREDITS": "Credits",
    "CREDITS.md": "Credits",
    "TODO": "Todo",
    "TODO.md": "Todo",
    "TODO.txt": "Todo",
    "ROADMAP": "Roadmap",
    "ROADMAP.md": "Roadmap",
    "FAQ": "FAQ",
    "FAQ.md": "FAQ",
    
    # Git and version control
    ".gitignore": "Git Ignore",
    ".gitattributes": "Git Attributes",
    ".gitmodules": "Git Modules",
    ".gitkeep": "Git Keep",
    ".gitconfig": "Git Config",
    ".gitmessage": "Git Message",
    ".mailmap": "Git Mailmap",
    ".hgignore": "Mercurial Ignore",
    ".hgrc": "Mercurial Config",
    ".svnignore": "SVN Ignore",
    ".cvsignore": "CVS Ignore",
    ".bzrignore": "Bazaar Ignore",
    ".p4ignore": "Perforce Ignore",
    ".fosseignore": "FOSS Ignore",
    
    # Docker / Container
    ".dockerignore": "Docker Ignore",
    ".containerignore": "Container Ignore",
    ".hadolint.yaml": "Hadolint",
    "hadolint.yaml": "Hadolint",
    
    # Editor / IDE configs
    ".editorconfig": "EditorConfig",
    ".prettierrc": "Prettier",
    ".prettierrc.json": "Prettier",
    ".prettierrc.yml": "Prettier",
    ".prettierrc.yaml": "Prettier",
    ".prettierrc.js": "Prettier",
    ".prettierrc.cjs": "Prettier",
    ".prettierrc.mjs": "Prettier",
    "prettier.config.js": "Prettier",
    "prettier.config.cjs": "Prettier",
    "prettier.config.mjs": "Prettier",
    ".prettierignore": "Prettier Ignore",
    ".eslintrc": "ESLint",
    ".eslintrc.js": "ESLint",
    ".eslintrc.cjs": "ESLint",
    ".eslintrc.mjs": "ESLint",
    ".eslintrc.json": "ESLint",
    ".eslintrc.yml": "ESLint",
    ".eslintrc.yaml": "ESLint",
    "eslint.config.js": "ESLint",
    "eslint.config.mjs": "ESLint",
    "eslint.config.cjs": "ESLint",
    ".eslintignore": "ESLint Ignore",
    ".stylelintrc": "Stylelint",
    ".stylelintrc.json": "Stylelint",
    ".stylelintrc.yml": "Stylelint",
    ".stylelintrc.yaml": "Stylelint",
    ".stylelintrc.js": "Stylelint",
    "stylelint.config.js": "Stylelint",
    ".stylelintignore": "Stylelint Ignore",
    ".babelrc": "Babel",
    ".babelrc.js": "Babel",
    ".babelrc.cjs": "Babel",
    ".babelrc.mjs": "Babel",
    ".babelrc.json": "Babel",
    "babel.config.js": "Babel",
    "babel.config.cjs": "Babel",
    "babel.config.mjs": "Babel",
    "babel.config.json": "Babel",
    ".browserslistrc": "Browserslist",
    "browserslist": "Browserslist",
    "tsconfig.json": "TypeScript Config",
    "tsconfig.build.json": "TypeScript Config",
    "tsconfig.base.json": "TypeScript Config",
    "jsconfig.json": "JavaScript Config",
    ".swcrc": "SWC",
    ".terserrc": "Terser",
    ".postcssrc": "PostCSS",
    ".postcssrc.json": "PostCSS",
    ".postcssrc.yml": "PostCSS",
    ".postcssrc.js": "PostCSS",
    "postcss.config.js": "PostCSS",
    "postcss.config.cjs": "PostCSS",
    "postcss.config.mjs": "PostCSS",
    "tailwind.config.js": "Tailwind CSS",
    "tailwind.config.cjs": "Tailwind CSS",
    "tailwind.config.mjs": "Tailwind CSS",
    "tailwind.config.ts": "Tailwind CSS",
    "vite.config.js": "Vite",
    "vite.config.ts": "Vite",
    "vite.config.mjs": "Vite",
    "vite.config.mts": "Vite",
    "next.config.js": "Next.js",
    "next.config.mjs": "Next.js",
    "next.config.ts": "Next.js",
    "nuxt.config.js": "Nuxt",
    "nuxt.config.ts": "Nuxt",
    "svelte.config.js": "Svelte",
    "svelte.config.mjs": "Svelte",
    "astro.config.js": "Astro",
    "astro.config.mjs": "Astro",
    "astro.config.ts": "Astro",
    "remix.config.js": "Remix",
    "remix.config.mjs": "Remix",
    "gatsby-config.js": "Gatsby",
    "gatsby-config.ts": "Gatsby",
    "angular.json": "Angular",
    "vue.config.js": "Vue CLI",
    "webpack.config.js": "Webpack",
    "webpack.config.ts": "Webpack",
    "webpack.config.cjs": "Webpack",
    "webpack.config.mjs": "Webpack",
    "rollup.config.js": "Rollup",
    "rollup.config.ts": "Rollup",
    "rollup.config.mjs": "Rollup",
    "esbuild.config.js": "esbuild",
    "esbuild.config.mjs": "esbuild",
    "parcel.config.json": "Parcel",
    ".parcelrc": "Parcel",
    "turbo.json": "Turborepo",
    "nx.json": "Nx",
    "lerna.json": "Lerna",
    "rush.json": "Rush",
    "pnpm-workspace.yaml": "pnpm Workspace",
    ".npmrc": "npm Config",
    ".yarnrc": "Yarn Config",
    ".yarnrc.yml": "Yarn Config",
    ".nvmrc": "nvm",
    ".node-version": "Node Version",
    ".ruby-version": "Ruby Version",
    ".python-version": "Python Version",
    ".java-version": "Java Version",
    ".tool-versions": "asdf",
    "mise.toml": "mise",
    ".mise.toml": "mise",
    
    # Testing
    "jest.config.js": "Jest",
    "jest.config.ts": "Jest",
    "jest.config.mjs": "Jest",
    "jest.config.cjs": "Jest",
    "jest.config.json": "Jest",
    "jest.setup.js": "Jest Setup",
    "jest.setup.ts": "Jest Setup",
    "vitest.config.js": "Vitest",
    "vitest.config.ts": "Vitest",
    "vitest.config.mjs": "Vitest",
    "vitest.config.mts": "Vitest",
    "playwright.config.js": "Playwright",
    "playwright.config.ts": "Playwright",
    "cypress.json": "Cypress",
    "cypress.config.js": "Cypress",
    "cypress.config.ts": "Cypress",
    "cypress.config.mjs": "Cypress",
    ".mocharc.js": "Mocha",
    ".mocharc.json": "Mocha",
    ".mocharc.yml": "Mocha",
    ".mocharc.yaml": "Mocha",
    "karma.conf.js": "Karma",
    "protractor.conf.js": "Protractor",
    "pytest.ini": "pytest",
    "setup.cfg": "Python Config",
    "tox.ini": "tox",
    ".coveragerc": "Coverage.py",
    "coverage.xml": "Coverage Report",
    "phpunit.xml": "PHPUnit",
    "phpunit.xml.dist": "PHPUnit",
    ".rspec": "RSpec",
    "spec_helper.rb": "RSpec",
    "rails_helper.rb": "RSpec Rails",
    "Guardfile": "Guard",
    
    # Linting / Code Quality
    ".pylintrc": "Pylint",
    "pylintrc": "Pylint",
    ".flake8": "Flake8",
    ".isort.cfg": "isort",
    "pyproject.toml": "pyproject",
    ".mypy.ini": "mypy",
    "mypy.ini": "mypy",
    ".bandit": "Bandit",
    ".rubocop.yml": "RuboCop",
    ".rubocop_todo.yml": "RuboCop Todo",
    ".erb_lint.yml": "ERB Lint",
    ".standard.yml": "Standard Ruby",
    ".reek.yml": "Reek",
    ".solhint.json": "Solhint",
    ".soliumrc.json": "Solium",
    "phpcs.xml": "PHP_CodeSniffer",
    "phpcs.xml.dist": "PHP_CodeSniffer",
    "phpmd.xml": "PHPMD",
    ".php-cs-fixer.php": "PHP CS Fixer",
    ".php-cs-fixer.dist.php": "PHP CS Fixer",
    "phpstan.neon": "PHPStan",
    "phpstan.neon.dist": "PHPStan",
    ".golangci.yml": "golangci-lint",
    ".golangci.yaml": "golangci-lint",
    ".markdownlint.json": "markdownlint",
    ".markdownlint.yaml": "markdownlint",
    ".markdownlint.yml": "markdownlint",
    ".markdownlintrc": "markdownlint",
    ".yamllint": "yamllint",
    ".yamllint.yml": "yamllint",
    ".yamllint.yaml": "yamllint",
    ".shellcheckrc": "ShellCheck",
    ".hadolint.yaml": "Hadolint",
    "hadolint.yaml": "Hadolint",
    ".commitlintrc.json": "commitlint",
    ".commitlintrc.yml": "commitlint",
    ".commitlintrc.yaml": "commitlint",
    "commitlint.config.js": "commitlint",
    "commitlint.config.cjs": "commitlint",
    "commitlint.config.mjs": "commitlint",
    ".cz.json": "Commitizen",
    ".czrc": "Commitizen",
    "cz.json": "Commitizen",
    ".releaserc": "semantic-release",
    ".releaserc.json": "semantic-release",
    ".releaserc.yml": "semantic-release",
    ".releaserc.yaml": "semantic-release",
    ".releaserc.js": "semantic-release",
    "release.config.js": "semantic-release",
    "release.config.cjs": "semantic-release",
    "release.config.mjs": "semantic-release",
    ".husky": "Husky",
    ".huskyrc": "Husky",
    ".huskyrc.json": "Husky",
    ".huskyrc.js": "Husky",
    ".lintstagedrc": "lint-staged",
    ".lintstagedrc.json": "lint-staged",
    ".lintstagedrc.yml": "lint-staged",
    ".lintstagedrc.yaml": "lint-staged",
    ".lintstagedrc.js": "lint-staged",
    "lint-staged.config.js": "lint-staged",
    "lint-staged.config.cjs": "lint-staged",
    "lint-staged.config.mjs": "lint-staged",
    "renovate.json": "Renovate",
    "renovate.json5": "Renovate",
    ".renovaterc": "Renovate",
    ".renovaterc.json": "Renovate",
    "dependabot.yml": "Dependabot",
    ".dependabot/config.yml": "Dependabot",
    
    # Environment / Secrets
    ".env": "Environment",
    ".env.local": "Environment Local",
    ".env.development": "Environment Development",
    ".env.development.local": "Environment Development Local",
    ".env.test": "Environment Test",
    ".env.test.local": "Environment Test Local",
    ".env.staging": "Environment Staging",
    ".env.production": "Environment Production",
    ".env.production.local": "Environment Production Local",
    ".env.example": "Environment Example",
    ".env.sample": "Environment Sample",
    ".env.template": "Environment Template",
    ".envrc": "direnv",
    
    # Other common files
    "MANIFEST.in": "Manifest",
    "MANIFEST": "Manifest",
    "VERSION": "Version",
    "VERSION.txt": "Version",
    "Makefile.am": "Automake",
    "configure.ac": "Autoconf",
    "configure.in": "Autoconf",
    "config.h.in": "Autoconf Header",
    "aclocal.m4": "Aclocal",
    "Makefile.in": "Makefile Template",
    "install-sh": "Install Script",
    "configure": "Configure Script",
    "config.guess": "Config Guess",
    "config.sub": "Config Sub",
    "ltmain.sh": "Libtool",
    "depcomp": "Depcomp",
    "missing": "Automake Helper",
    "compile": "Automake Helper",
    "ar-lib": "Automake Helper",
    "test-driver": "Automake Helper",
    "INSTALL": "Install Instructions",
    "INSTALL.md": "Install Instructions",
    "INSTALL.txt": "Install Instructions",
}

# Language family classification
LANGUAGE_FAMILIES: Dict[str, List[str]] = {
    # Systems Programming
    "Systems": [
        "C", "C++", "Rust", "Go", "Zig", "Nim", "D", "V", "Odin", "Carbon",
        "Assembly", "NASM", "YASM", "GNU Assembly",
        "Verilog", "SystemVerilog", "VHDL", "Bluespec",
        "C Header", "C++ Header", "C++ Inline", "C++ Template", "C Inline", "D Interface",
    ],
    
    # Web Frontend
    "Web": [
        "JavaScript", "TypeScript", "TypeScript Declaration",
        "HTML", "XHTML", "CSS", "SCSS", "Sass", "Less", "Stylus",
        "React JSX", "React TSX", "Vue", "Svelte", "Astro",
        "WebAssembly", "WebAssembly Text", "WGSL",
    ],
    
    # Template Languages
    "Template": [
        "Liquid", "Handlebars", "EJS", "Pug", "Jade", "Mustache", "Nunjucks",
        "Twig", "Jinja", "Jinja2", "Slim", "HAML", "Marko", "Dust", "Eta", "Edge",
        "Blade", "Razor", "Razor VB", "ERB", "PHP HTML",
    ],
    
    # Scripting Languages
    "Scripting": [
        "Python", "Python Stub", "Cython", "Ruby", "Rake", "Gemspec",
        "Perl", "Perl Module", "Perl Documentation", "Perl Test",
        "Lua", "MoonScript", "Tcl", "Tcl/Tk", "AWK", "Sed",
        "Shell", "Bash", "Zsh", "Fish", "Korn Shell", "C Shell", "TENEX C Shell",
        "PowerShell", "PowerShell Module", "PowerShell Data", "Batch",
        "PHP",
    ],
    
    # JVM Languages
    "JVM": [
        "Java", "Kotlin", "Kotlin Script", "Scala", "Scala Script",
        "Groovy", "Gradle", "Gradle Kotlin", "Clojure", "ClojureScript", "Clojure Common",
    ],
    
    # Functional Languages
    "Functional": [
        "Haskell", "Literate Haskell", "Elm", "PureScript",
        "OCaml", "OCaml Interface", "OCaml Lex", "OCaml Yacc",
        "Reason", "Reason Interface", "ReScript", "ReScript Interface",
        "Standard ML", "Standard ML Signature", "Standard ML Functor",
        "F#", "F# Signature", "F# Script",
        "Erlang", "Erlang Header", "Erlang App",
        "Elixir", "Elixir Script", "EEx", "HEEx", "LEEx",
    ],
    
    # Lisp Family
    "Lisp": [
        "Lisp", "Common Lisp", "Emacs Lisp", "Emacs Lisp Compiled",
        "Scheme", "Racket", "Scribble", "Fennel", "Hy",
    ],
    
    # Data Science & Statistics
    "Data": [
        "R", "R Markdown", "R Noweb", "Julia", "Julia Markdown",
        "SQL", "PostgreSQL", "MySQL", "PL/SQL", "T-SQL",
        "MATLAB", "MATLAB Live", "SAS", "SPSS", "Stata", "Stata Data",
        "Stan", "BUGS", "JAGS",
    ],
    
    # Query Languages
    "Query": [
        "GraphQL", "Cypher", "SPARQL", "Prisma", "EdgeQL", "SurrealQL",
        "AQL", "N1QL", "Cassandra CQL", "Flux", "InfluxQL",
    ],
    
    # Configuration & Data Formats
    "Config": [
        "JSON", "JSON with Comments", "JSON5", "JSON Lines", "Newline JSON", "GeoJSON",
        "YAML", "XML", "XML Schema", "DTD", "RELAX NG", "XSLT",
        "TOML", "INI", "Config", "Environment", "Environment Example",
        "Environment Local", "Environment Development", "Environment Production",
        "Properties", "HOCON", "HCL", "Terraform", "Terraform Variables", "Terraform State",
        "Nix", "Dhall", "CUE", "Jsonnet", "Jsonnet Library", "Pkl", "Rego", "Sentinel",
        "RON", "KDL", "EDN",
    ],
    
    # Documentation & Markup
    "Documentation": [
        "Markdown", "MDX", "Readme", "Changelog", "History", "News", "Changes",
        "LaTeX", "LaTeX Style", "LaTeX Class", "BibTeX",
        "reStructuredText", "AsciiDoc", "Text",
        "Org Mode", "Pod", "RDoc", "Creole", "Wiki", "MediaWiki", "Textile",
        "Djot", "Typst", "Quarto",
    ],
    
    # DevOps & Infrastructure
    "DevOps": [
        "Dockerfile", "Containerfile", "Docker Compose", "Docker Ignore",
        "Makefile", "Justfile", "Taskfile", "Earthfile", "Snakemake",
        "Gradle", "Gradle Kotlin", "Gradle Settings", "Gradle Kotlin Settings",
        "CMake", "Meson", "Ninja", "Bazel", "Starlark", "Buck", "GN", "GN Include",
        "GYP", "GYP Include", "SCons", "Premake", "xmake", "Tup",
        "Puppet", "Puppet Template", "Ansible", "Salt", "Chef",
        "Terraform", "Bicep", "ARM Template", "CloudFormation", "AWS SAM", "Pulumi",
        "Kubernetes", "Helm", "Helm Chart", "Kustomize",
        "Jenkinsfile", "Travis CI", "GitLab CI", "GitHub Actions", "CircleCI",
        "Azure Pipelines", "Bitbucket Pipelines", "AppVeyor", "Drone CI",
        "Netlify", "Vercel", "Render", "Fly.io", "Railway", "Heroku",
        "Vagrantfile", "Procfile", "Brewfile",
    ],
    
    # Microsoft Ecosystem
    "Microsoft": [
        "C#", "C# Script", "VB.NET", "VBScript",
        "F#", "F# Signature", "F# Script",
        "ASP Classic", "ASP.NET", "ASP.NET Control", "ASP.NET Service", "ASP.NET Handler",
        "Razor", "Razor VB",
        "Solution", "C# Project", "F# Project", "VB.NET Project", "VC++ Project",
        "MSBuild Targets", "MSBuild Props", "MSBuild Project",
    ],
    
    # Apple Ecosystem
    "Apple": [
        "Swift", "Swift Package", "Swift Package Lock",
        "Objective-C", "Objective-C++",
        "Storyboard", "Interface Builder", "Xcode Project", "Xcode Config",
        "Entitlements", "Property List",
    ],
    
    # Mobile Development
    "Mobile": [
        "Dart", "Dart ARB", "Flutter",
        "Android IDL", "Android HAL",
        "Kotlin", "Kotlin Script", "Java",
    ],
    
    # Blockchain & Smart Contracts
    "Blockchain": [
        "Solidity", "Vyper", "Yul", "Move", "Clarity", "Ride", "TEAL",
        "LIGO", "CameLIGO", "JsLIGO", "ReasonLIGO",
        "Michelson", "Func", "Cairo", "ink!",
    ],
    
    # Game Development
    "Game": [
        "GDScript", "Godot Scene", "Godot Resource", "Godot NativeScript", "Godot Shader",
        "Shader", "HLSL", "GLSL", "Fragment Shader", "Vertex Shader",
        "Geometry Shader", "Compute Shader", "Tessellation Control", "Tessellation Evaluation",
        "SPIR-V", "Metal", "Cg", "Effect", "CgFX",
        "Unreal Asset", "Unreal Map", "Unreal Plugin", "Unreal Project",
        "Unity Scene", "Unity Prefab", "Unity Material", "Unity Animation",
        "Unity Controller", "Unity Asset",
    ],
    
    # Legacy Languages
    "Legacy": [
        "COBOL", "COBOL Copybook", "Fortran", "Fortran 77", "Fortran 90",
        "Fortran 95", "Fortran 2003", "Fortran 2008", "Fortran 2018",
        "Pascal", "Delphi", "Delphi Form", "Lazarus",
        "Ada", "Ada Body", "Ada Spec",
        "Forth", "Factor",
    ],
    
    # Other Programming Languages
    "Other Languages": [
        "CoffeeScript", "Literate CoffeeScript", "Crystal", "Crystal Template",
        "Io", "Ioke", "Pony", "Red", "Red/System", "Ring", "Wren",
        "Vala", "Vala API", "Haxe", "Haxe Build", "Mint", "Gleam", "Roc",
        "Unison", "Idris", "Agda", "Lean", "Coq", "PVS",
    ],
    
    # Notebooks & Literate Programming
    "Notebooks": [
        "Jupyter Notebook", "Quarto", "Weave Julia", "Julia Markdown", "Pluto",
        "R Markdown", "Literate Haskell", "Literate CoffeeScript",
    ],
    
    # API & Schema Definitions
    "API": [
        "OpenAPI", "Swagger", "RAML", "API Blueprint", "WSDL", "WADL",
        "gRPC", "Smithy", "AsyncAPI",
        "Protocol Buffers", "Thrift", "Avro Schema", "Avro IDL",
        "FlatBuffers", "Cap'n Proto",
    ],
    
    # Security & Certificates
    "Security": [
        "PEM Certificate", "Certificate", "DER Certificate",
        "PKCS12", "Private Key", "Public Key", "Certificate Request",
        "CA Certificate", "Java Keystore", "Trust Store",
    ],
    
    # License Files
    "License": [
        "License", "MIT License", "Apache License", "BSD License",
        "GPL License", "LGPL License", "MPL License", "ISC License",
        "WTFPL License", "CC0 License", "CC BY License", "Unlicense",
    ],
    
    # Package Management
    "Packages": [
        "npm Package", "npm Lock", "Yarn Lock", "pnpm Lock", "Bun Lock",
        "Cargo", "Cargo Lock", "Go Module", "Go Sum", "Go Workspace",
        "pyproject", "Python Setup", "Python Config", "Python Requirements", "Pipfile", "Pipfile Lock",
        "Poetry Lock", "PDM Lock", "uv Lock",
        "Composer", "Composer Lock", "Maven POM", "Gemfile", "Podfile",
        "CocoaPods", "Pubspec", "Pubspec Lock",
        "Mix", "Mix Lock", "Rebar", "Rebar Lock",
        "Cabal", "Stack", "Elm Package", "Dub", "Shards", "Shards Lock",
        "Spago", "Spago Packages", "Esy", "OPAM", "Dune", "Dune Project",
        "Julia Project", "Julia Manifest", "R Package", "R Namespace",
        "Conan", "vcpkg", "CPAN", "CPAN Meta",
        "NuGet Config", "NuGet Packages", "NuGet Props", "Paket", "Paket Lock",
    ],
    
    # Editor & IDE Configuration
    "Editor": [
        "EditorConfig", "Prettier", "Prettier Ignore",
        "ESLint", "ESLint Ignore", "Stylelint", "Stylelint Ignore",
        "Babel", "Browserslist",
        "TypeScript Config", "JavaScript Config", "SWC", "Terser",
        "PostCSS", "Tailwind CSS",
        "Vite", "Next.js", "Nuxt", "Svelte", "Astro", "Remix", "Gatsby",
        "Angular", "Vue CLI", "Webpack", "Rollup", "esbuild", "Parcel",
        "Turborepo", "Nx", "Lerna", "Rush", "pnpm Workspace",
    ],
    
    # Testing Frameworks
    "Testing": [
        "Jest", "Jest Setup", "Vitest", "Playwright", "Cypress", "Mocha", "Karma", "Protractor",
        "pytest", "tox", "Coverage.py", "Coverage Report",
        "PHPUnit", "RSpec", "RSpec Rails", "Guard",
    ],
    
    # Linting & Code Quality
    "Linting": [
        "Pylint", "Flake8", "isort", "mypy", "Bandit",
        "RuboCop", "RuboCop Todo", "ERB Lint", "Standard Ruby", "Reek",
        "Solhint", "Solium",
        "PHP_CodeSniffer", "PHPMD", "PHP CS Fixer", "PHPStan",
        "golangci-lint", "markdownlint", "yamllint", "ShellCheck", "Hadolint",
        "commitlint", "Commitizen", "semantic-release",
        "Husky", "lint-staged", "Renovate", "Dependabot",
    ],
    
    # Version Control
    "VCS": [
        "Git Ignore", "Git Attributes", "Git Modules", "Git Keep", "Git Config", "Git Message", "Git Mailmap",
        "Mercurial Ignore", "Mercurial Config", "SVN Ignore", "CVS Ignore", "Bazaar Ignore", "Perforce Ignore",
        "Code Owners",
    ],
    
    # Audio & Music
    "Audio": [
        "ABC Notation", "LilyPond", "LilyPond Include", "MMA",
        "Csound", "SuperCollider", "Faust", "Faust DSP", "ChucK", "Sonic Pi",
    ],
    
    # Data Formats
    "Data Files": [
        "CSV", "TSV", "Parquet", "Arrow", "ORC", "Avro",
        "Log", "Diff", "Patch", "iCalendar", "vCard",
    ],
}


def get_language_name(extension: str, filename: Optional[str] = None) -> str:
    """
    Get human-readable language name for an extension or filename.
    
    First checks if the filename matches a known pattern (for files without
    extensions like Makefile, Dockerfile, LICENSE, etc.), then falls back
    to extension-based lookup.
    
    Args:
        extension: File extension (e.g., ".py")
        filename: Optional full filename for special file detection
        
    Returns:
        Language name (e.g., "Python") or capitalized extension if unknown
    """
    # First, check filename mapping for special files (Makefile, Dockerfile, etc.)
    if filename:
        # Try exact filename match
        language = FILENAME_TO_LANGUAGE.get(filename)
        if language:
            return language
        
        # Try case-insensitive match for common variations
        language = FILENAME_TO_LANGUAGE.get(filename.lower())
        if language:
            return language
        
        # Try matching just the base filename (without path)
        base_filename = filename.split("/")[-1].split("\\")[-1]
        if base_filename != filename:
            language = FILENAME_TO_LANGUAGE.get(base_filename)
            if language:
                return language
            language = FILENAME_TO_LANGUAGE.get(base_filename.lower())
            if language:
                return language
    
    if not extension:
        return "Unknown"
    
    # Normalize extension (lowercase, ensure starts with dot)
    ext = extension.lower()
    if not ext.startswith("."):
        ext = "." + ext
    
    # Lookup in extension dictionary
    language = EXTENSION_TO_LANGUAGE.get(ext)
    if language:
        return language
    
    # Fallback: capitalize extension without dot
    if ext.startswith("."):
        return ext[1:].capitalize()
    return ext.capitalize()


def classify_language_family(language_name: str) -> str:
    """
    Classify a language into its family.
    
    Args:
        language_name: Human-readable language name
        
    Returns:
        Family name or "Other" if not found
    """
    for family, languages in LANGUAGE_FAMILIES.items():
        if language_name in languages:
            return family
    return "Other"


def compute_ecosystem_breakdown(
    insights: Dict[str, Any],
    analysis_data: Dict[str, Any]
) -> Dict[str, Dict[str, Any]]:
    """
    Group languages by family and calculate statistics per family.
    
    Args:
        insights: Insights dictionary
        analysis_data: Raw analysis data
        
    Returns:
        Dictionary mapping family names to their statistics
    """
    by_extension = analysis_data.get("by_extension", {})
    total_lines = analysis_data.get("total_lines", 0)
    
    if total_lines == 0:
        return {}
    
    # Group by family
    family_stats: Dict[str, Dict[str, int]] = {}
    
    for ext, stats in by_extension.items():
        language_name = get_language_name(ext, filename=ext)
        family = classify_language_family(language_name)
        
        if family not in family_stats:
            family_stats[family] = {"files": 0, "lines": 0}
        
        family_stats[family]["files"] += stats.get("files", 0)
        family_stats[family]["lines"] += stats.get("lines", 0)
    
    # Calculate percentages and format
    breakdown = {}
    for family, stats in family_stats.items():
        percentage = (stats["lines"] / total_lines) * 100.0
        breakdown[family] = {
            "files": stats["files"],
            "lines": stats["lines"],
            "percentage": percentage
        }
    
    return breakdown



def generate_directory_tree(
    path: str,
    max_depth: int = 3,
    max_items_per_level: int = 100,
    display_name: Optional[str] = None
) -> str:
    """
    Generate comprehensive directory tree representation.
    
    Shows all files and directories up to the specified depth without
    truncation to provide a complete view of the project structure.
    
    Args:
        path: Path to repository directory
        max_depth: Maximum depth to traverse (default 3 for better visibility)
        max_items_per_level: Maximum items to show per level (default 100 to show all)
        display_name: Optional name to display as root (overrides path-based extraction)
        
    Returns:
        Formatted directory tree string
    """
    repo_name = display_name if display_name else extract_repo_name(path)
    
    # Normalize path to handle tilde, relative paths, and symlinks
    try:
        path_obj = normalize_path(path)
    except Exception:
        # Fallback to Path if normalization fails
        path_obj = Path(path)
    
    if not path_obj.exists() or not path_obj.is_dir():
        return f"{repo_name}/\n└── (empty)"
    
    # Priority files and directories
    priority_files = {
        "README.md", "LICENSE", "LICENSE.txt", "setup.py", "pyproject.toml",
        "package.json", "Cargo.toml", "go.mod", "requirements.txt",
        "Pipfile", "poetry.lock", "package-lock.json", "yarn.lock"
    }
    priority_dirs = {"src", "lib", "tests", "test", "docs", "doc", "config", "scripts"}
    
    # Skip patterns
    skip_dirs = {
        "__pycache__", "node_modules", ".git", "build", "dist", ".pytest_cache",
        "target", "bin", "obj", ".venv", "venv", ".env"
    }
    
    lines = [f"{repo_name}/"]
    
    def should_skip(name: str) -> bool:
        """Check if item should be skipped."""
        if name.startswith(".") and name not in {".gitignore", ".env.example", ".dockerignore"}:
            return True
        # Skip egg-info directories
        if name.endswith(".egg-info"):
            return True
        return name in skip_dirs
    
    def format_tree_item(prefix: str, name: str, is_last: bool, is_dir: bool = False) -> str:
        """Format a single tree item."""
        connector = "└──" if is_last else "├──"
        return f"{prefix}{connector} {name}"
    
    def collect_items(dir_path: Path, depth: int, prefix: str = "") -> List[str]:
        """Recursively collect directory items."""
        if depth > max_depth:
            return []
        
        items = []
        try:
            entries = list(dir_path.iterdir())
        except PermissionError:
            return []
        
        # Separate into directories and files, and filter skipped items
        directories = []
        files = []
        
        for entry in entries:
            if should_skip(entry.name):
                continue
            
            if entry.is_dir():
                directories.append(entry)
            else:
                files.append(entry)
        
        # Sort directories alphabetically (case-insensitive)
        directories.sort(key=lambda x: x.name.lower())
        
        # Sort files alphabetically (case-insensitive)
        files.sort(key=lambda x: x.name.lower())
        
        # Combine: all directories first, then all files (both alphabetically sorted)
        all_items = directories + files
        
        # Truncate if needed
        total_items = len(all_items)
        show_items = all_items[:max_items_per_level]
        truncated = total_items > max_items_per_level
        
        for i, entry in enumerate(show_items):
            is_last = (i == len(show_items) - 1) and not truncated
            is_dir = entry.is_dir()
            
            item_name = entry.name
            if is_dir:
                items.append(format_tree_item(prefix, item_name, is_last, True))
                
                # Recurse for directories
                next_prefix = prefix + ("    " if is_last else "│   ")
                sub_items = collect_items(entry, depth + 1, next_prefix)
                items.extend(sub_items)
            else:
                items.append(format_tree_item(prefix, item_name, is_last, False))
        
        # Add truncation note if needed
        if truncated:
            remaining = total_items - max_items_per_level
            trunc_prefix = prefix + "└──"
            items.append(f"{trunc_prefix} ... ({remaining} more items)")
        
        return items
    
    tree_items = collect_items(path_obj, 0)
    lines.extend(tree_items)
    
    return "\n".join(lines)


def format_largest_file_display(
    extension: str,
    by_extension: Dict[str, Dict[str, int]]
) -> str:
    """
    Format largest file display string.
    
    Args:
        extension: Extension string
        by_extension: Extension statistics
        
    Returns:
        Formatted string like "Python (avg 234 lines/file)" or "Python"
    """
    if not extension:
        return "N/A"
    
    language_name = get_language_name(extension)
    stats = by_extension.get(extension, {})
    
    files = stats.get("files", 0)
    lines = stats.get("lines", 0)
    
    if files > 0:
        avg_lines = lines / files
        if avg_lines > 200:
            return f"{language_name} (avg {int(avg_lines)} lines/file)"
    
    return language_name


def generate_project_snapshot_table(
    analysis_data: Dict[str, Any],
    insights: Dict[str, Any]
) -> str:
    """
    Generate project snapshot table.
    
    Args:
        analysis_data: Raw analysis data
        insights: Insights dictionary
        
    Returns:
        Markdown table string
    """
    total_files = analysis_data.get("total_files", 0)
    total_lines = analysis_data.get("total_lines", 0)
    total_chars = analysis_data.get("total_characters", 0)
    
    dominant_ext = insights.get("dominant_language", "")
    dominant_lang = get_language_name(dominant_ext) if dominant_ext else "N/A"
    health_score = insights.get("health_score", 0)
    
    lines = [
        "## Project Snapshot",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Files | {total_files:,} |",
        f"| Lines | {total_lines:,} |",
        f"| Characters | {total_chars:,} |",
        f"| Dominant Language | {dominant_lang} |",
        f"| Health Score | {health_score}/10 |",
    ]
    
    return "\n".join(lines)


def generate_language_breakdown_table(
    analysis_data: Dict[str, Any],
    insights: Dict[str, Any]
) -> str:
    """
    Generate language breakdown table with language names and visual bars in % column.
    
    Args:
        analysis_data: Raw analysis data
        insights: Insights dictionary
        
    Returns:
        Markdown table string with language names and visual bars
    """
    by_extension = analysis_data.get("by_extension", {})
    percentage_by_extension = insights.get("percentage_by_extension", {})
    
    # Sort by lines descending, limit to top 15
    sorted_exts = sorted(
        by_extension.items(),
        key=lambda x: x[1].get("lines", 0),
        reverse=True
    )[:15]
    
    lines = [
        "## Language Breakdown",
        "",
        "| Language | Files | Lines | % |",
        "|----------|-------|-------|---|",
    ]
    
    for ext, stats in sorted_exts:
        # Use language name instead of extension
        # ext could be a file extension (e.g., ".py") or filename (e.g., "Makefile")
        language_name = get_language_name(ext, filename=ext) if ext else "Unknown"
        files = stats.get("files", 0)
        line_count = stats.get("lines", 0)
        percentage = percentage_by_extension.get(ext, 0.0)
        
        # Calculate bar length (proportional, max 15 blocks for table)
        bar_length = int((percentage / 100.0) * 15)
        bar = "█" * bar_length if bar_length > 0 else ""
        
        # Format: Language | Files | Lines | Bar Percentage%
        lines.append(
            f"| {language_name} | {files:,} | {line_count:,} | {bar} {percentage:.1f}% |"
        )
    
    return "\n".join(lines)


def generate_language_distribution_bar(insights: Dict[str, Any]) -> str:
    """
    Generate GitHub-style language distribution bar with rankings.
    
    Combines visual bars and numbered rankings in one section.
    
    Args:
        insights: Insights dictionary
        
    Returns:
        Formatted bar and rankings string
    """
    language_ranking = insights.get("language_ranking", [])
    
    if not language_ranking:
        return "## Language Distribution (Rankings)\n\n(No languages found)"
    
    # Show top 10 languages
    top_languages = language_ranking[:10]
    
    lines = ["## Language Distribution (Rankings)", ""]
    
    # Visual bars
    for ext, percentage in top_languages:
        language_name = get_language_name(ext, filename=ext)
        
        # Calculate bar length (proportional, max 20 blocks)
        bar_length = int((percentage / 100.0) * 20)
        bar = "█" * bar_length
        
        lines.append(f"{language_name} {bar} {percentage:.1f}%")
    
    lines.append("")  # Blank line between bars and rankings
    
    # Numbered rankings
    for i, (ext, percentage) in enumerate(top_languages, 1):
        language_name = get_language_name(ext, filename=ext)
        lines.append(f"{i}. {language_name} — {percentage:.1f}%")
    
    return "\n".join(lines)


def generate_ecosystem_breakdown_table(insights: Dict[str, Any]) -> str:
    """
    Generate ecosystem breakdown table.
    
    Args:
        insights: Insights dictionary with ecosystem_breakdown
        
    Returns:
        Markdown table string
    """
    ecosystem_breakdown = insights.get("ecosystem_breakdown", {})
    
    if not ecosystem_breakdown:
        return "## Ecosystem Breakdown\n\n(No ecosystem data)"
    
    # Sort by percentage descending, limit to top 8
    sorted_families = sorted(
        ecosystem_breakdown.items(),
        key=lambda x: x[1].get("percentage", 0.0),
        reverse=True
    )[:8]
    
    lines = [
        "## Ecosystem Breakdown",
        "",
        "| Family | Files | Lines | % |",
        "|--------|-------|-------|---|",
    ]
    
    for family, stats in sorted_families:
        files = stats.get("files", 0)
        line_count = stats.get("lines", 0)
        percentage = stats.get("percentage", 0.0)
        
        lines.append(
            f"| {family} | {files:,} | {line_count:,} | {percentage:.1f}% |"
        )
    
    return "\n".join(lines)


def generate_rankings_list(insights: Dict[str, Any]) -> str:
    """
    Generate language rankings numbered list.
    
    Args:
        insights: Insights dictionary
        
    Returns:
        Formatted rankings string
    """
    language_ranking = insights.get("language_ranking", [])
    
    if not language_ranking:
        return "## Rankings\n\n(No languages found)"
    
    # Show top 10
    top_languages = language_ranking[:10]
    
    lines = ["## Rankings", ""]
    
    for i, (ext, percentage) in enumerate(top_languages, 1):
        language_name = get_language_name(ext, filename=ext)
        lines.append(f"{i}. {language_name} — {percentage:.1f}%")
    
    return "\n".join(lines)


def _generate_repo_seed(repo_path: str, analysis_data: Dict[str, Any]) -> int:
    """
    Generate deterministic seed from repository path and key metrics.
    
    Args:
        repo_path: Path to repository
        analysis_data: Analysis data for additional entropy
        
    Returns:
        Integer seed for random number generation
    """
    # Create hash from repo path and key metrics
    seed_string = f"{repo_path}_{analysis_data.get('total_files', 0)}_{analysis_data.get('total_lines', 0)}"
    seed_hash = hashlib.md5(seed_string.encode()).hexdigest()
    # Convert first 8 hex chars to integer
    return int(seed_hash[:8], 16)


def _select_phrase(phrases: List[str], seed: int, index: int, weights: Optional[List[float]] = None) -> str:
    """
    Select a phrase from list using deterministic randomness with optional weights.
    
    Args:
        phrases: List of phrase options
        seed: Base seed for randomness
        index: Index to vary selection
        weights: Optional weights for phrases (must match length)
        
    Returns:
        Selected phrase
    """
    if not phrases:
        return ""
    
    rng = random.Random(seed + index)
    
    if weights and len(weights) == len(phrases):
        return rng.choices(phrases, weights=weights)[0]
    return rng.choice(phrases)


def generate_insights_text(
    insights: Dict[str, Any],
    analysis_data: Dict[str, Any],
    repo_path: str = ""
) -> str:
    """
    Generate dynamic human-readable insights paragraph using phrase banks.
    
    Args:
        insights: Insights dictionary
        analysis_data: Raw analysis data
        repo_path: Repository path for deterministic seed
        
    Returns:
        Professional analysis paragraph (exactly 3 sentences)
    """
    # Generate deterministic seed
    seed = _generate_repo_seed(repo_path, analysis_data)
    
    dominant_ext = insights.get("dominant_language", "")
    dominant_lang = get_language_name(dominant_ext) if dominant_ext else "mixed languages"
    
    avg_lines = insights.get("average_lines_per_file", 0.0)
    doc_ratio = insights.get("documentation_ratio", {}).get("files", 0.0)
    balance_score = insights.get("structural_balance_score", 0.0)
    complexity = insights.get("complexity_level", "Medium")
    health_score = insights.get("health_score", 5)
    
    # Get ecosystem info
    ecosystem_breakdown = insights.get("ecosystem_breakdown", {})
    top_family = ""
    if ecosystem_breakdown:
        sorted_families = sorted(
            ecosystem_breakdown.items(),
            key=lambda x: x[1].get("percentage", 0.0),
            reverse=True
        )
        if sorted_families:
            top_family = sorted_families[0][0]
    
    # Build sentence components with metadata for flexible ordering
    sentence_components = []
    component_index = 0
    
    # 1. Dominant language (always first if present)
    if dominant_lang != "mixed languages":
        lang_phrase = _select_phrase(DOMINANT_LANGUAGE_PHRASES, seed, component_index)
        sentence_components.append({
            "text": lang_phrase.format(language=dominant_lang),
            "priority": 0,  # Always first
            "needs_transition": False
        })
        component_index += 1
    
    # 2. Documentation commentary
    if doc_ratio > 0.1:
        doc_phrase = _select_phrase(DOCUMENTATION_HIGH_PHRASES, seed, component_index)
        sentence_components.append({
            "text": doc_phrase,
            "priority": 1,
            "needs_transition": True
        })
    elif doc_ratio > 0.05:
        doc_phrase = _select_phrase(DOCUMENTATION_MEDIUM_PHRASES, seed, component_index)
        sentence_components.append({
            "text": doc_phrase,
            "priority": 1,
            "needs_transition": True
        })
    elif doc_ratio > 0:
        doc_phrase = _select_phrase(DOCUMENTATION_LOW_PHRASES, seed, component_index)
        sentence_components.append({
            "text": doc_phrase,
            "priority": 1,
            "needs_transition": True
        })
    else:
        doc_phrase = _select_phrase(DOCUMENTATION_NONE_PHRASES, seed, component_index)
        sentence_components.append({
            "text": doc_phrase,
            "priority": 1,
            "needs_transition": True
        })
    component_index += 1
    
    # 3. Complexity commentary
    if complexity == "Low":
        complexity_phrase = _select_phrase(COMPLEXITY_LOW_PHRASES, seed, component_index)
        sentence_components.append({
            "text": complexity_phrase,
            "priority": 2,
            "needs_transition": True
        })
    elif complexity == "Medium":
        complexity_phrase = _select_phrase(COMPLEXITY_MEDIUM_PHRASES, seed, component_index)
        sentence_components.append({
            "text": complexity_phrase,
            "priority": 2,
            "needs_transition": True
        })
    else:  # High
        complexity_phrase = _select_phrase(COMPLEXITY_HIGH_PHRASES, seed, component_index)
        sentence_components.append({
            "text": complexity_phrase,
            "priority": 2,
            "needs_transition": True
        })
    component_index += 1
    
    # 4. Code density commentary
    if 50 <= avg_lines <= 200:
        density_phrase = _select_phrase(DENSITY_REASONABLE_PHRASES, seed, component_index)
        sentence_components.append({
            "text": density_phrase,
            "priority": 3,
            "needs_transition": True
        })
    elif avg_lines < 50:
        density_phrase = _select_phrase(DENSITY_LOW_PHRASES, seed, component_index)
        sentence_components.append({
            "text": density_phrase,
            "priority": 3,
            "needs_transition": True
        })
    else:
        density_phrase = _select_phrase(DENSITY_HIGH_PHRASES, seed, component_index)
        sentence_components.append({
            "text": density_phrase,
            "priority": 3,
            "needs_transition": True
        })
    component_index += 1
    
    # 5. Structural balance commentary
    if balance_score > 0.6:
        balance_phrase = _select_phrase(BALANCE_GOOD_PHRASES, seed, component_index)
        sentence_components.append({
            "text": balance_phrase,
            "priority": 4,
            "needs_transition": True
        })
    elif balance_score > 0.3:
        balance_phrase = _select_phrase(BALANCE_MODERATE_PHRASES, seed, component_index)
        sentence_components.append({
            "text": balance_phrase,
            "priority": 4,
            "needs_transition": True
        })
    else:
        balance_phrase = _select_phrase(BALANCE_POOR_PHRASES, seed, component_index)
        sentence_components.append({
            "text": balance_phrase,
            "priority": 4,
            "needs_transition": True
        })
    component_index += 1
    
    # 6. Ecosystem commentary (if relevant)
    if top_family and top_family != "Other":
        ecosystem_phrase = _select_phrase(ECOSYSTEM_PHRASES, seed, component_index)
        sentence_components.append({
            "text": ecosystem_phrase.format(family=top_family),
            "priority": 5,
            "needs_transition": True
        })
        component_index += 1
    
    # 7. Health score commentary
    if health_score >= 8:
        health_phrase = _select_phrase(HEALTH_HIGH_PHRASES, seed, component_index)
        sentence_components.append({
            "text": health_phrase,
            "priority": 6,
            "needs_transition": True
        })
    elif health_score >= 5:
        health_phrase = _select_phrase(HEALTH_MEDIUM_PHRASES, seed, component_index)
        sentence_components.append({
            "text": health_phrase,
            "priority": 6,
            "needs_transition": True
        })
    else:
        health_phrase = _select_phrase(HEALTH_LOW_PHRASES, seed, component_index)
        sentence_components.append({
            "text": health_phrase,
            "priority": 6,
            "needs_transition": True
        })
    component_index += 1
    
    # Separate fixed priority (language) from variable priority components
    fixed_components = [c for c in sentence_components if c["priority"] == 0]
    variable_components = [c for c in sentence_components if c["priority"] > 0]
    
    # Select exactly 3 most relevant components for 99% accuracy
    # Priority order: language (if present) > health > complexity > documentation > balance > density
    selected_components = []
    
    # Always include language if present (sentence 1)
    if fixed_components:
        selected_components.append(fixed_components[0])
    
    # Score variable components by relevance and accuracy
    component_scores = []
    for comp in variable_components:
        priority = comp.get("priority", 99)
        # Lower priority number = higher importance
        # Health (6) and complexity (2) are most important
        score = 100 - priority
        if priority == 6:  # Health score
            score += 50  # Boost health score importance
        elif priority == 2:  # Complexity
            score += 30  # Boost complexity importance
        component_scores.append((score, comp))
    
    # Sort by score (highest first)
    component_scores.sort(key=lambda x: x[0], reverse=True)
    
    # Select top 2-3 variable components to reach exactly 3 sentences total
    needed = 3 - len(selected_components)
    for score, comp in component_scores[:needed]:
        selected_components.append(comp)
    
    # If we still don't have 3, fill with next best
    if len(selected_components) < 3:
        remaining = [comp for _, comp in component_scores[needed:]]
        selected_components.extend(remaining[:3 - len(selected_components)])
    
    # Limit to exactly 3 sentences
    ordered_components = selected_components[:3]
    
    # Build final sentences with natural transitions
    formatted_sentences = []
    for i, component in enumerate(ordered_components):
        text = component["text"].strip()
        if not text:
            continue
        
        # Add transition for variety (but not for first sentence)
        if i > 0 and component.get("needs_transition", False):
            transition = _select_phrase(TRANSITION_PHRASES, seed, i + 200)
            if transition:
                text = transition + text.lower()
        
        # Ensure first letter is capitalized
        if len(text) > 0:
            text = text[0].upper() + text[1:] if len(text) > 1 else text.upper()
        
        # Ensure proper sentence ending
        if not text.endswith(('.', '!', '?')):
            text += "."
        
        formatted_sentences.append(text)
    
    # Join with spaces for natural flow
    return " ".join(formatted_sentences)


def generate_recommendations(
    insights: Dict[str, Any],
    analysis_data: Dict[str, Any],
    repo_path: str = ""
) -> List[str]:
    """
    Generate conditional actionable recommendations using expanded phrase banks.
    
    Only generates recommendations when metrics trigger them. Uses expanded phrase bank
    for more variety and accuracy.
    
    Args:
        insights: Insights dictionary
        analysis_data: Raw analysis data
        repo_path: Repository path for deterministic seed
        
    Returns:
        List of 2-4 recommendation strings (only when conditions are met)
    """
    # Generate deterministic seed
    seed = _generate_repo_seed(repo_path, analysis_data)
    
    recommendations = []
    rec_scores = []  # Store recommendations with priority scores
    
    by_extension = analysis_data.get("by_extension", {})
    
    # Check for test files (check directory structure would require path access)
    has_tests = False
    test_patterns = ["test", "spec"]
    for ext, stats in by_extension.items():
        ext_lower = ext.lower()
        if any(pattern in ext_lower for pattern in test_patterns):
            if stats.get("files", 0) > 0:
                has_tests = True
                break
    
    # Conditional: Test coverage recommendation (highest priority)
    if not has_tests:
        test_phrase = _select_phrase(TEST_COVERAGE_PHRASES, seed, 0)
        rec_scores.append((100, test_phrase))  # Highest priority
    
    # Conditional: Documentation recommendation (high priority if very low)
    doc_ratio = insights.get("documentation_ratio", {}).get("files", 0.0)
    if doc_ratio < 0.05:  # Less than 5% documentation - critical
        doc_phrase = _select_phrase(DOCUMENTATION_RECOMMENDATIONS, seed, 1)
        rec_scores.append((90, doc_phrase))
    elif doc_ratio < 0.1:  # Less than 10% - still important
        doc_phrase = _select_phrase(DOCUMENTATION_RECOMMENDATIONS, seed, 1)
        rec_scores.append((70, doc_phrase))
    
    # Conditional: Large files / modularization (medium-high priority)
    largest_ext = insights.get("largest_file_extension", "")
    if largest_ext:
        largest_stats = by_extension.get(largest_ext, {})
        files = largest_stats.get("files", 1)
        lines = largest_stats.get("lines", 0)
        avg_lines = lines / files if files > 0 else 0
        if avg_lines > 1000:  # Very large files
            mod_phrase = _select_phrase(MODULARIZATION_PHRASES, seed, 2)
            rec_scores.append((80, mod_phrase))
        elif avg_lines > 500:  # Large files
            mod_phrase = _select_phrase(MODULARIZATION_PHRASES, seed, 2)
            rec_scores.append((60, mod_phrase))
    
    # Conditional: High complexity (medium priority)
    complexity = insights.get("complexity_level", "Medium")
    if complexity == "High":
        struct_phrase = _select_phrase(STRUCTURAL_PHRASES, seed, 3)
        rec_scores.append((50, struct_phrase))
    
    # Conditional: Poor structural balance (medium priority)
    balance_score = insights.get("structural_balance_score", 0.0)
    if balance_score < 0.2:  # Very poor balance
        struct_phrase = _select_phrase(STRUCTURAL_PHRASES, seed, 4)
        rec_scores.append((55, struct_phrase))
    elif balance_score < 0.3:  # Poor balance
        struct_phrase = _select_phrase(STRUCTURAL_PHRASES, seed, 4)
        rec_scores.append((45, struct_phrase))
    
    # Conditional: Low health score (medium priority)
    health_score = insights.get("health_score", 5)
    if health_score < 4:  # Very low health
        health_phrase = _select_phrase(HEALTH_IMPROVEMENT_PHRASES, seed, 5)
        rec_scores.append((65, health_phrase))
    elif health_score < 6:  # Low health
        health_phrase = _select_phrase(HEALTH_IMPROVEMENT_PHRASES, seed, 5)
        rec_scores.append((40, health_phrase))
    
    # Deduplicate recommendations by phrase text, keeping highest priority for each unique phrase
    unique_recs = {}
    for priority, phrase in rec_scores:
        if phrase not in unique_recs or priority > unique_recs[phrase]:
            unique_recs[phrase] = priority
    
    # Convert back to list of tuples for sorting
    rec_scores = [(priority, phrase) for phrase, priority in unique_recs.items()]
    
    # Sort by priority score (highest first) and take top recommendations
    rec_scores.sort(key=lambda x: x[0], reverse=True)
    recommendations = [phrase for _, phrase in rec_scores[:4]]  # Top 4 max
    
    # Ensure at least 2 recommendations if we have any issues
    if len(recommendations) == 1 and rec_scores:
        # Add second highest priority if available
        if len(rec_scores) > 1:
            recommendations.append(rec_scores[1][1])
    
    return recommendations


def generate_key_metrics_list(
    insights: Dict[str, Any],
    analysis_data: Dict[str, Any]
) -> str:
    """
    Generate key metrics bullet list.
    
    Args:
        insights: Insights dictionary
        analysis_data: Raw analysis data
        
    Returns:
        Formatted metrics list
    """
    avg_lines = insights.get("average_lines_per_file", 0.0)
    doc_ratio = insights.get("documentation_ratio", {}).get("files", 0.0)
    largest_ext = insights.get("largest_file_extension", "")
    complexity = insights.get("complexity_level", "Medium")
    
    by_extension = analysis_data.get("by_extension", {})
    largest_display = format_largest_file_display(largest_ext, by_extension)
    
    # Format documentation ratio
    if doc_ratio > 0:
        code_files = analysis_data.get("total_files", 0) - by_extension.get(".md", {}).get("files", 0)
        md_files = by_extension.get(".md", {}).get("files", 0)
        if code_files > 0 and md_files > 0:
            ratio_display = f"{doc_ratio:.3f} (1:{int(code_files/md_files)} ratio)"
        else:
            ratio_display = f"{doc_ratio:.3f}"
    else:
        ratio_display = "0.000 (no documentation)"
    
    lines = [
        "## Key Metrics",
        "",
        f"- Average lines per file: {int(avg_lines)}",
        f"- Documentation ratio: {ratio_display}",
        f"- Largest file extension: {largest_display}",
        f"- Complexity estimate: {complexity}",
    ]
    
    return "\n".join(lines)


def generate_markdown_report(
    analysis_data: Dict[str, Any],
    insights: Dict[str, Any],
    repo_path: str,
    analysis_path: Optional[str] = None
) -> str:
    """
    Generate complete Markdown intelligence report.
    
    Args:
        analysis_data: Raw analysis data
        insights: Insights dictionary (with ecosystem_breakdown computed)
        repo_path: Path or URL to repository (for name extraction)
        analysis_path: Actual directory path to analyze (for tree generation, defaults to repo_path)
        
    Returns:
        Complete Markdown report string
    """
    # Compute ecosystem breakdown if not present
    if "ecosystem_breakdown" not in insights or not insights["ecosystem_breakdown"]:
        insights["ecosystem_breakdown"] = compute_ecosystem_breakdown(insights, analysis_data)
    
    # Extract repo name for header (from repo_path which may be URL or path)
    repo_name = extract_repo_name(repo_path)
    
    # Use analysis_path for tree generation (actual directory), fallback to repo_path if not provided
    tree_path = analysis_path if analysis_path else repo_path
    
    # Handle empty repository
    if analysis_data.get("total_files", 0) == 0:
        return (
            f"# RepoLens Report For {repo_name}.\n\n"
            "## Project Snapshot\n\n"
            "| Metric | Value |\n"
            "|--------|-------|\n"
            "| Files | 0 |\n"
            "| Lines | 0 |\n"
            "| Characters | 0 |\n"
            "| Dominant Language | N/A |\n"
            "| Health Score | 0/10 |\n\n"
            "No analyzable files found in repository.\n"
        )
    
    sections = [
        f"# RepoLens Report For {repo_name}.",
        "",
        generate_project_snapshot_table(analysis_data, insights),
        "",
        "## Project Structure",
        "",
        "```",
        generate_directory_tree(tree_path, display_name=repo_name),
        "```",
        "",
        generate_language_breakdown_table(analysis_data, insights),
        "",
        generate_ecosystem_breakdown_table(insights),
        "",
        "## Insights",
        "",
        generate_insights_text(insights, analysis_data, tree_path),
        "",
        "## Recommendations",
        "",
    ]
    
    recommendations = generate_recommendations(insights, analysis_data, repo_path)
    if recommendations:
        for rec in recommendations:
            sections.append(f"- {rec}")
    else:
        sections.append("- Repository structure is well-maintained")
    
    sections.append("")
    sections.append(generate_key_metrics_list(insights, analysis_data))
    
    return "\n".join(sections)


# ============================================================================
# Export Functionality
# ============================================================================

def _generate_filename(extension: str, repo_name: Optional[str] = None) -> str:
    """
    Generate a timestamped filename for exports.
    
    Args:
        extension: File extension (e.g., "json", "csv")
        repo_name: Optional repository name to include in filename
        
    Returns:
        Filename in format: {repo_name}_repolens_report_HHMMSS.{extension}
        or repolens_report_HHMMSS.{extension} if repo_name is None
    """
    timestamp = datetime.now().strftime("%H%M%S")
    if repo_name and repo_name != "unknown":
        return f"{repo_name}_repolens_report_{timestamp}.{extension}"
    return f"repolens_report_{timestamp}.{extension}"


def export_json(data: Dict[str, Any], output_path: Optional[str] = None, output_dir: Optional[str] = None, repo_path: Optional[str] = None) -> str:
    """
    Export analysis data to a JSON file.
    
    Args:
        data: Analysis data dictionary
        output_path: Optional custom output path. If None, generates timestamped filename.
        output_dir: Optional output directory. If provided, saves file there.
        repo_path: Optional repository path/URL to extract repo name for filename
        
    Returns:
        Path to the exported JSON file
    """
    if output_path is None:
        repo_name = extract_repo_name(repo_path) if repo_path else None
        filename = _generate_filename("json", repo_name)
        if output_dir:
            output_path_obj = Path(output_dir) / filename
        else:
            output_path_obj = Path(filename)
    else:
        output_path_obj = Path(output_path)
        if output_dir:
            output_path_obj = Path(output_dir) / output_path_obj.name
    
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path_obj, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return str(output_path_obj.absolute())


def export_csv(data: Dict[str, Any], output_path: Optional[str] = None, output_dir: Optional[str] = None, repo_path: Optional[str] = None) -> str:
    """
    Export analysis data to a CSV file.
    
    Flattens the nested extension data into rows.
    
    Args:
        data: Analysis data dictionary
        output_path: Optional custom output path. If None, generates timestamped filename.
        output_dir: Optional output directory. If provided, saves file there.
        repo_path: Optional repository path/URL to extract repo name for filename
        
    Returns:
        Path to the exported CSV file
    """
    if output_path is None:
        repo_name = extract_repo_name(repo_path) if repo_path else None
        filename = _generate_filename("csv", repo_name)
        if output_dir:
            output_path_obj = Path(output_dir) / filename
        else:
            output_path_obj = Path(filename)
    else:
        output_path_obj = Path(output_path)
        if output_dir:
            output_path_obj = Path(output_dir) / output_path_obj.name
    
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path_obj, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(["Metric", "Value"])
        
        # Write summary rows
        writer.writerow(["Total Files", data.get("total_files", 0)])
        writer.writerow(["Total Lines", data.get("total_lines", 0)])
        writer.writerow(["Total Characters", data.get("total_characters", 0)])
        
        # Write empty row for separation
        writer.writerow([])
        
        # Write extension header
        writer.writerow(["Extension", "Files", "Lines", "Characters"])
        
        # Write extension data
        by_extension = data.get("by_extension", {})
        for ext, stats in sorted(by_extension.items()):
            writer.writerow([
                ext or "(no extension)",
                stats.get("files", 0),
                stats.get("lines", 0),
                stats.get("characters", 0)
            ])
    
    return str(output_path_obj.absolute())


def export_markdown(markdown_content: str, output_path: Optional[str] = None, output_dir: Optional[str] = None, repo_path: Optional[str] = None) -> str:
    """
    Export Markdown content to a file.
    
    Args:
        markdown_content: Markdown string content
        output_path: Optional custom output path. If None, generates timestamped filename.
        output_dir: Optional output directory. If provided, saves file there.
        repo_path: Optional repository path/URL to extract repo name for filename
        
    Returns:
        Path to the exported Markdown file
    """
    if output_path is None:
        repo_name = extract_repo_name(repo_path) if repo_path else None
        filename = _generate_filename("md", repo_name)
        if output_dir:
            output_path_obj = Path(output_dir) / filename
        else:
            output_path_obj = Path(filename)
    else:
        output_path_obj = Path(output_path)
        if output_dir:
            output_path_obj = Path(output_dir) / output_path_obj.name
    
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path_obj, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    return str(output_path_obj.absolute())
