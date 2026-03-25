from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Sum
from django.contrib import messages
from .models import OrderItem, Product, Cart, Wishlist, Order


# ================= AUTH =================

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('products')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')


def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another one.")
        else:
            User.objects.create_user(username=username, password=password)
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

        # Clear cart
        cart_items.delete()

        return render(request, 'payment.html', {
            'status': status,
            'order': order
        })

    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'total': total
    })


# ================= ORDERS =================

@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user)
    return render(request, 'orders.html', {'orders': user_orders})


# ================= ADMIN PANEL =================

@staff_member_required
def admin_dashboard(request):
    products = Product.objects.all()
    orders = Order.objects.all().order_by('-created_at')

    total_orders = orders.count()

    total_revenue = (
        orders.filter(status="Success")
        .aggregate(total=Sum('total_amount'))['total'] or 0
    )

    return render(request, 'admin/dashboard.html', {
        'products': products,
        'orders': orders,
        'total_orders': total_orders,
        'total_revenue': total_revenue
    })


@staff_member_required
def admin_add_product(request):
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST['description']
        price = request.POST['price']
        discount_percentage = request.POST.get('discount_percentage', 0)
        stock_quantity = request.POST.get('stock_quantity', 10)
        category = request.POST['category']
        image = request.FILES.get('image')

        Product.objects.create(
            name=name,
            description=description,
            price=price,
            discount_percentage=discount_percentage,
            stock_quantity=stock_quantity,
            category=category,
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