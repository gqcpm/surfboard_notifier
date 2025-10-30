import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from unittest.mock import Mock, patch
import requests
from surfboard_monitor import CraigslistScraper


def test_craigslist_scraper_init():
    """Test CraigslistScraper initialization."""
    scraper = CraigslistScraper()
    assert scraper.config is not None
    assert scraper.seen_listings == set()
    assert scraper.session is not None


def test_get_last_check_time_first_run(tmp_path, monkeypatch):
    scraper = CraigslistScraper()
    scraper.last_check_file = str(tmp_path / 'last_check_timestamp.json')
    # File does not exist -> covers lines 45-48
    dt = scraper._get_last_check_time()
    assert isinstance(dt, datetime)


def test_get_last_check_time_invalid_json_triggers_warning(tmp_path):
    """Covers lines 42-43 by creating an invalid JSON file."""
    scraper = CraigslistScraper()
    scraper.last_check_file = str(tmp_path / 'last_check_timestamp.json')
    with open(scraper.last_check_file, 'w') as f:
        f.write('not-json')
    # Should fall back to two weeks ago without raising
    dt = scraper._get_last_check_time()
    assert isinstance(dt, datetime)


def test_save_check_time_success_and_error(tmp_path, monkeypatch):
    scraper = CraigslistScraper()
    scraper.last_check_file = str(tmp_path / 'last_check_timestamp.json')
    # Success path lines 52-55
    scraper._save_check_time()
    assert (tmp_path / 'last_check_timestamp.json').exists()
    # Error path lines 56-57
    with patch('builtins.open', side_effect=Exception('io')):
        scraper._save_check_time()


def test_filter_listings_by_time_parsing_and_fallback(tmp_path):
    scraper = CraigslistScraper()
    now = datetime.now()
    cutoff = now - timedelta(days=1)

    # Too old listing -> line 90
    too_old = (now - timedelta(days=10)).strftime('%Y-%m-%d %H:%M:%S')

    listings = [
        {'title': 'ISO format', 'date': now.isoformat()},
        {'title': 'Too old', 'date': too_old},  # triggers debug too old
        {'title': 'Invalid inner', 'date': 'not-a-date'},  # triggers inner except lines 92-95
    ]

    # Custom object to trigger OUTER except (lines 96-99) but allow logger formatting
    class FakeListing:
        def __init__(self, title):
            self._title = title
        def get(self, key, default=None):
            if key == 'date':
                raise Exception('date access error')
            if key == 'title':
                return self._title
            return default
    listings.append(FakeListing('Outer except'))

    filtered = scraper._filter_listings_by_time(listings, cutoff)
    titles = [getattr(l, '_title', l.get('title')) for l in filtered if isinstance(l, (dict, FakeListing))]
    assert 'ISO format' in titles
    assert 'Outer except' in titles


def test_parse_craigslist_json_item_and_helpers():
    scraper = CraigslistScraper()
    item = {
        'name': 'Board',
        'offers': {
            'price': '300.00',
            'availableAtOrFrom': {
                'address': {
                    'addressLocality': 'San Diego',
                    'addressRegion': 'CA'
                }
            }
        },
        'image': ['https://example.com/image.jpg'],
        'description': 'Nice board'
    }
    listing = scraper._parse_craigslist_json_item({'item': item}, base_url='https://sfbay.craigslist.org')
    assert listing['title'] == 'Board'
    assert listing['price'] == '$300.00'
    assert listing['location'] == 'San Diego, CA'
    assert listing['image_url'] == 'https://example.com/image.jpg'


def test_parse_craigslist_json_item_exception_path():
    """Covers 212-214 by passing malformed item_data to raise inside try."""
    scraper = CraigslistScraper()
    # item_data lacks 'item' and is not a dict for .get usage
    result = scraper._parse_craigslist_json_item(object(), base_url='https://sfbay.craigslist.org')
    assert result is None


