# app_controller.py
import os
import json
from datetime import datetime

from auth import AuthSystem
from catalog import build_tree_and_items, init_availability
from dsa_structures import Stack, Queue, PriorityQueue, DoublyLinkedList
from requests import make_request, reason_to_priority, append_history


# ================================
# Helper functions
# ================================

def _safe_len(ds):
    """Safely get length of any DSA structure"""
    try:
        return len(ds)
    except Exception:
        return 0


# ================================
# CART (DOUBLY LINKED LIST)
# ================================

class Cart:
    """
    Cart implementation using Doubly Linked List
    - Allows dynamic insert and delete
    - Maintains order of selected items
    """

    def __init__(self, capacity=10):
        self.capacity = capacity
        self.items_list = DoublyLinkedList()

    def is_full(self):
        return len(self.items_list) >= self.capacity

    def add(self, item):
        if self.is_full():
            return False, "Cart full (10 max)."
        self.items_list.append(item)     # DLL append
        return True, f"Added '{item}'."

    def remove(self, item):
        removed = self.items_list.remove_first_value(item)  # DLL delete
        return removed, ("Removed." if removed else "Item not found.")

    def items(self):
        return self.items_list.to_list()  # DLL traversal


# ================================
# MAIN CONTROLLER
# ================================

class CircuitLendController:
    """
    Central controller that explicitly uses:
    - Queue for normal borrow requests (FIFO)
    - Priority Queue for prioritized requests
    - Stack for undo operations (LIFO)
    - Doubly Linked List for cart management
    """

    def __init__(self):
        # Catalog & availability
        self.tree_root, self.categories, self.all_items = build_tree_and_items()
        self.availability = init_availability(self.all_items)

        # Authentication
        self.auth = AuthSystem()
        self.current_user = None

        # DSA Structures
        self.cart = Cart()                 # Doubly Linked List
        self.pending_q = Queue()           # Queue (FIFO)
        self.priority_q = PriorityQueue()  # Priority Queue
        self.undo_stack = Stack()           # Stack (LIFO)

        # Settings
        self.settings_file = os.path.join(os.path.dirname(__file__), "user_settings.json")
        self.settings = self._load_settings()

        # Reminders
        self.reminders = self.settings.get("reminders", [])

        # Messages (optional feature)
        self.messages = []

        # Seed demo users
        self.auth.register("Theresa", email="theresa@school.edu",
                           student_id="2026-00001", password="test123")
        self.auth.register("Juan", student_id="2026-12345", password="pass")

    # ================================
    # SETTINGS
    # ================================

    def _load_settings(self):
        try:
            if os.path.isfile(self.settings_file):
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {
            "email": "",
            "name": "",
            "student_id": "",
            "theme": "pastel_red",
            "font_size": "medium",
            "reminder_time": "1_day",
            "reminders": []
        }

    def _persist(self):
        self.settings["reminders"] = self.reminders
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception:
            return False

    def save_settings(self, settings_dict):
        self.settings.update(settings_dict or {})
        return self._persist()

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value
        return self._persist()

    # ================================
    # AUTHENTICATION
    # ================================

    def login(self, identifier, password=None):
        res = self.auth.login(identifier, password)
        if res:
            self.current_user = res
            self.settings["email"] = getattr(res, "email", "")
            self.settings["name"] = getattr(res, "name", "")
            self.settings["student_id"] = getattr(res, "student_id", "")
            self._persist()
            return True, f"Welcome, {self.current_user.name}!"
        return False, "Login failed."

    def logout(self):
        self.current_user = None
        return True, "Logged out."

    def register(self, name, email=None, student_id=None, password=None):
        ok, msg = self.auth.register(name, email=email,
                                     student_id=student_id, password=password)
        if ok:
            self.settings["name"] = name
            if email:
                self.settings["email"] = email
            if student_id:
                self.settings["student_id"] = student_id
            self._persist()
        return ok, msg

    def change_username(self, new_name):
        if not self.current_user:
            return False, "Please log in first."
        ok, msg = self.auth.change_username(self.current_user, new_name)
        if ok:
            self.settings["name"] = new_name
            self._persist()
        return ok, msg

    def change_password(self, old_pwd, new_pwd):
        if not self.current_user:
            return False, "Please log in first."
        return self.auth.change_password(self.current_user, old_pwd, new_pwd)

    # ================================
    # CATALOG
    # ================================

    def search_items(self, q):
        from catalog import array_search
        return array_search(self.all_items, q)

    def sort_items(self, by="name"):
        from catalog import array_sort
        return array_sort(self.all_items, by=by, availability=self.availability)

    def availability_of(self, item):
        return self.availability.get(item, 0)

    # ================================
    # CART OPERATIONS (DLL)
    # ================================

    def add_to_cart(self, item):
        if item not in self.availability:
            return False, "Item not found."
        if self.availability[item] <= 0:
            return False, "Item unavailable."
        return self.cart.add(item)

    def remove_from_cart(self, item):
        return self.cart.remove(item)

    # ================================
    # BORROW REQUESTS (QUEUE & PQ)
    # ================================

    def submit_borrow(self, reason="normal", prioritize=False,
                      id_deposit=True, borrow_date=None, return_date=None):

        if not self.current_user:
            return False, "Please log in first."

        items = self.cart.items()
        if not items:
            return False, "Cart is empty."

        # Deduct stock
        for item in items:
            if self.availability[item] <= 0:
                return False, f"Out of stock: {item}"
        for item in items:
            self.availability[item] -= 1

        request = make_request(
            self.current_user, items,
            reason=reason, id_deposit=id_deposit
        )

        # PRIORITY QUEUE vs NORMAL QUEUE
        if prioritize:
            priority = reason_to_priority(reason)
            self.priority_q.push(priority, request)
        else:
            self.pending_q.enqueue(request)

        append_history(self.current_user, request)

        # STACK PUSH (UNDO)
        self.undo_stack.push({
            "type": "CANCEL_BORROW",
            "payload": request
        })

        # Save reminder
        if borrow_date and return_date:
            self.reminders.append({
                "user": self.current_user.name,
                "items": items,
                "borrow_date": borrow_date,
                "return_date": return_date
            })
            self._persist()

        self.cart = Cart()
        return True, (
            f"Submitted ({reason}). "
            f"Pending: {_safe_len(self.pending_q)} | "
            f"Priority: {_safe_len(self.priority_q)}"
        )

    # ================================
    # HISTORY & RECEIPTS
    # ================================

    def list_borrow_history(self):
        if not self.current_user:
            return []
        history = []
        node = self.current_user.history_head
        while node:
            history.append(node.get("request", {}))
            node = node.get("next")
        return history

    def list_reminders(self):
        return list(self.reminders)

    def generate_receipt(self, items, borrow_date, return_date):
        if not self.current_user:
            return None
        return {
            "borrower_name": self.current_user.name,
            "student_id": self.current_user.student_id,
            "email": self.current_user.email,
            "items": list(items),
            "borrow_date": borrow_date,
            "return_date": return_date,
            "issued_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

    # ================================
    # RETURNS & UNDO (STACK)
    # ================================

    def return_items(self, items):
        if not self.current_user:
            return False, "Please log in first."

        for item in items:
            self.availability[item] += 1

        self.undo_stack.push({
            "type": "REVERT_RETURN",
            "payload": items
        })

        return True, f"Returned {len(items)} item(s)."

    def clear_history(self):
        if not self.current_user:
            return False, "Please log in first."
        self.current_user.history_head = None
        self.current_user.history_tail = None
        return True, "Borrow history cleared."

    def undo(self):
        action = self.undo_stack.pop()
        if not action:
            return False, "Nothing to undo."

        if action["type"] == "CANCEL_BORROW":
            for item in action["payload"].get("items", []):
                self.availability[item] += 1
            return True, "Undo successful: borrow cancelled."

        if action["type"] == "REVERT_RETURN":
            for item in action["payload"]:
                self.availability[item] = max(0, self.availability[item] - 1)
            return True, "Undo successful: return reverted."

        return False, "Unknown undo action."
