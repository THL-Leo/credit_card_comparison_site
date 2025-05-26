import reflex as rx
from credit_card_comparison_site.states.credit_card_state import (
    CreditCardState,
    CreditCardInfo,
)


def card_option_ui(card: CreditCardInfo) -> rx.Component:
    is_selected = (
        CreditCardState.selected_card_ids.contains(
            card["id"]
        )
    )
    is_disabled = rx.cond(
        is_selected,
        False,
        CreditCardState.is_selection_at_max_limit,
    )
    return rx.el.div(
        rx.el.div(
            rx.el.img(
                src=card["issuer_logo_url"],
                alt=f"{card['issuer']} logo",
                class_name="h-16 w-16 object-contain mx-auto mb-2",
            ),
            rx.el.p(
                card["issuer"],
                class_name="text-sm text-gray-500 text-center",
            ),
            class_name="pt-4 pb-2 bg-gray-50 rounded-t-xl",
        ),
        rx.el.div(
            rx.el.h3(
                card["name"],
                class_name="text-lg font-semibold text-gray-800 mb-1",
            ),
            rx.el.p(
                f"Annual Fee: ${card['annual_fee']}",
                class_name="text-sm text-gray-600 mb-3",
            ),
            rx.el.button(
                rx.cond(
                    is_selected,
                    "Selected",
                    "Select to Compare",
                ),
                on_click=lambda: CreditCardState.toggle_selection(
                    card["id"]
                ),
                class_name=rx.cond(
                    is_selected,
                    "w-full py-2 px-4 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm font-medium",
                    rx.cond(
                        CreditCardState.is_selection_at_max_limit,
                        "w-full py-2 px-4 bg-gray-300 text-gray-500 rounded-lg cursor-not-allowed text-sm font-medium",
                        "w-full py-2 px-4 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors text-sm font-medium",
                    ),
                ),
                disabled=is_disabled,
            ),
            class_name="p-4",
        ),
        class_name="bg-white rounded-xl shadow-lg overflow-hidden border border-gray-200 hover:shadow-2xl transition-shadow duration-300",
    )


def card_selection_area() -> rx.Component:
    return rx.el.section(
        rx.el.h2(
            "Select Two Credit Cards to Compare",
            class_name="text-2xl font-semibold text-gray-700 mb-6 text-center",
        ),
        rx.el.div(
            rx.foreach(
                CreditCardState.all_cards, card_option_ui
            ),
            class_name="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6",
        ),
        rx.cond(
            (CreditCardState.selected_card_ids.length() > 0)
            & (
                CreditCardState.selected_card_ids.length()
                < CreditCardState.MAX_COMPARISON_CARDS
            ),
            rx.el.p(
                f"Select {CreditCardState.MAX_COMPARISON_CARDS - CreditCardState.selected_card_ids.length()} more card(s) to compare.",
                class_name="text-center text-indigo-600 mt-4 py-2",
            ),
            rx.fragment(),
        ),
        class_name="py-8 px-4",
    )