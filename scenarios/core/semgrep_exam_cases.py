"""Fixed rule-reading exercises; the local engine supplies the answer key."""

CASES = [
    ("Literal call", {"pattern": "danger(...)"}, [
        "danger(x)", "safe(x)", "# danger(x)\npass", "text = 'danger(x)'",
    ]),
    ("Argument ellipsis", {"pattern": "send(...)"}, [
        "send()", "send(x, y)", "send(x)", "sender(x)",
    ]),
    ("Single argument metavariable", {"pattern": "send($X)"}, [
        "send(x)", "send()", "send(x, y)", "send(x + y)",
    ]),
    ("Repeated metavariable", {"pattern": "compare($X, $X)"}, [
        "compare(a, a)", "compare(a, b)", "compare(obj.x, obj.x)", "compare(f(), g())",
    ]),
    ("OR patterns", {"pattern-either": [{"pattern": "alpha(...)"}, {"pattern": "beta(...)"}]}, [
        "alpha(x)", "beta(x)", "gamma(x)", "alpha()\nbeta()",
    ]),
    ("Exact exclusion", {"patterns": [{"pattern": "send(...)"}, {"pattern-not": "send(safe)"}]}, [
        "send(safe)", "send(unsafe)", "send(safe, extra)", "send()",
    ]),
    ("Keyword exclusion", {"patterns": [{"pattern": "connect(...)"}, {"pattern-not": "connect(..., verify=True, ...)"}]}, [
        "connect(host)", "connect(host, verify=True)", "connect(host, verify=False)", "connect(verify=True, host=host)",
    ]),
    ("Function containment", {"patterns": [{"pattern": "danger(...)"}, {"pattern-inside": "def handler(...):\n    ..."}]}, [
        "def handler():\n    danger(x)", "def worker():\n    danger(x)", "danger(x)", "def handler(x):\n    safe(x)",
    ]),
    ("Negative containment", {"patterns": [{"pattern": "danger(...)"}, {"pattern-not-inside": "def trusted(...):\n    ..."}]}, [
        "def trusted():\n    danger(x)", "def untrusted():\n    danger(x)", "danger(x)", "def trusted():\n    safe(x)",
    ]),
    ("Identifier regex", {"patterns": [{"pattern": "$FUNC(...)"}, {"metavariable-regex": {"metavariable": "$FUNC", "regex": "^unsafe_.*"}}]}, [
        "unsafe_open(x)", "safe_open(x)", "unsafe_close()", "open_unsafe(x)",
    ]),
    ("Numeric comparison", {"patterns": [{"pattern": "retry($N)"}, {"metavariable-comparison": {"metavariable": "$N", "comparison": "$N > 3"}}]}, [
        "retry(3)", "retry(4)", "retry(10)", "retry(0)",
    ]),
    ("OR then exclusion", {"patterns": [{"pattern-either": [{"pattern": "alpha(...)"}, {"pattern": "beta(...)"}]}, {"pattern-not": "beta(safe)"}]}, [
        "alpha(safe)", "beta(safe)", "beta(unsafe)", "gamma(unsafe)",
    ]),
    ("Ordered statement sequence", {"pattern": "prepare($X)\n...\nuse($X)"}, [
        "prepare(a)\nuse(a)", "use(a)\nprepare(a)", "prepare(a)\nlog()\nuse(a)", "prepare(a)\nuse(b)",
    ]),
    ("Method receiver reuse", {"pattern": "$OBJ.copy_from($OBJ)"}, [
        "a.copy_from(a)", "a.copy_from(b)", "obj.member.copy_from(obj.member)", "copy_from(a)",
    ]),
    ("Keyword literal", {"pattern": "fetch(..., secure=False, ...)"}, [
        "fetch(url, secure=False)", "fetch(url, secure=True)", "fetch(url)", "fetch(secure=False, timeout=1)",
    ]),
    ("Text regex versus AST", {"pattern-regex": "danger\\("}, [
        "danger(x)", "# danger(x)\npass", "text = 'danger(x)'", "danger (x)",
    ]),
    ("Same-variable validation exclusion", {"patterns": [{"pattern": "execute($X)"}, {"pattern-not-inside": "validate($X)\n...\nexecute($X)"}]}, [
        "validate(a)\nexecute(a)", "validate(b)\nexecute(a)", "execute(a)\nvalidate(a)", "execute(a)",
    ]),
    ("Any-variable validation exclusion", {"patterns": [{"pattern": "execute($X)"}, {"pattern-not-inside": "validate($Y)\n...\nexecute($X)"}]}, [
        "validate(a)\nexecute(a)", "validate(b)\nexecute(a)", "execute(a)\nvalidate(a)", "execute(a)",
    ]),
    ("Multiple AND exclusions", {"patterns": [{"pattern": "send(...)"}, {"pattern-not": "send(safe)"}, {"pattern-not": "send(trusted)"}]}, [
        "send(safe)", "send(trusted)", "send(unknown)", "send()",
    ]),
    ("Nested metavariable pattern", {"patterns": [{"pattern": "send($X)"}, {"metavariable-pattern": {"metavariable": "$X", "pattern": "source(...)"}}]}, [
        "send(source())", "send(other())", "send(source(x))", "send(x)",
    ]),
]
