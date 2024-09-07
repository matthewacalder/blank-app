import pandas as pd
import streamlit as st

def main() -> None:
    st.title("Trackmania Campaign Author Time Difficulty")
    st.markdown("All data taken from https://webservices.openplanet.dev/ on 7th September 2024.")
    st.markdown(
        "It is suggested that filtering from high to low on `10k Time % Difference` or "
        "`10k Time % Difference` column gives a good indication of easy -> hard author times."
    )
    st.markdown(
        "The above API only returns first 10,000 track times per track; an extension to determine the "
        "number/percentage of users to obtain an author medal on each track is suggested, if a data source is found."
    )

    df = pd.read_csv("campaign_data.csv")
    st.data_editor(
        df,
        column_config={"Thumbnail": st.column_config.ImageColumn("")},
        hide_index=True,    
    )

if __name__ == "__main__":
    main()
