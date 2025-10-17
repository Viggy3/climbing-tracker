def individual_serial(tracker) -> dict:
    return{
        "id": str(tracker["_id"]),
        "name": tracker["name"],
        "description": tracker["description"],
        "date": tracker["date"],
        "attempts": tracker["attempts"],
        "grade": tracker["grade"],
        "complete": tracker["complete"]
    }

def list_serial(tracker_list) -> list:
    return [individual_serial(tracker) for tracker in tracker_list]