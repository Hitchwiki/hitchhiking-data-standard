"""Every event this class creates must carry the Trustroots circle tags -- the
reference implementation every publish_*.py script (and any third-party
integrator copying this class) builds on, so a gap here silently propagates
everywhere. See research/trustroots-circles.md in the automation repo for the
full background: Hitchwiki/nostrhitch's separate hitchmap-dump mirror already
carries this label; this class historically did not, even though the live
maps.hitchwiki.org ride form uses the exact same tag pair once it does.

Standalone, network-free -- no real relay connection, no real keys, same
pattern as test_post_batch_pacing.py.

Run: .state/b82-venv/bin/python3 nostr/utils/test_trustroots_circle_tag.py
"""
import os
import sys

os.environ.setdefault("NSEC", "nsec1dummydummydummydummydummydummydummydummydummydummydumq7c4pj")
os.environ.setdefault("POST_TO_RELAYS", "true")
os.environ.setdefault("RELAYS", "['wss://fake.example']")

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "python"))

from post_hitchhiking_ride_to_nostr import HitchhikingDataStandardToNostrPoster  # noqa: E402
from hitchhiking_data_standard_pydantic_model import HitchhikingRecord  # noqa: E402

MINIMAL_RIDE = {
    "version": "1.0",
    "source": "test",
    "license": "odbl",
    "hitchhikers": [{"nickname": "Anonymous"}],
    "stops": [{"location": {"latitude": 52.5, "longitude": 13.4, "is_exact": True}}],
}


def make_poster():
    # __init__ decodes a real bech32 nsec via PrivateKey.from_nsec and opens
    # relay connections -- neither needed to test tag construction, and the
    # "dummy" nsec string above isn't valid bech32 (it exists only to satisfy
    # NSEC's presence at module import time). Same bypass test_post_batch_
    # pacing.py already uses, but with a real 32-byte key so event.sign()
    # (which create_event() itself calls) actually succeeds.
    poster = object.__new__(HitchhikingDataStandardToNostrPoster)
    poster.private_key_hex = "b" * 64
    poster.pubkey_hex = "a" * 64
    poster.event_kind = 36820
    return poster


def main():
    poster = make_poster()
    record = HitchhikingRecord.model_validate(MINIMAL_RIDE)
    event = poster.create_event(record)

    assert ["L", "trustroots-circle"] in event.tags, "missing the circle-label tag"
    assert ["l", "hitchhikers", "trustroots-circle"] in event.tags, "missing the circle-member tag"

    # Both tags travel together or not at all -- a mismatch (one present, one
    # missing) would be a real spec violation, not just an omission.
    has_label = any(t == ["L", "trustroots-circle"] for t in event.tags)
    has_member = any(t == ["l", "hitchhikers", "trustroots-circle"] for t in event.tags)
    assert has_label == has_member, "circle tags must be present together"

    # The existing d/geohash/published_at tags must still all be there -- this
    # change must be additive, not a replacement.
    assert any(t[0] == "d" for t in event.tags)
    assert sum(1 for t in event.tags if t[0] == "g") == 10
    assert any(t[0] == "published_at" for t in event.tags)

    print(f"PASS: {len(event.tags)} tags, circle label present, existing tags intact")


if __name__ == "__main__":
    main()
