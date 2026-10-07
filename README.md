# ☕ Simply Coffee — a simple coffee Demo website, Using open AI.

A Demo coffee shop website in **HTML + CSS + JavaScript "python"** with cart, orders and live search and no database connection.

## ✨ Features

| Feature | How it works |
|---|---|
| 🛒 **Add to cart** | "Add" on any coffee card, or pick size (S/M/L) + quantity on the show page |
| 🗑️ **Delete** | Trash button on every cart line item |
| 📦 **Order** | "Order Now" → checkout form → order gets an ID (SC-xxxxxx) |
| ❌ **Cancel** | "Cancel order" in **My Orders** or right on the success screen · "Cancel / Clear" empties the cart |
| 🔍 **Search all coffee** | Live search bar filters all 22 coffees by name, ingredient or category |
| 👁️ **Show page** | Click "Show" for the full detail page — description, ingredients, sizes + **another coffees** you may like |
| 🖼️ **22+ coffee images** | One real photo per drink (espresso → coconut cold brew) |
| 🎁 Promo code | `AK007` = 10% off · free delivery over ₹299 |
| 📱 Responsive | Works on phone, tablet and desktop |

## 📂 Files

- **`index.html`** ← **the website** (fully self-contained: CSS, JS and all 22+ images are inside — just double-click to open, works offline)
- `template.html` — onlt html code
- `build.py` — rebuild script (`python3 build.py`) that compresses `raw_images/` into `images/` and regenerates both versions
- `raw_images/` — original full-size photos before compression

## 🚀 Run it

Open `index.html` in any browser. No server, no internet needed.
