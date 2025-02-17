# tools.py
import json

def load_grants(file_path: str = "grants_search.json") -> dict:
    """Load grants from a JSON file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def find_optimal_grants(user_info: dict, grants_data: dict = None) -> dict:
    """
    Find the two grants with the highest budgets that are currently open.
    
    Args:
        user_info (dict): Dictionary containing user information
        grants_data (dict, optional): Dictionary containing grants data. 
                                    If None, loads from default file.
    
    Returns:
        dict: Dictionary containing the two grants with highest budgets as
             'best_grant' and 'second_best_grant'. If only one grant is
             available, 'second_best_grant' will be None.
    """
    # If no grants_data provided, load from file
    if grants_data is None:
        grants_data = load_grants()

    best_grant = None
    second_best_grant = None
    max_budget = 0
    second_max_budget = 0

    for grant in grants_data["grants"]:
        if grant["is_open"]:
            if grant['max_budget'] > max_budget:
                # Current best becomes second best
                second_best_grant = best_grant
                second_max_budget = max_budget
                # New grant becomes best
                best_grant = grant
                max_budget = grant['max_budget']
            elif grant['max_budget'] > second_max_budget:
                # New grant becomes second best
                second_best_grant = grant
                second_max_budget = grant['max_budget']

    return {
        "best_grant": best_grant,
        "second_best_grant": second_best_grant
    }


def get_grant_detail(bdns: str, file_path: str = "grants_detail.json") -> dict:
    """
    Get detailed information about a specific grant by its BDNS number.
    
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            grants_data = json.load(file)
            
        # Search for the grant with matching BDNS
        for grant in grants_data["grants"]:
            if grant.get("official_info", {}).get("bdns") == bdns:
                return grant
                
        return None  # Return None if no matching grant is found
        
    except FileNotFoundError:
        raise FileNotFoundError(f"Grants detail file not found: {file_path}")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Invalid JSON in grants detail file: {file_path}")