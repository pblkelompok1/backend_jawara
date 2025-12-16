import jinja2
from datetime import datetime

# 1. Definisi Template Jinja2 (HTML/CSS)
#    Ini meniru tata letak surat resmi Indonesia (font Times New Roman, tabel untuk aligment)
template_content = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <title>Surat Pernyataan Usaha</title>
    <style>
        body {
            font-family: 'Times New Roman', Times, serif;
            font-size: 12pt;
            line-height: 1.5;
            margin: 0;
            padding: 2cm 2cm; /* Margin standar surat */
            color: #000;
        }
        .container {
            max-width: 21cm; /* Ukuran A4 */
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 20px;
        }
        .header h2 {
            text-decoration: underline;
            margin: 0;
            text-transform: uppercase;
            font-size: 14pt;
        }
        .content {
            margin-top: 20px;
            text-align: justify;
        }
        /* Style untuk tabel form agar titik dua sejajar */
        .form-table {
            width: 100%;
            margin-left: 20px;
            margin-bottom: 15px;
            border-collapse: collapse;
        }
        .form-table td {
            vertical-align: top;
            padding: 2px 0;
        }
        .label-col {
            width: 160px;
        }
        .separator-col {
            width: 20px;
            text-align: center;
        }
        
        /* Area Tanda Tangan */
        .signature-section {
            margin-top: 40px;
            width: 100%;
        }
        .ttd-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 30px;
        }
        .ttd-box {
            text-align: center;
            width: 250px;
        }
        .ttd-lurah {
            text-align: center;
            margin: 0 auto;
            width: 300px;
        }
        
        /* Style untuk QR Code Dummy */
        .qr-placeholder {
            margin: 10px auto;
            border: 1px dashed #ccc;
            padding: 5px;
            width: 80px;
            height: 80px;
        }
        .qr-placeholder img {
            width: 100%;
            height: 100%;
        }
        .nama-pejabat {
            font-weight: bold;
            text-decoration: underline;
            margin-top: 5px;
        }
        .nip {
            font-size: 10pt;
        }
    </style>
</head>
<body>

<div class="container">
    <!-- Judul -->
    <div class="header">
        <h2>SURAT PERNYATAAN USAHA</h2>
    </div>

    <!-- Isi Surat -->
    <div class="content">
        <p>Yang bertandatangan di bawah ini:</p>

        <table class="form-table">
            <tr>
                <td class="label-col">Nama</td>
                <td class="separator-col">:</td>
                <td>{{ nama_pemohon }}</td>
            </tr>
            <tr>
                <td class="label-col">NIK</td>
                <td class="separator-col">:</td>
                <td>{{ nik }}</td>
            </tr>
            <tr>
                <td class="label-col">Tempat/Tgl Lahir</td>
                <td class="separator-col">:</td>
                <td>{{ tempat_lahir }}, {{ tgl_lahir }}</td>
            </tr>
            <tr>
                <td class="label-col">Jenis Kelamin</td>
                <td class="separator-col">:</td>
                <td>{{ jenis_kelamin }}</td>
            </tr>
            <tr>
                <td class="label-col">No. Telp/HP</td>
                <td class="separator-col">:</td>
                <td>{{ no_hp }}</td>
            </tr>
            <tr>
                <td class="label-col">Alamat</td>
                <td class="separator-col">:</td>
                <td>{{ alamat_rumah }}</td>
            </tr>
        </table>

        <p>Dengan ini menyatakan bahwa saya benar-benar memiliki usaha :</p>

        <table class="form-table">
            <tr>
                <td class="label-col">Nama Usaha</td>
                <td class="separator-col">:</td>
                <td>{{ nama_usaha }}</td>
            </tr>
            <tr>
                <td class="label-col">Jenis</td>
                <td class="separator-col">:</td>
                <td>{{ jenis_usaha }}</td>
            </tr>
            <tr>
                <td class="label-col">Luas Usaha</td>
                <td class="separator-col">:</td>
                <td>{{ luas_usaha }}</td>
            </tr>
            <tr>
                <td class="label-col">Alamat</td>
                <td class="separator-col">:</td>
                <td>{{ alamat_usaha }}</td>
            </tr>
        </table>

        <p>
            Surat Pernyataan ini saya buat dengan sebenar-benarnya dan untuk dipergunakan sebagai
            persyaratan <strong>{{ tujuan_surat }}</strong>.
        </p>

        <p>
            Demikian Surat Pernyataan ini saya buat dengan sebenar-benarnya dan apabila pernyataan ini
            tidak benar, maka saya bersedia dituntut sesuai peraturan perundang-undangan yang berlaku.
            Dan segala akibat yang timbul dari surat pernyataan ini menjadi tanggungjawab saya.
        </p>
    </div>

    <!-- Bagian Tanda Tangan -->
    <div class="signature-section">
        <!-- Tanggal dan Yang Menyatakan -->
        <div style="text-align: right; margin-bottom: 30px;">
            <p>Yogyakarta, {{ tanggal_surat }}<br>Yang Menyatakan</p>
            <div style="height: 70px; display: flex; align-items: center; justify-content: flex-end;">
                <div style="border: 1px solid #999; width: 60px; height: 30px; text-align: center; font-size: 8pt; line-height: 30px; margin-right: 10px; color: #999;">
                    Meterai<br>10.000
                </div>
            </div>
            <p class="nama-pejabat" style="text-decoration: none;">( {{ nama_pemohon }} )</p>
        </div>

        <p style="text-align: center;">Mengetahui,</p>

        <!-- Baris RT dan RW -->
        <div class="ttd-row">
            <div class="ttd-box">
                <p>Ketua RW {{ nomor_rw }}</p>
                <!-- Dummy QR Code RW -->
                <div class="qr-placeholder">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=Sign:{{ nama_rw }}" alt="QR RW">
                </div>
                <p class="nama-pejabat">( {{ nama_rw }} )</p>
            </div>

            <div class="ttd-box">
                <p>Ketua RT {{ nomor_rt }}</p>
                <!-- Dummy QR Code RT -->
                <div class="qr-placeholder">
                    <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=Sign:{{ nama_rt }}" alt="QR RT">
                </div>
                <p class="nama-pejabat">( {{ nama_rt }} )</p>
            </div>
        </div>

        <!-- Lurah (Tengah Bawah) -->
        <div class="ttd-lurah">
            <p>LURAH MUJA MUJU</p>
            <!-- Dummy QR Code Lurah -->
            <div class="qr-placeholder">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=Sign:{{ nama_lurah }}_Valid" alt="QR Lurah">
            </div>
            <p class="nama-pejabat">{{ nama_lurah }}</p>
            <p class="nip">No. {{ nomor_register_kelurahan }}</p>
        </div>
    </div>
