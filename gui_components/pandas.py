import pandas as pd
import streamlit as st

from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from pandas._libs.tslibs.parsing import DateParseError
from streamlit.delta_generator import DeltaGenerator


def _apply_categorical_filter(
    df: pd.DataFrame, col_name: str, gui_column: DeltaGenerator
) -> pd.DataFrame:
    user_cat_input = gui_column.multiselect(
        f"Values for {col_name}",
        df[col_name].unique(),
        default=list(df[col_name].unique()),
    )
    return df[df[col_name].isin(user_cat_input)]

def _apply_numerical_filter(
    df: pd.DataFrame, col_name: str, gui_column: DeltaGenerator
) -> pd.DataFrame:
    _min = float(df[col_name].min())
    _max = float(df[col_name].max())
    step = (_max - _min) / 100
    user_num_input = gui_column.slider(
        f"Values for {col_name}",
        min_value=_min,
        max_value=_max,
        value=(_min, _max),
        step=step,
    )
    return df[df[col_name].between(*user_num_input)]

def _apply_datetime_filter(
    df: pd.DataFrame, col_name: str, gui_column: DeltaGenerator
) -> pd.DataFrame:
    user_date_input = gui_column.date_input(
        f"Values for {col_name}",
        value=(
            df[col_name].min(),
            df[col_name].max(),
        ),
    )
    if len(user_date_input) == 2:
        user_date_input = tuple(map(pd.to_datetime, user_date_input))
        start_date, end_date = user_date_input
        return df.loc[df[col_name].between(start_date, end_date)]
    return df

def _apply_regex_filter(
    df: pd.DataFrame, col_name: str, gui_column: DeltaGenerator
) -> pd.DataFrame:
    user_text_input = gui_column.text_input(
        f"Substring or regex in {col_name}",
    )
    if user_text_input:
        return df[df[col_name].astype(str).str.contains(user_text_input)]
    return df

def _filter_column_contents(df: pd.DataFrame, filter_cols: list[str]) -> pd.DataFrame:
    to_filter_columns = st.multiselect("Filter dataframe on", filter_cols)
    _, right = st.columns((1, 20))
    for column in to_filter_columns:
        # Treat columns with < 10 unique values as categorical
        if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
            df = _apply_categorical_filter(df, column, right)
        elif is_numeric_dtype(df[column]):
            df = _apply_numerical_filter(df, column, right)
        elif is_datetime64_any_dtype(df[column]):
            df = _apply_datetime_filter(df, column, right)
        else:
            df = _apply_regex_filter(df, column, right)
    return df


def _filter_columns(df: pd.DataFrame) -> pd.DataFrame:
    all_columns = df.columns
    options = st.multiselect(
        label = "Columns to Show:",
        options=all_columns,
        default=all_columns,
    )
    df = df.drop(columns=set(all_columns) - set(options))
    return df


def filter_dataframe(df: pd.DataFrame, no_filter_cols: list[str]) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns
    A lot of code taken from:
        https://blog.streamlit.io/auto-generate-a-dataframe-filtering-ui-in-streamlit-with-filter_dataframe/

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    # Only show modification options if selected
    modify = st.checkbox("Add filters")
    if not modify:
        st.text(f"Tracks showing: {df.shape[0]}")
        return df

    # Configure what column contents can be controlled
    df = df.copy()
    filter_cols = list(df.columns)
    for col in no_filter_cols:
        filter_cols.remove(col)

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in filter_cols:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except DateParseError:
                pass
        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    # Apply filters
    modification_container = st.container()
    with modification_container:
        df = _filter_column_contents(df, filter_cols)
        df = _filter_columns(df)
        st.text(f"Tracks showing: {df.shape[0]}")

    return df
