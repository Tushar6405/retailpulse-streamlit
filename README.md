# 📊 RetailPulse — Live Interactive Dashboard (Streamlit)

A fully interactive, live-hosted version of the [RetailPulse SQL Data Warehouse & Power BI Dashboard](https://github.com/Tushar6405/retail-sales-dashboard) project — same star-schema data, same business questions, rebuilt with Streamlit + Plotly so anyone can explore it live in the browser with zero installs.

**🔗 Live Dashboard:** _add your Streamlit Cloud link here_
**📁 Related project (SQL + Power BI):** [github.com/Tushar6405/retail-sales-dashboard](https://github.com/Tushar6405/retail-sales-dashboard)

## Why this exists

The Power BI version of this dashboard is fully built (4 pages, 10 DAX measures, synced slicers — see screenshots in the linked repo), but Power BI's free "Publish to web" requires a Microsoft work/school account, which blocks a simple public link for personal projects. This Streamlit app solves that: it connects directly to the same SQLite star-schema warehouse and reproduces every page as a live, filterable web app — deployable for free with no account restrictions.

## Features

- **Live SQL-backed data** — queries the same `retailpulse.db` star schema (fact_sales + 4 dimension tables) directly via `pandas.read_sql`, not a flattened CSV
- **4 interactive tabs** mirroring the Power BI report pages: Executive Overview, Product Performance, Customer & Region Insights, Trends
- **Sidebar filters** (Year, Region, Category, Customer Segment) — equivalent to the Power BI synced slicers, filtering all tabs simultaneously
- **Auto-generated insights** — e.g. flags the lowest-margin top-selling product for a pricing review, based on whatever filter selection is active
- Built with Plotly for genuinely interactive charts (hover, zoom, legend toggling)

## Tech Stack

| Layer | Tools |
|---|---|
| Data | SQLite (star schema, same `retailpulse.db` as the Power BI project) |
| Data access | Pandas (`read_sql`, `groupby`, `pivot_table`) |
| Visualization | Plotly Express / Graph Objects |
| Web app | Streamlit |

## Run Locally

```bash
git clone https://github.com/<your-username>/retailpulse-streamlit.git
cd retailpulse-streamlit
pip install -r requirements.txt
streamlit run app.py
```

## Project Structure

```
retailpulse-streamlit/
├── app.py              # Streamlit app — data loading, filters, all 4 dashboard tabs
├── retailpulse.db       # SQLite star-schema warehouse (same as the SQL/Power BI project)
├── requirements.txt
└── README.md
```

## Deployment

Deployed on [Streamlit Community Cloud](https://streamlit.io/cloud) (free tier), entry point `app.py`.

---
Built by **Tushar Bhadane** — [Portfolio](https://tushar6405.github.io) · [GitHub](https://github.com/Tushar6405)
