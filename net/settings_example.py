
"""
Net settings

"""

from clay.net.factories import PollenUrlBuilderFactory

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
