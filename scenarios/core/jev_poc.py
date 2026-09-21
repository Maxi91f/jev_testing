"""Shared Jev request, response and evidence handling (stdlib only)."""

# All imports are part of Python's standard library: no SDK installation needed.
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Pin a version so an alias update cannot silently change the model.
MODEL = "jev-1.13.0"
# Socket-operation timeout, in seconds; not a strict total runtime limit.
TIMEOUT_SECONDS = 60
# __file__ locates this script; / joins filesystem path components.
OUTPUT_DIR = Path(__file__).resolve().parents[2] / "results" / "jev"
# The API key is sent in an HTTP header, not in the JSON body.
ENDPOINT = "https://api.typesafe.ai/v1/systemone"


def run(message, questions, print_scale=None, evaluate=None):
    # Check edited constants before making requests.
    if not message.strip():
        raise ValueError("MESSAGE must not be empty.")

    # This is the API body: model selects Jev, state provides the information,
    # and questions tells Jev what to evaluate about that information.
    payload = {
        "model": MODEL,
        "state": {"message": message},
        "questions": questions,
    }
    # Show exactly what will be sent. dumps turns a dictionary into JSON text.
    # indent adds whitespace; ensure_ascii=False keeps Unicode readable.
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    # Require the API key in the environment; there is no interactive prompt.
    # Keep secrets out of source code. This script does not read AWS SSM.
    api_key = os.environ.get("TYPESAFE_API_KEY", "").strip()
    if not api_key:
        raise ValueError("TYPESAFE_API_KEY must be set in the environment.")

    # Reuse one results directory; the UTC timestamp distinguishes each file.
    # parents=True creates missing folders; exist_ok=True allows the shared folder.
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"exchange_{stamp}.json"
    print(f"Evidence: {output_path}")

    # Save enough context to match each response to its input later.
    # Authentication headers are deliberately absent from this record.
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "url": ENDPOINT,
        "method": "POST",
        "request": payload,
    }
    # POST sends a body. encode() converts JSON text to UTF-8 bytes.
    # Authorization authenticates us; Content-Type describes the body.
    # Constructing Request does not contact the server yet.
    request = Request(
        ENDPOINT,
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    # A monotonic timer measures elapsed time without wall-clock changes.
    # This includes network, parsing and printing, not just model inference.
    start = time.perf_counter()
    try:
        # urlopen actually sends the request. timeout bounds blocking socket
        # operations; it is not a strict total runtime limit. with closes
        # the response connection even if reading raises an exception.
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            record["status"] = response.status
            record["response_raw"] = response.read().decode("utf-8")
        # Keep the original response text AND its parsed Python dictionary.
        body = json.loads(record["response_raw"])
        record["response"] = body
        # Basic envelope check, not full validation of every answer field.
        if not isinstance(body.get("answers"), dict):
            raise ValueError("Response has no answers object; inspect evidence")
        print(f"Message: {message}")
        print(json.dumps(body["answers"], indent=2, ensure_ascii=False))
        if print_scale is not None:
            print_scale()
        if evaluate is not None:
            record["evaluation"] = evaluate(body)
        # usage is the API's token accounting, not a dollar estimate.
        print(f"Usage: {body.get('usage', {})}")
    except HTTPError as exc:
        # The server responded with an HTTP error. Preserve its body for
        # diagnosis; errors='replace' tolerates non-UTF-8 error responses.
        record["status"] = exc.code
        record["response_raw"] = exc.read().decode("utf-8", errors="replace")
        record["error"] = f"HTTP {exc.code}"
        print(f"HTTP {exc.code}; see evidence", file=sys.stderr)
    except (URLError, TimeoutError, ValueError) as exc:
        # Network failures, timeouts, invalid JSON, or our envelope check.
        # stderr separates error messages from normal output in shell use.
        record["error"] = str(exc)
        print(str(exc), file=sys.stderr)
    finally:
        # Runs after success OR a handled error. Convert seconds to ms.
        record["elapsed_ms"] = round((time.perf_counter() - start) * 1000, 1)
        # The filename identifies the full request/response exchange and UTC time.
        # 'x' creates a new file and refuses to overwrite an existing one.
        with output_path.open("x", encoding="utf-8") as output:
            # Indentation makes the saved request and response easy to read.
            json.dump(record, output, indent=2, ensure_ascii=False)
            output.write("\n")
        print(f"Elapsed: {record['elapsed_ms']} ms")
    # Shell convention: 0 = success, 1 = failure.
    return int("error" in record)
