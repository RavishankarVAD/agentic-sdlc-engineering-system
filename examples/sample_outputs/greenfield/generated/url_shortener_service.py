import secrets, sqlite3, string
from urllib.parse import urlparse

ALPHABET = string.ascii_letters + string.digits
class InvalidURL(ValueError): pass
class URLNotFound(KeyError): pass

def validate_url(url):
    p = urlparse(url)
    if p.scheme not in {"http", "https"} or not p.netloc:
        raise InvalidURL("Only absolute HTTP(S) URLs are accepted")
    return url

class URLRepository:
    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("CREATE TABLE IF NOT EXISTS urls(code TEXT PRIMARY KEY,long_url TEXT NOT NULL,clicks INTEGER NOT NULL DEFAULT 0)")
    def create(self, code, url):
        self.conn.execute("INSERT INTO urls VALUES(?,?,0)",(code,url)); self.conn.commit()
    def get(self, code):
        row=self.conn.execute("SELECT * FROM urls WHERE code=?",(code,)).fetchone()
        if not row: raise URLNotFound(code)
        return dict(row)
    def click(self, code):
        cur=self.conn.execute("UPDATE urls SET clicks=clicks+1 WHERE code=?",(code,)); self.conn.commit()
        if cur.rowcount == 0: raise URLNotFound(code)

class URLShortenerService:
    def __init__(self, repo, length=7): self.repo,self.length=repo,length
    def shorten(self, url):
        validate_url(url)
        for _ in range(8):
            code="".join(secrets.choice(ALPHABET) for _ in range(self.length))
            try:
                self.repo.create(code,url); return {"code":code,"long_url":url}
            except sqlite3.IntegrityError: pass
        raise RuntimeError("Unable to allocate unique code")
    def resolve(self, code):
        item=self.repo.get(code); self.repo.click(code); return item["long_url"]
    def analytics(self, code):
        item=self.repo.get(code); return {"code":code,"clicks":item["clicks"],"long_url":item["long_url"]}
