import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg

# ১. কাস্টম ইউজার মডেল
class UserModel(AbstractUser):
    def __str__(self):
        return self.username


# ২. প্রোডাক্ট ক্যাটাগরি মডেল

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    # Category icon/image field
    image = models.ImageField(upload_to='category_imgs/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


# ৩. মূল প্রোডাক্ট মডেল
class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True) # Main / Regular Price
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='product_imgs/')
    stock = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_offer = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_new = models.BooleanField(default=True)       # New Arrivals ফিল্টারের জন্য
    is_featured = models.BooleanField(default=False)  # Featured ফিল্টারের জন্য
    is_top_selling = models.BooleanField(default=False) # Top Selling ফিল্টারের জন্য
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Product SKU")
    facebook_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Facebook Link")
    instagram_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Instagram Link")

    def save(self, *args, **kwargs):
        # যদি SKU ফাঁকা থাকে, তবে সিস্টেম নিজে থেকেই একটি ইউনিক SKU তৈরি করবে
        if not self.sku:
            self.sku = f"PRD-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    @property
    def average_rating(self):
        # প্রোডাক্টের সব রিভিউয়ের rating এর গড় বের করবে
        avg = self.reviews.aggregate(Avg('rating'))['rating__avg']
        return round(avg) if avg is not None else 0

    def __str__(self):
        return self.title

    # dynamic discount percentage calculation logic
    @property
    def discount_percentage(self):
        # বর্তমান বিক্রয় মূল্য নির্ধারণ (new_price থাকলে সেটি, না থাকলে price)
        current = self.new_price if self.new_price else self.price
        
        if self.old_price and self.old_price > current:
            discount = ((self.old_price - current) / self.old_price) * 100
            return int(round(discount))
        return 0




# একাধিক ইমেজের জন্য (অতিরিক্ত গ্যালারি ছবি)
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_imgs/gallery/')




# রিভিউর জন্য
class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(max_length=100)
    email = models.EmailField()
    review_text = models.TextField()
    rating = models.IntegerField(default=5)
    image = models.ImageField(upload_to='review_images/', blank=True, null=True) # নতুন ফিল্ড
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.product.title}"




       
# ৪. উইশলিস্ট মডেল
class Wishlist(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'product') # একই প্রোডাক্ট বারবার যোগ হওয়া আটকাবে

    def __str__(self):
        return f"{self.user.username} - {self.product.title}"


# ৫. কন্টাক্ট মেসেজ মডেল
class ContactMessage(models.Model):
    INQUIRY_CHOICES = [
        ('general', 'General Inquiry'),
        ('product', 'Product Details / Availability'),
        ('order', 'Order Status & Tracking'),
        ('warranty', 'Warranty & Return Support'),
        ('corporate', 'Bulk / Corporate Order'),
    ]

    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    inquiry_type = models.CharField(max_length=50, choices=INQUIRY_CHOICES, default='general')
    order_number = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.subject} ({self.created_at.strftime('%Y-%m-%d') if self.created_at else ''})"


# ৬. স্লাইডার / ক্যারোসেল মডেল
class Carousel(models.Model):
    # Product এর সাথে লিঙ্ক করার জন্য ForeignKey
    product = models.ForeignKey(
        Product, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='carousels',
        help_text="প্রোডাক্ট সিলেক্ট করলে সেটির তথ্য অটো নিয়ে নিবে (Optional)"
    )
    
    # প্রোডাক্ট না থাকলে ম্যানুয়ালি দেওয়ার জন্য ফিল্ডগুলো ফাঁকা (blank=True) রাখা হয়েছে
    title = models.CharField(max_length=255, blank=True, help_text="প্রোডাক্ট সিলেক্ট করলে খালি রাখুন, অটো চলে আসবে")
    sub_title = models.CharField(max_length=255, blank=True, help_text="Subtitle (e.g. Save Up To ৳400)")
    description = models.CharField(max_length=255, blank=True, default="Terms and Conditions Apply")
    image = models.ImageField(upload_to='carousel_imgs/', blank=True, null=True)
    
    button_text = models.CharField(max_length=50, default="Shop Now")
    button_link = models.CharField(max_length=255, default="#", help_text="প্রোডাক্ট সিলেক্ট করা থাকলে কাস্টম লিংক লাগবে না")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Order of appearance")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title or (self.product.title if self.product else f"Carousel #{self.id}")

    # প্রোডাক্ট সিলেক্ট করলে অটোমেটিক টাইটেল, ইমেজ এবং ডিসক্রিপশন নিয়ে নেওয়ার জন্য Logic
    def save(self, *args, **kwargs):
        if self.product:
            if not self.title:
                self.title = self.product.title
            if not self.description:
                self.description = self.product.description or "Terms and Conditions Apply"
            if not self.image and self.product.image:
                self.image = self.product.image
        super().save(*args, **kwargs)


# ৭. প্রোমো ব্যানার মডেল (Product এর সাথে লিংকড)
class PromoBanner(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, related_name='promo_banner')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='promo_banners', help_text="Select the featured product")
    save_amount = models.CharField(max_length=50, help_text="e.g. Save $48.00")
    offer_label = models.CharField(max_length=50, default="Special Offer")
    custom_image = models.ImageField(upload_to='promo_imgs/', blank=True, null=True, help_text="Optional: Leave empty to use product's default image")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Promo: {self.product.title}"




class Coupon(models.Model):
    name = models.CharField(max_length=100) # যেমন: Eid Special Offer
    code = models.CharField(max_length=50, unique=True) # যেমন: EID50
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2) # যেমন: 100
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.code}) - Tk. {self.discount_amount}"

class ShippingCharge(models.Model):
    title = models.CharField(max_length=100) # যেমন: Inside Dhaka
    amount = models.DecimalField(max_digits=10, decimal_places=2) # যেমন: 90
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} - Tk. {self.amount}"







class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending Verification', 'Pending Verification'),
        ('Confirmed', 'Confirmed'),
        ('Processing', 'Processing'),
        ('Shipped', 'Shipped'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    order_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True, blank=True)
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    city = models.CharField(max_length=50)


    # Pricing details
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    delivery_charge = models.DecimalField(max_digits=10, decimal_places=2)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    due_amount = models.DecimalField(max_digits=10, decimal_places=2)

    # Payment details (bKash/Nagad Advance)
    payment_method = models.CharField(max_length=50, default='bKash Advance + COD')
    sender_bkash_no = models.CharField(max_length=15)
    trx_id = models.CharField(max_length=100)
    advance_paid = models.DecimalField(max_digits=10, decimal_places=2)

    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='Pending Verification')
    created_at = models.DateTimeField(auto_now_add=True)
    cancel_reason = models.TextField(blank=True, null=True, verbose_name="Cancellation Reason")

    def save(self, *args, **kwargs):
        if not self.order_id:
            # ইউনিক অর্ডার আইডি জেনারেট করা (যেমন: ORD-8A3F2B)
            self.order_id = 'ORD-' + str(uuid.uuid4())[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_id} - {self.full_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"

  
# Create your models here.
