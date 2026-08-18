#!/usr/bin/env node
/* Alfred TypeScript/TSX knowledge-graph analyzer (TypeScript compiler API).
 * Emits React component / hook / type / module / test notes into the
 * generated vault and writes a manifest consumed by the Python generator.
 * Run from the frontend directory (resolves typescript locally).
 */
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const args = process.argv.slice(2);
const outFlag = args.indexOf("--out");
const rootFlag = args.indexOf("--root");
const genFlag = args.indexOf("--generated");
const OUT = outFlag >= 0 ? args[outFlag + 1] : "ts-manifest.json";
const REPO_ROOT = rootFlag >= 0 ? args[rootFlag + 1] : path.resolve("..");
const FRONTEND_ROOT = path.join(REPO_ROOT, "frontend");
const GENERATED =
  genFlag >= 0
    ? args[genFlag + 1]
    : path.join(REPO_ROOT, "docs", "obsidian", "99 - Generated");

// Resolve TypeScript from the frontend package (script lives outside it).
const requireFromFrontend = createRequire(path.join(FRONTEND_ROOT, "package.json"));
const ts = requireFromFrontend("typescript");

const MARKER =
  "> Auto-generated from source code. Do not manually edit this file; update source code or generator instead.";

function walk(dir) {
  const out = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (entry.name === "node_modules" || entry.name === "dist") continue;
    const p = path.join(dir, entry.name);
    if (entry.isDirectory()) out.push(...walk(p));
    else if (/\.(ts|tsx)$/.test(entry.name)) out.push(p);
  }
  return out;
}

const files = walk(path.join(FRONTEND_ROOT, "src"))
  .concat(walk(path.join(FRONTEND_ROOT, "tests")))
  .sort();

const program = ts.createProgram(files, {
  target: ts.ScriptTarget.ES2022,
  jsx: ts.JsxEmit.ReactJSX,
  module: ts.ModuleKind.ESNext,
  moduleResolution: ts.ModuleResolutionKind.Bundler,
  skipLibCheck: true,
  noEmit: true,
});

const checker = program.getTypeChecker();

const modules = [];
const reactComponents = [];
const hooks = [];
const types = [];
const functions = [];
const tests = [];
const graph = { nodes: [], edges: [] };

function relSource(file) {
  return path.relative(REPO_ROOT, file).replace(/\\/g, "/");
}

function displayName(file, symbolName) {
  return `${relSource(file).replace(/\.(ts|tsx)$/, "").replace(/\//g, ".")}.${symbolName}`;
}

function writeNote(filePath, content) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, content, "utf8");
}

function unwrapJsx(expr) {
  let cur = expr;
  while (
    cur &&
    (ts.isParenthesizedExpression(cur) || ts.isAsExpression(cur) || ts.isTypeAssertionExpression(cur))
  ) {
    cur = cur.expression;
  }
  return cur;
}

function isComponent(node, srcFile) {
  // PascalCase function returning JSX (arrow body or return statement)
  const nameText = node.name ? node.name.getText(srcFile) : "";
  if (!/^[A-Z]/.test(nameText)) return false;
  if (ts.isArrowFunction(node)) {
    const body = unwrapJsx(node.body);
    return ts.isJsxElement(body) || ts.isJsxFragment(body);
  }
  if ((ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node)) && node.body) {
    const ret = node.body.statements.find(ts.isReturnStatement);
    if (ret) {
      const expr = unwrapJsx(ret.expression);
      return Boolean(expr && (ts.isJsxElement(expr) || ts.isJsxFragment(expr)));
    }
  }
  return false;
}

function jsxChildComponents(node, acc) {
  ts.forEachChild(node, (child) => {
    if (ts.isJsxElement(child) || ts.isJsxSelfClosingElement(child)) {
      const tag = child.openingElement.tagName;
      if (ts.isIdentifier(tag) && /^[A-Z]/.test(tag.text)) acc.add(tag.text);
    }
    if (ts.isJsxElement(child) || ts.isJsxFragment(child) || ts.isJsxExpression(child)) {
      jsxChildComponents(child, acc);
    }
  });
}

function collectCallsAndQueries(node, src) {
  const calls = new Set();
  const queries = [];
  function visit(n) {
    if (ts.isCallExpression(n)) {
      const text = n.expression.getText(src);
      calls.add(text);
      if (text.startsWith("useQuery")) {
        const arg = n.arguments[0];
        if (arg) queries.push(arg.getText(src));
      }
      if (text === "useMutation") {
        const cfg = n.arguments[0];
        if (cfg && ts.isObjectLiteralExpression(cfg)) {
          const fn = cfg.properties.find(
            (p) => p.name && p.name.getText(src) === "mutationFn"
          );
          if (fn && ts.isPropertyAssignment(fn)) queries.push("mutate: " + fn.initializer.getText(src));
        }
      }
    }
    ts.forEachChild(n, visit);
  }
  visit(node);
  return { calls: [...calls], queries };
}

