import reflex as rx


def navbar() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.div(
                rx.icon(
                    tag="credit_card",
                    class_name="h-8 w-8 text-indigo-600",
                ),
                rx.el.h1(
                    "Credit Card Comparator",
                    class_name="text-2xl font-bold text-gray-800",
                ),
                class_name="flex items-center gap-3",
            ),
            class_name="container px-6 py-4 flex justify-between items-center",
        ),
        class_name="bg-white shadow-md sticky top-0 z-50",
    )