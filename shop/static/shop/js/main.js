document.addEventListener("DOMContentLoaded", function () {
    const mobileMenuBtn = document.getElementById("mobile-menu-btn");
    const mobileMenu = document.getElementById("mobile-menu");

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener("click", function () {
            mobileMenu.classList.toggle("hidden");
        });

        document.addEventListener("click", function (e) {
            if (!mobileMenuBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.add("hidden");
            }
        });
    }

    const header = document.getElementById("main-header");
    if (header) {
        window.addEventListener("scroll", function () {
            if (window.scrollY > 10) {
                header.classList.add("scrolled");
            } else {
                header.classList.remove("scrolled");
            }
        });
    }

    const announcementBar = document.getElementById("announcement-bar");
    const announcementClose = document.getElementById("announcement-close");
    if (announcementBar && announcementClose) {
        announcementClose.addEventListener("click", function () {
            announcementBar.style.transition = "all 0.3s ease";
            announcementBar.style.maxHeight = "0";
            announcementBar.style.paddingTop = "0";
            announcementBar.style.paddingBottom = "0";
            announcementBar.style.overflow = "hidden";
            setTimeout(function () { announcementBar.remove(); }, 300);
        });
    }
});
