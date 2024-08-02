import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Directory to save the PWA files
output_dir = "relieftrack_pwa"
os.makedirs(output_dir, exist_ok=True)

# Base URL
base_url = "https://relieftrack.glide.page/"

def download_file(url, folder):
    local_filename = os.path.join(folder, os.path.basename(urlparse(url).path))
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(local_filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
    return local_filename

# Fetch the website content
response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')

# Download and save HTML
with open(os.path.join(output_dir, 'index.html'), 'w', encoding='utf-8') as file:
    file.write(response.text)

# Parse and download CSS files
css_folder = os.path.join(output_dir, 'css')
os.makedirs(css_folder, exist_ok=True)
for link in soup.find_all('link', rel='stylesheet'):
    css_url = urljoin(base_url, link['href'])
    download_file(css_url, css_folder)

# Parse and download JS files
js_folder = os.path.join(output_dir, 'js')
os.makedirs(js_folder, exist_ok=True)
for script in soup.find_all('script', src=True):
    js_url = urljoin(base_url, script['src'])
    download_file(js_url, js_folder)

# Parse and download images
img_folder = os.path.join(output_dir, 'images')
os.makedirs(img_folder, exist_ok=True)
for img in soup.find_all('img'):
    img_url = urljoin(base_url, img['src'])
    download_file(img_url, img_folder)

# Create manifest.json
manifest = {
    "name": "ReliefTrack",
    "short_name": "ReliefTrack",
    "start_url": ".",
    "display": "standalone",
    "background_color": "#ffffff",
    "description": "Track relief efforts with ReliefTrack.",
    "icons": [
        {
            "src": "images/icon-192x192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "images/icon-512x512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

with open(os.path.join(output_dir, 'manifest.json'), 'w') as file:
    json.dump(manifest, file, indent=4)

# Create service worker
service_worker = """
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open('relieftrack-cache').then(function(cache) {
            return cache.addAll([
                '/',
                '/index.html',
                '/css/styles.css',
                '/js/scripts.js',
                '/images/icon-192x192.png',
                '/images/icon-512x512.png'
            ]);
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});
"""

with open(os.path.join(output_dir, 'service-worker.js'), 'w') as file:
    file.write(service_worker)

print(f"PWA files have been saved to {output_dir}")
