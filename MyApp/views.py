
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from .forms import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q




def registerPage(request):
    form = RegisterForm()
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            
            # ইমেইল আগে থেকেই আছে কিনা চেক করা
            emailExists = UserModel.objects.filter(email=data.email).exists()
            
            if emailExists:
                messages.warning(request, "Email Already Exists")
                # redirect না করে নিচে নেমে যেতে দেওয়া হবে যেন ফর্মের ডাটা থেকে যায়
            else:
                form.save()
                messages.success(request, "Registration successful! Please login.")
                return redirect('login')  # সফল হলেই কেবল রিডাইরেক্ট হবে

    # ইমেইল এক্সিস্ট করলে বা ফর্মে এরর থাকলে এই অংশ রান হবে
    context = {
        'form': form,
    }
    return render(request, 'base/authBaseForm.html', context)



def loginPage(request):
    form = AuthForm()
        
    if request.method == 'POST':
        text = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me') # ১. চেকবাক্সের ভ্যালু নেওয়া হলো

        # ১. ইনপুটটি ইউজারনেম নাকি ইমেইল তা চেক করে ইউজার অবজেক্ট খুঁজে বের করা
        user_obj = UserModel.objects.filter(username=text).first() or UserModel.objects.filter(email=text).first()
        
        # ২. ইউজার পাওয়া গেলে তার আসল username দিয়ে authenticate করা
        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {user.username}! Login successful.')
                
                # ৩. Remember Me লজিক
                if remember_me:
                    # সেশন মেয়ার ১৪ দিন (seconds: 1209600)
                    request.session.set_expiry(1209600)
                else:
                    # ব্রাউজার বন্ধ করলেই লগআউট হয়ে যাবে
                    request.session.set_expiry(0)

                return redirect('index')
            else:
                messages.error(request, "Wrong password!")
        else:
            messages.error(request, "User not found!")

    context = {'form': form}
    return render(request, 'base/authBaseForm.html', context)




@login_required
def logoutPage(request):
    logout(request)
    
    # মেসেজটি রিডাইরেক্টের আগেই সেট করে দেওয়া ভালো
    messages.success(request, "Logged out successfully!")
    
    # রিডাইরেক্ট রেসপন্স তৈরি
    response = redirect('index')
    
    # ব্রাউজার ক্যাশ বন্ধের হেডার
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # পাসওয়ার্ড পরিবর্তনের পর ইউজার যাতে লগআউট না হয়ে যায়
            update_session_auth_hash(request, user)
            messages.success(request, 'আপনার পাসওয়ার্ড সফলভাবে পরিবর্তন হয়েছে!')
            return redirect('index')
        else:
            messages.error(request, 'সঠিক তথ্য দিন।')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    
    return render(request, 'pages/baseForm.html', {'form': form})






def HomePage(request):
    # active carousel item গুলো অর্ডার অনুযায়ী নিয়ে আসা
    carousels = Carousel.objects.filter(is_active=True).order_by('order')
    
    # সর্বশেষ active promo banner নিয়ে আসা
    promo_banner = PromoBanner.objects.filter(is_active=True).last()

    products = Product.objects.filter(is_active=True)
    offer_products = Product.objects.filter(is_active=True, is_offer=True)

    special_deal = Product.objects.filter(is_active=True, is_offer=True, is_featured=True).first()
    if not special_deal:
        special_deal = Product.objects.filter(is_active=True, is_offer=True).first()

    # ২. ডান পাশের ব্যানারের জন্য (সর্বোচ্চ ডিসকাউন্ট বের করা)
    offered_products = Product.objects.filter(is_active=True, is_offer=True)
    top_offer_product = None
    max_discount = 0

    if offered_products.exists():
        top_offer_product = max(offered_products, key=lambda p: p.discount_percentage)
        max_discount = top_offer_product.discount_percentage

    total_offer_items = offered_products.count()

    categories = Category.objects.prefetch_related('products').all()
    

    context = {
        'carousels': carousels,
        'promo_banner': promo_banner,
        'products': products,
        'offer_products': offer_products,
        'special_deal': special_deal,
        'max_discount': max_discount,
        'top_offer_product': top_offer_product,
        'total_offer_items': total_offer_items,
        'categories': categories,
        
    }
    return render(request, 'pages/index.html', context)


