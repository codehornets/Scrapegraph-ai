import json


def set_default(obj):
    # Handle sets by converting them to lists
    if isinstance(obj, set):
        return list(obj)

    # Handle non-serializable objects by returning their string representation
    try:
        return str(obj)
    except Exception:
        raise TypeError(f"Object of type {type(obj)} is not serializable")


def die(data):
    try:
        # Attempt to serialize the data using custom set_default
        print(
            f"DEBUG: {json.dumps(data, indent=4, ensure_ascii=False, default=set_default)}"
        )
    except TypeError as e:
        # Catch and display a helpful message if there's a serialization error
        print(f"DEBUG: Serialization error: {e}")

    exit()
