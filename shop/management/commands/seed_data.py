from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from shop.models import Category, Product, SiteSettings


class Command(BaseCommand):
    help = "Seed database with sample products and categories"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@bharatpurplumbing.com", "admin123")
            self.stdout.write(self.style.SUCCESS("Created admin user (admin / admin123)"))

        SiteSettings.objects.get_or_create(
            pk=1,
            defaults={
                "whatsapp_number": "+9779800000000",
                "free_delivery_threshold": 5000,
                "delivery_fee": 150,
                "announcement_text": "Free delivery on orders above Rs 5,000!",
            },
        )

        categories_data = [
            {"name": "Pipes", "slug": "pipes", "icon": "🔧", "sort_order": 1,
             "description": "PVC, CPVC, HDPE and GI pipes for all plumbing needs"},
            {"name": "Fittings", "slug": "fittings", "icon": "⚙️", "sort_order": 2,
             "description": "Elbows, tees, couplings, and all pipe fittings"},
            {"name": "Taps & Showers", "slug": "taps-showers", "icon": "🚿", "sort_order": 3,
             "description": "Kitchen taps, bathroom taps, shower heads and sets"},
            {"name": "Bathroom & Sanitary", "slug": "bathroom-sanitary", "icon": "🛁", "sort_order": 4,
             "description": "Toilets, basins, mirrors, and bathroom accessories"},
            {"name": "Tools", "slug": "tools", "icon": "🔨", "sort_order": 5,
             "description": "Plumbing tools, wrenches, cutters and more"},
            {"name": "Valves & Accessories", "slug": "valves-accessories", "icon": "🚰", "sort_order": 6,
             "description": "Ball valves, gate valves, connectors and accessories"},
        ]

        categories = {}
        for data in categories_data:
            cat, _ = Category.objects.update_or_create(
                slug=data["slug"], defaults=data
            )
            categories[data["slug"]] = cat
            self.stdout.write(f"  Created category: {cat.name}")

        products_data = [
            # Pipes
            {"name": "1/2 inch PVC Pipe (10ft)", "slug": "pvc-pipe-half-inch",
             "category": "pipes", "price": 85, "original_price": 100,
             "stock": 200, "unit": "piece", "brand": "Supreme",
             "short_description": "High-quality PVC pipe for residential water supply",
             "description": "Durable 1/2 inch PVC pipe suitable for cold water supply lines. Made from virgin PVC material, resistant to corrosion and chemicals. Length: 10 feet. ISI marked product.", "is_featured": True},
            {"name": "1 inch PVC Pipe (10ft)", "slug": "pvc-pipe-1-inch",
             "category": "pipes", "price": 180, "original_price": 210,
             "stock": 150, "unit": "piece", "brand": "Supreme",
             "short_description": "1 inch PVC pipe for main water lines",
             "description": "Heavy-duty 1 inch PVC pipe for main water distribution lines. Suitable for both residential and commercial use. Pressure rating: 6 kg/cm2. Length: 10 feet.", "is_featured": False},
            {"name": "CPVC Pipe 1/2 inch (10ft)", "slug": "cpvc-pipe-half-inch",
             "category": "pipes", "price": 150, "stock": 120,
             "unit": "piece", "brand": "Astral",
             "short_description": "Hot and cold water CPVC pipe",
             "description": "CPVC pipe rated for both hot and cold water applications. Temperature resistance up to 90C. Ideal for bathroom and kitchen plumbing. ISI certified.", "is_featured": True},
            {"name": "HDPE Pipe 1 inch (6m)", "slug": "hdpe-pipe-1-inch",
             "category": "pipes", "price": 450, "stock": 50,
             "unit": "piece", "brand": "Finolex",
             "short_description": "Heavy-duty HDPE pipe for underground use",
             "description": "High-density polyethylene pipe suitable for underground water supply and irrigation. Flexible, durable, and UV resistant. Length: 6 meters.", "is_featured": False},
            {"name": "GI Pipe 3/4 inch (6ft)", "slug": "gi-pipe-3-4-inch",
             "category": "pipes", "price": 220, "original_price": 260,
             "stock": 80, "unit": "piece", "brand": "Tata",
             "short_description": "Galvanized iron pipe for heavy-duty use",
             "description": "Hot-dip galvanized iron pipe for water supply lines. Corrosion resistant zinc coating. Suitable for exposed plumbing. Length: 6 feet.", "is_featured": False},

            # Fittings
            {"name": "PVC Elbow 1/2 inch (Pack of 10)", "slug": "pvc-elbow-half-inch",
             "category": "fittings", "price": 60, "stock": 300,
             "unit": "pack", "brand": "Supreme",
             "short_description": "90-degree PVC elbow fittings",
             "description": "Pack of 10 PVC elbow fittings, 90-degree angle. Perfect for connecting pipes at corners. Solvent cement type connection. ISI approved.", "is_featured": True},
            {"name": "PVC Tee Joint 3/4 inch", "slug": "pvc-tee-3-4-inch",
             "category": "fittings", "price": 35, "stock": 250,
             "unit": "piece", "brand": "Supreme",
             "short_description": "T-joint for 3/4 inch PVC pipes",
             "description": "Tee joint fitting for 3/4 inch PVC pipe connections. Allows branching of water lines. Strong and leak-proof design.", "is_featured": False},
            {"name": "CPVC Elbow 1/2 inch (Pack of 10)", "slug": "cpvc-elbow-half-inch",
             "category": "fittings", "price": 120, "stock": 200,
             "unit": "pack", "brand": "Astral",
             "short_description": "CPVC elbow fittings for hot water",
             "description": "CPVC 90-degree elbow fittings rated for hot water. Temperature resistant up to 90C. Cement type joint. Pack of 10 pieces.", "is_featured": False},
            {"name": "PPR Coupling 1 inch", "slug": "ppr-coupling-1-inch",
             "category": "fittings", "price": 85, "stock": 180,
             "unit": "piece", "brand": "Astral",
             "short_description": "PPR coupling for 1 inch pipes",
             "description": "PPR coupling for joining 1 inch pipes end to end. Fusion welding type. Suitable for hot and cold water. Pressure rating: 20 bar.", "is_featured": False},
            {"name": "Reducing Socket 3/4 x 1/2 inch", "slug": "reducing-socket",
             "category": "fittings", "price": 25, "stock": 400,
             "unit": "piece", "brand": "Supreme",
             "short_description": "Reducer fitting to connect different pipe sizes",
             "description": "PVC reducing socket to connect 3/4 inch pipe to 1/2 inch pipe. Strong solvent weld connection. Smooth inner surface for better flow.", "is_featured": False},

            # Taps & Showers
            {"name": "Kitchen Mixer Tap - SS", "slug": "kitchen-mixer-tap-ss",
             "category": "taps-showers", "price": 1200, "original_price": 1500,
             "stock": 30, "unit": "piece", "brand": "Jaquar",
             "short_description": "Stainless steel kitchen mixer tap",
             "description": "Premium stainless steel kitchen mixer tap with swivel spout. Dual handle for hot and cold water. Anti-corrosion finish. 5-year warranty.", "is_featured": True},
            {"name": "Bathroom Pillar Tap - Chrome", "slug": "bathroom-pillar-tap-chrome",
             "category": "taps-showers", "price": 450, "stock": 50,
             "unit": "piece", "brand": "Cera",
             "short_description": "Chrome-plated bathroom pillar tap",
             "description": "Single lever chrome-plated bathroom pillar tap. Ceramic disc cartridge for smooth operation. Anti-drip design. Easy installation.", "is_featured": True},
            {"name": "Overhead Shower Set 8 inch", "slug": "overhead-shower-set",
             "category": "taps-showers", "price": 1800, "original_price": 2200,
             "stock": 20, "unit": "piece", "brand": "Jaquar",
             "short_description": "Complete overhead shower set with arm and flange",
             "description": "Complete overhead shower set includes 8 inch round shower head, shower arm, and wall flange. Anti-limescale nozzles. Chrome finish. Easy clean rubber nozzles.", "is_featured": False},
            {"name": "Health Faucet Set", "slug": "health-faucet-set",
             "category": "taps-showers", "price": 350, "stock": 40,
             "unit": "piece", "brand": "Cera",
             "short_description": "Health faucet with hose and holder",
             "description": "Complete health faucet set with 1.5m flexible hose and wall holder. Chrome finish. Anti-bacterial nozzle. Universal fitting.", "is_featured": False},
            {"name": "Bib Tap - Heavy Duty", "slug": "bib-tap-heavy-duty",
             "category": "taps-showers", "price": 180, "stock": 60,
             "unit": "piece", "brand": "Local",
             "short_description": "Heavy duty bib tap for outdoor use",
             "description": "Brass bib tap with chrome finish. Heavy duty construction for outdoor and garden use. 3/4 inch BSP thread. Anti-leak washer.", "is_featured": False},

            # Bathroom & Sanitary
            {"name": "Western Commode - Single Flush", "slug": "western-commode-single-flush",
             "category": "bathroom-sanitary", "price": 4500, "original_price": 5500,
             "stock": 10, "unit": "piece", "brand": "Cera",
             "short_description": "Single flush western commode with seat cover",
             "description": "EWC single flush western commode. Includes soft-close seat cover. Rimless design for easy cleaning. Water-efficient 3L flush. 10-year warranty.", "is_featured": True},
            {"name": "Wash Basin - Pedestal", "slug": "wash-basin-pedestal",
             "category": "bathroom-sanitary", "price": 3200, "stock": 8,
             "unit": "piece", "brand": "Hindware",
             "short_description": "Ceramic pedestal wash basin",
             "description": "Premium ceramic pedestal wash basin. Glossy white finish. Anti-bacterial glaze. Includes pedestal and basin. Dimensions: 600x450mm.", "is_featured": False},
            {"name": "Bathroom Mirror 18x24 inch", "slug": "bathroom-mirror-18x24",
             "category": "bathroom-sanitary", "price": 800, "stock": 15,
             "unit": "piece", "brand": "Local",
             "short_description": "Rectangular bathroom mirror with frame",
             "description": "18 x 24 inch rectangular bathroom mirror. Aluminium frame. Fog-free coating. Easy wall mount installation.", "is_featured": False},
            {"name": "Soap Dispenser Wall Mount", "slug": "soap-dispenser-wall-mount",
             "category": "bathroom-sanitary", "price": 250, "stock": 25,
             "unit": "piece", "brand": "Local",
             "short_description": "Wall-mounted liquid soap dispenser",
             "description": "ABS plastic wall-mounted soap dispenser. 350ml capacity. Transparent window to check level. Easy to refill. Suitable for bathrooms and kitchens.", "is_featured": False},

            # Tools
            {"name": "Pipe Wrench 12 inch", "slug": "pipe-wrench-12-inch",
             "category": "tools", "price": 650, "original_price": 800,
             "stock": 25, "unit": "piece", "brand": "Taparia",
             "short_description": "Heavy-duty 12 inch pipe wrench",
             "description": "Drop-forged steel pipe wrench, 12 inch length. Jaw capacity: 2 inch. Hardened teeth for positive grip. Drop-forged body for durability. Chrome vanadium steel.", "is_featured": True},
            {"name": "Pipe Cutter 1 inch", "slug": "pipe-cutter-1-inch",
             "category": "tools", "price": 350, "stock": 20,
             "unit": "piece", "brand": "Taparia",
             "short_description": "Cutter for PVC and CPVC pipes up to 1 inch",
             "description": "Ratchet-type pipe cutter for clean cuts on PVC and CPVC pipes up to 1 inch diameter. Sharp steel blade. Ergonomic handle. Compact and portable.", "is_featured": False},
            {"name": "Plumbing Tool Kit (8 pcs)", "slug": "plumbing-tool-kit-8pcs",
             "category": "tools", "price": 2500, "original_price": 3000,
             "stock": 10, "unit": "set", "brand": "Taparia",
             "short_description": "Complete plumbing toolkit with 8 essential tools",
             "description": "8-piece plumbing tool kit includes: pipe wrench, adjustable spanner, Teflon tape, pipe cutter, Allen keys, screwdriver set, pliers, and carry case. Ideal for home plumbing repairs.", "is_featured": True},
            {"name": "Teflon Tape (Pack of 10)", "slug": "teflon-tape-pack-10",
             "category": "tools", "price": 120, "stock": 100,
             "unit": "pack", "brand": "Loctite",
             "short_description": "PTFE thread seal tape for pipe joints",
             "description": "Pack of 10 rolls of premium PTFE thread seal tape. Width: 12mm, thickness: 0.1mm. Suitable for all types of pipe threads. Waterproof and chemical resistant.", "is_featured": False},
            {"name": "Adjustable Spanner 10 inch", "slug": "adjustable-spanner-10-inch",
             "category": "tools", "price": 400, "stock": 30,
             "unit": "piece", "brand": "Taparia",
             "short_description": "10 inch adjustable spanner/wrench",
             "description": "10 inch chrome-plated adjustable spanner. Jaw opening up to 25mm. Hardened and ground jaws. Knurl for smooth adjustment. Drop-forged steel body.", "is_featured": False},

            # Valves & Accessories
            {"name": "Brass Ball Valve 1/2 inch", "slug": "brass-ball-valve-half-inch",
             "category": "valves-accessories", "price": 180, "stock": 60,
             "unit": "piece", "brand": "Udarshi",
             "short_description": "Full port brass ball valve",
             "description": "Full port brass ball valve 1/2 inch. Chrome plated body. PTFE seat for bubble-tight shut off. Lever handle. Working pressure: 600 WOG.", "is_featured": True},
            {"name": "Gate Valve 1 inch - GI", "slug": "gate-valve-1-inch-gi",
             "category": "valves-accessories", "price": 350, "stock": 25,
             "unit": "piece", "brand": "Udarshi",
             "short_description": "Galvanized iron gate valve",
             "description": "1 inch galvanized iron gate valve. Rising stem type. Suitable for water supply lines. Full bore design for minimal pressure drop. Threaded ends.", "is_featured": False},
            {"name": "Flexible Hose 1/2 inch (60cm)", "slug": "flexible-hose-60cm",
             "category": "valves-accessories", "price": 150, "stock": 80,
             "unit": "piece", "brand": "Local",
             "short_description": "SS flexible connector hose",
             "description": "60cm stainless steel braided flexible hose. 1/2 inch BSP connectors on both ends. Suitable for toilet cistern and faucet connections. Burst pressure: 25 bar.", "is_featured": False},
            {"name": "Angle Valve 1/4 turn", "slug": "angle-valve-quarter-turn",
             "category": "valves-accessories", "price": 120, "stock": 100,
             "unit": "piece", "brand": "Local",
             "short_description": "Quarter-turn angle valve for bathroom",
             "description": "Chrome-plated brass angle valve. Quarter-turn operation. 3/4 inch to 1/2 inch connection. Ceramic disc cartridge. Easy installation. Suitable for geyser and basin connections.", "is_featured": False},
            {"name": "Non-Return Valve 1 inch", "slug": "non-return-valve-1-inch",
             "category": "valves-accessories", "price": 450, "stock": 15,
             "unit": "piece", "brand": "Udarshi",
             "short_description": "Check valve to prevent backflow",
             "description": "1 inch brass non-return valve (check valve). Spring-loaded disc type. Prevents backflow in water supply systems. Chrome plated. Threaded ends.", "is_featured": False},
        ]

        for data in products_data:
            category = categories[data.pop("category")]
            Product.objects.update_or_create(
                slug=data["slug"],
                defaults={**data, "category": category, "is_active": True},
            )
            self.stdout.write(f"  Created product: {data['name']}")

        self.stdout.write(self.style.SUCCESS(
            f"\nDone! Created {len(categories_data)} categories and {len(products_data)} products."
        ))
        self.stdout.write(self.style.SUCCESS(
            "Run the server: python manage.py runserver"
        ))
