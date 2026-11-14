import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Banking Customer Intelligence", page_icon="🏦", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.stApp{background:linear-gradient(135deg,#f7f8ff,#edf5ff 55%,#faf2ff)}
.block-container{max-width:1450px;padding-top:1.5rem}
.hero{background:linear-gradient(115deg,#171c4a,#4146b5 55%,#8950cc);padding:30px 34px;border-radius:22px;color:white;margin-bottom:22px}
.hero h1{color:white;font-size:34px;font-weight:800;margin:0}.hero p{color:#e5e6ff;margin:8px 0 0}
.kpi{background:white;border:1px solid #e8eaff;border-radius:17px;padding:18px;min-height:105px;box-shadow:0 8px 24px #27306b0d}
.kpi small{color:#737b9c;font-weight:700;letter-spacing:.7px}.kpi strong{display:block;color:#202653;font-size:25px;margin-top:8px}
div[data-testid="stMetric"]{background:white;border:1px solid #e8eaff;padding:15px;border-radius:15px}
</style>
""", unsafe_allow_html=True)

def demo_data():
    r=np.random.default_rng(18); n=900
    return pd.DataFrame({
      "Customer_ID":[f"C{10001+i}" for i in range(n)],
      "Transaction_ID":[f"T{50001+i}" for i in range(n)],
      "Transaction_Date":pd.date_range("2024-01-01","2025-12-31",periods=n),
      "Age":r.integers(19,76,n),
      "Gender":r.choice(["Female","Male","Other"],n,p=[.48,.49,.03]),
      "City":r.choice(["Hyderabad","Bengaluru","Mumbai","Chennai","Delhi","Pune","Anantapur"],n),
      "Account_Type":r.choice(["Savings","Current","Salary","Fixed Deposit"],n),
      "Transaction_Type":r.choice(["UPI","ATM","NEFT","IMPS","Debit Card","Credit Card"],n),
      "Amount":r.lognormal(7.1,.85,n).round(2),
      "Balance":r.lognormal(9.2,.5,n).round(2),
      "Channel":r.choice(["Mobile App","Branch","Internet Banking","ATM"],n),
      "Status":r.choice(["Success","Success","Success","Failed","Pending"],n)
    })

def detect(cols, words):
    for c in cols:
        s=str(c).lower().replace("_"," ").replace("-"," ")
        if any(w in s for w in words): return c
    return "(Not available)"

st.markdown('<div class="hero"><h1>🏦 Banking Customer Intelligence</h1><p>Upload your own banking dataset. Discover customer segments, transaction patterns and business trends.</p></div>',unsafe_allow_html=True)
with st.sidebar:
    st.header("📂 Data workspace")
    file=st.file_uploader("Upload CSV or Excel",type=["csv","xlsx","xls"])
    demo=st.toggle("Use sample banking dataset",value=file is None)
    st.divider()
    st.caption("Tip: Use anonymised data. Never upload real account numbers, card details, PINs or passwords.")

if file:
    try:
        raw=pd.read_csv(file) if file.name.lower().endswith(".csv") else pd.read_excel(file)
        source=file.name
    except Exception as e:
        st.error(f"Unable to read file: {e}"); st.stop()
elif demo:
    raw=demo_data(); source="Sample banking dataset"
else:
    st.info("Upload a CSV/Excel file or enable the sample dataset in the sidebar."); st.stop()

df=raw.copy()
df.columns=[str(c).strip() for c in df.columns]
for c in df.select_dtypes(include="object"):
    v=pd.to_numeric(df[c].astype(str).str.replace(",","",regex=False),errors="coerce")
    if v.notna().mean()>.8: df[c]=v

cols=["(Not available)"]+list(df.columns)
with st.expander("⚙️ Configure / map your dataset columns",expanded=file is not None):
    a,b,c=st.columns(3)
    def pick(container,label,words):
        guess=detect(df.columns,words)
        return container.selectbox(label,cols,index=cols.index(guess) if guess in cols else 0)
    customer=pick(a,"Customer ID",["customer id","customer_id","client id"])
    date=pick(a,"Transaction date",["transaction date","date","timestamp"])
    amount=pick(b,"Transaction amount",["amount","transaction value","value","debit","credit"])
    tx_type=pick(b,"Transaction type / channel",["transaction type","payment mode","channel","type"])
    segment=pick(c,"Customer segment / account type",["segment","account type","customer type"])
    location=pick(c,"City / region",["city","location","branch","region"])
    status=pick(st,"Transaction status",["status"])
def valid(x): return None if x=="(Not available)" else x
customer,date,amount,tx_type,segment,location,status=map(valid,[customer,date,amount,tx_type,segment,location,status])
work=df.copy()
if date: work[date]=pd.to_datetime(work[date],errors="coerce")
if amount:
    work[amount]=pd.to_numeric(work[amount],errors="coerce")
    work=work[work[amount].notna()].copy()

with st.sidebar:
    st.header("🔎 Filter analysis")
    filtered=work.copy()
    for col,label in [(location,"City / region"),(segment,"Customer segment"),(tx_type,"Transaction type")]:
        if col:
            vals=sorted(filtered[col].dropna().astype(str).unique())
            chosen=st.multiselect(label,vals,default=vals)
            filtered=filtered[filtered[col].astype(str).isin(chosen)]
    if date and filtered[date].notna().any():
        lo,hi=filtered[date].min().date(),filtered[date].max().date()
        period=st.date_input("Date range",(lo,hi),min_value=lo,max_value=hi)
        if isinstance(period,tuple) and len(period)==2:
            filtered=filtered[filtered[date].dt.date.between(period[0],period[1])]

n=len(filtered); customers=filtered[customer].nunique() if customer else None
total=filtered[amount].sum() if amount else None
avg=filtered[amount].mean() if amount and n else None
fmt=lambda x: f"₹{x:,.2f}" if x is not None else "Map amount column"
kpis=[("TRANSACTIONS",f"{n:,}"),("UNIQUE CUSTOMERS",f"{customers:,}" if customers is not None else "Map customer ID"),("TOTAL VALUE",fmt(total)),("AVERAGE VALUE",fmt(avg))]
k=st.columns(4)
for col,(label,value) in zip(k,kpis):
    col.markdown(f'<div class="kpi"><small>{label}</small><strong>{value}</strong></div>',unsafe_allow_html=True)
if status and n:
    rate=filtered[status].astype(str).str.lower().str.contains("success|complete|settled").mean()*100
    st.caption(f"Transaction success rate: **{rate:.1f}%**")

t1,t2,t3,t4=st.tabs(["📊 Overview","👥 Customer Segmentation","💳 Transaction Analysis","🗃️ Data Explorer"])
with t1:
    left,right=st.columns([1.5,1])
    with left:
        if date and amount:
            d=filtered.dropna(subset=[date]).copy()
            if len(d):
                d["Month"]=d[date].dt.to_period("M").astype(str)
                monthly=d.groupby("Month",as_index=False)[amount].sum()
                fig=px.area(monthly,x="Month",y=amount,markers=True,title="Monthly transaction value",color_discrete_sequence=["#6258d6"])
                fig.update_traces(line_width=3); fig.update_layout(paper_bgcolor="white",plot_bgcolor="white")
                st.plotly_chart(fig,use_container_width=True)
            else: st.info("No valid dates in the selected data.")
        else: st.info("Map transaction date and amount to show monthly trends.")
    with right:
        if segment:
            x=filtered[segment].fillna("Unknown").astype(str).value_counts().rename_axis("Segment").reset_index(name="Rows")
            st.plotly_chart(px.pie(x,names="Segment",values="Rows",hole=.6,title="Segment distribution",color_discrete_sequence=px.colors.qualitative.Pastel),use_container_width=True)
        elif location:
            x=filtered[location].astype(str).value_counts().head(10).rename_axis("Location").reset_index(name="Rows")
            st.plotly_chart(px.bar(x,x="Location",y="Rows",title="Top locations",color="Rows",color_continuous_scale="Purples"),use_container_width=True)
        else: st.info("Map a segment or location column for distribution.")
    if location and amount:
        x=filtered.groupby(location)[amount].sum().nlargest(10).reset_index()
        st.plotly_chart(px.bar(x,x=amount,y=location,orientation="h",title="Top locations by transaction value",color=amount,color_continuous_scale="Teal"),use_container_width=True)
with t2:
    if customer:
        agg={ "Transactions":(customer,"size") }
        if amount: agg["Total_Value"]=(amount,"sum"); agg["Average_Value"]=(amount,"mean")
        cust=filtered.groupby(customer,dropna=False).agg(**agg).reset_index()
        x,y=st.columns(2)
        x.metric("Customers in selection",f"{cust[customer].nunique():,}")
        x.plotly_chart(px.histogram(cust,x="Transactions",nbins=20,title="Transactions per customer",color_discrete_sequence=["#8174df"]),use_container_width=True)
        if amount and len(cust)>1:
            cust["Value_Segment"]=pd.qcut(cust["Total_Value"].rank(method="first"),q=min(4,len(cust)),labels=["Low","Regular","High","Premium"][:min(4,len(cust))])
            seg=cust.groupby("Value_Segment",observed=False)["Total_Value"].sum().reset_index()
            y.plotly_chart(px.bar(seg,x="Value_Segment",y="Total_Value",title="Value-based customer segments",color="Value_Segment",color_discrete_sequence=px.colors.qualitative.Pastel),use_container_width=True)
        st.markdown("**Top customers**")
        st.dataframe(cust.sort_values("Total_Value" if amount else "Transactions",ascending=False).head(25),use_container_width=True,hide_index=True)
    else: st.info("Map a Customer ID column to enable customer-level segmentation.")
with t3:
    x,y=st.columns(2)
    if tx_type:
        z=filtered[tx_type].fillna("Unknown").astype(str).value_counts().rename_axis("Type").reset_index(name="Transactions")
        x.plotly_chart(px.bar(z,x="Type",y="Transactions",title="Transactions by type / channel",color="Transactions",color_continuous_scale="Teal"),use_container_width=True)
    else: x.info("Map transaction type or channel.")
    if amount:
        y.plotly_chart(px.histogram(filtered,x=amount,nbins=35,title="Transaction amount distribution",color_discrete_sequence=["#ef9b68"]),use_container_width=True)
    else: y.info("Map transaction amount.")
    if status:
        z=filtered[status].fillna("Unknown").astype(str).value_counts().rename_axis("Status").reset_index(name="Count")
        st.plotly_chart(px.pie(z,names="Status",values="Count",hole=.5,title="Transaction status",color_discrete_sequence=px.colors.qualitative.Set2),use_container_width=True)
with t4:
    st.write(f"**Source:** {source} · {len(filtered):,} rows · {len(filtered.columns)} columns")
    st.dataframe(filtered,use_container_width=True,height=420)
    st.download_button("⬇️ Download filtered dataset CSV",filtered.to_csv(index=False).encode(), "banking_filtered.csv","text/csv")
    summary=pd.DataFrame({"Metric":["Rows","Columns","Unique customers","Total transaction value","Average transaction value"],"Value":[len(filtered),len(filtered.columns),customers,total,avg]})
    st.download_button("⬇️ Download KPI summary",summary.to_csv(index=False).encode(),"banking_kpis.csv","text/csv")
with st.expander("🧠 Data quality report"):
    quality=pd.DataFrame({"Column":filtered.columns,"Data type":[str(filtered[c].dtype) for c in filtered],"Missing values":[filtered[c].isna().sum() for c in filtered],"Missing (%)":[round(filtered[c].isna().mean()*100,2) for c in filtered],"Unique values":[filtered[c].nunique() for c in filtered]})
    st.dataframe(quality,use_container_width=True,hide_index=True)
st.divider()
st.caption("Portfolio learning project. Use synthetic or anonymised datasets only. Do not upload account numbers, card numbers, PINs, passwords, Aadhaar/PAN details or other sensitive customer data.")
