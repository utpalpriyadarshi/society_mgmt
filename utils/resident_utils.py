# utils/resident_utils.py
"""
Resident utility functions for the Society Management System.
This module provides helper functions for working with residents.
"""

import re

def sort_residents_by_flat(residents):
    """
    Sort residents by flat number in ascending order.
    
    This function handles alphanumeric flat numbers properly by splitting them into
    numeric and text components and sorting accordingly.
    
    Args:
        residents: List of resident objects with flat_no attribute
        
    Returns:
        List of residents sorted by flat number
    """
    def extract_flat_parts(flat_no):
        """Extract numeric and text parts from flat number for proper sorting."""
        if not flat_no:
            return []
        
        # Split into numeric and non-numeric parts
        parts = re.split('([0-9]+)', flat_no)
        # Convert numeric parts to integers for proper sorting
        for i, part in enumerate(parts):
            if part.isdigit():
                parts[i] = int(part)
        return parts
    
    # Filter out residents without flat numbers and sort
    residents_with_flats = [r for r in residents if r.flat_no]
    return sorted(residents_with_flats, key=lambda r: extract_flat_parts(r.flat_no))


def get_sorted_flat_numbers(residents):
    """
    Get a sorted list of unique flat numbers from residents.
    
    Args:
        residents: List of resident objects with flat_no attribute
        
    Returns:
        List of sorted flat numbers
    """
    # Get unique flat numbers and sort them
    flat_numbers = list(set([r.flat_no for r in residents if r.flat_no]))
    
    def extract_flat_parts(flat_no):
        """Extract numeric and text parts from flat number for proper sorting."""
        if not flat_no:
            return []
        
        # Split into numeric and non-numeric parts
        parts = re.split('([0-9]+)', flat_no)
        # Convert numeric parts to integers for proper sorting
        for i, part in enumerate(parts):
            if part.isdigit():
                parts[i] = int(part)
        return parts
    
    return sorted(flat_numbers, key=lambda x: extract_flat_parts(x))