</div>

</body>
</html>
"""

# 2. Data Dummy untuk Pengisian (Context)
data_context = {
    # Data Pemohon
    "nama_pemohon": "Budi Santoso",
    "nik": "3471012345678900",
    "tempat_lahir": "Sleman",
    "tgl_lahir": "12 Agustus 1985",
    "jenis_kelamin": "Laki-laki",
    "no_hp": "0812-3456-7890",
    "alamat_rumah": "Jl. Melati No. 45, RT 02 RW 05, Muja Muju, Yogyakarta",
    
    # Data Usaha
    "nama_usaha": "Warung Makan Berkah",
    "jenis_usaha": "Kuliner",
    "luas_usaha": "4 x 5 meter",
    "alamat_usaha": "Jl. Kusumanegara No. 10, Yogyakarta",
    "tujuan_surat": "Pengajuan KUR BRI",
    
    # Meta Surat
    "tanggal_surat": datetime.now().strftime("%d %B %Y"),
    
    # Data Pejabat (Dummy sesuai request)
    "nomor_rt": "02",
    "nama_rt": "Sutrisno, S.Pd",  # Dummy Name RT
    
    "nomor_rw": "05",
    "nama_rw": "Hj. Siti Aminah",  # Dummy Name RW
    
    "nama_lurah": "Drs. H. Joko Widodo, M.Si", # Dummy Name Lurah
    "nomor_register_kelurahan": "400/123/Kel-MJ/2024" # Dummy No Register
}

# 3. Proses Rendering
def render_template():
    # Setup Jinja2 Environment
    env = jinja2.Environment(loader=jinja2.BaseLoader())
    template = env.from_string(template_content)
    
    # Render template dengan data
    output_html = template.render(**data_context)
    
    # Simpan ke file untuk dilihat user
    output_filename = "surat_pernyataan_usaha_generated.html"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(output_html)
    
    print(f"Berhasil membuat surat! Silakan buka file '{output_filename}' di browser Anda.")
    print("-" * 30)
    print("Preview Data Pejabat (Digital Sign):")
    print(f"Lurah: {data_context['nama_lurah']}")
    print(f"RT: {data_context['nama_rt']}")
    print(f"RW: {data_context['nama_rw']}")

if __name__ == "__main__":
    render_template()