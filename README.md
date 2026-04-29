# 💊 Ashirwad Medicos – Django eCommerce Web Application

## 🧾 Project Overview

Ashirwad Medicos is a full-stack web-based eCommerce application developed using the Django framework. The system is designed specifically for an online medical store, allowing users to browse medicines, add them to cart, and place orders conveniently.

The application also includes an admin (owner) panel to manage products, monitor orders, and update delivery status. This project demonstrates the implementation of real-world web application features such as authentication, database relationships, and dynamic content rendering.

---

## 🎯 Objectives

* To develop an online medical store using Django
* To implement secure user authentication system
* To manage medicines, cart, wishlist, and orders
* To provide admin control over product and delivery system
* To understand full-stack development using MVT architecture

---

## 🏗️ System Architecture

The project follows **Django MVT (Model-View-Template)** architecture:

* **Model** → Handles database (Product, Cart, Order, etc.)
* **View** → Contains business logic and request handling
* **Template** → Frontend interface (HTML + CSS)

---

## 🛠️ Technologies Used

* **Frontend**: HTML, CSS (Amazon-style UI)
* **Backend**: Python, Django Framework
* **Database**: SQLite
* **Authentication**: Django built-in system
* **Static Files**: CSS via Django static system
* **Media Files**: Product images stored in media folder

---

## 📂 Project Modules

### 👤 User Module

* User Registration and Login
* Browse medicines/products
* Search functionality
* Add to Cart
* Wishlist management
* Place order
* View order history

---

### 🛒 Cart Module

* Add/remove products
* Update quantity
* Auto calculation of total price

---

### 📦 Order Module

* Order creation after checkout
* Order tracking (Processing / Delivered / Cancelled)
* Order history for users

---

### 👑 Admin (Owner) Module

* Admin dashboard
* Add/Delete products
* Manage stock
* Update order status
* View total orders and revenue

---

## 🔐 Key Features

* Secure login and registration system
* Session-based authentication
* Dynamic product search
* Cart and wishlist system
* Order placement and tracking
* Admin control panel
* Clean and responsive UI

---

## ⚙️ Installation & Setup

### Step 1: Clone Project

```bash
git clone <your-repo-link>
cd project-folder
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install django
```

### Step 4: Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Admin User

```bash
python manage.py createsuperuser
```

### Step 6: Run Server

```bash
python manage.py runserver
```

---

## 🌐 Usage

* Open browser → `http://127.0.0.1:8000/`
* Register/Login as customer
* Browse medicines and add to cart
* Place orders using checkout
* Admin can manage products and orders

---

## 🧠 Concepts Implemented

* Django ORM (Object Relational Mapping)
* ForeignKey relationships
* Session management
* Form handling (GET/POST)
* Static & Media file handling
* Role-based access (Admin vs Customer)

---

## ⚠️ Limitations

* No online payment gateway
* Uses SQLite (not suitable for large scale)
* Basic UI (can be enhanced further)

---

## 🚀 Future Enhancements

* Payment integration (Razorpay / Stripe)
* Prescription upload feature
* Product categories and filters
* Email notifications
* Deployment on cloud

---

## 📌 Conclusion

Ashirwad Medicos successfully demonstrates a complete eCommerce system for a medical store. It includes both frontend and backend functionalities, user authentication, and admin control. This project helps in understanding real-world web development using Django.

---

## 👨‍💻 Developed By

**Hardik**
Lovely Professional University (LPU)

---
