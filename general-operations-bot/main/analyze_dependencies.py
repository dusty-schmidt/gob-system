#!/usr/bin/env python3
"""
GOB to GOB Dependency Analysis Script
===========================================

This script analyzes all dependencies and potential breaking changes when converting
from gob to GOB. It identifies critical paths, imports, and configurations
that need careful handling.

Usage: python analyze_dependencies.py [--output-json] [--detailed]
"""

import os
import re
import json
import ast
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DependencyAnalyzer:
    """Analyzes dependencies for GOB to GOB conversion"""
    
    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir).resolve()
        self.analysis_results = {
            'file_references': defaultdict(list),
            'path_dependencies': defaultdict(list),
            'import_dependencies': defaultdict(list),
            'config_dependencies': defaultdict(list),
            'external_references': defaultdict(list),
            'critical_files': [],
            'potential_issues': [],
            'safe_to_change': [],
            'requires_manual_review': []
        }
        
        # Patterns to search for
        self.patterns = {
            'a0_paths': [
                r'/gob[/\\]',
                r'/gob$',
                r'\\gob[/\\]',
                r'\\gob$',
                r'"a0"',
                r"'a0'",
                r'=a0[/\\]',
                r'a0[/\\]tmp',
                r'a0[/\\]memory',
                r'a0[/\\]logs'
            ],
            'agent_zero_refs': [
                r'agent[_-]?zero',
                r'Agent[_-]?Zero',
                r'AGENT[_-]?ZERO',
                r'gobai',
                r'GOBFW'
            ],
            'external_urls': [
                r'https?://[^\s]*agent[_-]?zero[^\s]*',
                r'github\.com/[^\s]*agent[_-]?zero[^\s]*',
                r'docker\.io/[^\s]*agent[_-]?zero[^\s]*'
            ],
            'config_keys': [
                r'agent_profile',
                r'agent_memory',
                r'agent_knowledge'
            ]
        }
        
        self.skip_dirs = {'__pycache__', '.git', 'node_modules', 'logs', 'tmp', 'memory'}
        self.processable_extensions = {'.py', '.md', '.yaml', '.yml', '.json', '.js', '.html', '.css', '.txt', '.sh'}

    def analyze_python_imports(self, file_path: Path) -> List[Dict]:
        """Analyze Python imports for potential issues"""
        issues = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Parse AST to find imports
            try:
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if 'a0' in alias.name or 'agent' in alias.name.lower():
                                issues.append({
                                    'type': 'import',
                                    'line': node.lineno,
                                    'content': alias.name,
                                    'severity': 'high'
                                })
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and ('a0' in node.module or 'agent' in node.module.lower()):
                            issues.append({
                                'type': 'import_from',
                                'line': node.lineno,
                                'content': node.module,
                                'severity': 'high'
                            })
            except SyntaxError:
                # If AST parsing fails, fall back to regex
                import_lines = re.findall(r'^(import|from)\s+.*', content, re.MULTILINE)
                for i, line in enumerate(import_lines):
                    if 'a0' in line or 'agent' in line.lower():
                        issues.append({
                            'type': 'import_regex',
                            'line': i + 1,
                            'content': line.strip(),
                            'severity': 'medium'
                        })
                        
        except Exception as e:
            logger.warning(f"Could not analyze imports in {file_path}: {e}")
            
        return issues

    def analyze_file_content(self, file_path: Path) -> Dict:
        """Analyze a single file for dependencies and references"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read {file_path}: {e}")
            return {}
            
        analysis = {
            'path': str(file_path.relative_to(self.root_dir)),
            'size': len(content),
            'matches': defaultdict(list),
            'severity': 'low',
            'issues': []
        }
        
        # Check for various patterns
        for pattern_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                if matches:
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        line_content = content.split('\n')[line_num - 1].strip()
                        analysis['matches'][pattern_type].append({
                            'pattern': pattern,
                            'match': match.group(),
                            'line': line_num,
                            'context': line_content
                        })
        
        # Special analysis for Python files
        if file_path.suffix == '.py':
            python_issues = self.analyze_python_imports(file_path)
            analysis['issues'].extend(python_issues)
            
        # Determine severity
        if analysis['matches']['a0_paths'] or analysis['issues']:
            analysis['severity'] = 'high'
        elif analysis['matches']['agent_zero_refs']:
            analysis['severity'] = 'medium'
        elif analysis['matches']['external_urls']:
            analysis['severity'] = 'low'
            
        return analysis

    def categorize_files(self, analyses: List[Dict]) -> Dict:
        """Categorize files based on their conversion requirements"""
        categories = {
            'critical': [],      # Files that could break functionality
            'important': [],     # Files that need careful review
            'standard': [],      # Files with simple text replacements
            'external': [],      # Files with external references only
            'safe': []          # Files that are safe to auto-convert
        }
        
        for analysis in analyses:
            file_path = analysis['path']
            
            # Critical files (could break functionality)
            if (analysis['matches']['a0_paths'] or 
                analysis['issues'] or
                'config' in file_path.lower() or
                'settings' in file_path.lower() or
                file_path.endswith('.py')):
                categories['critical'].append(analysis)
                
            # Important files (need review)
            elif (analysis['matches']['agent_zero_refs'] and 
                  ('prompt' in file_path.lower() or 
                   'agent' in file_path.lower() or
                   file_path.endswith('.md'))):
                categories['important'].append(analysis)
                
            # External references only
            elif analysis['matches']['external_urls'] and not analysis['matches']['agent_zero_refs']:
                categories['external'].append(analysis)
                
            # Standard replacements
            elif analysis['matches']['agent_zero_refs']:
                categories['standard'].append(analysis)
                
            # Safe files
            else:
                categories['safe'].append(analysis)
                
        return categories

    def generate_conversion_plan(self, categories: Dict) -> Dict:
        """Generate a step-by-step conversion plan"""
        plan = {
            'phase_1_critical': {
                'description': 'Handle critical files that could break functionality',
                'files': [f['path'] for f in categories['critical']],
                'actions': [
                    'Create backup of entire system',
                    'Review each file manually before conversion',
                    'Test after each critical file conversion',
                    'Update path references carefully'
                ]
            },
            'phase_2_important': {
                'description': 'Convert important files with careful review',
                'files': [f['path'] for f in categories['important']],
                'actions': [
                    'Review agent prompts and roles',
                    'Update documentation systematically',
                    'Maintain functional equivalence'
                ]
            },
            'phase_3_standard': {
                'description': 'Automated conversion of standard files',
                'files': [f['path'] for f in categories['standard']],
                'actions': [
                    'Run automated text replacement',
                    'Verify no functionality changes'
                ]
            },
            'phase_4_external': {
                'description': 'Update external references',
                'files': [f['path'] for f in categories['external']],
                'actions': [
                    'Update URLs and links',
                    'Update repository references',
                    'Update documentation links'
                ]
            }
        }
        return plan

    def run_analysis(self) -> Dict:
        """Run complete dependency analysis"""
        logger.info(f"Starting dependency analysis for: {self.root_dir}")
        
        all_analyses = []
        file_count = 0
        
        # Walk through all files
        for root, dirs, files in os.walk(self.root_dir):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix in self.processable_extensions:
                    file_count += 1
                    analysis = self.analyze_file_content(file_path)
                    if analysis and (analysis['matches'] or analysis['issues']):
                        all_analyses.append(analysis)
        
        logger.info(f"Analyzed {file_count} files, found {len(all_analyses)} with references")
        
        # Categorize files
        categories = self.categorize_files(all_analyses)
        
        # Generate conversion plan
        conversion_plan = self.generate_conversion_plan(categories)
        
        # Compile final results
        results = {
            'summary': {
                'total_files_analyzed': file_count,
                'files_with_references': len(all_analyses),
                'critical_files': len(categories['critical']),
                'important_files': len(categories['important']),
                'standard_files': len(categories['standard']),
                'external_only': len(categories['external']),
                'safe_files': len(categories['safe'])
            },
            'file_analyses': all_analyses,
            'categories': categories,
            'conversion_plan': conversion_plan,
            'recommendations': self.generate_recommendations(categories)
        }
        
        return results

    def generate_recommendations(self, categories: Dict) -> List[str]:
        """Generate recommendations for the conversion"""
        recommendations = [
            "1. BACKUP: Create a complete backup before starting conversion",
            "2. TESTING: Set up a test environment to validate changes",
            "3. PHASED APPROACH: Convert in phases starting with critical files",
        ]
        
        if categories['critical']:
            recommendations.append(f"4. CRITICAL: {len(categories['critical'])} critical files need manual review")
            
        if categories['important']:
            recommendations.append(f"5. IMPORTANT: {len(categories['important'])} important files need careful conversion")
            
        recommendations.extend([
            "6. AUTOMATION: Use the conversion script for standard text replacements",
            "7. VALIDATION: Test each phase before proceeding to the next",
            "8. DOCUMENTATION: Update all documentation and README files",
            "9. EXTERNAL: Update external URLs and repository references last"
        ])
        
        return recommendations

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze dependencies for GOB to GOB conversion')
    parser.add_argument('--root-dir', default='.', help='Root directory to analyze')
    parser.add_argument('--output-json', help='Save results to JSON file')
    parser.add_argument('--detailed', action='store_true', help='Show detailed analysis')
    
    args = parser.parse_args()
    
    analyzer = DependencyAnalyzer(args.root_dir)
    results = analyzer.run_analysis()
    
    # Print summary
    print("\n" + "="*60)
    print("GOB TO GOB CONVERSION ANALYSIS")
    print("="*60)
    
    summary = results['summary']
    print(f"Total files analyzed: {summary['total_files_analyzed']}")
    print(f"Files with references: {summary['files_with_references']}")
    print(f"Critical files: {summary['critical_files']}")
    print(f"Important files: {summary['important_files']}")
    print(f"Standard files: {summary['standard_files']}")
    print(f"External references only: {summary['external_only']}")
    
    print("\nRECOMMENDATIONS:")
    for rec in results['recommendations']:
        print(f"  {rec}")
    
    if args.detailed:
        print("\nCONVERSION PLAN:")
        for phase, details in results['conversion_plan'].items():
            print(f"\n{phase.upper().replace('_', ' ')}:")
            print(f"  Description: {details['description']}")
            print(f"  Files: {len(details['files'])}")
            if details['files']:
                for file in details['files'][:5]:  # Show first 5
                    print(f"    - {file}")
                if len(details['files']) > 5:
                    print(f"    ... and {len(details['files']) - 5} more")
    
    # Save to JSON if requested
    if args.output_json:
        with open(args.output_json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nDetailed results saved to: {args.output_json}")

if __name__ == '__main__':
    main()