// Pre-pass: name → qualified id map (components/functions across files)
const nameToId = new Map();
for (const file of files) {
  const preSrc = ts.createSourceFile(
    file,
    fs.readFileSync(file, "utf8"),
    ts.ScriptTarget.ES2022,
    true,
    file.endsWith("tsx") ? ts.ScriptKind.TSX : ts.ScriptKind.TS
  );
  (function collect(node) {
    let name = null;
    if (ts.isFunctionDeclaration(node) && node.name) name = node.name.text;
    else if (ts.isVariableStatement(node)) {
      for (const d of node.declarationList.declarations) {
        if (ts.isIdentifier(d.name) && d.initializer) {
          if (!nameToId.has(d.name.text)) nameToId.set(d.name.text, displayName(file, d.name.text));
        }
      }
    } else if ((ts.isInterfaceDeclaration(node) || ts.isTypeAliasDeclaration(node)) && node.name) {
      name = node.name.text;
    }
    if (name && !nameToId.has(name)) nameToId.set(name, displayName(file, name));
    ts.forEachChild(node, collect);
  })(preSrc);
}

for (const file of files) {
  const src = ts.createSourceFile(file, fs.readFileSync(file, "utf8"), ts.ScriptTarget.ES2022, true, file.endsWith("tsx") ? ts.ScriptKind.TSX : ts.ScriptKind.TS);
  const srcText = src.text;
  const isTestFile = /\.test\.(ts|tsx)$/.test(file);
  const rel = relSource(file);
  const modId = `${rel.replace(/\.(ts|tsx)$/, "").replace(/\//g, ".")}`;
  modules.push(modId);

  const imports = [];
  ts.forEachChild(src, (node) => {
    if (ts.isImportDeclaration(node) && ts.isStringLiteral(node.moduleSpecifier)) {
      const names = [];
      const clause = node.importClause;
      if (clause) {
        if (clause.name) names.push(clause.name.text);
        if (clause.namedBindings) {
          if (ts.isNamedImports(clause.namedBindings)) {
            for (const el of clause.namedBindings.elements) names.push(el.name.text);
          }
        }
      }
      imports.push({ module: node.moduleSpecifier.text, names });
    }
  });

  const symbolNotes = [];

  // Nested named functions (e.g. `const X = memo(function X(){…})`)
  function scanAllFunctions(node) {
    if ((ts.isFunctionDeclaration(node) || ts.isFunctionExpression(node)) && node.name) {
      const name = node.name.text;
      const full = displayName(file, name);
      if (!symbolNotes.some((s) => s.name === name && s.kind !== "types")) {
        const component = isComponent(node, src);
        const kind = component ? "react_components" : name.startsWith("use") ? "hooks" : "functions";
        if (kind === "functions") functions.push(full);
        symbolNotes.push({ node, name, full, kind });
      }
    }
    ts.forEachChild(node, scanAllFunctions);
  }
  scanAllFunctions(src);

  ts.forEachChild(src, (node) => {
    if (ts.isVariableStatement(node)) {
      for (const decl of node.declarationList.declarations) {
        if (!ts.isIdentifier(decl.name) || !decl.initializer) continue;
        const name = decl.name.text;
        const full = displayName(file, name);
        if (ts.isArrowFunction(decl.initializer)) {
          const component = isComponent(decl.initializer, src);
          const kind = component ? "react_components" : name.startsWith("use") ? "hooks" : "functions";
          if (kind === "functions") functions.push(full);
          symbolNotes.push({ node: decl.initializer, name, full, kind });
        }
      }
    } else if (ts.isInterfaceDeclaration(node) || ts.isTypeAliasDeclaration(node)) {
      const name = node.name.text;
      const full = displayName(file, name);
      types.push(full);
      symbolNotes.push({ node, name, full, kind: "types" });
    }
  });

  if (isTestFile) {
    // collect test case names (full-tree — they nest inside describe())
    const testNames = [];
    function scanTests(node) {
      if (
        ts.isCallExpression(node) &&
        ts.isIdentifier(node.expression) &&
        (node.expression.text === "it" || node.expression.text === "test")
      ) {
        const label = node.arguments[0];
        if (label && ts.isStringLiteral(label)) testNames.push(label.text);
      }
      ts.forEachChild(node, scanTests);
    }
    scanTests(src);
    for (const tn of testNames) {
      const full = `${modId}.${tn}`;
      tests.push(full);
      writeNote(
        path.join(GENERATED, "Tests", `${full}.md`),
        [
          "---",
          "type: test",
          "generated: true",
          "language: typescript",
          "layer: frontend",
          `qualified_name: ${full}`,
          `source: ${rel}`,
          "status: active",
          "tags: [test, frontend]",
          "---",
          "",
          `# ${tn}`,
          "",
          MARKER,
          "",
          "## Purpose",
          "",
          `Frontend test case defined in \`${rel}\`.`,
          "",
          "## Related",
          "",
          `- [[${modId}]]`,
          "",
        ].join("\n")
      );
    }
  }

  for (const { node, name, full, kind } of symbolNotes) {
    const isComp = kind === "react_components";
    const isHook = kind === "hooks";
    const isType = kind === "types";
    const sig = isType ? "" : node.getText(src).split("{")[0].trim();
    const children = new Set();
    if (isComp && node.body) {
      jsxChildComponents(node.body, children);
    }
    const { calls, queries } = isComp || isHook ? collectCallsAndQueries(node, src) : { calls: [], queries: [] };
    const folder = isComp ? "React Components" : isHook ? "Hooks" : isType ? "Types" : "Functions";
    const target = isComp ? "react_components" : isHook ? "hooks" : isType ? "types" : "functions";
    const tags = [isComp ? "component" : isHook ? "hook" : isType ? "type" : "function", "frontend"];

    const childrenLinks = [...children]
      .map((c) => {
        const target = nameToId.get(c);
        return target ? `- [[${target}|${c}]] (renders)` : `- \`${c}\` (renders, external)`;
      })
      .join("\n");
    const queryLinks = queries.map((q) => `- \`${q}\``).join("\n");
    const callLinks = calls
      .filter((c) => /^[A-Za-z_][\w]*\(/.test(c))
      .map((c) => `- \`${c.split("(")[0]}\``)
      .slice(0, 20)
      .join("\n");

    writeNote(
      path.join(GENERATED, folder, `${full}.md`),
      [
        "---",
        `type: ${isComp ? "component" : isHook ? "hook" : isType ? "type" : "function"}`,
        "generated: true",
        "language: typescript",
        "layer: frontend",
        `qualified_name: ${full}`,
        `source: ${rel}`,
        "status: active",
        `tags: [${tags.join(", ")}]`,
        "---",
        "",
        `# ${name}`,
        "",
        MARKER,
        "",
        "## Purpose",
        "",
        isComp
          ? `React component declared in \`${rel}\`.`
          : isHook
            ? `React hook declared in \`${rel}\`.`
            : isType
              ? `TypeScript ${ts.isInterfaceDeclaration(node) ? "interface" : "type alias"} declared in \`${rel}\`.`
              : `Function declared in \`${rel}\`.`,
        "",
        "## Location",
        "",
        `\`${rel}\``,
        "",
        ...(sig ? ["## Signature", "", "```ts", sig, "```", ""] : []),
        ...(isComp && childrenLinks ? ["## Renders", "", childrenLinks, ""] : []),
        ...(queries.length ? ["## React Query usage", "", queryLinks, ""] : []),
        ...(callLinks ? ["## Calls", "", callLinks, ""] : []),
        "## Related",
        "",
        `- [[${modId}|${modId.split(".").pop()}]] (module)`,
        "",
      ].join("\n")
    );

    graph.nodes.push({ id: full, type: target, source: rel });
    if (target === "react_components") reactComponents.push(full);
    else if (target === "hooks") hooks.push(full);
    for (const c of children) {
      const childTarget = nameToId.get(c);
      if (childTarget) graph.edges.push({ from: full, to: childTarget, relation: "renders" });
    }
  }

  // module note
  writeNote(
    path.join(GENERATED, "Modules", `${modId}.md`),
    [
      "---",
      "type: module",
      "generated: true",
      "language: typescript",
      "layer: frontend",
      `qualified_name: ${modId}`,
      `source: ${rel}`,
      "status: active",
      "tags: [module, frontend]",
      "---",
      "",
      `# ${modId}`,
      "",
      MARKER,
      "",
      "## Source",
      "",
      `\`${rel}\``,
      "",
      ...(imports.length ? ["## Imports", "", ...imports.map((i) => `- \`${i.module}\` â† ${i.names.join(", ")}`), ""] : []),
    ].join("\n")
  );
}

const manifest = {
  modules: modules.sort(),
  react_components: reactComponents.sort(),
  hooks: hooks.sort(),
  types: types.sort(),
  functions: functions.sort(),
  tests: tests.sort(),
  classes: [],
  graph,
};
fs.writeFileSync(OUT, JSON.stringify(manifest, null, 2));
console.log(`ts analyzer: ${files.length} files, ${modules.length} modules, ${reactComponents.length} components`);



