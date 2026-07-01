// Copyright (C) 2025-2026 Till Wenke
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <https://www.gnu.org/licenses/>.

import WebSocket from "ws";
import { NostrFetcher } from "nostr-fetch";
import { writeFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { config as loadEnv } from "dotenv";

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Load environment variables from the .env file next to this script (if present).
// In production the fetch_nostr cron supplies the environment instead; dotenv
// leaves any variable that is already set untouched, so that keeps working.
loadEnv({ path: join(__dirname, "..", ".env") });

const nHoursAgo = (hrs: number): number =>
  Math.floor((Date.now() - hrs * 60 * 60 * 1000) / 1000);

const fetcher = NostrFetcher.init({
  webSocketConstructor: WebSocket,
});
if (!process.env.RELAYS) {
    console.error("RELAYS env var is not set");
    process.exit(1);
}
const relayUrls: string[] = JSON.parse(process.env.RELAYS);
console.log("Using relays:", relayUrls);

// // fetches all text events since 24 hr ago in streaming manner
// const postIter = fetcher.allEventsIterator(
//     relayUrls, 
//     /* filter (kinds, authors, ids, tags) */
//     { kinds: [ 30399] },
//     /* time range filter (since, until) */
//     { since: nHoursAgo(10000) },
//     /* fetch options (optional) */
//     { skipFilterMatching: true }
// );
// for await (const ev of postIter) {
//     console.log(ev.content);
// }

if (!process.env.NOSTR_EVENT_KIND) {
    console.error("NOSTR_EVENT_KIND env var is not set");
    process.exit(1);
}
const eventKind = parseInt(process.env.NOSTR_EVENT_KIND, 10);
console.log("Fetching Nostr event kind (this can take a while):", eventKind);

// Resolve the lower time bound for the relay query.
// SINCE may be an ISO 8601 date/datetime (e.g. 2026-01-01) or a raw Unix
// timestamp in seconds. When unset we fall back to "effectively everything"
// so the fetch_nostr cron keeps receiving the full ride history.
const parseSince = (raw: string | undefined): number => {
    if (!raw || !raw.trim()) return nHoursAgo(10000);
    const trimmed = raw.trim();
    // An all-digit value is treated as a Unix timestamp in seconds.
    if (/^\d+$/.test(trimmed)) return parseInt(trimmed, 10);
    const ms = Date.parse(trimmed);
    if (Number.isNaN(ms)) {
        console.error(`SINCE="${raw}" is not a valid ISO date or Unix timestamp`);
        process.exit(1);
    }
    return Math.floor(ms / 1000);
};
const since = parseSince(process.env.SINCE);
console.log("Fetching rides created since:", new Date(since * 1000).toISOString());

// OPTIONAL pubkey allow-list. When set, the relay query is restricted to these
// author public keys (hex) via the Nostr "authors" filter, so the relays only
// return events signed by trusted submitters (server-side filtering). Unset
// means accept events from any author.
let pubkeys: string[] | undefined;
if (process.env.PUBKEYS?.trim()) {
    pubkeys = JSON.parse(process.env.PUBKEYS);
    console.log("Restricting query to pubkeys:", pubkeys);
}

// OPTIONAL source filter. Each ride records its origin app in the content
// "source" field; relays cannot filter on content, so this is applied
// client-side after fetching. Unset means keep rides from every source.
const sourceFilter = process.env.SOURCE?.trim() || undefined;
if (sourceFilter) console.log("Keeping only rides from source:", sourceFilter);

// Relay-side filter: event kind, plus the optional pubkey allow-list. Applying
// "authors" here means untrusted submitters are dropped before they ever reach
// us; the SOURCE filter is then applied client-side on what remains.
const relayFilter = pubkeys
    ? { kinds: [eventKind], authors: pubkeys }
    : { kinds: [eventKind] };

// Fetch from each relay individually to track which relays have each event
const eventMap = new Map<string, { event: any; relays: string[] }>();

for (const relay of relayUrls) {
    try {
        const events = await fetcher.fetchAllEvents(
            [relay],
            relayFilter,
            { since },
            { sort: true }
        );
        console.log(`${events.length} events from ${relay}`);
        for (const ev of events) {
            const existing = eventMap.get(ev.id);
            if (existing) {
                existing.relays.push(relay);
            } else {
                eventMap.set(ev.id, { event: ev, relays: [relay] });
            }
        }
    } catch (e) {
        console.error(`Failed to fetch from ${relay}:`, e);
    }
}

// Build final array sorted by created_at, with relay info attached
const allPosts = Array.from(eventMap.values())
    .sort((a, b) => a.event.created_at - b.event.created_at)
    .map(({ event, relays }) => ({ ...event, _relays: relays }));

console.log(allPosts.length, "unique posts fetched across", relayUrls.length, "relays");

// Apply the optional source filter. A ride's origin app is stored in the
// JSON-encoded "content" under "source"; relays cannot filter on content, so
// this happens client-side. The "d" tag (prefixed "<source>-...") is used as a
// fallback when the content is missing or cannot be parsed.
const posts = sourceFilter
    ? allPosts.filter(post => {
        let contentSource: string | undefined;
        try {
            contentSource = JSON.parse(post.content)?.source;
        } catch {
            contentSource = undefined;
        }
        if (contentSource) return contentSource === sourceFilter;
        const dTag = (post.tags as string[][]).find(t => t[0] === "d")?.[1];
        return dTag?.startsWith(`${sourceFilter}-`) ?? false;
    })
    : allPosts;

if (sourceFilter) {
    console.log(posts.length, `posts remain after filtering by source "${sourceFilter}"`);
}

// Write JSON to file (in this project directory, gitignored)
const jsonFile = join(__dirname, "..", "rides.json");
writeFileSync(jsonFile, JSON.stringify(posts, null, 2));
console.log("JSON written to", jsonFile);

// Prepare CSV header and rows
const header = ["id", "pubkey", "created_at", "content", "tags"];
const rows = posts.map(post => [
    post.id,
    post.pubkey,
    post.created_at,
    JSON.stringify(post.content),
    JSON.stringify(post.tags)
]);

// Combine header and rows into CSV string
const csv = [header, ...rows]
    .map(row => row.map(field => `"${String(field).replace(/"/g, '""')}"`).join(","))
    .join("\n");

// Write CSV to file (in this project directory, gitignored)
const csvFile = join(__dirname, "..", "rides.csv");
writeFileSync(csvFile, csv);
console.log("CSV written to", csvFile);

process.exit(0);
