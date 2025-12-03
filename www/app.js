// ================================
// CELESTIAL HOROSCOPE - Main Application
// ================================

// Zodiac Signs Data
const zodiacSigns = [
    {
        name: 'Aries',
        symbol: '♈',
        emoji: '🐏',
        dates: 'Mar 21 - Apr 19',
        element: '🔥',
        elementName: 'Fire',
        quality: 'Cardinal',
        ruler: 'Mars',
        rulerSymbol: '♂️',
        color: '#FF6B6B',
        traits: ['Bold', 'Ambitious', 'Energetic', 'Competitive'],
        strengths: ['Courageous', 'Determined', 'Confident', 'Enthusiastic'],
        weaknesses: ['Impatient', 'Impulsive', 'Aggressive', 'Competitive'],
        compatibility: ['Leo', 'Sagittarius', 'Gemini', 'Aquarius'],
        luckyNumbers: [1, 8, 17],
        luckyDay: 'Tuesday',
        bodyPart: 'Head',
        description: 'Aries is the first sign of the zodiac, symbolizing new beginnings and the spark of life. As a fire sign ruled by Mars, Aries natives are natural-born leaders with boundless energy and enthusiasm. They charge headfirst into challenges and inspire others with their courage and determination.'
    },
    {
        name: 'Taurus',
        symbol: '♉',
        emoji: '🐂',
        dates: 'Apr 20 - May 20',
        element: '🌍',
        elementName: 'Earth',
        quality: 'Fixed',
        ruler: 'Venus',
        rulerSymbol: '♀️',
        color: '#4ECDC4',
        traits: ['Reliable', 'Patient', 'Practical', 'Devoted'],
        strengths: ['Reliable', 'Patient', 'Practical', 'Devoted'],
        weaknesses: ['Stubborn', 'Possessive', 'Uncompromising'],
        compatibility: ['Virgo', 'Capricorn', 'Cancer', 'Pisces'],
        luckyNumbers: [2, 6, 9, 12],
        luckyDay: 'Friday',
        bodyPart: 'Neck/Throat',
        description: 'Taurus is the anchor of the zodiac, representing stability, sensuality, and the appreciation of life\'s pleasures. Ruled by Venus, the planet of love and beauty, Taurus natives have a deep connection to the material world and find joy in comfort, art, and nature.'
    },
    {
        name: 'Gemini',
        symbol: '♊',
        emoji: '👯',
        dates: 'May 21 - Jun 20',
        element: '💨',
        elementName: 'Air',
        quality: 'Mutable',
        ruler: 'Mercury',
        rulerSymbol: '☿',
        color: '#FFE66D',
        traits: ['Adaptable', 'Curious', 'Communicative', 'Witty'],
        strengths: ['Gentle', 'Affectionate', 'Curious', 'Quick learner'],
        weaknesses: ['Nervous', 'Inconsistent', 'Indecisive'],
        compatibility: ['Libra', 'Aquarius', 'Aries', 'Leo'],
        luckyNumbers: [5, 7, 14, 23],
        luckyDay: 'Wednesday',
        bodyPart: 'Arms/Hands',
        description: 'Gemini is the sign of the twins, representing duality, communication, and intellectual curiosity. Ruled by Mercury, Geminis are quick-witted, versatile, and eternally youthful in spirit. They are the social butterflies of the zodiac, connecting ideas and people with ease.'
    },
    {
        name: 'Cancer',
        symbol: '♋',
        emoji: '🦀',
        dates: 'Jun 21 - Jul 22',
        element: '💧',
        elementName: 'Water',
        quality: 'Cardinal',
        ruler: 'Moon',
        rulerSymbol: '🌙',
        color: '#C7CEEA',
        traits: ['Intuitive', 'Emotional', 'Protective', 'Nurturing'],
        strengths: ['Tenacious', 'Imaginative', 'Loyal', 'Sympathetic'],
        weaknesses: ['Moody', 'Pessimistic', 'Suspicious', 'Manipulative'],
        compatibility: ['Scorpio', 'Pisces', 'Taurus', 'Virgo'],
        luckyNumbers: [2, 7, 11, 16],
        luckyDay: 'Monday',
        bodyPart: 'Chest/Stomach',
        description: 'Cancer is the nurturing mother of the zodiac, deeply connected to home, family, and emotional security. Ruled by the Moon, Cancer natives experience life through their feelings and possess remarkable intuition. They are the protectors and caregivers who create safe havens for those they love.'
    },
    {
        name: 'Leo',
        symbol: '♌',
        emoji: '🦁',
        dates: 'Jul 23 - Aug 22',
        element: '🔥',
        elementName: 'Fire',
        quality: 'Fixed',
        ruler: 'Sun',
        rulerSymbol: '☀️',
        color: '#FFA500',
        traits: ['Confident', 'Creative', 'Generous', 'Dramatic'],
        strengths: ['Creative', 'Passionate', 'Generous', 'Warm-hearted'],
        weaknesses: ['Arrogant', 'Stubborn', 'Self-centered', 'Lazy'],
        compatibility: ['Aries', 'Sagittarius', 'Gemini', 'Libra'],
        luckyNumbers: [1, 3, 10, 19],
        luckyDay: 'Sunday',
        bodyPart: 'Heart/Spine',
        description: 'Leo is the king of the zodiac, radiating warmth, creativity, and natural charisma. Ruled by the Sun, Leos are born to shine and lead. They possess a generous heart and a flair for the dramatic, inspiring others with their enthusiasm and unwavering self-confidence.'
    },
    {
        name: 'Virgo',
        symbol: '♍',
        emoji: '👼',
        dates: 'Aug 23 - Sep 22',
        element: '🌍',
        elementName: 'Earth',
        quality: 'Mutable',
        ruler: 'Mercury',
        rulerSymbol: '☿',
        color: '#98D8C8',
        traits: ['Analytical', 'Practical', 'Diligent', 'Modest'],
        strengths: ['Loyal', 'Analytical', 'Kind', 'Hardworking'],
        weaknesses: ['Shyness', 'Worry', 'Overly critical', 'All work no play'],
        compatibility: ['Taurus', 'Capricorn', 'Cancer', 'Scorpio'],
        luckyNumbers: [5, 14, 15, 23],
        luckyDay: 'Wednesday',
        bodyPart: 'Digestive System',
        description: 'Virgo is the healer and perfectionist of the zodiac, with an eye for detail and a heart of service. Ruled by Mercury, Virgos possess analytical minds and practical wisdom. They strive for excellence in everything they do and find fulfillment in helping others improve their lives.'
    },
    {
        name: 'Libra',
        symbol: '♎',
        emoji: '⚖️',
        dates: 'Sep 23 - Oct 22',
        element: '💨',
        elementName: 'Air',
        quality: 'Cardinal',
        ruler: 'Venus',
        rulerSymbol: '♀️',
        color: '#FFB6C1',
        traits: ['Diplomatic', 'Graceful', 'Fair-minded', 'Social'],
        strengths: ['Cooperative', 'Diplomatic', 'Gracious', 'Fair-minded'],
        weaknesses: ['Indecisive', 'Avoids confrontations', 'Self-pity'],
        compatibility: ['Gemini', 'Aquarius', 'Leo', 'Sagittarius'],
        luckyNumbers: [4, 6, 13, 15],
        luckyDay: 'Friday',
        bodyPart: 'Kidneys/Lower Back',
        description: 'Libra is the sign of balance, beauty, and partnership. Ruled by Venus, Libras are natural diplomats with a refined aesthetic sense. They seek harmony in all relationships and environments, and possess the gift of seeing multiple perspectives with fairness and grace.'
    },
    {
        name: 'Scorpio',
        symbol: '♏',
        emoji: '🦂',
        dates: 'Oct 23 - Nov 21',
        element: '💧',
        elementName: 'Water',
        quality: 'Fixed',
        ruler: 'Pluto/Mars',
        rulerSymbol: '♇',
        color: '#8B0000',
        traits: ['Passionate', 'Resourceful', 'Brave', 'Mysterious'],
        strengths: ['Resourceful', 'Brave', 'Passionate', 'Stubborn'],
        weaknesses: ['Distrusting', 'Jealous', 'Secretive', 'Violent'],
        compatibility: ['Cancer', 'Pisces', 'Virgo', 'Capricorn'],
        luckyNumbers: [8, 11, 18, 22],
        luckyDay: 'Tuesday',
        bodyPart: 'Reproductive System',
        description: 'Scorpio is the alchemist of the zodiac, mastering the art of transformation and rebirth. Ruled by Pluto, Scorpios dive deep into life\'s mysteries with intensity and fearlessness. They possess profound emotional intelligence and the power to transform themselves and others.'
    },
    {
        name: 'Sagittarius',
        symbol: '♐',
        emoji: '🏹',
        dates: 'Nov 22 - Dec 21',
        element: '🔥',
        elementName: 'Fire',
        quality: 'Mutable',
        ruler: 'Jupiter',
        rulerSymbol: '♃',
        color: '#9B59B6',
        traits: ['Adventurous', 'Optimistic', 'Philosophical', 'Free-spirited'],
        strengths: ['Generous', 'Idealistic', 'Great sense of humor'],
        weaknesses: ['Promises more than can deliver', 'Impatient'],
        compatibility: ['Aries', 'Leo', 'Libra', 'Aquarius'],
        luckyNumbers: [3, 7, 9, 12],
        luckyDay: 'Thursday',
        bodyPart: 'Hips/Thighs',
        description: 'Sagittarius is the explorer and philosopher of the zodiac, always seeking truth and meaning. Ruled by Jupiter, the planet of expansion, Sagittarians are optimistic adventurers with a love for freedom, travel, and higher learning. They inspire others with their enthusiasm and big-picture vision.'
    },
    {
        name: 'Capricorn',
        symbol: '♑',
        emoji: '🐐',
        dates: 'Dec 22 - Jan 19',
        element: '🌍',
        elementName: 'Earth',
        quality: 'Cardinal',
        ruler: 'Saturn',
        rulerSymbol: '♄',
        color: '#2C3E50',
        traits: ['Ambitious', 'Disciplined', 'Patient', 'Responsible'],
        strengths: ['Responsible', 'Disciplined', 'Self-control', 'Good managers'],
        weaknesses: ['Know-it-all', 'Unforgiving', 'Condescending'],
        compatibility: ['Taurus', 'Virgo', 'Scorpio', 'Pisces'],
        luckyNumbers: [4, 8, 13, 22],
        luckyDay: 'Saturday',
        bodyPart: 'Knees/Bones',
        description: 'Capricorn is the master builder of the zodiac, climbing steadily toward their goals with determination. Ruled by Saturn, Capricorns understand that lasting success comes through patience and hard work. They are the architects of their destiny, building legacies that stand the test of time.'
    },
    {
        name: 'Aquarius',
        symbol: '♒',
        emoji: '🏺',
        dates: 'Jan 20 - Feb 18',
        element: '💨',
        elementName: 'Air',
        quality: 'Fixed',
        ruler: 'Uranus/Saturn',
        rulerSymbol: '♅',
        color: '#00CED1',
        traits: ['Innovative', 'Humanitarian', 'Independent', 'Original'],
        strengths: ['Progressive', 'Original', 'Independent', 'Humanitarian'],
        weaknesses: ['Runs from emotional expression', 'Temperamental'],
        compatibility: ['Gemini', 'Libra', 'Aries', 'Sagittarius'],
        luckyNumbers: [4, 7, 11, 22],
        luckyDay: 'Saturday',
        bodyPart: 'Ankles/Circulation',
        description: 'Aquarius is the visionary and humanitarian of the zodiac, always ahead of their time. Ruled by Uranus, Aquarians are innovative thinkers who challenge conventions and champion progress. They dream of a better world and work tirelessly to bring their revolutionary ideas to life.'
    },
    {
        name: 'Pisces',
        symbol: '♓',
        emoji: '🐟',
        dates: 'Feb 19 - Mar 20',
        element: '💧',
        elementName: 'Water',
        quality: 'Mutable',
        ruler: 'Neptune/Jupiter',
        rulerSymbol: '♆',
        color: '#7B68EE',
        traits: ['Intuitive', 'Artistic', 'Compassionate', 'Dreamy'],
        strengths: ['Compassionate', 'Artistic', 'Intuitive', 'Gentle'],
        weaknesses: ['Fearful', 'Overly trusting', 'Sad', 'Desire to escape reality'],
        compatibility: ['Cancer', 'Scorpio', 'Taurus', 'Capricorn'],
        luckyNumbers: [3, 9, 12, 15],
        luckyDay: 'Thursday',
        bodyPart: 'Feet/Lymphatic System',
        description: 'Pisces is the mystic and dreamer of the zodiac, swimming in the depths of imagination and emotion. Ruled by Neptune, Pisceans possess extraordinary intuition and artistic sensitivity. They are the old souls who feel the collective consciousness and express universal truths through art and compassion.'
    }
];

