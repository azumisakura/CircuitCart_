# auth.py
import hashlib

class User:
    def __init__(self, name, email=None, student_id=None):
        self.name = name
        self.email = email
        self.student_id = student_id
        self.password_hash = None
        # borrow history linked list of dict nodes: {"request": {...}, "next": node}
        self.history_head = None
        self.history_tail = None

class AuthSystem:
    """
    Supports:
      - register(name, email=None, student_id=None, password=None) -> (ok: bool, msg: str)
      - login(identifier, password=None) -> User or None
      - change_username(user: User, new_name: str) -> (ok, msg)
      - change_password(user: User, old_pwd: str, new_pwd: str) -> (ok, msg)
    """
    def __init__(self):
        self.users = []
        self.by_email = {}
        self.by_id = {}

    def _hash(self, pwd):
        return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

    def register(self, name, email=None, student_id=None, password=None):
        if email and email in self.by_email:
            return False, "Email already registered."
        if student_id and student_id in self.by_id:
            return False, "Student ID already registered."
        u = User(name, email=email, student_id=student_id)
        if password:
            u.password_hash = self._hash(password)
        self.users.append(u)
        if email:
            self.by_email[email] = u
        if student_id:
            self.by_id[student_id] = u
        return True, f"Registered {name}."

    def login(self, identifier, password=None):
        # identifier can be email or student_id
        u = self.by_email.get(identifier) or self.by_id.get(identifier)
        if not u:
            return None
        if password is not None:
            if not u.password_hash:
                return None
            if u.password_hash != self._hash(password):
                return None
        return u

    def change_username(self, user, new_name):
        if not user or not new_name.strip():
            return False, "Invalid username."
        user.name = new_name.strip()
        return True, "Username updated."

    def change_password(self, user, old_pwd, new_pwd):
        if not user:
            return False, "No user."
        if not user.password_hash:
            return False, "Password not set. Please set a password via Sign up."
        if user.password_hash != self._hash(old_pwd or ""):
            return False, "Old password incorrect."
        if not new_pwd or len(new_pwd) < 4:
            return False, "New password must be at least 4 characters."
        user.password_hash = self._hash(new_pwd)
        return True, "Password changed."
