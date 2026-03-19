# Test PWA (Progressive Web App) implementation
# Tests for manifest.json, sw.js, offline.html, icons, and meta tags

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestPWAManifest:
    """Test manifest.json accessibility and content"""
    
    def test_manifest_accessible(self):
        """GET /manifest.json returns HTTP 200"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ manifest.json accessible: {response.status_code}")
    
    def test_manifest_content_type(self):
        """manifest.json returns JSON content type"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        content_type = response.headers.get('Content-Type', '')
        assert 'application/json' in content_type, f"Expected JSON content type, got {content_type}"
        print(f"✅ manifest.json content type: {content_type}")
    
    def test_manifest_valid_json(self):
        """manifest.json is valid JSON"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        assert isinstance(data, dict), "manifest.json should be a JSON object"
        print(f"✅ manifest.json is valid JSON")
    
    def test_manifest_name_field(self):
        """manifest.json has name field"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        assert "name" in data, "manifest.json should have 'name' field"
        assert data["name"] == "Ranking Run Pró", f"Expected 'Ranking Run Pró', got {data['name']}"
        print(f"✅ manifest.json name: {data['name']}")
    
    def test_manifest_short_name(self):
        """manifest.json has short_name field"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        assert "short_name" in data, "manifest.json should have 'short_name' field"
        assert data["short_name"] == "RunPró", f"Expected 'RunPró', got {data['short_name']}"
        print(f"✅ manifest.json short_name: {data['short_name']}")
    
    def test_manifest_start_url(self):
        """manifest.json has start_url field"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        assert "start_url" in data, "manifest.json should have 'start_url' field"
        assert data["start_url"] == "/", f"Expected '/', got {data['start_url']}"
        print(f"✅ manifest.json start_url: {data['start_url']}")
    
    def test_manifest_display(self):
        """manifest.json has display field set to standalone"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        assert "display" in data, "manifest.json should have 'display' field"
        assert data["display"] == "standalone", f"Expected 'standalone', got {data['display']}"
        print(f"✅ manifest.json display: {data['display']}")
    
    def test_manifest_theme_color(self):
        """manifest.json has theme_color field"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        assert "theme_color" in data, "manifest.json should have 'theme_color' field"
        assert data["theme_color"] == "#10b981", f"Expected '#10b981', got {data['theme_color']}"
        print(f"✅ manifest.json theme_color: {data['theme_color']}")
    
    def test_manifest_icons_array(self):
        """manifest.json has icons array with 8 sizes"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        assert "icons" in data, "manifest.json should have 'icons' field"
        assert isinstance(data["icons"], list), "icons should be an array"
        assert len(data["icons"]) == 8, f"Expected 8 icons, got {len(data['icons'])}"
        
        expected_sizes = ["72x72", "96x96", "128x128", "144x144", "152x152", "192x192", "384x384", "512x512"]
        actual_sizes = [icon["sizes"] for icon in data["icons"]]
        for size in expected_sizes:
            assert size in actual_sizes, f"Missing icon size: {size}"
        print(f"✅ manifest.json icons: {len(data['icons'])} sizes configured")
    
    def test_manifest_shortcuts(self):
        """manifest.json has shortcuts configured (Ranking, Submeter, Feed)"""
        response = requests.get(f"{BASE_URL}/manifest.json")
        data = response.json()
        assert "shortcuts" in data, "manifest.json should have 'shortcuts' field"
        assert isinstance(data["shortcuts"], list), "shortcuts should be an array"
        assert len(data["shortcuts"]) == 3, f"Expected 3 shortcuts, got {len(data['shortcuts'])}"
        
        shortcut_names = [s["short_name"] for s in data["shortcuts"]]
        assert "Ranking" in shortcut_names, "Missing 'Ranking' shortcut"
        assert "Submeter" in shortcut_names, "Missing 'Submeter' shortcut"
        assert "Feed" in shortcut_names, "Missing 'Feed' shortcut"
        print(f"✅ manifest.json shortcuts: {shortcut_names}")


class TestServiceWorker:
    """Test Service Worker (sw.js) accessibility and content"""
    
    def test_sw_accessible(self):
        """GET /sw.js returns HTTP 200"""
        response = requests.get(f"{BASE_URL}/sw.js")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ sw.js accessible: {response.status_code}")
    
    def test_sw_content_type(self):
        """sw.js returns JavaScript content type"""
        response = requests.get(f"{BASE_URL}/sw.js")
        content_type = response.headers.get('Content-Type', '')
        assert 'javascript' in content_type.lower(), f"Expected JavaScript content type, got {content_type}"
        print(f"✅ sw.js content type: {content_type}")
    
    def test_sw_has_install_handler(self):
        """sw.js has install event handler"""
        response = requests.get(f"{BASE_URL}/sw.js")
        content = response.text
        assert "addEventListener('install'" in content or 'addEventListener("install"' in content, \
            "sw.js should have install event handler"
        print(f"✅ sw.js has install event handler")
    
    def test_sw_has_activate_handler(self):
        """sw.js has activate event handler"""
        response = requests.get(f"{BASE_URL}/sw.js")
        content = response.text
        assert "addEventListener('activate'" in content or 'addEventListener("activate"' in content, \
            "sw.js should have activate event handler"
        print(f"✅ sw.js has activate event handler")
    
    def test_sw_has_fetch_handler(self):
        """sw.js has fetch event handler"""
        response = requests.get(f"{BASE_URL}/sw.js")
        content = response.text
        assert "addEventListener('fetch'" in content or 'addEventListener("fetch"' in content, \
            "sw.js should have fetch event handler"
        print(f"✅ sw.js has fetch event handler")
    
    def test_sw_has_cache_strategy(self):
        """sw.js implements cache strategies"""
        response = requests.get(f"{BASE_URL}/sw.js")
        content = response.text
        assert "caches.open" in content, "sw.js should use Cache API"
        assert "networkFirstStrategy" in content or "cacheFirstStrategy" in content, \
            "sw.js should implement cache strategies"
        print(f"✅ sw.js implements cache strategies")


class TestOfflinePage:
    """Test offline.html accessibility"""
    
    def test_offline_page_accessible(self):
        """GET /offline.html returns HTTP 200"""
        response = requests.get(f"{BASE_URL}/offline.html")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ offline.html accessible: {response.status_code}")
    
    def test_offline_page_content_type(self):
        """offline.html returns HTML content type"""
        response = requests.get(f"{BASE_URL}/offline.html")
        content_type = response.headers.get('Content-Type', '')
        assert 'text/html' in content_type, f"Expected HTML content type, got {content_type}"
        print(f"✅ offline.html content type: {content_type}")
    
    def test_offline_page_has_content(self):
        """offline.html has appropriate offline content"""
        response = requests.get(f"{BASE_URL}/offline.html")
        content = response.text
        assert "offline" in content.lower(), "offline.html should mention offline state"
        assert "Ranking Run Pró" in content, "offline.html should have app title"
        print(f"✅ offline.html has offline content")


class TestPWAIcons:
    """Test PWA icons accessibility"""
    
    icon_sizes = ["72x72", "96x96", "128x128", "144x144", "152x152", "192x192", "384x384", "512x512"]
    
    @pytest.mark.parametrize("size", icon_sizes)
    def test_icon_accessible(self, size):
        """Test each icon size is accessible"""
        response = requests.get(f"{BASE_URL}/icons/icon-{size}.png")
        assert response.status_code == 200, f"Icon {size} not accessible: {response.status_code}"
        content_type = response.headers.get('Content-Type', '')
        assert 'image/png' in content_type, f"Expected PNG, got {content_type}"
        print(f"✅ icon-{size}.png accessible")


class TestIndexHTML:
    """Test index.html has PWA meta tags"""
    
    def test_index_html_accessible(self):
        """GET / returns HTTP 200"""
        response = requests.get(f"{BASE_URL}/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        print(f"✅ index.html accessible: {response.status_code}")
    
    def test_index_has_manifest_link(self):
        """index.html has link to manifest.json"""
        response = requests.get(f"{BASE_URL}/")
        content = response.text
        assert 'rel="manifest"' in content, "index.html should have manifest link"
        assert 'href="/manifest.json"' in content or "href='/manifest.json'" in content, \
            "manifest link should point to /manifest.json"
        print(f"✅ index.html has manifest link")
    
    def test_index_has_theme_color(self):
        """index.html has theme-color meta tag"""
        response = requests.get(f"{BASE_URL}/")
        content = response.text
        assert 'name="theme-color"' in content, "index.html should have theme-color meta"
        assert '#10b981' in content, "theme-color should be #10b981"
        print(f"✅ index.html has theme-color meta tag")
    
    def test_index_has_apple_web_app_capable(self):
        """index.html has apple-mobile-web-app-capable meta tag"""
        response = requests.get(f"{BASE_URL}/")
        content = response.text
        assert 'name="apple-mobile-web-app-capable"' in content, \
            "index.html should have apple-mobile-web-app-capable meta"
        print(f"✅ index.html has apple-mobile-web-app-capable meta tag")
    
    def test_index_has_sw_registration(self):
        """index.html has service worker registration script"""
        response = requests.get(f"{BASE_URL}/")
        content = response.text
        assert "serviceWorker.register" in content, \
            "index.html should have service worker registration"
        assert "/sw.js" in content, "SW registration should reference /sw.js"
        print(f"✅ index.html has service worker registration script")
    
    def test_index_has_apple_touch_icon(self):
        """index.html has apple-touch-icon link"""
        response = requests.get(f"{BASE_URL}/")
        content = response.text
        assert 'rel="apple-touch-icon"' in content, "index.html should have apple-touch-icon"
        print(f"✅ index.html has apple-touch-icon link")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
