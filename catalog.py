# catalog.py
def build_tree_and_items():
    demo_items = [
        "Breadboard",
        "DC Power Supply",
        "AC Power Supply",
        "Digital Multimeter",
        "AC Ammeter",
        "AC Voltmeter",
        "Analog Multimeter",
        "Resistors (10 Ω – 1 kΩ)",
        "Potentiometer",
        "Capacitors (0.1 µF – 100 µF)",
        "Inductors (10 mH – 1.389 H)",
        "Connecting Wires",
        "Alligator Clips",
        "Switches"
    ]
    categories = {
        "Equipment": demo_items[:7],
        "Components": demo_items[7:11],
        "Accessories": demo_items[11:]
    }
    tree_root = {"name": "root", "children": list(categories.keys())}
    return tree_root, categories, demo_items

def init_availability(all_items):
    avail = {}
    for it in all_items:
        if "Resistors" in it or "Wires" in it:
            avail[it] = 100
        elif "Capacitors" in it:
            avail[it] = 40
        elif "Power Supply" in it:
            avail[it] = 15
        else:
            avail[it] = 10
    return avail

def array_search(all_items, q):
    ql = q.lower()
    return [it for it in all_items if ql in it.lower()]

def array_sort(all_items, by="name", availability=None):
    if by == "availability" and availability:
        return sorted(all_items, key=lambda x: availability.get(x, 0), reverse=True)
    return sorted(all_items, key=lambda x: x.lower())
