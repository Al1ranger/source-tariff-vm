# SourceTariffVM

A GenLayer source-to-program compiler and bounded integer interpreter for metered USD rate schedules. Applications reuse an immutable program to calculate many quotes without repeating an LLM request.

## Problem and architecture

A rate document can specify that each job rounds up separately, that durations aggregate before rounding, or that a minimum applies. A blockchain can multiply stored rates but cannot independently interpret those distinctions in an external prose document. SourceTariffVM makes that interpretation an explicit consensus boundary.

```text
Pinned public document + full-response SHA-256 + exact requested SKUs
                              |
                  each validator independently fetches
                              |
               semantic compiler interprets meter rules
                              |
          exact program + source + decision comparison
                              |
                 immutable executable program root
                              |
             integer interpreter -> quote -> receipt
```

This architecture installs a reusable executable artifact. It has no owner-controlled graph, proposal head, certificate consumption or settlement balance. The compiler's consequential output determines rounding scope, rounding direction, unit duration, minimum quantity and exact per-SKU rates. Evidence is acquired inside the nondeterministic flow. Callers supply source coordinates and target SKU names, never rates, summaries, opcodes or compiler outcomes.

## Supported language and consensus

The meter language supports uniform whole time units, `CEIL` or `FLOOR`, `EACH` or `TOTAL` scope, a minimum number of units, and 1–4 constant SKU rates in integer microUSD. One USD equals 1,000,000 microUSD. No model-generated Python is executed.

Leader and validators independently fetch the pinned document and compile it. They must reproduce the entire report exactly: raw-body hash, commitment match, requested SKUs, every operand, decision and artifact root. Disagreement prevents installation; it does not fabricate a stored conflict result. Missing or ambiguous rules yield `UNSUPPORTED`. Fetch failure yields `UNAVAILABLE`; retries retain each attempt in append-only history. Other completed decisions are terminal.

```text
FETCH -> hash mismatch / rejected source / unsupported -> no installed program
   |
   +-> independently compiled identical rules -> COMPILED -> deterministic quotes
   |
   +-> UNAVAILABLE -> retry permitted, earlier attempts retained
```

## Real-source demonstration

Live StudioNet contract: [0xfD40c1B9786D1CA432fB2478C3526D15E5a30a95](https://explorer-studio.genlayer.com/address/0xfD40c1B9786D1CA432fB2478C3526D15E5a30a95). [Seven inspected receipts](LIVE_PROOFS.md) cover deployment, semantic compilation, two quotes, two fail-closed compilation decisions and an expected replay rejection.

The demo fetches [GitHub's official source document](https://github.com/github/docs/blob/56fcfa816f27bca239e5d39fff0d4f74f77ec995/content/billing/reference/actions-runner-pricing.md), not a fixture authored by this project. Its selected larger-runner SKUs are `linux_4_core`, `windows_4_core` and `macos_l`. The document's per-job whole-minute rule must compile to `unit_seconds=60`, `rounding=CEIL`, `scope=EACH`. See [GitHub's pricing reference](https://docs.github.com/en/billing/reference/actions-runner-pricing).

Two 61-second jobs consequently have four billed units. Aggregating them first would produce three, so rounding semantics have a measurable onchain effect. [LIVE_PROOFS.md](LIVE_PROOFS.md) contains only inspected receipts and stored-state readbacks.

Quotes describe caller-selected duration scenarios. They do not prove actual runner usage or settle an invoice. The compiler uses a pinned revision, not an assertion that rates remain current. It does not apply taxes, credits, account allowances or storage charges. Consumers must select the applicable SKU and accepted program root. The adapter supports public UTF-8 GitHub documents up to 12 KiB; missing includes and unsupported nonlinear rules must fail closed.

## API

- `compilation_key(owner, repo, commit, path, expected_hash, skus_csv)` derives the source-and-target key.
- `compile_program(...)` acquires evidence and installs an artifact after consensus.
- `get_compilation(key)`, `get_program(root)` and `get_history(index)` expose evidence and programs.
- `quote(root, sku, durations_csv)` interprets a program without LLM calls.
- `record_quote(root, sku, durations_csv, nonce)` stores a principal-bound receipt.
- `get_receipt(principal, nonce)` returns that immutable receipt.

Durations are positive integer seconds, at most 32 per quote, each bounded to 30 days. Comma-separated arguments avoid shell JSON-quoting ambiguity. Completed compilations cannot be resampled and receipt nonces cannot be reused by the same principal.

## Install, test and deploy

```powershell
python -m pip install -r requirements-dev.txt
npm install -g genlayer
genvm-lint check contracts/SourceTariffVM.py
python -m pytest tests -q
genlayer network set studionet
genlayer deploy --contract contracts/SourceTariffVM.py
```

The concrete GenVM runner is pinned in the first contract line. Direct tests mock acquisition/compiler responses and check state and interpreter safety; they do not exercise validators. The StudioNet workflow tests the real acquisition/semantic consensus path.

```powershell
genlayer write CONTRACT_ADDRESS compile_program --args github docs 56fcfa816f27bca239e5d39fff0d4f74f77ec995 content/billing/reference/actions-runner-pricing.md 62f7f4c44a1597fabe7d133179f7cd3e0d0f3ef7c12ceaf94f35dbeb8d224a04 'linux_4_core,windows_4_core,macos_l'
genlayer call CONTRACT_ADDRESS get_compilation --args REQUEST_ID
genlayer write CONTRACT_ADDRESS record_quote --args PROGRAM_ROOT linux_4_core '61,61' example-one
genlayer call CONTRACT_ADDRESS get_receipt --args PRINCIPAL_ADDRESS example-one
genlayer receipt TRANSACTION_HASH
```

Inspect both `FINALIZED` and leader `SUCCESS`, then compare Explorer source with GitHub. `scripts/verify_receipts.mjs` performs read-only RPC receipt checks.