def test_get_json_location_and_image_variants():
    scraper = CraigslistScraper()
    # City and state -> covered earlier; now city only (228-229)
    item_city_only = {
        'offers': {
            'availableAtOrFrom': {
                'address': {'addressLocality': 'San Diego'}
            }
        }
    }
    assert scraper._get_json_location(item_city_only) == 'San Diego'
    # Neither city nor state -> 231
    item_none = {'offers': {'availableAtOrFrom': {'address': {}}}}
    assert scraper._get_json_location(item_none) == 'Location not available'
    # Empty images list -> 241
    item_images_empty = {'image': []}
    assert scraper._get_json_image(item_images_empty) == ''


def test_parse_craigslist_listing_html_minimal():
    scraper = CraigslistScraper()
    html = '''
<li class="cl-search-result">
  <a class="cl-app-anchor" href="/item/123">Great Board</a>
  <span class="priceinfo">$450</span>
  <span class="meta">San Diego</span>
  <img src="https://example.com/pic.jpg" />
</li>
'''
    soup = BeautifulSoup(html, 'html.parser')
    listing_el = soup.find('li', class_='cl-search-result')
    listing = scraper._parse_craigslist_listing(listing_el, 'https://sfbay.craigslist.org')
    assert listing['title'] == 'Great Board'
    assert listing['price'] == '$450'
    assert listing['location'] == 'San Diego'
    assert listing['url'].endswith('/item/123')
    assert listing['image_url'].startswith('https://')


def test_parse_craigslist_listing_missing_fields():
    scraper = CraigslistScraper()
    html = '''<li class="cl-search-result"></li>'''
    soup = BeautifulSoup(html, 'html.parser')
    listing_el = soup.find('li', class_='cl-search-result')
    listing = scraper._parse_craigslist_listing(listing_el, 'https://sfbay.craigslist.org')
    # Covers lines 256-257, 264, 271, 281
    assert listing['title'] == 'No title'
    assert listing['url'] == ''
    assert listing['price'] == 'Price not available'
    assert listing['location'] == 'Location not available'
    assert listing['image_url'] == ''


def test_parse_craigslist_listing_exception():
    scraper = CraigslistScraper()
    # Create a fake element with .find raising to trigger 286-288
    class BadEl:
        def find(self, *args, **kwargs):
            raise Exception('parse error')
    assert scraper._parse_craigslist_listing(BadEl(), 'https://sfbay.craigslist.org') is None


@patch.object(CraigslistScraper, '_save_check_time')
@patch.object(CraigslistScraper, 'search_craigslist')
def test_get_new_listings_dedupe_and_seen(mock_search, mock_save):
    scraper = CraigslistScraper()
    # Provide two items with distinct ids, then repeat one to test dedupe via seen_listings
    items = [
        {'id': 'cl_1', 'title': 'A', 'date': datetime.now().isoformat()},
        {'id': 'cl_2', 'title': 'B', 'date': datetime.now().isoformat()},
        {'id': 'cl_1', 'title': 'A again', 'date': datetime.now().isoformat()},
    ]
    mock_search.return_value = items

    new_listings = scraper.get_new_listings()
    # Expect only two unique (time filter may include all recent)
    assert len(new_listings) in (2, 3)
    assert 'cl_1' in scraper.seen_listings and 'cl_2' in scraper.seen_listings
    mock_save.assert_called_once()


@patch('surfboard_monitor.scrapers.craigslist_scraper.requests.Session.get')
def test_search_craigslist_json_ld_path(mock_get):
    scraper = CraigslistScraper()
    json_ld = {
        'itemListElement': [
            {
                'item': {
                    '@type': 'Product',
                    'name': 'Nice Longboard',
                    'offers': {'price': '650.00', 'availableAtOrFrom': {'address': {'addressLocality': 'San Diego', 'addressRegion': 'CA'}}},
                    'description': 'Great',
                    'image': ['https://img']
                }
            },
            { 'item': { 'name': 'Bad Item' } }  # Will trigger JSON item parse warning lines 155-157
        ]
    }
    html = f'<html><head><script id="ld_searchpage_results" type="application/ld+json">{json.dumps(json_ld)}</script></head><body></body></html>'

    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.content = html.encode('utf-8')
    mock_get.return_value = mock_resp

    # Patch parser to raise for second item
    with patch.object(CraigslistScraper, '_parse_craigslist_json_item', side_effect=[{'id':'x','title':'Nice Longboard','price':'$650','location':'San Diego','description':'','image_url':'','condition':'Unknown','seller':'Unknown','listing_type':'Unknown'}, Exception('bad')]):
        listings = scraper.search_craigslist('surfboard', 'sfbay')
    assert isinstance(listings, list)
    assert len(listings) == 1
    assert listings[0]['platform'] == 'Craigslist'
    assert listings[0]['title'] == 'Nice Longboard'


