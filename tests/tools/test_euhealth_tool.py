import os
import pytest
from tooluniverse.database_setup.hf.sync_hf import db_path_for_collection

EU_DB = db_path_for_collection("euhealth")

euhealth_present = os.path.exists(EU_DB)


@pytest.mark.euhealth
@pytest.mark.skipif(
    not euhealth_present,
    reason="euhealth.db not found; build or download before running",
)
def test_topic_smoke_and_shape():
    from tooluniverse.euhealth import tools_runtime as rt

    # confirm topics are exported
    assert isinstance(rt.TOPICS, dict) and len(rt.TOPICS) > 0

    # pick 2 topics deterministically
    names = sorted(rt.TOPICS.keys())[:2]
    for name in names:
        fn = getattr(rt, name)
        rows = fn(limit=3, method="hybrid")
        # shape check
        for r in rows:
            assert {"uuid", "title", "landing_page", "snippet"} <= set(r.keys())


@pytest.mark.euhealth
@pytest.mark.skipif(
    not euhealth_present,
    reason="euhealth.db not found; build or download before running",
)
def test_deepdive_minimal():
    from tooluniverse.euhealth import tools_runtime as rt

    seeds = rt.euhealthinfo_search_cancer(limit=1)
    if not seeds:
        pytest.skip("No seeds found in cancer search")
    uuid = seeds[0]["uuid"]

    out = rt.euhealthinfo_deepdive(uuids=[uuid], links_per=2, limit=1)
    assert isinstance(out, list) and len(out) >= 1
    entry = out[0]
    assert {"uuid", "title", "candidates"} <= set(entry.keys())
    # candidate shape (no 'preview' in the schema)
    if entry["candidates"]:
        c0 = entry["candidates"][0]
        assert {"url", "classification"} <= set(c0.keys())
