from flask import Blueprint, render_template


bp = Blueprint("links", __name__, url_prefix="/links")


@bp.route("/")
def links():

    links = [
        {
            "url": "https://medium.com/@ankur_anand/the-terrible-performance-cost-of-cors-api-on-the-single-page-application-spa-6fcf71e50147",
            "domain": "medium.com",
            "title": "The Terrible Performance Cost of CORS Request on the Single-Page Application",
            "description": "CORS request is very expensive on a SPA",
            "tags": ["web", "cors"],
        },
        {
            "url": "https://www.reclaimerlabs.com/blog/2018/8/7/the-usb-c-explorer",
            "domain": "reclaimerlabs.com",
            "title": "USB-C Explorer – A development board to get started working with USB Type-C",
            "tags": ["hardware", "usb"],
        },
        {
            "url": "https://www.youtube.com/watch?v=Bo3lUw9GUJA",
            "domain": "youtube.com",
            "title": "	SGI's $250,000 Graphics Supercomputer from 1993 – Onyx RealityEngine² [video]",
            "tags": ["video", "computers"],
        },
        {
            "url": "https://google.com",
            "domain": "google.com",
            "title": "Google",
            "tags": ["search"],
        },
        {
            "url": "https://facebook.com",
            "domain": "facebook.com",
            "title": "Facebook",
            "tags": ["social", "old", "wall"],
        },
        {
            "url": "https://twitter.com",
            "domain": "twitter.com",
            "title": "Twitter",
            "tags": ["social", "microblog"],
        },
        {
            "url": "https://instagram.com",
            "domain": "instagram.com",
            "title": "Instagram",
            "tags": ["social", "images", "models"],
            "description": (
                "Instagram is a social site of some repute. "
                "Users can share images, videos etc to their followers."
            ),
        },
    ]
    config = {
        "show_target_link": True,
        "show_target_domain": True,
        "open_new_tab": True,
        "show_copy_link": True,
    }
    return render_template("links.html", links=links, config=config)
