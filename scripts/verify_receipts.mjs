// Read-only receipt verification. Does not sign or send transactions.
const args = process.argv.slice(2);
const expectError = args[0] === '--expect-error';
const ids = expectError ? args.slice(1) : args;
if (!ids.length || ids.some(id => !/^0x[0-9a-fA-F]{64}$/.test(id))) {
  throw new Error('Usage: node scripts/verify_receipts.mjs TRANSACTION_HASH ...');
}
const results = await Promise.all(ids.map(async hash => {
  const response = await fetch('https://studio.genlayer.com/api', {
    method: 'POST', headers: {'content-type': 'application/json'},
    body: JSON.stringify({jsonrpc: '2.0', id: 1, method: 'eth_getTransactionByHash', params: [hash]}),
  });
  const json = await response.json();
  if (json.error || !json.result) throw new Error(JSON.stringify(json.error ?? 'Missing transaction'));
  const tx = json.result;
  const leader = tx.consensus_data?.leader_receipt?.find(item => item.mode === 'leader');
  return {hash, status: tx.status, execution: leader?.execution_result, consensus: tx.result_name,
    ...(expectError ? {rejection: leader?.genvm_result?.stderr || leader?.result} : {})};
}));
console.log(JSON.stringify(results, null, 2));
if (results.some(item => item.status !== 'FINALIZED' ||
  item.execution !== (expectError ? 'ERROR' : 'SUCCESS'))) process.exitCode = 1;
