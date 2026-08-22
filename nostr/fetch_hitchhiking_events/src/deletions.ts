export type NostrEvent = {
    id: string;
    pubkey: string;
    created_at: number;
    kind: number;
    tags: string[][];
};

const dTag = (event: NostrEvent): string | undefined =>
    event.tags.find(tag => tag[0] === "d")?.[1];

const addressMatches = (ride: NostrEvent, address: string): boolean => {
    const [kind, pubkey, ...identifierParts] = address.split(":");
    const identifier = identifierParts.join(":");
    return (
        kind === String(ride.kind) &&
        pubkey === ride.pubkey &&
        identifier === dTag(ride)
    );
};

export const isDeletedBy = (
    ride: NostrEvent,
    deletion: NostrEvent,
): boolean => {
    if (deletion.kind !== 5 || deletion.pubkey !== ride.pubkey) return false;

    return deletion.tags.some(tag => {
        if (tag[0] === "e") return tag[1] === ride.id;
        if (tag[0] === "a") {
            return (
                deletion.created_at >= ride.created_at &&
                addressMatches(ride, tag[1] ?? "")
            );
        }
        return false;
    });
};

export const isDeleted = (
    ride: NostrEvent,
    deletions: NostrEvent[],
): boolean => deletions.some(deletion => isDeletedBy(ride, deletion));
