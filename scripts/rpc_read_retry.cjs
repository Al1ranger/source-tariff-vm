// Optional CLI preload for transient read failures. Signing/broadcast calls are never retried.
require('node:dns').setDefaultResultOrder('ipv4first');
const baseFetch = globalThis.fetch;
const reads = new Set(['eth_chainId', 'eth_getTransactionCount', 'eth_getTransactionByHash',
  'eth_getTransactionReceipt', 'eth_getCode', 'eth_call', 'gen_call', 'gen_getContractCode',
  'gen_getContractSchema', 'eth_getBalance']);
globalThis.fetch = async (url, options) => {
  let method = '';
  try { method = JSON.parse(options?.body ?? '{}').method ?? ''; } catch {}
  for (let attempt = 0; ; attempt++) {
    try {
      const response = await baseFetch(url, options);
      if (reads.has(method)) {
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        await response.clone().json();
      }
      if (method === 'eth_sendRawTransaction') {
        const body = await response.clone().json();
        if (typeof body.result === 'string') console.error(`BROADCAST_HASH ${body.result}`);
      }
      return response;
    }
    catch (error) {
      console.error(`RPC ${method}: ${error.cause?.code ?? error.message}`);
      if (!reads.has(method) || attempt >= 2) throw error;
      await new Promise(resolve => setTimeout(resolve, 500));
    }
  }
};