def ShopPage(request):
    # Base Queryset (শুধু Active প্রোডাক্টসমূহ লোড করবে)
    products_qs = Product.objects.filter(is_active=True).select_related('category')

    # ১. সার্চ ফিল্টার (Title, Description, SKU)
    query = request.GET.get('q', '').strip()
    if query:
        products_qs = products_qs.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(sku__icontains=query)
        )

    # ২. ক্যাটাগরি ফিল্টার (ড্রপডাউন বা ইউআরএল থেকে)
    selected_category = request.GET.get('category', '').strip()
    if selected_category and selected_category != 'All Category':
        products_qs = products_qs.filter(category__slug=selected_category)

    # ৩. প্রাইস ফিল্টার
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price and min_price.isdigit():
        products_qs = products_qs.filter(price__gte=min_price)
    if max_price and max_price.isdigit():
        products_qs = products_qs.filter(price__lte=max_price)

    # ৪. সর্টিং ফিল্টার
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'price_low':
        products_qs = products_qs.order_by('price')
    elif sort_by == 'price_high':
        products_qs = products_qs.order_by('-price')
    else:  # default or newest
        products_qs = products_qs.order_by('-created_at')

    # মোট ফিল্টারড প্রোডাক্ট সংখ্যা
    total_products_count = products_qs.count()

    # ৫. পেজিনেশন (প্রতি পেজে ১২টি প্রোডাক্ট)
    paginator = Paginator(products_qs, 12)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)

    # সাইডবার এবং সার্চ বারের জন্য সব ক্যাটাগরি
    categories = Category.objects.all()

    # ৬. প্রোমো ব্যানার ডাটা (Product Model থেকে Offerd Items)
    promo_banners = Product.objects.filter(is_active=True, is_offer=True)
    if selected_category and selected_category != 'All Category':
        promo_banners = promo_banners.filter(category__slug=selected_category)
    
    promo_banners = promo_banners[:5]

    context = {
        'page_obj': products_page,
        'products': products_page,  # টেমপ্লেটের সুবিধার্থে
        'categories': categories,
        'promo_banners': promo_banners,
        'total_products_count': total_products_count,
        'selected_category': selected_category,
        'sort_by': sort_by,
        'query': query,
        'min_price': min_price or '',
        'max_price': max_price or '',
    }
    
    return render(request, 'pages/shop.html', context)










def ContactPage(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # ১. ডাটাবেজে মেসেজ সেভ করা
            contact_instance = form.save()

            # ২. গ্যাজেট শপের উপযোগী ইমেইল সাবজেক্ট ও বডি
            email_subject = f"New Inquiry: {contact_instance.subject} (From {contact_instance.name})"
            email_body = (
                f"You have received a new contact message from your Gadget Store.\n\n"
                f"---------------- Contact Details ----------------\n"
                f"Name         : {contact_instance.name}\n"
                f"Email        : {contact_instance.email}\n"
                f"Phone        : {contact_instance.phone}\n"
                f"Inquiry Type : {contact_instance.get_inquiry_type_display()}\n"
                f"Order ID     : {contact_instance.order_number or 'N/A'}\n"
                f"Subject      : {contact_instance.subject}\n"
                f"-------------------------------------------------\n\n"
                f"Message:\n{contact_instance.message}\n"
            )

            # ৩. ইমেইল সেন্ডিং ট্রাই-এক্সেপ্ট ব্লক
            try:
                send_mail(
                    subject=email_subject,
                    message=email_body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.CONTACT_RECEIVER_EMAIL],
                    fail_silently=False,
                )
            except Exception as e:
                # ইমেইল ফেইল করলেও মেসেজ যেন ডাটাবেজে সেভ থাকে তা নিশ্চিত করে কনসোলে প্রিন্ট দেওয়া
                print(f"Failed to send email notification: {e}")

            messages.success(request, 'Thank you! Your message has been sent successfully. Our team will get back to you shortly.')
            return redirect('contact')
            
    else:
        form = ContactForm()

    context = {
        'form': form
    }
    return render(request, 'pages/contact.html', context)






