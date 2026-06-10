# Insurance OCR

Aplikasi web untuk mengekstrak data dari dokumen asuransi dan medis menggunakan AI-powered OCR. Aplikasi ini memanfaatkan model **BytePlus ModelArk (seed-2-0-pro-260328)** untuk melakukan pengenalan dan ekstraksi teks dari gambar dokumen.

## Daftar Isi

- [Fitur](#fitur)
- [Arsitektur](#arsitektur)
- [Struktur Proyek](#struktur-proyek)
- [Instalasi](#instalasi)
- [Konfigurasi](#konfigurasi)
- [Menjalankan Aplikasi](#menjalankan-aplikasi)
- [Tipe Dokumen yang Didukung](#tipe-dokumen-yang-didukung)
- [API Reference](#api-reference)
- [Alur Kerja Aplikasi](#alur-kerja-aplikasi)

## Fitur

- Upload dan proses berbagai tipe dokumen asuransi/medis secara bersamaan
- Ekstraksi data otomatis menggunakan model LLM multimodal (BytePlus ModelArk)
- Hasil ekstraksi ditampilkan dalam format **Markdown** dan **JSON**
- Preview gambar dokumen sebelum diproses
- Copy JSON hasil ekstraksi ke clipboard
- Responsive design untuk desktop dan mobile

## Arsitektur

```
Browser (Frontend)
    │
    │  POST /api/ocr  (FormData: file + doc_type)
    ▼
FastAPI Backend (app.py)
    │
    │  OpenAI SDK (compatible)
    ▼
BytePlus ModelArk API
(https://ark.ap-southeast.bytepluses.com/api/v3)
    │
    │  Model: seed-2-0-pro-260328
    ▼
Response: { markdown, json }
```

- **Backend**: FastAPI (Python) menerima upload gambar, meng-encode ke base64, lalu mengirim ke ModelArk API
- **Frontend**: Single-page HTML/CSS/JS dengan form upload dan tampilan hasil
- **AI Model**: BytePlus ModelArk `seed-2-0-pro-260328` untuk multimodal understanding (image + text)

## Struktur Proyek

```
Insurance-OCR/
├── app.py                  # Backend FastAPI + OCR logic
├── static/
│   └── index.html          # Frontend (HTML/CSS/JS)
├── Demo Data Extract/      # Contoh dokumen untuk testing
│   ├── insurance_card-1.png
│   ├── insurance_invoice.png
│   ├── CMS1500.png
│   └── ML-10224-DriversLicense-2.png
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (JANGAN commit ke git)
├── .env.example            # Template environment variables
└── README.md               # Dokumentasi ini
```

## Instalasi

### Prasyarat

- Python 3.7+
- BytePlus ModelArk API Key (dapatkan dari [API Key Management](https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey))

### Langkah Instalasi

1. Clone atau masuk ke direktori proyek:
   ```bash
   cd Insurance-OCR
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Salin file `.env.example` ke `.env` dan isi API key:
   ```bash
   cp .env.example .env
   ```

## Konfigurasi

Edit file `.env` dengan nilai yang sesuai:

| Variable | Deskripsi | Default |
|---|---|---|
| `ARK_API_KEY` | API key BytePlus ModelArk | *(wajib diisi)* |
| `ARK_BASE_URL` | Base URL API ModelArk | `https://ark.ap-southeast.bytepluses.com/api/v3` |
| `MODEL` | Model ID yang digunakan | `seed-2-0-pro-260328` |

### Region yang Tersedia

| Region | Base URL |
|---|---|
| Asia Pacific (ap-southeast-1) | `https://ark.ap-southeast.bytepluses.com/api/v3` |
| Europe (eu-west-1) | `https://ark.eu-west.bytepluses.com/api/v3` |

## Menjalankan Aplikasi

```bash
python3 app.py
```

Aplikasi akan berjalan di `http://localhost:8000`.

## Tipe Dokumen yang Didukung

### 1. Insurance Card (`insurance_card`)

Kartu asuransi kesehatan. Field yang diekstrak:

| Field | Deskripsi |
|---|---|
| `plan_name` | Nama plan asuransi |
| `health_plan_code` | Kode health plan |
| `plan_reference_number` | Nomor referensi plan |
| `member_name` | Nama member |
| `member_id` | ID member |
| `group_number` | Nomor grup |
| `pcp_name` | Nama primary care physician |
| `pcp_phone` | Telepon PCP |
| `payer_id` | ID payer |
| `rx_bin` | Pharmacy BIN number |
| `rx_grp` | Pharmacy group number |
| `rx_pcn` | Pharmacy PCN number |
| `issuer` | Penerbit/administrator asuransi |

### 2. Medical Invoice (`medical_invoice`)

Invoice/tagihan medis. Field yang diekstrak:

| Field | Deskripsi |
|---|---|
| `hospital_name` | Nama rumah sakit/provider |
| `issuer_contact` | Kontak penerbit |
| `issuer_address` | Alamat penerbit |
| `issuer_city_state` | Kota & negara bagian penerbit |
| `issuer_zip` | Kode pos penerbit |
| `issuer_phone` | Telepon penerbit |
| `issuer_email` | Email penerbit |
| `invoice_number` | Nomor invoice |
| `invoice_date` | Tanggal invoice |
| `bill_to_name` | Nama penerima tagihan |
| `bill_to_address` | Alamat penerima |
| `bill_to_city_state` | Kota & negara bagian penerima |
| `bill_to_zip` | Kode pos penerima |
| `items` | Array line items (description, amount) |
| `subtotal` | Subtotal |
| `discount` | Diskon |
| `tax` | Pajak |
| `total` | Total |
| `support_phone` | Telepon support |
| `support_email` | Email support |

### 3. CMS-1500 Claim Form (`cms1500`)

Form klaim asuransi kesehatan standar AS (HCFA-1500). Field yang diekstrak:

| Field | Deskripsi |
|---|---|
| `insurance_type` | Tipe asuransi (Medicare/Medicaid/dll) |
| `insured_id_number` | ID tertanggung (field 1a) |
| `patient_name` | Nama pasien (field 2) |
| `patient_dob` | Tanggal lahir pasien (field 3) |
| `patient_sex` | Jenis kelamin pasien (field 3) |
| `insured_name` | Nama tertanggung (field 4) |
| `patient_address` | Alamat pasien (field 5) |
| `patient_city/state/zip/phone` | Detail alamat pasien |
| `patient_relationship` | Hubungan dengan tertanggung (field 6) |
| `insured_address` | Alamat tertanggung (field 7) |
| `patient_marital_status` | Status pernikahan (field 8) |
| `insured_policy_group_number` | Nomor polis/grup (field 11) |
| `insured_dob/sex` | DOB & jenis kelamin tertanggung (field 11a) |
| `insurance_plan_name` | Nama plan asuransi (field 11c) |
| `patient_signature` | Tanda tangan pasien (field 12) |
| `patient_signature_date` | Tanggal tanda tangan |
| `insured_signature` | Tanda tangan tertanggung (field 13) |
| `date_of_current_illness` | Tanggal sakit/cidera (field 14) |
| `diagnosis_codes` | Array kode diagnosis ICD (field 21) |
| `service_lines` | Array layanan (field 24): from_date, to_date, place_of_service, type_of_service, cpt_code, diagnosis_pointer, charges, days_units |
| `total_charge` | Total biaya (field 28) |
| `provider_name` | Nama provider (field 33) |
| `provider_npi` | NPI provider (field 33) |

### 4. Driver's License / ID Card (`drivers_license`)

SIM atau kartu identitas. Field yang diekstrak:

| Field | Deskripsi |
|---|---|
| `document_type` | Tipe dokumen |
| `expiration_date` | Tanggal kadaluarsa |
| `license_number` | Nomor SIM |
| `license_class` | Kelas SIM |
| `endorsements` | Endorsement |
| `last_name` | Nama belakang |
| `first_name` | Nama depan |
| `address_street` | Alamat jalan |
| `address_city_state_zip` | Kota, negara bagian, ZIP |
| `date_of_birth` | Tanggal lahir |
| `sex` | Jenis kelamin |
| `hair_color` | Warna rambut |
| `eye_color` | Warna mata |
| `height` | Tinggi badan |
| `weight` | Berat badan |
| `organ_donor` | Status donor organ |

### 5. Tipe Dokumen Lainnya

Tersedia juga melalui dropdown "Additional Document":

- **Medical Record** (`medical_record`) - Rekam medis
- **Receipt / Kuitansi** (`receipt`) - Kwitansi pembayaran
- **Prescription / Perincian Obat** (`prescription`) - Resep obat
- **Lab Result** (`lab_result`) - Hasil laboratorium
- **Other Document** (`other`) - Dokumen lainnya

## API Reference

### `POST /api/ocr`

Memproses satu dokumen gambar dan mengembalikan data yang diekstrak.

**Request**: `multipart/form-data`

| Parameter | Tipe | Deskripsi |
|---|---|---|
| `file` | File | File gambar (PNG, JPG, dll) |
| `doc_type` | String | Tipe dokumen: `insurance_card`, `medical_invoice`, `cms1500`, `drivers_license`, `medical_record`, `receipt`, `prescription`, `lab_result`, `other` |

**Response**:

```json
{
  "doc_type": "insurance_card",
  "filename": "insurance_card-1.png",
  "result": {
    "markdown": "# Insurance Card\n\n| Field | Value |\n|---|---|\n| Member Name | JOHN DOE |\n...",
    "json": {
      "plan_name": "Group Insurance of America Community Plan",
      "member_name": "JOHN DOE",
      "member_id": "11-2234-10190",
      "group_number": "AAAAA",
      ...
    }
  }
}
```

### `POST /api/ocr/batch`

Memproses beberapa dokumen sekaligus (insurance card + medical invoice).

**Request**: `multipart/form-data`

| Parameter | Tipe | Deskripsi |
|---|---|---|
| `insurance_card` | File | *(opsional)* Gambar kartu asuransi |
| `medical_invoice` | File | *(opsional)* Gambar invoice medis |

**Response**:

```json
{
  "insurance_card": {
    "doc_type": "insurance_card",
    "filename": "card.png",
    "result": { ... }
  },
  "medical_invoice": {
    "doc_type": "medical_invoice",
    "filename": "invoice.png",
    "result": { ... }
  }
}
```

### `GET /`

Menampilkan halaman frontend (index.html).

## Alur Kerja Aplikasi

```
1. User membuka http://localhost:8000
          │
2. User mengupload gambar dokumen ke claim form
   (Insurance Card, Medical Invoice, CMS-1500, SIM, dll)
          │
3. User klik "Extract Data"
          │
4. Frontend mengirim setiap gambar ke POST /api/ocr
   beserta doc_type yang sesuai
          │
5. Backend:
   a. Membaca file gambar → encode ke base64
   b. Memilih prompt OCR sesuai doc_type
   c. Mengirim ke BytePlus ModelArk API
      (model: seed-2-0-pro-260328)
   d. Menerima response berisi markdown + json
   e. Parse JSON response
   f. Return ke frontend
          │
6. Frontend menampilkan hasil:
   - Tab Markdown: data terformat dalam tabel/list
   - Tab JSON: data terstruktur dengan tombol Copy
```
