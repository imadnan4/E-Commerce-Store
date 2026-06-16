from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Category, Order, OrderItem, Product


def home(request):
    categories = Category.objects.all()
    category_slug = request.GET.get("category")
    products = Product.objects.filter(is_available=True)
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(
        request,
        "store/home.html",
        {
            "products": products,
            "categories": categories,
            "selected_category": category_slug,
        },
    )


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_available=True)
    return render(request, "store/product_detail.html", {"product": product})


def cart_view(request):
    cart = request.session.get("cart", {})
    cart_items = []
    total = 0
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * item["quantity"]
            total += item_total
            cart_items.append(
                {
                    "product": product,
                    "quantity": item["quantity"],
                    "item_total": item_total,
                }
            )
        except Product.DoesNotExist:
            pass
    return render(
        request, "store/cart.html", {"cart_items": cart_items, "total": total}
    )


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get("cart", {})
    pid = str(product_id)
    if pid in cart:
        cart[pid]["quantity"] += 1
    else:
        cart[pid] = {"quantity": 1, "price": str(product.price)}
    request.session["cart"] = cart
    messages.success(request, f'"{product.name}" added to cart!')
    return redirect(request.META.get("HTTP_REFERER", "home"))


def remove_from_cart(request, product_id):
    cart = request.session.get("cart", {})
    pid = str(product_id)
    if pid in cart:
        del cart[pid]
        request.session["cart"] = cart
        messages.info(request, "Item removed from cart.")
    return redirect("cart")


def update_cart(request, product_id):
    cart = request.session.get("cart", {})
    pid = str(product_id)
    quantity = int(request.POST.get("quantity", 1))
    if quantity > 0:
        cart[pid] = {"quantity": quantity, "price": cart.get(pid, {}).get("price", "0")}
    else:
        cart.pop(pid, None)
    request.session["cart"] = cart
    return redirect("cart")


@login_required
def checkout(request):
    cart = request.session.get("cart", {})
    if not cart:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart")

    cart_items = []
    total = 0
    for product_id, item in cart.items():
        try:
            product = Product.objects.get(id=product_id)
            item_total = product.price * item["quantity"]
            total += item_total
            cart_items.append(
                {
                    "product": product,
                    "quantity": item["quantity"],
                    "item_total": item_total,
                }
            )
        except Product.DoesNotExist:
            pass

    if request.method == "POST":
        address = request.POST.get("address", "").strip()
        if not address:
            messages.error(request, "Please provide a shipping address.")
            return render(
                request,
                "store/checkout.html",
                {"cart_items": cart_items, "total": total},
            )

        order = Order.objects.create(
            user=request.user,
            shipping_address=address,
            total_price=total,
            status="pending",
        )
        for product_id, item in cart.items():
            try:
                product = Product.objects.get(id=product_id)
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item["quantity"],
                    price=product.price,
                )
                product.stock = max(0, product.stock - item["quantity"])
                product.save()
            except Product.DoesNotExist:
                pass

        request.session["cart"] = {}
        messages.success(request, "Order placed successfully!")
        return redirect("order_success", order_id=order.id)

    return render(
        request, "store/checkout.html", {"cart_items": cart_items, "total": total}
    )


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "store/order_success.html", {"order": order})
