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
languageSelector is an element not a string, so you need to create a select element, instantiate it or select it then use it here.

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
        // optional prompt translation
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
for example to translate a prompt to fr:
```javascript
const translation={
    //.. other languages
    fr:{
        name: "French",
        translations: {
            "elementName1": "Translation1"
            //... more elements
        },
        // optional prompt translation
        promptTranslations: {
            "prompt1": "prompt text {variable1} more text {variable2}"
        }
    }
}
// To translate the prompt
const localizedPrompt = localizer.formatPrompt("prompt1", {
    "variable1": "variable 1 value"
})
```