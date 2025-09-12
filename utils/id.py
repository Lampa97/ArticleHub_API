from fastapi import HTTPException
from bson import ObjectId


def change_id_name(obj: dict | list):
    """
    Recursively change '_id' keys to 'id' in a dictionary or list of dictionaries.
    """
    if isinstance(obj, dict):
        if "_id" in obj:
            obj["id"] = str(obj["_id"])
            obj.pop("_id")
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                change_id_name(value)
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, (dict, list)):
                change_id_name(item)
    return obj


def check_correct_id(id_str: str) -> bool:
    """
    Check if the provided string is a valid MongoDB ObjectId.

    Args:
        id_str (str): The string to check.

    Returns:
        bool: True if the string is a valid ObjectId, False otherwise.
    """
    try:
        ObjectId(id_str)
        return True
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid article ID format") 