from __future__ import annotations

from pathlib import Path
from .models import RequirementAnalysis, Task, ArchitectureDecision, ValidationResult


class RequirementAgent:
    ambiguity_markers = ("fast", "scalable", "secure", "analytics", "large", "high availability")

    def analyze(self, requirement: str, codebase: str | None = None) -> RequirementAnalysis:
        text = " ".join(requirement.strip().split())
        lower = text.lower()
        scenario = "brownfield" if codebase or any(w in lower for w in ("existing", "refactor", "bug", "fix", "enhance")) else "greenfield"
        ambiguities = [f"'{m}' is not quantified; define a measurable target." for m in self.ambiguity_markers if m in lower]
        if len(text.split()) < 9:
            ambiguities.append("Requirement is brief; non-functional requirements and acceptance criteria are incomplete.")
        is_url = "url" in lower and ("shorten" in lower or "shortener" in lower)
        if is_url:
            return RequirementAnalysis(
                original=text,
                normalized="Create an HTTP service that accepts long URLs, generates collision-resistant short codes, redirects them, persists mappings, and records basic click analytics.",
                intent="Build a scalable URL shortening service with redirect, persistence, and analytics capabilities",
                scenario=scenario,
                ambiguities=ambiguities,
                assumptions=[
                    "Anonymous shortening is allowed for the prototype.",
                    "Basic aggregate click analytics are sufficient; no PII is stored.",
                    "SQLite is a local-demo persistence choice; production can use PostgreSQL/DynamoDB.",
                    "Redirects use HTTP 307 in the prototype.",
                ],
                acceptance_criteria=[
                    "POST /v1/urls creates a short code for a valid HTTP(S) URL.",
                    "GET /{code} redirects to the long URL.",
                    "GET /v1/urls/{code}/analytics returns a click count.",
                    "Invalid URLs and unknown codes return controlled errors.",
                ],
                entities=["URLMapping", "ClickEvent"],
            )
        return RequirementAnalysis(text, text.rstrip(".") + ".", "Implement the requested software change", scenario, ambiguities)


class CodebaseAgent:
    def inspect(self, codebase: str | None) -> dict[str, object]:
        if not codebase:
            return {"files": [], "impacted": [], "notes": ["No existing codebase supplied."]}
        root = Path(codebase)
        if not root.exists():
            return {"files": [], "impacted": [], "notes": [f"Codebase path does not exist: {codebase}"]}
        files = [str(p.relative_to(root)) for p in root.rglob("*") if p.is_file() and ".git" not in p.parts][:100]
        impacted = [f for f in files if any(x in f.lower() for x in ("api", "route", "service", "model", "test", "readme"))][:20]
        return {"files": files, "impacted": impacted, "notes": ["Heuristic impact scan; production should add AST/symbol/dependency analysis."]}


class PlanningAgent:
    def plan(self, analysis: RequirementAnalysis, _: dict[str, object]) -> list[Task]:
        return [
            Task("T1", "Clarify and normalize requirement", "Capture intent, ambiguity, assumptions and acceptance criteria.", owner_agent="requirement-agent"),
            Task("T2", "Reason about codebase impact", "Inspect likely impacted areas for brownfield work.", ["T1"], "codebase-agent"),
            Task("T3", "Design architecture and contracts", "Define APIs, persistence, scaling, security and observability.", ["T1", "T2"], "architecture-agent"),
            Task("T4", "Generate engineering artifacts", "Generate code, API contract, tests and documentation.", ["T3"], "generation-agent"),
            Task("T5", "Validate outputs", "Check completeness, syntax, contract consistency and guardrails.", ["T4"], "validation-agent"),
            Task("T6", "Repair failed validations", "Perform bounded regeneration for correctable failures.", ["T5"], "repair-agent"),
            Task("T7", "Human approval gate", "Require explicit reviewer approval before acceptance.", ["T5", "T6"], "human"),
        ]


