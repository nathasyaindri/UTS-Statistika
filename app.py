import io
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Statistika Deskriptif", page_icon="📊", layout="wide")

st.title("📊 Aplikasi Statistika Deskriptif")
st.write("Unggah data Excel/CSV, pilih variabel numerik, lalu hitung ukuran statistika deskriptif.")

with st.sidebar:
    st.header("Pengaturan")
    st.caption("Pilih ukuran statistik dan visualisasi yang ingin ditampilkan.")
    selected_stats = st.multiselect(
        "Ukuran statistik",
        ["Jumlah data (N)", "Minimum", "Maksimum", "Mean", "Median", "Modus",
         "Varians", "Standar deviasi", "Kuartil (Q1, Q2, Q3)"],
        default=["Jumlah data (N)", "Minimum", "Maksimum", "Mean", "Median",
                 "Modus", "Varians", "Standar deviasi", "Kuartil (Q1, Q2, Q3)"]
    )
    variance_type = st.radio(
        "Jenis varians dan standar deviasi",
        ["Sampel (n−1)", "Populasi (n)"],
        help="Sampel menggunakan pembagi n−1; populasi menggunakan pembagi n."
    )
    show_hist = st.checkbox("Tampilkan histogram", value=True)
    show_box = st.checkbox("Tampilkan boxplot", value=True)
    show_freq = st.checkbox("Tampilkan tabel frekuensi", value=False)

uploaded_file = st.file_uploader("Unggah dataset (.xlsx, .xls, atau .csv)", type=["xlsx", "xls", "csv"])

def load_data(file):
    if file.name.lower().endswith(".csv"):
        return pd.read_csv(file)
    return pd.read_excel(file)

def format_value(value):
    if isinstance(value, (float, np.floating)):
        if np.isnan(value):
            return "Tidak tersedia"
        return round(float(value), 4)
    if value is None:
        return "Tidak tersedia"
    return value

if uploaded_file is None:
    st.info("Belum ada file. Coba unggah dataset sendiri atau gunakan data contoh di bawah.")
    sample = pd.DataFrame({
        "Nama": ["Ani", "Budi", "Citra", "Doni", "Eka", "Fani", "Gilang", "Hana"],
        "Nilai Ujian": [78, 85, 90, 78, 88, 92, 85, 80],
        "Waktu Belajar (jam)": [2, 3, 4, 2, 3, 5, 4, 2],
        "Usia": [18, 19, 18, 20, 19, 18, 20, 19],
    })
    st.subheader("Contoh data")
    st.dataframe(sample, use_container_width=True)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        sample.to_excel(writer, index=False, sheet_name="Data")
    st.download_button("Unduh dataset contoh Excel", data=buffer.getvalue(),
                       file_name="dataset_contoh_statistika.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.caption("Unggah file Excel/CSV untuk mulai menganalisis.")
    st.stop()

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"File tidak dapat dibaca. Periksa format dan isi file. Detail: {e}")
    st.stop()

if df.empty:
    st.warning("Dataset kosong. Silakan unggah file yang berisi data.")
    st.stop()

st.subheader("1. Data yang diunggah")
c1, c2, c3 = st.columns(3)
c1.metric("Jumlah baris", len(df))
c2.metric("Jumlah kolom", len(df.columns))
c3.metric("Sel kosong", int(df.isna().sum().sum()))
st.dataframe(df, use_container_width=True, height=300)

numeric_cols = df.select_dtypes(include="number").columns.tolist()
if not numeric_cols:
    st.warning("Tidak ditemukan kolom numerik. Pastikan kolom angka tersimpan sebagai angka, bukan teks.")
    st.stop()

st.subheader("2. Pilih variabel numerik")
selected_cols = st.multiselect(
    "Variabel yang dianalisis (boleh lebih dari satu)",
    options=numeric_cols,
    default=numeric_cols[:1]
)
if not selected_cols:
    st.info("Pilih minimal satu variabel numerik untuk melihat hasil.")
    st.stop()

