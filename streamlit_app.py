import pandas as pd
import streamlit as st

from gui_components.pandas import filter_dataframe

def main() -> None:
    st.title("Trackmania 2020 Campaign Author Time Difficulty")
    st.markdown(
        "The below table shows the author times for all Trackmania 2020 Campaign tracks (as of 7th September 2024) "
        "alongisde world record times and the 10,000th position on leaderboard times."
    )
    st.markdown(
        "It is suggested that filtering from high to low on `10k Time Difference` or "
        "`10k Time % Difference` column gives a good indication of easy -> hard author times."
    )

    df = pd.read_csv("data_ingestion/campaign_data.csv")

    st.data_editor(
        filter_dataframe(df, no_filter_cols=["Thumbnail", "Completed"]),
        column_config={"Thumbnail": st.column_config.ImageColumn("")},
        hide_index=True,
    )

    st.markdown("All data taken from https://webservices.openplanet.dev/ on 7th September 2024.")
    st.markdown(
        "The API used to obtain data only returns first 10,000 track times per track; an extension to determine the "
        "number/percentage of users to obtain an author medal on each track is suggested, if a data source is found."
    )

if __name__ == "__main__":
    main()