// Daily Horoscopes Templates
const horoscopeTemplates = {
    daily: [
        "The cosmic energies today align in your favor, bringing unexpected opportunities for growth. Trust your instincts and take that leap of faith you've been contemplating.",
        "Today, the stars encourage you to focus on self-care and reflection. Take time to nurture your inner world, and you'll find clarity emerging from the stillness.",
        "A meaningful connection awaits you today. Whether it's rekindling an old friendship or meeting someone new, the universe is orchestrating beautiful encounters.",
        "Your creative energy is at a peak today. Channel this celestial inspiration into projects that matter to you, and watch magic unfold.",
        "The planetary alignment suggests a day of transformation. Embrace change as it comes, knowing that what falls away makes room for something better.",
        "Financial matters come into focus today. The stars support wise decisions and could bring news of prosperity. Trust your practical instincts.",
        "Communication flows easily today, making it ideal for important conversations. Express your truth with kindness, and you'll be heard.",
        "Adventure calls to your spirit today. Even small explorations can lead to profound discoveries. Say yes to new experiences.",
        "The moon's influence heightens your intuition today. Pay attention to dreams and gut feelings—they carry important messages.",
        "Today brings harmony to relationships. Express appreciation for those who matter, and watch your bonds grow stronger."
    ],
    weekly: [
        "This week brings a powerful shift in your personal relationships. Venus moving through your sector of partnerships creates opportunities for deeper connections and meaningful conversations. Mid-week may bring a challenge, but it's designed to strengthen your resolve. By the weekend, you'll feel more aligned with your true path than ever before.",
        "The week ahead is charged with creative potential. Mercury's influence sharpens your mental acuity, making it an excellent time for brainstorming and problem-solving. Pay attention to recurring themes in your dreams—they hold valuable insights. Financial matters improve by Thursday, and the weekend favors social activities.",
        "A transformative week lies ahead. The sun's journey through your sector of personal development illuminates areas ready for growth. Old patterns may surface for healing mid-week. Embrace this process with compassion. By Sunday, you'll emerge with renewed clarity and purpose."
    ],
    monthly: [
        "This month marks a significant chapter in your cosmic journey. The planetary configurations create a powerful backdrop for personal evolution. Early in the month, focus on setting clear intentions. Mid-month brings opportunities for advancement in career or creative pursuits. The final week is ideal for nurturing relationships and celebrating progress. Trust the timing of your life.",
        "A month of abundance and expansion awaits you. Jupiter's benevolent influence opens doors you didn't know existed. Focus on gratitude to amplify these blessings. Challenges that arise are simply opportunities in disguise. By month's end, you'll have a clearer vision of your purpose and the courage to pursue it.",
        "This month invites deep reflection and spiritual growth. The universe is guiding you toward greater authenticity. Release what no longer serves you with love. New connections forming this month could prove significant. Trust your intuition above all else, and remember that you are exactly where you need to be."
    ]
};

