# requests.py
import datetime

def reason_to_priority(reason):
    mapping = {"emergency": 0, "urgent": 1, "normal": 2, "low": 3}
    return mapping.get(reason, 2)

def make_request(user, items, reason="normal", id_deposit=True):
    return {
        "user": {"name": getattr(user, "name", str(user)), "student_id": getattr(user, "student_id", None)},
        "items": list(items),
        "reason": reason,
        "id_deposit": bool(id_deposit),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

def append_history(user, req):
    node = {"request": req, "next": None}
    if getattr(user, "history_head", None) is None:
        user.history_head = node
        user.history_tail = node
    else:
        user.history_tail["next"] = node
        user.history_tail = node
    return True
