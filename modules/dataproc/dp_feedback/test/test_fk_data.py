import random
import pytest
from datetime import datetime, timedelta
from modules.dataproc.dp_feedback.src.utils.fk_data import FkFeedback


@pytest.fixture
def seeded_fk():
    random.seed(0)
    fk = FkFeedback(country="en_US")
    fk.fake.seed_instance(0)
    return fk


@pytest.mark.parametrize(
    "rating,expected_start,expected_end",
    [
        (1, "I regret this purchase completely.", "I will never buy from this company again."),
        (2, "Not what I expected.", "The quality was much lower than advertised."),
        (3, "It's okay, but could be better.", "I might consider buying again if improvements are made."),
        (4, "Pretty good overall.", "I'm satisfied with my purchase."),
        (5, "Absolutely wonderful!", "Exceeded all my expectations!"),
        (6, "Absolutely wonderful!", "Exceeded all my expectations!"),
    ],
)
def test_generate_comment_phrases(seeded_fk, rating, expected_start, expected_end):
    comment = seeded_fk.generate_comment(rating)
    assert comment.startswith(expected_start)
    assert comment.endswith(expected_end)


def test_generate_fake_feedbacks_basic_structure(seeded_fk):
    n = 20
    feedbacks = seeded_fk.generate_fake_feedbacks(n)
    assert isinstance(feedbacks, list)
    assert len(feedbacks) == n

    required_keys = {
        "feedback_id",
        "type",
        "rating",
        "title",
        "comment",
        "fb_date",
        "verified_purchase",
        "would_recommend",
        "company_response",
        "response_date",
        "product_name",
        "brand_name",
        "size",
        "color",
    }

    now = datetime.now()
    min_date = now - timedelta(days=180)

    ids = set()
    for fb in feedbacks:
        # keys present
        assert required_keys.issubset(fb.keys())

        # id uniqueness and prefix
        assert isinstance(fb["feedback_id"], str) and fb["feedback_id"].startswith("FB##")
        ids.add(fb["feedback_id"])

        # rating bounds
        assert isinstance(fb["rating"], int) and 1 <= fb["rating"] <= 5

        # types and basic strings
        assert isinstance(fb["type"], str) and fb["type"] in seeded_fk.feedback_types
        assert isinstance(fb["title"], str) and "experience with the" in fb["title"]
        assert isinstance(fb["comment"], str) and len(fb["comment"]) > 0

        # booleans
        assert isinstance(fb["verified_purchase"], bool)
        assert isinstance(fb["would_recommend"], bool)

        # fb_date window
        assert isinstance(fb["fb_date"], datetime)
        assert min_date <= fb["fb_date"] <= now

        # response_date range if present
        if fb["response_date"] is not None:
            assert isinstance(fb["response_date"], datetime)
            assert fb["fb_date"] < fb["response_date"] <= fb["fb_date"] + timedelta(days=7)

    assert len(ids) == n


def test_product_fields_with_clothing_category_have_size_and_color(seeded_fk):
    # Force only "Product" types for deterministic checks
    seeded_fk.feedback_types = ["Product"]
    random.seed(1)
    seeded_fk.fake.seed_instance(1)

    feedbacks = seeded_fk.generate_fake_feedbacks(10, category="Clothing")
    sizes_allowed = {"S", "M", "L", "XL", "One Size"}

    for fb in feedbacks:
        assert fb["type"] == "Product"
        # size and color should be populated for Clothing
        assert fb["size"] in sizes_allowed
        assert isinstance(fb["color"], str) and len(fb["color"]) > 0
        # product_name and brand_name remain None per current implementation
        assert fb["product_name"] is None
        assert fb["brand_name"] is None


def test_product_fields_with_none_category_are_none(seeded_fk):
    # Force only "Product" types for deterministic checks
    seeded_fk.feedback_types = ["Product"]
    random.seed(2)
    seeded_fk.fake.seed_instance(2)

    feedbacks = seeded_fk.generate_fake_feedbacks(8, category=None)
    for fb in feedbacks:
        assert fb["type"] == "Product"
        assert fb["size"] is None
        assert fb["color"] is None


def test_non_product_never_sets_size_or_color_even_with_clothing(seeded_fk):
    # Force only non-Product types
    seeded_fk.feedback_types = ["Service", "Support", "Delivery", "Website/App"]
    random.seed(3)
    seeded_fk.fake.seed_instance(3)

    feedbacks = seeded_fk.generate_fake_feedbacks(12, category="Clothing")
    for fb in feedbacks:
        assert fb["type"] in seeded_fk.feedback_types and fb["type"] != "Product"
        assert fb["size"] is None
        assert fb["color"] is None