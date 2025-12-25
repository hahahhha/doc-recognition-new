from dataclasses import dataclass


@dataclass
class DataParseObject:
    field_title: str
    title_search_patterns: list[str]
    json_field_title: str