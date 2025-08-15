/*
 * Mobile-First Theme JavaScript
 * =============================
 */

document.addEventListener('DOMContentLoaded', function() {
    // Mobile menu functionality
    const mobileMenu = document.querySelector('.mobile-menu');
    const mobileMenuContent = document.querySelector('.mobile-menu-content');
    const mobileMenuLinks = document.querySelectorAll('.mobile-menu-content a');

    // Initialize mobile menu to closed state
    if (mobileMenu) {
        mobileMenu.classList.remove('active');
        mobileMenu.setAttribute('aria-expanded', 'false');
        document.body.style.overflow = '';
    }

    // Toggle mobile menu
    if (mobileMenu) {
        mobileMenu.addEventListener('click', function() {
            this.classList.toggle('active');
            
            // Update ARIA attributes
            const isExpanded = this.classList.contains('active');
            this.setAttribute('aria-expanded', isExpanded);
            
            // Debug: Log the state
            console.log('Mobile menu clicked, active:', isExpanded);
            
            // Toggle mobile menu content visibility
            if (mobileMenuContent) {
                if (isExpanded) {
                    mobileMenuContent.classList.add('active');
                } else {
                    mobileMenuContent.classList.remove('active');
                }
            }
            
            // Prevent background scroll when menu is open
            if (isExpanded) {
                document.body.style.overflow = 'hidden';
            } else {
                document.body.style.overflow = '';
            }
        });
    }

    // Close menu when clicking on a link
    mobileMenuLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            mobileMenu.classList.remove('active');
            mobileMenu.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (mobileMenu && mobileMenu.classList.contains('active') && 
            !mobileMenu.contains(event.target) && 
            !mobileMenuContent.contains(event.target)) {
            mobileMenu.classList.remove('active');
            mobileMenu.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        }
    });

    // Close menu on escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape' && mobileMenu && mobileMenu.classList.contains('active')) {
            mobileMenu.classList.remove('active');
            mobileMenu.setAttribute('aria-expanded', 'false');
            document.body.style.overflow = '';
        }
    });

    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function(anchor) {
        anchor.addEventListener('click', function(event) {
            event.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading states to buttons
    document.querySelectorAll('.btn, button[type="submit"]').forEach(function(button) {
        // 検索フォームの送信ボタンは除外
        if (button.closest('#search-form')) return;
        button.addEventListener('click', function() {
            if (!this.classList.contains('loading')) {
                this.classList.add('loading');
                this.disabled = true;
                // Remove loading state after a delay (for demo purposes)
                setTimeout(() => {
                    this.classList.remove('loading');
                    this.disabled = false;
                }, 2000);
            }
        });
    });

    // Add focus styles for better accessibility
    document.querySelectorAll('a, button, input, textarea, select').forEach(function(element) {
        element.addEventListener('focus', function() {
            this.classList.add('focused');
        });
        
        element.addEventListener('blur', function() {
            this.classList.remove('focused');
        });
    });

    // Sort buttons functionality
    const sortButtons = document.querySelectorAll('.sort-btn');
    sortButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            sortButtons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            this.classList.add('active');
            
            // Get sort parameters
            const sortBy = this.getAttribute('data-sort');
            const sortOrder = this.getAttribute('data-order');
            
            // Get current URL and parameters
            const url = new URL(window.location);
            url.searchParams.set('sort_by', sortBy);
            url.searchParams.set('sort_order', sortOrder);
            
            // Navigate to new URL
            window.location.href = url.toString();
        });
    });

    // Set active state based on current sort parameters
    const urlParams = new URLSearchParams(window.location.search);
    const currentSortBy = urlParams.get('sort_by');
    const currentSortOrder = urlParams.get('sort_order');
    
    // Default sort is "ag:datePublished" desc (公開日新しい順)
    const defaultSortBy = 'ag:datePublished';
    const defaultSortOrder = 'desc';
    
    // If no sort parameters are set, use defaults
    const sortBy = currentSortBy || defaultSortBy;
    const sortOrder = currentSortOrder || defaultSortOrder;
    
    const activeButton = document.querySelector(`.sort-btn[data-sort="${sortBy}"][data-order="${sortOrder}"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }

    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // Add smooth transitions for page loads
    window.addEventListener('pageshow', function(event) {
        if (event.persisted) {
            document.body.classList.add('page-loaded');
        }
    });

    // Add scroll-based animations
    if ('IntersectionObserver' in window) {
        const animationObserver = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });

        document.querySelectorAll('.card, h1, h2, h3').forEach(function(element) {
            animationObserver.observe(element);
        });
    }

    // Add keyboard navigation for mobile menu
    if (mobileMenu) {
        mobileMenu.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                this.click();
            }
        });
    }

    // Add skip link functionality
    const skipLink = document.getElementById('skipnav');
    if (skipLink) {
        skipLink.addEventListener('click', function(event) {
            event.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.focus();
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    }
}); 

// ページの最上部にスクロールする関数
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}