st.subheader("3. Ringkasan statistika deskriptif")
rows = []
ddof = 1 if variance_type == "Sampel (n−1)" else 0
for col in selected_cols:
    series = pd.to_numeric(df[col], errors="coerce").dropna()
    n = int(series.count())
    modes = series.mode().tolist() if n else []
    row = {"Variabel": col}
    if "Jumlah data (N)" in selected_stats:
        row["Jumlah data (N)"] = n
    if "Minimum" in selected_stats:
        row["Minimum"] = series.min() if n else np.nan
    if "Maksimum" in selected_stats:
        row["Maksimum"] = series.max() if n else np.nan
    if "Mean" in selected_stats:
        row["Mean"] = series.mean() if n else np.nan
    if "Median" in selected_stats:
        row["Median"] = series.median() if n else np.nan
    if "Modus" in selected_stats:
        row["Modus"] = ", ".join(map(str, modes)) if modes else "Tidak ada"
    if "Varians" in selected_stats:
        row["Varians"] = series.var(ddof=ddof) if n > ddof else np.nan
    if "Standar deviasi" in selected_stats:
        row["Standar deviasi"] = series.std(ddof=ddof) if n > ddof else np.nan
    if "Kuartil (Q1, Q2, Q3)" in selected_stats:
        row["Q1"] = series.quantile(0.25) if n else np.nan
        row["Q2"] = series.quantile(0.50) if n else np.nan
        row["Q3"] = series.quantile(0.75) if n else np.nan
    rows.append(row)

summary = pd.DataFrame(rows)
for col in summary.columns:
    if col != "Variabel" and summary[col].dtype == "float64":
        summary[col] = summary[col].round(4)
st.dataframe(summary, use_container_width=True)
st.caption("Catatan: nilai kosong diabaikan dalam perhitungan. Modus dapat berjumlah lebih dari satu. Varians dan standar deviasi mengikuti pilihan sampel/populasi di sidebar.")

st.subheader("4. Visualisasi")
for col in selected_cols:
    series = pd.to_numeric(df[col], errors="coerce").dropna()
    with st.expander(f"Visualisasi: {col}", expanded=True):
        if series.empty:
            st.warning("Tidak ada data numerik valid untuk divisualisasikan.")
            continue
        if show_hist:
            st.markdown("**Histogram**")
            hist_data = pd.DataFrame({col: series})
            st.bar_chart(hist_data[col].value_counts().sort_index(), use_container_width=True)
            st.caption("Batang menunjukkan banyaknya kemunculan setiap nilai; untuk data kontinu, pertimbangkan pengelompokan ke interval.")
        if show_box:
            st.markdown("**Boxplot**")
            fig, ax = plt.subplots()
            ax.boxplot(series.dropna())
            ax.set_title(f"Boxplot {col}")
            ax.set_ylabel(col)
            st.pyplot(fig)
            plt.close(fig)
        if show_freq:
            st.markdown("**Tabel frekuensi**")
            freq = series.value_counts(dropna=False).sort_index().rename_axis("Nilai").reset_index(name="Frekuensi")
            freq["Persentase (%)"] = (freq["Frekuensi"] / freq["Frekuensi"].sum() * 100).round(2)
            st.dataframe(freq, use_container_width=True)

st.subheader("5. Unduh hasil")
csv_data = summary.to_csv(index=False).encode("utf-8-sig")
st.download_button("Unduh ringkasan CSV", data=csv_data, file_name="ringkasan_statistika.csv", mime="text/csv")
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
    summary.to_excel(writer, index=False, sheet_name="Ringkasan")
    df.to_excel(writer, index=False, sheet_name="Data")
st.download_button(
    "Unduh hasil Excel",
    data=excel_buffer.getvalue(),
    file_name="hasil_statistika.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

with st.expander("Penjelasan singkat ukuran statistik"):
    st.markdown("""
    - **N**: banyaknya nilai numerik yang tidak kosong.
    - **Minimum/Maksimum**: nilai terkecil/terbesar.
    - **Mean**: rata-rata aritmetika.
    - **Median (Q2)**: nilai tengah setelah data diurutkan.
    - **Modus**: nilai yang paling sering muncul; bisa lebih dari satu.
    - **Varians**: ukuran penyebaran data berdasarkan kuadrat selisih dari rata-rata.
    - **Standar deviasi**: akar kuadrat varians.
    - **Q1 dan Q3**: kuartil 25% dan 75%.
    """)
