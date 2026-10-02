# StudioNet proofs

## Corrected deployment

StudioNet, chain ID `61999`. [Contract and deployed source](https://explorer-studio.genlayer.com/address/0xfD40c1B9786D1CA432fB2478C3526D15E5a30a95).

Sender: `0x3161CCB0182EB20aF5b38cBDec54a79179525aEA`.

RPC `gen_getContractCode` matches `contracts/SourceTariffVM.py`, normalizing only line endings and the final newline. Normalized source SHA-256: `0c693308eacb7f4cf29066cd31f8b34d0d81040119dd4a6ce842793270b6b3d9`.

## Proof matrix

All seven receipts were inspected through `eth_getTransactionByHash`. All are FINALIZED, with consensus `MAJORITY_AGREE` (not a claim of unanimous execution).

| Scenario | Transaction | Leader execution | Inspected outcome |
|---|---|---|---|
| Corrected deployment | [Deploy](https://explorer-studio.genlayer.com/tx/0x7b41f9d93d7b6ed05cf9c3a20ad4588746baa9334387cb8679935dbc1386e76c) | SUCCESS | Exact corrected source available |
| Independent semantic compilation | [Compile](https://explorer-studio.genlayer.com/tx/0x6b5e69bf5b1f6e9fd59db047247ea232f9b58fc34b38f9e8f3e95a66fe391ec9) | SUCCESS | COMPILED; CEIL, EACH, 60-second units, three exact rates |
| Partial-minute Linux jobs | [Linux quote](https://explorer-studio.genlayer.com/tx/0xd854deb3e8601dd7c6aef6c46a1cbc55100035a2a1d11d72152982e9b5934586) | SUCCESS | 61 + 61 seconds -> [2,2] units -> 48,000 microUSD |
| Exact-minute Windows jobs | [Windows quote](https://explorer-studio.genlayer.com/tx/0xdc8f9589fe1c36fb49450351fb7be7d37d3fe93f9b57b487812df0b61ae38e6e) | SUCCESS | 60 + 60 seconds -> [1,1] units -> 44,000 microUSD |
| Missing requested SKU rate | [Unsupported](https://explorer-studio.genlayer.com/tx/0xe066e1ab6c48f2e10d2d0a4c801694f28f6316e38c410bbf9cf3b45f94339d4f) | SUCCESS | UNSUPPORTED; code null; empty program root |
| Wrong source commitment | [Hash mismatch](https://explorer-studio.genlayer.com/tx/0xf1c4e1c51b7a905a927f0891c5bca81562d7a85bedf37138a5068954007e9888) | SUCCESS | HASH_MISMATCH; no executable program installed |
| Nonce reuse with changed duration | [Replay rejection](https://explorer-studio.genlayer.com/tx/0x95b13c2136b9669284ff39739ab8fcf5f5b30cee7d2421bdcb20a4a2f0aeaead) | ERROR (expected) | `[EXPECTED] receipt nonce already used by principal`; original receipt unchanged |

The replay transaction is a rejection proof, **not** successful usage. Successful negative compilation transactions record fail-closed decisions, without installing programs.

## Acquired source and stored state

The contract fetches [GitHub's official pinned document](https://github.com/github/docs/blob/56fcfa816f27bca239e5d39fff0d4f74f77ec995/content/billing/reference/actions-runner-pricing.md), not a fixture authored by this project. HTTP 200; 4,858 bytes; full-body SHA-256 `62f7f4c44a1597fabe7d133179f7cd3e0d0f3ef7c12ceaf94f35dbeb8d224a04`.

Installed code: USD; minimum units 0; CEIL rounding; EACH scope; 60-second units. Rates in microUSD per unit: `linux_4_core=12000`, `windows_4_core=22000`, `macos_l=77000`.

- Compiled request: `70cc04a9eced1d6391c00a55e631aacb64be4b3012b5f0a77bd5d65b5d6dc0c7`.
- Program root: `9af1c7ed8d67bc035f9b96830dc0456903e6d1eda238f1fa649082b60f8b4997`.
- Compilation report root: `3650c5d317873d7a47149949d37e69389f343186d07ff7feca24fcb07aba41de`.
- Unsupported request: `9ace6c9ddba90686f889744243023ff876cfac47d3608130619a64a5b92e4b35`, requested `actions_linux`; its rate is not present in the fetched body.
- Wrong-commitment request: `12c92be10cbd19a45be9e3075941afd6b509dacba544f1d6bff76f5c9e40669d`; expected hash deliberately set to 64 `a` characters.
- Linux nonce: `linux-two-jobs`; receipt root `b6d395b71d4075a91826e7292e312f9c7a53001f1ab7691a9af8780a359127f3`.
- Windows nonce: `windows-boundary`; receipt root `9b1dcea305423d00da40882591f1e3d49e8c3ef146183a40674876f529b2fb77`.

EACH rounding bills four units for two 61-second jobs; TOTAL rounding would bill three. Quotes execute the installed operands without another model call. They describe duration scenarios, not independently verified actual usage or settled invoices. Pinned historical rates do not imply current prices.

## Reproduce checks

```powershell
genvm-lint check contracts/SourceTariffVM.py
python -m pytest tests -q
node --require ./scripts/rpc_read_retry.cjs scripts/verify_source.mjs 0xfD40c1B9786D1CA432fB2478C3526D15E5a30a95
node --require ./scripts/rpc_read_retry.cjs scripts/verify_receipts.mjs 0x6b5e69bf5b1f6e9fd59db047247ea232f9b58fc34b38f9e8f3e95a66fe391ec9
node --require ./scripts/rpc_read_retry.cjs scripts/verify_receipts.mjs --expect-error 0x95b13c2136b9669284ff39739ab8fcf5f5b30cee7d2421bdcb20a4a2f0aeaead
genlayer call 0xfD40c1B9786D1CA432fB2478C3526D15E5a30a95 get_compilation --args 70cc04a9eced1d6391c00a55e631aacb64be4b3012b5f0a77bd5d65b5d6dc0c7
genlayer call 0xfD40c1B9786D1CA432fB2478C3526D15E5a30a95 get_receipt --args 0x3161CCB0182EB20aF5b38cBDec54a79179525aEA linux-two-jobs
```

GenVM lint and SDK validation pass; **11 tests pass** (10 direct state/interpreter tests and one pure equivalence test). Direct tests mock web and LLM calls; they are not live-validator tests. StudioNet compilation and unsupported-SKU proofs exercise actual fetched evidence and semantic consensus. Quote and replay receipts exercise deterministic execution and state protection.
