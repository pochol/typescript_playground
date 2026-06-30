"""Analiza zdjęcia growkitu modelem wizyjnym Claude.

Zwraca ustrukturyzowany JSON: etap wzrostu, % pokrycia grzybnią, wykrycie
pierwszych zawiązków (pinów), morfologia, kondensacja oraz odczyt temperatury
i wilgotności z wyświetlacza widocznego w boxie.
"""
from __future__ import annotations

import base64
import json
import os
from dataclasses import dataclass, asdict
from typing import Optional

import anthropic

# Schemat, który wymuszamy na modelu przez "tool use" (gwarantuje poprawny JSON).
ANALYSIS_TOOL = {
    "name": "record_growth_observation",
    "description": "Zapisz obserwację wzrostu grzybni ze zdjęcia growkitu.",
    "input_schema": {
        "type": "object",
        "properties": {
            "stage": {
                "type": "string",
                "enum": [
                    "inoculation",      # świeża inokulacja, brak grzybni
                    "colonization",     # grzybnia kolonizuje podłoże
                    "fully_colonized",  # podłoże w pełni zarośnięte (białe)
                    "pinning",          # pierwsze zawiązki / piny
                    "fruiting",         # owocniki rosną
                    "harvest_ready",    # gotowe do zbioru
                    "contamination",    # podejrzenie kontaminacji
                    "unknown",
                ],
                "description": "Aktualny etap rozwoju.",
            },
            "colonization_pct": {
                "type": "integer",
                "minimum": 0, "maximum": 100,
                "description": "Szacowany % pokrycia podłoża białą grzybnią.",
            },
            "pins_detected": {
                "type": "boolean",
                "description": "Czy widać pierwsze zawiązki/piny (start owocowania).",
            },
            "pin_count_estimate": {
                "type": "integer",
                "description": "Przybliżona liczba widocznych zawiązków/owocników (0 jeśli brak).",
            },
            "morphology": {
                "type": "string",
                "enum": ["none", "normal", "long_stems", "large_caps", "leggy_thin", "aborts"],
                "description": "Morfologia owocników: długie nóżki (long_stems) sugerują "
                               "za mało świeżego powietrza/CO2; large_caps = OK; leggy_thin = stres.",
            },
            "condensation": {
                "type": "string",
                "enum": ["none", "light", "heavy", "standing_water"],
                "description": "Kondensacja/krople na ściankach — heavy/standing_water = za dużo wilgoci.",
            },
            "temperature_c": {
                "type": ["number", "null"],
                "description": "Temperatura odczytana z wyświetlacza w boxie (°C), null jeśli nieczytelna.",
            },
            "humidity_pct": {
                "type": ["number", "null"],
                "description": "Wilgotność odczytana z wyświetlacza w boxie (%), null jeśli nieczytelna.",
            },
            "issues": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Wykryte problemy (np. 'za sucho', 'plamy kontaminacji', 'za mało światła').",
            },
            "recommendation": {
                "type": "string",
                "description": "Jedno krótkie zalecenie dla hodowcy na podstawie tego zdjęcia.",
            },
            "confidence": {
                "type": "number",
                "minimum": 0, "maximum": 1,
                "description": "Pewność oceny (0-1).",
            },
        },
        "required": [
            "stage", "colonization_pct", "pins_detected", "pin_count_estimate",
            "morphology", "condensation", "temperature_c", "humidity_pct",
            "issues", "recommendation", "confidence",
        ],
    },
}

SYSTEM_PROMPT = (
    "Jesteś ekspertem od uprawy grzybów (mykologia stosowana). Analizujesz "
    "zdjęcia growkitu zrobione na wprost pojemnika z grzybnią. W kadrze zwykle "
    "widoczny jest też wyświetlacz pokazujący wilgotność i temperaturę w boxie. "
    "Oceń stan grzybni rzetelnie i ostrożnie. Jeśli czegoś nie widać wyraźnie, "
    "zaznacz niską pewność i użyj null dla nieczytelnych odczytów. "
    "Zawsze wywołaj narzędzie record_growth_observation."
)


@dataclass
class Analysis:
    stage: str
    colonization_pct: int
    pins_detected: bool
    pin_count_estimate: int
    morphology: str
    condensation: str
    temperature_c: Optional[float]
    humidity_pct: Optional[float]
    issues: list
    recommendation: str
    confidence: float

    def to_dict(self) -> dict:
        return asdict(self)


def _media_type(path: str) -> str:
    p = path.lower()
    if p.endswith(".png"):
        return "image/png"
    if p.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"


class Analyzer:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key or os.environ["ANTHROPIC_API_KEY"])
        self.model = model or os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8")

    def analyze(self, image_path: str) -> Analysis:
        with open(image_path, "rb") as f:
            data = base64.standard_b64encode(f.read()).decode("ascii")

        resp = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=[ANALYSIS_TOOL],
            tool_choice={"type": "tool", "name": "record_growth_observation"},
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": _media_type(image_path),
                            "data": data,
                        },
                    },
                    {
                        "type": "text",
                        "text": "Przeanalizuj to zdjęcie growkitu i zapisz obserwację.",
                    },
                ],
            }],
        )

        for block in resp.content:
            if block.type == "tool_use" and block.name == "record_growth_observation":
                return Analysis(**block.input)
        raise RuntimeError("Model nie zwrócił oczekiwanego wywołania narzędzia.")


if __name__ == "__main__":
    import sys
    a = Analyzer()
    result = a.analyze(sys.argv[1])
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
