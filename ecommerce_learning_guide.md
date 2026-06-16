# E-commerce Store — Self-Learning Guide
### Django + PostgreSQL | CodeAlpha Internship Task 1

---

## How to use this guide

Read each phase top to bottom. Code everything yourself — do not copy-paste. When you finish the milestone at the end of each phase, only then move to the next one. Every concept has an explanation of *why* it works, not just *what* to type.

---


CodeAlpha_EcommerceStore/
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
│
├── ecommerce/                  # Django project settings
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── users/                      # User auth app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   └── urls.py
│
├── store/                      # Products & orders app
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── context_processors.py
│
├── templates/
│   ├── base.html
│   ├── navbar.html
│   ├── users/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   └── store/
│       ├── home.html
│       ├── product_detail.html
│       ├── cart.html
│       ├── checkout.html
│       └── order_success.html
│
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── cart.js

## Table of Contents

1. [Phase 1 — Project Setup](#phase-1--project-setup)
2. [Phase 2 — How Django Works (MVT)](#phase-2--how-django-works-mvt)
3. [Phase 3 — Models and the Database](#phase-3--models-and-the-database)
4. [Phase 4 — User Authentication](#phase-4--user-authentication)
5. [Phase 5 — Store Logic (Cart and Orders)](#phase-5--store-logic-cart-and-orders)
6. [Phase 6 — Frontend (Templates and CSS)](#phase-6--frontend-templates-and-css)
7. [Final Checklist](#final-checklist)
8. [Common Errors and Fixes](#common-errors-and-fixes)

---

## Phase 1 — Project Setup

### What you are building first

Before any app code, you need three things ready: a Python virtual environment, a PostgreSQL database, and a Django project skeleton with two apps inside it.

---

### Concept 1 — Virtual Environment

A virtual environment is an isolated Python installation just for this project. Without it, every package you install goes globally and different projects can conflict with each other.

**Why it matters:** If you install Django 4.2 globally and later start a project that needs Django 3.2, they will fight each other. Virtual environments prevent this completely.

**Commands to run inside your project folder:**

```bash
python -m venv venv
source venv/bin/activate
```

After activation your terminal prompt will show `(venv)` at the start. Every `pip install` from this point only affects this project.

**Install your dependencies:**

```bash
pip install django psycopg2-binary python-dotenv Pillow
```

What each package does:
- `django` — the web framework itself
- `psycopg2-binary` — the driver that lets Django talk to PostgreSQL
- `python-dotenv` — reads your `.env` file so secrets stay out of code
- `Pillow` — required by Django to handle image uploads (product photos)

After installing, freeze them:

```bash
pip freeze > requirements.txt
```

This creates a file anyone can use to install exactly the same versions with `pip install -r requirements.txt`.

---

### Concept 2 — Environment Variables and the .env File

Never put passwords, secret keys, or database credentials directly in your Python files. If you push to GitHub, everyone can see them.

The solution: store secrets in a `.env` file and add `.env` to `.gitignore`.

**Create `.env` in your project root:**

```
SECRET_KEY=some-long-random-string-here
DEBUG=True
DB_NAME=ecommerce_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

**Create `.gitignore`:**

```
__pycache__/
*.pyc
.env
venv/
media/
staticfiles/
```

In `settings.py` you will read these with:

```python
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
```

`load_dotenv()` reads the `.env` file and puts each line into the OS environment. `os.getenv()` then reads them by name.

---

### Concept 3 — PostgreSQL Database Setup

Django does not create the database for you. It only creates tables inside an existing database. You create the database manually first.

**Open psql:**

```bash
psql -U postgres
```

**Inside psql, run:**

```sql
CREATE DATABASE ecommerce_db;
\q
```

That is all. Now Django can connect to it and create tables when you run migrations.

**Understanding the difference:**
- Database = the container (you create this manually)
- Tables = the data structure inside (Django creates these via migrations)
- Rows = the actual data (your app creates these at runtime)

---

### Concept 4 — Django Project vs Django App

This confuses almost everyone at first.

A **project** is the overall configuration — settings, root URLs, wsgi. There is only one project.

An **app** is a self-contained feature module. You can have many apps. Each app has its own models, views, and URLs.

**Why split into apps?** Because `users` and `store` are separate concerns. User registration has nothing to do with product listings. Keeping them separate makes the codebase easier to navigate and each app potentially reusable in other projects.

**Create the project and two apps:**

```bash
django-admin startproject ecommerce .
python manage.py startapp users
python manage.py startapp store
```

The `.` in the first command is important — it puts `settings.py` in the current folder instead of creating a nested folder.

**Register both apps in `ecommerce/settings.py`:**

```python
INSTALLED_APPS = [
    # ... django built-in apps ...
    'users',
    'store',
]
```

If you forget this step, Django will not find your models or templates.

---

### Phase 1 Milestone

Run this command:

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000` in your browser. You should see the Django rocket launch page. If you do, your setup is complete and you can move on.

---

## Phase 2 — How Django Works (MVT)

### The most important concept in this entire guide

Every single page in your app follows the same flow:

```
Browser Request
      ↓
  URLs (urls.py)       — which view handles this URL?
      ↓
  View (views.py)      — fetch data, prepare context
      ↓
  Template (.html)     — render data into HTML
      ↓
Browser Response
```

Django calls this MVT: Model, View, Template. Understand this flow completely before writing any feature.

---

### Concept 1 — URL Configuration

When a browser visits `http://127.0.0.1:8000/`, Django looks at `ecommerce/urls.py` to decide what to do.

**`ecommerce/urls.py` (project-level):**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('store.urls')),        # all store URLs
    path('users/', include('users.urls')),  # all user URLs prefixed with /users/
]
```

`include()` delegates URL matching to the app's own `urls.py`. So when someone visits `/users/login/`, Django strips the `users/` prefix and passes `login/` to `users/urls.py`.

**`store/urls.py` (app-level):**

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
]
```

The `name='home'` parameter lets you reference this URL in templates with `{% url 'home' %}` instead of hardcoding `/`. If you ever change the URL path, all links update automatically.

**URL patterns with parameters:**

`<slug:slug>` is a URL converter. It captures a slug-formatted string from the URL and passes it to the view as a keyword argument named `slug`. Other converters: `<int:id>`, `<str:name>`.

---

### Concept 2 — Views

A view is a Python function that receives an `HttpRequest` object and returns an `HttpResponse`.

**Simplest possible view:**

```python
from django.shortcuts import render

def home(request):
    return render(request, 'store/home.html', {})
```

`render()` is a shortcut that combines loading a template and returning an HttpResponse. The third argument is the **context** — a dictionary of data your template can access.

**View with data:**

```python
def home(request):
    products = Product.objects.all()          # fetch from database
    return render(request, 'store/home.html', {
        'products': products,                  # pass to template
    })
```

Now in the template, `{{ products }}` and `{% for product in products %}` work.

---

### Concept 3 — Templates and Template Inheritance

Templates are HTML files with Django template tags mixed in. Django template tags use `{% %}` for logic and `{{ }}` for output.

**Template tag reference:**

| Tag | Purpose |
|-----|---------|
| `{{ variable }}` | Output a variable value |
| `{% if condition %}` | Conditional block |
| `{% for item in list %}` | Loop |
| `{% url 'name' %}` | Generate a URL by name |
| `{% static 'path' %}` | Generate a static file URL |
| `{% csrf_token %}` | Security token for forms |
| `{% block name %}` | Define a replaceable block |
| `{% extends 'base.html' %}` | Inherit from a parent template |
| `{% include 'file.html' %}` | Insert another template |

**Template inheritance is how you avoid repeating the navbar and footer on every page.**

`templates/base.html` is the parent. It defines the full HTML structure and placeholders:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}ShopAlpha{% endblock %}</title>
</head>
<body>
    {% include 'navbar.html' %}
    <main>
        {% block content %}{% endblock %}
    </main>
    <footer>...</footer>
</body>
</html>
```

Every other template is a child that fills those placeholders:

```html
{% extends 'base.html' %}

{% block title %}Home{% endblock %}

{% block content %}
<h1>Products</h1>
{% endblock %}
```

Django replaces `{% block content %}` in the parent with whatever the child puts in its `{% block content %}`.

---

### Concept 4 — Static Files

Static files are CSS, JavaScript, and images that are part of your code (not uploaded by users).

**In `settings.py`:**

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
```

**In templates, load and use:**

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/style.css' %}">
```

`{% load static %}` must appear at the top of any template that uses `{% static %}`. The `{% static %}` tag generates the correct URL regardless of where you deploy.

**Media files** are different — these are files uploaded by users (product images). They need separate settings:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

And in `ecommerce/urls.py` add this at the end to serve them during development:

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [...] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

### Concept 5 — Context Processors

A context processor is a function that runs on every single request and automatically adds variables to the template context — so you don't have to pass them manually in every view.

The cart item count needs to show in the navbar on every page. Without a context processor, you'd have to pass `cart_count` in every single view. With one, you define it once.

**`store/context_processors.py`:**

```python
def cart_count(request):
    cart = request.session.get('cart', {})
    count = sum(item['quantity'] for item in cart.values())
    return {'cart_count': count}
```

**Register it in `settings.py`:**

```python
TEMPLATES = [{
    ...
    'OPTIONS': {
        'context_processors': [
            # django built-in ones here
            'store.context_processors.cart_count',  # add this line
        ],
    },
}]
```

Now `{{ cart_count }}` works in every template including the navbar.

---

### Phase 2 Milestone

Create a `home` URL, a `home` view that passes a hardcoded string in context, and a `home.html` template that displays it. Visit `localhost:8000` and see the string on screen. The full Django request-response cycle is working.

---

## Phase 3 — Models and the Database

### What a model is

A model is a Python class where each attribute becomes a column in a PostgreSQL table. Django's ORM (Object Relational Mapper) translates your Python into SQL automatically — you never write raw SQL for standard operations.

```python
# This Python class...
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)

# ...becomes this SQL table:
# CREATE TABLE store_product (
#     id SERIAL PRIMARY KEY,
#     name VARCHAR(200),
#     price DECIMAL(10, 2)
# );
```

Django also adds an `id` primary key column automatically unless you tell it not to.

---

### Concept 1 — Field Types

| Field | Use case |
|-------|----------|
| `CharField(max_length=N)` | Short text (names, titles) |
| `TextField()` | Long text (descriptions) |
| `DecimalField(max_digits, decimal_places)` | Money values — never use FloatField for prices |
| `IntegerField()` / `PositiveIntegerField()` | Whole numbers |
| `BooleanField(default=True)` | True/False flags |
| `ImageField(upload_to='folder/')` | Image uploads (requires Pillow) |
| `SlugField(unique=True)` | URL-safe strings like `blue-sneakers` |
| `DateTimeField(auto_now_add=True)` | Timestamp set once on creation |
| `DateTimeField(auto_now=True)` | Timestamp updated on every save |
| `ForeignKey(Model, on_delete=...)` | Many-to-one relationship |
| `OneToOneField(Model, on_delete=...)` | One-to-one relationship |

**Why `DecimalField` and not `FloatField` for price?**
Floating point numbers have precision errors in binary. `0.1 + 0.2` in Python gives `0.30000000000000004`. For money you need exact decimal arithmetic, which `DecimalField` provides via Python's `Decimal` type.

---

### Concept 2 — Relationships Between Models

**ForeignKey (many-to-one):**

```python
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
```

Many products can belong to one category. The `on_delete=models.SET_NULL` means if you delete a category, its products keep existing but their `category` field becomes `null` instead of being deleted too. Other options: `CASCADE` (delete the child too), `PROTECT` (prevent deleting the parent).

**OneToOneField:**

```python
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
```

One user has exactly one profile. If the user is deleted, the profile is deleted too (CASCADE). The difference from ForeignKey is that Django enforces uniqueness — you cannot accidentally create two profiles for the same user.

**Accessing related objects:**

```python
product.category          # gets the Category object
product.category.name     # gets the category name
category.product_set.all()  # gets all products in a category (reverse relation)
```

---

### Concept 3 — The Category and Product Models

Write this in `store/models.py`:

```python
from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
```

**Understanding `blank` vs `null`:**
- `null=True` — the database column can hold a NULL value
- `blank=True` — the Django form field is not required
- For strings, use `blank=True` only (empty string is better than NULL for text)
- For non-strings (FK, numbers, images), use both `null=True, blank=True` together

**Understanding `__str__`:**
This controls what you see in the Django admin panel when viewing a product. Without it you'd see `Product object (1)`. With it you see `Blue Sneakers`.

---

### Concept 4 — The Order and OrderItem Models

An order contains multiple products. You model this with two tables — one for the order header, one for each line item inside it.

```python
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_address = models.TextField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order #{self.id} by {self.user.username}'

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # price at time of purchase

    def get_total_price(self):
        return self.price * self.quantity
```

**Why store `price` in OrderItem instead of reading from Product?**
Product prices change over time. If a user bought something for $29.99 and you later change the price to $49.99, the order history should still show $29.99. Snapshotting the price at purchase time is standard e-commerce practice.

**Why `on_delete=CASCADE` on OrderItem?**
If an order is deleted, all its items should be deleted too. There's no point having orphaned order items floating around.

---

### Concept 5 — Migrations

After writing or changing models you must run two commands:

```bash
python manage.py makemigrations
python manage.py migrate
```

**What `makemigrations` does:** Reads your current models, compares them to the previous migration state, and generates a Python file describing the changes as SQL operations.

**What `migrate` does:** Actually runs those SQL operations against your PostgreSQL database, creating or altering the tables.

**Important rules:**
- Run `makemigrations` after every model change, no matter how small
- If you add a non-nullable field to an existing model, Django will ask you for a default value
- Never edit migration files manually unless you really know what you're doing
- Commit migration files to git — they are part of your codebase

---

### Concept 6 — Django Admin

The admin panel at `/admin` lets you add, edit, and delete model data without writing any views. Use it heavily during development to add test data.

**`store/admin.py`:**

```python
from django.contrib import admin
from .models import Category, Product, Order, OrderItem

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'stock', 'is_available']
    list_editable = ['price', 'stock', 'is_available']
    prepopulated_fields = {'slug': ('name',)}
```

`prepopulated_fields` auto-fills the slug field in the admin form as you type the name. `list_editable` lets you edit fields directly in the list view without opening each record.

**Create your superuser:**

```bash
python manage.py createsuperuser
```

Then go to `http://127.0.0.1:8000/admin` and add 3-4 categories and 6-8 products with images.

---

### Phase 3 Milestone

Open the admin, add some products, then write a temporary view that does `Product.objects.all()` and prints the count. You can read real data from PostgreSQL into Python. Move on.

---

## Phase 4 — User Authentication

### Django's built-in auth system

Django ships with a complete authentication system. Never build your own password hashing or session management from scratch. Use what Django provides.

The built-in `User` model gives you: `username`, `password` (hashed automatically), `email`, `first_name`, `last_name`, `is_staff`, `is_active`, `date_joined`.

---

### Concept 1 — The Profile Model

The built-in User does not have fields for phone number or address. Instead of replacing the User model (complex), you extend it by creating a Profile model with a OneToOneField.

**`users/models.py`:**

```python
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f'{self.user.username} Profile'
```

In views you access profile data like this:

```python
request.user.profile.phone
request.user.profile.address
```

---

### Concept 2 — Django Forms

Forms in Django serve two purposes: rendering HTML input fields and validating submitted data.

**`users/forms.py`:**

```python
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'address', 'city', 'country']
```

`UserCreationForm` is Django's built-in form for creating users. It automatically:
- Validates that `password1` and `password2` match
- Checks the password against Django's password validators
- Ensures the username is unique

You extend it by adding extra fields like `email`.

---

### Concept 3 — The Registration View

Every form view follows the same pattern:

```python
def register_view(request):
    if request.method == 'POST':               # form was submitted
        form = RegisterForm(request.POST)
        if form.is_valid():                    # all validation passed
            user = form.save()                 # save to database
            Profile.objects.create(user=user)  # create linked profile
            login(request, user)               # log them in immediately
            return redirect('home')            # send to home page
        # if not valid, fall through and re-render with errors
    else:                                      # GET request — show empty form
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})
```

**The POST/GET/redirect pattern:**
- GET → show empty form
- POST with invalid data → re-render form with error messages
- POST with valid data → process and redirect

Always redirect after a successful POST. If you render instead of redirecting, refreshing the page submits the form again (the "are you sure you want to resubmit?" browser warning).

---

### Concept 4 — Login, Logout, and Sessions

```python
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)              # creates a session
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)                           # destroys the session
    return redirect('home')
```

**How sessions work:**
When `login()` is called, Django creates a session record in the database and sends a session cookie to the browser. On every subsequent request, the browser sends that cookie back and Django uses it to look up the session and set `request.user`. When `logout()` is called, the session record is deleted.

**The `?next=` parameter:**
When `@login_required` redirects to the login page, it appends `?next=/checkout/`. After login, you redirect to that URL so the user lands where they were trying to go.

---

### Concept 5 — The @login_required Decorator

```python
from django.contrib.auth.decorators import login_required

@login_required
def checkout(request):
    ...
```

If an anonymous user tries to visit `/checkout/`, Django redirects them to `/users/login/?next=/checkout/`. After they log in, they are sent to `/checkout/` automatically.

Set where `@login_required` redirects in `settings.py`:

```python
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
```

---

### Phase 4 Milestone

A user can: register and get logged in automatically, log in and see their username in the navbar, visit their profile page, update their address, and log out. Visiting `/checkout/` while logged out redirects to the login page.

---

## Phase 5 — Store Logic (Cart and Orders)

### Concept 1 — Session-Based Cart

The cart does not need a database table. It lives in Django's session — a server-side dictionary tied to the user's browser via a cookie. This means even logged-out users can have a cart.

**The cart data structure in the session:**

```python
{
    '3': {'quantity': 2, 'price': '29.99'},
    '7': {'quantity': 1, 'price': '14.50'},
}
```

Keys are product IDs as strings (JSON serialization converts dict keys to strings, so always use strings to avoid mismatches).

**Reading the cart:**

```python
cart = request.session.get('cart', {})
```

The second argument `{}` is the default if no cart exists yet.

**Writing back to the session:**

```python
cart[pid] = {'quantity': 1, 'price': str(product.price)}
request.session['cart'] = cart   # this line is required
```

Django only marks the session as modified when you reassign the top-level key. If you mutate a nested value without reassigning, Django may not save the change.

---

### Concept 2 — Add to Cart View

```python
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    pid = str(product_id)

    if pid in cart:
        cart[pid]['quantity'] += 1
    else:
        cart[pid] = {'quantity': 1, 'price': str(product.price)}

    request.session['cart'] = cart
    messages.success(request, f'"{product.name}" added to cart!')
    return redirect(request.META.get('HTTP_REFERER', 'home'))
```

`request.META.get('HTTP_REFERER', 'home')` redirects back to the page the user came from. `HTTP_REFERER` is the URL of the previous page. If it's not available, fall back to `'home'`.

`get_object_or_404()` is a shortcut that fetches an object by lookup or returns a 404 response if not found, instead of raising an exception.

---

### Concept 3 — Cart View (Displaying the Cart)

```python
def cart_view(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0

    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * item['quantity']
            total += item_total
            cart_items.append({
                'product': product,
                'quantity': item['quantity'],
                'item_total': item_total,
            })
        except Product.DoesNotExist:
            pass   # product was deleted after being added to cart — skip it

    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })
```

**Why handle `Product.DoesNotExist`?**
A product in the cart might get deleted from the database by an admin after a customer added it. Without the try/except, this would crash with an error. Handle it gracefully by just skipping that item.

**Why calculate totals in the view and not the template?**
Templates should only display data, not compute it. Keeping logic in the view makes code easier to test, debug, and reuse. This is the "thin template, fat view" principle.

---

### Concept 4 — Checkout and Order Creation

This is where the session cart becomes real database records.

```python
@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('cart')

    # Build cart_items list for display (same as cart_view)
    cart_items = []
    total = 0
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * item['quantity']
            total += item_total
            cart_items.append({'product': product, 'quantity': item['quantity'], 'item_total': item_total})
        except Product.DoesNotExist:
            pass

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        if not address:
            messages.error(request, 'Please provide a shipping address.')
            return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})

        # 1. Create the order
        order = Order.objects.create(
            user=request.user,
            shipping_address=address,
            total_price=total,
            status='pending'
        )

        # 2. Create one OrderItem per product
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=product.price    # snapshot the price
                )
                # 3. Reduce stock
                product.stock = max(0, product.stock - item['quantity'])
                product.save()
            except Product.DoesNotExist:
                pass

        # 4. Clear the cart
        request.session['cart'] = {}
        messages.success(request, 'Order placed successfully!')
        return redirect('order_success', order_id=order.id)

    return render(request, 'store/checkout.html', {'cart_items': cart_items, 'total': total})
```

**The order of operations matters:**
1. Validate the form first — if invalid, stop and re-render
2. Create the Order row
3. Create OrderItem rows for each product
4. Decrement stock
5. Clear the session cart
6. Redirect to success page

If you clear the cart before creating the order, and something fails in step 3, the user loses their cart with no order created. Always do database writes before clearing session data.

---

### Concept 5 — Django QuerySet Methods

When fetching products from the database in views, these are the methods you'll use most:

```python
Product.objects.all()                          # all products
Product.objects.filter(is_available=True)      # where is_available = true
Product.objects.filter(category__slug=slug)    # join to category table via slug
Product.objects.get(id=5)                      # one object, raises error if not found
Product.objects.get(slug='blue-sneakers')      # one object by slug
Product.objects.order_by('-created_at')        # newest first (- = descending)
Product.objects.filter(...).order_by(...)      # chain methods
```

The double underscore `__` in `category__slug` is Django's way of traversing a ForeignKey relationship in a filter. It generates a SQL JOIN automatically.

---

### Phase 5 Milestone

A user can add a product to the cart, see the cart count update in the navbar, visit the cart page and see all items with totals, update quantity, remove items, proceed to checkout, submit an address, and see the order success page. The order appears in the Django admin under Orders.

---

## Phase 6 — Frontend (Templates and CSS)

### Concept 1 — Template Structure and Files to Create

```
templates/
├── base.html              ← parent of all pages
├── navbar.html            ← included in base.html
├── users/
│   ├── login.html
│   ├── register.html
│   └── profile.html
└── store/
    ├── home.html
    ├── product_detail.html
    ├── cart.html
    ├── checkout.html
    └── order_success.html
```

Django looks for templates in the `templates/` directory you specify in `settings.py`:

```python
TEMPLATES = [{
    'DIRS': [BASE_DIR / 'templates'],
    ...
}]
```

---

### Concept 2 — Rendering Django Forms in Templates

Django forms can be rendered in two ways:

**Method 1 — Auto-render (quick but ugly):**

```html
{{ form.as_p }}
```

Renders all fields wrapped in `<p>` tags. No control over styling.

**Method 2 — Manual loop (recommended):**

```html
<form method="POST">
    {% csrf_token %}
    {% for field in form %}
        <div class="form-group">
            <label for="{{ field.id_for_label }}">{{ field.label }}</label>
            {{ field }}
            {% if field.errors %}
                <span class="error">{{ field.errors.0 }}</span>
            {% endif %}
        </div>
    {% endfor %}
    <button type="submit">Submit</button>
</form>
```

`{{ field }}` renders the input element itself. `field.label` is the label text. `field.errors.0` is the first error message for that field if validation failed.

**The `{% csrf_token %}` tag is non-negotiable.** Every POST form must have it inside the `<form>` tag. Django rejects POST requests without a valid CSRF token as a security measure against cross-site request forgery attacks.

---

### Concept 3 — The Product Grid

Use CSS Grid for the product listing. This one rule makes it fully responsive with no media queries needed:

```css
.product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 24px;
}
```

`auto-fill` — create as many columns as fit in the container.
`minmax(240px, 1fr)` — each column is at least 240px wide and at most an equal share of remaining space.

On a wide screen this creates 4 columns. On a tablet it becomes 2. On mobile it becomes 1. No media queries.

---

### Concept 4 — Category Filter with GET Parameters

Filtering by category works via a URL query parameter: `/?category=electronics`.

**In the template, the filter buttons are just links:**

```html
<a href="{% url 'home' %}">All</a>
{% for cat in categories %}
    <a href="?category={{ cat.slug }}">{{ cat.name }}</a>
{% endfor %}
```

**In the view, read the parameter and filter:**

```python
def home(request):
    products = Product.objects.filter(is_available=True)
    selected = request.GET.get('category')   # None if not present
    if selected:
        products = products.filter(category__slug=selected)
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
        'selected_category': selected,
    })
```

**In the template, highlight the active filter:**

```html
<a href="?category={{ cat.slug }}"
   class="btn {% if selected_category == cat.slug %}btn-active{% endif %}">
    {{ cat.name }}
</a>
```

---

### Concept 5 — Flash Messages

Django's messages framework lets you display one-time notifications (success, error, warning) after a redirect.

**In a view:**

```python
from django.contrib import messages

messages.success(request, 'Order placed successfully!')
messages.error(request, 'Invalid username or password.')
messages.warning(request, 'Your cart is empty.')
messages.info(request, 'Item removed from cart.')
```

**In `base.html`, display them:**

```html
{% if messages %}
    <div class="messages">
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }}">{{ message }}</div>
        {% endfor %}
    </div>
{% endif %}
```

`message.tags` gives you `success`, `error`, `warning`, or `info` — use them as CSS class names to style each type differently.

Messages disappear after being displayed once. They are perfect for "Item added to cart!" style notifications.

---

### Concept 6 — Product Images

In the Product model you have `image = models.ImageField(upload_to='products/')`. In templates, display it like this:

```html
{% if product.image %}
    <img src="{{ product.image.url }}" alt="{{ product.name }}">
{% else %}
    <div class="product-placeholder">📦</div>
{% endif %}
```

Always check `{% if product.image %}` before using `.url`. If no image was uploaded, `.url` will raise an error because there is no file path to generate a URL for.

---

### Phase 6 Milestone

Every page is styled. The navbar shows cart count and the username when logged in. The product grid is responsive. Category filtering works. Form errors display inline. Flash messages appear and disappear. The entire app works end-to-end as a user.

---

## Final Checklist

Go through each item and make sure it works in your browser before submission.

### Setup
- [ ] Virtual environment is active when running the project
- [ ] `.env` file exists with all credentials
- [ ] `.env` is in `.gitignore`
- [ ] `requirements.txt` is generated and committed
- [ ] PostgreSQL database exists and Django can connect

### Models and Admin
- [ ] Category, Product, Order, OrderItem models exist
- [ ] All migrations have been applied
- [ ] Admin is configured with list_display and prepopulated slugs
- [ ] Superuser exists and admin panel loads at `/admin`
- [ ] At least 4 categories and 8 products added with images and stock

### Authentication
- [ ] User can register with email, first name, last name
- [ ] User is logged in immediately after registration
- [ ] User can log in and sees their name in the navbar
- [ ] User can log out
- [ ] Profile page shows and saves address info
- [ ] `@login_required` redirects anonymous users to login page

### Store
- [ ] Home page shows all products in a grid
- [ ] Category filter buttons work
- [ ] Product detail page shows image, description, price, stock
- [ ] Add to cart works from both home and detail pages
- [ ] Cart count in navbar updates immediately
- [ ] Cart page shows all items with quantities and totals
- [ ] Quantity update works
- [ ] Remove from cart works
- [ ] Checkout page requires login
- [ ] Checkout creates an Order and OrderItems in the database
- [ ] Stock decrements after a successful order
- [ ] Cart is cleared after checkout
- [ ] Order success page shows order ID and details

### Frontend
- [ ] All pages extend `base.html`
- [ ] CSS is loading (no unstyled pages)
- [ ] Flash messages appear after add-to-cart, login, checkout
- [ ] Site is usable on mobile (responsive layout)
- [ ] No raw Python errors visible to the user

---

## Common Errors and Fixes

### `TemplateDoesNotExist`
Django cannot find your template file. Check:
1. `TEMPLATES['DIRS']` in settings.py points to `BASE_DIR / 'templates'`
2. The file path exactly matches what you pass to `render()` — `'store/home.html'` means `templates/store/home.html`

### `NoReverseMatch`
You used `{% url 'some_name' %}` but that URL name does not exist or is not registered. Check:
1. The `name=` parameter in `urls.py` exactly matches what you used in the template
2. The app's `urls.py` is included in the project's `urls.py`

### `CSRF verification failed`
Your POST form is missing `{% csrf_token %}` inside the `<form>` tag. Add it.

### `RelatedObjectDoesNotExist` on `request.user.profile`
The user exists but has no Profile row in the database. Fix: use `get_or_create` instead of `get`:
```python
profile, created = Profile.objects.get_or_create(user=request.user)
```

### `ValueError: Cannot use ImageField because Pillow is not installed`
Run `pip install Pillow` inside your virtual environment.

### Static files not loading
1. `{% load static %}` must be at the top of the template
2. `STATICFILES_DIRS = [BASE_DIR / 'static']` must be in settings
3. Your CSS file must actually be at `static/css/style.css`

### `django.db.utils.OperationalError: could not connect to server`
Your PostgreSQL credentials in `.env` are wrong, PostgreSQL is not running, or the database does not exist yet. Check `DB_NAME`, `DB_USER`, `DB_PASSWORD`.

### Cart not saving between requests
You modified a nested value in `request.session['cart']` but did not reassign the top-level key. Always do:
```python
cart = request.session.get('cart', {})
# ... modify cart ...
request.session['cart'] = cart   # required
```

---

*Built for CodeAlpha Full Stack Development Internship — Task 1: E-commerce Store*
