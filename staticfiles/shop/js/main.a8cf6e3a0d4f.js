document.addEventListener("DOMContentLoaded", function () {

    // Mobile menu toggle
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const mobileMenu = document.getElementById("mobile-menu");

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener("click", function (e) {
            e.stopPropagation();
            mobileMenu.classList.toggle("hidden");
            const icon = mobileMenuBtn.querySelector("i");
            if (mobileMenu.classList.contains("hidden")) {
                icon.className = "fas fa-bars text-gray-600 text-lg";
            } else {
                icon.className = "fas fa-times text-gray-600 text-lg";
            }
        });

        document.addEventListener("click", function (e) {
            if (!mobileMenuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.add("hidden");
                const icon = mobileMenuBtn.querySelector("i");
                if (icon) icon.className = "fas fa-bars text-gray-600 text-lg";
            }
        });
    }

    // Header scroll effect
    const header = document.getElementById("main-header");
    if (header) {
        let lastScroll = 0;
        window.addEventListener("scroll", function () {
            const currentScroll = window.scrollY;
            if (currentScroll > 10) {
                header.classList.add("scrolled");
            } else {
                header.classList.remove("scrolled");
            }
            lastScroll = currentScroll;
        }, { passive: true });
    }

    // Announcement bar close
    const announcementBar = document.getElementById("announcement-bar");
    const announcementClose = document.getElementById("announcement-close");
    if (announcementBar && announcementClose) {
        announcementClose.addEventListener("click", function () {
            announcementBar.classList.add("collapsed");
            setTimeout(function () { announcementBar.remove(); }, 350);
        });
    }

    // Scroll-triggered fade-in animations
    const animateElements = document.querySelectorAll(".animate-in");
    if (animateElements.length > 0 && "IntersectionObserver" in window) {
        const observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.style.animationPlayState = "running";
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1, rootMargin: "0px 0px -40px 0px" });

        animateElements.forEach(function (el) {
            el.style.animationPlayState = "paused";
            observer.observe(el);
        });
    }

    // Active nav link highlighting
    const currentPath = window.location.pathname;
    document.querySelectorAll(".nav-link").forEach(function (link) {
        if (link.getAttribute("href") === currentPath) {
            link.classList.add("text-primary-700", "bg-primary-50");
            link.classList.remove("text-gray-600");
        }
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener("click", function (e) {
            const target = document.querySelector(this.getAttribute("href"));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: "smooth", block: "start" });
            }
        });
    });

});
