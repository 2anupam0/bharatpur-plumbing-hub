import re
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from shop.models import Category, Product, SiteSettings


def slugify(name):
    s = name.lower().strip()
    s = s.encode('ascii', 'ignore').decode('ascii')
    s = re.sub(r'[^\w\s-]', '', s)
    s = re.sub(r'[-\s]+', '-', s)
    s = s.strip('-')
    return s


class Command(BaseCommand):
    help = "Seed database with ARUN Suppliers products and categories"

    def handle(self, *args, **options):
        self.stdout.write("Seeding ARUN Suppliers database...")

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@arunplumbing.com", "admin123")
            self.stdout.write(self.style.SUCCESS("Created admin user (admin / admin123)"))

        SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                "shop_name": "ARUN Suppliers",
                "shop_tagline": "All Plumbing & Hardware Materials in Bharatpur",
                "shop_phone": "+9779800000000",
                "shop_email": "info@arunplumbing.com",
                "shop_address": "Bharatpur 44200, Nepal",
                "shop_opening_hours": "Sun-Fri: 8:00 AM - 7:00 PM | Sat: 9:00 AM - 5:00 PM",
                "whatsapp_number": "+9779800000000",
                "free_delivery_threshold": 5000,
                "delivery_fee": 150,
                "announcement_text": "Free delivery on orders above Rs 5,000!",
            },
        )
        s = SiteSettings.objects.get(pk=1)
        updated = False
        for field, default in [
            ("shop_name", "ARUN Suppliers"),
            ("shop_tagline", "All Plumbing & Hardware Materials in Bharatpur"),
            ("shop_phone", "+9779800000000"),
            ("shop_email", "info@arunplumbing.com"),
            ("shop_address", "Bharatpur 44200, Nepal"),
            ("shop_opening_hours", "Sun-Fri: 8:00 AM - 7:00 PM | Sat: 9:00 AM - 5:00 PM"),
        ]:
            if not getattr(s, field):
                setattr(s, field, default)
                updated = True
        if updated:
            s.save()

        Product.objects.all().delete()
        Category.objects.all().delete()
        self.stdout.write("Cleared old categories and products.")

        categories_data = [
            {"name": "CPVC Pipes", "slug": "cpvc-pipes", "icon": "🔧", "sort_order": 1,
             "description": "SDR 11, SDR 13.5 and Schedule-40 CPVC pipes in various sizes"},
            {"name": "Standard CPVC Fittings", "slug": "standard-cpvc-fittings", "icon": "⚙️", "sort_order": 2,
             "description": "Couplers, elbows, tees, cross tees, end caps, clamps and brackets"},
            {"name": "Valves & Hardware", "slug": "valves-hardware", "icon": "🚰", "sort_order": 3,
             "description": "Ball valves, unions, tank connectors, clamps and concealed valves"},
            {"name": "Threaded & Brass Fittings", "slug": "threaded-brass-fittings", "icon": "🔗", "sort_order": 4,
             "description": "CPVC and brass threaded adaptors, elbows, tees and reducers"},
            {"name": "Reducers", "slug": "reducers", "icon": "📏", "sort_order": 5,
             "description": "Reducing couplers, tees and bushes in various size combinations"},
            {"name": "Cement & Sundries", "slug": "cement-sundries", "icon": "🧪", "sort_order": 6,
             "description": "CPVC solvent cement and adhesives"},
        ]

        categories = {}
        for data in categories_data:
            cat, _ = Category.objects.update_or_create(
                slug=data["slug"], defaults=data
            )
            categories[data["slug"]] = cat
            self.stdout.write(f"  Created category: {cat.name}")

        SIZES = ["1-2", "3-4", "1", "1-1-4", "1-1-2", "2", "2-1-2", "3", "4", "6"]
        SIZE_LABELS = ["1/2\"", "3/4\"", "1\"", "1-1/4\"", "1-1/2\"", "2\"", "2-1/2\"", "3\"", "4\"", "6\""]

        def size_price(label):
            mapping = {
                "1/2\"": 85, "3/4\"": 110, "1\"": 150, "1-1/4\"": 210,
                "1-1/2\"": 280, "2\"": 400, "2-1/2\"": 520, "3\"": 680,
                "4\"": 950, "6\"": 1500,
            }
            return mapping.get(label, 100)

        def stock_for_size(label):
            small = ["1/2\"", "3/4\"", "1\""]
            med = ["1-1/4\"", "1-1/2\"", "2\""]
            if label in small:
                return 300
            if label in med:
                return 200
            return 100

        products = []

        # ═══════════════════════════════════════════════════════
        # CATEGORY 1: CPVC PIPES (16 items)
        # ═══════════════════════════════════════════════════════
        pipe_sizes_6 = ["1/2\"", "3/4\"", "1\"", "1-1/4\"", "1-1/2\"", "2\""]
        pipe_sizes_4 = ["2-1/2\"", "3\"", "4\"", "6\""]

        for sz in pipe_sizes_6:
            szs = sz.replace("/", "-").replace("\"", "")
            products.append({
                "name": f"SDR 11 Pipe (3m) - {sz}",
                "category": "cpvc-pipes", "price": size_price(sz), "stock": stock_for_size(sz),
                "unit": "piece", "brand": "ARUN",
                "short_description": f"SDR 11 rated CPVC pipe, 3 metre length, {sz}",
                "description": f"SDR 11 rated CPVC pipe for cold water plumbing. Smooth interior ensures consistent flow. Suitable for residential and commercial water supply. Size: {sz}, Length: 3 metres.",
            })

        for sz in pipe_sizes_6:
            products.append({
                "name": f"SDR 13.5 Pipe (3m) - {sz}",
                "category": "cpvc-pipes", "price": size_price(sz) - 20, "stock": stock_for_size(sz),
                "unit": "piece", "brand": "ARUN",
                "short_description": f"SDR 13.5 rated CPVC pipe, 3 metre length, {sz}",
                "description": f"SDR 13.5 rated pipe for general-purpose plumbing. UV-resistant outer layer. Size: {sz}, Length: 3 metres.",
            })

        for sz in pipe_sizes_4:
            products.append({
                "name": f"CPVC Schedule-40 Pipe (3m) - {sz}",
                "category": "cpvc-pipes", "price": size_price(sz) + 30, "stock": stock_for_size(sz),
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Schedule-40 CPVC pipe, hot and cold water, 3 metre length, {sz}",
                "description": f"CPVC Schedule-40 pipe rated for hot and cold water. Temperature resistance up to 90°C. Pressure rated. Size: {sz}, Length: 3 metres.",
                "is_featured": True if sz in ["2-1/2\"", "3\"", "4\""] else False,
            })

        # ═══════════════════════════════════════════════════════
        # CATEGORY 2: STANDARD CPVC FITTINGS (43 items)
        # ═══════════════════════════════════════════════════════
        std_sizes = ["1/2\"", "3/4\"", "1\"", "1-1/4\"", "1-1/2\"", "2\""]

        def fitting_price(label):
            mapping = {"1/2\"": 10, "3/4\"": 14, "1\"": 18, "1-1/4\"": 25, "1-1/2\"": 32, "2\"": 45}
            return mapping.get(label, 20)

        for sz in std_sizes:
            products.append({
                "name": f"Coupler - {sz}",
                "category": "standard-cpvc-fittings", "price": fitting_price(sz), "stock": 400,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC straight coupler for {sz} pipe",
                "description": f"CPVC socket coupler for joining two {sz} pipes in a straight line. Solvent cement connection. Leak-proof and durable.",
            })

        for sz in std_sizes:
            products.append({
                "name": f"Elbow 90\u00ba - {sz}",
                "category": "standard-cpvc-fittings", "price": fitting_price(sz) + 5, "stock": 400,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC 90-degree elbow for {sz} pipe",
                "description": f"CPVC 90-degree elbow for changing pipe direction at a right angle. {sz} size. Solvent cement type. Smooth interior for unrestricted flow.",
            })

        for sz in std_sizes:
            products.append({
                "name": f"Elbow 45\u00ba - {sz}",
                "category": "standard-cpvc-fittings", "price": fitting_price(sz) + 5, "stock": 350,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC 45-degree elbow for {sz} pipe",
                "description": f"CPVC 45-degree elbow for gradual pipe direction change. {sz} size. Reduces stress on pipe joints. Solvent cement type.",
            })

        for sz in std_sizes:
            products.append({
                "name": f"Tee - {sz}",
                "category": "standard-cpvc-fittings", "price": fitting_price(sz) + 8, "stock": 400,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC tee fitting for {sz} pipe",
                "description": f"CPVC tee fitting for three-way branch connection. {sz} size, all ports equal. Solvent cement connection.",
            })

        cross_sizes = ["1/2\"", "3/4\""]
        for sz in cross_sizes:
            products.append({
                "name": f"Cross Tee - {sz}",
                "category": "standard-cpvc-fittings", "price": fitting_price(sz) + 15, "stock": 250,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC cross tee for {sz} pipe, four-way",
                "description": f"CPVC cross tee fitting for four-way pipe connections. {sz} size. Ideal for complex plumbing layouts. Solvent cement type.",
            })

        for sz in std_sizes:
            products.append({
                "name": f"End Cap - {sz}",
                "category": "standard-cpvc-fittings", "price": fitting_price(sz) - 2, "stock": 400,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC end cap for {sz} pipe",
                "description": f"CPVC end cap for sealing open {sz} pipe ends. Solvent cement connection. Clean, leak-proof finish.",
            })

        for sz in std_sizes:
            products.append({
                "name": f"Pipe Clamp (ABS Plastic) - {sz}",
                "category": "standard-cpvc-fittings", "price": fitting_price(sz) - 3, "stock": 500,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"ABS plastic pipe clamp for {sz} pipe",
                "description": f"Lightweight ABS plastic pipe clamp for securing {sz} pipes to walls. Snap-fit design for easy installation.",
            })

        passover_sizes = ["1/2\"", "3/4\"", "1\""]
        for sz in passover_sizes:
            products.append({
                "name": f"Passover / Step Over Bend - {sz}",
                "category": "standard-cpvc-fittings", "price": fitting_price(sz) + 40, "stock": 120,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Step-over bend for {sz} pipe",
                "description": f"Passover / step-over bend for routing {sz} pipe over another without T-junction. CPVC construction. Smooth flow path.",
            })

        products.append({
            "name": "CPVC Mixer Bracket - Standard Size",
            "category": "standard-cpvc-fittings", "price": 120, "stock": 150,
            "unit": "piece", "brand": "ARUN",
            "short_description": "CPVC bracket for wall-mounted mixer taps",
            "description": "CPVC mixer bracket for securely mounting hot and cold water mixer taps. Pre-set pipe spacing for standard mixer taps. Durable CPVC construction.",
        })

        # ═══════════════════════════════════════════════════════
        # CATEGORY 3: VALVES & HARDWARE (25 items)
        # ═══════════════════════════════════════════════════════
        for sz in std_sizes:
            products.append({
                "name": f"Ball Valve - {sz}",
                "category": "valves-hardware", "price": fitting_price(sz) * 6 + 60, "stock": 150,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Full port ball valve, {sz}",
                "description": f"Full port brass ball valve for quick quarter-turn shut-off. {sz} size. Chrome-plated body. PTFE seat for bubble-tight seal. Lever handle.",
                "is_featured": True if sz in ["1/2\"", "3/4\"", "1\""] else False,
            })

        for sz in std_sizes:
            products.append({
                "name": f"Union - {sz}",
                "category": "valves-hardware", "price": fitting_price(sz) * 3 + 10, "stock": 150,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Threaded union fitting, {sz}",
                "description": f"Threaded union fitting for connecting and disconnecting {sz} pipes without cutting. Allows easy maintenance. Chrome-plated brass.",
            })

        tank_sizes = ["1/2\"", "3/4\"", "1\"", "1-1/4\"", "1-1/2\""]
        for sz in tank_sizes:
            products.append({
                "name": f"Tank Connector - {sz}",
                "category": "valves-hardware", "price": fitting_price(sz) * 3 + 5, "stock": 120,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Tank connector for {sz} pipe",
                "description": f"Tank connector for creating watertight inlet/outlet on water tanks. {sz} size. Rubber gasket seal. Durable PVC and brass construction.",
            })

        for sz in std_sizes:
            products.append({
                "name": f"Metal Clamp (U-Type) - {sz}",
                "category": "valves-hardware", "price": fitting_price(sz) + 3, "stock": 400,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"U-type metal clamp for {sz} pipe",
                "description": f"Heavy-duty U-type metal pipe clamp for securing {sz} pipes to walls. Galvanised steel. Includes screw and anchor.",
            })

        concealed_sizes = ["1/2\"", "3/4\""]
        for sz in concealed_sizes:
            products.append({
                "name": f"Concealed Valve (Chrome Plated) - {sz}",
                "category": "valves-hardware", "price": fitting_price(sz) * 15 + 100, "stock": 80,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Chrome-plated concealed valve, {sz}",
                "description": f"Chrome-plated concealed valve for hidden wall installation. {sz} size. Quarter-turn operation. Ceramic disc cartridge. Modern bathroom installations.",
                "is_featured": True,
            })

        # ═══════════════════════════════════════════════════════
        # CATEGORY 4: THREADED & BRASS FITTINGS (44 items)
        # ═══════════════════════════════════════════════════════
        for sz in std_sizes:
            products.append({
                "name": f"Male Threaded Adaptor CPVC - {sz}",
                "category": "threaded-brass-fittings", "price": fitting_price(sz) + 12, "stock": 300,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC male threaded adaptor, {sz}",
                "description": f"Male threaded adaptor (MTA) for connecting {sz} CPVC pipe to a female threaded fitting. One end solvent cement, other end BSP male thread.",
            })

        for sz in std_sizes:
            products.append({
                "name": f"Female Threaded Adaptor CPVC - {sz}",
                "category": "threaded-brass-fittings", "price": fitting_price(sz) + 12, "stock": 300,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC female threaded adaptor, {sz}",
                "description": f"Female threaded adaptor (FTA) for connecting {sz} CPVC pipe to a male threaded fitting. One end solvent cement, other end BSP female thread.",
            })

        for sz in std_sizes:
            products.append({
                "name": f"Male Threaded Adaptor (Brass) - {sz}",
                "category": "threaded-brass-fittings", "price": fitting_price(sz) + 30, "stock": 250,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Brass male threaded adaptor, {sz}",
                "description": f"Brass male threaded adaptor for connecting {sz} pipes to female threaded fittings. Precision-cut BSP threads. Chrome-plated finish.",
                "is_featured": True if sz in ["1/2\"", "3/4\"", "1\""] else False,
            })

        for sz in std_sizes:
            products.append({
                "name": f"Female Threaded Adaptor (Brass) - {sz}",
                "category": "threaded-brass-fittings", "price": fitting_price(sz) + 30, "stock": 250,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Brass female threaded adaptor, {sz}",
                "description": f"Brass female threaded adaptor for connecting {sz} male threaded fittings to pipes. Chrome-plated brass. Precision BSP threads.",
            })

        fte_sizes = ["1/2\"", "3/4\"", "1\""]
        for sz in fte_sizes:
            products.append({
                "name": f"Female Threaded Elbow (Brass) - {sz}",
                "category": "threaded-brass-fittings", "price": fitting_price(sz) + 45, "stock": 200,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Brass 90\u00ba elbow with female thread, {sz}",
                "description": f"Brass 90-degree elbow with {sz} female threaded ends. Ideal for tight corner connections. Chrome-plated finish. Precision-cut BSP threads.",
                "is_featured": True if sz == "1/2\"" else False,
            })

        products.append({
            "name": "Female Threaded Tee (Brass) - 1/2\"",
            "category": "threaded-brass-fittings", "price": 90, "stock": 150,
            "unit": "piece", "brand": "ARUN",
            "short_description": "Brass tee with three 1/2\" female threaded ports",
            "description": "Brass tee fitting with three 1/2\" female threaded ports. Ideal for branching water lines with threaded connections. Chrome-plated finish.",
        })

        products.append({
            "name": "End Plug Threaded - Standard Size",
            "category": "threaded-brass-fittings", "price": 25, "stock": 400,
            "unit": "piece", "brand": "ARUN",
            "short_description": "Threaded end plug for sealing pipe ends",
            "description": "Threaded metal end plug for sealing open pipe or fitting ends. BSP thread. Durable brass construction.",
        })

        products.append({
            "name": "Reducer Elbow 90\u00ba - 3/4\" x 1/2\"",
            "category": "threaded-brass-fittings", "price": 35, "stock": 200,
            "unit": "piece", "brand": "ARUN",
            "short_description": "CPVC reducer elbow 90\u00ba, 3/4\" to 1/2\"",
            "description": "CPVC reducer elbow 90-degree fitting connecting 3/4\" to 1/2\" pipe while changing direction. Solvent cement connection.",
        })

        products.append({
            "name": "Reducer Elbow 90\u00ba - 1\" x 3/4\"",
            "category": "threaded-brass-fittings", "price": 40, "stock": 200,
            "unit": "piece", "brand": "ARUN",
            "short_description": "CPVC reducer elbow 90\u00ba, 1\" to 3/4\"",
            "description": "CPVC reducer elbow 90-degree fitting connecting 1\" to 3/4\" pipe. Solvent cement connection.",
        })

        products.append({
            "name": "Reducer MTA CPVC - 3/4\" x 1/2\"",
            "category": "threaded-brass-fittings", "price": 32, "stock": 250,
            "unit": "piece", "brand": "ARUN",
            "short_description": "CPVC reducing male threaded adaptor, 3/4\" to 1/2\"",
            "description": "Reducing male threaded adaptor to connect 3/4\" CPVC pipe to 1/2\" female threaded fitting. Solvent cement to male thread.",
        })

        rmta_sizes = [("3/4\" x 1/2\"", 48), ("1\" x 1/2\"", 55)]
        for label, price in rmta_sizes:
            products.append({
                "name": f"Reducing MTA (Brass) - {label}",
                "category": "threaded-brass-fittings", "price": price, "stock": 200,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Brass reducing male threaded adaptor, {label}",
                "description": f"Reducing brass male threaded adaptor for {label} connection. Precision-machined threads. Chrome-plated finish.",
            })

        rfta_sizes = [("3/4\" x 1/2\"", 48), ("1\" x 1/2\"", 55)]
        for label, price in rfta_sizes:
            products.append({
                "name": f"Reducer FTA (Brass) - {label}",
                "category": "threaded-brass-fittings", "price": price, "stock": 200,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Brass reducing female threaded adaptor, {label}",
                "description": f"Reducing brass female threaded adaptor for {label} connection. Chrome-plated brass construction.",
            })

        rfel_sizes = [("3/4\" x 1/2\"", 70), ("1\" x 1/2\"", 80)]
        for label, price in rfel_sizes:
            products.append({
                "name": f"Reducer Female Elbow (Brass) - {label}",
                "category": "threaded-brass-fittings", "price": price, "stock": 150,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Brass reducing female threaded elbow, {label}",
                "description": f"Reducing brass 90-degree elbow with female threaded ends for {label} connection. Chrome-plated finish.",
            })

        rft_sizes = [("3/4\" x 1/2\"", 85), ("1\" x 1/2\"", 95)]
        for label, price in rft_sizes:
            products.append({
                "name": f"Reducer Female Tee (Brass) - {label}",
                "category": "threaded-brass-fittings", "price": price, "stock": 150,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"Brass reducing female threaded tee, {label}",
                "description": f"Reducing brass tee with female threaded ports for {label} connection. Chrome-plated brass. Precision-cut BSP threads.",
            })

        products.append({
            "name": "Double Female Elbow (Brass) All Down - 3/4\" x 1/2\"",
            "category": "threaded-brass-fittings", "price": 85, "stock": 120,
            "unit": "piece", "brand": "ARUN",
            "short_description": "Double female brass elbow, 3/4\" x 1/2\"",
            "description": "Double female brass elbow with two female threaded outlets (3/4\" and 1/2\") at 90-degree angle. Heavy-duty brass. Chrome-plated finish.",
        })

        products.append({
            "name": "Triple Female Elbow (Brass) Top Bottom Adaptor - 3/4\" x 1/2\"",
            "category": "threaded-brass-fittings", "price": 110, "stock": 100,
            "unit": "piece", "brand": "ARUN",
            "short_description": "Triple female brass elbow, 3/4\" x 1/2\"",
            "description": "Triple female brass elbow with three female threaded ports at 90-degree angles. 3/4\" x 1/2\" sizes. Chrome-plated brass. Complex plumbing layouts.",
        })

        # ═══════════════════════════════════════════════════════
        # CATEGORY 5: DEDICATED REDUCERS (32 items)
        # ═══════════════════════════════════════════════════════
        rc_pairs = [
            ("3/4\" x 1/2\"", 18), ("1\" x 1/2\"", 25), ("1\" x 3/4\"", 22),
            ("1-1/4\" x 1/2\"", 35), ("1-1/4\" x 3/4\"", 32), ("1-1/2\" x 3/4\"", 40),
            ("1-1/2\" x 1\"", 38), ("2\" x 3/4\"", 55), ("2\" x 1\"", 50),
            ("2\" x 1-1/4\"", 48), ("2\" x 1-1/2\"", 45),
        ]
        for label, price in rc_pairs:
            products.append({
                "name": f"Reducing Coupler - {label}",
                "category": "reducers", "price": price, "stock": 250,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC reducing coupler {label}",
                "description": f"CPVC reducing coupler for connecting {label} pipes. Solvent cement connection. Smooth interior for consistent flow.",
            })

        rt_pairs = [
            ("3/4\" x 1/2\"", 22), ("1\" x 1/2\"", 30), ("1\" x 3/4\"", 28),
            ("1-1/4\" x 3/4\"", 38), ("1-1/4\" x 1\"", 35),
            ("1-1/2\" x 1\"", 42), ("2\" x 3/4\"", 60), ("2\" x 1\"", 55),
            ("2\" x 1-1/4\"", 52), ("2\" x 1-1/2\"", 50),
        ]
        for label, price in rt_pairs:
            products.append({
                "name": f"Reducing Tee - {label}",
                "category": "reducers", "price": price, "stock": 250,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC reducing tee {label}",
                "description": f"CPVC reducing tee for connecting {label} pipes in a three-way branch. Solvent cement connection.",
            })

        rb_pairs = [
            ("3/4\" x 1/2\"", 15), ("1\" x 1/2\"", 22), ("1-1/4\" x 1/2\"", 30),
            ("1-1/4\" x 3/4\"", 28), ("1-1/2\" x 3/4\"", 35), ("1-1/2\" x 1\"", 32),
            ("2\" x 3/4\"", 50), ("2\" x 1\"", 48), ("2\" x 1-1/4\"", 45), ("2\" x 1-1/2\"", 42),
        ]
        for label, price in rb_pairs:
            products.append({
                "name": f"Reducing Bush - {label}",
                "category": "reducers", "price": price, "stock": 250,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"CPVC reducing bush {label}",
                "description": f"CPVC reducing bush for transitioning from {label} pipe. Solvent cement connection. Compact design for tight spaces.",
            })

        products.append({
            "name": "Additional Matrix Variation 1",
            "category": "reducers", "price": 25, "stock": 100,
            "unit": "piece", "brand": "ARUN",
            "short_description": "Specialty reducer fitting variation",
            "description": "Specialty CPVC reducer fitting for non-standard pipe size transitions. Contact us for specific size requirements.",
        })

        products.append({
            "name": "Additional Matrix Variation 2",
            "category": "reducers", "price": 25, "stock": 100,
            "unit": "piece", "brand": "ARUN",
            "short_description": "Specialty reducer fitting variation",
            "description": "Specialty CPVC reducer fitting for non-standard pipe size transitions. Contact us for specific size requirements.",
        })

        # ═══════════════════════════════════════════════════════
        # CATEGORY 6: CEMENT & SUNDRIES (3 items)
        # ═══════════════════════════════════════════════════════
        cement_sizes = [("59ml", 65), ("118ml", 120), ("237ml", 250)]
        for vol, price in cement_sizes:
            products.append({
                "name": f"CPVC Solvent Cement (NSF) - {vol}",
                "category": "cement-sundries", "price": price, "stock": 200,
                "unit": "piece", "brand": "ARUN",
                "short_description": f"NSF-certified CPVC solvent cement, {vol}",
                "description": f"NSF-certified CPVC solvent cement ({vol}) for joining CPVC pipes and fittings. Quick-setting formula. Permanent, leak-proof bond. Suitable for potable water systems.",
                "is_featured": True if vol == "237ml" else False,
            })

        # ── Create all products ──
        slug_counts = {}
        for data in products:
            category = categories[data.pop("category")]
            base_slug = slugify(data["name"])
            if base_slug in slug_counts:
                slug_counts[base_slug] += 1
                slug = f"{base_slug}-{slug_counts[base_slug]}"
            else:
                slug_counts[base_slug] = 1
                slug = base_slug
            data.setdefault("is_featured", False)
            Product.objects.update_or_create(
                slug=slug,
                defaults={**data, "category": category, "is_active": True},
            )
            self.stdout.write(f"  Created: {data['name']}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Created {len(categories_data)} categories and {len(products)} products."
        ))
        self.stdout.write(self.style.SUCCESS(
            "Run the server: python manage.py runserver"
        ))
