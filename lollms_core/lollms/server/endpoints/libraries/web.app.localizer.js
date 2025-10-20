class WebAppLocalizer {
    constructor(translations, localStoragePrefix = 'webAppLocalizer_', languageSelector = null) {
        this.translations = translations;
        this.localStoragePrefix = localStoragePrefix;
        this.currentLang = this.loadCurrentLanguage() || Object.keys(translations)[0];

        if (typeof languageSelector === 'string') {
            this.languageSelector = document.getElementById(languageSelector);
        } else {
            this.languageSelector = languageSelector;
        }
        
        if (this.languageSelector) {
            this.initializeLanguageSelector();
        }
    }

    loadCurrentLanguage() {
        return localStorage.getItem(this.localStoragePrefix + 'currentLang');
    }

    saveCurrentLanguage(lang) {
        localStorage.setItem(this.localStoragePrefix + 'currentLang', lang);
    }

    setLanguage(lang) {
        if (this.translations.hasOwnProperty(lang)) {
            this.currentLang = lang;
            this.saveCurrentLanguage(lang);
            this.apply();
            if (this.languageSelector) {
                this.languageSelector.value = lang;
            }
        } else {
            console.warn(`Language '${lang}' not found in translations.`);
        }
    }

    getCurrentLanguage() {
        return this.currentLang;
    }

    getAvailableLanguages() {
        return Object.keys(this.translations).map(lang => ({
            code: lang,
            name: this.translations[lang].name
        }));
    }

    translate(key) {
        const translations = this.translations[this.currentLang].translations;
        return translations[key] || key;
    }

    apply() {
        const elements = document.querySelectorAll('[data-translate]');
        elements.forEach(element => {
            const key = element.getAttribute('data-translate');
            const useHTML = element.hasAttribute('data-translate-html');
            
            if (key.includes('placeholder') || key.includes('Placeholder')) {
                // If the key contains "placeholder", set the translation as the placeholder attribute
                element.setAttribute('placeholder', this.translate(key));
            } else if (useHTML) {
                // If data-translate-html is present, set the translation as innerHTML
                element.innerHTML = this.translate(key);
            } else {
                // Otherwise, set the translation as textContent
                element.textContent = this.translate(key);
            }
        });
    }

    initializeLanguageSelector() {
        if (!(this.languageSelector instanceof HTMLElement)) {
            console.warn('Language selector is not a valid HTML element.');
            return;
        }

        if (this.languageSelector.tagName.toLowerCase() !== 'select') {
            // Create a select element if the provided element is not a select
            const selectElement = document.createElement('select');
            this.languageSelector.appendChild(selectElement);
            this.languageSelector = selectElement;
        }

        // Clear existing options
        this.languageSelector.innerHTML = '';

        // Add options for each available language
        this.getAvailableLanguages().forEach(lang => {
            const option = document.createElement('option');
            option.value = lang.code;
            option.textContent = lang.name;
            this.languageSelector.appendChild(option);
        });

        // Set the current language
        this.languageSelector.value = this.currentLang;

        // Add event listener for language change
        this.languageSelector.addEventListener('change', (event) => {
            this.setLanguage(event.target.value);
        });
    }
    // helper functions
    // A format prompt function
    formatPrompt(prompt_name, values) {
        return this.translations[this.currentLang].promptTranslations[prompt_name].replace(/\{(\w+)\}/g, (match, key) => values[key] || match);
    }
}

