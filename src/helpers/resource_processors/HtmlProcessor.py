from urllib.parse import urljoin, urlparse

from lxml import etree

from src.helpers.abstract_classes.AbstractMimeContentProcessor import AbstractMimeContentProcessor
from src.helpers.resource_obtainers.SimpleResourceObtainer import SimpleResourceObtainer


class HtmlProcessor(AbstractMimeContentProcessor):
    def __init__(self):
        accepted_types = ['text/html']
        resource_obtainer = SimpleResourceObtainer()  # FirefoxSeleniumResourceObtainer()
        super().__init__(accepted_types, resource_obtainer)

    def process_resource(self, resource: str, domain: str) -> tuple[list[str], bool]:
        resource = urljoin(domain, resource)

        # If the resource is not ending with '/' the join between resource path and relative urls doesn't work:
        # Ex: urljoin('http://site.com/page', 'song.mp3') = 'http://site.com/song.mp3' (which is wrong)
        # After appending '/': urljoin('http://site.com/page/', 'song.mp3') = 'http://site.com/page/song.mp3' (OK)
        if not resource.endswith('/'):
            resource += '/'

        domain = urlparse(domain)
        res = self._resource_obtainer.obtain_resource(resource)
        dom = etree.HTML(res.text)

        # Getting "a" elements that have "href" attribute
        elements = dom.xpath('//a[@href]')

        # Extracting the "href" attribute
        found_urls = list(map(lambda it: it.attrib['href'], elements))

        # If the URL is relative, joining it to the domain. If it is absolute it will be left untouched.
        # (no matter if it has the same domain or not)
        found_urls = list(map(lambda it: urljoin(resource, it), found_urls))

        # URL -> ParseResult
        found_urls = list(map(lambda it: urlparse(it), found_urls))

        # Filtering the domains that have the crawled domain
        found_urls = list(filter(lambda it: it.netloc == domain.netloc, found_urls))

        # ParseResult -> Relative path to resource
        found_urls = list(map(lambda it: it.path, found_urls))

        return found_urls, False
