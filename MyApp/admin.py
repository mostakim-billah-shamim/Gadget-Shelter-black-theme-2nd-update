from django.contrib import admin
from django.utils.html import format_html
from .models import (
    UserModel, Category, Product, Wishlist, 
    ContactMessage, Carousel, PromoBanner, Review, ProductImage
)
from .models import *



# ১. Simple Model Registrations
admin.site.register(UserModel)
admin.site.register(Category)
admin.site.register(Wishlist)
admin.site.register(ContactMessage)


# ২. PromoBanner Admin
@admin.register(PromoBanner)
class PromoBannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_product_title', 'get_category_name', 'get_price', 'is_active')
    list_editable = ('is_active',)

    @admin.display(ordering='product__title', description='Product Title')
    def get_product_title(self, obj):
        return obj.product.title if obj.product else "-"

    @admin.display(ordering='product__category', description='Category Name')
    def get_category_name(self, obj):
        return obj.product.category.name if obj.product and obj.product.category else "-"

    @admin.display(ordering='product__price', description='New Price')
    def get_price(self, obj):
        return obj.product.price if obj.product else "-"


# ৩. Carousel Admin
@admin.register(Carousel)
class CarouselAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'sub_title', 'is_active', 'order')
    list_editable = ('is_active', 'sub_title', 'order')
    list_display_links = ('id', 'title')


# ৪. Review Inline Setup (অবশ্যই ProductAdmin এর আগে থাকতে হবে)
class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('created_at',)
    fields = ('name', 'email', 'rating', 'review_text', 'created_at')


# ১. ProductImage এর জন্য Inline Class তৈরি করুন
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3  # বাই-ডিফল্ট ৩টি খালি আপলোড ফিল্ড দেখাবে
    fields = ('image',)  # ইনলাইনে শুধু ইমেজের ফিল্ডটি দেখাবে


# ৫. Product Admin Configuration
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'product_image',
        'title',
        'category',
        'display_price',
        'discount_badge',
        'stock',
        'display_rating',
        'is_active',
        'is_new',
        'is_featured',
        'is_top_selling',
        'is_offer',
    )

    list_display_links = ('product_image', 'title')

    list_filter = (
        'category',
        'is_active',
        'is_offer',
        'is_new',
        'is_featured',
        'is_top_selling',
        'created_at',
    )

    search_fields = ('title', 'description')
    list_editable = ('stock', 'is_active', 'is_new','is_offer', 'is_featured', 'is_top_selling')
    list_per_page = 20
    inlines = [ProductImageInline, ReviewInline]
    # SKU দিয়ে সহজে এডমিন প্যানেলে সার্চ করার জন্য:
    search_fields = ('title', 'sku', 'description')

    # --- Custom Methods ---
    def product_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 45px; height: 45px; object-fit: cover; border-radius: 6px;" />', obj.image.url)
        return "No Image"
    product_image.short_description = "Image"

    def display_price(self, obj):
        current_price = obj.new_price if obj.new_price else obj.price
        if obj.old_price:
            return format_html('<del style="color: red; font-size: 11px;">৳{}</del> <br><b>৳{}</b>', obj.old_price, current_price)
        return f"৳{current_price}" if current_price else "N/A"
    display_price.short_description = "Price"

    def discount_badge(self, obj):
        discount = obj.discount_percentage
        if discount > 0:
            return format_html('<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 10px; font-weight: bold; font-size: 11px;">-{}%</span>', discount)
        return "-"
    discount_badge.short_description = "Discount"

    def display_rating(self, obj):
        rating = obj.average_rating
        stars = "★" * rating + "☆" * (5 - rating)
        count = obj.reviews.count()
        return format_html('<span style="color: #ffc107; font-size: 14px;">{}</span> <small style="color: #6c757d;">({})</small>', stars, count)
    display_rating.short_description = "Rating"


# ৬. Review Admin (আলাদাভাবে সব রিভিউ দেখার জন্য)
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'product', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('name', 'email', 'review_text')




# ১. Coupon Admin রেজিস্টার
@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'discount_amount', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('code', 'name')
    list_editable = ('is_active',)  # অ্যাডমিন লিস্ট থেকেই এক ক্লিকে চালু/বন্ধ করা যাবে


# ২. ShippingCharge Admin রেজিস্টার
@admin.register(ShippingCharge)
class ShippingChargeAdmin(admin.ModelAdmin):
    list_display = ('title', 'amount', 'is_default')
    list_editable = ('amount', 'is_default')  # সরাসরি লিস্ট থেকে টাকা ও ডিফোল্ট পরিবর্তন করা যাবে
    search_fields = ('title',)





class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'full_name', 'phone', 'grand_total', 'advance_paid', 'due_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_id', 'full_name', 'phone', 'trx_id')
    list_editable = ('status',) # অ্যাডমিন এখান থেকেই সরাসরি অর্ডার স্ট্যাটাস চেঞ্জ করতে পারবেন
    inlines = [OrderItemInline]