import reflex as rx
from typing import TypedDict, List, Union
import os
from supabase import create_client, Client
from credit_card_comparison_site.utils.issuer_icons import get_issuer_icon_url, GENERIC_BANK_ICON, get_default_icon_url


class IssuerInfo(TypedDict):
    id: str
    name: str
    logo_url: str
    website_url: str
    description: str


class CreditCardInfo(TypedDict):
    id: str
    name: str
    issuer_logo_url: str
    annual_fee: int
    rewards_general_spend_pct: float
    rewards_dining_pct: float
    rewards_travel_pct: float
    rewards_gas_pct: float
    rewards_grocery_pct: float
    welcome_bonus: str
    intro_apr_purchase: str
    intro_apr_balance_transfer: str
    regular_apr: str
    issuer: str  # Keep for backward compatibility
    issuer_id: str  # New foreign key
    other_notes: str


class CreditCardFeatureRow(TypedDict):
    feature_label: str
    values: List[Union[str, int, float, None]]


class CreditCardState(rx.State):
    all_cards: List[CreditCardInfo] = []
    all_issuers: List[IssuerInfo] = []
    selected_card_ids: List[str] = []
    MAX_COMPARISON_CARDS: int = 2
    MIN_COMPARISON_CARDS: int = 2
    search_name_query: str = ""
    issuer_filter_query: str = ""
    network_filter_query: str = ""

    @rx.event(background=True)
    async def load_initial_cards_from_db(self):
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_ANON_KEY")
        if not supabase_url or not supabase_key:
            print(
                "Supabase URL or Key not configured. Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
            )
            yield rx.toast(
                "Supabase connection details not found. Configure environment variables.",
                duration=5000,
            )
            async with self:
                self.all_cards = []
                self.all_issuers = []
            return
        try:
            supabase_client: Client = create_client(
                supabase_url, supabase_key
            )
            
            # Load issuers first
            issuers_response = (
                supabase_client.table("issuers")
                .select("*")
                .execute()
            )
            
            loaded_issuers_data = []
            if issuers_response.data:
                for item in issuers_response.data:
                    logo_url = item.get("logo_url", "/placeholder.svg")
                    issuer_name = item.get("name", "N/A")
                    
                    # Use Simple Icons as fallback if logo is placeholder or missing
                    if logo_url in ["/placeholder.svg", "", None, "CUSTOM_BANK_ICON"]:
                        logo_url = get_default_icon_url()
                    
                    issuer_info = IssuerInfo(
                        id=str(item.get("id", "")),
                        name=issuer_name,
                        logo_url=logo_url,
                        website_url=item.get("website_url", ""),
                        description=item.get("description", ""),
                    )
                    loaded_issuers_data.append(issuer_info)
            
            # Load credit cards with issuer information using proper JOIN syntax
            response = (
                supabase_client.table("credit_cards")
                .select("""
                    *,
                    issuers (
                        id,
                        name,
                        logo_url,
                        website_url,
                        description
                    )
                """)
                .execute()
            )
            
            loaded_cards_data = []
            if response.data:
                for item in response.data:
                    # Get issuer information from the joined data
                    issuer_data = item.get("issuers", {})
                    if issuer_data:
                        issuer_name = issuer_data.get("name", "N/A")
                        issuer_logo = issuer_data.get("logo_url", "/placeholder.svg")
                        
                        # Use Simple Icons as fallback if logo is placeholder or missing
                        if issuer_logo in ["/placeholder.svg", "", None, "CUSTOM_BANK_ICON"]:
                            issuer_logo = get_default_icon_url()
                    else:
                        # Fallback to the old issuer field if JOIN didn't work
                        issuer_name = item.get("issuer", "N/A")
                        issuer_logo = item.get("issuer_logo_url", "/placeholder.svg")
                        
                        # Use Simple Icons as fallback
                        if issuer_logo in ["/placeholder.svg", "", None, "CUSTOM_BANK_ICON"]:
                            issuer_logo = get_default_icon_url()
                    
                    card_info = CreditCardInfo(
                        id=str(item.get("id", "")),
                        name=item.get("name", "N/A"),
                        issuer_logo_url=issuer_logo,
                        annual_fee=int(
                            item.get("annual_fee", 0)
                        ),
                        rewards_general_spend_pct=float(
                            item.get(
                                "rewards_general_spend_pct",
                                0.0,
                            )
                        ),
                        rewards_dining_pct=float(
                            item.get(
                                "rewards_dining_pct", 0.0
                            )
                        ),
                        rewards_travel_pct=float(
                            item.get(
                                "rewards_travel_pct", 0.0
                            )
                        ),
                        rewards_gas_pct=float(
                            item.get("rewards_gas_pct", 0.0)
                        ),
                        rewards_grocery_pct=float(
                            item.get(
                                "rewards_grocery_pct", 0.0
                            )
                        ),
                        welcome_bonus=item.get(
                            "welcome_bonus", "N/A"
                        ),
                        intro_apr_purchase=item.get(
                            "intro_apr_purchase", "N/A"
                        ),
                        intro_apr_balance_transfer=item.get(
                            "intro_apr_balance_transfer",
                            "N/A",
                        ),
                        regular_apr=item.get(
                            "regular_apr", "N/A"
                        ),
                        issuer=issuer_name,  # For backward compatibility
                        issuer_id=str(item.get("issuer_id", "")),
                        other_notes=item.get(
                            "other_notes", "N/A"
                        ),
                    )
                    loaded_cards_data.append(card_info)
            
            async with self:
                self.all_cards = loaded_cards_data
                self.all_issuers = loaded_issuers_data
                
            if not loaded_cards_data:
                print(
                    "No cards loaded from Supabase, or table is empty."
                )
                yield rx.toast(
                    "No credit card data found in the database.",
                    duration=3000,
                )
        except Exception as e:
            print(f"Error fetching data from Supabase: {e}")
            yield rx.toast(
                "Error connecting to the database. Check logs.",
                duration=5000,
            )
            async with self:
                self.all_cards = []
                self.all_issuers = []

    @rx.event
    def set_search_name_query(self, query: str):
        self.search_name_query = query

    @rx.event
    def set_issuer_filter_query(self, query: str):
        self.issuer_filter_query = query

    @rx.event
    def set_network_filter_query(self, query: str):
        self.network_filter_query = query

    @rx.event
    def clear_all_filters(self):
        self.search_name_query = ""
        self.issuer_filter_query = ""
        self.network_filter_query = ""

    @rx.var
    def filtered_cards(self) -> List[CreditCardInfo]:
        cards_to_filter = self.all_cards
        if self.search_name_query:
            query = self.search_name_query.lower()
            cards_to_filter = [
                card
                for card in cards_to_filter
                if query in card["name"].lower()
            ]
        if self.issuer_filter_query:
            query = self.issuer_filter_query.lower()
            cards_to_filter = [
                card
                for card in cards_to_filter
                if query in card["issuer"].lower()
            ]
        if self.network_filter_query:
            query = self.network_filter_query.lower()
            cards_result = []
            for card in cards_to_filter:
                text_to_search = f"{card['name']} {card['other_notes']}".lower()
                if query in text_to_search:
                    cards_result.append(card)
            cards_to_filter = cards_result
        return cards_to_filter

    @rx.var
    def unique_issuers(self) -> List[str]:
        """Get list of unique issuer names for filter dropdown"""
        return sorted(list(set(issuer["name"] for issuer in self.all_issuers)))

    def _get_card_by_id(
        self, card_id: str
    ) -> CreditCardInfo | None:
        for card in self.all_cards:
            if card["id"] == card_id:
                return card
        return None

    def _get_issuer_by_id(
        self, issuer_id: str
    ) -> IssuerInfo | None:
        for issuer in self.all_issuers:
            if issuer["id"] == issuer_id:
                return issuer
        return None

    @rx.event
    def toggle_selection(self, card_id: str):
        if card_id in self.selected_card_ids:
            self.selected_card_ids.remove(card_id)
        elif (
            len(self.selected_card_ids)
            < self.MAX_COMPARISON_CARDS
        ):
            self.selected_card_ids.append(card_id)
            if (
                len(self.selected_card_ids)
                == self.MAX_COMPARISON_CARDS
            ):
                card_id_1 = self.selected_card_ids[0]
                card_id_2 = self.selected_card_ids[1]
                if (
                    self._get_card_by_id(card_id_1)
                    and self._get_card_by_id(card_id_2)
                    and (card_id_1 != card_id_2)
                ):
                    yield rx.redirect(
                        f"/compare/{card_id_1}/{card_id_2}"
                    )
                else:
                    self.selected_card_ids = [
                        id_
                        for id_ in self.selected_card_ids
                        if self._get_card_by_id(id_)
                    ]
                    if len(self.selected_card_ids) < 2:
                        if (
                            card_id
                            in self.selected_card_ids
                        ):
                            self.selected_card_ids.remove(
                                card_id
                            )
        else:
            yield rx.toast(
                f"You can select a maximum of {self.MAX_COMPARISON_CARDS} cards to compare.",
                duration=3000,
            )

    @rx.var
    def cards_to_compare(self) -> List[CreditCardInfo]:
        valid_selected_cards = []
        if not self.all_cards:
            return []
        for card_id in self.selected_card_ids:
            card = self._get_card_by_id(card_id)
            if card:
                valid_selected_cards.append(card)
        return valid_selected_cards

    @rx.var
    def is_selection_at_max_limit(self) -> bool:
        return (
            len(self.selected_card_ids)
            >= self.MAX_COMPARISON_CARDS
        )

    def _format_percentage(self, value: float) -> str:
        return f"{value}%" if value > 0 else "N/A"

    def _format_fee_display(self, value: int) -> str:
        return f"${value}" if value > 0 else "No Annual Fee"

    @rx.var
    def comparison_data_rows(
        self,
    ) -> List[CreditCardFeatureRow]:
        if (
            not self.cards_to_compare
            or len(self.cards_to_compare) == 0
        ):
            return []
        features_map: List[tuple[str, str]] = [
            ("Annual Fee", "annual_fee"),
            ("Welcome Bonus", "welcome_bonus"),
            (
                "General Spend Rewards",
                "rewards_general_spend_pct",
            ),
            ("Dining Rewards", "rewards_dining_pct"),
            ("Travel Rewards", "rewards_travel_pct"),
            ("Gas Rewards", "rewards_gas_pct"),
            ("Grocery Rewards", "rewards_grocery_pct"),
            ("Intro APR (Purchases)", "intro_apr_purchase"),
            (
                "Intro APR (Balance Transfer)",
                "intro_apr_balance_transfer",
            ),
            ("Regular APR", "regular_apr"),
            ("Issuer", "issuer"),
            ("Other Notes", "other_notes"),
        ]
        output_rows: List[CreditCardFeatureRow] = []
        for label, key in features_map:
            values_for_row: List[
                Union[str, int, float, None]
            ] = []
            for card in self.cards_to_compare:
                raw_value = card.get(key)
                if key == "annual_fee":
                    values_for_row.append(
                        self._format_fee_display(raw_value)
                    )
                elif "_pct" in key:
                    values_for_row.append(
                        self._format_percentage(raw_value)
                    )
                else:
                    values_for_row.append(
                        str(raw_value)
                        if raw_value is not None
                        else "N/A"
                    )
            output_rows.append(
                {
                    "feature_label": label,
                    "values": values_for_row,
                }
            )
        return output_rows

    @rx.var
    def param_card1_id(self) -> str:
        return self.router.page.params.get("card1_id", "")

    @rx.var
    def param_card2_id(self) -> str:
        return self.router.page.params.get("card2_id", "")

    @rx.event
    def load_cards_for_comparison(self):
        card_id1_from_url = self.param_card1_id
        card_id2_from_url = self.param_card2_id
        current_selection: List[str] = []
        card1_obj = self._get_card_by_id(card_id1_from_url)
        if card1_obj:
            current_selection.append(card1_obj["id"])
        card2_obj = self._get_card_by_id(card_id2_from_url)
        if (
            card2_obj
            and card2_obj["id"] != card_id1_from_url
        ):
            current_selection.append(card2_obj["id"])
        self.selected_card_ids = current_selection

    @rx.event
    def clear_selected_cards(self):
        self.selected_card_ids = []