class ArchitectureAgent:
    def design(self, analysis: RequirementAnalysis) -> ArchitectureDecision:
        if "url" in analysis.intent.lower() and "short" in analysis.intent.lower():
            return ArchitectureDecision(
                components=["FastAPI API service", "URL service layer", "Repository abstraction", "SQLite demo persistence", "Analytics counter"],
                data_flow=["Create: client -> API -> service -> repository", "Redirect: lookup -> click increment -> redirect", "Analytics: API -> aggregate read"],
                api_contracts=[
                    {"method": "POST", "path": "/v1/urls", "purpose": "Create short URL"},
                    {"method": "GET", "path": "/{code}", "purpose": "Redirect"},
                    {"method": "GET", "path": "/v1/urls/{code}/analytics", "purpose": "Read analytics"},
                ],
                persistence="SQLite locally behind a repository interface; PostgreSQL/DynamoDB for production.",
                scalability=["Stateless API replicas", "Redis/cache for hot redirects", "Async event stream for high-volume analytics"],
                observability=["Structured logs", "latency/error metrics", "redirect/create counters", "run IDs"],
                security=["HTTP(S)-only URL validation", "bounded repair loop", "human approval", "rate limiting recommended"],
                tradeoffs=["SQLite maximizes demo portability", "Synchronous analytics add redirect write work", "Random codes need collision handling"],
            )
        return ArchitectureDecision(["API", "Service", "Repository", "Validation"], ["request -> validation -> service -> storage"], [], "TBD after clarification", ["Stateless services"], ["logs", "metrics", "traces"], ["input validation", "least privilege", "human approval"], ["Domain details remain to be clarified"])


class GenerationAgent:
    def generate(self, analysis: RequirementAnalysis, architecture: ArchitectureDecision) -> dict[str, str]:
        if "url" not in analysis.intent.lower() or "short" not in analysis.intent.lower():
            return {
                "implementation_plan.md": f"# Implementation Plan\n\n{analysis.normalized}\n",
                "api_contract.yaml": "openapi: 3.1.0\ninfo: {title: Generated API, version: 0.1.0}\npaths: {}\n",
                "generated_app.py": "def main():\n    return {'status': 'generated'}\n",
                "test_generated_app.py": "def test_generated():\n    assert True\n",
            }

        service = '''import secrets, sqlite3, string\nfrom urllib.parse import urlparse\n\nALPHABET = string.ascii_letters + string.digits\nclass InvalidURL(ValueError): pass\nclass URLNotFound(KeyError): pass\n\ndef validate_url(url):\n    p = urlparse(url)\n    if p.scheme not in {"http", "https"} or not p.netloc:\n        raise InvalidURL("Only absolute HTTP(S) URLs are accepted")\n    return url\n\nclass URLRepository:\n    def __init__(self, db_path=":memory:"):\n        self.conn = sqlite3.connect(db_path, check_same_thread=False)\n        self.conn.row_factory = sqlite3.Row\n        self.conn.execute("CREATE TABLE IF NOT EXISTS urls(code TEXT PRIMARY KEY,long_url TEXT NOT NULL,clicks INTEGER NOT NULL DEFAULT 0)")\n    def create(self, code, url):\n        self.conn.execute("INSERT INTO urls VALUES(?,?,0)",(code,url)); self.conn.commit()\n    def get(self, code):\n        row=self.conn.execute("SELECT * FROM urls WHERE code=?",(code,)).fetchone()\n        if not row: raise URLNotFound(code)\n        return dict(row)\n    def click(self, code):\n        cur=self.conn.execute("UPDATE urls SET clicks=clicks+1 WHERE code=?",(code,)); self.conn.commit()\n        if cur.rowcount == 0: raise URLNotFound(code)\n\nclass URLShortenerService:\n    def __init__(self, repo, length=7): self.repo,self.length=repo,length\n    def shorten(self, url):\n        validate_url(url)\n        for _ in range(8):\n            code="".join(secrets.choice(ALPHABET) for _ in range(self.length))\n            try:\n                self.repo.create(code,url); return {"code":code,"long_url":url}\n            except sqlite3.IntegrityError: pass\n        raise RuntimeError("Unable to allocate unique code")\n    def resolve(self, code):\n        item=self.repo.get(code); self.repo.click(code); return item["long_url"]\n    def analytics(self, code):\n        item=self.repo.get(code); return {"code":code,"clicks":item["clicks"],"long_url":item["long_url"]}\n'''
        api = '''from fastapi import FastAPI,HTTPException\nfrom fastapi.responses import RedirectResponse\nfrom pydantic import BaseModel\nfrom .url_shortener_service import InvalidURL,URLNotFound,URLRepository,URLShortenerService\napp=FastAPI(title="Generated URL Shortener",version="0.1.0")\nservice=URLShortenerService(URLRepository("url_shortener.db"))\nclass CreateURLRequest(BaseModel): url:str\n@app.get("/health")\ndef health(): return {"status":"ok"}\n@app.post("/v1/urls",status_code=201)\ndef create_url(body:CreateURLRequest):\n    try:\n        r=service.shorten(body.url); return {**r,"short_url":f"/{r['code']}"}\n    except InvalidURL as exc: raise HTTPException(422,str(exc)) from exc\n@app.get("/v1/urls/{code}/analytics")\ndef analytics(code:str):\n    try: return service.analytics(code)\n    except URLNotFound as exc: raise HTTPException(404,"Short code not found") from exc\n@app.get("/{code}")\ndef redirect(code:str):\n    try: return RedirectResponse(service.resolve(code),status_code=307)\n    except URLNotFound as exc: raise HTTPException(404,"Short code not found") from exc\n'''
        tests = '''from fastapi.testclient import TestClient\nfrom generated.url_shortener_api import app\nclient=TestClient(app)\ndef test_create_redirect_analytics():\n    r=client.post("/v1/urls",json={"url":"https://example.com/path"}); assert r.status_code==201\n    code=r.json()["code"]\n    red=client.get(f"/{code}",follow_redirects=False); assert red.status_code==307\n    a=client.get(f"/v1/urls/{code}/analytics"); assert a.status_code==200 and a.json()["clicks"]>=1\ndef test_invalid_url(): assert client.post("/v1/urls",json={"url":"file:///etc/passwd"}).status_code==422\ndef test_missing_code(): assert client.get("/missing-code",follow_redirects=False).status_code==404\n'''
        contract = '''openapi: 3.1.0\ninfo: {title: Generated URL Shortener API, version: 0.1.0}\npaths:\n  /v1/urls:\n    post:\n      summary: Create a short URL\n      responses: {'201': {description: Created}, '422': {description: Invalid URL}}\n  /{code}:\n    get:\n      summary: Redirect to original URL\n      responses: {'307': {description: Redirect}, '404': {description: Unknown code}}\n  /v1/urls/{code}/analytics:\n    get:\n      summary: Get aggregate click analytics\n      responses: {'200': {description: Analytics}, '404': {description: Unknown code}}\n'''
        plan = "# Generated Implementation Plan\n\n" + analysis.normalized + "\n\n## Trade-offs\n" + "\n".join(f"- {x}" for x in architecture.tradeoffs) + "\n\n## Validation\n- Compile Python.\n- Check API contract.\n- Run tests.\n- Require human approval.\n"
        return {"generated/url_shortener_service.py": service, "generated/url_shortener_api.py": api, "generated/__init__.py": "", "generated/tests/test_url_shortener.py": tests, "generated/openapi.yaml": contract, "generated/implementation_plan.md": plan}


