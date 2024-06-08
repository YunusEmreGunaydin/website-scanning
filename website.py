import requests
from bs4 import BeautifulSoup


class LoggingHTTPAdapter(requests.adapters.HTTPAdapter):
    def send(self, request, **kwargs):
        response = super(LoggingHTTPAdapter, self).send(request, **kwargs)
        print(f"\nResponse:\nStatus Code: {response.status_code} {response.reason}\nHeaders: {response.headers}\n")
        return response


def check_platform_from_cookies(cookies, headers):
    platform = "Unknown"

    if 'PHPSESSID' in cookies:
        platform = 'PHP'
    elif 'ASP.NET_SessionId' in cookies:
        platform = 'ASP.NET'
    elif 'JSESSIONID' in cookies:
        platform = 'Java'
    elif any('express' in cookie.lower() for cookie in cookies):
        platform = 'Node.js (Express)'
    elif any('node' in cookie.lower() for cookie in cookies):
        platform = 'Node.js'

    x_powered_by = headers.get('X-Powered-By', '').lower()
    if 'express' in x_powered_by:
        platform = 'Node.js (Express)'
    elif 'next' in x_powered_by:
        platform = 'Node.js'

    return platform


def get_js_frameworks_and_libraries(script_tags):
    js_frameworks = set()
    js_libraries = set()

    for script in script_tags:
        if script.has_attr('src'):
            js_file_url = script['src']
            if 'jquery' in js_file_url.lower():
                js_libraries.add("jQuery")
            if 'react' in js_file_url.lower():
                js_frameworks.add("React")
            if 'vue' in js_file_url.lower():
                js_frameworks.add("Vue.js")
            if 'angular' in js_file_url.lower():
                js_frameworks.add("Angular")
            if 'd3' in js_file_url.lower():
                js_libraries.add("D3.js")
            if 'underscore' in js_file_url.lower():
                js_libraries.add("Underscore.js")
            if 'lodash' in js_file_url.lower():
                js_libraries.add("Lodash")

    return js_frameworks, js_libraries


def get_wordpress_theme(response_text):
    theme_name = None
    if 'wp-content/themes/' in response_text:
        start = response_text.find('wp-content/themes/') + len('wp-content/themes/')
        end = response_text.find('/', start)
        theme_name = response_text[start:end]
    return theme_name


def check_security_headers(headers):
    security_headers = {
        'Strict-Transport-Security': 'Strict-Transport-Security',
        'Content-Security-Policy': 'Content-Security-Policy',
        'X-Content-Type-Options': 'X-Content-Type-Options',
        'X-Frame-Options': 'X-Frame-Options',
        'X-XSS-Protection': 'X-XSS-Protection'
    }

    detected_headers = {key: headers.get(key) for key in security_headers.keys() if headers.get(key)}

    return detected_headers


def get_technology_versions(url):
    session = requests.Session()
    adapter = LoggingHTTPAdapter()
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    response = session.get(url)

    if response.status_code == 200:
        server_header = response.headers.get('Server')
        if server_header:
            print(f"Server: {server_header}")

        cookies = {cookie.name: cookie.value for cookie in response.cookies}
        headers = response.headers
        platform = check_platform_from_cookies(cookies, headers)

        soup = BeautifulSoup(response.content, 'html.parser')
        script_tags = soup.find_all('script')

        js_frameworks, js_libraries = get_js_frameworks_and_libraries(script_tags)

        wordpress_theme = get_wordpress_theme(response.text)

        if wordpress_theme:
            platform = 'PHP'

        node_version = None
        if 'node.js' in response.text.lower():
            node_version = 'Node.js'

        security_headers = check_security_headers(headers)

        return {
            'platform': platform,
            'node_version': node_version,
            'js_frameworks': js_frameworks,
            'js_libraries': js_libraries,
            'wordpress_theme': wordpress_theme,
            'security_headers': security_headers
        }
    else:
        return None


def print_intro():
    print('"""""""""""""""""""""""""""""""MRPYTHON0"""""""""""""""""""""""""""""""""')
    print()
    print()
    print('#########################################################################')


def main():
    print_intro()

    while True:
        url = input('Lütfen kontrol etmek istediğiniz URL\'yi girin: ')
        versions = get_technology_versions(url)
        if versions:
            print("Teknoloji sürümleri:")
            if versions['platform'] != "Unknown":
                print(f"Platform: {versions['platform']}")
            else:
                print("Platform belirlenemedi.")

            if versions['node_version']:
                print(f"Node.js: {versions['node_version']}")
            else:
                print("Node.js ile ilgili bilgi bulunamadı.")

            if versions['js_frameworks']:
                print("JavaScript frameworkleri:", versions['js_frameworks'])
            else:
                print("Herhangi bir JavaScript frameworkü bulunamadı.")

            if versions['js_libraries']:
                print("JavaScript kütüphaneleri:", versions['js_libraries'])
            else:
                print("Herhangi bir JavaScript kütüphanesi bulunamadı.")

            if versions['wordpress_theme']:
                print(f"WordPress Teması: {versions['wordpress_theme']}")
            else:
                print("WordPress teması bulunamadı.")

            if versions['security_headers']:
                print("Güvenlik Başlıkları:")
                for header, value in versions['security_headers'].items():
                    print(f"{header}: {value}")
            else:
                print("Herhangi bir güvenlik başlığı bulunamadı.")
        else:
            print("URL'ye erişilemedi veya herhangi bir teknoloji sürümü bulunamadı.")

        
        devam = input("Başka bir URL kontrol etmek ister misiniz? (Evet/Hayır): ")
        if devam.lower() != 'evet':
            break


if __name__ == "__main__":
    main()
