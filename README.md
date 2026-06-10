# Insurance OCR

Aplikasi web untuk mengekstrak data dari dokumen asuransi dan medis menggunakan AI-powered OCR, dilengkapi dengan pengecekan kelayakan klaim dan deteksi potensi fraud menggunakan RAG (Retrieval-Augmented Generation).

**Teknologi Utama:**
- **OCR & LLM**: BytePlus ModelArk (`seed-2-0-pro-260328`) — multimodal image understanding
- **RAG**: BytePlus VikingDB Knowledge Engine — semantic retrieval kebijakan asuransi
- **Backend**: FastAPI (Python)
- **Frontend**: Single-page HTML/CSS/JS

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

### OCR & Ekstraksi Data
- Upload dan proses berbagai tipe dokumen asuransi/medis secara bersamaan
- Ekstraksi data otomatis menggunakan model LLM multimodal BytePlus ModelArk
- Hasil ekstraksi ditampilkan dalam format **Markdown** dan **JSON**
- Preview gambar dokumen sebelum diproses
- Copy JSON hasil ekstraksi ke clipboard

### Claim Check & Fraud Detection (RAG + LLM)
- Setiap item/prosedur medis dari invoice di-query satu per satu ke knowledge base RAG
- RAG mencari kebijakan asuransi yang relevan (coverage, limit, batasan)
- LLM menganalisa kelayakan klaim per item: **Full / Partial / Denied**
- Deteksi potensi fraud dengan risk score 0-100:
  - Duplicate claims
  - Inflated charges vs policy limits
  - Mismatched diagnosis dan procedures
  - Suspicious provider information
  - Upcoding atau unbundling
- Rekomendasi tindakan selanjutnya

### UI/UX
- Responsive design untuk desktop dan mobile
- Tab Markdown dan JSON untuk setiap hasil ekstraksi
- Visualisasi risk score dengan progress bar
- Badge status klaim (Fully Claimable / Partially Claimable / Claim Denied)
- Tampilan RAG context yang di-retrieve dari knowledge base

## Arsitektur

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Frontend)                    │
│  Upload dokumen → OCR extraction → Claim Check + Fraud  │
└──────────┬──────────────────────────────────┬───────────┘
           │                                  │
           │  POST /api/ocr                   │  POST /api/claim-check
           │  (FormData: file + doc_type)     │  (FormData: ocr_results JSON)
           ▼                                  ▼
┌──────────────────────────────────────────────────────────┐
│                  FastAPI Backend (app.py)                 │
│                                                          │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────┐  │
│  │  OCR Engine  │  │  RAG Service │  │  LLM Analyzer  │  │
│  │  (base64     │  │  (VikingDB   │  │  (seed-2-0-    │  │
│  │   encode →   │  │   query per  │  │   pro-260328)  │  │
│  │   ModelArk)  │  │   item)      │  │                │  │
│  └──────┬───────┘  └──────┬───────┘  └───────┬────────┘  │
└─────────┼─────────────────┼──────────────────┼───────────┘
          │                 │                  │
          ▼                 ▼                  ▼
┌─────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  ModelArk   │  │  VikingDB RAG    │  │  ModelArk LLM    │
│  Vision API │  │  Knowledge Base  │  │  Chat API        │
│             │  │  (policy data)   │  │  (analysis)      │
└─────────────┘  └──────────────────┘  └──────────────────┘
```

## Struktur Proyek

```
Insurance-OCR/
├── app.py                  # Backend FastAPI: OCR, RAG, Claim Check, Fraud Detection
├── rag_service.py          # RAG client: VikingDB Knowledge Engine integration
├── static/
│   └── index.html          # Frontend (HTML/CSS/JS) single-page app
├── Demo Data Extract/      # Contoh dokumen untuk testing
│   ├── insurance_card-1.png
│   ├── insurance_invoice.png
│   ├── CMS1500.png
│   └── ML-10224-DriversLicense-2.png
├── Insurance_claimable.csv # Data klaim referensi (untuk RAG knowledge base)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (JANGAN commit ke git)
├── .env.example            # Template environment variables
├── .gitignore              # Git ignore rules
└── README.md               # Dokumentasi ini
```

## Instalasi

### Prasyarat

- Python 3.7+
- BytePlus ModelArk API Key — [API Key Management](https://console.byteplus.com/ark/region:ark+ap-southeast-1/apiKey)
- BytePlus VikingDB Knowledge Engine API Key (untuk fitur RAG)

### Langkah Instalasi

```bash
cd Insurance-OCR
pip install -r requirements.txt
cp .env.example .env
# Edit .env dengan API key kamu
```

## Konfigurasi

Edit file `.env`:

| Variable | Deskripsi | Default |
|---|---|---|
| `ARK_API_KEY` | API key BytePlus ModelArk | *(wajib diisi)* |
| `ARK_BASE_URL` | Base URL API ModelArk | `https://ark.ap-southeast.bytepluses.com/api/v3` |
| `MODEL` | Model ID untuk OCR & LLM | `seed-2-0-pro-260328` |
| `RAG_API_KEY` | API key VikingDB Knowledge Engine | *(opsional)* |
| `RAG_HOST` | Host VikingDB Knowledge Engine | `api-knowledgebase.mlp.ap-southeast-1.bytepluses.com` |
| `RAG_SERVICE_RESOURCE_ID` | Service resource ID knowledge base | *(opsional, untuk service chat)* |
| `RAG_COLLECTION_NAME` | Nama knowledge base collection | *(opsional, untuk search)* |
| `RAG_RESOURCE_ID` | Resource ID knowledge base | *(opsional, untuk search)* |

