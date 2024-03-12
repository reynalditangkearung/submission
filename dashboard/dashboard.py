import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

sns.set(style="dark")


# membuat fungsi bagi casual user
def create_casual_users(casual):
    casual_users = casual.groupby(by="dateday").agg({"casual": "sum"}).reset_index()
    return casual_users


# membuat fungsi bagi registered user
def create_registered_users(registered):
    registered_users = (
        registered.groupby(by="dateday").agg({"registered": "sum"}).reset_index()
    )
    return registered_users


# membuat fungsi bagi total user
def create_total_users(total):
    total_users = total.groupby(by="dateday").agg({"count": "sum"}).reset_index()
    return total_users


# judul dashboard
st.title("Bike Sharing Analysis Dashboard :man-biking:")


# fungsi memuat semua data csv
all_df = pd.read_csv("../main_data.csv")
day_df = pd.read_csv("../data/day.csv")
hour_df = pd.read_csv("../data/hour.csv")


# melakukan rename nama kolom
day_df.rename(
    columns={
        "dteday": "dateday",
        "yr": "year",
        "mnth": "month",
        "hr": "hour",
        "weathersit": "weather",
        "cnt": "count",
    },
    inplace=True,
)

day_df["season"] = day_df["season"].map(
    {1: "Springer", 2: "Summer", 3: "Fall", 4: "Winter"}
)

# mengubah format object ke tanggal
min_date = pd.to_datetime(day_df["dateday"]).dt.date.min()
max_date = pd.to_datetime(day_df["dateday"]).dt.date.max()

# tampilan sidebar dashboard
with st.sidebar:
    st.image("bike_share.jpg")
    start_date, end_date = st.date_input(
        label="Date Range",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

main_df = day_df[
    (day_df["dateday"] >= str(start_date)) & (day_df["dateday"] <= str(end_date))
]

# memanggil fungsi dataframe yang telah didefinisikan
casual_df = create_casual_users(main_df)
registered_df = create_registered_users(main_df)
total_df = create_total_users(main_df)

# menampilkan total jumlah penyewaan sepeda
cols1, cols2, cols3 = st.columns(3)

with cols1:
    casual_user = casual_df["casual"].sum()
    st.metric("Casual User", value=casual_user)

with cols2:
    registered_user = registered_df["registered"].sum()
    st.metric("Registered User", value=registered_user)

with cols3:
    total_user = total_df["count"].sum()
    st.metric("Total User", value=total_user)


# menghitung rata-rata penyewaan sepeda pada tahun 2011-2012
st.subheader("1. Number of bicycle rentals in 2011-2012.")

monthly_df = day_df.groupby(by=["month", "year"]).agg({"count": "sum"}).reset_index()
fig, ax = plt.subplots()
sns.lineplot(
    data=monthly_df,
    x="month",
    y="count",
    hue="year",
    marker="o",
    palette="flare",
    ax=ax,
)

plt.xlabel(None)
plt.ylabel("number of bike rentals by month")
plt.xticks(
    np.arange(1, 13),
    [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ],
)

plt.title("number of bicycle rentals by month in 2011-2012")
plt.legend(title="Year", labels=["2011", "2012"])
st.pyplot(fig)

# menghitung jumlah penyewaan sepeda bagi pengguna casual dan registered.
st.subheader("2. Number of bike rentals for casual and registered users.")

season_df = day_df.groupby("season")[["registered", "casual"]].sum().reset_index()

fig, ax = plt.subplots(figsize=(10, 7))

plt.bar(
    season_df["season"], season_df["registered"], label="Registered", color="tab:green"
)

plt.bar(season_df["season"], season_df["casual"], label="Casual", color="tab:grey")

plt.title("Number of bike rentals per day by season")
plt.legend(title="Users")
st.pyplot(fig)


# membuat RFM Analysis
st.subheader("3. RFM Analysis")

day_df["dateday"] = pd.to_datetime(day_df["dateday"])
last_date = day_df["dateday"].max()

rfm_data = (
    day_df.groupby(by="instant")
    .agg(
        {
            "dateday": lambda x: (last_date - x.max()).days,
            "count": ["count", "sum"],
        }
    )
    .reset_index()
)

rfm_data.columns = ["instant", "recency", "frequency", "monetary"]

fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(30, 6))

sns.barplot(
    y="recency",
    x="instant",
    data=rfm_data.sort_values(by="recency", ascending=True).head(5),
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("By Recency", loc="center", fontsize=15)
ax[0].tick_params(axis="x", labelsize=15)

sns.barplot(
    y="frequency",
    x="instant",
    data=rfm_data.sort_values(by="frequency", ascending=False).head(5),
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].set_title("By Frequency", loc="center", fontsize=15)
ax[1].tick_params(axis="x", labelsize=15)

sns.barplot(
    y="monetary",
    x="instant",
    data=rfm_data.sort_values(by="monetary", ascending=False).head(5),
    ax=ax[2],
)
ax[2].set_ylabel(None)
ax[2].set_xlabel(None)
ax[2].set_title("By Monetary", loc="center", fontsize=15)
ax[2].tick_params(axis="x", labelsize=15)

plt.suptitle("Best bike rentals on RFM Parameters (instant)", fontsize=20)
st.pyplot(fig)

st.caption("Copyright © reynalditangkearung 2024")
