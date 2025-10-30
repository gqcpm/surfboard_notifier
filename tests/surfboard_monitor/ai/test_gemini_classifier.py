from unittest.mock import MagicMock, patch
from surfboard_monitor import GeminiClassifier


def test_gemini_classifier_init():
    """Test GeminiClassifier initialization."""
    classifier = GeminiClassifier()
    assert classifier.config is not None


def test_gemini_classifier_empty_listings():
    """Test GeminiClassifier with empty listings."""
    classifier = GeminiClassifier()
    result = classifier.classify_listings([])
    assert result == []


def test_gemini_filtering_disabled_returns_empty():
    classifier = GeminiClassifier()
    with patch.object(classifier, 'client', None):
        with patch.object(classifier.config, 'ENABLE_GEMINI_FILTERING', False):
            assert classifier.classify_listings([{'title': 'Any'}]) == []


@patch('surfboard_monitor.ai.gemini_classifier.genai.Client')
def test_gemini_classifier_parsing_and_filters(mock_client_cls):
    """Test classification parsing and safety filters/overrides."""
    # Build fake response text aligning with 4 listings
    # 1. LONGBOARD should be kept
    # 2. OTHER but title contains 'noserider' -> override to LONGBOARD
    # 3. SHORTBOARD -> filtered
    # 4. OTHER router -> filtered by keyword
    fake_response = MagicMock()
    fake_response.text = """
1. LONGBOARD
2. OTHER
3. SHORTBOARD
4. OTHER
""".strip()

    fake_models = MagicMock()
    fake_models.generate_content.return_value = fake_response

    fake_client = MagicMock()
    fake_client.models = fake_models
    mock_client_cls.return_value = fake_client

    classifier = GeminiClassifier()
    # Ensure client is set from our mock
    classifier.client = fake_client

    listings = [
        {'title': "10'0 Classic Log", 'description': '', 'price': '$500'},            # keep
        {'title': '7’6 Noserider special', 'description': '', 'price': '$400'},        # override keep
        {'title': "5'10 shortboard ripper", 'description': '', 'price': '$200'},      # filtered by SHORTBOARD
        {'title': 'High-speed router', 'description': '', 'price': '$50'},             # filtered by keyword
    ]

    kept = classifier.classify_listings(listings)
    assert len(kept) == 2
    assert any('Classic Log' in x.get('title', '') for x in kept)
    assert any('Noserider' in x.get('title', '') for x in kept)


@patch('surfboard_monitor.ai.gemini_classifier.genai.Client')
def test_gemini_classifier_else_drop_branch(mock_client_cls):
    """Cover the 'else' branch where non-longboard items are dropped (not continue)."""
    # Response marks second item as OTHER (not noserider), first as LONGBOARD
    fake_response = MagicMock()
    fake_response.text = """
1. LONGBOARD
2. OTHER
""".strip()
    fake_models = MagicMock()
    fake_models.generate_content.return_value = fake_response
    fake_client = MagicMock(models=fake_models)
    mock_client_cls.return_value = fake_client

    classifier = GeminiClassifier()
    classifier.client = fake_client

    listings = [
        {'title': "9'6 Log Board", 'description': '', 'price': '$700'},  # keep
        {'title': 'Generic item', 'description': 'not noserider', 'price': '$10'},  # else drop
    ]

    kept = classifier.classify_listings(listings)
    assert len(kept) == 1
    assert kept[0]['title'].startswith("9'6")


@patch('surfboard_monitor.ai.gemini_classifier.genai.Client', side_effect=Exception('init fail'))
def test_client_init_exception_sets_none(mock_client_cls):
    """Cover client init exception path (lines 24-25)."""
    classifier = GeminiClassifier()
    assert classifier.client is None


def test_no_api_key_warning_path():
    """Cover path where no API key is set (lines 26-27)."""
    with patch('surfboard_monitor.ai.gemini_classifier.Config') as MockCfg:
        cfg = MockCfg.return_value
        cfg.GEMINI_API_KEY = ''
        classifier = GeminiClassifier()
        assert classifier.client is None
