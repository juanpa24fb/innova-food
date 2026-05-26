document.addEventListener("DOMContentLoaded", function () {
    const animatedSelectors = [
        ".section-title",
        ".section-subtitle",
        ".info-card",
        ".product-card",
        ".form-box",
        ".table-box",
        ".total-box",
        ".hero-card",
        ".hero-text",
        ".messages",
        "table",
        "form"
    ];

    animatedSelectors.forEach(selector => {
        document.querySelectorAll(selector).forEach((element, index) => {
            element.classList.add("reveal");
            element.style.transitionDelay = `${Math.min(index * 80, 400)}ms`;
        });
    });

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("active");
            }
        });
    }, {
        threshold: 0.12
    });

    document.querySelectorAll(".reveal").forEach(element => {
        observer.observe(element);
    });

    const header = document.querySelector(".header");

    window.addEventListener("scroll", function () {
        if (window.scrollY > 40) {
            header.classList.add("header-scrolled");
        } else {
            header.classList.remove("header-scrolled");
        }
    });

    document.querySelectorAll(".btn").forEach(button => {
        button.addEventListener("mousemove", function (e) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            button.style.setProperty("--x", `${x}px`);
            button.style.setProperty("--y", `${y}px`);
        });
    });
});
