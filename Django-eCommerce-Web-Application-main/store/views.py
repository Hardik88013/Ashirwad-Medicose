from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum, Q
from django.contrib import messages
from .models import OrderItem, Product, Cart, Wishlist, Order, UserProfile, Invoice
import uuid
import datetime
from .utils import render_to_pdf

# ================= AUTH =================

def login_view(request):
    if request.method == "POST":
        login_input = request.POST['username']
        password = request.POST['password']

        # Try to find user by email or mobile first
        user = None
        users = User.objects.filter(Q(username=login_input) | Q(email=login_input) | Q(profile__mobile=login_input)).distinct()
        if users.exists():
            u = users.first()
            user = authenticate(request, username=u.username, password=password)

        if user:
            login(request, user)

            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('products')
        else:
            messages.error(request, "Invalid credentials.")

    return render(request, 'login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        email = request.POST.get('email', '')
        name = request.POST.get('name', '')
        mobile = request.POST.get('mobile', '')
        age = request.POST.get('age', '')
        gender = request.POST.get('gender', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another one.")
        elif User.objects.filter(email=email).exists() and email != '':
            messages.error(request, "Email already exists. Please choose another one.")
        elif UserProfile.objects.filter(mobile=mobile).exists() and mobile != '':
            messages.error(request, "Mobile number already exists.")
        else:
            user = User.objects.create_user(username=username, email=email, password=password, first_name=name)
            UserProfile.objects.create(
                user=user,
                mobile=mobile,
                age=age if age else None,
                gender=gender
            )
            messages.success(request, "Registration successful. Please login.")
            return redirect('login')

    return render(request, 'register.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ================= PRODUCTS =================

@login_required
def products(request):
    query = request.GET.get('q')
    category = request.GET.get('category')

    products = Product.objects.all()

    # 🔍 Search filter
    if query:
        products = products.filter(name__icontains=query)

    # 🏷 Category filter
    if category:
        products = products.filter(category=category)

    user_wishlist = Wishlist.objects.filter(user=request.user)
    wishlist_products = [item.product for item in user_wishlist]

    return render(request, 'products.html', {
        'products': products,
        'user_wishlist': wishlist_products
    })


@login_required
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def ai_suggest(request):
    suggestions = []
    symptoms_input = ""

    if request.method == "POST":
        symptoms_input = request.POST.get("symptoms", "").lower()

        # Simple Rule-based suggestions
        medical_mapping = {
            "fever": ["Paracetamol", "Ibuprofen"],
            "headache": ["Aspirin", "Ibuprofen", "Paracetamol"],
            "cold": ["Cetirizine", "Loratadine", "Decongestant Spray"],
            "cough": ["Dextromethorphan (for dry cough)", "Guaifenesin (for wet cough)"],
            "pain": ["Diclofenac Gel", "Ibuprofen", "Naproxen"],
            "acidity": ["Antacid Tablets", "Omeprazole", "Ranitidine"],
            "allergy": ["Cetirizine", "Fexofenadine"],
            "diarrhea": ["Loperamide", "ORS (Oral Rehydration Salts)"],
            "constipation": ["Bisacodyl", "Psyllium Husk"],
            "injury": ["Antiseptic Cream", "Bandages", "Neosporin"],
        }

        for symptom, meds in medical_mapping.items():
            if symptom in symptoms_input:
                suggestions.extend(meds)

        # De-duplicate
        suggestions = list(set(suggestions))

        if not suggestions:
            suggestions.append("Please consult a professional healthcare provider for a proper diagnosis as your symptoms are not clear.")
        else:
            suggestions.append("<i>Note: It is always recommended to consult a medical professional for expert advice.</i>")

    return render(request, "ai_suggest.html", {

        "suggestions": suggestions,
        "symptoms_input": symptoms_input
    })

# ================= CART =================

@login_required
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    if request.GET.get('buy_now'):
        return redirect('cart')

    return redirect('products')



@login_required
def cart_view(request):
    items = Cart.objects.filter(user=request.user)
    total = sum(item.subtotal() for item in items)

    return render(request, 'cart.html', {
        'items': items,
        'total': total
    })


@login_required
def update_cart_quantity(request, id, action):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)

    if action == "increase":
        cart_item.quantity += 1
    elif action == "decrease":
        if cart_item.quantity > 1:
            cart_item.quantity -= 1

    cart_item.save()
    return redirect('cart')


@login_required
def remove_from_cart(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.delete()
    return redirect('cart')


# ================= WISHLIST =================

@login_required
def add_to_wishlist(request, id):
    product = get_object_or_404(Product, id=id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect('wishlist')


@login_required
def wishlist_view(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist.html', {'items': items})


@login_required
def toggle_wishlist(request, id):
    product = get_object_or_404(Product, id=id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()
    else:
        Wishlist.objects.create(user=request.user, product=product)

    return redirect(request.META.get('HTTP_REFERER', 'products'))


# ================= CHECKOUT =================

@login_required
def checkout(request):
    cart_items = Cart.objects.filter(user=request.user)

    if not cart_items.exists():
        return redirect('cart')

    total = sum(item.subtotal() for item in cart_items)

    if request.method == "POST":
        address = request.POST['address']
        mobile = request.POST['mobile']
        status = "Pending"

        order = Order.objects.create(
            user=request.user,
            address=address,
            mobile=mobile,
            total_amount=total,
            status=status
        )

        # Create Order Items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discounted_price
            )

        # Generate Invoice
        invoice_number = f"INV-{order.id}-{uuid.uuid4().hex[:6].upper()}"
        pdf_file = render_to_pdf('invoice_template.html', {'order': order, 'invoice_number': invoice_number})
        
        invoice = Invoice(order=order, serial_number=invoice_number)
        if pdf_file:
            invoice.pdf.save(f"invoice_{invoice_number}.pdf", pdf_file)
        invoice.save()

        # Clear cart
        cart_items.delete()

        return render(request, 'payment.html', {
            'status': status,
            'order': order,
            'invoice': invoice
        })

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })


# ================= ORDERS =================

@login_required
def orders(request):
    if request.user.is_staff:
        user_orders = Order.objects.all().order_by('-created_at')
    else:
        user_orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders.html', {'orders': user_orders})


# ================= ADMIN PANEL =================

@staff_member_required
def admin_dashboard(request):
    products = Product.objects.all()
    orders = Order.objects.all().order_by('-created_at')

    total_orders = orders.count()

    # Near Products logic: Products expiring within 30 days
    today = datetime.date.today()
    thirty_days_later = today + datetime.timedelta(days=30)
    near_products = Product.objects.filter(expiry_date__lte=thirty_days_later, expiry_date__gte=today).order_by('expiry_date')

    return render(request, 'admin/dashboard.html', {
        'products': products,
        'orders': orders,
        'total_orders': total_orders,
        'near_products': near_products
    })

@staff_member_required
def admin_sales(request):
    delivered_orders = Order.objects.filter(status="Delivered")
    
    # ------------------ TIME FILTERING ------------------
    range_param = request.GET.get('range', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    today = datetime.date.today()
    if start_date and end_date:
        s_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        e_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        delivered_orders = delivered_orders.filter(created_at__date__gte=s_date, created_at__date__lte=e_date)
    elif range_param == 'today':
        delivered_orders = delivered_orders.filter(created_at__date=today)
    elif range_param == '1m':
        delivered_orders = delivered_orders.filter(created_at__date__gte=today - datetime.timedelta(days=30))
    elif range_param == '6m':
        delivered_orders = delivered_orders.filter(created_at__date__gte=today - datetime.timedelta(days=180))
    elif range_param == '1y':
        delivered_orders = delivered_orders.filter(created_at__date__gte=today - datetime.timedelta(days=365))

    # ------------------ HEAD CARD METRICS ------------------
    total_sales = delivered_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    monthly_orders = Order.objects.filter(status="Delivered", created_at__year=today.year, created_at__month=today.month)
    monthly_sales = monthly_orders.aggregate(total=Sum('total_amount'))['total'] or 0
    yearly_orders = Order.objects.filter(status="Delivered", created_at__year=today.year)
    yearly_sales = yearly_orders.aggregate(total=Sum('total_amount'))['total'] or 0

    # ------------------ CHART DATA AGGREGATION ------------------
    import json
    
    # 1. Category wise Sales (Pie Chart) & Product Wise (Drilldown)
    category_sales = {}
    category_qty = {}
    product_sales = {} # category -> {product_name: revenue}
    product_qty = {}   # category -> {product_name: qty_sold}
    
    for item in OrderItem.objects.filter(order__in=delivered_orders):
        cat = item.product.get_category_display()
        prod = item.product.name
        rev = float(item.subtotal())
        qty = item.quantity
        
        # Category Aggregation
        category_sales[cat] = category_sales.get(cat, 0) + rev
        category_qty[cat] = category_qty.get(cat, 0) + qty
        
        # Product Aggregation inside Category
        if cat not in product_sales:
            product_sales[cat] = {}
            product_qty[cat] = {}
        product_sales[cat][prod] = product_sales[cat].get(prod, 0) + rev
        product_qty[cat][prod] = product_qty[cat].get(prod, 0) + qty

    # 2. Daily Sales (Line/Points Chart)
    from django.db.models.functions import TruncDate
    daily_sales_qs = delivered_orders.annotate(date=TruncDate('created_at')).values('date').annotate(daily_total=Sum('total_amount')).order_by('date')
    
    daily_labels = [dt['date'].strftime('%Y-%m-%d') for dt in daily_sales_qs]
    daily_data = [float(dt['daily_total']) for dt in daily_sales_qs]

    return render(request, 'admin/sales.html', {
        'total_sales': total_sales,
        'monthly_sales': monthly_sales,
        'yearly_sales': yearly_sales,
        'category_sales_labels': json.dumps(list(category_sales.keys())),
        'category_sales_data': json.dumps(list(category_sales.values())),
        'category_qty_data': json.dumps(list(category_qty.values())),
        'product_sales_dict': json.dumps(product_sales),
        'product_qty_dict': json.dumps(product_qty),
        'daily_labels': json.dumps(daily_labels),
        'daily_data': json.dumps(daily_data),
        'range_param': range_param,
        'start_date_param': start_date or '',
        'end_date_param': end_date or '',
    })

import csv
from django.http import HttpResponse

@staff_member_required
def export_orders_csv(request):
    delivered_orders = Order.objects.filter(status="Delivered")
    
    range_param = request.GET.get('range', 'all')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    today = datetime.date.today()
    if start_date and end_date:
        s_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        e_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        delivered_orders = delivered_orders.filter(created_at__date__gte=s_date, created_at__date__lte=e_date)
    elif range_param == 'today':
        delivered_orders = delivered_orders.filter(created_at__date=today)
    elif range_param == '1m':
        delivered_orders = delivered_orders.filter(created_at__date__gte=today - datetime.timedelta(days=30))
    elif range_param == '6m':
        delivered_orders = delivered_orders.filter(created_at__date__gte=today - datetime.timedelta(days=180))
    elif range_param == '1y':
        delivered_orders = delivered_orders.filter(created_at__date__gte=today - datetime.timedelta(days=365))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Customer', 'Mobile', 'Address', 'Total Amount (Rs)', 'Date', 'Status'])
    
    for order in delivered_orders:
        writer.writerow([
            order.id, 
            order.user.username, 
            order.mobile, 
            order.address, 
            order.total_amount, 
            order.created_at.strftime('%Y-%m-%d %H:%M:%S'), 
            order.status
        ])
        
    return response

@staff_member_required
def admin_add_product(request):
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        discount_percentage = request.POST.get('discount_percentage', 0)
        stock_quantity = request.POST.get('stock_quantity', 10)
        category = request.POST['category']
        expiry_date = request.POST.get('expiry_date')
        if not expiry_date:
            expiry_date = None
        image = request.FILES.get('image')

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            discount_percentage=discount_percentage,
            stock_quantity=stock_quantity,
            category=category,
            expiry_date=expiry_date,
            image=image
        )

        return redirect('admin_dashboard')

    return render(request, 'admin/add_product.html')


@staff_member_required
def admin_delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('admin_dashboard')


@staff_member_required
def admin_edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.discount_percentage = request.POST.get('discount_percentage', 0)
        product.stock_quantity = request.POST.get('stock_quantity', 10)
        product.category = request.POST['category']
        expiry_date = request.POST.get('expiry_date')
        if expiry_date:
            product.expiry_date = expiry_date
        else:
            product.expiry_date = None
        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')
        
        product.save()
        return redirect('admin_dashboard')

    return render(request, 'admin/edit_product.html', {'product': product})


@staff_member_required
def admin_update_order_status(request, id):
    order = get_object_or_404(Order, id=id)

    if request.method == "POST":
        new_status = request.POST.get("status")
        order.status = new_status
        order.save()

    return redirect("admin_dashboard")