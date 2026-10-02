# Security model

- Only fixed HTTPS GitHub raw URLs with validated paths and a 40-hex commit are acquired. Complete bodies must match the expected SHA-256 before compilation.
- The model cannot mutate storage or execute Python. Operands must satisfy a small bounded instruction set and the exact requested SKU set.
- Validators refetch and independently compile all consequential rules. Exact comparison includes the decision and rounding scope; no confidence tolerance crosses a decision boundary.
- Artifacts are addressed by source-and-program hashes. Completed compilations cannot be replaced or resampled. Fetch retries preserve earlier reports.
- Quotes validate durations and SKU membership. Receipts use authenticated sender plus nonce as their storage key; another principal cannot overwrite them.
- Source ownership, provider honesty and actual metered usage are outside the proof. Pins preserve a revision, not freshness. No money moves.
- Compilation is deliberately permissionless: a caller can create a new source-spec key, but cannot overwrite a completed compilation or mutate an installed artifact. There is no privileged admin, upgrade path, balance or external adapter dispatch.
- HTTP non-200 responses can be recorded as UNAVAILABLE. Transport exceptions or exhausted consensus abort execution without claiming that a stored conflict/unavailability report exists.

Independent models can share a semantic error. Exact equality guards disagreement, not objective correctness. Consumers must review applicability and the source revision. Missing referenced documents cannot be assumed to contain a rate or rule.

Report sensitive defects privately to the repository owner.
