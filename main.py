import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import altair as alt
import os

def hitung_kerusakan(teks):
    if not teks or teks == "":
        return 0
    if pd.isna(teks) or teks == '' or teks is None:
        return 0
    
    # Hitung jumlah item berdasarkan koma
    jumlah_kerusakan = teks.count(',') + 1

    # Jika mengandung "cek rutin", kurangi 1
    if 'cek rutin' in teks.lower():
        jumlah_kerusakan -= 1

    return jumlah_kerusakan


st.markdown("""
    <style>
    /* Style tombol sidebar */
    [data-testid="stSidebar"] div.stButton > button {
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        display: block;
        margin: 5px 0;
        border: none !important;
    }

    /* Judul menu di sidebar rata kiri */
    [data-testid="stSidebar"] h3 {
        text-align: left !important;
    }

    /* Sembunyikan MainMenu dan footer */
    #MainMenu, footer {
        display: none !important;
    }

    /* Sembunyikan avatar/foto pengguna dan "Hosted by Streamlit" */
    [data-testid="stSidebarUserContent"] {
        display: none !important;
    }

    /* Sembunyikan elemen 'Made with Streamlit' di footer kanan */
    .css-cio0dv.ea3mdgi1 {
        display: none !important;
    }

    </style>
""", unsafe_allow_html=True)


# Daftar menu
menu_items = [
    "SPK",
    "HM 3 Shift",
    "Pemakaian Harian",
    "Total Jam per Hari",
    "Tingkat Kerusakan",
    "Monitoring Forklift",
    "Tabel Kerusakan"
]

# Simpan menu yang sedang aktif di session_state
if "menu" not in st.session_state:
    st.session_state.menu = "SPK"

# Sidebar dengan tombol navigasi
st.sidebar.markdown("### MENU")

for item in menu_items:
    if st.sidebar.button(item):
        st.session_state.menu = item  # Simpan pilihan menu ke session_state

menu = st.session_state.menu  # Gunakan nilai dari session_state


# File Excel
excel_file = "data_spk.xlsx"
if not os.path.exists(excel_file):
    header_template = pd.DataFrame(columns=[
        "Tanggal", "Nomor SPK", "Area / Mesin", "Mulai Pengerjaan", "Selesai Pengerjaan",
        "Jenis Kerusakan", "Penyelesaian", "Keterangan/Penyebab",
        "Tanggal Pengerjaan", "Masuk Bengkel", "Keluar Bengkel"
    ])
    header_template.to_excel(excel_file, index=False)