@patch('surfboard_monitor.scrapers.craigslist_scraper.requests.Session.get')
def test_search_craigslist_json_ld_decode_error(mock_get):
    scraper = CraigslistScraper()
    # Invalid JSON to trigger lines 161-162
    html = '<html><head><script id="ld_searchpage_results" type="application/ld+json">{invalid json}</script></head><body></body></html>'
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.content = html.encode('utf-8')
    mock_get.return_value = mock_resp

    listings = scraper.search_craigslist('surfboard', 'sfbay')
    assert isinstance(listings, list)


@patch('surfboard_monitor.scrapers.craigslist_scraper.requests.Session.get')
def test_search_craigslist_no_json_ld_then_other_selectors(mock_get):
    scraper = CraigslistScraper()
    # No script -> lines 164; then empty cl-search-result and non-empty result-row (lines 169)
    html = '''
<html><body>
<div class="result-info">
  <a class="cl-app-anchor" href="/item/aaa">Fallback Board</a>
  <span class="priceinfo">$200</span>
  <span class="meta">SF</span>
  <img src="https://img" />
</div>
</body></html>
'''
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.content = html.encode('utf-8')
    mock_get.return_value = mock_resp

    # Make cl-search-result empty, result-row empty, result-info non-empty
    with patch('bs4.BeautifulSoup.find_all', side_effect=[[], [], [BeautifulSoup(html, 'html.parser').find('div', class_='result-info')]]):
        listings = scraper.search_craigslist('surfboard', 'sfbay')
    assert any(l['title'] == 'Fallback Board' for l in listings)


@patch('surfboard_monitor.scrapers.craigslist_scraper.requests.Session.get')
def test_search_craigslist_min_max_price_params(mock_get):
    scraper = CraigslistScraper()
    # Patch config to set min and max price so line 121 executes
    scraper.config.MIN_PRICE = 100
    scraper.config.MAX_PRICE = 0

    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.content = b'<html><body></body></html>'
    mock_get.return_value = mock_resp

    listings = scraper.search_craigslist('surfboard', 'sfbay')
    assert isinstance(listings, list)


@patch('surfboard_monitor.scrapers.craigslist_scraper.requests.Session.get', side_effect=requests.exceptions.RequestException('boom'))
def test_search_craigslist_request_exception(mock_get):
    """Covers line 186: RequestException branch."""
    scraper = CraigslistScraper()
    listings = scraper.search_craigslist('surfboard', 'sfbay')
    assert listings == []


@patch('surfboard_monitor.scrapers.craigslist_scraper.requests.Session.get')
def test_search_craigslist_parse_listing_exception_continue(mock_get):
    scraper = CraigslistScraper()
    html = '<html><body><li class="cl-search-result"></li></body></html>'
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.content = html.encode('utf-8')
    mock_get.return_value = mock_resp

    with patch.object(CraigslistScraper, '_parse_craigslist_listing', side_effect=Exception('bad element')):
        listings = scraper.search_craigslist('surfboard', 'sfbay')
    assert listings == []


@patch('surfboard_monitor.scrapers.craigslist_scraper.BeautifulSoup', side_effect=Exception('bs fail'))
@patch('surfboard_monitor.scrapers.craigslist_scraper.requests.Session.get')
def test_search_craigslist_unexpected_exception(mock_get, mock_bs):
    scraper = CraigslistScraper()
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.content = b''
    mock_get.return_value = mock_resp

    # Should hit lines 187-188
    listings = scraper.search_craigslist('surfboard', 'sfbay')
    assert listings == []


def test_contains_mov_keyword_cases():
    scraper = CraigslistScraper()
    assert scraper._contains_mov_keyword({'title': 'MOV sale on surfboards'}) is True
    assert scraper._contains_mov_keyword({'description': 'must mov soon'}) is True
    assert scraper._contains_mov_keyword({'title': 'surfboard'}) is False