// Moon Phases
const moonPhases = [
    { emoji: '🌑', name: 'New Moon', message: 'Time for new beginnings' },
    { emoji: '🌒', name: 'Waxing Crescent', message: 'Set your intentions' },
    { emoji: '🌓', name: 'First Quarter', message: 'Take action on goals' },
    { emoji: '🌔', name: 'Waxing Gibbous', message: 'Refine and adjust' },
    { emoji: '🌕', name: 'Full Moon', message: 'Harvest your efforts' },
    { emoji: '🌖', name: 'Waning Gibbous', message: 'Share your wisdom' },
    { emoji: '🌗', name: 'Last Quarter', message: 'Release and let go' },
    { emoji: '🌘', name: 'Waning Crescent', message: 'Rest and reflect' }
];

// Compatibility Matrix
const compatibilityMatrix = {
    'Aries-Aries': 75, 'Aries-Taurus': 60, 'Aries-Gemini': 85, 'Aries-Cancer': 45,
    'Aries-Leo': 95, 'Aries-Virgo': 55, 'Aries-Libra': 70, 'Aries-Scorpio': 60,
    'Aries-Sagittarius': 90, 'Aries-Capricorn': 50, 'Aries-Aquarius': 80, 'Aries-Pisces': 55,
    'Taurus-Taurus': 85, 'Taurus-Gemini': 50, 'Taurus-Cancer': 90, 'Taurus-Leo': 65,
    'Taurus-Virgo': 95, 'Taurus-Libra': 70, 'Taurus-Scorpio': 85, 'Taurus-Sagittarius': 45,
    'Taurus-Capricorn': 95, 'Taurus-Aquarius': 40, 'Taurus-Pisces': 85,
    'Gemini-Gemini': 70, 'Gemini-Cancer': 55, 'Gemini-Leo': 85, 'Gemini-Virgo': 60,
    'Gemini-Libra': 90, 'Gemini-Scorpio': 45, 'Gemini-Sagittarius': 80, 'Gemini-Capricorn': 50,
    'Gemini-Aquarius': 95, 'Gemini-Pisces': 55,
    'Cancer-Cancer': 85, 'Cancer-Leo': 60, 'Cancer-Virgo': 80, 'Cancer-Libra': 50,
    'Cancer-Scorpio': 95, 'Cancer-Sagittarius': 45, 'Cancer-Capricorn': 70, 'Cancer-Aquarius': 40,
    'Cancer-Pisces': 95,
    'Leo-Leo': 75, 'Leo-Virgo': 55, 'Leo-Libra': 85, 'Leo-Scorpio': 65,
    'Leo-Sagittarius': 95, 'Leo-Capricorn': 50, 'Leo-Aquarius': 70, 'Leo-Pisces': 55,
    'Virgo-Virgo': 80, 'Virgo-Libra': 60, 'Virgo-Scorpio': 85, 'Virgo-Sagittarius': 50,
    'Virgo-Capricorn': 95, 'Virgo-Aquarius': 45, 'Virgo-Pisces': 75,
    'Libra-Libra': 70, 'Libra-Scorpio': 60, 'Libra-Sagittarius': 80, 'Libra-Capricorn': 55,
    'Libra-Aquarius': 90, 'Libra-Pisces': 60,
    'Scorpio-Scorpio': 85, 'Scorpio-Sagittarius': 50, 'Scorpio-Capricorn': 80, 'Scorpio-Aquarius': 45,
    'Scorpio-Pisces': 95,
    'Sagittarius-Sagittarius': 80, 'Sagittarius-Capricorn': 50, 'Sagittarius-Aquarius': 90, 'Sagittarius-Pisces': 55,
    'Capricorn-Capricorn': 85, 'Capricorn-Aquarius': 55, 'Capricorn-Pisces': 75,
    'Aquarius-Aquarius': 80, 'Aquarius-Pisces': 50,
    'Pisces-Pisces': 85
};