new_data = None


    
if menu == "SPK":
    st.session_state.shift3 = False
    
    # Tampilkan seluruh isi tabel SPK
    st.header("Tabel Data SPK")
    
    try:
        all_data = pd.read_excel(excel_file, dtype={"Nomor SPK": str})
        all_data['Tanggal'] = pd.to_datetime(all_data['Tanggal']).dt.strftime('%Y-%m-%d')
        all_data = all_data.sort_values("Tanggal", ascending=False)
        all_data = all_data.reset_index(drop=True)
        st.dataframe(all_data)
    except Exception as e:
        st.error(f"Gagal membaca file SPK: {e}")

    col1, col2, col3, col4 = st.columns(4)

    # Tambah data
    if "show_form" not in st.session_state:
        st.session_state.show_form = False

    with col1:
        if st.button("Tambah data", use_container_width=True):
            st.session_state.show_form = not st.session_state.get("show_form", False)
            # Tutup menu lainnya
            st.session_state.editData = False
            st.session_state.hapusData = False
            st.session_state.download = False

    with col2:
        if st.button("Edit data", use_container_width=True):
            st.session_state.editData = not st.session_state.get("editData", False)
            st.session_state.show_form = False
            st.session_state.hapusData = False
            st.session_state.download = False

    with col3:
        if st.button("Hapus data", use_container_width=True):
            st.session_state.hapusData = not st.session_state.get("hapusData", False)
            st.session_state.show_form = False
            st.session_state.editData = False
            st.session_state.download = False

    with col4:
        if st.button("Download", use_container_width=True):
            st.session_state.download = not st.session_state.get("download", False)
            st.session_state.show_form = False
            st.session_state.editData = False
            st.session_state.hapusData = False

            
    if st.session_state.show_form:
        st.write("#### Form Data SPK")
        with st.form("form_spk"):
            col1, col2 = st.columns(2)

            with col1:
                tgl = st.date_input("Tanggal", value=datetime.today()).strftime("%Y-%m-%d")
                area_mesin = st.text_input("Area / Mesin")
                penyelesaian = st.text_area("Penyelesaian / Tindak Lanjut")
                mulai_pengerjaan_input = st.text_input("Mulai Pengerjaan (HH:MM)", value="")
                selesai_pengerjaan_input = st.text_input("Selesai Pengerjaan (HH:MM)", value="")

            with col2:
                nomor = st.text_input("Nomor SPK")
                jenis_kerusakan = st.text_area("Jenis Kerusakan")
                penyebab = st.text_input("Keterangan / Penyebab Kerusakan")
                masuk_bengkel_input = st.text_input("Masuk Bengkel (HH:MM)", value="")
                keluar_bengkel_input = st.text_input("Keluar Bengkel (HH:MM)", value="")

            submit = st.form_submit_button("Simpan Data")
            
                
            if submit:
                if nomor == "":
                    st.error("Nomor SPK tidak boleh kosong")
                else:
                    if str(nomor) in list(all_data["Nomor SPK"]):
                        st.error("Nomor SPK suda ada")
                    else:
                        try:
                            mulai_pengerjaan = pd.to_datetime(mulai_pengerjaan_input, format='%H:%M').strftime('%H:%M')
                        except:
                            mulai_pengerjaan = None

                        try:
                            selesai_pengerjaan = pd.to_datetime(selesai_pengerjaan_input, format='%H:%M').strftime('%H:%M')
                        except:
                            selesai_pengerjaan = None
                            
                        try:
                            masuk_bengkel = pd.to_datetime(masuk_bengkel_input, format='%H:%M').strftime('%H:%M')
                        except:
                            masuk_bengkel = None

                        try:
                            keluar_bengkel = pd.to_datetime(keluar_bengkel_input, format='%H:%M').strftime('%H:%M')
                        except:
                            keluar_bengkel = None

                        new_data = pd.DataFrame({
                            "Tanggal": [tgl],
                            "Nomor SPK": [nomor],
                            "Area / Mesin": [area_mesin],
                            "Mulai Pengerjaan": [mulai_pengerjaan],
                            "Selesai Pengerjaan": [selesai_pengerjaan],
                            "Jenis Kerusakan": [jenis_kerusakan],
                            "Penyelesaian": [penyelesaian],
                            "Keterangan/Penyebab": [penyebab],
                            "Masuk Bengkel": [masuk_bengkel],
                            "Keluar Bengkel": [keluar_bengkel],
                            "Total Kerusakan": [hitung_kerusakan(jenis_kerusakan)]
                        })

                        try:
                            existing_data = pd.read_excel(excel_file, dtype={"Nomor SPK": str})
                        except:
                            existing_data = pd.DataFrame()

                        updated_data = pd.concat([existing_data, new_data], ignore_index=True)
                        updated_data.to_excel(excel_file, index=False)

                        st.success("Berhasil")

                        # Reset form view
                        st.session_state.show_form = False
                        st.rerun()

    # Edit data
    if "editData" not in st.session_state:
        st.session_state.editData = False    
        
    if st.session_state.editData:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Edit data berdasarkan nomor SPK")

        search_spk = st.text_input("Cari berdasarkan Nomor SPK (untuk Edit)", key="search_spk")
        edit_mode = False

        if search_spk:
            df = pd.read_excel(excel_file, dtype={"Nomor SPK": str})
            matched_data = df[df["Nomor SPK"] == search_spk]

            if matched_data.empty:
                st.warning(f"Data dengan Nomor SPK '{search_spk}' tidak ditemukan.")
            else:
                st.success("Data ditemukan. Silakan lakukan perubahan pada form di bawah ini.")
                edit_mode = True
                data_to_edit = matched_data.iloc[0]

                with st.form("edit_form_spk"):
                    col1, col2 = st.columns(2)

                    with col1:
                        tgl_val = "" if pd.isna(data_to_edit["Tanggal"]) else pd.to_datetime(data_to_edit["Tanggal"])
                        tgl_edit = st.date_input("Tanggal", value=tgl_val).strftime("%Y-%m-%d")
                        

                        area_mesin_edit = st.text_input("Area / Mesin", value="" if pd.isna(data_to_edit["Area / Mesin"]) else data_to_edit["Area / Mesin"])

                        penyelesaian_edit = st.text_area("Penyelesaian / Tindak Lanjut", value="" if pd.isna(data_to_edit["Penyelesaian"]) else data_to_edit["Penyelesaian"],height=191)

                        mulai_val = "" if pd.isna(data_to_edit["Mulai Pengerjaan"]) else str(data_to_edit["Mulai Pengerjaan"])[:5]
                        mulai_pengerjaan_edit = st.text_input("Mulai Pengerjaan (HH:MM)", value=mulai_val)

                        selesai_val = "" if pd.isna(data_to_edit["Selesai Pengerjaan"]) else str(data_to_edit["Selesai Pengerjaan"])[:5]
                        selesai_pengerjaan_edit = st.text_input("Selesai Pengerjaan (HH:MM)", value=selesai_val)

                    with col2:
                        nomor_edit = st.text_input("Nomor SPK", value=search_spk)

                        jenis_kerusakan_edit = st.text_area("Jenis Kerusakan", value="" if pd.isna(data_to_edit["Jenis Kerusakan"]) else data_to_edit["Jenis Kerusakan"], height=130)

                        penyebab_edit = st.text_area("Keterangan / Penyebab Kerusakan", value="" if pd.isna(data_to_edit["Keterangan/Penyebab"]) else data_to_edit["Keterangan/Penyebab"])

                        # Untuk Masuk Bengkel
                        if not pd.isna(data_to_edit["Masuk Bengkel"]):
                            masuk_bengkel_edit = st.text_input(
                                "Masuk Bengkel", 
                                value=data_to_edit["Masuk Bengkel"])
                        else:
                            masuk_bengkel_edit = st.text_input(
                                "Masuk Bengkel (HH:MM)", 
                                value=""
                            )

                        # Untuk Keluar Bengkel
                        if not pd.isna(data_to_edit["Keluar Bengkel"]):
                            keluar_bengkel_edit = st.text_input(
                                "Keluar Bengkel", 
                                value=data_to_edit["Keluar Bengkel"])
                        else:
                            keluar_bengkel_edit = st.text_input(
                                "Keluar Bengkel (HH:MM)", 
                                value=""
                            )


                    submit_edit = st.form_submit_button("Update Data")

                    if submit_edit:
                        try:
                            mulai_pengerjaan_new = datetime.strptime(mulai_pengerjaan_edit.strip(), "%H:%M").time()
                        except:
                            mulai_pengerjaan_new = None

                        try:
                            selesai_pengerjaan_new = datetime.strptime(selesai_pengerjaan_edit.strip(), "%H:%M").time()
                        except:
                            selesai_pengerjaan_new = None

                        idx = matched_data.index[0]
                        df.loc[idx, "Nomor SPK"] = nomor_edit
                        df.loc[idx, "Tanggal"] = tgl_edit
                        df.loc[idx, "Area / Mesin"] = area_mesin_edit
                        df.loc[idx, "Penyelesaian"] = penyelesaian_edit
                        df.loc[idx, "Mulai Pengerjaan"] = mulai_pengerjaan_new
                        df.loc[idx, "Selesai Pengerjaan"] = selesai_pengerjaan_new
                        df.loc[idx, "Jenis Kerusakan"] = jenis_kerusakan_edit
                        df.loc[idx, "Keterangan/Penyebab"] = penyebab_edit
                        
                        
                        # df.loc[idx, "Masuk Bengkel"] = masuk_bengkel_edit
                        # df.loc[idx, "Keluar Bengkel"] = keluar_bengkel_edit
                        try:
                            masuk_bengkel_final = (
                                pd.to_datetime(masuk_bengkel_edit, format='%H:%M').strftime('%H:%M')
                                if masuk_bengkel_edit.strip() != ""
                                else ""
                            )
                        except:
                            masuk_bengkel_final = ""

                        try:
                            keluar_bengkel_final = (
                                pd.to_datetime(keluar_bengkel_edit, format='%H:%M').strftime('%H:%M')
                                if keluar_bengkel_edit.strip() != ""
                                else ""
                            )
                        except:
                            keluar_bengkel_final = ""
                        
                        df.loc[idx, "Masuk Bengkel"] = masuk_bengkel_final
                        df.loc[idx, "Keluar Bengkel"] = keluar_bengkel_final



                        df.to_excel(excel_file, index=False)

                        st.success("Data berhasil diperbarui!")
                        st.session_state.editData = False
                        st.rerun()

    # Hapus data
    if "hapusData" not in st.session_state:
        st.session_state.hapusData = False
        
    if st.session_state.hapusData:
        st.subheader("Hapus data berdasarkan nomor SPK")

        hapus_nomor_spk = st.text_input("Masukkan Nomor SPK yang ingin dihapus", key="hapus_spk")

        if hapus_nomor_spk.strip() != "":
            try:
                df = pd.read_excel(excel_file, dtype={"Nomor SPK": str})
                matching_data = df[df["Nomor SPK"] == hapus_nomor_spk]

                if matching_data.empty:
                    st.warning(f"Tidak ada data dengan Nomor SPK: {hapus_nomor_spk}")
                else:
                    st.write("Data yang akan dihapus:")
                    st.dataframe(matching_data)

                    konfirmasi_hapus = st.checkbox("Saya yakin ingin menghapus data ini")

                    if konfirmasi_hapus:
                        if st.button("Hapus Data SPK Sekarang"):
                            df = df[df["Nomor SPK"] != hapus_nomor_spk]
                            df.to_excel(excel_file, index=False)
                            st.success("Data SPK berhasil dihapus.")
                            st.session_state.hapusData = False
                            st.rerun()
            except Exception as e:
                st.error(f"Gagal memproses data: {e}")
        else:
            st.info("Silakan masukkan Nomor SPK terlebih dahulu.")
            
    
    if "download" not in st.session_state:
        st.session_state.download = False
        
    if st.session_state.download:
        # Fitur download data berdasarkan tanggal tertentu
        st.subheader("Download Data Berdasarkan Tanggal")
        df = pd.read_excel(excel_file, dtype={"Nomor SPK": str})
        df['Tanggal'] = pd.to_datetime(df['Tanggal'])


        try:
            start_date = st.date_input("Tanggal Awal")
            end_date = st.date_input("Tanggal Akhir")

            if end_date < start_date:
                raise ValueError("Tanggal akhir tidak boleh lebih kecil dari tanggal awal.")

            # Filter data berdasarkan tanggal
            filtered_df = df[(df['Tanggal'] >= pd.to_datetime(start_date)) & (df['Tanggal'] <= pd.to_datetime(end_date))]

            if not filtered_df.empty:
                from io import BytesIO
                buffer = BytesIO()
                filtered_df.to_excel(buffer, index=False, engine='openpyxl')
                buffer.seek(0)

                st.download_button(
                    label="Download",
                    data=buffer,
                    file_name=f"data_{start_date}_to_{end_date}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            else:
                st.info("Tidak ada data pada rentang tanggal tersebut.")

        except ValueError as ve:
            st.error(f"Kesalahan input tanggal: {ve}")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {e}")
 
# HM 3 Shift ===============================================================================================================           
if menu == "HM 3 Shift":
 
    st.header("HM Harian Tiap Shift")
    # Nama file Excel
    file_excel = "HM_Harian.xlsx"

    # List Forklift dan Shift
    forklifts = ["FK 14", "FK 16", "FK 17", "FK 19", "FK 20", "FK 21", "FK 22", "FK 23", "FK 24", "FK 27",
                "FK 28", "FK 29", "FK 35", "FK 38", "FK 40", "FK 41", "FK 43", "FK 46", "FK 49", "FK 50",
                "FK 51", "FK 52", "FK 53", "Truk A", "Truk B", "Truk C"]
    shifts = ['Shift 1', 'Shift 2', 'Shift 3']

    # Buat semua kombinasi kolom header: FK - Shift
    column_headers = [f"{fk} - {shift}" for fk in forklifts for shift in shifts]

    # Pilih tanggal
    start_date = st.date_input("Tanggal mulai", datetime.now() - timedelta(days=7))
    end_date = st.date_input("Tanggal akhir", datetime.today())

    # Generate list tanggal
    date_range = pd.date_range(start=start_date, end=end_date)

    # Load data sebelumnya jika ada
    if os.path.exists(file_excel):
        df_old = pd.read_excel(file_excel)
        df_old['Tanggal'] = pd.to_datetime(df_old['Tanggal']).dt.date
    else:
        df_old = pd.DataFrame(columns=['Tanggal'] + column_headers)

    # Siapkan tabel baru dengan data lama jika ada
    data_baru = []

    for tanggal in date_range:
        row = {'Tanggal': tanggal.date()}
        for col in column_headers:
            match = df_old[(df_old['Tanggal'] == tanggal.date())]
            if not match.empty and col in match.columns:
                val = match.iloc[0][col]
                row[col] = '' if pd.isna(val) else str(val)
            else:
                row[col] = ''
        data_baru.append(row)

    df_input = pd.DataFrame(data_baru)

    # Pastikan seluruh sel kosong tidak NaN tapi string kosong
    df_input = df_input.fillna('')

    # Konversi semua kolom (selain Tanggal) jadi string agar bisa diisi angka/huruf
    for col in df_input.columns:
        if col != 'Tanggal':
            df_input[col] = df_input[col].astype(str)

    # Tampilkan editor
    df_edited = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

    # Tombol simpan
    if st.button("Simpan Data"):
        df_old_filtered = df_old[~df_old['Tanggal'].isin(df_input['Tanggal'])]
        df_final = pd.concat([df_old_filtered, df_edited], ignore_index=True)
        df_final = df_final.sort_values(by='Tanggal')
        df_final.to_excel(file_excel, index=False)
        st.success("Data berhasil disimpan!")
        
if menu == "Pemakaian Harian":
    st.header("Penggunaan forklift Harian(Jam)")

    # Baca data dari file Excel (sesuaikan nama file jika perlu)
    df = pd.read_excel("HM_Harian.xlsx")

    # Pastikan kolom 'Tanggal' bertipe datetime
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')

    # Fungsi untuk mencoba mengonversi ke float, jika tidak berhasil maka biarkan nilainya asli
    def convert_to_numeric(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return value

    # Ubah semua kolom kecuali 'Tanggal'
    df.iloc[:, 1:] = df.iloc[:, 1:].applymap(convert_to_numeric)

    # DataFrame untuk hasil penggunaan
    usage_df = df.copy()

    num_forklifts = 26       # Total forklift
    shifts_per_forklift = 3  # Shift per forklift
    total_columns = num_forklifts * shifts_per_forklift

    # Kolom-kolom yang akan dihitung (semua kolom kecuali 'Tanggal')
    cols = df.columns[1:total_columns + 1]

    # Proses per forklift: kumpulkan data dari ketiga shift per forklift secara berurutan
    for i in range(num_forklifts):
        # Daftar kolom untuk forklift ke-i
        forklift_cols = [cols[i * shifts_per_forklift + j] for j in range(shifts_per_forklift)]
        
        # Kumpulkan posisi (baris, kolom) untuk forklift ini secara berurutan
        positions = []
        for r in range(len(df)):
            for col in forklift_cols:
                positions.append((r, col))
        
        # Untuk setiap posisi, jika nilainya angka, cari nilai numerik berikutnya dalam urutan positions
        for index, (r, col) in enumerate(positions):
            current_val = df.at[r, col]
            if isinstance(current_val, (int, float)):
                # Cari nilai numerik berikutnya dalam urutan positions
                next_numeric = None
                for j in range(index + 1, len(positions)):
                    r_next, col_next = positions[j]
                    candidate = df.at[r_next, col_next]
                    if isinstance(candidate, (int, float)):
                        next_numeric = candidate
                        break
                # Jika ditemukan nilai berikutnya, hitung selisihnya, jika tidak, salin nilai aslinya
                if next_numeric is not None:
                    usage_df.at[r, col] = next_numeric - current_val
                else:
                    usage_df.at[r, col] = current_val
            else:
                # Jika bukan angka, langsung salin nilai aslinya
                usage_df.at[r, col] = current_val

    # Dua field untuk memasukkan rentang tanggal (default adalah tanggal hari ini)
    st.write("Pilih rentang tanggal untuk menampilkan data:")
    start_date = st.date_input("Tanggal Mulai", value=datetime(datetime.now().year, 1, 1))
    end_date   = st.date_input("Tanggal Akhir", value=datetime.now())

    # Filter data berdasarkan rentang tanggal yang diinput
    mask = (usage_df['Tanggal'] >= pd.to_datetime(start_date)) & (usage_df['Tanggal'] <= pd.to_datetime(end_date))
    filtered_df = usage_df.loc[mask]

    st.subheader("Tabel Penggunaan Forklift")
    st.dataframe(filtered_df)
    
if menu == "Total Jam per Hari":
    st.header("Jumlah Jam Penggunaan Forklift Per Hari")

    # Baca data dari file Excel
    df = pd.read_excel("HM_Harian.xlsx")

    # Pastikan kolom 'Tanggal' bertipe datetime
    df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')

    # Fungsi untuk mencoba mengonversi ke float, jika tidak maka nilai aslinya disimpan
    def convert_to_numeric(value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return value

    # Ubah semua kolom kecuali 'Tanggal'
    df.iloc[:, 1:] = df.iloc[:, 1:].applymap(convert_to_numeric)

    # Buat salinan df untuk menyimpan hasil perhitungan usage
    usage_df = df.copy()

    # --- Hitung penggunaan tiap shift per forklift ---
    # Kita hanya memproses kolom yang namanya diawali dengan "FK" (mengabaikan kolom Truk)
    forklift_cols_all = [col for col in df.columns if col.startswith("FK")]

    # Jumlah forklift didapat dari banyaknya kolom FK dibagi 3 (karena tiap forklift memiliki 3 shift)
    shifts_per_forklift = 3
    num_forklifts = len(forklift_cols_all) // shifts_per_forklift

    # Proses per forklift: untuk tiap forklift, kita “flatten” data (urutan: baris pertama Shift 1, baris pertama Shift 2, baris pertama Shift 3, baris kedua Shift 1, dst)
    for i in range(num_forklifts):
        # Ambil 3 kolom untuk forklift ke-i
        forklift_cols = forklift_cols_all[i * shifts_per_forklift : i * shifts_per_forklift + shifts_per_forklift]
        
        # Kumpulkan posisi (indeks baris, nama kolom) secara berurutan untuk forklift ini
        positions = []
        for r in range(len(df)):
            for col in forklift_cols:
                positions.append((r, col))
        
        # Untuk tiap posisi, jika nilainya angka, cari nilai angka berikutnya dalam urutan positions
        for index, (r, col) in enumerate(positions):
            current_val = df.at[r, col]
            # Hanya proses jika nilai saat ini adalah angka
            if isinstance(current_val, (int, float)):
                next_numeric = None
                # Cari nilai numerik berikutnya di positions (abaikan nilai non-angka)
                for j in range(index + 1, len(positions)):
                    r_next, col_next = positions[j]
                    candidate = df.at[r_next, col_next]
                    if isinstance(candidate, (int, float)):
                        next_numeric = candidate
                        break
                if next_numeric is not None:
                    usage_df.at[r, col] = next_numeric - current_val
                else:
                    usage_df.at[r, col] = current_val
            else:
                # Jika bukan angka, biarkan nilainya
                usage_df.at[r, col] = current_val

    # --- Hitung total jam per forklift per hari ---
    # Kita akan membuat dataframe baru yang memiliki kolom "Tanggal" dan satu kolom untuk tiap forklift
    result_df = pd.DataFrame()
    result_df['Tanggal'] = usage_df['Tanggal']

    # Untuk setiap forklift, jumlahkan penggunaan dari ketiga shift pada baris (hari) yang sama.
    # Hanya nilai numerik yang dihitung (non-angka akan diabaikan)
    for i in range(num_forklifts):
        forklift_cols = forklift_cols_all[i * shifts_per_forklift : i * shifts_per_forklift + shifts_per_forklift]
        # Ekstrak nama forklift dari kolom pertama (misal: "FK 14 - Shift 1" akan jadi "FK 14")
        forklift_name = forklift_cols[0].split(" - ")[0]
        
        # Ambil data 3 shift, konversi ke numerik (jika gagal jadi NaN) lalu jumlahkan per baris
        numeric_data = usage_df[forklift_cols].apply(pd.to_numeric, errors='coerce')
        result_df[forklift_name] = numeric_data.sum(axis=1, skipna=True)

    # --- Filter berdasarkan rentang tanggal ---
    st.write("Masukkan rentang tanggal untuk menampilkan data:")
    start_date = st.date_input("Tanggal Mulai", value=datetime(datetime.now().year, 1, 1))
    end_date   = st.date_input("Tanggal Akhir", value=datetime.now())

    mask = (result_df['Tanggal'] >= pd.to_datetime(start_date)) & (result_df['Tanggal'] <= pd.to_datetime(end_date))
    filtered_df = result_df.loc[mask].reset_index(drop=True)

    st.subheader("Tabel Jumlah Jam per Hari per Forklift")
    filtered_df['Tanggal'] = filtered_df['Tanggal'].dt.strftime('%Y-%m-%d')
    st.dataframe(filtered_df)


if menu == "Tingkat Kerusakan":
    # Daftar forklift yang digunakan
    forklifts = ["FK 14", "FK 16", "FK 17", "FK 19", "FK 20", "FK 21", "FK 22", "FK 23", "FK 24",
                "FK 27", "FK 28", "FK 29", "FK 35", "FK 38", "FK 40", "FK 41", "FK 43", "FK 46",
                "FK 49", "FK 50", "FK 51", "FK 52", "FK 53"]

    # Fungsi untuk load data dengan caching agar loading lebih cepat
    @st.cache_data
    def load_data():
        data_spk = pd.read_excel("data_spk.xlsx")
        penggunaan = pd.read_excel("penggunaan_forklift.xlsx")
        # Pastikan kolom Tanggal dikonversi ke datetime
        data_spk["Tanggal"] = pd.to_datetime(data_spk["Tanggal"])
        penggunaan["Tanggal"] = pd.to_datetime(penggunaan["Tanggal"])
        return data_spk, penggunaan

    # Load data
    data_spk, penggunaan = load_data()

    st.title("Analisis Pemakaian Forklift dan Kerusakan")

    st.markdown("Pilih rentang tanggal untuk analisis:")

    # Input tanggal dengan nilai default
    start_date = st.date_input("Tanggal Mulai", value=datetime(datetime.now().year, 1, 1))
    end_date   = st.date_input("Tanggal Akhir", value=datetime.now())

    # Handling jika tanggal mulai melebihi tanggal akhir
    if start_date > end_date:
        st.error("Error: Tanggal Mulai tidak boleh lebih besar dari Tanggal Akhir.")
    else:
        # Filter data berdasarkan rentang tanggal
        mask_spk = (data_spk["Tanggal"] >= pd.to_datetime(start_date)) & (data_spk["Tanggal"] <= pd.to_datetime(end_date))
        mask_penggunaan = (penggunaan["Tanggal"] >= pd.to_datetime(start_date)) & (penggunaan["Tanggal"] <= pd.to_datetime(end_date))
        
        spk_filtered = data_spk.loc[mask_spk].copy()
        penggunaan_filtered = penggunaan.loc[mask_penggunaan].copy()

        # --- Perhitungan Total Kerusakan/Perbaikan ---
        damage_dict = {}
        for fk in forklifts:
            # Gunakan logika 'in' untuk mengatasi data seperti "FK 16 (39987)"
            mask_fk = spk_filtered["Area / Mesin"].astype(str).str.contains(fk)
            total_damage = spk_filtered.loc[mask_fk, "Total Kerusakan"].sum()
            damage_dict[fk] = total_damage

        damage_df = pd.DataFrame(list(damage_dict.items()), columns=["No FK", "Total Kerusakan/Perbaikan"])

        # --- Perhitungan Total Pemakaian ---
        # Hanya kolom selain Tanggal
        penggunaan_cols = [col for col in penggunaan_filtered.columns if col != "Tanggal"]
        
        # Ubah nilai non-numerik menjadi NaN, kemudian diisi 0
        for col in penggunaan_cols:
            penggunaan_filtered[col] = pd.to_numeric(penggunaan_filtered[col], errors="coerce").fillna(0)
        
        usage_dict = {}
        for fk in forklifts:
            # Cari kolom yang diawali dengan nama forklift (misal "FK 14 - Shift 1", "FK 14 - Shift 2", dsb.)
            fk_cols = [col for col in penggunaan_cols if col.startswith(fk)]
            total_usage = penggunaan_filtered[fk_cols].sum().sum() if fk_cols else 0
            usage_dict[fk] = total_usage

        usage_df = pd.DataFrame(list(usage_dict.items()), columns=["No FK", "Total Pemakaian"])

        # --- Gabungkan Data Penggunaan dan Kerusakan ---
        result = pd.merge(usage_df, damage_df, on="No FK", how="outer").fillna(0)
        
        # Hitung Tingkat Kerusakan: rasio kerusakan terhadap pemakaian
        result["Tingkat Kerusakan"] = result.apply(
            lambda row: row["Total Kerusakan/Perbaikan"] / row["Total Pemakaian"] if row["Total Pemakaian"] != 0 else 0,
            axis=1
        )
        
        

        # --- Visualisasi Tingkat Kerusakan ---
        st.subheader("Visualisasi Tingkat Kerusakan")
        chart = alt.Chart(result).mark_bar().encode(
            x=alt.X("No FK:N", title="Nomor Forklift"),
            y=alt.Y("Tingkat Kerusakan:Q", title="Tingkat Kerusakan"),
            tooltip=["No FK", "Tingkat Kerusakan", "Total Kerusakan/Perbaikan", "Total Pemakaian"]
        ).properties(
            width=700,
            height=400,
            title="Tingkat Kerusakan per Forklift"
        )
        st.altair_chart(chart, use_container_width=True)
        
        # Tampilkan tabel hasil analisis
        st.subheader("Hasil Analisis")
        st.dataframe(result)
        
        
if menu == "Monitoring Forklift":
    # Baca file HM_Harian.xlsx
    df_harian = pd.read_excel("HM_Harian.xlsx")
    all_columns = df_harian.columns.tolist()

    # Ekstrak daftar forklift berdasarkan awalan nama kolom (misal "FK 14" dari "FK 14 - Shift 1")
    forklifts = sorted(set(col.split(" - ")[0] for col in all_columns))
    estimasi_dict = {}

    for fk in forklifts:
        # Cari kolom-kolom yang sesuai dengan forklift, misalnya: "FK 14 - Shift 1", "FK 14 - Shift 2", "FK 14 - Shift 3"
        fk_cols = [col for col in all_columns if col.startswith(fk)]
        
        # Untuk tiap kolom, konversi ke numerik dan ambil nilai maksimal (jika ada lebih dari 1 baris)
        max_values = []
        for col in fk_cols:
            col_max = pd.to_numeric(df_harian[col], errors='coerce').max()
            max_values.append(col_max)
        
        # Bandingkan ketiga nilai tersebut dan ambil yang paling besar
        overall_max = max(max_values)
        
        # Tambahkan 21 untuk mendapatkan estimasi HM harian
        estimasi = overall_max + 21 if pd.notnull(overall_max) else None
        estimasi_dict[fk] = estimasi

    # --- Langkah 2: Baca data_oli.xlsx dan tambahkan kolom Estimasi HM Hari Ini ---
    df_oli = pd.read_excel("data_oli.xlsx")

    # Mapping berdasarkan "No. FK" (diasumsikan di data_oli.xlsx formatnya sama, misal "FK 14")
    df_oli["Estimasi HM Hari Ini"] = df_oli["No. FK"].map(estimasi_dict)

    # --- Langkah 3: Menghitung kolom Sisa HM Ganti Oli ---
    df_oli["Sisa HM Ganti Oli mesin"] = df_oli["HM Terakhir Ganti Oli mesin"] + 250 - df_oli["Estimasi HM Hari Ini"]
    df_oli["Sisa HM Ganti Oli Hidrolik"] = df_oli["HM Terakhir Ganti Oli Hidrolik"] + 3000 - df_oli["Estimasi HM Hari Ini"]
    df_oli["Sisa HM Ganti Oli Transmisi"] = df_oli["HM Terakhir Saat Ganti Oli Transmisi"] + 2500 - df_oli["Estimasi HM Hari Ini"]
    df_oli["Sisa HM Ganti Oli Gardan"] = df_oli["HM Terakhir Saat Ganti Oli Gardan"] + 2500 - df_oli["Estimasi HM Hari Ini"]

    # --- Langkah 4: Menampilkan Tabel ---

    # Tabel non-editable: tampilkan No. FK, Status, Estimasi HM Hari Ini, dan Sisa HM Ganti Oli
    non_editable_columns = [
        "No. FK", "Status", "Estimasi HM Hari Ini",
        "Sisa HM Ganti Oli mesin", "Sisa HM Ganti Oli Hidrolik",
        "Sisa HM Ganti Oli Transmisi", "Sisa HM Ganti Oli Gardan"
    ]

    # Fungsi untuk memberi background merah jika nilai numerik <= 63, dan kuning jika <= 147
    def highlight_red(val):
        try:
            if float(val) <= 63:
                return "background-color: red"
            elif float(val) <= 147:
                return "background-color: yellow"
        except:
            return ""
        return ""

    # Terapkan format angka hanya pada kolom numerik dengan 1 digit di belakang koma
    styled_df = df_oli[non_editable_columns].style.format({
        "Estimasi HM Hari Ini": "{:.1f}",
        "Sisa HM Ganti Oli mesin": "{:.1f}",
        "Sisa HM Ganti Oli Hidrolik": "{:.1f}",
        "Sisa HM Ganti Oli Transmisi": "{:.1f}",
        "Sisa HM Ganti Oli Gardan": "{:.1f}",
    }).applymap(highlight_red)

    st.subheader("Tabel Estimasi HM dan Sisa HM Ganti Oli (Non-editable)")
    st.write(styled_df)

    # st.dataframe(df_oli[non_editable_columns], use_container_width=True)

    # Tabel editable: untuk mengupdate nilai HM terakhir
    editable_columns = [
        "No. FK", "Status", "HM Terakhir Ganti Oli mesin", "HM Terakhir Ganti Oli Hidrolik",
        "HM Terakhir Saat Ganti Oli Transmisi", "HM Terakhir Saat Ganti Oli Gardan"
    ]
    st.subheader("Update HM Terakhir Ganti Oli (Editable)")
    edited_df = st.data_editor(df_oli[editable_columns], num_rows="dynamic")

    # Tombol simpan perubahan
    if st.button("Simpan Perubahan"):
        # Pastikan 'No. FK' sebagai index untuk keduanya agar bisa di-merge/update dengan aman
        edited_df_indexed = edited_df.set_index("No. FK")
        df_oli.set_index("No. FK", inplace=True)

        # Update kolom numerik dan string, termasuk "Status"
        for col in edited_df_indexed.columns:
            df_oli[col].update(edited_df_indexed[col])

        # Reset index kembali agar bisa disimpan ke Excel
        df_oli.reset_index(inplace=True)

        # Rehitung kolom Sisa HM Ganti Oli setelah update HM terakhir
        df_oli["Sisa HM Ganti Oli mesin"] = df_oli["HM Terakhir Ganti Oli mesin"] + 250 - df_oli["Estimasi HM Hari Ini"]
        df_oli["Sisa HM Ganti Oli Hidrolik"] = df_oli["HM Terakhir Ganti Oli Hidrolik"] + 3000 - df_oli["Estimasi HM Hari Ini"]
        df_oli["Sisa HM Ganti Oli Transmisi"] = df_oli["HM Terakhir Saat Ganti Oli Transmisi"] + 2500 - df_oli["Estimasi HM Hari Ini"]
        df_oli["Sisa HM Ganti Oli Gardan"] = df_oli["HM Terakhir Saat Ganti Oli Gardan"] + 2500 - df_oli["Estimasi HM Hari Ini"]

        # Simpan data ke file Excel
        df_oli.to_excel("data_oli.xlsx", index=False)
        st.success("Data berhasil disimpan ke data_oli.xlsx")
if menu == "Tabel Kerusakan":
    st.title("Tabel Rekap Kerusakan Forklift")

    # Baca file Excel
    file_path = "data_SPK.xlsx"

    try:
        df = pd.read_excel(file_path)

        # Pastikan kolom tanggal adalah datetime
        df['Tanggal'] = pd.to_datetime(df['Tanggal'], errors='coerce')

        # Validasi apakah kolom Tanggal berhasil dikonversi
        if df['Tanggal'].isnull().all():
            st.error("Semua nilai kolom 'Tanggal' tidak valid atau tidak bisa dikonversi ke format datetime.")
            st.stop()

        # Ambil rentang tanggal dari data
        min_tanggal = df['Tanggal'].min().date()
        max_tanggal = df['Tanggal'].max().date()

        # Input tanggal mulai dan akhir (2 field terpisah)
        st.subheader("Pilih Rentang Tanggal")
        tanggal_mulai = st.date_input("Tanggal Mulai", value=min_tanggal, min_value=min_tanggal, max_value=max_tanggal)
        tanggal_akhir = st.date_input("Tanggal Akhir", value=max_tanggal, min_value=min_tanggal, max_value=max_tanggal)

        # Validasi range
        if tanggal_mulai > tanggal_akhir:
            st.warning("Tanggal Mulai tidak boleh setelah Tanggal Akhir.")
            st.stop()

        # Filter data
        start_date = pd.to_datetime(tanggal_mulai)
        end_date = pd.to_datetime(tanggal_akhir)
        df = df[(df['Tanggal'] >= start_date) & (df['Tanggal'] <= end_date)]

        # Kamus jenis kerusakan
        dict_keyword_kerusakan = {
            "Cek rutin": "cek rutin",
            "Ganti oli mesin": "ganti oli mesin",
            "Kontrol valve rembes": "kontrol valve rembes",
            "Lift turun sendiri": "lift turun sendiei",
            "Lampu utama mati": "lampu utama",
            "Ban aus/pecah/oleng": "ban",
            "Dinamo / baut dinamo bermasalah": "dinamo",
            "Pin tie rod kocak/aus": "pin tie rod",
            "Kelistrikan bermasalah": "kelistrikan",
            "Per pedal kopling putus": "pedal kopling",
            "Stir liar": "stir",
            "Klakson mati": "klakson",
            "Seal rem atas rembes": "seal rem atas",
            "Bearing lift": "bearing lift",
            "Selang hidrolik": "selang hidrolik",
            "Mesin mulai ngobos": "mesin mulai",
            "Suara mesin kasar": "mesin kasar",
            "Seal stick rembes": "seal stick",
            "Accu": "accu",
            "Persneling / selang perseneling": "persneling",
            "Suara transmisi kasar": "transmisi kasar",
            "Kampas kopling": "kampas kopling",
            "Baut pangkon / pangkon": "pangkon",
            "Pompa hidrolik rembes": "pompa hidrolik",
            "Rem kurang pakem": "rem kurang",
            "Lampu stoper dan sein mati": "lampu stoper",
            "Bushing beam axle aus": "bushing",
            "Sekring": "sekring",
            "Ganti oli transmisi": "oli transmisi",
            "Knalpot bocor": "knalpot",
            "Garpu/fork miring": "fork",
            "Ganti oli gardan": "oli gardan",
            "Ganti oli hidrolik": "oli hidrolik"
        }

        jenis_kerusakan_list = list(dict_keyword_kerusakan.keys())
        nomor_forklift = [14, 16, 17, 19, 20, 21, 22, 23, 24, 27, 28, 29, 35, 38, 40, 41, 43, 46, 49, 50, 51, 52, 53]
        nomor_forklift_str = list(map(str, nomor_forklift))

        # Pastikan kolom teks menjadi string
        df['Area / Mesin'] = df['Area / Mesin'].astype(str)
        df['Jenis Kerusakan'] = df['Jenis Kerusakan'].astype(str)

        # Dataframe hasil akhir
        hasil_df = pd.DataFrame(columns=['No', 'JENIS KERUSAKAN'] + nomor_forklift_str + ['TOTAL'])

        for i, kerusakan in enumerate(jenis_kerusakan_list, start=1):
            keyword = dict_keyword_kerusakan[kerusakan]
            baris = {'No': i, 'JENIS KERUSAKAN': kerusakan}
            total = 0
            for fk in nomor_forklift_str:
                count = df[
                    df['Area / Mesin'].str.contains(f"FK {fk}", case=False, na=False) &
                    df['Jenis Kerusakan'].str.contains(keyword, case=False, na=False)
                ].shape[0]
                baris[fk] = count
                total += count
            baris['TOTAL'] = total
            hasil_df = pd.concat([hasil_df, pd.DataFrame([baris])], ignore_index=True)

        # Hitung Lainnya
        pattern = '|'.join(dict_keyword_kerusakan.values())
        baris_lainnya = {'No': len(hasil_df) + 1, 'JENIS KERUSAKAN': 'Lainnya'}
        total_lainnya = 0
        for fk in nomor_forklift_str:
            count = df[
                df['Area / Mesin'].str.contains(f"FK {fk}", case=False, na=False) &
                ~df['Jenis Kerusakan'].str.contains(pattern, case=False, na=False)
            ].shape[0]
            baris_lainnya[fk] = count
            total_lainnya += count
        baris_lainnya['TOTAL'] = total_lainnya

        hasil_df = pd.concat([hasil_df, pd.DataFrame([baris_lainnya])], ignore_index=True)

        # Tampilkan tabel
        st.dataframe(hasil_df)

        # Visualisasi
        st.subheader("Diagram Batang Total Kerusakan per Jenis")

        chart_data = hasil_df[['JENIS KERUSAKAN', 'TOTAL']].sort_values(by='TOTAL', ascending=False)

        chart = alt.Chart(chart_data).mark_bar().encode(
            x=alt.X('TOTAL:Q', title='Jumlah Kerusakan'),
            y=alt.Y('JENIS KERUSAKAN:N', sort='-x', title='Jenis Kerusakan',
            axis=alt.Axis(labelLimit=300, labelFontSize=12, labelOverlap=False)),
            tooltip=['JENIS KERUSAKAN', 'TOTAL']
        ).properties(
            width=700,
            height=500
        )

        st.altair_chart(chart, use_container_width=True)

    except FileNotFoundError:
        st.error("File data_SPK.xlsx tidak ditemukan.")
    except Exception as e:
        st.error(f"Terjadi kesalahan: {e}")
