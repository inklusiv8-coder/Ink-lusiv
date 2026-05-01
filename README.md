# ink-lusiv. - Wrist Watch E-Commerce Website

A professional, responsive wrist watch e-commerce website built with HTML, CSS, and JavaScript.

## 📋 Features

### Core Features
- **Product Catalog**: Display 8 premium wrist watches with detailed information
- **Product Filtering**: Filter watches by category (All, Luxury, Sport, Classic)
- **Product Details Modal**: View detailed information about each watch including specs and reviews
- **Shopping Cart**: Add/remove items, update quantities, persistent storage using localStorage
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Professional UI**: Modern design with smooth animations and transitions

### Sections
1. **Navigation Bar** - Sticky header with logo, menu, and cart icon
2. **Hero Section** - Eye-catching welcome banner with call-to-action
3. **Products Grid** - Browse and filter watches by category
4. **Product Modal** - Detailed view with specs and quantity selector
5. **About Us** - Why choose our store (quality, shipping, payment, returns)
6. **Contact Form** - Get in touch with customer support
7. **Footer** - Social media links and company info

### JavaScript Functionality
- Dynamic product filtering
- Shopping cart management (add, remove, quantity)
- LocalStorage for persistent cart data
- Product modals with detailed specifications
- Mobile menu toggle
- Form handling
- Toast notifications
- Cart counter display

## 🎨 Design Highlights

- **Color Scheme**: Gold/Bronze primary color (#d4a574) with dark backgrounds
- **Typography**: Modern sans-serif fonts with clear hierarchy
- **Animations**: Smooth transitions and fade-in effects
- **Mobile-First**: Fully responsive with breakpoints at 768px and 480px
- **Performance**: Clean, optimized code

## 📦 Product Data

Each product includes:
- Name and category
- Price with discount percentage
- Star rating and review count
- Detailed description
- Technical specifications (movement, size, water resistance, etc.)
- Product image placeholder with icon

## 🚀 How to Use

1. **Open the website**: Open `index.html` in any modern web browser
2. **Browse products**: View all watches or filter by category
3. **View details**: Click any product card to see full details and specifications
4. **Add to cart**: Select quantity and click "Add to Cart"
5. **View cart**: Click the shopping cart icon to see your items
6. **Contact**: Fill out the contact form for inquiries
7. **Mobile**: Fully responsive - works on all devices

## 📁 File Structure

```
Wrist watch web/
├── index.html      (Main HTML structure)
├── style.css       (All styling and responsive design)
├── script.js       (JavaScript functionality)
└── README.md       (This file)
```

## 🔧 Customization

### Add More Products
Edit `script.js` and add objects to the `products` array:
```javascript
{
    id: 9,
    name: 'Your Watch Name',
    category: 'luxury', // or 'sport', 'classic'
    price: 199.99,
    originalPrice: 299.99,
    rating: 4.8,
    reviews: 100,
    description: 'Watch description',
    specs: {
        'Movement': 'Automatic',
        'Case Size': '42mm',
        // ... more specs
    }
}
```

### Change Colors
Edit the CSS variables in `style.css`:
```css
:root {
    --primary-color: #d4a574;  /* Change this */
    --dark-color: #1a1a1a;
    --light-color: #f5f5f5;
    /* ... other variables */
}
```

### Update Company Info
Edit these sections in `index.html`:
- Logo text in navbar
- Contact information
- Social media links
- Footer text

## 🌐 Browser Compatibility

- Chrome/Edge (Latest)
- Firefox (Latest)
- Safari (Latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## 💡 Enhancement Ideas

- Add payment integration (Stripe, PayPal)
- Implement user authentication
- Add product reviews and ratings
- Inventory management system
- Admin dashboard
- Email notifications
- Search functionality
- Wishlist feature
- Product comparison
- Customer testimonials

## 📱 Mobile Responsiveness

The site is fully responsive with:
- Mobile hamburger menu
- Touch-friendly buttons
- Optimized grid layouts
- Mobile-first CSS approach
- Readable font sizes on all devices

## 🖥️ Backend Setup

A simple Python Flask backend has been added.

Files added:
- `server.py`
- `requirements.txt`
- `start-backend.bat`
- `data/products.json`
- `data/users.json`
- `data/orders.json`

### Run backend
1. Open terminal in the project folder.
2. Run `start-backend.bat` or run:
   - `python -m pip install -r requirements.txt`
   - `python server.py`
3. Open `http://127.0.0.1:5000/` in your browser.
4. `start-backend.bat` already sets the Supabase environment variables required to sync registered users into your `users` table. For backend inserts, you need the **Supabase service role key**, not the publishable key:
   - `SUPABASE_URL=https://tkjwwtwtjatcbdxvwwzu.supabase.co`
   - `SUPABASE_SERVICE_ROLE_KEY=<your service role key>`
   - `SUPABASE_KEY=<your public anon key>`  # optional readonly public key for frontend/read-only calls

The `.env` file is also loaded automatically via `python-dotenv` when you run the server manually.

The backend prefers `SUPABASE_SERVICE_ROLE_KEY` for server-side sync and only uses `SUPABASE_KEY` as a readonly fallback.

The frontend is now wired to fetch products from `/api/products`, register/login via `/api/register`, and submit orders via `/api/orders`.

## 🎯 Performance Tips

- Product images load fast (using CSS icons)
- Minimal CSS and JavaScript
- LocalStorage for instant cart persistence
- Smooth animations with CSS transforms
- Optimized for all screen sizes

## 📝 Notes

- All product data is stored in JavaScript
- Cart data is stored in browser's LocalStorage
- No backend server required to run the website
- Easy to deploy to any web hosting service

---

**Developed with ❤️ for watch enthusiasts**