class ValidationAgent:
    required = {"generated/url_shortener_service.py", "generated/url_shortener_api.py", "generated/tests/test_url_shortener.py", "generated/openapi.yaml", "generated/implementation_plan.md"}

    def validate(self, analysis: RequirementAnalysis, artifacts: dict[str, str]) -> ValidationResult:
        is_url = "url" in analysis.intent.lower() and "short" in analysis.intent.lower()
        missing = sorted(self.required - set(artifacts)) if is_url else []
        checks = [{"name": "required_artifacts", "passed": not missing, "details": missing or "complete"}]
        syntax_errors=[]
        for path, text in artifacts.items():
            if path.endswith(".py"):
                try: compile(text,path,"exec")
                except SyntaxError as exc: syntax_errors.append(f"{path}: {exc.msg}")
        checks.append({"name":"python_syntax","passed":not syntax_errors,"details":syntax_errors or "all generated Python compiles"})
        forbidden=("subprocess.Popen","os.system(","eval(","exec(")
        unsafe=[p for p,t in artifacts.items() if p.endswith(".py") and any(x in t for x in forbidden)]
        checks.append({"name":"guardrail_scan","passed":not unsafe,"details":unsafe or "no forbidden execution primitives"})
        contract=artifacts.get("generated/openapi.yaml","")
        contract_ok=(not is_url) or all(x in contract for x in ("/v1/urls","/{code}","analytics"))
        checks.append({"name":"contract_consistency","passed":contract_ok,"details":"mandatory paths present" if contract_ok else "API contract incomplete"})
        passed=all(c["passed"] for c in checks)
        risks=["Generated code requires normal engineering review before production.","Deterministic generation demonstrates orchestration; production AI needs model evaluation and sandboxing.","SQLite is a demo choice, not the production high-scale datastore."]
        repairs=[] if passed else ["Regenerate failed artifacts once, then stop for human review."]
        return ValidationResult(passed, checks, risks, repairs)
