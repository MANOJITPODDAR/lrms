# Directorate of Education, Library Requisition Management System
## A&N Islands — Internal Staff Portal

---

## Setup & Run

```bash
pip install flask
python app.py
# Visit: http://localhost:5000
```

---

## Login Credentials

### Master Admin
| Username | Password |
|----------|----------|
| masteradmin | Master@2025 |

### Library Admins
| Username | Password | Library |
|----------|----------|---------|
| wandoor | Wandoor@123 | Zonal Library Wandoor |
| manpur | Manpur@123 | Zonal Library Manpur |
| ferrargunj | Ferrar@123 | Zonal Library Ferrargunj |
| wimberlygunj | Wimberly@123 | Zonal Library Wimberlygunj |
| kadamtala | Kadam@123 | Zonal Library Kadamtala |
| bakultala | Bakul@123 | Zonal Library Bakultala |
| rangat | Rangat@123 | Zonal Library Rangat |
| billiground | Billi@123 | Zonal Library Billiground |
| diglipur | Digli@123 | Zonal Library Diglipur |
| vijaynagar | Vijay@123 | Zonal Library Vijay Nagar |
| campbellbay | Campbell@123 | Zonal Library Campbell Bay |
| kamorta | Kamort@123 | Zonal Library Kamorta |
| katchal | Katch@123 | Zonal Library Katchal |
| hutbay | Hutbay@123 | Zonal Library Hutbay |
| rkpur | Rkpur@123 | Zonal Library R K Pur |
| swarajdweep | Swaraj@123 | Zonal Library Swaraj Dweep |
| shaheed | Shaheed@123 | Zonal Library Shaheed Dweep |
| longisland | Long@123 | Zonal Library Long Island |

---

## Features

### Dashboard (Request Form)
- Secure login per library admin
- Submit requisitions: BOOK / MAGAZINE / NEWSPAPER
- Book sub-types: Competitive Book / Subject Book / Others (with free text)
- Membership card number (optional)
- Stats: Today's, this month's, and total requests
- Reports button opens in new browser tab

### Reports Page (new tab)
- **Master Admin**: View ALL libraries, filter by date + library
- **Library Admin**: View ONLY their own library's data
- Summary cards: total, books, magazines, newspapers
- Full requisitions table with date, library, item, type, sub-type
- Top 10 most requested items with animated bar chart
- Print / Export to PDF support

---

## Access Control
- Master admin can view and submit for any library
- Library admins can only view/submit for their own branch
- Sessions expire on browser close
