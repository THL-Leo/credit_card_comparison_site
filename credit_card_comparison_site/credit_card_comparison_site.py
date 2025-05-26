import reflex as rx
from credit_card_comparison_site.states.credit_card_state import CreditCardState
from credit_card_comparison_site.components.navbar import navbar
from credit_card_comparison_site.components.credit_card_table import (
    credit_card_table_view,
)
from credit_card_comparison_site.pages.compare_page import comparison_page


def index() -> rx.Component:
    return rx.el.main(
        navbar(),
        rx.el.div(
            credit_card_table_view(),
            class_name="h-[calc(100vh-68px)]",
        ),
        class_name="font-['Inter'] bg-gray-50 min-h-screen",
    )


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(
            rel="preconnect",
            href="https://fonts.googleapis.com",
        ),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            crossorigin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(
    index,
    route="/",
    on_load=[
        CreditCardState.clear_selected_cards,
        CreditCardState.load_initial_cards_from_db,
        CreditCardState.clear_all_filters,
    ],
)
app.add_page(
    comparison_page,
    route="/compare/[card1_id]/[card2_id]",
    on_load=[
        CreditCardState.load_initial_cards_from_db,
        CreditCardState.load_cards_for_comparison,
    ],
)