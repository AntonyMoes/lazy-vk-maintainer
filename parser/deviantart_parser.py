from typing import Tuple, List
from selectolax.parser import HTMLParser

from parser import Parser, ContentListRef, ContentRef


class DeviantArtParser(Parser):

    def parse_content_list(self, content_list: str) -> Tuple[List[ContentRef], List[ContentListRef]]:
        def ch(node, n):
            return list(node.iter())[n]
        
        rows = list(ch(ch(ch(ch(HTMLParser(content_list).css_first('#root'), 1), 2).child.child, 2), 1).child.iter())

        arts = [art for row in rows for art in row.child.iter()]
        art_urls = [ContentRef(art.child.child.child.attributes['href']) for art in arts]
        return art_urls, []

    def parse_content(self, content: str):
        return HTMLParser(content).css_first('main').css_first('img[aria-hidden]').attributes['src']

