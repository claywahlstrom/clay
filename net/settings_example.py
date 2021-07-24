
"""
Net settings

"""

from clay.net.factories import PollenUrlBuilderFactory

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36',
    'Accept': 'text/html,text/plain,application/xhtml+xml,application/xml,application/_json;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Charset': 'Windows-1252,utf-8;q=0.7,*;q=0.3',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.8;q=0.5',
    'Connection': 'keep-alive'
}

_pollen_url_builder_factory = PollenUrlBuilderFactory()

pollen_source_urls = {
    98105: {
        'weather values': _pollen_url_builder_factory.weather \
            .with_geocode(47.654003, -122.309166) \
            .build(),
        'wu poll': _pollen_url_builder_factory.wunderground \
            .with_location('wa', 'seattle', 'KWASEATT446') \
            .with_query_params({'cm_ven': 'localwx_modpollen'}) \
            .build()
    },
    98684: {
        'weather values': _pollen_url_builder_factory.weather \
            .with_geocode(45.639816, -122.497902) \
            .build(),
        'wu poll': _pollen_url_builder_factory.wunderground \
            .with_location('wa', 'vancouver', 'KWAVANCO547') \
            .with_query_params({'cm_ven': 'localwx_modpollen'}) \
            .build()
    }
}

for url in pollen_source_urls:
    # weather text and values use the same endpoint
    pollen_source_urls[url]['weather text'] = pollen_source_urls[url]['weather values']
del url # remove variable from scope
