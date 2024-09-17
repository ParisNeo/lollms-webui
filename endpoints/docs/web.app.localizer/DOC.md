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
        },
        // optional
        promptTranslations: {
            [prompt name]: "Translation"
        }
    }
}
```

## HTML Usage
If your translation is plain text, then use:
```html
<element data-translate="key"></element>
```
If your translation contains html, then add data-translate-html entry:
```html
<element data-translate="key" data-translate-html></element>
```


Apply translations: `localizer.apply();`
Get the translation of a prompt with options:
```javascript
localizer.formatPrompt([prompt name], {
    variable name: variable value to substitude in the translation string
})
```
In the translation string use the syntax {variable name}. This will allow using variable string parts when translating.