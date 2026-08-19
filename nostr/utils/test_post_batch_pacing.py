"""Standalone, network-free check of post_batch's pacing and OK-notice
accounting (issue #61) -- no real relay connection, no real keys.

Run: .state/b82-venv/bin/python3 nostr/utils/test_post_batch_pacing.py
"""
import os
import sys
import time

os.environ.setdefault("NSEC", "nsec1dummydummydummydummydummydummydummydummydummydummydumq7c4pj")
os.environ.setdefault("POST_TO_RELAYS", "true")
os.environ.setdefault("RELAYS", "['wss://fake.example']")

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "python"))

from post_hitchhiking_ride_to_nostr import HitchhikingDataStandardToNostrPoster  # noqa: E402


class FakeOkNotice:
    def __init__(self, url, ok, message=""):
        self.url = url
        self.ok = ok
        self.message = message


class FakeMessagePool:
    def __init__(self, pattern):
        # pattern: list of bool, cycled, one entry consumed per publish call
        self.pattern = pattern
        self.i = 0
        self.pending = []

    def queue_next(self):
        ok = self.pattern[self.i % len(self.pattern)]
        self.i += 1
        self.pending.append(FakeOkNotice("wss://fake.example", ok, "" if ok else "rate-limited"))

    def has_ok_notices(self):
        return bool(self.pending)

    def get_ok_notice(self):
        return self.pending.pop(0)


class FakeRelayManager:
    def __init__(self, pattern):
        self.message_pool = FakeMessagePool(pattern)
        self.published = 0

    def publish_event(self, event):
        self.published += 1

    def run_sync(self):
        # Simulate the relay answering the most recently published event.
        if self.message_pool.i < self.published:
            self.message_pool.queue_next()


def make_poster(pattern):
    poster = object.__new__(HitchhikingDataStandardToNostrPoster)
    poster.pubkey_hex = "a" * 64
    poster.private_key_hex = "b" * 64
    poster.event_kind = 36820
    poster.relay_manager = FakeRelayManager(pattern)
    poster.create_event = lambda record: object()  # bypass real event construction
    return poster


def test_pacing_respects_rate():
    poster = make_poster(pattern=[True])
    n = 12
    events_per_sec = 6.0  # loose enough that CI/dev-machine jitter won't false-fail
    start = time.monotonic()
    poster.post_batch([f"record-{i}" for i in range(n)], batch_size=5, events_per_sec=events_per_sec)
    elapsed = time.monotonic() - start
    min_expected = (n / events_per_sec) * 0.8  # tolerance for scheduling jitter
    assert elapsed >= min_expected, f"ran too fast: {elapsed:.2f}s for {n} events at {events_per_sec}/sec (min {min_expected:.2f}s)"
    print(f"PASS  pacing: {n} events in {elapsed:.2f}s at target {events_per_sec}/sec")


def test_counts_confirmed_and_rejected():
    # 1 accepted, 1 rejected, repeating -- exercises both branches of the OK check.
    poster = make_poster(pattern=[True, False])
    n = 10
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        poster.post_batch([f"record-{i}" for i in range(n)], batch_size=n, events_per_sec=50.0)
    out = buf.getvalue()
    assert "5 confirmed" in out, out
    assert "5 rejected" in out, out
    assert "0 unconfirmed" in out, out
    print("PASS  counts: 5 confirmed / 5 rejected / 0 unconfirmed correctly split")


def test_unconfirmed_when_relay_silent():
    # Relay never answers at all -- every event should land in "unconfirmed",
    # not silently counted as success (the old code's bug).
    class SilentRelayManager(FakeRelayManager):
        def run_sync(self):
            pass  # never produces an OK notice

    poster = make_poster(pattern=[True])
    poster.relay_manager = SilentRelayManager(pattern=[True])
    n = 4
    import io
    import contextlib

    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        poster.post_batch([f"record-{i}" for i in range(n)], batch_size=n, events_per_sec=50.0)
    out = buf.getvalue()
    assert "0 confirmed" in out, out
    assert "4 unconfirmed" in out, out
    print("PASS  silent relay: all 4 correctly counted unconfirmed, not assumed successful")


if __name__ == "__main__":
    test_pacing_respects_rate()
    test_counts_confirmed_and_rejected()
    test_unconfirmed_when_relay_silent()
    print("3/3 passed")
