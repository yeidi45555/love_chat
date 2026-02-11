"""Utilidades para cuotas y unidades de uso. Escalable a imagen/audio."""


def estimate_text_units(text: str) -> int:
    """Estima unidades para texto. ~4 chars ≈ 1 token (OpenAI). 1 token = 1 unidad."""
    if not text:
        return 0
    return (len(text) + 3) // 4
