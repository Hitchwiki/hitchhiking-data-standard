From [hitchhiking-data-standard](https://github.com/Hitchwiki/hitchhiking-data-standard/tree/main/nostr/fetch_hitchhiking_events).

# Querying all hitchhiking ride events

The ride events are stored on Nostr relays. Interacting with Nostr relays is tradintionally done in `.js`.

## Install

```shell
npm install ws
npm install --save-dev @types/ws
# or just ... to install from package.json
npm install
```

## Run 

```shell
# to compile src/index.ts into dist/index.js
npx tsc 
# to run the fetcher
node dist/index.js
```