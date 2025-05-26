import reflex as rx
from credit_card_comparison_site.states.credit_card_state import CreditCardState
from credit_card_comparison_site.components.navbar import navbar
from credit_card_comparison_site.components.comparison_section import (
    comparison_table,
)


def comparison_page() -> rx.Component:
    card1_name = rx.cond(
        CreditCardState.cards_to_compare.length() > 0,
        CreditCardState.cards_to_compare[0]["name"],
        "Card 1",
    )
    card2_name = rx.cond(
        CreditCardState.cards_to_compare.length() > 1,
        CreditCardState.cards_to_compare[1]["name"],
        "Card 2",
    )
    title_text = rx.el.h2(
        rx.el.span("Comparing "),
        rx.el.span(
            card1_name, class_name="text-indigo-600"
        ),
        rx.el.span(" vs "),
        rx.el.span(
            card2_name, class_name="text-indigo-600"
        ),
        class_name="text-3xl font-bold text-gray-800 mb-8 text-center py-6",
    )
    return rx.el.main(
        navbar(),
        rx.el.div(
            title_text,
            comparison_table(),
            class_name="container mx-auto px-4",
        ),
        class_name="font-['Inter'] bg-gray-50 min-h-screen",
    )