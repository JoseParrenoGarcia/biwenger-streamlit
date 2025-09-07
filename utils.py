from supabase_client.connection import get_supabase_client
from supabase_client.utils import (
    check_if_table_exists
)
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Iterable, Optional, List, Any


supabase = get_supabase_client()
player_stats_table_name = "biwenger_player_stats"
if not check_if_table_exists(supabase, player_stats_table_name):
    st.warning(f"⚠️ Table '{player_stats_table_name}' does not exist.")

current_team_table_name = "biwenger_current_team"
if not check_if_table_exists(supabase, current_team_table_name):
    st.warning(f"⚠️ Table '{current_team_table_name}' does not exist.")

player_value_table_name = "biwenger_player_value"
if not check_if_table_exists(supabase, player_value_table_name):
    st.warning(f"⚠️ Table '{player_value_table_name}' does not exist.")

player_matches_table_name = "biwenger_player_matches"
if not check_if_table_exists(supabase, player_matches_table_name):
    st.warning(f"⚠️ Table '{player_matches_table_name}' does not exist.")

def fetch_all_rows_from_supabase(
    table_name: str,
    select: str = "*",
    page_size: int = 5000,
    order_by: Optional[str] = None,
    ascending: bool = True,
    eq_filters: Optional[Dict[str, Any]] = None,
    in_filters: Optional[Dict[str, Iterable[Any]]] = None,
    drop_columns: Optional[List[str]] = None,
) -> pd.DataFrame:
    """
    Read ALL rows from a Supabase table using paginated .range() requests.

    Args:
        table_name: Supabase table name.
        select: PostgREST select string (default "*").
        page_size: Chunk size for pagination (default 5000).
        order_by: Optional column to order by (recommended for deterministic paging).
        ascending: Sort direction if order_by is provided.
        eq_filters: Dict of column -> value to apply with .eq().
        in_filters: Dict of column -> iterable of values to apply with .in_().
        drop_columns: Columns to drop from the final DataFrame (e.g., ["id","created_at"]).

    Returns:
        pandas.DataFrame with all matching rows (empty if none).
    """
    rows: List[dict] = []
    start = 0

    while True:
        query = supabase.table(table_name).select(select)

        # Apply filters if any
        if eq_filters:
            for col, val in eq_filters.items():
                query = query.eq(col, val)

        if in_filters:
            for col, values in in_filters.items():
                # Ensure values is a list for in_()
                query = query.in_(col, list(values))

        # Optional deterministic ordering
        if order_by:
            query = query.order(order_by, desc=not ascending)

        # Page
        res = query.range(start, start + page_size - 1).execute()
        data = getattr(res, "data", None) or []

        if not data:
            break

        rows.extend(data)

        # If we received fewer rows than page_size, we're done
        if len(data) < page_size:
            break

        start += page_size

    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)

    if drop_columns:
        # Drop only if columns exist
        cols_to_drop = [c for c in drop_columns if c in df.columns]
        if cols_to_drop:
            df = df.drop(columns=cols_to_drop, errors="ignore")

    return df


@st.cache_data
def load_player_stats() -> pd.DataFrame:
    df = fetch_all_rows_from_supabase(
        table_name=player_stats_table_name,
        select="*",                # or list the exact columns for performance
        page_size=5000,
        order_by="player_name",    # optional but helps deterministic paging
        ascending=True,
        drop_columns=["id", "created_at"]
    )
    if df.empty:
        return df

    # Your existing enrichments
    return (
        df.assign(
            points_per_value=lambda d: np.round(
                np.maximum(0, d["points"] / d["value"].replace(0, pd.NA)) * 100_000, 2
            ),
            ratio_purchase_sales=lambda d: np.round(
                np.maximum(0, d["market_purchases_pct"] / d["market_sales_pct"]).replace(0, pd.NA), 2
            ),
            position=lambda d: d["position"].map({
                "Defender": "2 - Defensa",
                "Forward": "4 - Delantero",
                "Goalkeeper": "1 - Portero",
                "Midfielder": "3 - Centrocampista",
            }),
        )
    )

@st.cache_data
def load_current_team_players() -> pd.DataFrame:
    return fetch_all_rows_from_supabase(
        table_name=current_team_table_name,
        select="*",
        page_size=5000,
        order_by="name",
        ascending=True,
        drop_columns=["id", "created_at"]
    )

@st.cache_data
def load_player_matches() -> pd.DataFrame:
    return fetch_all_rows_from_supabase(
        table_name=player_matches_table_name,
        select="*",
        page_size=5000,
        order_by="player_name",
        ascending=True,
        drop_columns=["id", "created_at"]
    )

@st.cache_data
def load_market_value(player_names=None) -> pd.DataFrame:
    in_filters = {"player_name": player_names} if player_names else None
    df = fetch_all_rows_from_supabase(
        table_name=player_value_table_name,
        select="*",
        page_size=5000,
        order_by="player_name",
        ascending=True,
        in_filters=in_filters,
        drop_columns=["id", "created_at"]
    )
    if df.empty:
        return df

    # Convert date and compute your time-series features
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(["player_name", "date"]).reset_index(drop=True)

    df = (
        df.groupby("player_name", group_keys=False)
        .apply(lambda g: g.assign(
            value_change_1d=g["market_value_eur"].diff(),
            value_change_1d_pct=g["market_value_eur"].pct_change() * 100,
            value_change_7d=g["market_value_eur"].diff(periods=7),
            value_change_7d_pct=g["market_value_eur"].pct_change(periods=7) * 100,
            value_change_30d=g["market_value_eur"].diff(periods=30),
            value_change_30d_pct=g["market_value_eur"].pct_change(periods=30) * 100,
            value_avg_7d=g["market_value_eur"].rolling(window=7, min_periods=1).mean(),
            value_avg_14d=g["market_value_eur"].rolling(window=14, min_periods=1).mean(),
            value_avg_30d=g["market_value_eur"].rolling(window=30, min_periods=1).mean(),
        ))
        .reset_index(drop=True)
    )

    return df.sort_values(["player_name", "date"], ascending=[True, False])
