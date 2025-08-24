// SEO and Performance Utilities

// Lazy loading for images
export const lazyLoadImages = () => {
  const images = document.querySelectorAll("img[data-src]");
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove("lazy");
        imageObserver.unobserve(img);
      }
    });
  });

  images.forEach((img) => imageObserver.observe(img));
};

// Generate structured data for stock analysis
export const generateStockStructuredData = (stockData) => {
  return {
    "@context": "https://schema.org",
    "@type": "FinancialProduct",
    name: `${stockData.symbol} Stock Analysis`,
    description: `AI-powered analysis of ${stockData.symbol} including technical indicators, sentiment analysis, and trading signals`,
    provider: {
      "@type": "Organization",
      name: "Stock Sage",
    },
    offers: {
      "@type": "Offer",
      price: "0",
      priceCurrency: "USD",
    },
    aggregateRating: {
      "@type": "AggregateRating",
      ratingValue: stockData.confidence
        ? (stockData.confidence / 20).toFixed(1)
        : "4.0",
      bestRating: "5",
      worstRating: "1",
      ratingCount: "100",
    },
  };
};

// Generate breadcrumb structured data
export const generateBreadcrumbData = (breadcrumbs) => {
  return {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    itemListElement: breadcrumbs.map((crumb, index) => ({
      "@type": "ListItem",
      position: index + 1,
      name: crumb.name,
      item: crumb.url,
    })),
  };
};

// Add structured data to page
export const addStructuredData = (data) => {
  const script = document.createElement("script");
  script.type = "application/ld+json";
  script.text = JSON.stringify(data);
  document.head.appendChild(script);
};

// Remove structured data
export const removeStructuredData = () => {
  const scripts = document.querySelectorAll(
    'script[type="application/ld+json"]'
  );
  scripts.forEach((script) => {
    if (
      script.text.includes('"@type": "FinancialProduct"') ||
      script.text.includes('"@type": "BreadcrumbList"')
    ) {
      script.remove();
    }
  });
};

// Generate meta description for stock pages
export const generateStockMetaDescription = (symbol, signal, confidence) => {
  const signalText =
    signal === "STRONG_BUY"
      ? "Strong Buy"
      : signal === "BUY"
      ? "Buy"
      : signal === "SELL"
      ? "Sell"
      : signal === "STRONG_SELL"
      ? "Strong Sell"
      : "Hold";

  return `${symbol} stock analysis shows ${signalText} signal with ${confidence}% confidence. Get real-time technical analysis, sentiment analysis, and trading signals for ${symbol}.`;
};

// Generate keywords for stock pages
export const generateStockKeywords = (symbol, market) => {
  const baseKeywords = `${symbol} stock, ${symbol} analysis, ${symbol} trading signals, ${symbol} technical analysis`;
  const marketKeywords =
    market === "India"
      ? `${symbol} NSE, Indian stock ${symbol}, ${symbol} BSE`
      : `${symbol} NYSE, ${symbol} NASDAQ, US stock ${symbol}`;

  return `${baseKeywords}, ${marketKeywords}, stock market analysis, AI trading signals`;
};

// Preload critical resources
export const preloadCriticalResources = () => {
  // Preload critical API endpoints
  const link1 = document.createElement("link");
  link1.rel = "dns-prefetch";
  link1.href = "//localhost:8000";
  document.head.appendChild(link1);

  // Preload fonts if using external fonts
  const link2 = document.createElement("link");
  link2.rel = "preload";
  link2.href =
    "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap";
  link2.as = "style";
  document.head.appendChild(link2);
};

// Track page views for analytics
export const trackPageView = (pageName, additionalData = {}) => {
  // Google Analytics 4 tracking
  if (typeof gtag !== "undefined") {
    gtag("config", "GA_MEASUREMENT_ID", {
      page_title: pageName,
      page_location: window.location.href,
      ...additionalData,
    });
  }

  // Custom analytics tracking
  console.log(`Page view: ${pageName}`, additionalData);
};

// Optimize images for better performance
export const optimizeImage = (src, width = 800, quality = 80) => {
  // This would integrate with an image optimization service
  // For now, return the original src
  return src;
};

// Generate social sharing URLs
export const generateSocialUrls = (url, title, description) => {
  const encodedUrl = encodeURIComponent(url);
  const encodedTitle = encodeURIComponent(title);
  const encodedDescription = encodeURIComponent(description);

  return {
    facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodedUrl}`,
    twitter: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    whatsapp: `https://wa.me/?text=${encodedTitle}%20${encodedUrl}`,
    telegram: `https://t.me/share/url?url=${encodedUrl}&text=${encodedTitle}`,
  };
};
