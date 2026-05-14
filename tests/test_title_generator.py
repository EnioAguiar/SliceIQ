# tests/test_title_generator.py
import pytest
from core.title_generator import TitleGenerator, TEMPLATES

def test_templates_loaded():
    assert "chamativo" in TEMPLATES
    assert "informativo" in TEMPLATES
    assert len(TEMPLATES["chamativo"]) > 0

def test_generate_auto_mode():
    gen = TitleGenerator(mode="auto", config={})
    title = gen.generate_title(
        highlight_text="Discussão sobre áudio vazado de Bolsonaro",
        start=0.0,
        end=45.0,
        duration=45.0
    )
    assert isinstance(title, str)
    assert len(title) <= 50

def test_generate_custom_mode():
    gen = TitleGenerator(
        mode="custom",
        config={"prompt": "Título: {text}"}
    )
    title = gen.generate_title(
        highlight_text="Flávio e Vorcaro",
        start=800.0,
        end=862.0,
        duration=62.0
    )
    assert isinstance(title, str)