def contact_message_list(request):
    filter_type = request.GET.get('filter', 'all')
    
    if filter_type == 'pending':
        contact_messages = ContactMessage.objects.filter(is_read=False)
    elif filter_type == 'done':
        contact_messages = ContactMessage.objects.filter(is_read=True)
    else:
        contact_messages = ContactMessage.objects.all()

    context = {
        'contact_messages': contact_messages,
        'filter_type': filter_type,
        'pending_count': ContactMessage.objects.filter(is_read=False).count(),
        'done_count': ContactMessage.objects.filter(is_read=True).count(),
        'all_count': ContactMessage.objects.count(),
    }
    return render(request, 'pages/contact_message_list.html', context)



def toggle_message_done(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = not msg.is_read  # is_done এর জায়গায় is_read
    msg.save()
    messages.info(request, "Status updated successfully!")
    return redirect('contact_message_list')


def delete_contact_message(request, pk):
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.delete()
    messages.success(request, "Message deleted successfully!")
    return redirect('contact_message_list')




















def SinglePage(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)

    # POST Request হ্যান্ডলিং
    if request.method == 'POST':
        # ১. Add to Cart ফর্ম সাবমিট হলে
        if 'add_to_cart' in request.POST:
            try:
                quantity = int(request.POST.get('quantity', 1))
            except ValueError:
                quantity = 1

            # সেশনে কার্ট ডাটা সেভ করা
            cart = request.session.get('cart', {})
            product_id = str(product.id)

            if product_id in cart:
                cart[product_id] += quantity
            else:
                cart[product_id] = quantity

            request.session['cart'] = cart
            request.session.modified = True

            messages.success(request, f"{quantity} psc '{product.title}' added to cart successfully!")

            # 🎯 এখানে 'cart' পেজে রিডাইরেক্ট করা হচ্ছে
            return redirect('cart')

        # ২. Review / Comment ফর্ম সাবমিট হলে
        elif 'add_review' in request.POST:
            name = request.POST.get('name')
            email = request.POST.get('email')
            review_text = request.POST.get('review_text')
            rating = request.POST.get('rating', 5)
            image = request.FILES.get('image')

            # Review সেভ করা
            Review.objects.create(
                product=product,
                name=name,
                email=email,
                review_text=review_text,
                rating=int(rating),
                image=image
            )
            messages.success(request, "Thank you for your review!")
            return redirect('single', pk=product.pk)

    # GET Request: ক্যাটাগরি অনুযায়ী Related Products এবং Context প্রস্তুতকরণ
    related_products = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:6]

    context = {
        'product': product,
        'related_products': related_products,
    }

    return render(request, 'pages/single.html', context)









