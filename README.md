# 🌙 Celestial Horoscope - Android Astrology App

A beautiful, cosmic-themed astrology application for Android that provides personalized horoscopes, zodiac insights, birth chart calculations, and compatibility analysis.

![Celestial Horoscope](https://img.shields.io/badge/Platform-Android-green) ![Capacitor](https://img.shields.io/badge/Built%20with-Capacitor-blue) ![License](https://img.shields.io/badge/License-MIT-purple)

## ✨ Features

### 🔮 Daily Horoscopes
- Personalized daily, weekly, and monthly horoscope readings
- Lucky numbers, colors, and mood predictions
- Cosmic advice tailored to your zodiac sign

### ♈ Complete Zodiac Guide
- Detailed information for all 12 zodiac signs
- Personality traits, strengths, and growth areas
- Element, quality, and planetary ruler details
- Compatible signs and lucky attributes

### 🗺️ Birth Chart Calculator
- Calculate your Big Three (Sun, Moon, Rising signs)
- Complete planetary position analysis
- Visual chart wheel representation
- Personalized interpretation of your cosmic blueprint

### 💫 Compatibility Checker
- Love compatibility between any two signs
- Detailed breakdown: Romance, Communication, Trust, Values
- Relationship tips and cosmic connection analysis
- Animated compatibility score visualization

### 🎨 Stunning UI
- Cosmic-themed dark design with golden accents
- Animated starry background with shooting stars
- Smooth transitions and micro-interactions
- Mobile-optimized responsive layout

## 🚀 Quick Start

### Prerequisites

- Node.js 16+ installed
- Android Studio (for APK building)
- Java JDK 11+ (for Android builds)

### Installation

```bash
# Clone the repository
cd /workspace

# Install dependencies
npm install

# Preview the app in browser
npm start
# Open http://localhost:3000
```

### Building Android APK

#### Step 1: Initialize Capacitor

```bash
# Initialize Capacitor (only needed once)
npx cap init "Celestial Horoscope" com.celestial.horoscope --web-dir www

# Add Android platform
npx cap add android
```

#### Step 2: Sync and Build

```bash
# Sync web assets to Android project
npx cap sync

# Open in Android Studio (optional - for debugging)
npx cap open android

# Build debug APK via command line
cd android
./gradlew assembleDebug
```

The APK will be generated at:
```
android/app/build/outputs/apk/debug/app-debug.apk
```

#### Step 3: Build Release APK

For a signed release APK:

```bash
cd android
./gradlew assembleRelease
```

## 📱 App Structure

```
celestial-horoscope/
├── www/                      # Web application files
│   ├── index.html           # Main HTML with app structure
│   ├── styles.css           # Cosmic theme & animations
│   └── app.js               # Application logic & data
├── android/                  # Android platform (after cap add)
├── capacitor.config.json    # Capacitor configuration
├── package.json             # Project dependencies
└── README.md                # This file
```

## 🎯 How to Use

### Home Screen
1. View current moon phase and cosmic energy
2. Select your zodiac sign from the wheel
3. Receive personalized daily insight

### Zodiac Guide
1. Tap on any zodiac card to view detailed information
2. Learn about traits, compatibility, and more

### Daily Horoscope
1. Select your sign from the dropdown
2. Switch between daily, weekly, and monthly readings
3. View lucky attributes and cosmic advice

### Birth Chart
1. Enter your birth date (required)
2. Add birth time for accurate rising sign (optional)
3. Tap "Reveal My Chart" to see your celestial blueprint

### Compatibility
1. Select your zodiac sign
2. Select your partner's zodiac sign
3. Tap "Check Compatibility" to see your cosmic connection

## 🛠️ Customization

### Changing App Colors

Edit CSS variables in `www/styles.css`:

```css
:root {
    --cosmic-gold: #ffd700;
    --aurora-blue: #4fc3f7;
    --aurora-purple: #ba68c8;
    /* ... */
}
```

### Adding More Horoscope Content

Edit the `horoscopeTemplates` object in `www/app.js`:

```javascript
const horoscopeTemplates = {
    daily: [
        "Your new horoscope text here...",
        // ...
    ],
    // ...
};
```

### Modifying Zodiac Data

Edit the `zodiacSigns` array in `www/app.js` to customize sign information.

## 📦 Dependencies

- **@capacitor/core** - Cross-platform native runtime
- **@capacitor/android** - Android platform support
- **@capacitor/cli** - Build tools

## 🌟 Credits

- Fonts: [Cinzel](https://fonts.google.com/specimen/Cinzel) & [Cormorant Garamond](https://fonts.google.com/specimen/Cormorant+Garamond)
- Built with love for astrology enthusiasts ✨

## 📄 License

MIT License - Feel free to use and modify for your projects!

---

Made with 🌙 and ✨ by Celestial Apps
