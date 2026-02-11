from datetime import date


def _is_adult_from_birthdate(birthdate: date | None) -> bool:
    """Deriva mayoría de edad (18+) desde birthdate. Sin birthdate = no adulto (fail closed)."""
    if birthdate is None:
        return False
    today = date.today()
    age = today.year - birthdate.year
    if (today.month, today.day) < (birthdate.month, birthdate.day):
        age -= 1
    return age >= 18


class Guardrails:
    @staticmethod
    def validate_input(*, birthdate: date | None, user_text: str) -> None:
        is_adult = _is_adult_from_birthdate(birthdate)
        if not is_adult:
            raise ValueError("Age gate: must confirm 18+. Add birthdate to your profile and ensure you are 18+.")

        text = user_text.lower()

        # Bloqueo mínimo: menores (MVP)
        banned = [
            "minor", "underage", "child",
            "niña", "niño", "menor", "menor de edad"
        ]
        if any(w in text for w in banned):
            raise ValueError("Refused: content involving minors is not allowed.")
