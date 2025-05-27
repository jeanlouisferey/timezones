#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import pytz
import pycountry
from typing import Dict, Optional, Tuple

class TimezoneManager:
    def __init__(self, reference_timezone):
        """Initialize the timezone manager.
        
        Args:
            reference_timezone (str): Reference timezone (country code or timezone identifier)
        """
        self._initialize_country_mappings()
        
        try:
            # Handle both timezone and country code input for reference
            if '-' in reference_timezone:  # Multi-timezone country code
                if reference_timezone not in self.multi_timezone_countries:
                    raise ValueError(f"Invalid multi-timezone country code: {reference_timezone}")
                reference_timezone = self.multi_timezone_countries[reference_timezone][1]
            else:  # Standard country code or timezone
                country = pycountry.countries.get(alpha_3=reference_timezone)
                if country:
                    # Get timezones for this country's alpha-2 code
                    matching_zones = pytz.country_timezones.get(country.alpha_2, [])
                    if matching_zones:
                        reference_timezone = matching_zones[0]
                    else:
                        raise ValueError(f"No timezone found for country: {reference_timezone}")
            
            self.reference_tz = pytz.timezone(reference_timezone)
        except pytz.exceptions.UnknownTimeZoneError:
            raise ValueError(f"Invalid timezone or country code: {reference_timezone}")
        
        # Working hours in reference timezone
        self.working_hours = {
            'start': 8,  # 08:00
            'end': 20,   # 20:00
        }

    def _initialize_country_mappings(self):
        """Initialize mappings between countries and timezones."""
        # Initialize dictionaries
        self.country_to_timezone: Dict[str, str] = {}
        self.timezone_to_country: Dict[str, str] = {}
        self.alpha3_to_name: Dict[str, str] = {}

        # Special handling for multi-timezone countries
        self.multi_timezone_countries = {
            'USA-E': ('United States (Eastern)', 'America/New_York'),
            'USA-C': ('United States (Central)', 'America/Chicago'),
            'USA-M': ('United States (Mountain)', 'America/Denver'),
            'USA-P': ('United States (Pacific)', 'America/Los_Angeles'),
            'RUS-W': ('Russia (Western)', 'Europe/Moscow'),
            'RUS-C': ('Russia (Central)', 'Asia/Yekaterinburg'),
            'RUS-E': ('Russia (Eastern)', 'Asia/Vladivostok'),
            'CAN-E': ('Canada (Eastern)', 'America/Toronto'),
            'CAN-C': ('Canada (Central)', 'America/Winnipeg'),
            'CAN-M': ('Canada (Mountain)', 'America/Edmonton'),
            'CAN-P': ('Canada (Pacific)', 'America/Vancouver'),
            'BRA-E': ('Brazil (Eastern)', 'America/Sao_Paulo'),
            'BRA-C': ('Brazil (Central)', 'America/Manaus'),
            'CHN-E': ('China (Eastern)', 'Asia/Shanghai'),
            'CHN-W': ('China (Western)', 'Asia/Urumqi'),
            'AUS-E': ('Australia (Eastern)', 'Australia/Sydney'),
            'AUS-C': ('Australia (Central)', 'Australia/Adelaide'),
            'AUS-W': ('Australia (Western)', 'Australia/Perth'),
        }

        # Add multi-timezone countries
        for code, (name, tz) in self.multi_timezone_countries.items():
            self.country_to_timezone[code] = tz
            self.timezone_to_country[tz] = name
            self.alpha3_to_name[code] = name

        # Process all countries from pycountry
        for country in pycountry.countries:
            self.alpha3_to_name[country.alpha_3] = country.name
            
            # Skip multi-timezone countries as they're handled separately
            if country.alpha_3 in ['USA', 'RUS', 'CAN', 'BRA', 'CHN', 'AUS']:
                continue
            
            # Find matching timezones for this country
            matching_zones = [tz for tz in pytz.all_timezones if country.alpha_2 in pytz.country_timezones.get(country.alpha_2, [])]
            
            if matching_zones:
                # Use the first timezone as default for the country
                self.country_to_timezone[country.alpha_3] = matching_zones[0]
                if matching_zones[0] not in self.timezone_to_country:
                    self.timezone_to_country[matching_zones[0]] = country.name

    def get_timezone_for_country(self, country_code: str) -> Optional[str]:
        """Get timezone identifier for a country code.
        
        Args:
            country_code (str): Country code (alpha-3 or special multi-timezone code)
            
        Returns:
            Optional[str]: Timezone identifier or None if not found
        """
        # Check multi-timezone countries first
        if country_code in self.multi_timezone_countries:
            return self.multi_timezone_countries[country_code][1]

        try:
            # Try to get the country from the alpha-3 code
            country = pycountry.countries.get(alpha_3=country_code)
            if country:
                # Get timezones for this country's alpha-2 code
                matching_zones = pytz.country_timezones.get(country.alpha_2, [])
                if matching_zones:
                    return matching_zones[0]  # Return first timezone
        except (KeyError, AttributeError):
            pass
        return None
    
    def load_timezones(self, timezone_file) -> list[Tuple[str, pytz.timezone]]:
        """Load timezones from a file.
        
        Args:
            timezone_file (Path): Path to file containing country codes
            
        Returns:
            list: List of tuples (country_name, timezone_object)
        """
        timezone_data = []
        with open(timezone_file, 'r') as f:
            for line in f:
                # Skip empty lines and comments
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Extract country code (first word before any comment or whitespace)
                country_code = line.split('#')[0].strip()
                country_code = country_code.split()[0] if country_code else ''
                
                if not country_code:
                    continue
                
                # Get timezone identifier from country code
                tz_name = self.get_timezone_for_country(country_code)
                if not tz_name:
                    country_name = self.alpha3_to_name.get(country_code, country_code)
                    print(f"Warning: Unknown country code ignored: {country_code} ({country_name})")
                    continue
                
                try:
                    tz = pytz.timezone(tz_name)
                    country_name = self.get_country_name(country_code)
                    timezone_data.append((country_name, tz))
                except pytz.exceptions.UnknownTimeZoneError:
                    country_name = self.alpha3_to_name.get(country_code, country_code)
                    print(f"Warning: Invalid timezone ignored for country {country_name}: {tz_name}")
        return timezone_data
    
    def get_period_type(self, hour, minute=0):
        """Get the type of period for a given hour.
        
        Args:
            hour (int): Hour to check
            minute (int): Minute to check
            
        Returns:
            str: Period type ('early_late', 'noon', or 'normal')
        """
        # Convert hour and minute to a decimal hour for comparison
        decimal_hour = hour + minute / 60.0
        
        if decimal_hour < 9 or decimal_hour >= 18:
            return 'early_late'
        elif 12 <= decimal_hour < 13:
            return 'noon'
        else:
            return 'normal'
    
    def get_time_periods(self, target_tz, reference_time=None):
        """Get time periods for the target timezone.
        
        Args:
            target_tz (timezone): Target timezone
            reference_time (datetime, optional): Reference time. Defaults to current time.
            
        Returns:
            list: List of dictionaries containing time periods and their types
        """
        if reference_time is None:
            reference_time = datetime.now(self.reference_tz)
            
        # Get the start of the day in reference timezone
        ref_start = reference_time.replace(
            hour=self.working_hours['start'],
            minute=0,
            second=0,
            microsecond=0
        )
        
        periods = []
        current_hour = self.working_hours['start']
        
        while current_hour < self.working_hours['end']:
            # Get time in reference timezone
            ref_time = ref_start.replace(hour=current_hour)
            # Convert to target timezone
            target_time = ref_time.astimezone(target_tz)
            
            # Determine period type based on target timezone hour and minute
            target_hour = target_time.hour
            target_minute = target_time.minute
            period_type = self.get_period_type(target_hour, target_minute)
            
            periods.append({
                'time': target_time,
                'type': period_type
            })
            
            current_hour += 1
            
        return periods

    def format_time(self, dt):
        """Format datetime object to hour string.
        
        Args:
            dt (datetime): Datetime object
            
        Returns:
            str: Formatted time string (HH:00 or HH:MM)
        """
        # For timezones with 30-minute offsets, show the actual minutes
        if dt.minute != 0:
            return dt.strftime("%H:%M")
        return dt.strftime("%H:00")

    def get_country_name(self, country_code: str) -> str:
        """Get country name from country code.
        
        Args:
            country_code (str): Country code (alpha-3 or special multi-timezone code)
            
        Returns:
            str: Country name or code if not found
        """
        # Check multi-timezone countries first
        if country_code in self.multi_timezone_countries:
            return self.multi_timezone_countries[country_code][0]

        try:
            country = pycountry.countries.get(alpha_3=country_code)
            return country.name if country else country_code
        except (KeyError, AttributeError):
            return country_code

    def get_reference_country_name(self) -> str:
        """Get the name of the reference country.
        
        Returns:
            str: Country name
        """
        # Check if it's a multi-timezone country
        for code, (name, tz) in self.multi_timezone_countries.items():
            if tz == self.reference_tz.zone:
                return name

        # Otherwise, try to find the country by timezone
        for country in pycountry.countries:
            matching_zones = pytz.country_timezones.get(country.alpha_2, [])
            if self.reference_tz.zone in matching_zones:
                return country.name
        return self.reference_tz.zone.split('/')[-1]