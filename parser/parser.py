from abc import ABC, abstractmethod
from typing import NewType, Tuple, List

ContentListRef = NewType('ContentListRef', str)
ContentRef = NewType('ContentRef', str)


class Parser(ABC):
    @abstractmethod
    def parse_content_list(self, content_list: str) -> Tuple[List[ContentRef], List[ContentListRef]]:
        pass

    @abstractmethod
    def parse_content(self, content: str):
        pass
