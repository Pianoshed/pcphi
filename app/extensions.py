import time
from collections import defaultdict, deque
from functools import wraps
from flask import request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from flask_login import LoginManager

db, migrate, csrf, login_manager = SQLAlchemy(), Migrate(), CSRFProtect(), LoginManager()

class _Hits:
    """Tiny in-memory sliding-window counter (per worker). Swap for Redis if you scale out."""
    def __init__(self): self.d = defaultdict(deque)
    def count(self, key, window):
        q, now = self.d[key], time.monotonic()
        while q and now - q[0] > window: q.popleft()
        if not q: self.d.pop(key, None)
        return len(q)
    def add(self, key): self.d[key].append(time.monotonic())

hits = _Hits()

def limited(limit, window, scope):
    """Rate-limit POST requests per client IP."""
    def deco(f):
        @wraps(f)
        def inner(*a, **kw):
            if request.method == "POST":
                key = f"{scope}:{request.remote_addr}"
                if hits.count(key, window) >= limit: abort(429)
                hits.add(key)
            return f(*a, **kw)
        return inner
    return deco
