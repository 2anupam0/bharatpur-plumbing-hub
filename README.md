# Bharatpur Plumbing Hub

A production-ready plumbing hardware shop website with Django backend, Tailwind CSS frontend, and WhatsApp ordering integration.

## Quick Start

### 1. Setup Virtual Environment

```bash
cd "hardware plumbing"
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Migrations

```bash
python manage.py makemigrations shop
python manage.py migrate
```

### 4. Create Superuser (Admin Access)

```bash
python manage.py createsuperuser
```

Enter username, email, and password when prompted.

### 5. Seed Sample Data

```bash
python manage.py seed_data
```

This loads 6 categories and 30 sample products.

### 6. Run Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000**

Admin Panel: **http://127.0.0.1:8000/admin**

## Project Structure

```
hardware plumbing/
├── manage.py
├── requirements.txt
├── db.sqlite3
├── plumbing_shop/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── shop/
│   ├── __init__.py
│   ├── models.py          # Category, Product, ContactInquiry, SiteSettings
│   ├── admin.py            # Admin panel configuration
│   ├── views.py            # All page views
│   ├── urls.py             # URL routing
│   ├── forms.py            # Contact form
│   ├── context_processors.py
│   ├── templates/shop/
│   │   ├── base.html       # Base layout with header, footer, WhatsApp button
│   │   ├── home.html       # Homepage with hero, categories, featured products
│   │   ├── product_list.html  # Product listing with filters & search
│   │   ├── product_detail.html # Product detail with WhatsApp order
│   │   ├── contact.html    # Contact/inquiry form
│   │   ├── delivery_info.html # Delivery information page
│   │   └── about.html      # About us page
│   ├── static/shop/
│   │   ├── css/style.css
│   │   └── js/main.js
│   └── management/commands/
│       └── seed_data.py    # Sample data loader
├── media/products/         # Uploaded product images
└── staticfiles/
```

## Features

- **Homepage**: Hero section, category grid, featured products, trust badges, offer banner
- **Product Catalog**: Browse by category, search, sort (price/newest), stock status
- **Product Detail**: Full product info with "Order via WhatsApp" button
- **WhatsApp Ordering**: Floating button + per-product order messages
- **Admin Panel**: Full CRUD for products, categories, manage inquiries
- **Contact Form**: General, bulk order, contractor, and delivery inquiries
- **Responsive Design**: Mobile-first, works on all devices
- **SEO**: Meta tags, semantic HTML, fast loading

## Admin Panel

Access at `/admin` to:
- Add/edit/delete products with images
- Manage categories
- View and respond to customer inquiries
- Toggle featured products
- Update site settings (WhatsApp number, delivery threshold)

## WhatsApp Integration

- Floating WhatsApp button on every page
- Product pages have "Order via WhatsApp" that sends product name and price
- Auto-generated message: "Hello, I want to order [Product Name] (Rs [Price] per [Unit])"

## Customization

### Change WhatsApp Number
Edit `plumbing_shop/settings.py`:
```python
WHATSAPP_PHONE = "+97798XXXXXXXX"
```
Or update via Admin > Site Settings.

### Change Shop Details
Edit these in `plumbing_shop/settings.py`:
```python
SITE_NAME = "Your Shop Name"
SITE_PHONE = "+977 98X-XXXXXXX"
SITE_ADDRESS = "Your Address"
SITE_OPENING_HOURS = "Sun-Fri: 8AM-7PM"
```

### Add Real Product Images
1. Go to Admin > Products
2. Upload images for each product
3. Images are stored in `media/products/`
