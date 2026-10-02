# Builder submission draft

Publish the repository before submitting. This file does not claim a completed GitHub push.

Contribution type: Builder / Intelligent Contracts.

Title: SourceTariffVM — Consensus-Compiled Metered Tariffs

## Description (973 characters)

SourceTariffVM is a reusable GenLayer source-to-program compiler and integer interpreter, not a graph or certificate variant. Leader and validators independently fetch a pinned public rate document, verify its SHA-256 and semantically compile unit duration, per-job versus aggregate rounding, rounding direction, minimum units and exact SKU rates. Exact equality of the complete report is required before an immutable executable program is installed.

Applications reuse the program for quotes without another LLM call. Missing rates and wrong commitments cannot install code. Completed compilations are terminal, history is append-only, and receipt nonces are principal-bound.

StudioNet proofs show official GitHub documentation compiled, two quote scenarios executed, missing-rate and hash-mismatch decisions installed nothing, and nonce replay was rejected without overwriting the original receipt. Quotes are scenarios, not proof of actual usage or invoice settlement.

## Evidence

- [Repository](https://github.com/Al1ranger/source-tariff-vm)
- [Contract](https://github.com/Al1ranger/source-tariff-vm/blob/main/contracts/SourceTariffVM.py)
- [README](https://github.com/Al1ranger/source-tariff-vm/blob/main/README.md)
- [Proof matrix](https://github.com/Al1ranger/source-tariff-vm/blob/main/LIVE_PROOFS.md)
- [Deployed source](https://explorer-studio.genlayer.com/address/0xfD40c1B9786D1CA432fB2478C3526D15E5a30a95)
- [Deployment](https://explorer-studio.genlayer.com/tx/0x7b41f9d93d7b6ed05cf9c3a20ad4588746baa9334387cb8679935dbc1386e76c)
- [Semantic compilation](https://explorer-studio.genlayer.com/tx/0x6b5e69bf5b1f6e9fd59db047247ea232f9b58fc34b38f9e8f3e95a66fe391ec9)
- [Linux quote](https://explorer-studio.genlayer.com/tx/0xd854deb3e8601dd7c6aef6c46a1cbc55100035a2a1d11d72152982e9b5934586)
- [Windows quote](https://explorer-studio.genlayer.com/tx/0xdc8f9589fe1c36fb49450351fb7be7d37d3fe93f9b57b487812df0b61ae38e6e)
- [Unsupported rate](https://explorer-studio.genlayer.com/tx/0xe066e1ab6c48f2e10d2d0a4c801694f28f6316e38c410bbf9cf3b45f94339d4f)
- [Hash mismatch](https://explorer-studio.genlayer.com/tx/0xf1c4e1c51b7a905a927f0891c5bca81562d7a85bedf37138a5068954007e9888)
- [Replay rejection — expected execution error](https://explorer-studio.genlayer.com/tx/0x95b13c2136b9669284ff39739ab8fcf5f5b30cee7d2421bdcb20a4a2f0aeaead)
