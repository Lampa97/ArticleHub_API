def change_id_name(obj: dict | list):
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
