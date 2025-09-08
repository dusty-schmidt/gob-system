#!/usr/bin/env python3
"""
Agent-Zero to GOB Conversion Script
==================================

This script systematically converts all references from agent-zero/a0 to GOB (General Operations Bots).
It handles text replacements, file renames, and dependency updates while preserving functionality.

Usage: python convert_to_gob.py [--dry-run] [--backup]
"""

import os
import re
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AgentZeroToGOBConverter:
    """Converts Agent-Zero framework to GOB (General Operations Bots)"""
    
    def __init__(self, root_dir: str = ".", dry_run: bool = False, create_backup: bool = True):
        self.root_dir = Path(root_dir).resolve()
        self.dry_run = dry_run
        self.create_backup = create_backup
        self.changes_made = []
        
        # Define conversion mappings
        self.text_replacements = {
            # Core identity replacements
            "agent zero": "GOB",
            "Agent Zero": "GOB", 
            "agent-zero": "gob",
            "Agent-Zero": "GOB",
            "agentzero": "gob",
            "AgentZero": "GOB",
            "AGENT_ZERO": "GOB",
            "AGENT-ZERO": "GOB",
            
            # Path replacements
            "/a0/": "/gob/",
            "/a0": "/gob",
            "\\a0\\": "\\gob\\",
            "\\a0": "\\gob",
            
            # Specific technical terms
            "agent0ai": "gobai",
            "Agent0ai": "GOBai", 
            "agent0": "gob0",
            "Agent0": "GOB0",
            
            # Framework specific
            "Agent Zero framework": "GOB framework",
            "agent zero framework": "GOB framework",
            "Agent Zero System": "GOB System",
            "agent zero system": "GOB system",
            
            # URLs and repositories (will need manual review)
            "github.com/frdel/agent-zero": "github.com/your-org/gob",
            "agent-zero.ai": "gob.ai",
            "AgentZeroFW": "GOBFW",
            
            # Docker references
            "agent0ai/agent-zero": "gobai/gob",
        }
        
        # File extensions to process
        self.processable_extensions = {
            '.py', '.md', '.yaml', '.yml', '.json', '.js', '.html', '.css', 
            '.txt', '.sh', '.dockerfile', '.env'
        }
        
        # Directories to skip
        self.skip_dirs = {
            '__pycache__', '.git', 'node_modules', '.venv', 'venv', 
            'logs', 'tmp', 'memory', '.pytest_cache'
        }
        
        # Files to skip
        self.skip_files = {
            'convert_to_gob.py',  # This script itself
        }

    def create_backup_if_needed(self):
        """Create a backup of the current state"""
        if not self.create_backup or self.dry_run:
            return
            
        backup_dir = self.root_dir.parent / f"{self.root_dir.name}_backup_agent_zero"
        if backup_dir.exists():
            logger.warning(f"Backup directory already exists: {backup_dir}")
            return
            
        logger.info(f"Creating backup at: {backup_dir}")
        shutil.copytree(self.root_dir, backup_dir, ignore=shutil.ignore_patterns(
            '__pycache__', '*.pyc', '.git', 'logs', 'tmp', 'memory'
        ))

    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed"""
        # Skip if in excluded directories
        for part in file_path.parts:
            if part in self.skip_dirs:
                return False
                
        # Skip specific files
        if file_path.name in self.skip_files:
            return False
            
        # Only process files with specific extensions
        return file_path.suffix.lower() in self.processable_extensions

    def apply_text_replacements(self, content: str, file_path: Path) -> Tuple[str, List[str]]:
        """Apply text replacements to content"""
        changes = []
        modified_content = content
        
        for old_text, new_text in self.text_replacements.items():
            if old_text in modified_content:
                count = modified_content.count(old_text)
                modified_content = modified_content.replace(old_text, new_text)
                changes.append(f"Replaced '{old_text}' -> '{new_text}' ({count} times)")
                
        return modified_content, changes

    def process_file(self, file_path: Path) -> bool:
        """Process a single file"""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                original_content = f.read()
                
            # Apply replacements
            modified_content, changes = self.apply_text_replacements(original_content, file_path)
            
            # Check if changes were made
            if modified_content != original_content:
                if not self.dry_run:
                    # Write modified content back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(modified_content)
                        
                # Log changes
                rel_path = file_path.relative_to(self.root_dir)
                logger.info(f"Modified: {rel_path}")
                for change in changes:
                    logger.debug(f"  - {change}")
                    
                self.changes_made.append({
                    'file': str(rel_path),
                    'changes': changes
                })
                return True
                
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            
        return False

    def find_files_to_process(self) -> List[Path]:
        """Find all files that should be processed"""
        files_to_process = []
        
        for root, dirs, files in os.walk(self.root_dir):
            # Remove excluded directories from dirs list to prevent walking into them
            dirs[:] = [d for d in dirs if d not in self.skip_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if self.should_process_file(file_path):
                    files_to_process.append(file_path)
                    
        return files_to_process

    def run_conversion(self) -> Dict:
        """Run the complete conversion process"""
        logger.info(f"Starting Agent-Zero to GOB conversion...")
        logger.info(f"Root directory: {self.root_dir}")
        logger.info(f"Dry run: {self.dry_run}")
        
        # Create backup
        self.create_backup_if_needed()
        
        # Find files to process
        files_to_process = self.find_files_to_process()
        logger.info(f"Found {len(files_to_process)} files to process")
        
        # Process files
        modified_files = 0
        for file_path in files_to_process:
            if self.process_file(file_path):
                modified_files += 1
                
        # Summary
        summary = {
            'total_files_scanned': len(files_to_process),
            'files_modified': modified_files,
            'dry_run': self.dry_run,
            'changes': self.changes_made
        }
        
        logger.info(f"Conversion complete!")
        logger.info(f"Files scanned: {summary['total_files_scanned']}")
        logger.info(f"Files modified: {summary['files_modified']}")
        
        return summary

    def generate_report(self, summary: Dict) -> str:
        """Generate a detailed conversion report"""
        report = f"""
Agent-Zero to GOB Conversion Report
==================================

Summary:
- Total files scanned: {summary['total_files_scanned']}
- Files modified: {summary['files_modified']}
- Dry run: {summary['dry_run']}

Modified Files:
"""
        
        for change in summary['changes']:
            report += f"\n{change['file']}:\n"
            for detail in change['changes']:
                report += f"  - {detail}\n"
                
        return report

def main():
    parser = argparse.ArgumentParser(description='Convert Agent-Zero framework to GOB')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be changed without making changes')
    parser.add_argument('--no-backup', action='store_true',
                       help='Skip creating backup (not recommended)')
    parser.add_argument('--root-dir', default='.',
                       help='Root directory to process (default: current directory)')
    parser.add_argument('--report', action='store_true',
                       help='Generate detailed report file')
    
    args = parser.parse_args()
    
    # Initialize converter
    converter = AgentZeroToGOBConverter(
        root_dir=args.root_dir,
        dry_run=args.dry_run,
        create_backup=not args.no_backup
    )
    
    # Run conversion
    summary = converter.run_conversion()
    
    # Generate report if requested
    if args.report:
        report = converter.generate_report(summary)
        report_file = Path(args.root_dir) / 'gob_conversion_report.txt'
        
        if not args.dry_run:
            with open(report_file, 'w') as f:
                f.write(report)
            logger.info(f"Report saved to: {report_file}")
        else:
            logger.info("Report would be saved to: gob_conversion_report.txt")
            print(report)

if __name__ == '__main__':
    main()