// Planets for Birth Chart
const planets = [
    { name: 'Sun', symbol: '☀️', meaning: 'Core identity & ego' },
    { name: 'Moon', symbol: '🌙', meaning: 'Emotions & inner self' },
    { name: 'Mercury', symbol: '☿️', meaning: 'Communication & thinking' },
    { name: 'Venus', symbol: '♀️', meaning: 'Love & beauty' },
    { name: 'Mars', symbol: '♂️', meaning: 'Energy & action' },
    { name: 'Jupiter', symbol: '♃', meaning: 'Growth & expansion' },
    { name: 'Saturn', symbol: '♄', meaning: 'Structure & discipline' },
    { name: 'Uranus', symbol: '♅', meaning: 'Innovation & change' },
    { name: 'Neptune', symbol: '♆', meaning: 'Dreams & intuition' },
    { name: 'Pluto', symbol: '♇', meaning: 'Transformation & power' }
];

// Lucky colors
const luckyColors = [
    { name: 'Ruby Red', hex: '#E91E63' },
    { name: 'Ocean Blue', hex: '#2196F3' },
    { name: 'Forest Green', hex: '#4CAF50' },
    { name: 'Royal Purple', hex: '#9C27B0' },
    { name: 'Sunset Orange', hex: '#FF9800' },
    { name: 'Golden Yellow', hex: '#FFC107' },
    { name: 'Rose Pink', hex: '#E91E63' },
    { name: 'Midnight Blue', hex: '#3F51B5' },
    { name: 'Emerald', hex: '#00BCD4' },
    { name: 'Silver', hex: '#9E9E9E' }
];

// Moods
const moods = ['Optimistic ✨', 'Romantic 💕', 'Creative 🎨', 'Energetic ⚡', 'Reflective 🔮', 'Adventurous 🌟', 'Peaceful 🕊️', 'Passionate 🔥', 'Intuitive 🌙', 'Grounded 🌿'];

// App State
let selectedSign = null;
let currentPage = 'home';

// Initialize App
document.addEventListener('DOMContentLoaded', initApp);

function initApp() {
    updateCurrentDate();
    updateMoonPhase();
    populateZodiacWheel();
    populateZodiacGrid();
    populateSignSelectors();
    setupNavigation();
    setupHoroscopeTabs();
    
    // Add SVG gradient for compatibility score
    addScoreGradient();
}

function updateCurrentDate() {
    const dateEl = document.getElementById('currentDate');
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    dateEl.textContent = new Date().toLocaleDateString('en-US', options);
}

