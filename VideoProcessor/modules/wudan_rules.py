"""
Wudan Rules Engine for PhoneSync + VideoProcessor
Implements time-based rules for video categorization (converted from PowerShell logic)
"""

import logging
from datetime import datetime, time
from typing import Dict, Any, List, Tuple

class WudanRulesEngine:
    """
    Implements Wudan time-based rules for video categorization
    Converted from PowerShell Test-WudanTimeRules function
    """
    
    def __init__(self, config: Dict[str, Any], logger: logging.Logger):
        """Initialize Wudan rules engine with configuration"""
        self.config = config
        self.logger = logger
        self.wudan_rules = config['wudan_rules']
        
        # Parse time ranges for easier processing
        self._parse_time_ranges()
    
    def _parse_time_ranges(self):
        """Parse time range strings into time objects for efficient comparison"""
        self.parsed_rules = {
            'before_2021': {
                'days_of_week': set(self.wudan_rules['before_2021']['days_of_week']),
                'time_ranges': []
            },
            'after_2021': {
                'days_of_week': set(self.wudan_rules['after_2021']['days_of_week']),
                'time_ranges': {}
            }
        }
        
        # Parse before_2021 time ranges (simple list)
        for time_range in self.wudan_rules['before_2021']['time_ranges']:
            start_time = self._parse_time_string(time_range['start'])
            end_time = self._parse_time_string(time_range['end'])
            if start_time and end_time:
                self.parsed_rules['before_2021']['time_ranges'].append((start_time, end_time))
        
        # Parse after_2021 time ranges (day-specific)
        for day_str, time_ranges in self.wudan_rules['after_2021']['time_ranges'].items():
            day_num = int(day_str)
            parsed_ranges = []
            
            for time_range in time_ranges:
                start_time = self._parse_time_string(time_range['start'])
                end_time = self._parse_time_string(time_range['end'])
                if start_time and end_time:
                    parsed_ranges.append((start_time, end_time))
            
            self.parsed_rules['after_2021']['time_ranges'][day_num] = parsed_ranges
    
    def _parse_time_string(self, time_str: str) -> time:
        """
        Parse time string in HH:MM format to time object
        
        Args:
            time_str: Time string like "05:00" or "18:30"
            
        Returns:
            time object or None if parsing fails
        """
        try:
            hour, minute = map(int, time_str.split(':'))
            return time(hour, minute)
        except (ValueError, AttributeError):
            self.logger.warning(f"Invalid time format: {time_str}")
            return None
    
    def should_go_to_wudan_folder(self, file_date: datetime) -> bool:
        """
        Determine if a video file should go to the Wudan folder based on date/time rules
        This is the main function converted from PowerShell Test-WudanTimeRules
        
        Args:
            file_date: DateTime when the file was created/modified
            
        Returns:
            True if file should go to Wudan folder, False otherwise
        """
        year = file_date.year
        day_of_week = file_date.weekday()  # Python: Monday=0, Sunday=6
        file_time = file_date.time()
        
        # Convert Python weekday to PowerShell format (Sunday=0, Monday=1, etc.)
        powershell_day_of_week = (day_of_week + 1) % 7
        
        self.logger.debug(f"Checking Wudan rules for {file_date}: "
                         f"Year={year}, DayOfWeek={powershell_day_of_week}, Time={file_time}")
        
        # Determine which rule set to use
        if year < 2021:
            return self._check_before_2021_rules(powershell_day_of_week, file_time)
        else:
            return self._check_after_2021_rules(powershell_day_of_week, file_time)
    
    def _check_before_2021_rules(self, day_of_week: int, file_time: time) -> bool:
        """
        Check before 2021 rules: Simple day/time ranges for all specified days
        
        Args:
            day_of_week: Day of week (Sunday=0, Monday=1, etc.)
            file_time: Time of day
            
        Returns:
            True if matches Wudan rules
        """
        rules = self.parsed_rules['before_2021']
        
        # Check if day of week matches
        if day_of_week not in rules['days_of_week']:
            self.logger.debug(f"Day {day_of_week} not in before_2021 days: {rules['days_of_week']}")
            return False
        
        # Check if time falls within any of the time ranges
        for start_time, end_time in rules['time_ranges']:
            if self._time_in_range(file_time, start_time, end_time):
                self.logger.debug(f"Time {file_time} matches before_2021 range: {start_time}-{end_time}")
                return True
        
        self.logger.debug(f"Time {file_time} does not match any before_2021 time ranges")
        return False
    
    def _check_after_2021_rules(self, day_of_week: int, file_time: time) -> bool:
        """
        Check after 2021 rules: Day-specific time ranges
        
        Args:
            day_of_week: Day of week (Sunday=0, Monday=1, etc.)
            file_time: Time of day
            
        Returns:
            True if matches Wudan rules
        """
        rules = self.parsed_rules['after_2021']
        
        # Check if day of week matches
        if day_of_week not in rules['days_of_week']:
            self.logger.debug(f"Day {day_of_week} not in after_2021 days: {rules['days_of_week']}")
            return False
        
        # Get day-specific time ranges
        day_time_ranges = rules['time_ranges'].get(day_of_week, [])
        
        if not day_time_ranges:
            self.logger.debug(f"No time ranges defined for day {day_of_week} in after_2021 rules")
            return False
        
        # Check if time falls within any of the day-specific time ranges
        for start_time, end_time in day_time_ranges:
            if self._time_in_range(file_time, start_time, end_time):
                self.logger.debug(f"Time {file_time} matches after_2021 range for day {day_of_week}: {start_time}-{end_time}")
                return True
        
        self.logger.debug(f"Time {file_time} does not match any after_2021 time ranges for day {day_of_week}")
        return False
    
    def _time_in_range(self, check_time: time, start_time: time, end_time: time) -> bool:
        """
        Check if a time falls within a time range
        
        Args:
            check_time: Time to check
            start_time: Start of range (inclusive)
            end_time: End of range (inclusive)
            
        Returns:
            True if time is in range
        """
        return start_time <= check_time <= end_time
    
    def get_wudan_rule_summary(self, file_date: datetime) -> Dict[str, Any]:
        """
        Get detailed information about why a file does/doesn't match Wudan rules
        
        Args:
            file_date: DateTime to analyze
            
        Returns:
            Dictionary with rule analysis details
        """
        year = file_date.year
        day_of_week = file_date.weekday()
        powershell_day_of_week = (day_of_week + 1) % 7
        file_time = file_date.time()
        
        rule_set = 'before_2021' if year < 2021 else 'after_2021'
        matches_wudan = self.should_go_to_wudan_folder(file_date)
        
        summary = {
            'file_date': file_date.strftime('%Y-%m-%d %H:%M:%S'),
            'year': year,
            'day_of_week': powershell_day_of_week,
            'day_name': file_date.strftime('%A'),
            'time': file_time.strftime('%H:%M'),
            'rule_set': rule_set,
            'matches_wudan': matches_wudan,
            'applicable_rules': self._get_applicable_rules(rule_set, powershell_day_of_week)
        }
        
        return summary
    
    def _get_applicable_rules(self, rule_set: str, day_of_week: int) -> Dict[str, Any]:
        """Get the applicable rules for a specific rule set and day"""
        rules = self.parsed_rules[rule_set]
        
        applicable = {
            'day_matches': day_of_week in rules['days_of_week'],
            'valid_days': list(rules['days_of_week']),
            'time_ranges': []
        }
        
        if rule_set == 'before_2021':
            applicable['time_ranges'] = [
                f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
                for start, end in rules['time_ranges']
            ]
        else:
            day_ranges = rules['time_ranges'].get(day_of_week, [])
            applicable['time_ranges'] = [
                f"{start.strftime('%H:%M')}-{end.strftime('%H:%M')}"
                for start, end in day_ranges
            ]
        
        return applicable
    
    def validate_rules_configuration(self) -> List[str]:
        """
        Validate the Wudan rules configuration
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        try:
            # Check before_2021 rules
            before_rules = self.wudan_rules['before_2021']
            if not isinstance(before_rules.get('days_of_week'), list):
                errors.append("before_2021.days_of_week must be a list")
            
            if not isinstance(before_rules.get('time_ranges'), list):
                errors.append("before_2021.time_ranges must be a list")
            
            # Check after_2021 rules
            after_rules = self.wudan_rules['after_2021']
            if not isinstance(after_rules.get('days_of_week'), list):
                errors.append("after_2021.days_of_week must be a list")
            
            if not isinstance(after_rules.get('time_ranges'), dict):
                errors.append("after_2021.time_ranges must be a dictionary")
            
            # Validate day numbers (0-6)
            for rule_set_name, rule_set in [('before_2021', before_rules), ('after_2021', after_rules)]:
                for day in rule_set.get('days_of_week', []):
                    if not isinstance(day, int) or day < 0 or day > 6:
                        errors.append(f"{rule_set_name}: Invalid day of week {day} (must be 0-6)")
            
        except Exception as e:
            errors.append(f"Error validating rules configuration: {e}")
        
        return errors