# ১. কার্ট পেজ ভিউ (কুপন ও শিপিং চার্জ সহ)
def CartPage(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total_price = 0

    # সেশন থেকে কার্ট আইটেম প্রসেস করা
    for product_id, item_data in cart.items():
        if isinstance(item_data, dict):
            quantity = item_data.get('quantity', 1)
        else:
            quantity = int(item_data)
            
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total_price += subtotal

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
            'id': product_id
        })

    # ১. ডাইনামিক কুপন ও শিপিং চার্জ ডাটাবেজ থেকে নিয়ে আসা
    coupons = Coupon.objects.filter(is_active=True)
    shipping_charges = ShippingCharge.objects.all()

    # ২. শিপিং চার্জ লজিক (সেশন অথবা ফর্ম সিলেক্ট থেকে)
    selected_shipping_id = request.GET.get('shipping_id') or request.session.get('shipping_id')
    selected_shipping = None
    
    if selected_shipping_id:
        selected_shipping = ShippingCharge.objects.filter(id=selected_shipping_id).first()
    
    # ডিফোল্ট শিপিং সিলেক্ট করা (যদি ইউজার আগে কিছু সিলেক্ট না করে)
    if not selected_shipping:
        selected_shipping = ShippingCharge.objects.filter(is_default=True).first() or shipping_charges.first()
    
    if selected_shipping:
        request.session['shipping_id'] = selected_shipping.id
        delivery_charge = float(selected_shipping.amount)
    else:
        delivery_charge = 0.0

    # ৩. কুপন ও শিপিং ফর্ম সাবমিশন হ্যান্ডলিং
    if request.method == "POST":
        if 'apply_coupon' in request.POST:
            code = request.POST.get('coupon_code', '').strip()
            try:
                coupon = Coupon.objects.get(code__iexact=code, is_active=True)
                request.session['coupon_discount'] = float(coupon.discount_amount)
                request.session['applied_coupon_code'] = coupon.code
                messages.success(request, f"কুপন '{coupon.code}' সফলভাবে যুক্ত হয়েছে!")
            except Coupon.DoesNotExist:
                messages.error(request, "ইনভ্যালিড বা মেয়াদউত্তীর্ণ কুপন কোড!")
            return redirect('cart')

        elif 'remove_coupon' in request.POST:
            request.session.pop('coupon_discount', None)
            request.session.pop('applied_coupon_code', None)
            messages.info(request, "কুপন সরিয়ে ফেলা হয়েছে।")
            return redirect('cart')

    # ৪. সেশন থেকে কুপন তথ্য সংগ্রহ
    coupon_discount = float(request.session.get('coupon_discount', 0))
    applied_coupon_code = request.session.get('applied_coupon_code', '')

    # ৫. গ্র্যান্ড টোটাল হিসাব (Subtotal - Discount + Delivery)
    grand_total = max(0, (float(total_price) - coupon_discount)) + delivery_charge

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'coupons': coupons,
        'shipping_charges': shipping_charges,
        'selected_shipping': selected_shipping,
        'delivery_charge': delivery_charge,
        'coupon_discount': coupon_discount,
        'applied_coupon_code': applied_coupon_code,
        'grand_total': grand_total,
    }
    return render(request, 'pages/cart.html', context)


# ২. কার্টে প্রোডাক্ট যোগ করার ভিউ
def add_to_cart(request, product_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', {})

        str_product_id = str(product_id)

        if str_product_id in cart:
            if isinstance(cart[str_product_id], dict):
                cart[str_product_id]['quantity'] += quantity
            else:
                cart[str_product_id] = {'quantity': int(cart[str_product_id]) + quantity}
        else:
            cart[str_product_id] = {'quantity': quantity}

        request.session['cart'] = cart
        request.session.modified = True
        messages.success(request, "পণ্যটি সাকসেসফুলি কার্টে যোগ করা হয়েছে!")

    return redirect('cart')


# ৩. কার্ট থেকে প্রোডাক্ট ডিলিট করার ভিউ
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        str_item_id = str(item_id)

        if str_item_id in cart:
            del cart[str_item_id]
            request.session['cart'] = cart
            request.session.modified = True
            messages.success(request, "পণ্যটি কার্ট থেকে মুছে ফেলা হয়েছে।")

    return redirect('cart')












# ================= WISHLIST VIEWS =================


def wishlist_view(request):
    wishlist_items = []
    
    # ইউজার লগইন থাকলে কেবল তখনই তার ডাটা তুলে আনা হবে
    if request.user.is_authenticated:
        wishlist_items = Wishlist.objects.filter(user=request.user)

    context = {
        'wishlist_items': wishlist_items,
    }
    return render(request, 'pages/wishlist.html', context)



def add_to_wishlist(request, product_id):
    """Wishlist-এ প্রোডাক্ট যোগ করার ভিউ"""
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)
    
    if created:
        messages.success(request, f"{product.title} wishlisted successfully!")
    else:
        messages.info(request, f"{product.title} is already in your wishlist.")
        
    return redirect(request.META.get('HTTP_REFERER', 'wishlist'))



