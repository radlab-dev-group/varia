#!/usr/bin/env python3
from pathlib import Path

from deck_content import populate
from deck_layout import Deck


if __name__ == '__main__':
    deck = Deck()
    populate(deck.title_slide, deck.section_slide, deck.content_slide, deck.code_slide,
             deck.two_col_slide, deck.architecture_slide)
    deck.file.save(Path(__file__).with_name('LLMRouter_DSS2026_tutorial.pptx'))