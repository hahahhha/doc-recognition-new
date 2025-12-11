from dataclasses import dataclass


@dataclass
class ParseDataObject:
    field_title: str
    title_search_pattern: str
    json_field_title: str