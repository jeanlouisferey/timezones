#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard library imports
import argparse
import sys
from pathlib import Path

# Local imports

from timezone_manager import TimezoneManager
from table_generator import TableGenerator

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate a visual timetable showing working hours across different time zones."
    )
    parser.add_argument(
        "-r", "--reference",
        required=True,
        help="Reference country code (e.g., 'FRA' for France)"
    )
    parser.add_argument(
        "-c", "--countries",
        required=True,
        type=Path,
        help="Path to text file containing list of country codes"
    )
    parser.add_argument(
        "--early-late-color",
        default="#FFD700",
        help="Color for early/late hours (default: Gold)"
    )
    parser.add_argument(
        "--noon-color",
        default="#87CEEB",
        help="Color for noon hours (default: Sky Blue)"
    )
    parser.add_argument(
        "--normal-color",
        default="white",
        help="Color for normal working hours (default: White)"
    )
    parser.add_argument(
        "-o", "--output",
        default="timetable.png",
        help="Output PNG file path (default: timetable.png)"
    )
    
    args = parser.parse_args()
    
    # Validate countries file exists
    if not args.countries.is_file():
        parser.error(f"Countries file not found: {args.countries}")
    
    return args

def main():
    """Main program entry point."""
    try:
        args = parse_arguments()
        
        # Initialize timezone manager
        tz_manager = TimezoneManager(args.reference)
        
        # Load target timezones
        timezone_data = tz_manager.load_timezones(args.countries)
        if not timezone_data:
            raise ValueError("No valid timezones found in the input file")
            
        # Prepare colors dictionary
        colors = {
            'early_late': args.early_late_color,
            'noon': args.noon_color,
            'normal': args.normal_color
        }
        
        # Initialize table generator
        table_gen = TableGenerator(colors)
        
        # Prepare data for the table
        table_data = []
        for country_name, tz in timezone_data:
            table_data.append({
                'country': country_name,
                'timezone': tz,
                'periods': tz_manager.get_time_periods(tz)
            })
        
        # Sort data by first time period
        table_data = sorted(table_data, key=lambda x: x['periods'][0]['time'].hour * 60 + x['periods'][0]['time'].minute)
        
        # Generate the table
        table_gen.generate_table(
            table_data,
            args.output,
            tz_manager.reference_tz,
            tz_manager
        )
        print(f"Timetable generated successfully: {args.output}")
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()