# Standard for how to track hitchhiking rides

Applications which help hitchhikers track their trips should rely one a common data format such that records of rides can be shared easily and be used for the benefit of all.

This standard should reflect the diversity of hitchhikers such that it allows shallow records from the average or beginner hitchhiker as well as very in-depth and almost customized records from [super-hitchhikers](https://prino.neocities.org/miscellaneous/keeping-statistics).

This data format should reflect a single ride via hitchhiking. Building up on this it will be possible to connect rides to trips, judge the "hitchability" of certain frequently used spots as well as to gain deeper insights into state of hitchhiking.

This standard should also provide the single source of truth about how a hitchhiking ride NOSTR event should be tagged.

To describe the tags of this standard we took inspiration from [OSM tagging](https://wiki.openstreetmap.org/wiki/Tag:highway%3Dhitchhiking) and [NOSTR Standardized Tags](https://github.com/nostr-protocol/nips?tab=readme-ov-file#standardized-tags).

To establish this standard and to propose new features of hitchhiking rides that could be recorded the proposal process from [OSM](https://wiki.openstreetmap.org/wiki/Proposal_process) is adapted.

- create a new issue called "Proposal: xxx", stating which new dimension of hitchhiking you want to add to the already existing standard or how you would extend or change it to better capture the reality of hitchhiking in more detail.
- find a consensus about how to make the proposal happen - the discussion should be about the _how_ rather than the _if_ as applications will decide independently whether they and their user base will be able to record this new feature
- if a consensus is reached document it in `STANDARD.md`, another file named `object_name.md` might be used to define more complex objects.
- also adapt the python validation object in `python/python.py` to your change.
- close the proposal issue with a `accepted` comment and if a `object_name.md` add an `Approved` checkbox to it.
- inform applications like `hitchmap.com` about the extension/ change of the standard to make it come alife.

The sole creation of this standard provides an overview of the breadth and depth of dimensions of hitchhiking that stems from indivudual experiences and interviews with the broader community. 

## nostr

Nostr is a fairly recent standard for Notes and Other Stuff Transmitted by Relays.

The corresponding Nostr event
In `NOSTR.md`.


