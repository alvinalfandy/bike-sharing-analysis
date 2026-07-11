import streamlit as st
import pandas as pd
import numpy as np
import os

st.set_page_config(page_title="Analisis Bike Sharing", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .stButton>button { background-color: #2c3e50; color: white; border-radius: 5px; }
    h1, h2, h3 { color: #2c3e50; }
</style>
""", unsafe_allow_html=True)

st.title("Dashboard Analisis Bike Sharing")

@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bike-sharing-dataset", "hour.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        return df.sample(3000, random_state=42).reset_index(drop=True)
    return None

df = load_data()

if df is None:
    st.error("Dataset tidak ditemukan.")
    st.stop()

with st.sidebar:
    st.title("Analisis Bike Sharing")
    st.markdown("---")
    st.subheader("Kelompok 1")
    st.caption("Praktikum Data Mining 2026")
    st.markdown("| Nama | GitHub |\n|------|--------|\n| Alvin Alfandy | [alvinalfandy](https://github.com/alvinalfandy) |\n| Abidzar Sabil Handoyo | [eufroshine](https://github.com/eufroshine) |\n| Ridho Fauzi | [ridhoofauzii](https://github.com/ridhoofauzii) |")

st.write(f"Dataset: {df.shape[0]:,} baris, {df.shape[1]} kolom")

col1, col2, col3, col4 = st.columns(4)
with col1: st.metric("Total Baris", f"{df.shape[0]:,}")
with col2: st.metric("Total Kolom", f"{df.shape[1]}")
with col3: st.metric("Rata-rata Penyewaan", f"{int(df['cnt'].mean()):,}")
with col4: st.metric("Total Penyewaan", f"{int(df['cnt'].sum()):,}")

tab1, tab2, tab3, tab4 = st.tabs(["Explorasi Data", "Pemodelan", "Prediksi", "Data Mentah"])

with tab1:
    import plotly.express as px
    import plotly.graph_objects as go

    if 'hr' in df.columns and 'cnt' in df.columns:
        st.subheader("Rata-rata Penyewaan per Jam")
        hourly = df.groupby('hr')['cnt'].mean().reset_index()
        fig = px.bar(hourly, x='hr', y='cnt', labels={'hr':'Jam','cnt':'Rata-rata'}, template='plotly_white')
        st.plotly_chart(fig, use_container_width=True)

    if 'dteday' in df.columns:
        st.subheader("Tren Penyewaan")
        df['dteday'] = pd.to_datetime(df['dteday'])
        daily = df.groupby('dteday')['cnt'].sum().reset_index()
        fig2 = px.line(daily, x='dteday', y='cnt', labels={'dteday':'Tanggal','cnt':'Total'}, template='plotly_white')
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Matriks Korelasi")
    num_cols = df.select_dtypes(include=['float64','int64']).columns
    corr = df[num_cols].corr()
    fig3 = px.imshow(corr, text_auto=".2f", color_continuous_scale='RdBu_r', aspect="auto")
    st.plotly_chart(fig3, use_container_width=True)

with tab2:
    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
    from sklearn.metrics import r2_score, accuracy_score, f1_score, mean_squared_error, mean_absolute_error, confusion_matrix

    st.subheader("Konfigurasi Model")
    analysis_type = st.radio("Tipe:", ["Regresi", "Klasifikasi"], horizontal=True)

    num_cols_list = df.select_dtypes(include=['float64','int64']).columns.tolist()
    exclude = ['cnt','casual','registered','instant']
    features = [c for c in num_cols_list if c not in exclude]

    target = st.selectbox("Target", num_cols_list, index=num_cols_list.index('cnt'))
    selected = st.multiselect("Fitur", [c for c in features if c!=target], default=[c for c in features if c!=target][:4])

    if not selected:
        st.warning("Pilih minimal 1 fitur.")
        st.stop()

    if analysis_type == "Regresi":
        algo = st.selectbox("Algoritma", ["Linear Regression","Random Forest","Decision Tree"])
    else:
        algo = st.selectbox("Algoritma", ["Logistic Regression","Random Forest","Decision Tree"])

    if st.button("Latih Model", use_container_width=True):
        with st.spinner("Melatih..."):
            X = df[selected].values
            y = df[target].values
            Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42)

            if analysis_type == "Regresi":
                if algo == "Linear Regression": model = LinearRegression()
                elif algo == "Random Forest": model = RandomForestRegressor(n_estimators=50, random_state=42)
                else: model = DecisionTreeRegressor(random_state=42)
            else:
                if algo == "Logistic Regression": model = LogisticRegression(max_iter=1000)
                elif algo == "Random Forest": model = RandomForestClassifier(n_estimators=50, random_state=42)
                else: model = DecisionTreeClassifier(random_state=42)

            model.fit(Xtr, ytr)
            yp_tr = model.predict(Xtr)
            yp = model.predict(Xte)

            st.subheader("Hasil Evaluasi")

            if analysis_type == "Regresi":
                r2_tr = r2_score(ytr, yp_tr)
                r2_te = r2_score(yte, yp)
                rmse = np.sqrt(mean_squared_error(yte, yp))
                mae = mean_absolute_error(yte, yp)

                m1,m2,m3,m4 = st.columns(4)
                with m1: st.metric("R2 Train", f"{r2_tr:.4f}")
                with m2: st.metric("R2 Test", f"{r2_te:.4f}")
                with m3: st.metric("RMSE", f"{rmse:.2f}")
                with m4: st.metric("MAE", f"{mae:.2f}")

                fig = go.Figure()
                fig.add_trace(go.Bar(name='Train', x=['R2'], y=[r2_tr], marker_color='#3498db'))
                fig.add_trace(go.Bar(name='Test', x=['R2'], y=[r2_te], marker_color='#e74c3c'))
                fig.update_layout(title='R2 Train vs Test', barmode='group', yaxis_range=[0,1], template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

                c1,c2 = st.columns(2)
                with c1:
                    st.write("**Aktual vs Prediksi**")
                    fig2 = px.scatter(x=yte, y=yp, labels={'x':'Aktual','y':'Prediksi'}, template='plotly_white')
                    fig2.add_trace(go.Scatter(x=[y.min(),y.max()], y=[y.min(),y.max()], mode='lines', name='Ideal', line=dict(color='red',dash='dash')))
                    st.plotly_chart(fig2, use_container_width=True)
                with c2:
                    st.write("**Residual**")
                    res = yte - yp
                    fig3 = px.scatter(x=yp, y=res, labels={'x':'Prediksi','y':'Residual'}, template='plotly_white')
                    fig3.add_hline(y=0, line_dash="dash", line_color="red")
                    st.plotly_chart(fig3, use_container_width=True)

            else:
                acc_tr = accuracy_score(ytr, yp_tr)
                acc_te = accuracy_score(yte, yp)
                f1 = f1_score(yte, yp, average='weighted')

                m1,m2,m3 = st.columns(3)
                with m1: st.metric("Accuracy Train", f"{acc_tr:.4f}")
                with m2: st.metric("Accuracy Test", f"{acc_te:.4f}")
                with m3: st.metric("F1 Score", f"{f1:.4f}")

                fig = go.Figure()
                fig.add_trace(go.Bar(name='Train', x=['Accuracy'], y=[acc_tr], marker_color='#3498db'))
                fig.add_trace(go.Bar(name='Test', x=['Accuracy'], y=[acc_te], marker_color='#e74c3c'))
                fig.update_layout(title='Accuracy Train vs Test', barmode='group', yaxis_range=[0,1], template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)

                c1,c2 = st.columns(2)
                with c1:
                    st.write("**Confusion Matrix**")
                    cm = confusion_matrix(yte, yp)
                    fig2 = px.imshow(cm, text_auto=True, labels=dict(x="Prediksi",y="Aktual"), template='plotly_white', color_continuous_scale='Blues')
                    st.plotly_chart(fig2, use_container_width=True)
                with c2:
                    st.write("**Distribusi**")
                    pdf = pd.DataFrame({'Kategori':['Rendah','Tinggi'], 'Jumlah':[(yp==0).sum(),(yp==1).sum()]})
                    fig3 = px.bar(pdf, x='Kategori', y='Jumlah', template='plotly_white', color='Kategori', color_discrete_sequence=['#3498db','#e74c3c'])
                    st.plotly_chart(fig3, use_container_width=True)

            if hasattr(model, 'feature_importances_'):
                st.subheader("Feature Importance")
                idf = pd.DataFrame({'Fitur':selected, 'Importance':model.feature_importances_}).sort_values('Importance', ascending=True)
                fig4 = px.bar(idf, x='Importance', y='Fitur', orientation='h', template='plotly_white', color='Importance', color_continuous_scale='Viridis')
                st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("Prediksi Penyewaan Sepeda")

    pred_type = st.radio("Jenis:", ["Regresi","Klasifikasi"], horizontal=True, key='pred_type')

    c1,c2,c3,c4 = st.columns(4)
    with c1:
        season = st.slider("Musim", 1,4,2, key='s1')
        yr = st.slider("Tahun", 0,1,1, key='yr1')
        mnth = st.slider("Bulan", 1,12,6, key='mn1')
        hr = st.slider("Jam", 0,23,12, key='hr1')
    with c2:
        holiday = st.slider("Libur", 0,1,0, key='ho1')
        weekday = st.slider("Hari", 0,6,3, key='wd1')
        workingday = st.slider("Hari Kerja", 0,1,1, key='wk1')
        weathersit = st.slider("Cuaca", 1,4,1, key='ws1')
    with c3:
        temp = st.slider("Suhu", 0.0,1.0,0.5, key='tp1')
        atemp = st.slider("Suhu Terasa", 0.0,1.0,0.5, key='at1')
    with c4:
        hum = st.slider("Kelembaban", 0.0,1.0,0.5, key='hm1')
        windspeed = st.slider("Angin", 0.0,1.0,0.3, key='wn1')

    if st.button("Hitung Prediksi", use_container_width=True):
        with st.spinner("Menghitung..."):
            inp = pd.DataFrame({'season':[season],'yr':[yr],'mnth':[mnth],'hr':[hr],'holiday':[holiday],'weekday':[weekday],'workingday':[workingday],'weathersit':[weathersit],'temp':[temp],'atemp':[atemp],'hum':[hum],'windspeed':[windspeed]})

            if pred_type == "Regresi":
                model = RandomForestRegressor(n_estimators=50, random_state=42)
            else:
                y_cls = (df['cnt'] >= df['cnt'].median()).astype(int)
                model = RandomForestClassifier(n_estimators=50, random_state=42)

            X = df[selected].values
            if pred_type == "Regresi":
                model.fit(X, df['cnt'].values)
            else:
                model.fit(X, y_cls.values)

            pred = model.predict(inp[selected])[0]

            c1,c2 = st.columns(2)
            with c1:
                if pred_type == "Regresi":
                    st.metric("Prediksi", f"{int(round(pred))} sepeda")
                else:
                    st.metric("Kategori", "Tinggi" if pred>=1 else "Rendah")
            with c2:
                if pred_type == "Regresi":
                    q25,q50,q75 = np.percentile(df['cnt'], [25,50,75])
                    if pred<q25: s,c = "Sangat Rendah","red"
                    elif pred<q50: s,c = "Rendah","orange"
                    elif pred<q75: s,c = "Sedang","blue"
                    else: s,c = "Tinggi","green"
                    st.markdown(f"<h3 style='color:{c}'>Status: {s}</h3>", unsafe_allow_html=True)

with tab4:
    st.subheader("Data Mentah")
    st.dataframe(df, use_container_width=True)
