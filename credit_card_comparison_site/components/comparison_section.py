import reflex as rx
from credit_card_comparison_site.states.credit_card_state import CreditCardState


def comparison_table() -> rx.Component:
    grid_class_for_two_cards = "grid grid-cols-[minmax(150px,_1fr)_repeat(2,_minmax(0,_2fr))]"
    return rx.el.section(
        rx.cond(
            CreditCardState.cards_to_compare.length()
            == CreditCardState.MIN_COMPARISON_CARDS,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        "Feature",
                        class_name="p-3 font-semibold text-gray-700 bg-gray-100 border-b border-r border-gray-300 text-left sticky left-0 z-10",
                    ),
                    rx.foreach(
                        CreditCardState.cards_to_compare,
                        lambda card: rx.el.div(
                            rx.el.img(
                                src=card["issuer_logo_url"],
                                alt=f"{card['name']} logo",
                                class_name="h-8 w-auto mx-auto mb-1",
                            ),
                            rx.el.span(
                                card["name"],
                                class_name="block text-center font-semibold text-indigo-700",
                            ),
                            class_name="p-3 bg-gray-100 border-b border-r border-gray-300",
                        ),
                    ),
                    class_name=grid_class_for_two_cards,
                ),
                rx.foreach(
                    CreditCardState.comparison_data_rows,
                    lambda feature_row: rx.el.div(
                        rx.el.div(
                            feature_row["feature_label"],
                            class_name="p-3 font-medium text-gray-600 bg-gray-50 border-b border-r border-gray-300 text-left sticky left-0 z-10",
                        ),
                        rx.foreach(
                            feature_row["values"],
                            lambda value: rx.el.div(
                                value.to_string(),
                                class_name="p-3 text-gray-700 border-b border-r border-gray-300 text-center",
                            ),
                        ),
                        class_name=grid_class_for_two_cards,
                    ),
                ),
                class_name="bg-white rounded-xl shadow-xl border border-gray-200 text-sm",
            ),
            rx.el.div(
                rx.el.p(
                    "Could not load comparison. Please ensure two valid and distinct cards were selected or provided in the URL.",
                    class_name="text-center text-red-600 py-10 bg-white rounded-xl shadow-md",
                ),
                class_name="px-4",
            ),
        ),
        class_name="py-8 overflow-x-auto p-1",
    )