# 💰 Finance Dashboard System

## 📌 Overview

The **Finance Dashboard System** is a full-stack web application built using **Flask, MySQL, HTML, CSS, and Bootstrap**.
It allows users to manage financial records (income & expenses) with **role-based access control** and view dashboard analytics.

---

## 🚀 Features

### 👥 User Management

* Role-based access control (Admin, Analyst, Viewer)
* Secure login system
* Active/Inactive user management

### 💵 Financial Records

* Create, update, delete records
* Categorize income and expenses
* Filter records by date, type, and category

### 📊 Dashboard Analytics

* Total Income
* Total Expenses
* Net Balance
* Category-wise breakdown
* Recent transactions

### 🔐 Security

* Password hashing (Werkzeug)
* Session-based authentication (Flask-Login)
* Role-based route protection

---

## 🏗️ Tech Stack

* **Backend:** Python (Flask)
* **Database:** MySQL (Local)
* **Frontend:** HTML, CSS, Bootstrap
* **ORM:** SQLAlchemy

---

## 📁 Project Structure

```
finance_dashboard/
│
├── app.py
├── requirements.txt
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── records.html
│   ├── create_record.html
│   ├── edit_record.html
│   └── users.html
│
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/finance-dashboard-system.git
cd finance-dashboard-system
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🗄️ Database Setup (Local MySQL)

1. Open MySQL
2. Create database:

```sql
CREATE DATABASE finance_dashboard;
```

3. Update credentials in `app.py`:

```python
MYSQL_HOST = '127.0.0.1'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'your-password'
MYSQL_DB = 'finance_dashboard'
```

---

## ▶️ Run the Application

```bash
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

## 🔑 Demo Credentials

| Role    | Username | Password   |
| ------- | -------- | ---------- |
| Admin   | admin    | admin123   |
| Analyst | analyst  | analyst123 |
| Viewer  | viewer   | viewer123  |

---

## ⚠️ Known Limitations

* Works only on local MySQL setup
* Not deployed on cloud environment
* Basic UI (can be enhanced further)

---

## 🚀 Future Improvements

* Cloud database integration
* Deployment on Render/AWS
* API integration (FastAPI)
* Advanced analytics charts
* Pagination & search

---

## 👨‍💻 Author

**Syed Sadain**

---

## 📎 License

This project is for educational and assignment purposes.
