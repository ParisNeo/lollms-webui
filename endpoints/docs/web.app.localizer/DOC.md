# WebAppLocalizer

Quick reference for AI-assisted development of the WebAppLocalizer class.

## Import
```html
    <script src="/lollms_assets/js/web.app.localizer"></script>
```

## Initialization
```javascript
const localizer = new WebAppLocalizer(translations, localStoragePrefix, languageSelector);
```

## Key Methods
- `setLanguage(lang)`
- `getCurrentLanguage()`
- `getAvailableLanguages()`
- `translate(key)`
- `apply()`

## Translations Object Structure
```javascript
{
    [langCode]: {
        name: "Language Name",
        translations: {
            [key]: "Translation"
        }
    }
}
```

## HTML Usage
```html
<element data-translate="key"></element>
```

Apply translations: `localizer.apply();`