function updateMoonPhase() {
    // Calculate approximate moon phase based on lunar cycle
    const now = new Date();
    const lunarCycle = 29.53; // days
    const knownNewMoon = new Date('2024-01-11'); // Reference new moon
    const daysSinceNewMoon = (now - knownNewMoon) / (1000 * 60 * 60 * 24);
    const moonAge = daysSinceNewMoon % lunarCycle;
    const phaseIndex = Math.floor((moonAge / lunarCycle) * 8);
    
    const phase = moonPhases[phaseIndex];
    document.getElementById('moonVisual').textContent = phase.emoji;
    document.getElementById('moonPhaseName').textContent = phase.name;
    document.getElementById('moonMessage').textContent = phase.message;
}

function populateZodiacWheel() {
    const wheel = document.getElementById('zodiacWheel');
    wheel.innerHTML = zodiacSigns.map(sign => `
        <div class="zodiac-wheel-item" data-sign="${sign.name}" onclick="selectSign('${sign.name}')">
            <span class="symbol">${sign.symbol}</span>
            <span class="name">${sign.name}</span>
        </div>
    `).join('');
}

function populateZodiacGrid() {
    const grid = document.getElementById('zodiacGrid');
    grid.innerHTML = zodiacSigns.map(sign => `
        <div class="zodiac-card" onclick="openSignModal('${sign.name}')" style="--sign-color: ${sign.color}">
            <span class="element">${sign.element}</span>
            <span class="symbol">${sign.symbol}</span>
            <span class="name">${sign.name}</span>
            <span class="dates">${sign.dates}</span>
        </div>
    `).join('');
}

function populateSignSelectors() {
    const selectors = ['horoscopeSignSelect', 'yourSign', 'partnerSign'];
    
    selectors.forEach(selectorId => {
        const select = document.getElementById(selectorId);
        if (select) {
            zodiacSigns.forEach(sign => {
                const option = document.createElement('option');
                option.value = sign.name;
                option.textContent = `${sign.symbol} ${sign.name}`;
                select.appendChild(option);
            });
        }
    });
    
    // Setup change listeners for compatibility
    document.getElementById('yourSign')?.addEventListener('change', updateSignDisplay);
    document.getElementById('partnerSign')?.addEventListener('change', updateSignDisplay);
    document.getElementById('horoscopeSignSelect')?.addEventListener('change', showHoroscope);
}

function updateSignDisplay(e) {
    const signName = e.target.value;
    const displayId = e.target.id === 'yourSign' ? 'yourSignDisplay' : 'partnerSignDisplay';
    const display = document.getElementById(displayId);
    
    if (signName) {
        const sign = zodiacSigns.find(s => s.name === signName);
        display.querySelector('.sign-symbol').textContent = sign.symbol;
        display.style.borderColor = sign.color;
        display.style.boxShadow = `0 0 20px ${sign.color}40`;
    } else {
        display.querySelector('.sign-symbol').textContent = '?';
        display.style.borderColor = 'rgba(255, 215, 0, 0.2)';
        display.style.boxShadow = 'none';
    }
}

function setupNavigation() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const page = btn.dataset.page;
            navigateTo(page);
        });
    });
}

function navigateTo(page) {
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.page === page);
    });
    
    // Show correct page
    document.querySelectorAll('.page').forEach(p => {
        p.classList.toggle('active', p.id === page);
    });
    
    currentPage = page;
    
    // Scroll to top
    document.querySelector('.pages-container').scrollTop = 0;
}

function selectSign(signName) {
    selectedSign = signName;
    
    // Update wheel selection
    document.querySelectorAll('.zodiac-wheel-item').forEach(item => {
        item.classList.toggle('selected', item.dataset.sign === signName);
    });
    
    // Update daily insight
    updateDailyInsight(signName);
}

function updateDailyInsight(signName) {
    const sign = zodiacSigns.find(s => s.name === signName);
    const insightCard = document.getElementById('dailyInsightCard');
    const insightText = document.getElementById('insightText');
    const insightStats = document.getElementById('insightStats');
    
    // Get random daily horoscope
    const dailyIndex = new Date().getDate() % horoscopeTemplates.daily.length;
    insightText.textContent = horoscopeTemplates.daily[dailyIndex];
    
    // Show stats with animation
    insightStats.style.display = 'block';
    
    // Generate pseudo-random stats based on sign and date
    const seed = signName.charCodeAt(0) + new Date().getDate();
    const loveScore = 50 + (seed * 17) % 50;
    const careerScore = 50 + (seed * 23) % 50;
    const healthScore = 50 + (seed * 31) % 50;
    
    setTimeout(() => {
        document.getElementById('loveStat').style.width = loveScore + '%';
        document.getElementById('careerStat').style.width = careerScore + '%';
        document.getElementById('healthStat').style.width = healthScore + '%';
    }, 100);
}

function setupHoroscopeTabs() {
    document.querySelectorAll('.horoscope-tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.horoscope-tab').forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            
            const signSelect = document.getElementById('horoscopeSignSelect');
            if (signSelect.value) {
                updateHoroscopeContent(signSelect.value, tab.dataset.period);
            }
        });
    });
}

function showHoroscope() {
    const select = document.getElementById('horoscopeSignSelect');
    const signName = select.value;
    
    if (!signName) {
        document.getElementById('horoscopeResult').style.display = 'none';
        return;
    }
    
    const sign = zodiacSigns.find(s => s.name === signName);
    const result = document.getElementById('horoscopeResult');
    
    document.getElementById('horoscopeSignIcon').textContent = sign.symbol;
    document.getElementById('horoscopeSignName').textContent = sign.name;
    document.getElementById('horoscopeDateRange').textContent = sign.dates;
    
    result.style.display = 'block';
    
    updateHoroscopeContent(signName, 'daily');
}

