import reflex as rx
from credit_card_comparison_site.states.credit_card_state import (
    CreditCardState,
    CreditCardInfo,
)


def filter_sidebar_component() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Filters",
            class_name="text-xl font-semibold mb-6 text-gray-700",
        ),
        rx.el.div(
            rx.el.label(
                "Brand (Issuer)",
                class_name="block text-sm font-medium text-gray-600 mb-1",
            ),
            rx.el.input(
                placeholder="e.g., Chase, Amex",
                on_change=CreditCardState.set_issuer_filter_query.debounce(
                    500
                ),
                class_name="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
            ),
            class_name="mb-4",
        ),
        # rx.el.div(
        #     rx.el.label(
        #         "Card Network / Features",
        #         class_name="block text-sm font-medium text-gray-600 mb-1",
        #     ),
        #     rx.el.input(
        #         placeholder="e.g., Visa, Mastercard, travel",
        #         on_change=CreditCardState.set_network_filter_query.debounce(
        #             500
        #         ),
        #         class_name="w-full p-2 border border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm",
        #     ),
        #     class_name="mb-4",
        # ),
    )


def table_row_component(
    card: CreditCardInfo,
) -> rx.Component:
    is_selected = (
        CreditCardState.selected_card_ids.contains(
            card["id"]
        )
    )
    is_disabled_for_selection = rx.cond(
        is_selected,
        False,
        CreditCardState.is_selection_at_max_limit,
    )
    return rx.el.tr(
        rx.el.td(
            rx.el.img(
                src=card["issuer_logo_url"],
                alt=f"{card['issuer']} logo",
                class_name="h-8 w-8 object-contain rounded",
            ),
            class_name="p-3 border-b border-gray-200 align-middle",
        ),
        rx.el.td(
            card["name"],
            class_name="p-3 border-b border-gray-200 text-sm text-gray-800 font-medium align-middle",
        ),
        rx.el.td(
            card["issuer"],
            class_name="p-3 border-b border-gray-200 text-sm text-gray-600 align-middle",
        ),
        rx.el.td(
            rx.cond(
                card["annual_fee"] > 0,
                "$" + card["annual_fee"].to_string(),
                "No Annual Fee",
            ),
            class_name="p-3 border-b border-gray-200 text-sm text-gray-600 align-middle",
        ),
        rx.el.td(
            rx.el.button(
                rx.cond(is_selected, "Selected", "Select"),
                on_click=lambda: CreditCardState.toggle_selection(
                    card["id"]
                ),
                class_name=rx.cond(
                    is_selected,
                    "px-4 py-1.5 bg-red-500 text-white rounded-md hover:bg-red-600 text-xs font-semibold transition-colors",
                    rx.cond(
                        CreditCardState.is_selection_at_max_limit,
                        "px-4 py-1.5 bg-gray-300 text-gray-500 rounded-md cursor-not-allowed text-xs font-semibold transition-colors",
                        "px-4 py-1.5 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 text-xs font-semibold transition-colors",
                    ),
                ),
                disabled=is_disabled_for_selection,
            ),
            class_name="p-3 border-b border-gray-200 text-center align-middle",
        ),
        class_name=rx.cond(
            is_selected,
            "bg-indigo-50 hover:bg-indigo-100 transition-colors",
            "hover:bg-gray-50 transition-colors",
        ),
    )


def actual_table_component() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Available Credit Cards",
                class_name="text-xl font-semibold text-gray-700",
            ),
            rx.el.span(
                CreditCardState.filtered_cards.length().to_string()
                + " cards found",
                class_name="text-sm text-gray-500",
            ),
            class_name="flex justify-between items-center mb-4",
        ),
        rx.el.input(
            placeholder="Search by card name...",
            on_change=CreditCardState.set_search_name_query.debounce(
                500
            ),
            class_name="w-full p-3 mb-6 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white text-gray-900 placeholder-gray-400",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Issuer",
                            class_name="p-3 text-left text-xs font-semibold text-gray-500 bg-gray-100 uppercase tracking-wider sticky top-0",
                        ),
                        rx.el.th(
                            "Card Name",
                            class_name="p-3 text-left text-xs font-semibold text-gray-500 bg-gray-100 uppercase tracking-wider sticky top-0",
                        ),
                        rx.el.th(
                            "Bank",
                            class_name="p-3 text-left text-xs font-semibold text-gray-500 bg-gray-100 uppercase tracking-wider sticky top-0",
                        ),
                        rx.el.th(
                            "Annual Fee",
                            class_name="p-3 text-left text-xs font-semibold text-gray-500 bg-gray-100 uppercase tracking-wider sticky top-0",
                        ),
                        rx.el.th(
                            "Action",
                            class_name="p-3 text-center text-xs font-semibold text-gray-500 bg-gray-100 uppercase tracking-wider sticky top-0",
                        ),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        CreditCardState.filtered_cards,
                        table_row_component,
                    )
                ),
                class_name="w-full",
            ),
            class_name="overflow-x-auto overflow-y-auto max-h-[calc(100vh-300px)] bg-white rounded-lg border border-gray-200 shadow-md",
        ),
        rx.cond(
            (CreditCardState.selected_card_ids.length() > 0)
            & (
                CreditCardState.selected_card_ids.length()
                < CreditCardState.MAX_COMPARISON_CARDS
            ),
            rx.el.p(
                "Select "
                + (
                    CreditCardState.MAX_COMPARISON_CARDS
                    - CreditCardState.selected_card_ids.length()
                ).to_string()
                + " more card(s) to compare.",
                class_name="text-center text-indigo-600 mt-4 py-2 font-medium",
            ),
            rx.fragment(),
        ),
    )


def credit_card_table_view() -> rx.Component:
    return rx.el.div(
        rx.el.aside(
            filter_sidebar_component(),
            class_name="w-72 p-6 bg-white border-r border-gray-200 shadow-sm space-y-6 shrink-0",
        ),
        rx.el.div(
            actual_table_component(),
            class_name="flex-1 p-6 overflow-auto",
        ),
        class_name="flex h-[calc(100vh-var(--navbar-height,80px))] bg-gray-50",
    )