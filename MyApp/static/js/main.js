(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner(0);
    
    
    // Initiate the wowjs
    new WOW().init();


    // Sticky Navbar
    $(window).scroll(function () {
        if ($(this).scrollTop() > 45) {
            $('.nav-bar').addClass('sticky-top shadow-sm');
        } else {
            $('.nav-bar').removeClass('sticky-top shadow-sm');
        }
    });



    // Hero Header carousel
    $(".header-carousel").owlCarousel({
        items: 1,
        autoplay: true,
        smartSpeed: 2000,
        center: false,
        dots: false,
        loop: true,
        margin: 0,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ]
    });


    // ProductList carousel
    $(".productList-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 2000,
        dots: false,
        loop: true,
        margin: 25,
        nav : true,
        navText : [
            '<i class="fas fa-chevron-left"></i>',
            '<i class="fas fa-chevron-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0:{
                items:1
            },
            576:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:2
            },
            1200:{
                items:3
            }
        }
    });

    // ProductList categories carousel
    $(".productImg-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        dots: false,
        loop: true,
        items: 1,
        margin: 25,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ]
    });


    // Single Products carousel
    $(".single-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        dots: true,
        dotsData: true,
        loop: true,
        items: 1,
        nav : true,
        navText : [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ]
    });


    // ProductList carousel
    $(".related-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        dots: false,
        loop: true,
        margin: 25,
        nav : true,
        navText : [
            '<i class="fas fa-chevron-left"></i>',
            '<i class="fas fa-chevron-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0:{
                items:1
            },
            576:{
                items:1
            },
            768:{
                items:2
            },
            992:{
                items:3
            },
            1200:{
                items:4
            }
        }
    });





    
   // Back to top button

    const backToTopBtn = document.getElementById('backToTop');

    // Window scroll event listener
    window.addEventListener('scroll', () => {
        // Page 300px er beshi scroll korle button show hobe
        if (window.scrollY > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });

    // Smooth scroll to top when clicked
    backToTopBtn.addEventListener('click', (e) => {
        e.preventDefault();
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });


   

})(jQuery);








// baseForm design

document.addEventListener('DOMContentLoaded', function () {
    const toggleButtons = document.querySelectorAll('.btn-password-toggle');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', function () {
            const inputField = this.previousElementSibling;
            const icon = this.querySelector('i');
            
            if (inputField.type === 'password') {
                inputField.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                inputField.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });
});




 // ==========================================
// 1. Our Products Filtering (Clean Single Implementation)
// ==========================================
document.addEventListener('DOMContentLoaded', function () {
    const filterBtns = document.querySelectorAll('.filter-btn');
    const productItems = document.querySelectorAll('#product-grid .product-item');

    if (!filterBtns.length || !productItems.length) return;

    filterBtns.forEach(btn => {
        btn.addEventListener('click', function () {
            // 1. Active Button Toggle
            filterBtns.forEach(b => {
                b.classList.remove('active');
                b.classList.add('text-secondary');
            });
            this.classList.add('active');
            this.classList.remove('text-secondary');

            // 2. Extract Data Filter Value
            const filterValue = this.getAttribute('data-filter');

            // 3. Filter Items
            productItems.forEach(item => {
                if (filterValue === 'all' || item.classList.contains(filterValue)) {
                    item.style.setProperty('display', 'block', 'important');
                    item.style.animation = 'fadeIn 0.3s ease';
                } else {
                    item.style.setProperty('display', 'none', 'important');
                }
            });
        });
    });
});

// Ensure execution on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProductFilter);
} else {
    initProductFilter();
}


// ==========================================
// 2. Owl Carousel Initialization
// ==========================================
$(document.ready).ready(function(){
    var $carousel = $(".offer-carousel");
    
    if ($carousel.length) {
        $carousel.owlCarousel({
            autoplay: true,
            autoplayTimeout: 3500, // 3.5 Seconds
            autoplayHoverPause: true,
            smartSpeed: 800,
            loop: true,
            margin: 24,
            dots: true,
            nav: false,
            responsiveRefreshRate: 100,
            responsive: {
                0: { items: 1 },    // Mobile 1 Item
                768: { items: 2 }   // Desktop 2 Items
            }
        });

        // Force refresh to handle dynamic Django elements
        setTimeout(function(){
            $carousel.trigger('refresh.owl.carousel');
        }, 300);
    }
});


// ==========================================
// 3. Native Share & Clipboard Copy Function
// ==========================================
function shareProduct() {
    const shareData = {
        title: "{{ product.title|escapejs }}",
        text: "Check out this product: {{ product.title|escapejs }}",
        url: window.location.href
    };

    if (navigator.share) {
        navigator.share(shareData)
            .catch((err) => console.log('Share canceled', err));
    } else {
        navigator.clipboard.writeText(window.location.href).then(() => {
            alert('Product link copied to clipboard! You can share it anywhere.');
        }).catch(err => {
            console.error('Failed to copy: ', err);
        });
    }
}


// Spinner hide logic
var spinner = function () {
    setTimeout(function () {
        if ($('#spinner').length > 0) {
            $('#spinner').removeClass('show');
        }
    }, 1);
};
spinner();





$(document).ready(function(){
    $(".productImg-carousel").each(function(){
        var $carousel = $(this);
        var categoryId = $carousel.data("category");
        
        $carousel.owlCarousel({
            loop: true,
            margin: 0,
            nav: false,
            dots: false,
            autoplay: false,
            smartSpeed: 400,
            responsive: {
                0: {
                    items: 1
                },
                1000: {
                    items: 1
                }
            }
        });

        // Top Custom Nav Click Handler
        $("#nav-" + categoryId + " .custom-prev").off('click').on("click", function(e){
            e.preventDefault();
            $carousel.trigger('prev.owl.carousel');
        });

        $("#nav-" + categoryId + " .custom-next").off('click').on("click", function(e){
            e.preventDefault();
            $carousel.trigger('next.owl.carousel');
        });
    });
});






$(document).ready(function(){
    $(".promo-banner-carousel").owlCarousel({
        loop: true,
        margin: 24,
        nav: false,
        dots: true,
        autoplay: true,
        autoplayTimeout: 4000,
        autoplayHoverPause: true,
        smartSpeed: 600,
        responsive: {
            0: {
                items: 1
            },
            768: {
                items: 2
            }
        }
    });
});






function selectCategory(slug, name, event) {
    event.preventDefault();
    // Update hidden input value for form submit
    document.getElementById('selectedCategoryInput').value = slug;
    // Update button text
    document.getElementById('selectedCatText').innerText = name;
    
    // Close dropdown
    const dropdownEl = document.getElementById('catDropdownBtn');
    const bsDropdown = bootstrap.Dropdown.getInstance(dropdownEl);
    if(bsDropdown) {
        bsDropdown.hide();
    }
}
