#!/usr/bin/env python3
"""Alfred knowledge-graph generator.

Scans the repository (Python, TypeScript/TSX, Rust, SQL schema, tests),
constructs a static symbol graph, and emits an Obsidian-compatible vault
under docs/obsidian/99 - Generated/. Never touches curated notes.

Usage:
    py tools/docs/generate_knowledge_graph.py            # regenerate
    py tools/docs/generate_knowledge_graph.py --check    # exit 1 if stale
    py tools/docs/generate_knowledge_graph.py --skip-ts  # python/rust only

Deterministic: identical source yields byte-identical output (sorted
symbols, sorted links, no timestamps).
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = ROOT / "tools" / "docs" / "docs_config.toml"
GENERATED_MARKER = "> Auto-generated from source code. Do not manually edit this file; update source code or generator instead."

# ────────────────────────────────────────────────────────────────
# Critical-path + security symbol sets (curated, code-informed)
# ────────────────────────────────────────────────────────────────
CRITICAL_PATH = {
    "backend.app.main.sync_account",
    "backend.app.main._analysis_worker",
    "backend.app.main._backfill_worker",
    "backend.app.main.lifespan",
    "backend.app.mail.providers.gmail.GmailProvider.sync_messages",
    "backend.app.mail.providers.gmail.GmailProvider.backfill_messages",
    "backend.app.ai.ollama_client.OllamaClient.generate",
    "backend.app.ai.service.AIService.analyze_email",
    "backend.app.services.task_derivation.derive_tasks",
    "backend.app.db.database.connect",
    "backend.app.db.repositories.Repository.upsert_email",
    "backend.app.db.repositories.Repository.next_job",
}
SECURITY_SYMBOLS = {
    "backend.app.main.gmail_callback",
    "backend.app.main.connect_gmail",
    "backend.app.db.secure_store",
    "backend.app.mail.providers.gmail",
    "backend.app.mail.normalizer",
    "backend.app.ai.service",
}


def load_config() -> dict:
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def tag_list(layer: str, kind: str, qualified: str) -> list[str]:
    tags = [kind, layer]
    if qualified in CRITICAL_PATH:
        tags.append("critical-path")
    if qualified in SECURITY_SYMBOLS or layer in ("gmail",):
        pass  # per-symbol security tags applied by callers
    return tags


# ════════════════════════════════════════════════════════════════
# PYTHON ANALYSIS
# ════════════════════════════════════════════════════════════════

class PySymbol:
    def __init__(self, kind: str, name: str, qualified: str, source: str,
                 line: int, doc: str = "", sig: str = "", decorators: list[str] | None = None,
                 async_: bool = False, params: list[tuple[str, str | None]] | None = None,
                 returns: str | None = None, bases: list[str] | None = None,
                 constants: list[str] | None = None):
        self.kind = kind
        self.name = name
        self.qualified = qualified
        self.source = source
        self.line = line
        self.doc = doc
        self.sig = sig
        self.decorators = decorators or []
        self.async_ = async_
        self.params = params or []
        self.returns = returns
        self.bases = bases or []
        self.constants = constants or []
        self.calls: list[tuple[str, str]] = []      # (qualified_target, relation)
        self.called_by: list[str] = []
        self.tables_read: set[str] = set()
        self.tables_write: set[str] = set()
        self.is_test = False
        self.route: tuple[str, str] | None = None   # (method, path)

    @property
    def layer(self) -> str:
        if self.source.startswith("backend/tests") or self.source.startswith("tests"):
            return "test"
        if "/ai/" in self.source:
            return "ai"
        if "/mail/" in self.source:
            return "gmail"
        if "/db/" in self.source:
            return "database"
        return "backend"


def _qname(prefix: str, name: str) -> str:
    return f"{prefix}.{name}" if prefix else name


def _anno(node) -> str | None:
    try:
        return ast.unparse(node)
    except Exception:
        return None


def _doc(node) -> str:
    return ast.get_docstring(node, clean=False) or ""


def _sig(args: ast.arguments) -> str:
    parts = []
    pos = args.posonlyargs + args.args
    defaults = [None] * (len(pos) - len(args.defaults)) + list(args.defaults)
    for a, d in zip(pos, defaults):
        s = a.arg
        if a.annotation is not None:
            s += f": {_anno(a.annotation)}"
        if d is not None:
            s += f" = {_anno(d)}"
        parts.append(s)
    if args.vararg:
        parts.append(f"*{args.vararg.arg}")
    for a, d in zip(args.kwonlyargs, args.kw_defaults):
        s = a.arg
        if a.annotation:
            s += f": {_anno(a.annotation)}"
        if d is not None:
            s += f" = {_anno(d)}"
        parts.append(s)
    if args.kwarg:
        parts.append(f"**{args.kwarg.arg}")
    return ", ".join(parts)


class CallCollector(ast.NodeVisitor):
    """Resolve simple call targets (Name / dotted Attribute on locals+imports)."""

    def __init__(self, module_scope: set[str], locals_: set[str]):
        self.module_scope = module_scope
        self.locals_ = locals_
        self.calls: list[str] = []

    def visit_Call(self, node):
        target = node.func
        if isinstance(target, ast.Name):
            if target.id in self.locals_ or target.id in self.module_scope:
                self.calls.append(target.id)
        elif isinstance(target, ast.Attribute):
            parts = []
            cur = target
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
                base = cur.id
                full = ".".join(reversed(parts))
                if base in self.locals_ or base in self.module_scope:
                    self.calls.append(full)
        self.generic_visit(node)


def _resolve_call_target(call: str, locals_map: dict[str, str], imports: dict[str, str],
                         module: str) -> str | None:
    """Map a syntactic call to a best-effort qualified symbol."""
    if call in locals_map:
        return locals_map[call]
    parts = call.split(".")
    first = parts[0]
    if first in locals_map:
        return locals_map[first] + "." + ".".join(parts[1:])
    if first in imports:
        target_mod = imports[first]
        if len(parts) == 1:
            # from X import y  → imports[y] is already the qualified symbol
            return target_mod
        # from X import y  → y.z resolves as X.y.z when X is a module
        return target_mod + "." + ".".join(parts[1:])
    if first == "repo":
        return "backend.app.db.repositories.Repository." + ".".join(parts[1:])
    if first == "ai":
        return "backend.app.ai.service.AIService." + ".".join(parts[1:])
    if first == "self":
        return None  # handled via locals_map (methods of own class)
    return None


TABLE_NAMES = set()
TABLE_COLUMNS: dict[str, list[str]] = {}
TABLE_PKS: dict[str, list[str]] = {}
TABLE_SQL: dict[str, str] = {}
INDEX_SQL: str = ""

SCHEMA_RE = re.compile(
    r"CREATE\s+(?:VIRTUAL\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([`\"\[]?[\w]+[`\"\]]?)"
    r"(?:\s+USING\s+\w+)?\s*\((.*?)\)\s*;",
    re.DOTALL | re.IGNORECASE,
)
COL_RE = re.compile(r"^\s*([`\"\[]?[\w]+[`\"\]]?)\s+([^,()]+?)(?:,|$)", re.MULTILINE)


def parse_schema(path: Path):
    global INDEX_SQL
    text = path.read_text(encoding="utf-8")
    for var in ("SCHEMA", "FTS_SCHEMA"):
        m = re.search(var + r"\s*=\s*(\"\"\"|''')(.*?)\1", text, re.DOTALL)
        if m:
            schema = m.group(2)
            for tm in SCHEMA_RE.finditer(schema):
                name = tm.group(1).strip('`"[]')
                body = tm.group(2)
                TABLE_SQL[name] = body
                cols, pks = [], []
                for cm in COL_RE.finditer(body):
                    col = cm.group(1).strip('`"[]')
                    if not col or col.upper() in ("PRIMARY", "FOREIGN", "UNIQUE", "CONSTRAINT", "CHECK"):
                        continue
                    if col == "PRIMARY" and "KEY" in cm.group(2).upper():
                        continue
                    cols.append(col)
                    if re.search(r"PRIMARY\s+KEY", cm.group(2), re.I):
                        pks.append(col)
                TABLE_NAMES.add(name)
                TABLE_COLUMNS[name] = cols
                TABLE_PKS[name] = pks
    im = re.search(r"INDEXES\s*=\s*(\"\"\"|''')(.*?)\1", text, re.DOTALL)
    if im:
        INDEX_SQL = im.group(2)


def _tables_from_sql(sql: str) -> tuple[set[str], set[str]]:
    reads, writes = set(), set()
    for t in TABLE_NAMES:
        if re.search(rf"\b{t}\b", sql, re.I):
            if re.match(r"^\s*(INSERT|UPDATE|DELETE|CREATE|ALTER)", sql, re.I):
                writes.add(t)
            else:
                reads.add(t)
    return reads, writes


def analyze_python(paths: list[Path]) -> dict:
    modules: dict[str, dict] = {}
    symbols: dict[str, PySymbol] = {}

    for path in sorted(paths):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel.startswith("backend/"):
            module = rel[:-3].replace("/", ".").replace("\\", ".")
        else:
            module = rel[:-3].replace("/", ".").replace("\\", ".")
        if module.endswith(".__init__"):
            module = module[:-9]

        module_symbols = set()
        imports: dict[str, str] = {}
        module_constants: list[str] = []

        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for a in node.names:
                        imports[a.asname or a.name.split(".")[0]] = a.name
                elif node.module:
                    base = node.module.replace(".", "")
                    for a in node.names:
                        if a.name == "*":
                            continue
                        imports[a.asname or a.name] = (
                            node.module if node.level == 0
                            else _resolve_relative(module, node.level, node.module)
                        ) + (f".{a.name}" if node.level > 0 and a.name else f".{a.name}")
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                pass  # handled below
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):
                names = []
                targets = node.targets if isinstance(node, ast.Assign) else [node.target]
                for t in targets:
                    if isinstance(t, ast.Name) and t.id.isupper():
                        names.append(t.id)
                module_constants.extend(names)
                for n in names:
                    module_symbols.add(n)

        # Top-level defs
        def walk_defs(body, prefix):
            for node in body:
                if isinstance(node, ast.ClassDef):
                    yield from walk_class(node, prefix)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    yield from walk_func(node, prefix)

        def walk_class(node, prefix):
            q = _qname(prefix, node.name)
            bases = [_anno(b) for b in node.bases] if node.bases else []
            sym = PySymbol(
                "class", node.name, q, rel, node.lineno,
                doc=_doc(node), bases=bases,
                decorators=[_anno(d) for d in node.decorator_list],
            )
            class_locals = {m.name: f"{q}.{m.name}" for m in node.body
                            if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef))}
            cls_module = module
            yield sym
            for m in node.body:
                if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    yield from walk_func(m, q, class_locals, cls_module)
                elif isinstance(m, ast.ClassDef):
                    yield from walk_class(m, q)

        def walk_func(node, prefix, class_locals=None, cls_module=None):
            class_locals = class_locals or {}
            q = _qname(prefix, node.name)
            args_s = _sig(node.args)
            ret = _anno(node.returns) if node.returns else None
            params = []
            for a in node.args.args + node.args.kwonlyargs:
                params.append((a.arg, _anno(a.annotation) if a.annotation else None))
            sym = PySymbol(
                "function" if not isinstance(node, ast.AsyncFunctionDef) else "function",
                node.name, q, rel, node.lineno,
                doc=_doc(node), sig=f"({args_s})" + (f" -> {ret}" if ret else ""),
                decorators=[_anno(d) for d in node.decorator_list],
                async_=isinstance(node, ast.AsyncFunctionDef),
                params=params, returns=ret,
            )
            # FastAPI route detection
            for d in node.decorator_list:
                if isinstance(d, ast.Call) and isinstance(d.func, ast.Attribute):
                    base = d.func.value
                    base_name = base.id if isinstance(base, ast.Name) else ""
                    if base_name == "app" and d.func.attr in ("get", "post", "delete", "put", "patch") and d.args:
                        try:
                            sym.route = (d.func.attr.upper(), ast.literal_eval(d.args[0]))
                        except Exception:
                            pass
            sym.is_test = node.name.startswith("test_") and ("tests" in rel)
            # calls
            local_names = {a.arg for a in node.args.args}
            collector = CallCollector(set(imports.keys()) | {n for n in module_symbols}, local_names)
            for stmt in node.body:
                collector.visit(stmt)
            seen = set()
            for call in collector.calls:
                target = _resolve_call_target(call, class_locals or {}, imports, module)
                if target and target not in seen:
                    seen.add(target)
                    sym.calls.append((target, "calls"))
            # SQL table usage
            sql_hits = re.findall(r'["\']((?:SELECT|INSERT|UPDATE|DELETE|CREATE)[^"\']*)["\']', ast.unparse(node) if hasattr(ast, "unparse") else "")
            for sql in sql_hits:
                r_, w_ = _tables_from_sql(sql)
                sym.tables_read |= r_
                sym.tables_write |= w_
            yield sym
            # nested functions
            for stmt in node.body:
                if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    nested_locals = {m.name: f"{q}.{m.name}" for m in
                                     [x for x in node.body if isinstance(x, (ast.FunctionDef, ast.AsyncFunctionDef))]}
                    yield from walk_func(stmt, q, nested_locals, cls_module or module)

        for sym in walk_defs(tree.body, module):
            symbols[sym.qualified] = sym
            module_symbols.add(sym.name)

        modules[module] = {
            "source": rel,
            "imports": dict(sorted(imports.items())),
            "constants": sorted(set(module_constants)),
        }

    # resolve call edges
    for q, sym in symbols.items():
        for target, relation in list(sym.calls):
            if target in symbols:
                symbols[target].called_by.append(q)
                sym.calls[sym.calls.index((target, relation))] = (target, "calls")
            else:
                # keep as inferred link (may resolve to TS symbol later)
                sym.calls[sym.calls.index((target, relation))] = (target, "calls-inferred")

    # Repository method -> tables map
    repo_method_tables: dict[str, tuple[set, set]] = {}
    for q, sym in symbols.items():
        if sym.qualified.startswith("backend.app.db.repositories.Repository.") and sym.kind == "function":
            repo_method_tables[q] = (sym.tables_read, sym.tables_write)
    for q, sym in symbols.items():
        for target, _ in sym.calls:
            if target in repo_method_tables:
                r_, w_ = repo_method_tables[target]
                sym.tables_read |= r_
                sym.tables_write |= w_

    return {"modules": modules, "symbols": symbols}


def _resolve_relative(module: str, level: int, target: str) -> str:
    parts = module.split(".")
    if level >= 1:
        parts = parts[:-level]
    return ".".join(parts + [target])


# ════════════════════════════════════════════════════════════════
# RUST MINI-SCANNER (heuristic — small Tauri crate)
# ════════════════════════════════════════════════════════════════
def analyze_rust(paths: list[Path]) -> dict:
    symbols = {}
    modules = {}
    for path in sorted(paths):
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()
        module = rel[:-3].replace("/", ".")
        fns = re.findall(
            r"((?:pub\s+|async\s+)*fn\s+([a-zA-Z_][\w]*)\s*\(([^)]*)\)(?:\s*->\s*([^{\n]+))?)",
            text,
        )
        module_fns = []
        for sig, name, params, ret in fns:
            q = f"{module}.{name}"
            sym = PySymbol(
                "function", name, q, rel, text[: text.find(f"fn {name}")].count("\n") + 1,
                doc="", sig=f"fn {name}({params})" + (f" -> {ret.strip()}" if ret else ""),
                params=[(p.strip().split(":")[0].strip(), p.strip().split(":")[-1].strip() if ":" in p else None)
                        for p in params.split(",") if p.strip()],
                returns=ret.strip() if ret else None,
            )
            if "#[tauri::command]" in text:
                sym.decorators.append("tauri::command")
            symbols[q] = sym
            module_fns.append(name)
        modules[module] = {"source": rel, "functions": module_fns}
    return {"modules": modules, "symbols": symbols}


# ════════════════════════════════════════════════════════════════
# NOTE EMITTERS
# ════════════════════════════════════════════════════════════════

def esc(text: str) -> str:
    return text.replace("\n", " ").strip()


def purpose_of(sym: PySymbol) -> str:
    doc = sym.doc.strip()
    if doc:
        first = doc.split("\n\n")[0].split("\n")[0].strip()
        if first:
            return first
    return f"Purpose inferred from usage: `{sym.name}` in `{sym.source}`."


def _write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")


def emit_symbol_notes(symbols: dict[str, PySymbol], out: Path) -> dict:
    """Emit Modules/ Classes/ Functions/ Endpoints/ Tests notes."""
    counts = {}
    resolved_targets = set(symbols.keys())
    for q, sym in sorted(symbols.items()):
        layer = sym.layer
        if sym.is_test:
            folder = out / "Tests"
            fname = f"{q}.md"
        elif sym.kind == "class":
            folder = out / "Classes"
            fname = f"{q}.md"
        else:
            # Routed functions ALSO get a plain function note (curated
            # docs link handlers by qualified name); the endpoint note
            # remains the route documentation.
            folder = out / "Functions"
            fname = f"{q}.md"

        tags = [layer, sym.kind]
        if sym.is_test:
            tags.append("test")
        if q in CRITICAL_PATH:
            tags.append("critical-path")
        if sym.route:
            tags.append("endpoint")
        if layer == "test":
            layer_meta = "test"
        else:
            layer_meta = layer

        lines = [
            "---",
            f"type: {sym.kind}",
            "generated: true",
            f"language: {'rust' if sym.source.endswith('.rs') else 'python'}",
            f"layer: {layer_meta}",
            f"module: {q.rsplit('.', 1)[0] if '.' in q else q}",
            f"qualified_name: {q}",
            f"source: {sym.source}",
            f"line: {sym.line}",
            "status: active",
            f"tags: [{', '.join(tags)}]",
            "---",
            "",
            f"# {sym.name}",
            "",
            GENERATED_MARKER,
            "",
            "## Purpose",
            "",
            purpose_of(sym),
            "",
        ]
        if sym.route:
            method, path = sym.route
            lines += ["## Route", "", f"`{method} {path}`", ""]
            # Emit a separate endpoint note with the route-friendly filename
            ep_folder = out / "API Endpoints"
            ep_name = f"{method} -{path.replace('/', '-')}.md"
            ep_name = ep_name.replace("{{", "{").replace("}}", "}")
            ep_lines = [
                "---",
                "type: endpoint",
                "generated: true",
                "layer: backend",
                f"qualified_name: {q}",
                f"source: {sym.source}",
                f"line: {sym.line}",
                "status: active",
                f"tags: [{', '.join(tags + ['endpoint'])}]",
                "---",
                "",
                f"# {method} {path}",
                "",
                GENERATED_MARKER,
                "",
                "## Purpose",
                "",
                purpose_of(sym),
                "",
                "## Handler",
                "",
                f"[[{q}|{sym.name}]]",
                "",
                "## Location",
                "",
                f"`{sym.source}:{sym.line}`",
                "",
            ]
            if sym.params:
                ep_lines += ["## Parameters", ""]
                for pname, ptype in sym.params:
                    ep_lines.append(f"- `{pname}`" + (f" (`{ptype}`)" if ptype else ""))
                ep_lines.append("")
            if sym.tables_read:
                ep_lines += ["## Reads", ""]
                ep_lines += [f"- [[table_{t}]]" for t in sorted(sym.tables_read)]
                ep_lines.append("")
            if sym.tables_write:
                ep_lines += ["## Writes", ""]
                ep_lines += [f"- [[table_{t}]]" for t in sorted(sym.tables_write)]
                ep_lines.append("")
            if "gmail" in path or "oauth" in q.lower():
                ep_lines += ["## Security", "", "See [[OAuth Security]] and [[Token Security]].", ""]
            _write(ep_folder / ep_name, "\n".join(ep_lines))
        lines += [f"## Location", "", f"`{sym.source}:{sym.line}`", ""]
        if sym.sig:
            lines += ["## Signature", "", "```python" if not sym.source.endswith(".rs") else "```rust", sym.sig, "```", ""]
        if sym.params:
            lines += ["## Parameters", ""]
            for pname, ptype in sym.params:
                lines.append(f"- `{pname}`" + (f" (`{ptype}`)" if ptype else ""))
            lines.append("")
        if sym.returns:
            lines += ["## Returns", "", f"`{sym.returns}`", ""]
        if sym.bases:
            lines += ["## Bases", ""]
            lines += [f"- `{b}`" for b in sym.bases]
            lines.append("")
        if sym.calls:
            lines += ["## Calls", ""]
            for target, rel in sorted(set(sym.calls)):
                name = target.split(".")[-1]
                if target in resolved_targets:
                    lines.append(f"- [[{target}|{name}]] ({rel})")
                else:
                    lines.append(f"- `{name}` (`{target}`, {rel})")
            lines.append("")
        if sym.called_by:
            lines += ["## Called By", ""]
            for caller in sorted(set(sym.called_by)):
                name = caller.split(".")[-1]
                lines.append(f"- [[{caller}|{name}]]")
            lines.append("")
        if sym.tables_read:
            lines += ["## Reads", ""]
            lines += [f"- [[table_{t}]]" for t in sorted(sym.tables_read)]
            lines.append("")
        if sym.tables_write:
            lines += ["## Writes", ""]
            lines += [f"- [[table_{t}]]" for t in sorted(sym.tables_write)]
            lines.append("")
        lines += ["## Side Effects", ""]
        side = []
        if sym.async_:
            side.append("async I/O")
        if sym.tables_read or sym.tables_write:
            side.append("SQLite")
        if any("client." in c for c, _ in sym.calls) or "httpx" in sym.source:
            side.append("network (HTTP)")
        if q in SECURITY_SYMBOLS or "secure_store" in q or "token" in q.lower():
            side.append("handles credentials/tokens — see [[Token Security]]")
        lines.append("- " + "; ".join(side) if side else "- none statically observed")
        lines.append("")
        if q in SECURITY_SYMBOLS or sym.route and "gmail" in (sym.route[1] or ""):
            lines += ["## Security", "", "See [[OAuth Security]] and [[Token Security]].", ""]
        _write(folder / fname, "\n".join(lines))

        kind_key = "tests" if sym.is_test else (
            "endpoints" if sym.route else ("classes" if sym.kind == "class" else "functions"))
        counts[kind_key] = counts.get(kind_key, 0) + 1
        if sym.route:
            counts["functions"] = counts.get("functions", 0) + 1
    return counts


def emit_module_notes(modules: dict[str, dict], symbols: dict[str, PySymbol], out: Path) -> int:
    n = 0
    for mod, meta in sorted(modules.items()):
        mod_syms = [s for s in symbols.values() if s.qualified.startswith(mod + ".")]
        fname = f"{mod}.md"
        tags = ["module"]
        layer = "backend" if mod.startswith("backend") else "test"
        lines = [
            "---",
            "type: module",
            "generated: true",
            "language: python",
            f"layer: {layer}",
            f"qualified_name: {mod}",
            f"source: {meta['source']}",
            "status: active",
            f"tags: [{', '.join(tags + [layer])}]",
            "---",
            "",
            f"# {mod}",
            "",
            GENERATED_MARKER,
            "",
            "## Source",
            "",
            f"`{meta['source']}`",
            "",
        ]
        if meta.get("imports"):
            lines += ["## Imports", ""]
            lines += [f"- `{k}` ← `{v}`" for k, v in sorted(meta["imports"].items())]
            lines.append("")
        classes = [s for s in mod_syms if s.kind == "class"]
        funcs = [s for s in mod_syms if s.kind == "function" and not s.is_test]
        tests = [s for s in mod_syms if s.is_test]
        if classes:
            lines += ["## Classes", ""]
            for s in sorted(classes, key=lambda x: x.qualified):
                lines.append(f"- [[{s.qualified}|{s.name}]]")
            lines.append("")
        if funcs:
            lines += ["## Functions", ""]
            for s in sorted(funcs, key=lambda x: x.qualified):
                lines.append(f"- [[{s.qualified}|{s.name}]]")
            lines.append("")
        if tests:
            lines += ["## Tests", ""]
            for s in sorted(tests, key=lambda x: x.qualified):
                lines.append(f"- [[{s.qualified}|{s.name}]]")
            lines.append("")
        if meta.get("constants"):
            lines += ["## Constants", ""]
            lines += [f"- `{c}`" for c in sorted(meta["constants"])]
            lines.append("")
        _write(out / "Modules" / fname, "\n".join(lines))
        n += 1
    return n


def emit_table_notes(out: Path) -> int:
    n = 0
    for t in sorted(TABLE_NAMES):
        cols = TABLE_COLUMNS.get(t, [])
        pks = TABLE_PKS.get(t, [])
        lines = [
            "---",
            "type: database-table",
            "generated: true",
            "layer: database",
            f"qualified_name: table_{t}",
            "source: backend/app/db/database.py",
            "status: active",
            "tags: [database, database-table]",
            "---",
            "",
            f"# {t}",
            "",
            GENERATED_MARKER,
            "",
            "## Purpose",
            "",
            f"SQLite table `{t}` defined in the Alfred schema.",
            "",
            "## Columns",
            "",
        ]
        for c in cols:
            pk = " · PRIMARY KEY" if c in pks else ""
            lines.append(f"- `{c}`{pk}")
        lines += ["", "## Ownership", "", "See [[Data Ownership]] for source/derived/user-state classification.", ""]
        _write(out / "Database Tables" / f"table_{t}.md", "\n".join(lines))
        n += 1
    return n


def emit_indexes_note(out: Path):
    if not INDEX_SQL:
        return
    lines = [
        "---",
        "type: database-table",
        "generated: true",
        "layer: database",
        "source: backend/app/db/database.py",
        "status: active",
        "tags: [database, database-table]",
        "---",
        "",
        "# table_indexes",
        "",
        GENERATED_MARKER,
        "",
        "## Indexes (as declared in `INDEXES`)",
        "",
        "```sql",
        INDEX_SQL.strip(),
        "```",
        "",
        "## Related",
        "",
        "- [[Indexes]]",
    ]
    _write(out / "Database Tables" / "table_indexes.md", "\n".join(lines))


def build_index_json(py_data, rust_data, ts_manifest: dict | None) -> dict:
    symbols = py_data["symbols"]
    rust_symbols = rust_data["symbols"]
    py_funcs = [s for s in symbols.values() if s.kind == "function" and not s.is_test]
    py_classes = [s for s in symbols.values() if s.kind == "class"]
    py_tests = [s for s in symbols.values() if s.is_test]
    endpoints = [s for s in symbols.values() if s.route]
    ts = ts_manifest or {}
    return {
        "languages": {
            "python": len(py_data["modules"]),
            "rust": len(rust_data["modules"]),
            "typescript": len(ts.get("modules", [])),
        },
        "modules": sorted(list(py_data["modules"].keys()) + list(rust_data["modules"].keys()) + ts.get("modules", [])),
        "classes": sorted([s.qualified for s in py_classes]) + ts.get("classes", []),
        "functions": sorted([s.qualified for s in py_funcs] + [s.qualified for s in rust_symbols.values()]) + ts.get("functions", []),
        "methods": sorted([s.qualified for s in py_funcs if "." in s.qualified.rsplit(".", 1)[0]]),
        "api_endpoints": sorted([f"{s.route[0]} {s.route[1]}" for s in endpoints]),
        "database_tables": sorted(TABLE_NAMES),
        "react_components": ts.get("react_components", []),
        "hooks": ts.get("hooks", []),
        "types": ts.get("types", []),
        "tests": sorted([s.qualified for s in py_tests]) + ts.get("tests", []),
        "configuration": ["backend/.env (names only — see [[Environment Variables]])"],
    }


def build_dependency_graph(py_data, rust_data, ts_manifest: dict | None) -> dict:
    nodes, edges = [], []
    for q, s in sorted(py_data["symbols"].items()):
        nodes.append({"id": q, "type": "test" if s.is_test else s.kind, "source": s.source})
        for target, rel in sorted(set(s.calls)):
            edges.append({"from": q, "to": target, "relation": rel})
    for q, s in sorted(rust_data["symbols"].items()):
        nodes.append({"id": q, "type": s.kind, "source": s.source})
    if ts_manifest:
        for n in ts_manifest.get("graph", {}).get("nodes", []):
            nodes.append(n)
        for e in ts_manifest.get("graph", {}).get("edges", []):
            edges.append(e)
    return {"nodes": sorted(nodes, key=lambda n: n["id"]), "edges": sorted(edges, key=lambda e: (e["from"], e["to"], e["relation"]))}


# ════════════════════════════════════════════════════════════════
# CANVAS EMITTERS
# ════════════════════════════════════════════════════════════════
CANVAS_SPECS = [
    ("System Architecture", "02 - Architecture/System Architecture.md", [
        ("02 - Architecture/Backend Architecture.md", 0, 0), ("02 - Architecture/Frontend Architecture.md", 340, 0),
        ("02 - Architecture/Gmail Architecture.md", 0, 260), ("02 - Architecture/AI Architecture.md", 340, 260),
        ("02 - Architecture/Database Architecture.md", 170, 500), ("02 - Architecture/Security Architecture.md", 510, 500),
        ("02 - Architecture/Desktop Architecture.md", 170, 740),
    ], [(0, 1, "HTTP+SSE"), (0, 2, "OAuth"), (0, 3, "Ollama"), (0, 4, "SQLite"), (3, 4, "analyses"), (0, 5, "threat model"), (6, 0, "wraps")]),
    ("Gmail OAuth", "03 - Data Flows/Gmail OAuth Flow.md", [
        ("09 - Gmail/Google OAuth.md", 0, 0), ("09 - Gmail/DPAPI.md", 300, 0), ("13 - Security/OAuth Security.md", 0, 260),
        ("09 - Gmail/Token Storage.md", 300, 260),
    ], [(0, 1, "encrypts"), (0, 2, "threats"), (2, 3, "storage")]),
    ("Gmail Sync", "03 - Data Flows/Gmail Incremental Sync Flow.md", [
        ("09 - Gmail/Gmail Provider.md", 0, 0), ("09 - Gmail/History Sync.md", 300, 0),
        ("03 - Data Flows/All Mail Backfill Flow.md", 0, 260), ("09 - Gmail/Pagination.md", 300, 260),
    ], [(0, 1, "historyId"), (0, 2, "backfill"), (2, 3, "page tokens")]),
    ("AI Pipeline", "03 - Data Flows/Email Analysis Flow.md", [
        ("08 - AI/AI Overview.md", 0, 0), ("08 - AI/Structured Output.md", 300, 0),
        ("03 - Data Flows/Background Analysis Job Flow.md", 0, 260), ("08 - AI/AI Failure Handling.md", 300, 260),
    ], [(0, 1, "schema"), (0, 2, "queue"), (0, 3, "errors")]),
    ("Task Derivation", "03 - Data Flows/Task Derivation Flow.md", [
        ("08 - AI/Task Intelligence.md", 0, 0), ("14 - Decisions/ADR-008 - Separate Action Candidates From Tasks.md", 300, 0),
        ("14 - Decisions/ADR-009 - Versioned Task Derivation.md", 0, 260), ("12 - Testing/Migration Testing.md", 300, 260),
    ], [(0, 1, "rationale"), (0, 2, "versioning"), (2, 3, "verified by")]),
    ("Frontend Data Flow", "03 - Data Flows/Frontend Data Fetch Flow.md", [
        ("05 - Frontend/Frontend Overview.md", 0, 0), ("03 - Data Flows/SSE Progress Flow.md", 300, 0),
        ("07 - API/API Map.md", 0, 260), ("10 - UX/Design System.md", 300, 260),
    ], [(0, 1, "progress"), (0, 2, "endpoints"), (0, 3, "tokens")]),
    ("Database Relationships", "06 - Database/Database Overview.md", [
        ("06 - Database/Tables/emails.md", 0, 0), ("06 - Database/Tables/email_analysis.md", 300, 0),
        ("06 - Database/Tables/tasks.md", 0, 260), ("06 - Database/Tables/jobs.md", 300, 260),
        ("06 - Database/Tables/accounts.md", 0, 520), ("06 - Database/Tables/credentials.md", 300, 520),
    ], [(0, 1, "content_hash"), (1, 2, "derives"), (0, 3, "queue target"), (4, 5, "1:1")]),
    ("Runtime Lifecycle", "02 - Architecture/Runtime Lifecycle.md", [
        ("03 - Data Flows/Application Startup Flow.md", 0, 0), ("16 - Code Map/Entry Points.md", 300, 0),
        ("11 - Desktop/Sidecar Architecture.md", 0, 260), ("15 - Operations/Running Alfred.md", 300, 260),
    ], [(0, 1, "entry"), (0, 2, "sidecar"), (2, 3, "manual")]),
]


def emit_canvases(out: Path, vault: Path) -> int:
    n = 0
    for title, focus, nodes, edges in CANVAS_SPECS:
        canvas = {"nodes": [], "edges": []}
        canvas["nodes"].append({
            "id": "focus", "type": "file", "file": focus,
            "x": 340, "y": 300, "width": 320, "height": 120,
        })
        for i, (f, x, y) in enumerate(nodes):
            canvas["nodes"].append({
                "id": f"n{i}", "type": "file", "file": f,
                "x": x, "y": y, "width": 300, "height": 120,
            })
        for i, (a, b, label) in enumerate(edges):
            src = "focus" if a == 0 else f"n{a - 1}"
            dst = f"n{b - 1}" if b > 0 else "focus"
            canvas["edges"].append({
                "id": f"e{i}", "fromNode": src, "toNode": dst, "label": label,
            })
        path = vault / f"{title}.canvas"
        path.write_text(json.dumps(canvas, indent=2), encoding="utf-8")
        n += 1
    return n


# ════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════
def run(check: bool = False, skip_ts: bool = False):
    cfg = load_config()
    vault = ROOT / cfg["vault"]["path"]
    gen_dir = vault / cfg["vault"]["generated_dir"]
    ignore = set(cfg["ignore"]["paths"])
    py_roots = [ROOT / r for r in cfg["sources"]["python_roots"]]
    ts_roots = [ROOT / r for r in cfg["sources"]["typescript_roots"]]
    rust_roots = [ROOT / r for r in cfg["sources"]["rust_roots"]]

    out_dir = tempfile.mkdtemp(prefix="alfred-docs-") if check else str(gen_dir)
    out = Path(out_dir)

    if not check and gen_dir.exists():
        # Safe clean: ONLY the generated section is wiped. Curated notes
        # and everything else in the vault are never touched.
        shutil.rmtree(gen_dir)
    out.mkdir(parents=True, exist_ok=True)

    def is_ignored(p: Path) -> bool:
        rel = p.relative_to(ROOT)
        # Root-level exclusions (legacy dirs) match the first path segment;
        # universal junk dirs match anywhere.
        if rel.parts and rel.parts[0] in ("src", "config", "Data_clean", ".preview-data"):
            return True
        junk = {"__pycache__", "node_modules", "dist", "target", ".git",
                ".pytest_cache", "build", "cache", "venv"}
        return any(seg in junk for seg in rel.parts)

    py_files = sorted(
        p for root in py_roots if root.exists()
        for p in root.rglob("*.py")
        if not is_ignored(p) and "__pycache__" not in str(p) and "tools/docs" not in str(p)
    )
    ts_files = sorted(
        p for root in ts_roots if root.exists()
        for p in root.rglob("*")
        if p.suffix in (".ts", ".tsx") and not is_ignored(p)
    )
    rust_files = sorted(
        p for root in rust_roots if root.exists()
        for p in root.rglob("*.rs") if not is_ignored(p)
    )

    # SQL schema comes from the database module regardless of roots
    parse_schema(ROOT / "backend" / "app" / "db" / "database.py")

    py_data = analyze_python(py_files)
    rust_data = analyze_rust(rust_files)

    ts_manifest = None
    if not skip_ts and ts_files:
        ts_manifest = run_ts_analyzer(ts_files, out)

    # Emit (into temp dir in check mode)
    emit_symbol_notes(py_data["symbols"], out)
    emit_symbol_notes(rust_data["symbols"], out)
    emit_module_notes(py_data["modules"], py_data["symbols"], out)
    emit_module_notes(rust_data["modules"], rust_data["symbols"], out)
    emit_table_notes(out)
    emit_indexes_note(out)

    index = build_index_json(py_data, rust_data, ts_manifest)
    (out / "repository-index.json").write_text(
        json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    graph = build_dependency_graph(py_data, rust_data, ts_manifest)
    # External call targets (libraries) become explicit external nodes so
    # every edge endpoint exists in the graph.
    known = {n["id"] for n in graph["nodes"]}
    for e in graph["edges"]:
        for endpoint in ("from", "to"):
            if e[endpoint] not in known:
                graph["nodes"].append({"id": e[endpoint], "type": "external",
                                       "source": None})
                known.add(e[endpoint])
    graph["nodes"] = sorted(graph["nodes"], key=lambda n: n["id"])
    (out / "dependency-graph.json").write_text(
        json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    emit_canvases(out, vault)

    if check:
        import filecmp
        a, b = Path(out_dir), gen_dir
        missing = []
        different = []
        for f in sorted(a.rglob("*")):
            rel = f.relative_to(a)
            other = b / rel
            if not other.exists():
                missing.append(str(rel))
            elif f.is_file() and not filecmp.cmp(f, other, shallow=False):
                different.append(str(rel))
        extra = sorted(
            str(p.relative_to(b)) for p in b.rglob("*") if not (a / p.relative_to(b)).exists()
        )
        shutil.rmtree(a, ignore_errors=True)
        if missing or different or extra:
            print("STALE: generated docs are out of date.")
            for m in missing:
                print(f"  missing: {m}")
            for d in different[:30]:
                print(f"  changed: {d}")
            for e in extra[:30]:
                print(f"  extra:   {e}")
            sys.exit(1)
        print("OK: generated docs are current.")
        return

    print(f"vault generated at: {gen_dir}")
    print(f"python modules: {len(py_data['modules'])}  symbols: {len(py_data['symbols'])}")
    print(f"rust modules: {len(rust_data['modules'])}")
    if ts_manifest:
        print(f"typescript modules: {len(ts_manifest.get('modules', []))}  components: {len(ts_manifest.get('react_components', []))}")
    print(f"tables: {len(TABLE_NAMES)}")


def run_ts_analyzer(ts_files: list[Path], out: Path) -> dict | None:
    """Shell out to the TypeScript analyzer (uses the TS compiler API)."""
    node = shutil.which("node")
    if not node:
        print("node not found — skipping TypeScript analysis", file=sys.stderr)
        return None
    script = ROOT / "tools" / "docs" / "generate_ts_graph.mjs"
    manifest_path = out / "ts-manifest.json"
    env = dict(__import__("os").environ)
    try:
        res = subprocess.run(
            [node, str(script), "--out", str(manifest_path),
             "--root", str(ROOT), "--generated", str(out.resolve())],
            cwd=str(ROOT / "frontend"), capture_output=True, text=True, timeout=300,
            env=env,
        )
    except (subprocess.TimeoutExpired, OSError) as e:
        print(f"TypeScript analysis failed: {e}", file=sys.stderr)
        return None
    if res.returncode != 0:
        print(f"TypeScript analysis failed:\n{res.stderr[-800:]}", file=sys.stderr)
        return None
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    (out / "ts-manifest.json").unlink(missing_ok=True)
    return manifest
if __name__ == "__main__":
    import argparse
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Alfred knowledge graph generator")
    parser.add_argument("--check", action="store_true", help="exit non-zero if generated docs are stale")
    parser.add_argument("--skip-ts", action="store_true", help="skip TypeScript analysis")
    args = parser.parse_args()
    run(check=args.check, skip_ts=args.skip_ts)
