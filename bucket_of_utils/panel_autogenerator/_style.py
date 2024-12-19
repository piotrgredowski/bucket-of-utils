import dataclasses
import enum


class TitleType(enum.StrEnum):
    CAPITALIZED = enum.auto()
    CAPITALIZED_FIRST_WORD = enum.auto()
    UPPER_CASED = enum.auto()
    LOWER_CASED = enum.auto()


@dataclasses.dataclass
class Style:
    title: TitleType = TitleType.CAPITALIZED

    def format_title(self, function_name: str):
        def _split(word: str) -> list[str]:
            return word.split("_")

        def _capitalize(function_name: str) -> list[str]:
            return [w.capitalize() for w in _split(function_name)]

        def _capitalize_first_word(function_name: str) -> list[str]:
            words = _split(function_name)
            return [words[0].capitalize(), *words[1:]]

        def _lower(function_name: str) -> list[str]:
            return [w.lower() for w in _split(function_name)]

        def _upper(function_name: str) -> list[str]:
            return [w.upper() for w in _split(function_name)]

        title_formatters = {
            TitleType.CAPITALIZED: _capitalize,
            TitleType.CAPITALIZED_FIRST_WORD: _capitalize_first_word,
            TitleType.UPPER_CASED: _upper,
            TitleType.LOWER_CASED: _lower,
        }

        formatter = title_formatters.get(self.title, _capitalize)

        return " ".join(formatter(function_name))