function updateHoroscopeContent(signName, period) {
    const sign = zodiacSigns.find(s => s.name === signName);
    const templates = horoscopeTemplates[period];
    const seed = signName.charCodeAt(0) + new Date().getDate();
    const index = seed % templates.length;
    
    document.getElementById('horoscopeText').textContent = templates[index];
    
    // Lucky number (based on sign)
    const luckyNum = sign.luckyNumbers[seed % sign.luckyNumbers.length];
    document.getElementById('luckyNumber').textContent = luckyNum;
    
    // Lucky color
    const color = luckyColors[seed % luckyColors.length];
    document.getElementById('luckyColor').style.backgroundColor = color.hex;
    document.getElementById('luckyColor').title = color.name;
    
    // Mood
    const mood = moods[seed % moods.length];
    document.getElementById('mood').textContent = mood;
    
    // Cosmic advice
    const advices = [
        "Focus on your inner wisdom today. The answers you seek are already within you.",
        "Open your heart to new possibilities. The universe has surprises in store.",
        "Practice gratitude to amplify positive cosmic energies in your life.",
        "Trust the timing of your journey. Everything is unfolding as it should.",
        "Embrace your authentic self. Your uniqueness is your greatest strength.",
        "Connect with nature to ground your spiritual energy today.",
        "Listen to your dreams—they carry messages from the cosmos.",
        "Release what no longer serves you to make room for new blessings."
    ];
    document.getElementById('cosmicAdvice').textContent = advices[seed % advices.length];
}