def remove_from_wishlist(request, product_id):
    """Wishlist থেকে প্রোডাক্ট রিমুভ করার ভিউ"""
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    messages.success(request, "Product removed from wishlist.")
    return redirect('wishlist')


# ================= COMPARE VIEWS (Session Based) =================



def compare_view(request):
    """Session থেকে প্রোডাক্ট আইডি এনে তুলনামূলক পেজ দেখাবে"""
    compare_ids = request.session.get('compare_list', [])
    products = Product.objects.filter(id__in=compare_ids)
    return render(request, 'pages/compare.html', {'products': products})

def add_to_compare(request, product_id):
    """Compare লিস্টে সর্বোচ্চ ৪টি প্রোডাক্ট সেশনে সেভ করবে"""
    compare_list = request.session.get('compare_list', [])
    
    if product_id not in compare_list:
        if len(compare_list) >= 4:
            compare_list.pop(0) # সর্বোচ্চ ৪টি রাখতে প্রথমটি রিমুভ করবে
        compare_list.append(product_id)
        request.session['compare_list'] = compare_list
        messages.success(request, "Product added to compare list!")
    else:
        messages.info(request, "Product is already in compare list.")
        
    return redirect(request.META.get('HTTP_REFERER', 'compare'))



def remove_from_compare(request, product_id):
    """Compare লিস্ট থেকে একটি প্রোডাক্ট বাদ দেবে"""
    compare_list = request.session.get('compare_list', [])
    if product_id in compare_list:
        compare_list.remove(product_id)
        request.session['compare_list'] = compare_list
        messages.success(request, "Product removed from compare list.")
    return redirect('compare')





# ১. চেকআউট পেজ ভিউ
def checkout_page(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.warning(request, "আপনার কার্ট খালি!")
        return redirect('cart')

    cart_items = []
    total_price = 0

    for product_id, item_data in cart.items():
        quantity = item_data.get('quantity', 1) if isinstance(item_data, dict) else int(item_data)
        product = get_object_or_404(Product, id=product_id)
        subtotal = product.price * quantity
        total_price += subtotal
        cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})

    # কুপন ও শিপিং সেশন তথ্য
    coupon_discount = float(request.session.get('coupon_discount', 0))
    shipping_id = request.session.get('shipping_id')
    
    selected_shipping = ShippingCharge.objects.filter(id=shipping_id).first() if shipping_id else ShippingCharge.objects.first()
    delivery_charge = float(selected_shipping.amount) if selected_shipping else 100.0

    grand_total = max(0, (float(total_price) - coupon_discount)) + delivery_charge
    due_amount = grand_total - delivery_charge  # ডেলিভারি চার্জ বাদ দিয়ে বাকিটা COD

    if request.method == "POST":
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        sender_bkash_no = request.POST.get('sender_bkash_no')
        trx_id = request.POST.get('trx_id')

        # অর্ডার অবজেক্ট তৈরি
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=full_name,
            phone=phone,
            address=address,
            city=city,
            subtotal=total_price,
            discount=coupon_discount,
            delivery_charge=delivery_charge,
            grand_total=grand_total,
            due_amount=due_amount,
            sender_bkash_no=sender_bkash_no,
            trx_id=trx_id,
            advance_paid=delivery_charge
        )

        # অর্ডারের আইটেমগুলো সেভ করা
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['product'].price
            )

        # কার্ট এবং সেশন ক্লিন করা
        request.session['cart'] = {}
        request.session.pop('coupon_discount', None)
        request.session.pop('applied_coupon_code', None)
        request.session.modified = True

        return redirect('order_success', order_id=order.order_id)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'coupon_discount': coupon_discount,
        'delivery_charge': delivery_charge,
        'grand_total': grand_total,
        'due_amount': due_amount,
    }
    return render(request, 'pages/checkout.html', context)


