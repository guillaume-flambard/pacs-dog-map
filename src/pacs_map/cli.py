"""
Command Line Interface for PACS Dog Map
"""

import argparse
import sys
from typing import List, Optional

from .config import Config
from .core import PacsMapGenerator
from .data import DataManager
from .operations import BatchOperations


class CLI:
    """Command Line Interface for PACS Dog Map"""
    
    def __init__(self):
        self.config = Config.from_env()
        self.map_generator = PacsMapGenerator(self.config)
        self.data_manager = DataManager(self.config)
        self.operations = BatchOperations(self.config)
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create the argument parser"""
        parser = argparse.ArgumentParser(
            description="PACS Dog Map - Animal Sterilization Tracking System",
            prog="pacs-map"
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Sync command
        sync_parser = subparsers.add_parser('sync', help='Sync data from Google Sheets')
        sync_parser.add_argument('--generate', action='store_true', 
                               help='Generate map after syncing')
        
        # Generate command
        generate_parser = subparsers.add_parser('generate', help='Generate the interactive map')
        generate_parser.add_argument('--output', '-o', help='Output file path')
        
        # List command
        list_parser = subparsers.add_parser('list', help='List animals')
        list_parser.add_argument('--pending', action='store_true', 
                               help='Show only pending animals')
        list_parser.add_argument('--priority', action='store_true',
                               help='Show priority order for field work')
        list_parser.add_argument('--location', help='Filter by location')
        
        # Complete command
        complete_parser = subparsers.add_parser('complete', help='Mark animals as completed')
        complete_parser.add_argument('ids', nargs='+', type=int,
                                   help='Animal IDs to mark as completed')
        
        # Report command  
        report_parser = subparsers.add_parser('report', help='Generate field work report')
        report_parser.add_argument('--output', '-o', help='Output CSV file path')
        
        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show statistics')
        
        return parser
    
    def run(self, args: List[str] = None) -> int:
        """Run the CLI with given arguments"""
        parser = self.create_parser()
        
        if args is None:
            args = sys.argv[1:]
        
        if not args:
            parser.print_help()
            return 0
        
        parsed_args = parser.parse_args(args)
        
        try:
            return self._execute_command(parsed_args)
        except Exception as e:
            print(f"❌ Error: {e}")
            return 1
    
    def _execute_command(self, args) -> int:
        """Execute the parsed command"""
        if args.command == 'sync':
            return self._sync_command(args)
        elif args.command == 'generate':
            return self._generate_command(args)
        elif args.command == 'list':
            return self._list_command(args)
        elif args.command == 'complete':
            return self._complete_command(args)
        elif args.command == 'report':
            return self._report_command(args)
        elif args.command == 'stats':
            return self._stats_command(args)
        else:
            print("❌ Unknown command")
            return 1
    
    def _sync_command(self, args) -> int:
        """Handle sync command"""
        df = self.data_manager.sync_from_google_sheets()
        if df is None:
            return 1
        
        if args.generate:
            self.map_generator.generate_map(df)
        
        return 0
    
    def _generate_command(self, args) -> int:
        """Handle generate command"""
        output_path = self.map_generator.generate_map()
        
        if args.output and args.output != output_path:
            import shutil
            shutil.copy2(output_path, args.output)
            print(f"📋 Map copied to {args.output}")
        
        return 0
    
    def _list_command(self, args) -> int:
        """Handle list command"""
        if args.priority:
            result = self.operations.generate_priority_list()
        elif args.location:
            result = self.operations.get_animals_by_location(args.location)
        else:
            result = self.operations.list_pending()
        
        return 0 if result is not None else 1
    
    def _complete_command(self, args) -> int:
        """Handle complete command"""
        updated = self.operations.mark_completed(args.ids)
        return 0 if updated > 0 else 1
    
    def _report_command(self, args) -> int:
        """Handle report command"""
        self.operations.export_field_report(args.output)
        return 0
    
    def _stats_command(self, args) -> int:
        """Handle stats command"""
        df = self.data_manager.load_data()
        if df is None:
            return 1
        
        stats = self.data_manager.get_statistics(df)
        
        print("\n📊 PACS DOG MAP STATISTICS")
        print("=" * 30)
        print(f"Total Animals: {stats['total_animals']}")
        print(f"With Coordinates: {stats['animals_with_coords']}")
        print(f"Pending: {stats['pending']}")
        print(f"Completed: {stats['completed']}")
        print(f"Pregnant (High Priority): {stats['pregnant']}")
        print(f"Wild Animals: {stats['wild']}")
        print(f"Friendly Animals: {stats['friendly']}")
        
        return 0


def main():
    """Main entry point"""
    cli = CLI()
    return cli.run()


if __name__ == '__main__':
    sys.exit(main())