function calculateBirthChart() {
    const birthDate = document.getElementById('birthDate').value;
    const birthTime = document.getElementById('birthTime').value;
    const birthLocation = document.getElementById('birthLocation').value;
    
    if (!birthDate) {
        alert('Please enter your birth date');
        return;
    }
    
    const date = new Date(birthDate);
    
    // Calculate Sun Sign
    const sunSign = getSunSign(date);
    
    // Calculate Moon Sign (simplified - based on day)
    const moonSignIndex = (date.getDate() + date.getMonth()) % 12;
    const moonSign = zodiacSigns[moonSignIndex].name;
    
    // Calculate Rising Sign (simplified - based on time or random if not provided)
    let risingSignIndex;
    if (birthTime) {
        const [hours] = birthTime.split(':').map(Number);
        risingSignIndex = Math.floor(hours / 2) % 12;
    } else {
        risingSignIndex = (date.getFullYear() + date.getMonth()) % 12;
    }
    const risingSign = zodiacSigns[risingSignIndex].name;
    
    // Update Big Three
    document.getElementById('sunSign').textContent = sunSign;
    document.getElementById('moonSign').textContent = moonSign;
    document.getElementById('risingSign').textContent = risingSign;
    
    // Generate planetary positions
    generatePlanetaryPositions(date);
    
    // Generate interpretation
    generateChartInterpretation(sunSign, moonSign, risingSign);
    
    // Draw chart wheel
    drawChartWheel();
    
    // Show results
    document.getElementById('birthChartResult').style.display = 'block';
    
    // Scroll to results
    setTimeout(() => {
        document.getElementById('birthChartResult').scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

function getSunSign(date) {
    const month = date.getMonth() + 1;
    const day = date.getDate();
    
    const zodiacDates = [
        { sign: 'Capricorn', start: [1, 1], end: [1, 19] },
        { sign: 'Aquarius', start: [1, 20], end: [2, 18] },
        { sign: 'Pisces', start: [2, 19], end: [3, 20] },
        { sign: 'Aries', start: [3, 21], end: [4, 19] },
        { sign: 'Taurus', start: [4, 20], end: [5, 20] },
        { sign: 'Gemini', start: [5, 21], end: [6, 20] },
        { sign: 'Cancer', start: [6, 21], end: [7, 22] },
        { sign: 'Leo', start: [7, 23], end: [8, 22] },
        { sign: 'Virgo', start: [8, 23], end: [9, 22] },
        { sign: 'Libra', start: [9, 23], end: [10, 22] },
        { sign: 'Scorpio', start: [10, 23], end: [11, 21] },
        { sign: 'Sagittarius', start: [11, 22], end: [12, 21] },
        { sign: 'Capricorn', start: [12, 22], end: [12, 31] }
    ];
    
    for (const zodiac of zodiacDates) {
        const [startMonth, startDay] = zodiac.start;
        const [endMonth, endDay] = zodiac.end;
        
        if ((month === startMonth && day >= startDay) || (month === endMonth && day <= endDay)) {
            return zodiac.sign;
        }
    }
    
    return 'Capricorn';
}

function generatePlanetaryPositions(date) {
    const planetsList = document.getElementById('planetsList');
    const seed = date.getTime();
    
    planetsList.innerHTML = planets.map((planet, index) => {
        const signIndex = (Math.floor(seed / Math.pow(10, index)) + index * 3) % 12;
        const sign = zodiacSigns[signIndex];
        return `
            <div class="planet-item">
                <span class="icon">${planet.symbol}</span>
                <span class="planet-label">${planet.name}</span>
                <span class="planet-sign">${sign.symbol} ${sign.name}</span>
            </div>
        `;
    }).join('');
}

function generateChartInterpretation(sunSign, moonSign, risingSign) {
    const interpretation = document.getElementById('chartInterpretation');
    const sun = zodiacSigns.find(s => s.name === sunSign);
    const moon = zodiacSigns.find(s => s.name === moonSign);
    const rising = zodiacSigns.find(s => s.name === risingSign);
    
    interpretation.innerHTML = `
        <h4>✨ Your Cosmic Blueprint</h4>
        <p>
            With your Sun in ${sunSign}, your core essence radiates ${sun.traits[0].toLowerCase()} and ${sun.traits[1].toLowerCase()} energy. 
            Your ${moonSign} Moon reveals a deep emotional nature that is ${moon.traits[0].toLowerCase()} and ${moon.traits[2].toLowerCase()}. 
            The world sees you through your ${risingSign} Rising, perceiving you as ${rising.traits[0].toLowerCase()} and ${rising.traits[3].toLowerCase()}.
        </p>
        <p style="margin-top: 1rem;">
            This unique combination creates a soul journey focused on balancing your ${sun.elementName} Sun with your ${moon.elementName} Moon, 
            while expressing yourself through the lens of ${rising.elementName} energy. Embrace all aspects of your celestial nature.
        </p>
    `;
}

function drawChartWheel() {
    const wheel = document.getElementById('chartWheel');
    wheel.innerHTML = `
        <svg viewBox="0 0 280 280" style="width: 100%; height: 100%;">
            <defs>
                <radialGradient id="wheelGradient" cx="50%" cy="50%" r="50%">
                    <stop offset="0%" style="stop-color: rgba(255,215,0,0.1)"/>
                    <stop offset="100%" style="stop-color: transparent"/>
                </radialGradient>
            </defs>
            <!-- Outer circle -->
            <circle cx="140" cy="140" r="130" fill="none" stroke="rgba(255,215,0,0.3)" stroke-width="2"/>
            <!-- Middle circle -->
            <circle cx="140" cy="140" r="100" fill="none" stroke="rgba(255,215,0,0.2)" stroke-width="1"/>
            <!-- Inner circle -->
            <circle cx="140" cy="140" r="60" fill="url(#wheelGradient)" stroke="rgba(255,215,0,0.2)" stroke-width="1"/>
            <!-- Division lines -->
            ${generateWheelLines()}
            <!-- Zodiac symbols -->
            ${generateWheelSymbols()}
        </svg>
    `;
}

function generateWheelLines() {
    let lines = '';
    for (let i = 0; i < 12; i++) {
        const angle = (i * 30 - 90) * Math.PI / 180;
        const x1 = 140 + 60 * Math.cos(angle);
        const y1 = 140 + 60 * Math.sin(angle);
        const x2 = 140 + 130 * Math.cos(angle);
        const y2 = 140 + 130 * Math.sin(angle);
        lines += `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="rgba(255,215,0,0.15)" stroke-width="1"/>`;
    }
    return lines;
}

function generateWheelSymbols() {
    let symbols = '';
    for (let i = 0; i < 12; i++) {
        const angle = (i * 30 - 75) * Math.PI / 180;
        const x = 140 + 115 * Math.cos(angle);
        const y = 140 + 115 * Math.sin(angle);
        symbols += `<text x="${x}" y="${y}" fill="rgba(255,215,0,0.6)" font-size="14" text-anchor="middle" dominant-baseline="middle">${zodiacSigns[i].symbol}</text>`;
    }
    return symbols;
}

function checkCompatibility() {
    const yourSign = document.getElementById('yourSign').value;
    const partnerSign = document.getElementById('partnerSign').value;
    
    if (!yourSign || !partnerSign) {
        alert('Please select both signs');
        return;
    }
    
    const result = document.getElementById('compatibilityResult');
    
    // Get compatibility score
    const key1 = `${yourSign}-${partnerSign}`;
    const key2 = `${partnerSign}-${yourSign}`;
    const baseScore = compatibilityMatrix[key1] || compatibilityMatrix[key2] || 65;
    
    // Add some daily variance
    const variance = (new Date().getDate() % 10) - 5;
    const score = Math.min(100, Math.max(0, baseScore + variance));
    
    // Animate score
    animateScore(score);
    
    // Update category bars
    const categories = {
        romance: score + (Math.random() * 20 - 10),
        comm: score + (Math.random() * 20 - 10),
        trust: score + (Math.random() * 20 - 10),
        values: score + (Math.random() * 20 - 10)
    };
    
    Object.keys(categories).forEach(cat => {
        const val = Math.min(100, Math.max(0, categories[cat]));
        setTimeout(() => {
            document.getElementById(`${cat}Bar`).style.width = val + '%';
            document.getElementById(`${cat}Score`).textContent = Math.round(val) + '%';
        }, 500);
    });
    
    // Set title based on score
    const titles = [
        [90, 'Soulmate Connection 💫'],
        [75, 'Strong Cosmic Bond ✨'],
        [60, 'Harmonious Pairing 🌟'],
        [45, 'Growth Opportunity 🌱'],
        [0, 'Challenging Match 💪']
    ];
    const title = titles.find(([threshold]) => score >= threshold)[1];
    document.getElementById('compatTitle').textContent = title;
    
    // Generate analysis
    generateCompatibilityAnalysis(yourSign, partnerSign, score);
    
    // Generate tips
    generateRelationshipTips(yourSign, partnerSign);
    
    result.style.display = 'block';
    
    setTimeout(() => {
        result.scrollIntoView({ behavior: 'smooth' });
    }, 100);
}

function animateScore(targetScore) {
    const scoreNumber = document.getElementById('compatScore');
    const scoreFill = document.getElementById('scoreFill');
    
    // Calculate stroke-dashoffset (283 is circumference of circle with r=45)
    const circumference = 283;
    const offset = circumference - (targetScore / 100) * circumference;
    
    scoreFill.style.strokeDashoffset = offset;
    
    // Animate number
    let current = 0;
    const duration = 1500;
    const start = performance.now();
    
    function animate(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        current = Math.round(progress * targetScore);
        scoreNumber.textContent = current;
        
        if (progress < 1) {
            requestAnimationFrame(animate);
        }
    }
    
    requestAnimationFrame(animate);
}

function generateCompatibilityAnalysis(sign1, sign2, score) {
    const s1 = zodiacSigns.find(s => s.name === sign1);
    const s2 = zodiacSigns.find(s => s.name === sign2);
    
    const analysis = document.getElementById('compatAnalysis');
    
    let text = '';
    if (s1.elementName === s2.elementName) {
        text = `As two ${s1.elementName} signs, you share a natural understanding of each other's core needs and expression. This elemental harmony creates a strong foundation for your connection.`;
    } else if (
        (s1.elementName === 'Fire' && s2.elementName === 'Air') ||
        (s1.elementName === 'Air' && s2.elementName === 'Fire') ||
        (s1.elementName === 'Earth' && s2.elementName === 'Water') ||
        (s1.elementName === 'Water' && s2.elementName === 'Earth')
    ) {
        text = `Your elements (${s1.elementName} and ${s2.elementName}) complement each other beautifully. You fuel each other's strengths and provide balance where needed.`;
    } else {
        text = `Your elements (${s1.elementName} and ${s2.elementName}) present opportunities for growth through difference. Embrace what you can learn from each other's unique perspective.`;
    }
    
    analysis.innerHTML = `
        <h4>💫 Your Cosmic Connection</h4>
        <p>${text}</p>
        <p style="margin-top: 1rem;">
            ${sign1}'s ${s1.traits[0].toLowerCase()} nature ${score > 70 ? 'harmonizes wonderfully' : 'creates interesting dynamics'} with ${sign2}'s ${s2.traits[1].toLowerCase()} tendencies. 
            Together, you can ${score > 70 ? 'build something beautiful' : 'learn and grow immensely'}.
        </p>
    `;
}

function generateRelationshipTips(sign1, sign2) {
    const s1 = zodiacSigns.find(s => s.name === sign1);
    const s2 = zodiacSigns.find(s => s.name === sign2);
    
    const tips = [
        `Appreciate ${sign1}'s ${s1.traits[0].toLowerCase()} approach to life`,
        `Honor ${sign2}'s need for ${s2.traits[2].toLowerCase()} expression`,
        `Find common ground in shared ${s1.elementName === s2.elementName ? 'elemental energy' : 'values and goals'}`,
        `Communicate openly about your different ${s1.quality !== s2.quality ? 'paces' : 'approaches'}`,
        `Create rituals that honor both your ${s1.ruler} and ${s2.ruler} influences`,
        `Practice patience during ${s1.quality === 'Fixed' || s2.quality === 'Fixed' ? 'times of change' : 'moments of intensity'}`
    ];
    
    const tipsList = document.getElementById('tipsList');
    tipsList.innerHTML = tips.map(tip => `<li>${tip}</li>`).join('');
}

function addScoreGradient() {
    const svg = document.querySelector('.score-ring svg');
    if (svg) {
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        defs.innerHTML = `
            <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color: #4fc3f7"/>
                <stop offset="50%" style="stop-color: #ba68c8"/>
                <stop offset="100%" style="stop-color: #f48fb1"/>
            </linearGradient>
        `;
        svg.insertBefore(defs, svg.firstChild);
    }
}

function openSignModal(signName) {
    const sign = zodiacSigns.find(s => s.name === signName);
    const modal = document.getElementById('signModal');
    
    document.getElementById('modalIcon').textContent = sign.symbol;
    document.getElementById('modalTitle').textContent = sign.name;
    document.getElementById('modalDates').textContent = `${sign.dates} • ${sign.elementName} Sign`;
    
    const body = document.getElementById('modalBody');
    body.innerHTML = `
        <div class="modal-section">
            <h3>📖 About ${sign.name}</h3>
            <p>${sign.description}</p>
        </div>
        
        <div class="modal-section">
            <h3>✨ Key Traits</h3>
            <div class="traits-grid">
                <div class="trait-item">
                    <span class="trait-label">Element</span>
                    <span class="trait-value">${sign.element} ${sign.elementName}</span>
                </div>
                <div class="trait-item">
                    <span class="trait-label">Quality</span>
                    <span class="trait-value">${sign.quality}</span>
                </div>
                <div class="trait-item">
                    <span class="trait-label">Ruler</span>
                    <span class="trait-value">${sign.rulerSymbol} ${sign.ruler}</span>
                </div>
                <div class="trait-item">
                    <span class="trait-label">Lucky Day</span>
                    <span class="trait-value">${sign.luckyDay}</span>
                </div>
            </div>
        </div>
        
        <div class="modal-section">
            <h3>💪 Strengths</h3>
            <ul>
                ${sign.strengths.map(s => `<li>${s}</li>`).join('')}
            </ul>
        </div>
        
        <div class="modal-section">
            <h3>🌱 Growth Areas</h3>
            <ul>
                ${sign.weaknesses.map(w => `<li>${w}</li>`).join('')}
            </ul>
        </div>
        
        <div class="modal-section">
            <h3>💕 Compatible Signs</h3>
            <p>${sign.compatibility.join(', ')}</p>
        </div>
        
        <div class="modal-section">
            <h3>🔮 Lucky Numbers</h3>
            <p>${sign.luckyNumbers.join(', ')}</p>
        </div>
    `;
    
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    document.getElementById('signModal').classList.remove('active');
    document.body.style.overflow = '';
}

// Close modal on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Close modal on backdrop click
document.getElementById('signModal')?.addEventListener('click', (e) => {
    if (e.target.id === 'signModal') {
        closeModal();
    }
});

// Make functions globally available
window.navigateTo = navigateTo;
window.selectSign = selectSign;
window.openSignModal = openSignModal;
window.closeModal = closeModal;
window.calculateBirthChart = calculateBirthChart;
window.checkCompatibility = checkCompatibility;
