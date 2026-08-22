import assert from "node:assert/strict";
import test from "node:test";

import { isDeletedBy, NostrEvent } from "./deletions.js";

const ride = (overrides: Partial<NostrEvent> = {}): NostrEvent => ({
    id: "ride-event-id",
    pubkey: "author-pubkey",
    created_at: 100,
    kind: 36820,
    tags: [["d", "source-ride:with-colon"]],
    ...overrides,
});

const deletion = (overrides: Partial<NostrEvent> = {}): NostrEvent => ({
    id: "deletion-event-id",
    pubkey: "author-pubkey",
    created_at: 200,
    kind: 5,
    tags: [["a", "36820:author-pubkey:source-ride:with-colon"], ["k", "36820"]],
    ...overrides,
});

test("an author can delete every older version by ride address", () => {
    assert.equal(isDeletedBy(ride(), deletion()), true);
});

test("an e tag deletes the exact event for compatibility", () => {
    assert.equal(
        isDeletedBy(ride(), deletion({ tags: [["e", "ride-event-id"], ["k", "36820"]] })),
        true,
    );
});

test("an e tag identifies the exact event despite author clock skew", () => {
    assert.equal(
        isDeletedBy(
            ride(),
            deletion({ created_at: 90, tags: [["e", "ride-event-id"]] }),
        ),
        true,
    );
});

test("another author cannot delete the ride", () => {
    assert.equal(isDeletedBy(ride(), deletion({ pubkey: "attacker-pubkey" })), false);
});

test("an address containing another author cannot delete the ride", () => {
    assert.equal(
        isDeletedBy(
            ride(),
            deletion({ tags: [["a", "36820:attacker-pubkey:source-ride:with-colon"]] }),
        ),
        false,
    );
});

test("a later republished version survives an older deletion request", () => {
    assert.equal(isDeletedBy(ride({ created_at: 300 }), deletion()), false);
});

test("an unrelated event id is not deleted", () => {
    assert.equal(
        isDeletedBy(ride(), deletion({ tags: [["e", "different-event-id"]] })),
        false,
    );
});
