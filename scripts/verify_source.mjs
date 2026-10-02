import fs from 'node:fs';
import crypto from 'node:crypto';
const address = process.argv[2];
if (!/^0x[0-9a-fA-F]{40}$/.test(address ?? '')) throw new Error('Contract address required');
const response = await fetch('https://studio.genlayer.com/api', {
  method: 'POST', headers: {'content-type': 'application/json'},
  body: JSON.stringify({jsonrpc: '2.0', id: 1, method: 'gen_getContractCode', params: [address]}),
});
const json = await response.json();
if (json.error || typeof json.result !== 'string') throw new Error(JSON.stringify(json.error));
const normalize = text => text.replace(/\r\n/g, '\n').trimEnd() + '\n';
const deployed = normalize(Buffer.from(json.result, 'base64').toString('utf8'));
const local = normalize(fs.readFileSync('contracts/SourceTariffVM.py', 'utf8'));
const matches = deployed === local;
console.log(JSON.stringify({address, matches, normalized_source_sha256:
  crypto.createHash('sha256').update(deployed).digest('hex')}, null, 2));
if (!matches) process.exitCode = 1;