### Region yang Tersedia

| Service | Region | Base URL |
|---|---|---|
| ModelArk | Asia Pacific | `https://ark.ap-southeast.bytepluses.com/api/v3` |
| ModelArk | Europe | `https://ark.eu-west.bytepluses.com/api/v3` |
| VikingDB RAG | Asia Pacific (Johor) | `api-knowledgebase.mlp.ap-southeast-1.bytepluses.com` |
| VikingDB RAG | Hong Kong | `api-knowledgebase.mlp.cn-hongkong.bytepluses.com` |

## Menjalankan Aplikasi

```bash
python3 app.py
```

Aplikasi berjalan di **http://localhost:8000**.

## Tipe Dokumen yang Didukung

### 1. Insurance Card (`insurance_card`)

Kartu asuransi kesehatan.

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

Invoice/tagihan medis. **Field `items[].description` digunakan sebagai input utama untuk RAG query.**

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

Form klaim asuransi kesehatan standar AS (HCFA-1500).

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

SIM atau kartu identitas.

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

### 5. Tipe Dokumen Lainnya (via dropdown "Additional Document")

| Tipe | `doc_type` | Deskripsi |
|---|---|---|
| Medical Record | `medical_record` | Rekam medis |
| Receipt / Kuitansi | `receipt` | Kwitansi pembayaran |
| Prescription / Perincian Obat | `prescription` | Resep obat |
| Lab Result | `lab_result` | Hasil laboratorium |
| Other Document | `other` | Dokumen lainnya |

## API Reference

### `POST /api/ocr`

Memproses satu dokumen gambar dan mengembalikan data yang diekstrak dalam format Markdown + JSON.

**Request**: `multipart/form-data`

| Parameter | Tipe | Deskripsi |
|---|---|---|
| `file` | File | File gambar (PNG, JPG, dll) |
| `doc_type` | String | Tipe dokumen (lihat daftar di atas) |

**Response**:

```json
{
  "doc_type": "insurance_card",
  "filename": "insurance_card-1.png",
  "result": {
    "markdown": "# Insurance Card\n\n| Field | Value |\n|---|---|...",
    "json": {
      "plan_name": "Group Insurance of America Community Plan",
      "member_name": "JOHN DOE",
      "member_id": "11-2234-10190",
      ...
    }
  }
}
```

### `POST /api/ocr/batch`

Memproses insurance card + medical invoice sekaligus.

**Request**: `multipart/form-data`

| Parameter | Tipe | Deskripsi |
|---|---|---|
| `insurance_card` | File | *(opsional)* Gambar kartu asuransi |
| `medical_invoice` | File | *(opsional)* Gambar invoice medis |

### `POST /api/claim-check`

Menganalisa kelayakan klaim dan potensi fraud menggunakan RAG + LLM.
**Setiap item `description` dari invoice di-query satu per satu ke RAG knowledge base.**

**Request**: `multipart/form-data`

| Parameter | Tipe | Deskripsi |
|---|---|---|
| `ocr_results` | String | JSON string hasil OCR dari frontend |

**Response**:

```json
{
  "rag_context": [
    {
      "item": "Full body checkup (PPD)",
      "amount": "$745.00",
      "answer": "Full body checkup is covered up to $500 per year...",
      "source": "knowledge_service_chat"
    }
  ],
  "analysis": {
    "claim_status": "partial",
    "claim_status_reason": "Some items exceed policy coverage limits",
    "eligible_items": [
      {"item": "Full body checkup", "allowed_amount": "$500.00", "reason": "Annual limit"}
    ],
    "non_eligible_items": [
      {"item": "Infection check", "reason": "Not covered under basic plan"}
    ],
    "total_eligible_amount": "$500.00",
    "fraud_analysis": {
      "risk_level": "low",
      "risk_score": 15,
      "indicators": ["Slight discrepancy in billed vs allowed amount"],
      "explanation": "No major fraud indicators detected..."
    },
    "recommendations": ["Verify provider credentials", "Request additional documentation"],
    "markdown": "## Claim Analysis Report\n\n..."
  }
}
```

### `GET /`

Menampilkan halaman frontend.

## Alur Kerja Aplikasi

### Alur OCR (Ekstraksi Data)

```
1. User upload dokumen → klik "Extract Data"
2. Frontend kirim gambar ke POST /api/ocr (satu per satu)
3. Backend encode gambar ke base64
4. Pilih prompt OCR sesuai doc_type
5. Kirim ke BytePlus ModelArk API (multimodal: image + text)
6. ModelArk return markdown + JSON terstruktur
7. Frontend tampilkan hasil di tab Markdown & JSON
```

### Alur Claim Check (RAG + Fraud Detection)

```
1. User klik "Check Claim Eligibility & Fraud Analysis"
2. Frontend kirim semua hasil OCR ke POST /api/claim-check
3. Backend ekstrak items[].description dari medical invoice
4. Untuk SETIAP item description, query RAG:
   → "Is 'Full body checkup' ($745.00) covered under the policy?"
5. RAG (VikingDB) mencari data polis yang relevan
6. Hasil RAG + data OCR dikirim ke LLM (ModelArk) untuk analisa:
   a. Kelayakan klaim per item (full/partial/denied)
   b. Deteksi fraud (risk score 0-100)
   c. Rekomendasi tindakan
7. Frontend tampilkan:
   - Claim Status Badge
   - Eligible vs Non-Eligible Items
   - Fraud Risk Score + Indicators
   - RAG Retrieved Policy Context
   - Full Analysis Report (Markdown)
```