# ২. অর্ডার সাকসেস কনফার্মেশন ভিউ
def order_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)
    return render(request, 'pages/order_success.html', {'order': order})




# ৩. অর্ডার ট্র্যাকিং ভিউ
def track_order(request):
    # ADMIN STATUS UPDATE LOGIC
    if request.method == "POST" and "update_status" in request.POST:
        if request.user.is_staff or request.user.is_superuser:
            order_id = request.POST.get("order_id")
            new_status = request.POST.get("status")
            current_status_filter = request.GET.get("status_filter", "")
            
            order = get_object_or_404(Order, order_id=order_id)
            order.status = new_status
            order.save()
            
            messages.success(request, f"Order {order_id} status updated to '{new_status}' successfully!")
            
            # Status update এর পর রিডাইরেক্টে ফিল্টার ফিল্ড ধরে রাখা হবে
            redirect_url = f"{request.path}?order_id={order.order_id}&phone={order.phone}"
            if current_status_filter:
                redirect_url += f"&status_filter={current_status_filter}"
            return redirect(redirect_url)
        
    orders = []
    searched_order = None
    searched = False
    
    # অ্যাডমিন সামারি ডেটা
    admin_summary = {}
    selected_status = request.GET.get('status_filter', '').strip()

    # ১. ইউজার যদি অ্যাডমিন/স্টাফ হন, তবে সকল অর্ডার লোড করা ও ফিল্টার প্রযোজ্য করা
    if request.user.is_staff or request.user.is_superuser:
        all_orders = Order.objects.all().order_by('-created_at')
        
        # স্ট্যাটাস ভিত্তিক সামারি কাউন্ট (ফিল্টারের পূর্বের মোট হিসাবের জন্য)
        admin_summary = {
            'total': all_orders.count(),
            'pending': all_orders.filter(status__iexact='Pending').count(),
            'processing': all_orders.filter(status__iexact='Processing').count(),
            'shipped': all_orders.filter(status__iexact='Shipped').count(),
            'delivered': all_orders.filter(status__iexact='Delivered').count(),
            'cancelled': all_orders.filter(status__iexact='Cancelled').count(),
        }

        # স্ট্যাটাস ফিল্টার সিলেক্ট করা থাকলে কোয়েরি ফিল্টার করা
        if selected_status:
            orders = all_orders.filter(status__iexact=selected_status)
        else:
            orders = all_orders

    # সাধারণ লগইন করা ইউজার হলে শুধু তার নিজস্ব অর্ডার লোড করা
    elif request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # ২. যদি কোনো কাস্টমার Search Form ব্যবহার করে বা টেবিল/স্ট্যাটাস থেকে ক্লিক করে
    order_id = request.POST.get('order_id') or request.GET.get('order_id')
    phone = request.POST.get('phone') or request.GET.get('phone')

    order_id = order_id.strip() if order_id else None
    phone = phone.strip() if phone else None

    if order_id and phone:
        searched = True
        searched_order = Order.objects.filter(
            order_id__iexact=order_id, 
            phone__icontains=phone
        ).first()
    elif order_id:
        searched = True
        searched_order = Order.objects.filter(
            order_id__iexact=order_id
        ).first()

    context = {
        'orders': orders,
        'searched_order': searched_order,
        'searched': searched,
        'admin_summary': admin_summary,
        'selected_status': selected_status, # টেমপ্লেটের জন্য পাঠানো হলো
    }
    return render(request, 'pages/track_order.html', context)



# Create your views here.
